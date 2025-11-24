Web VPython 3.2
from vpython import *
import random


scene.title = "Simulação Xique-Xique Bahia: Ciclo Circadiano & Clima"
scene.width = 900
scene.height = 600
scene.center = vec(0, 5, 0)
scene.camera.pos = vec(60, 50, 60) # Câmera levemente ajustada para ver a escola
scene.camera.axis = vec(-60, -50, -60)
scene.background = color.black 

# Gráficos em Tempo Real
g_display = graph(title='Monitoramento Ambiental', width=900, height=200, 
                  xtitle='Tempo (s)', ytitle='Escalas Variadas', fast=False, scroll=True, xmin=0, xmax=50)

plot_temp = gcurve(color=color.red, label='Temperatura (°C)')
plot_press = gcurve(color=color.blue, label='Pressão (hPa/10 - Norm)')
plot_sol = gcurve(color=color.yellow, label='Radiação Solar')

# --- 2. CLASSE: O SOL (Motor do Dia/Noite) ---

class CicloSolar:
    def __init__(self):
        self.raio_orbita = 80
        self.angulo = 0.5
        self.velocidade = 0.2
        
        self.esfera = sphere(pos=vec(self.raio_orbita, 0, 0), radius=5, color=color.yellow, emissive=True)
        self.luz = local_light(pos=self.esfera.pos, color=color.white)
        
        self.eh_dia = True
        self.fator_iluminacao = 1.0 # 0 a 1

    def atualizar(self, dt, tem_tempestade):
        self.angulo += self.velocidade * dt
        x = self.raio_orbita * cos(self.angulo)
        y = self.raio_orbita * sin(self.angulo)
        
        self.esfera.pos = vec(x, y, 0)
        self.luz.pos = self.esfera.pos
        
        # Altura normalizada (-1 a 1)
        altura_norm = y / self.raio_orbita
        self.fator_iluminacao = max(0, altura_norm) # Apenas valores positivos para luz
        
        # Lógica do Céu (Prioridade: Tempestade > Noite > Dia)
        if tem_tempestade:
            target_bg = vec(0.15, 0.15, 0.2) # Cinza chumbo
            self.luz.color = vec(0.3, 0.3, 0.3) # Sol fica fraco
            self.eh_dia = False # Consideramos "escuro" para acender luzes
        elif altura_norm > 0:
            # Dia Claro
            target_bg = vec(0.4*altura_norm, 0.7*altura_norm, 1.0*altura_norm)
            self.luz.color = vec(1, 1, 1) * (0.3 + 0.7*altura_norm)
            self.eh_dia = True
        else:
            # Noite
            target_bg = vec(0, 0, 0.05)
            self.luz.color = vec(0.1, 0.1, 0.15) # Luz da lua
            self.eh_dia = False
            
        scene.background = target_bg

# --- 3. CLASSE: TRÁFEGO (Carros com Faróis) ---

class Carro:
    def __init__(self, eixo, direcao):
        self.eixo = eixo
        self.direcao = direcao
        start = -60 * direcao
        offset = 3.5 * direcao
        
        cor = vec(random.random(), random.random(), random.random())
        if eixo == 'x':
            pos = vec(start, 0.6, offset)
            size = vec(4, 1.5, 2)
            self.vel_vec = vec(1, 0, 0)
        else:
            pos = vec(-offset, 0.6, start)
            size = vec(2, 1.5, 4)
            self.vel_vec = vec(0, 0, 1)
            
        self.body = box(pos=pos, size=size, color=cor)
        self.cabin = box(pos=pos + vec(0,1,0), size=size*0.6, color=color.black)
        
        self.speed = (15 + random.random()*15) * direcao
        
        # Faróis (Cones de luz)
        self.farois = []
        for i in [-1, 1]:
            f_pos_offset = vec(2, 0, i*0.5) if eixo == 'x' else vec(i*0.5, 0, 2)
            if direcao == -1: f_pos_offset *= -1
            
            # Direção do faixo de luz
            dir_luz = self.vel_vec * direcao
            
            luz = cone(pos=pos + f_pos_offset, axis=dir_luz*6, radius=1.5, color=color.yellow, opacity=0.3, visible=False)
            self.farois.append({'obj': luz, 'offset': f_pos_offset})

    def mover(self, dt, escuro):
        # Física de movimento
        delta = vec(0,0,0)
        if self.eixo == 'x': delta = vec(self.speed*dt, 0, 0)
        else: delta = vec(0, 0, self.speed*dt)
        
        self.body.pos += delta
        self.cabin.pos += delta
        
        # Atualiza Faróis
        for f in self.farois:
            f['obj'].pos = self.body.pos + f['offset']
            f['obj'].visible = escuro # Acende se estiver escuro (Noite ou Chuva)
            
        # Loop infinito (Teleporte)
        limite = 65
        if (self.eixo == 'x' and abs(self.body.pos.x) > limite) or \
           (self.eixo == 'z' and abs(self.body.pos.z) > limite):
             fator_inv = -1
             if self.eixo == 'x': 
                 self.body.pos.x *= fator_inv
                 self.cabin.pos.x *= fator_inv
             else:
                 self.body.pos.z *= fator_inv
                 self.cabin.pos.z *= fator_inv

# --- 4. CLASSE: INFRAESTRUTURA ---

class Cidade:
    def __init__(self):
        # Chão
        box(pos=vec(0, -0.5, 0), size=vec(140, 1, 140), color=vec(0.1, 0.25, 0.1))
        
        # Ruas
        box(pos=vec(0, 0.01, 0), size=vec(140, 0.1, 14), color=vec(0.2, 0.2, 0.2))
        
        self.postes = []
        self.predios = []
        
        # Coordenadas da escola para evitar sobreposição
        self.escola_pos = vec(35, 0, 35)
        
        self.construir()
        self.add_escola() # Adiciona a escola específica
        
    def construir(self):
        
        # Prédios Aleatórios
        for x in range(-55, 60, 18):
            for z in range(-55, 60, 18):
                # Regras: Longe da rua central E longe da escola
                distancia_escola = mag(vec(x,0,z) - self.escola_pos)
                
                if abs(x) > 12 and abs(z) > 12 and distancia_escola > 20 and random.random() > 0.25:
                    self.add_predio(x, z)

    def add_escola(self):
        # Localização fixa
        x, z = self.escola_pos.x * -1, self.escola_pos.z
        comp = 25 # Comprimento (Escola é horizontal)
        larg = 12
        h = 7     # Altura baixa
        
        # Corpo Principal (Branco/Gelo)
        box(pos=vec(x, h/2, z), size=vec(comp, h, larg), color=vec(0.9, 0.95, 1.0))
        
        # Telhado (Avermelhado)
        box(pos=vec(x, h + 0.5, z), size=vec(comp+2, 1, larg+2), color=vec(0.6, 0.3, 0.2))
        
        # Letreiro ESCOLA (usando objetos textuais ou simulado)
        # Vamos fazer um letreiro 3D simples
        label(pos=vec(x, h + 4, z), text="ESCOLA ESTADUAL", height=15, border=4, color=color.white, box=False, opacity=0)
        
        # Entrada Principal (Azul - comum em escolas públicas)
        box(pos=vec(x, 2, z + larg/2 + 0.1), size=vec(5, 4, 0.5), color=color.blue)
        
        # Janelas (Série horizontal)
        janelas_group = []
        for jx in range(int(x - comp/2 + 3), int(x + comp/2 - 2), 4):
            # Não desenhar janela em cima da porta
            if abs(jx - x) > 3:
                w = box(pos=vec(jx, h/2, z + larg/2 + 0.1), size=vec(2, 2, 0.2), color=color.black)
                janelas_group.append(w)
        
        self.predios.append(janelas_group)

    def add_predio(self, x, z):
        h = 8 + random.random()*16
        w = 5 + random.random()*4
        cor = vec(random.random()*0.5, random.random()*0.5, random.random()*0.5 + 0.2)
        box(pos=vec(x, h/2, z), size=vec(w, h, w), color=cor)
        
        # Janelas
        wins = []
        for yi in range(2, int(h), 3):
            w1 = box(pos=vec(x, yi, z+w/2+0.1), size=vec(w-1, 1.5, 0.1), color=color.black)
            w2 = box(pos=vec(x, yi, z-w/2-0.1), size=vec(w-1, 1.5, 0.1), color=color.black)
            wins.append(w1)
            wins.append(w2)
        self.predios.append(wins)

    def gerenciar_luzes(self, escuro):
        # Se estiver escuro (Noite ou Chuva), acende luzes
        cor_poste = color.yellow if escuro else color.black
        emissao = True if escuro else False
        
        for p in self.postes:
            p.color = cor_poste
            p.emissive = emissao
            
        # Janelas (Lógica probabilística para não piscar loucamente)
        # Apenas mudamos se o estado dia/noite mudou, controlado no main loop

# --- 5. CLASSE: ESTAÇÃO METEOROLÓGICA (Cérebro) ---

class Estacao:
    def __init__(self, sol_obj):
        self.sol = sol_obj
        self.pressao = 1013.0
        self.temperatura = 27.0
        self.tempo = 0
        self.chuva_ativa = False
        self.gotas = []
        
        # Sensor
        self.base = box(pos=vec(18, 8, 18), size=vec(3, 3, 3), color=color.white)
        self.label = label(pos=vec(18, 11, 18), text="Init", height=10, border=2)

    def atualizar(self, dt):
        self.tempo += dt
        
        # 1. Lógica de Chuva (Baseada na Pressão do Usuário)
        threshold_chuva = 995
        self.chuva_ativa = self.pressao < threshold_chuva
        
        if self.chuva_ativa:
            self.gerar_chuva()
        else:
            self.limpar_chuva()
            
        # 2. Lógica de Temperatura (Baseada no Sol + Efeito da Chuva)
        # Sol alto = Quente (31). Sol baixo/Noite = Frio (23).
        # Chuva resfria o ambiente (-2 graus).
        
        temp_alvo = 23.0
        if self.sol.fator_iluminacao > 0:
            temp_alvo += self.sol.fator_iluminacao * 8 # Delta de 8 graus (23->31)
            
        if self.chuva_ativa:
            temp_alvo -= 2.0 # Resfriamento por evaporação
            
        # Inércia térmica (suavização)
        self.temperatura = self.temperatura + (temp_alvo - self.temperatura) * 0.05
        
        # 3. Visualização
        norm_t = (self.temperatura - 21) / (31 - 21) # Ajustei range p/ 21 por causa da chuva
        norm_t = max(0, min(1, norm_t))
        self.base.color = vec(norm_t, 0, 1 - norm_t)
        
        status = "CHUVA" if self.chuva_ativa else "SECO"
        self.label.text = f"T: {self.temperatura:.1f}C\nP: {self.pressao:.0f}hPa\n{status}"
        
        # 4. Gráficos
        plot_temp.plot(self.tempo, self.temperatura)
        # Normaliza pressão visualmente para caber no gráfico
        plot_press.plot(self.tempo, (self.pressao - 950)/5 + 20) 
        plot_sol.plot(self.tempo, 20 + self.sol.fator_iluminacao * 10)

    def gerar_chuva(self):
        # Cria gotas
        if len(self.gotas) < 150:
            g = sphere(pos=vec(random.random()*100-50, 40+random.random()*10, random.random()*100-50), 
                       radius=0.2, color=vec(0.6, 0.6, 1), emissive=True)
            g.v = vec(0, -35, 0)
            self.gotas.append(g)
            
        for g in self.gotas:
            g.pos += g.v * 0.05
            if g.pos.y < 0: g.pos.y = 40 + random.random()*10
            g.visible = True

    def limpar_chuva(self):
        for g in self.gotas: g.visible = False

# --- 6. LEGENDA ---
class Legenda:
    def __init__(self):
        painel = vec(26, 5, 18)
        box(pos=painel, size=vec(6, 10, 0.5), color=color.black, opacity=0.8)
        label(pos=painel+vec(0, 4.5, 0), text="ESCALA", height=10, box=False, color=color.white)
        
        temps = [31, 27, 23]
        y = 2
        for t in temps:
             n = (t - 21) / 10
             c = vec(n, 0, 1-n)
             box(pos=painel+vec(-1.5, y, 0.3), size=vec(1.5, 1.5, 0.1), color=c, emissive=True)
             label(pos=painel+vec(1.5, y, 0.3), text=f"{t}C", height=10, box=False)
             y -= 2.5

# --- 7. INSTANCIAÇÃO E CONTROLES ---

sol = CicloSolar()
cidade = Cidade()
estacao = Estacao(sol)
legenda_obj = Legenda()

# Frota de carros
carros = []
# Carros apenas no eixo X (uma única rua)
for _ in range(5): carros.append(Carro('x', 1))
for _ in range(5): carros.append(Carro('x', -1))

# Slider de Pressão
def muda_pressao(s):
    estacao.pressao = s.value
    wt_p.text = f'{s.value:.0f} hPa'

scene.append_to_caption('\n<b>CONTROLE CLIMÁTICO</b>\n')
scene.append_to_caption('Pressão (<995 inicia tempestade): ')
slider(min=980, max=1040, value=1013, length=250, bind=muda_pressao)
wt_p = wtext(text='1013 hPa')

# --- 8. LOOP PRINCIPAL ---
dt = 0.05
estado_anterior_escuro = False

while True:
    rate(30)
    
    # Atualiza Física Climática
    # Verifica se está escuro (pode ser Noite OU Tempestade)
    esta_escuro = (not sol.eh_dia) or estacao.chuva_ativa
    
    sol.atualizar(dt, estacao.chuva_ativa)
    estacao.atualizar(dt)
    
    # Atualiza Infraestrutura se o estado de luz mudou
    if esta_escuro != estado_anterior_escuro:
        cidade.gerenciar_luzes(esta_escuro)
        # Atualiza janelas dos prédios (aleatório)
        for predio_wins in cidade.predios:
            for w in predio_wins:
                if esta_escuro and random.random() > 0.4:
                    w.color = color.yellow
                    w.emissive = True
                else:
                    w.color = color.black
                    w.emissive = False
        estado_anterior_escuro = esta_escuro

    # Move Carros
    for c in carros:
        c.mover(dt, esta_escuro)
