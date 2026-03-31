# Legenda:
# X = grama (plataforma)   D = terra (preenchimento)
# P = jogador              G = meta (saída)
# E = inimigo              M = memória (coletável)
# W = água (perigo)        1-3 = árvores  4-5 = arbustos
# C = escada (escalável)   K = chave      L = porta trancada

LEVEL_MAP = [
#   0         1         2         3         4
#   0123456789012345678901234567890123456789012
    '                                           ',  # 00 - céu
    '                                           ',  # 01 - céu
    '    3                          1           ',  # 02 - decoração alta
    '   XXX      MMM     5         XXX          ',  # 03 - plataforma alta
    '           CXXX    XXXM                    ',  # 04 - plataforma média-alta
    ' P 5 MMMM   XXXXX         M         2       ',  # 05 - plataforma média
    ' XXX XXXXMMM                     CXXXX     ',  # 06 - suporte (C=topo da escada)
    '               X    E   M E      C     KL ',  # 07 - chão do jogador (C=escada, X=prateleira, K=chave, L=porta)
    'XXXXX  XXXXXX  XXXXXXXX  XXXXXXXXXXXXXXWWW ',  # 08 - chão principal
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 09 - terra
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 10 - terra
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 11 - terra
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 12 - terra
]

# ── FASE 2: Selva Apertada ────────────────────────────────────────────────────
# 55 colunas × 13 linhas
# Apresentação → Teste → Clímax  |  Chave + Porta no final
LEVEL_MAP_2 = [
#   0         1         2         3         4         5
#   012345678901234567890123456789012345678901234567890123456
    '                                                       ',  # 00
    '                                                       ',  # 01
    '  2        M             1          2                  ',  # 02
    '  XXX    XXXM           XXXM      XXXXX    M           ',  # 03
    '  C          XXXM                 C    M   XXX         ',  # 04
    ' P 5  M      C    E    5    M     C         C   M      ',  # 05
    ' XXX XXXX   XXXXX XXXX XXXXX  XXXXXX XXXX  XXXXXX     ',  # 06
    '                                              E  E KL  ',  # 07
    'XXXXXXX  XXXX   WWWW  XXXX  XXXXX   XXXX  XXXXXXXXWWWW',  # 08
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 09
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 10
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 11
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 12
]

# ── FASE 3: Coração da Floresta ──────────────────────────────────────────────
# 60 colunas × 13 linhas
# Apresentação → Teste → Clímax  |  Portal final (G) no extremo direito
LEVEL_MAP_3 = [
#   0         1         2         3         4         5
#   012345678901234567890123456789012345678901234567890123456789
    '                                                            ',  # 00
    '                                                            ',  # 01
    '  3        M                  1     M          3            ',  # 02
    '  XXX    XXXM      M        CXXXX XXXXX     CXXXXX  M       ',  # 03
    '  C            XXXM XXX       C            M  C       XXXX    ',  # 04
    ' P 5  M       M  C    M   5    M   XXXXX  5 M       M  ',  # 05
    ' XXX XXXX XXXXXXXXXXXX XXXXX XXXXX XXXXX XXXXX XXXXXXXX    ',  # 06
    '              E   E     E  M   E  E         E   E      E  G',  # 07
    'XXXXXXX  XXXX    WWWW   XXX  XXXX   XXXXX  XXXX  XXXXXXXXXX',  # 08
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 09
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 10
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 11
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 12
]

ALL_LEVELS = [LEVEL_MAP, LEVEL_MAP_2, LEVEL_MAP_3]