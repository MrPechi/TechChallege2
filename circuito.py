import pygame
from enum import Enum
from config import HEIGHT, WIDTH, COR_GRID, COR_CELULA_VISITADA


class Grid:
    def __init__(self, cell_size, height=HEIGHT, width=WIDTH):
        self.width     = width
        self.height    = height
        self.cell_size = cell_size
        self.cols      = width  // cell_size
        self.rows      = height // cell_size

    def get_quadradinho_grid(self, x, y):
        i = int(x // self.cell_size)
        j = int(y // self.cell_size)
        i = max(0, min(self.cols-1, i))
        j = max(0, min(self.rows-1, j))
        return (i, j)

    def draw_grid(self, surface):
        """
            Desenha o grid.
        """
        for i in range(self.cols + 1):
            x = i * self.cell_size
            pygame.draw.line(surface, COR_GRID, (x, 0), (x, self.height))
        for j in range(self.rows + 1):
            y = j * self.cell_size
            pygame.draw.line(surface, COR_GRID, (0, y), (self.width, y))

    def draw_celulas_visitados(self, surface, visited):
        """
            Preenche cada célula já visitada com um retângulo semi-transparente.
        """
        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        for (i, j) in visited:
            rect = pygame.Rect(
                i * self.cell_size,
                j * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(overlay, COR_CELULA_VISITADA, rect)

        surface.blit(overlay, (0, 0))

class Circuito:
    def __init__(self, filepath, largada: tuple, grid=Grid(40), iteracoes_maximas=1000):
        self.image = pygame.image.load(filepath).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.grid = grid
        self.largada= largada
        self.iteracoes_maximas = iteracoes_maximas

    def draw(self, screen):
        screen.blit(self.image, (0, 0))

    def esta_no_circuito(self, x, y):
        # Retorna True se pixel (x,y) for parte da pista
        try:
            return self.mask.get_at((int(x), int(y))) == 1
        except IndexError:
            return False


class CicuitosEnum(Enum):
    DINO =  lambda _: Circuito("circuitos/dino.png", largada=(420, 475), iteracoes_maximas=2000 )
    DIFICIL = lambda _: Circuito("circuitos/dificil.png", largada=(100, 50), iteracoes_maximas=2000 )
    INTERLAGOS = lambda _: Circuito("circuitos/interlagos.png", largada=(500, 530), iteracoes_maximas=1500)
