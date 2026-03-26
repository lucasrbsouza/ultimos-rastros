# Legenda:
# X = grama (plataforma)   D = terra (preenchimento)
# P = jogador              G = meta (saída)
# E = inimigo              M = memória (coletável)
# W = água (perigo)        1-3 = árvores  4-5 = arbustos
# C = escada (escalável)

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
    '               X    E   M E      C     G  ',  # 07 - chão do jogador (C=escada, X=prateleira ledge grab)
    'XXXXX  XXXXXX  XXXXXXXX  XXXXXXXXXXXXXXWWW ',  # 08 - chão principal
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 09 - terra
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 10 - terra
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 11 - terra
    'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',  # 12 - terra
]