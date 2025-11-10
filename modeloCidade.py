from vpython import *
import random

scene.title = "Cidade Densa com Praça, Avenidas e Carros"
scene.width = 1000
scene.height = 600
scene.background = vector(0.53, 0.81, 0.92)
scene.center = vector(0,7,0)
scene.range = 40

#camera de visualização 
def vistaAerea(b):
    scene.userzoom = False
    scene.userspin = False
    scene.forward = vector(-1, -0.8, -1)  # direção da câmera
    scene.center = vector(0, 7, 0)        # ponto para onde a câmera olha
    scene.range = 40      
botao = button(text="vista aerea", bind=vistaAerea)

# Chão
chao = box(pos=vector(0, 0, 0), size=vector(70, 0.5, 70), color=color.gray(0.5))

def cor_temperatura(temp):
    temp = max(0, min(50, temp))
    r = temp / 50
    b = 1 - r
    g = 0.2
    return vector(r, g, b)

num_lados = 14
espaco = 4.5
tamanho_praca = 10
raio_avenida = 5  # largura das avenidas

# Criação das avenidas horizontais e verticais
avenida_h = box(pos=vector(0, 0.26, 0), size=vector(70, 0.52, raio_avenida), color=color.black)
avenida_v = box(pos=vector(0, 0.26, 0), size=vector(raio_avenida, 0.52, 70), color=color.black)

predios = []
TEXTURAS_PREDIOS = ("https://i.ibb.co/Kz5d2yY7/janelas-1.jpg","https://i.ibb.co/HTJPd7yG/facada-de-edificio-de-concreto-com-muitas-janelas-23-2151966493.png","https://i.ibb.co/Y4c8BYWP/Buildings-High-Rise0628-2-350.jpg","https://i.ibb.co/qMpzK2bZ/janela-2.png","https://i.ibb.co/4ZtwPW65/7f78f1b27bd53188883b678f69284a38.jpg","https://i.ibb.co/JR9RX1QR/1000-F-193615255-tzxio-ZKHVFo-Lq5l-Cn-Dr-WQaysx-Ql4-B55v.jpg")
numTexturasPredios = len(TEXTURAS_PREDIOS)-1
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
        grauCinzaCobertura = random.uniform(0,0.6)
        largura = random.uniform(2.0, 3.5)
        profundidade = random.uniform(2.0, 3.5)
        altura = random.uniform(2.8, 10)
        temp = random.uniform(0, 50)
        pressao = random.uniform(1, 4)
        texturaIndex = random.randint(0,numTexturasPredios)

        predio = box(pos=vector(x, altura/2, z), size=vector(largura, altura, profundidade),texture=TEXTURAS_PREDIOS[texturaIndex])
        cobertura = box(pos=vector(x,altura,z), size=vector(largura,0.05,profundidade),color=color.gray(grauCinzaCobertura))
        
        press = cylinder(pos=vector(x, altura, z), axis=vector(0, pressao, 0),
                         radius=largura/20, color=color.white, opacity=0.7)
        

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

#temp_text = label(pos=vector(0,12,0), text="Temperatura (azul-frio, vermelho-quente)", box=False, height=10)
#press_text = label(pos=vector(0,10,0), text="Pressão (altura do cilindro)", box=False, height=10)

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
            if carro.pos.z > 25:
                carro.pos.z = -35
                carro.color = random.choice(cores_carros)
                
while True:
    rate(100)
    
    # Atualiza cor temperatura dos prédios
    for p, temp, pressao in predios:
        temp = random.uniform(0, 50)
        p.color = cor_temperatura(temp)