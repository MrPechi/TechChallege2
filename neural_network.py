import random
import math
import copy
from config import INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE

class NeuralNetwork:

    def __init__(self):
        self.w1 = [[random.uniform(-1, 1) for _ in range(INPUT_SIZE)] for _ in range(HIDDEN_SIZE)]
        self.w2 = [[random.uniform(-1, 1) for _ in range(HIDDEN_SIZE)] for _ in range(OUTPUT_SIZE)]

    def activate(self, x):
        """
        Função sigmoid
            Varia de 0 a 1
            Quanto maior o X, mais próximo de 1 ela fica;
            Quanto menor o X (inclusive negativo), mais próximo de 0 ela fica. 
            Para x=0, y=0.5

            Para valores maiores que 500, atribuo 1 (ou a 0, quando pequeno), sem fazer o cálculo
        """
        if x < -500:
            return 0
        elif x > 500:
            return 1
        else:
            return 1 / (1 + math.exp(-x))

    def forward(self, inputs):
        """
        inputs: lista de 3 valores numéricos (floats ou ints),
                cada um correspondendo à distância lida por um sensor do carro.
                Exemplo: [dist_frente, dist_diagonal_esq, dist_diagonal_dir]
        Retorna: tuple (aceleração, direção) no intervalo [0, 1].
        """
        hidden = [self.activate(sum(w * i for w, i in zip(weights, inputs))) for weights in self.w1]
        outputs = [self.activate(sum(w * h for w, h in zip(weights, hidden))) for weights in self.w2]
        return outputs

    def get_weights(self):
        """
        Retorna:
            - w1 (hidden_size x input_size): pesos da camada de entrada para oculta
            - w2 (output_size x hidden_size): pesos da camada oculta para saída
        """
        return copy.deepcopy(self.w1), copy.deepcopy(self.w2)

    def set_weights(self, w1: list, w2: list):
        self.w1 = w1
        self.w2 = w2

    def __str__(self):
        return f"NeuralNetwork(input_size={len(self.w1[0])}, hidden_size={len(self.w1)}, output_size={len(self.w2)})"
