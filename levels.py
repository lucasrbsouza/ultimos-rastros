# ── Legenda do mapa ───────────────────────────────────────────────────────────
# Terreno
#   X = grama (plataforma)        D = terra (preenchimento)
#   W = água (perigo/morte)
#
# Objetos interativos
#   C = escada (escalável)        K = chave
#   L = porta trancada            G = meta / saída da fase
#   M = memória (coletável)       R = coração (+1 HP)
#
# Spawn
#   P = jogador (spawn)
#
# Decoração
#   1-3 = árvores                 4-6 = arbustos
#
# Inimigos comuns
#   E = fly (patrulha)            F = slime normal
#   T = slime fogo                V = slime espinho
#
# Inimigos / mini-boss de fase
#   N = Plent                     S = Skeleton
#   A = Orc Warrior               B = Orc Berserk
#   H = Orc Shaman (boss final)
# ─────────────────────────────────────────────────────────────────────────────

LEVEL_MAP = [
#   0         1         2         3         4
#   0123456789012345678901234567890123456789012
    '                                                                             ',  # 00 - céu
    '                                                                              ',  # 01 - céu
    '                                                                                       3K',  # 02 - decoração alta
    '                                                                                     CXXXX    R',  # 03 - plataforma alta
    '                                                               M     E M        M    C5    XXXX E2',  # 04 - plataforma média-alta
    '                        DM                               4    XXX   XXXXWX 3 V  XXX           DDXXX 1  F',  # 05 - plataforma média
    '                 XXX        E                           XXX         DDDDDDDDDDD                     DDDDD   1  E 24  F  35 V   E 16   L',  # 06 - suporte (C=topo da escada)
    'P  M    FM            1        44     2 5 E  M   E M    DDD                                               XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',  # 07 - chão do jogador (E=fly, N=Plent boss, K=chave, L=porta)
    'XXXXXXXXXXXXXWWXXXXXXXXXXXXXXXXXXXX 4XXXXXXXXXXXXXXXXXX                                                   DDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 08 - chão principal (WW=água no Teste)
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDQDDDDDDDDDD                                                    DDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 09 - terra
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD                                                      DDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 10 - terra
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD                                                       DDDDDDDDDDDDDDDDDDDDDDDD',  # 11 - terra
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 12 - terra
]

# ── FASE 2: Selva Apertada ────────────────────────────────────────────────────
# 55 colunas × 13 linhas
# Apresentação → Teste → Clímax  |  Chave + Porta no final
LEVEL_MAP_2 = [
#   0         1         2         3         4         5
#   012345678901234567890123456789012345678901234567890123456
    '                                                                                                                                                         ',  # 00
    '                                                                                                                                                          ',  # 01
    '                                                                                                                                                           ',  # 02
    '                                                                      4E       M 15                                                                            ',  # 03
    '                                                                    XXXXXX   CDXXXXX       M                          25 E      M        N                             126R',  # 04
    '                           26 M R                          2  T M                        XXXXX                     66VXXXXX   XXXXXXXXXXXXXXWXXX      VE              XXXXXX  T   M          N   L',  # 05
    '                          XXXXXX                          CXXXXXX                     D                     M    XXXXX          DDDDDDDDDDDDDDDDD   XXXXXX     M             XXXXXX      XXXXXXXXXX',  # 06
    'P16 45E 14  M T 35     ME        2V456 15  34 NM 52 F     C                                          F  T XXXXX                 DDDDDDD            DDDDDDKRXXXXXXXXXDDD      DDDDDD  X  RDDDDDDDDDD                               ',  # 07 - E=fly N=Plent S=Skeleton A=Warrior B=Berserk H=Shaman(boss)
    'XXXXXXXXXXXXXXXXXXX  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX                                         XXXXXXXXX                     DDDDDDD               DDDDDD  DDDDDDDD        DDDDDD  D  D    '
    'XXXXXXXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXDDDDDDDDDDDDDDDDD                                       X                               DDDDDDD                             ',  # 08
    'DDDDDDDDDDDDDDDDDD   DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD                                      D                               DDDDDDD                              ',  # 09
    'DDDDDDDDDDDDDDDDDD   DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD                                      D                               DDDDDDD                              ',  # 10
    'DDDDDDDDDDDDDDDDDD   DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD                                      D                                                              ',  # 11
    'DDDDDDDDDDDDDDDDDD   DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD                                      D                                                              ',  # 12
]

# ── FASE 3: Coração da Floresta ──────────────────────────────────────────────
# 60 colunas × 13 linhas
# Apresentação → Teste → Clímax  |  Portal final (G) no extremo direito
LEVEL_MAP_3 = [
#   0         1         2         3         4         5
#   012345678901234567890123456789012345678901234567890123456789
    '                                                            ',  # 00
    '                                                            ',  # 01
    '         ',  # 02
    '      ',  # 03
    '      ',  # 04
    ' P   ',  # 05
    ' X    ',  # 06
    '                                       E    M         KL      ',  # 07 - E=fly N=Plent S=Skeleton A=Warrior B=Berserk H=Shaman(boss)  
    'XXXXXXX  XXXX    WWWW   XXX  XXXX   XXXXX  XXXX  XXXXXXXXXX',  # 08
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 09
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 10
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 11
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 12
]

ALL_LEVELS = [LEVEL_MAP, LEVEL_MAP_2, LEVEL_MAP_3]