import pygame

class ParallaxBackground:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.images = []
        
        # Fatores de velocidade para cada camada. 
        # 0.0 é estático (céu), 0.8 move quase junto com a câmera (frente)
        self.scroll_factors = [0.0, 0.2, 0.4, 0.6, 0.8] 
        self.scroll_x = 0

        # Carrega as 5 imagens (certifique-se de que estão na pasta correta)
        for i in range(1, 6):
            try:
                img = pygame.image.load(f'assets/bg/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (screen_width, screen_height))
                self.images.append(img)
            except FileNotFoundError:
                print(f"Aviso: Não foi possível carregar assets/bg/{i}.png")
                # Fallback visual caso falte alguma imagem
                fallback = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                self.images.append(fallback)

    def update(self, world_shift):
        # Acumula o movimento da câmera
        self.scroll_x += world_shift

    def draw(self, surface):
        for i, img in enumerate(self.images):
            factor = self.scroll_factors[i]
            
            # O módulo (%) cria o efeito infinito limitando o valor à largura da tela
            x_offset = (self.scroll_x * factor) % self.screen_width
            
            # Desenha a imagem duas vezes para preencher os espaços em branco do loop
            surface.blit(img, (x_offset, 0))
            surface.blit(img, (x_offset - self.screen_width, 0))