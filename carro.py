import math
import pygame
from neural_network import NeuralNetwork
from circuito import Circuito
from config import DISTANCIA_MAXIMA_SENSOR, DISTANCIA_PASSO

class GeradorCarro:
    def __init__(self, posicao_inicial=(100, 50)):
        self.posicao_inicia = posicao_inicial
    
    def novo(self,cor=(255, 0, 0) ):
        return Carro(self.posicao_inicia, cor=cor)
    
    def novo_com_pesos(self, pesos):
        c = self.novo()
        c.nn.set_weights(pesos[0],pesos[1])
        return c

class Carro:
    def __init__(self, posicao_inicial, cor):
        self.x = posicao_inicial[0]
        self.y = posicao_inicial[1]
        self.ultima_posicao = ()
        self.rastro = []
        self.cor = cor
        self.angulo = 0
        self.velocidade = 0
        self.nn = NeuralNetwork()
        self.vivo = True
        self.distancia = 0
        self.pontos = 0

    def sensores(self, circuito: Circuito):
        # Retorna lista de 3 distâncias usando ray-casting
        readings = []
        angulos = [0, math.radians(45), -math.radians(45)]
        for a in angulos:
            dist = 0
            # Avance passo a passo até encontrar parede
            while True:
                px = self.x + math.cos(self.angulo + a) * dist
                py = self.y + math.sin(self.angulo + a) * dist
                if not circuito.esta_no_circuito(px, py) or dist >= DISTANCIA_MAXIMA_SENSOR:
                    break
                dist += 1
            readings.append(dist)
        return readings

    def update(self, circuito: Circuito):
        if not self.vivo:
            return

        # Sensores
        inputs = self.sensores(circuito)
        outputs = self.nn.forward(inputs)

        """
            Deixei com o passo de 10, apenas para acelerar o movimento:
            - Com passos menores ele demora muito. 
            - Com passos maiores ele sai muito do mapa.
        """
        self.velocidade = outputs[0] * DISTANCIA_PASSO

        """
            O valor do output vai de 0 a 1, mas quero que ele possa girar pros dois lados 
            (esquerda=negativo e direita=positivo) então eu multiplico a saída por 2 e diminuo 1:
            Ex: Se 0   -> -1 (gira tudo pra esquerda)
                Se 0.5 ->  0 (não gira)
                Se 1   ->  1 (gira tudo pra diretia)
        """
        self.angulo += outputs[1] * 2 - 1

        self.x += math.cos(self.angulo) * self.velocidade 
        self.y += math.sin(self.angulo) * self.velocidade



        posicao = circuito.grid.get_quadradinho_grid(self.x, self.y)

        if self.ultima_posicao != posicao:
            self.ultima_posicao = posicao
            if len(self.rastro) == 0:
                self.rastro.append(posicao)
            else:
                if posicao == self.rastro[0]:
                    if len(self.rastro) > 30:
                        self.pontos = len(self.rastro) + self.pontos
                    else:
                        self.pontos = 0
                    self.rastro.clear()
                    self.rastro.append(posicao)
                elif posicao != self.rastro[-1]:
                    if posicao in self.rastro:
                        self.rastro.remove(posicao)
                    else:
                        self.rastro.append(posicao)

        # Verifica colisão
        if not circuito.esta_no_circuito(self.x, self.y):
            self.vivo = False
            return
        else:
            self.distancia += len(self.rastro) + self.pontos

        

    def draw_sensors(self, screen, sensors):
        angulos = [0, math.radians(45), -math.radians(45)]
        
        for i, dist in enumerate(sensors):
            angulo = self.angulo + angulos[i]
            end_x = self.x + math.cos(angulo) * dist
            end_y = self.y + math.sin(angulo) * dist
            pygame.draw.line(screen, (0, 255, 0), (self.x, self.y), (end_x, end_y), 1)

    def draw(self, screen):
        # Desenhar como um círculo para simplificar
        pygame.draw.circle(surface=screen, color=self.cor, center=(int(self.x), int(self.y)), radius=5)


    def set_color(self, cor):
        self.cor = cor

    def __str__(self):
        return f"Carro(x={self.x}, y={self.y}, angulo={self.angulo}, velocidade={self.velocidade}, vivo={self.vivo}, rastro={self.rastro}, distancia={self.distancia}, pesos={self.nn.get_weights()})"
    
    def __repr__(self):
        return self.__str__()
