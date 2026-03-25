from levels import *
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