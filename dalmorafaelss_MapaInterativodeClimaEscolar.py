from vpython import *
#Web VPython 3.2
from vpython import *
import random

scene.title = "Cidade Densa com Praça, Avenidas e Carros"
scene.width = 1000
scene.height = 600
scene.background = color.black
scene.center = vector(0,7,0)
scene.range = 40

# Chão
chao = box(pos=vector(0, 0, 0), size=vector(70, 0.5, 70), color=vector(0.2, 0.6, 0.2))

def cor_temperatura(temp):
    temp = max(0, min(50, temp))
    r = temp / 50
    b = 1 - r
    g = 0.2
    return vector(r, g, b)

num_lados = 14
espaco = 4.5
tamanho_praca = 10
raio_avenida = 8  # largura das avenidas

# Criação das avenidas horizontais e verticais
avenida_h = box(pos=vector(0, 0.26, 0), size=vector(70, 0.52, raio_avenida), color=color.black)
avenida_v = box(pos=vector(0, 0.26, 0), size=vector(raio_avenida, 0.52, 70), color=color.black)

predios = []
for i in range(-num_lados//2, num_lados//2 + 1):
    for j in range(-num_lados//2, num_lados//2 + 1):
        x = i * espaco
        z = j * espaco

        # Espaço para a praça central (vazio)
        if abs(x) < tamanho_praca/2 and abs(z) < tamanho_praca/2:
            continue

        # Espaço para as avenidas (vazios)
        if abs(z) < raio_avenida/2 and abs(x) < 35:
            continue
        if abs(x) < raio_avenida/2 and abs(z) < 35:
            continue

        # Prédios pequenos e variados
        largura = random.uniform(2.0, 3.5)
        profundidade = random.uniform(2.0, 3.5)
        altura = random.uniform(2.8, 10)
        temp = random.uniform(0, 50)
        pressao = random.uniform(1, 4)

        predio = box(pos=vector(x, altura/2, z), size=vector(largura, altura, profundidade),
                     color=cor_temperatura(temp))
        
        press = cylinder(pos=vector(x, altura, z), axis=vector(0, pressao, 0),
                         radius=largura/4, color=color.white, opacity=0.7)
        
        # Janelas
        num_janelas_altura = int(altura // 2)
        for k in range(num_janelas_altura):
            y = 2 * k + 1.1
            for lado in [-1, 1]:
                janela = box(pos=vector(x + lado * (largura / 2 + 0.05), y, z),
                             size=vector(0.3, 0.7, profundidade / 4),
                             color=color.yellow if random.random() > 0.3 else color.black)
        predios.append((predio, temp, pressao))

# Praça central
'''praca = box(pos=vector(0, 0.51, 0), size=vector(tamanho_praca, 0.02, tamanho_praca), color=vector(0.4, 0.7, 0.4))
label(pos=vector(0, 2, 0), text="PRAÇA CENTRAL", box=True, height=16, color=color.white, opacity=0.6)'''

# Configuração dos carros nas avenidas, com espaçamento
carros = []
cores_carros = [color.red, color.blue, color.orange, color.white, color.green]
num_carros_h = 5
num_carros_v = 5
espaco_carros = 14

for i in range(num_carros_h):
    carro = box(pos=vector(-35 + i*espaco_carros, 0.7, 0), size=vector(2.2, 1, 1.2), color=random.choice(cores_carros))
    carros.append(("h", carro))

for i in range(num_carros_v):
    carro = box(pos=vector(0, 0.7, -35 + i*espaco_carros), size=vector(1.2, 1, 2.2), color=random.choice(cores_carros))
    carros.append(("v", carro))

temp_text = label(pos=vector(0,12,0), text="Temperatura (azul-frio, vermelho-quente)", box=False, height=10)
press_text = label(pos=vector(0,10,0), text="Pressão (altura do cilindro)", box=False, height=10)

# Sol
sol = sphere(pos=vector(-70, 50, -70), radius=6, color=color.yellow, emissive=True)
# Animação principal
while True:
    rate(30)
    for tipo, carro in carros:
        if tipo == "h":
            carro.pos.x += 0.7
            if carro.pos.x > 35:
                carro.pos.x = -35
                carro.color = random.choice(cores_carros)
        else:
            carro.pos.z += 0.7
            if carro.pos.z > 35:
                carro.pos.z = -35
                carro.color = random.choice(cores_carros)
                
while True:
    rate(100)
    
    # Atualiza cor temperatura dos prédios
    for p, temp, pressao in predios:
        temp = random.uniform(0, 50)
        p.color = cor_temperatura(temp)
