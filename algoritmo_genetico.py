import random
from carro import Carro, GeradorCarro
import itertools

class AlgoritmoGenetico:
    def __init__(self, tamanho_populacao, taxa_mutacao, gerador_carro: GeradorCarro, populacao_inicial:list[Carro] = []):
        self.tamanho_populacao = tamanho_populacao
        self.taxa_mutacao = taxa_mutacao
        self.gerador_carro = gerador_carro
        self.populacao = [gerador_carro.novo() for _ in range(tamanho_populacao)]

        for idx, carro in enumerate(populacao_inicial):
            if idx < len(self.populacao):
                self.populacao[idx] = carro

        self.funcao_rank = lambda c: c.pontos + len(c.rastro)

    def nova_geracao(self):

        # Avalia fitness
        rank = sorted(self.populacao, key=self.funcao_rank, reverse=True)
        print(f"Melhor: {rank[0]}")

        # Usei estatégia de elitismo pra ficar com os 3 melhores e gerar 2 filhos entre eles
        nova_populacao = []
        nova_populacao.extend(self.elitismo(rank, qtd_salvos=3, qtd_filhos=2))
        
        # Eliminação dos os 30% piores
        self.populacao = rank[:- len(rank)//3]

        # Aqui é o cruzamento normal, usando mutacao e estratégia de roleta. 
        while len(nova_populacao) < self.tamanho_populacao:
            pai1, pai2 = self.roleta_simples(self.populacao)
            filho = self.cruzamento(pai1, pai2)
            self.mutacao(filho)
            if not self.avaliacao_gemeos(nova_populacao, filho):
                nova_populacao.append(filho)

        self.populacao = nova_populacao


    def avaliacao_gemeos(self, populacao: list[Carro], carro: Carro):
        """
            Avalia se o carro já existe na população.
            Se existir retorna True, ele será eliminado!!!!
        """
        for c in populacao:
            if c.nn.get_weights() == carro.nn.get_weights():
                return True
        return False

    def cruzamento(self, pai1: Carro, pai2:Carro) -> Carro:
        """
            Cruzamento por Recombinação em 1 ponto
            Feito para cada camada.
        """
        camada1_pai1, camada2_pai1 = pai1.nn.get_weights()
        camada1_pai2, camada2_pai2 = pai2.nn.get_weights()

        ponto_corte1 = random.randint(0, len(camada1_pai1))
        camada1 = camada1_pai1[:ponto_corte1] + camada1_pai2[ponto_corte1:]

        ponto_corte2 = random.randint(0, len(camada2_pai1))
        camada2 = camada2_pai1[:ponto_corte2] + camada2_pai2[ponto_corte2:]

        filho = self.gerador_carro.novo()
        filho.nn.set_weights(camada1, camada2)
        return filho

    def mutacao(self, carro: Carro):
        """
            Para cada peso de cada camada tem chance de adicionar uma pequena mutação.
        """
        w1, w2 = carro.nn.get_weights()
        
        for layer in (w1, w2):
            for i in range(len(layer)):
                for j in range(len(layer[i])):
                    if random.random() < self.taxa_mutacao:
                        layer[i][j] += random.gauss(0, 0.1)
        carro.nn.set_weights(w1, w2)


    def elitismo(self, rank: list[Carro], qtd_salvos, qtd_filhos):
        """
        A ideia aqui é manter os melhores carros da geração anterior e criar novos filhos a partir deles.
        """
        
        lista_carros_salvos = []

        """
        1) Encontro os X melhores carros da geração anterior
        """
        for i in range(qtd_salvos):
            campeao = rank[i]
            carro = self.gerador_carro.novo()
            carro.nn.set_weights(*campeao.nn.get_weights())
            lista_carros_salvos.append(carro)
        
        """
        2) Gero N filhos a partir dos campeões
        """
        for i in range(qtd_filhos):
            pais = random.sample(lista_carros_salvos, 2)
            filho = self.cruzamento(pais[0], pais[1])
            self.mutacao(filho)
            if not self.avaliacao_gemeos(lista_carros_salvos, filho):
                lista_carros_salvos.append(filho)

        return lista_carros_salvos


    def roleta_simples(self, populacao:list[Carro]) -> list[Carro]:
        """
        O que eu tentei fazer aqui foi uma seleção por roleta, onde os carros com maior distância tem mais chance de serem escolhidos.        
        """

        """
        1) Soma todas as disntancias (fitness) dos carros:
            Carro1: 100, Carro2: 200, Carro3: 300
            Total: 600
        """
        total_fitness = 0
        for carro in populacao:
            total_fitness += carro.distancia

        """
        2) Divide cada uma pelo total:
            Carro1: 100/600 = 0.1667
            Carro2: 200/600 = 0.3333
            Carro3: 300/600 = 0.5
        """
        probs = [carro.distancia / total_fitness for carro in populacao]

        """
        3) Cria uma lista cumulativa de probabilidades:
            Carro1: 0.1667
            Carro2: 0.1667 + 0.3333 = 0.5
            Carro3: 0.5 + 0.5 = 1
            Fica assim: [0.1667, 0.5, 1]

            Desse jeito os que tem maior probabilidade de serem escolhidos tem um espaço maior na lista.
        """ 
        probabilidade_acumulada = list(itertools.accumulate(probs))

        """
        4) Escolhe 2 pais de forma aleatória, mas respeitando a probabilidade cumulativa.
            Ou seja o "melhor" deve aparecer mais vezes.

            A lógica é:
            - Gera um número aleatório entre 0 e 1.
            - Encontra o primeiro índice onde cumulative[i] >= número aleatório.
        Exemplo: Se o número aleatório for 0.4, o primeiro índice onde probabilidade_acumulada[i] >= 0.4 é i=1, então escolhemos o Carro2.
        """
        pais_selecionados = []
        for _ in range(2):
            r = random.random()
            for i, probs in enumerate(probabilidade_acumulada):
                if r <= probs:
                    pais_selecionados.append(populacao[i])
                    break

        return pais_selecionados
