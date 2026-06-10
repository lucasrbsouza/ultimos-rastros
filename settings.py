import sys
from levels import *

DEV_MODE = '--dev' in sys.argv

# Configurações de Tela
TILE_SIZE = 60
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 680
FPS = 60

# Cores Básicas (RGB)
COLOR_BACKGROUND = (15, 25, 20)
COLOR_TEXT = (255, 255, 255)

# Configurações do Jogo
TILE_SIZE = 60

# Configurações do Jogador
# --- NOVAS CONFIGURAÇÕES DO PLAYER ---
# Ajuste com base no tamanho REAL das imagens que você abriu

# Exemplo: Se Idle.png tem 192 de largura total e 6 desenhos lado a lado:
# 192 / 6 = 32 pixels de largura por quadro.
IDLE_FRAME_WIDTH = 32  # <-- TROQUE PELO VALOR REAL
IDLE_FRAME_HEIGHT = 32 # <-- TROQUE PELO VALOR REAL
IDLE_FRAMES = 6         # <-- QUANTIDADE DE DESENHOS NO IDLE.PNG

WALK_FRAME_WIDTH = 32
WALK_FRAME_HEIGHT = 32
WALK_FRAMES = 8 # Walk costuma ter mais quadros

RUN_FRAME_WIDTH = 32
RUN_FRAME_HEIGHT = 32
RUN_FRAMES = 8

JUMP_FRAME_WIDTH = 32
JUMP_FRAME_HEIGHT = 32
JUMP_FRAMES = 7 # Jump às vezes é só um quadro de subida e um de descida

# Fator de escala visual (quanto maior, maior o boneco na tela)
# Um valor como 3.0 ou 3.5 deve ficar bom com a sua escala de jogo
PLAYER_VISUAL_SCALE = 3.5

GOOD_ENDING_THRESHOLD = 5  # memórias mínimas para o final bom

PROLOG_TEXT = [
    "Eu costumava ser o medo e o respeito desta floresta.",
    "Mas não me lembro mais do meu próprio nome.",
    "Preciso encontrar os rastros do que fui —",
    "antes que desapareça para sempre.",
]

CUTSCENE_TEXTS = {
    0: [   # após fase 1 → antes da fase 2
        "Cada memória que encontro é como acender uma fogueira no escuro.",
        "Lembro agora: meus pés sempre apontaram para trás,",
        "confundindo quem me perseguia.",
        "A floresta ainda guarda histórias. Eu preciso encontrá-las.",
    ],
    1: [   # após fase 2 → antes da fase 3
        "As memórias voltam em fragmentos.",
        "Guerreiros que me temiam. Crianças que ouviam meu nome",
        "e corriam para dentro de casa.",
        "A floresta está me chamando de volta. Esta é minha última chance.",
    ],
}

VICTORY_GOOD_TEXT = [
    "Fui lembrado.",
    "A floresta voltou a viver e meu nome foi gravado nas lendas.",
    "O Curupira não morreu — ele se tornou eterno.",
    "Obrigado por não me esquecer.",
]

VICTORY_BAD_TEXT = [
    "A floresta sobreviveu.",
    "Mas faltaram histórias. Ainda existo — mas na sombra,",
    "esquecido pela maioria.",
    "Talvez, um dia, alguém me lembre inteiro.",
]

# Progressão de habilidades
STAGE_THRESHOLDS = {
    'rastro_confuso':    0,
    'passos_invisiveis': 3,
    'sussurro_mata':     5,
    'guardiao_desperto': 7,
}

# Loja de poderes (7 poderes conforme GDD v2)
SHOP_POWERS = [
    {
        'id':          'rastro_confuso',
        'name':        'Rastro Confuso',
        'description': 'Sempre ativo — pés apontam para trás',
        'cost':        0,
        'once':        True,
    },
    {
        'id':          'sussurro_mata',
        'name':        'Sussurro da Mata',
        'description': 'Desbloqueia double-tap para correr',
        'cost':        3,
        'once':        True,
    },
    {
        'id':          'flecha_fogo',
        'name':        'Flecha de Fogo',
        'description': 'Desbloqueia tecla Z (projétil)',
        'cost':        5,
        'once':        True,
    },
    {
        'id':          'voz_floresta',
        'name':        'Voz da Floresta',
        'description': 'Tecla X — congela inimigos por 3s',
        'cost':        8,
        'once':        True,
    },
    {
        'id':          'chama_ancestral',
        'name':        'Chama Ancestral',
        'description': 'Tecla Z faz 3× dano (1 uso por compra)',
        'cost':        10,
        'once':        False,
    },
    {
        'id':          'guardiao_vida',
        'name':        'Guardião Desperto',
        'description': '+2 HP permanente',
        'cost':        12,
        'once':        True,
    },
    {
        'id':          'sombra_mata',
        'name':        'Sombra da Mata',
        'description': 'Tecla X — intangível por 3s (SHIFT alterna)',
        'cost':        15,
        'once':        True,
    },
]