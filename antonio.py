Web VPython 3.2
from vpython import *
import random


scene.title = "Simulação Colegio Villa: Ciclo Circadiano & Clima"
scene.width = 900
scene.height = 600
scene.center = vec(0, 5, -10)
scene.camera.pos = vec(60, 70, 90) 
scene.camera.axis = vec(-60, -70, -90)
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
        self.raio_orbita = 120
        self.angulo = 0.5 # Começa de manhã
        self.velocidade = 0.2 # Velocidade da passagem do tempo
        
        self.esfera = sphere(pos=vec(self.raio_orbita, 0, 0), radius=2, color=color.yellow, emissive=True)
        self.luz = local_light(pos=self.esfera.pos, color=color.white)
        
        self.eh_dia = True
        self.fator_iluminacao = 1.0 # 0 a 1

    def atualizar(self, dt, tem_tempestade):
        self.angulo += self.velocidade * dt
        x = self.raio_orbita * cos(self.angulo)
        y = self.raio_orbita * sin(self.angulo)
        
        self.esfera.pos = vec(x, y, 0)
        self.luz.pos = self.esfera.pos
        
        altura_norm = y / self.raio_orbita
        self.fator_iluminacao = max(0, altura_norm)
        
        if tem_tempestade:
            target_bg = vec(0.15, 0.15, 0.2)
            self.luz.color = vec(0.3, 0.3, 0.3)
            self.eh_dia = False
        elif altura_norm > 0:
            target_bg = vec(0.4*altura_norm, 0.7*altura_norm, 1.0*altura_norm)
            self.luz.color = vec(1, 1, 1) * (0.3 + 0.7*altura_norm)
            self.eh_dia = True
        else:
            target_bg = vec(0, 0, 0.05)
            self.luz.color = vec(0.1, 0.1, 0.15)
            self.eh_dia = False
            
        scene.background = target_bg

# --- 3. CLASSE: TRÁFEGO (Carros) ---

class Carro:
    def __init__(self, eixo, direcao, z_base=0):
        self.eixo = eixo
        self.direcao = direcao
        self.z_base = z_base
        start = -60 * direcao
        offset = 3.5 # Offset fixo positivo para alinhar na mão correta da via
        
        cor = vec(random.random(), random.random(), random.random())
        
        if eixo == 'x':
            # Se direcao é 1 (vai p/ direita), fica no lado direito da rua (offset positivo em Z se considerarmos a via)
            # Para simplificar vias de mão única, vamos apenas variar aleatoriamente a faixa (pista 1 ou 2)
            faixa = random.choice([2, 5]) 
            # Se a rua vai para a esquerda (-1), invertemos a logica visual se quiséssemos mão inglesa, 
            # mas aqui é mão única total, então carros ocupam toda largura
            
            pos = vec(start, 0.6, self.z_base + faixa * (1 if direcao == 1 else -1))
            size = vec(4, 1.5, 2)
            self.vel_vec = vec(1, 0, 0)
        else:
            pos = vec(-offset, 0.6, start)
            size = vec(2, 1.5, 4)
            self.vel_vec = vec(0, 0, 1)
            
        self.body = box(pos=pos, size=size, color=cor)
        self.cabin = box(pos=pos + vec(0,1,0), size=size*0.6, color=color.black)
        self.speed = (random.random()*14) * direcao
        
        self.farois = []
        for i in [-1, 1]:
            # Ajuste manual do offset local para alinhar com o carro
            f_local_offset = vec(2, 0, i*0.5) 
            if direcao == -1: f_local_offset = vec(-2, 0, i*0.5) # Inverte para X negativo
            
            dir_luz = self.vel_vec * direcao
            luz = cone(pos=pos + f_local_offset, axis=dir_luz*6, radius=1.5, color=color.yellow, opacity=0.3, visible=False)
            self.farois.append({'obj': luz, 'local_offset': f_local_offset})

    def mover(self, dt, escuro):
        delta = vec(0,0,0)
        if self.eixo == 'x': delta = vec(self.speed*dt, 0, 0)
        else: delta = vec(0, 0, self.speed*dt)
        
        self.body.pos += delta
        self.cabin.pos += delta
        
        for f in self.farois:
            f['obj'].pos = self.body.pos + f['local_offset']
            f['obj'].visible = escuro 
            
        limite = 90
        if self.eixo == 'x':
            if abs(self.body.pos.x) > limite:
                # Teletransporte para o outro lado mantendo a direção
                self.body.pos.x = -limite if self.direcao == 1 else limite
                self.cabin.pos.x = -limite if self.direcao == 1 else limite

# --- 4. CLASSE: TREM DO METRÔ ---

class TremMetro:
    def __init__(self, z_linha, direcao):
        self.z_linha = z_linha
        self.velocidade = 50 
        self.direcao = direcao # 1 ou -1
        
        # Posição inicial depende da direção
        pos_x = -90 if direcao == 1 else 90
        self.posicao = vec(pos_x, 1.5, z_linha)
        
        self.vagoes = []
        cor_trem = vec(0.8, 0.8, 0.9) 
        
        for i in range(3):
            # Se vai p/ direita, vagões para tras (esquerda). Se vai p/ esquerda, vagões p/ direita.
            offset_x = i * -14 * direcao 
            
            v = box(pos=vec(pos_x + offset_x, 1.8, z_linha), size=vec(12, 3, 3.2), color=cor_trem)
            faixa = box(pos=vec(pos_x + offset_x, 1.8, z_linha), size=vec(12.1, 0.5, 3.3), color=color.blue)
            
            janelas = []
            for j in range(-4, 5, 2):
                win = box(pos=vec(pos_x + offset_x + j, 2.2, z_linha), size=vec(1.5, 1, 3.4), color=color.black)
                janelas.append(win)
                
            self.vagoes.append({'corpo': v, 'faixa': faixa, 'janelas': janelas, 'offset_inicial': offset_x})

        # Luz frontal
        frente_x = 6 * direcao
        self.farol = cone(pos=vec(pos_x + frente_x, 1.5, z_linha), axis=vec(10 * direcao, -2, 0), radius=3, color=color.white, opacity=0.3, visible=False)

    def mover(self, dt, escuro):
        deslocamento = self.velocidade * dt * self.direcao
        self.posicao.x += deslocamento
        
        # Atualiza posições reais
        for vagao in self.vagoes:
            vagao['corpo'].pos.x = self.posicao.x + vagao['offset_inicial']
            vagao['faixa'].pos.x = self.posicao.x + vagao['offset_inicial']
            
            base_janela_x = -4
            for win in vagao['janelas']:
                win.pos.x = vagao['corpo'].pos.x + base_janela_x
                base_janela_x += 2

        frente_x = 6 * self.direcao
        self.farol.pos = vec(self.posicao.x + frente_x, 1.5, self.z_linha)
        self.farol.visible = escuro

        # Loop (Teleporte)
        if self.direcao == 1 and self.posicao.x > 110:
            self.posicao.x = -110
        elif self.direcao == -1 and self.posicao.x < -110:
            self.posicao.x = 110

# --- 5. CLASSE: INFRAESTRUTURA ---

class Cidade:
    def __init__(self):
        # Chão
        box(pos=vec(0, -0.5, 0), size=vec(220, 1, 160), color=vec(0.1, 0.25, 0.1))
        
        # Avenida 1 (Z=0) - Sentido DIREITA (1)
        box(pos=vec(0, 0.01, 0), size=vec(220, 0.1, 14), color=vec(0.2, 0.2, 0.2))
        
        # Avenida 2 (Z=-24) - Sentido ESQUERDA (-1)
        self.z_avenida2 = -24
        box(pos=vec(0, 0.01, self.z_avenida2), size=vec(220, 0.1, 14), color=vec(0.2, 0.2, 0.2))
        
        # Setas indicativas no chão
        for x in range(-80, 81, 40):
            # Seta Av 1 (Direita >)
            arrow(pos=vec(x, 0.1, 0), axis=vec(5, 0, 0), color=color.white, shaftwidth=0.5)
            # Seta Av 2 (Esquerda <)
            arrow(pos=vec(x, 0.1, self.z_avenida2), axis=vec(-5, 0, 0), color=color.white, shaftwidth=0.5)

        self.postes = []
        self.predios = []
        self.escola_pos = vec(0, 0, 22)
        
        # Z das linhas de metrô
        self.z_metro1 = -36 # Ida
        self.z_metro2 = -42 # Volta
        
        self.construir_luzes()
        self.add_linhas_metro()
        self.add_escola()
        self.add_circo()
        self.add_estacionamento()
        self.add_bosque()
        
    def construir_luzes(self):
        for i in range(-60, 61, 20):
            self.add_poste(i, 9)
            self.add_poste(i, -9)
            self.add_poste(i, self.z_avenida2 + 9)
            self.add_poste(i, self.z_avenida2 - 9)

    def add_linhas_metro(self):
        # Base de brita (pedras) - Agora mais larga para caber duas linhas
        z_centro_metro = (self.z_metro1 + self.z_metro2) / 2
        largura_base = abs(self.z_metro1 - self.z_metro2) + 6
        box(pos=vec(0, 0.1, z_centro_metro), size=vec(220, 0.2, largura_base), color=vec(0.4, 0.4, 0.4))
        
        # --- LINHA 1 ---
        # Trilhos (Ferro)
        box(pos=vec(0, 0.3, self.z_metro1 - 1.5), size=vec(220, 0.2, 0.2), color=vec(0.7, 0.7, 0.75))
        box(pos=vec(0, 0.3, self.z_metro1 + 1.5), size=vec(220, 0.2, 0.2), color=vec(0.7, 0.7, 0.75))
        # Dormentes
        for x in range(-110, 110, 2):
            box(pos=vec(x, 0.2, self.z_metro1), size=vec(1, 0.15, 4), color=vec(0.3, 0.2, 0.1))

        # --- LINHA 2 ---
        # Trilhos (Ferro)
        box(pos=vec(0, 0.3, self.z_metro2 - 1.5), size=vec(220, 0.2, 0.2), color=vec(0.7, 0.7, 0.75))
        box(pos=vec(0, 0.3, self.z_metro2 + 1.5), size=vec(220, 0.2, 0.2), color=vec(0.7, 0.7, 0.75))
        # Dormentes
        for x in range(-110, 110, 2):
            box(pos=vec(x, 0.2, self.z_metro2), size=vec(1, 0.15, 4), color=vec(0.3, 0.2, 0.1))
            
        # Postes de eletricidade Centrais (Catenária dupla)
        for x in range(-80, 81, 40):
            # Poste no meio das duas linhas
            cylinder(pos=vec(x, 0, z_centro_metro), axis=vec(0, 8, 0), radius=0.3, color=color.gray(0.3))
            # Braço duplo T
            box(pos=vec(x, 8, z_centro_metro), size=vec(0.2, 0.2, 10), color=color.gray(0.3))

    def add_escola(self):
        x, z = self.escola_pos.x, self.escola_pos.z
        comp, larg, h = 30, 20, 8
        box(pos=vec(x, h/2, z), size=vec(comp, h, larg), color=vec(0.9, 0.95, 1.0))
        box(pos=vec(x, h + 0.5, z), size=vec(comp+2, 1, larg+2), color=vec(0.6, 0.3, 0.2))
        label(pos=vec(x, h + 4, z - larg/2), text="ESCOLA VILLA", height=15, border=4, color=color.white, box=False, opacity=0)
        
        janelas_group = []
        for jx in range(int(x - comp/2 + 3), int(x + comp/2 - 2), 4):
            if abs(jx - x) > 3:
                w = box(pos=vec(jx, h/2, z - larg/2 - 0.1), size=vec(2, 2, 0.2), color=color.black)
                janelas_group.append(w)
                
        self.predios.append(janelas_group)

    def add_circo(self):
        pos = self.escola_pos + vec(-35, 0, 0) 
        r_base, h_base = 8, 6
        for angle_deg in range(0, 360, 15):
            angle = radians(angle_deg)
            x, z = r_base * cos(angle), r_base * sin(angle)
            cor = color.red if (angle_deg % 30 == 0) else color.white
            cylinder(pos=pos + vec(x, 0, z), axis=vec(0, h_base, 0), radius=1.3, color=cor)
        cone(pos=pos + vec(0, h_base, 0), axis=vec(0, 8, 0), radius=r_base + 2, color=color.red)
        box(pos=pos + vec(0, 2, -r_base), size=vec(4, 4, 2), color=color.black)
        label(pos=pos + vec(0, h_base + 2, -r_base - 1), text="CIRCO", height=12, border=2, color=color.yellow, box=False, opacity=0)

    def add_estacionamento(self):
        pos = self.escola_pos + vec(35, 0.05, 0)
        largura_est = 30
        profundidade_est = 20
        box(pos=pos, size=vec(largura_est, 0.1, profundidade_est), color=vec(0.3, 0.3, 0.35))
        cylinder(pos=pos + vec(0, 0, -profundidade_est/2), axis=vec(0,5,0), radius=0.2, color=color.gray(0.5))
        label(pos=pos + vec(0, 5.5, -profundidade_est/2), text="ESTACIONAMENTO", height=10, box=True, opacity=0.5)
        
        start_x = pos.x - largura_est/2 + 4
        for i in range(5):
            x_slot = start_x + i * 5.5
            box(pos=vec(x_slot - 2.75, 0.1, pos.z), size=vec(0.2, 0.12, profundidade_est-2), color=color.white)
            if random.random() > 0.3:
                cor_c = vec(random.random(), random.random(), random.random())
                box(pos=vec(x_slot, 1, pos.z), size=vec(3, 1.5, 4), color=cor_c)
                box(pos=vec(x_slot, 1.8, pos.z), size=vec(2.5, 0.8, 2.5), color=color.black)

    def add_bosque(self):
        for _ in range(250):
            x = random.uniform(-100, 100)
            z = random.uniform(42, 75)
            self.add_arvore(x, z)
            
    def add_arvore(self, x, z):
        cylinder(pos=vec(x, 0, z), axis=vec(0, 2.5, 0), radius=0.5, color=vec(0.4, 0.25, 0.1))
        h_copa = 4 + random.uniform(0, 2)
        r_copa = 2 + random.uniform(0, 1)
        cor_verde = vec(0, 0.5 + random.uniform(0, 0.3), 0)
        cone(pos=vec(x, 2.5, z), axis=vec(0, h_copa, 0), radius=r_copa, color=cor_verde)

    def add_poste(self, x, z):
        cylinder(pos=vec(x, 0, z), axis=vec(0, 7, 0), radius=0.3, color=color.gray(0.4))
        luz = sphere(pos=vec(x, 7, z), radius=0.6, color=color.black, emissive=False)
        self.postes.append(luz)

    def gerenciar_luzes(self, escuro):
        cor_poste = color.yellow if escuro else color.black
        emissao = True if escuro else False
        for p in self.postes:
            p.color = cor_poste
            p.emissive = emissao

# --- 5. CLASSE: ESTAÇÃO METEOROLÓGICA ---

class Estacao:
    def __init__(self, sol_obj):
        self.sol = sol_obj
        self.pressao = 1013.0
        self.temperatura = 27.0
        self.tempo = 0
        self.chuva_ativa = False
        self.gotas = []
        self.base = box(pos=vec(18, 8, 18), size=vec(3, 3, 3), color=color.white)
        self.label = label(pos=vec(18, 11, 18), text="Init", height=10, border=2)

    def atualizar(self, dt):
        self.tempo += dt
        threshold_chuva = 995
        self.chuva_ativa = self.pressao < threshold_chuva
        if self.chuva_ativa: self.gerar_chuva()
        else: self.limpar_chuva()
            
        temp_alvo = 23.0 + (self.sol.fator_iluminacao * 8 if self.sol.fator_iluminacao > 0 else 0)
        if self.chuva_ativa: temp_alvo -= 2.0
        self.temperatura += (temp_alvo - self.temperatura) * 0.05
        
        norm_t = max(0, min(1, (self.temperatura - 21) / 10))
        self.base.color = vec(norm_t, 0, 1 - norm_t)
        status = "CHUVA" if self.chuva_ativa else "SECO"
        self.label.text = f"T: {self.temperatura:.1f}C\nP: {self.pressao:.0f}hPa\n{status}"
        
        plot_temp.plot(self.tempo, self.temperatura)
        plot_press.plot(self.tempo, (self.pressao - 950)/5 + 20) 
        plot_sol.plot(self.tempo, 20 + self.sol.fator_iluminacao * 10)

    def gerar_chuva(self):
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

# --- 7. INSTANCIAÇÃO ---

sol = CicloSolar()
cidade = Cidade()
estacao = Estacao(sol)

# Trens do Metrô
metro1 = TremMetro(cidade.z_metro1, 1)  # Linha 1: Vai para a direita
metro2 = TremMetro(cidade.z_metro2, -1) # Linha 2: Vai para a esquerda

# Frota de carros
carros = []
# Avenida 1 (Z=0) -> SÓ VAI PARA A DIREITA (1)
for _ in range(8): carros.append(Carro('x', 1, z_base=0))

# Avenida 2 (Z=-24) -> SÓ VAI PARA A ESQUERDA (-1)
for _ in range(8): carros.append(Carro('x', -1, z_base=-24))

# Slider
def muda_pressao(s):
    estacao.pressao = s.value
    wt_p.text = f'{s.value:.0f} hPa'

scene.append_to_caption('\n<b>CONTROLE CLIMÁTICO</b>\n')
scene.append_to_caption('Pressão (<995 inicia tempestade): ')
slider(min=980, max=1040, value=1013, length=250, bind=muda_pressao)
wt_p = wtext(text='1013 hPa')

# --- 8. LOOP ---
dt = 0.05
estado_anterior_escuro = False

while True:
    rate(30)
    esta_escuro = (not sol.eh_dia) or estacao.chuva_ativa
    
    sol.atualizar(dt, estacao.chuva_ativa)
    estacao.atualizar(dt)
    
    if esta_escuro != estado_anterior_escuro:
        cidade.gerenciar_luzes(esta_escuro)
        for predio_wins in cidade.predios:
            for w in predio_wins:
                if esta_escuro and random.random() > 0.4:
                    w.color = color.yellow
                    w.emissive = True
                else:
                    w.color = color.black
                    w.emissive = False
        estado_anterior_escuro = esta_escuro

    for c in carros:
        c.mover(dt, esta_escuro)
        
    metro1.mover(dt, esta_escuro)
    metro2.mover(dt, esta_escuro)
