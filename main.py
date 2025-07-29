import pygame
from config import WIDTH, HEIGHT, SIDEBAR_WIDTH, TAMANHO_POPULACAO, TAXA_MUTACAO
from circuito import CicuitosEnum, Circuito
from carro import GeradorCarro
from algoritmo_genetico import AlgoritmoGenetico

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + SIDEBAR_WIDTH, HEIGHT))

    circuito =  CicuitosEnum.DIFICIL(None)
    gerador = GeradorCarro(posicao_inicial=circuito.largada)

    carros_iniciais = []
    # treinado_interlagos = gerador.novo_com_pesos([[[0.9643902534496249, -0.4834704433577387, 0.08014343221241838], [0.5522375044965095, 0.8271267996339497, -0.2897027285339244], [-0.9082816118754422, 0.8891505761935002, -0.17434486719422138], [0.5967710662463663, 0.7317377535054852, -0.25212847281552064], [-0.6550605614277104, -0.7195637966780781, 1.2497561789937075]], [[0.3575740883221396, -0.6143717812327611, 0.6284118199697367, 0.05442193685079434, 0.6729495900887689], [-0.37561599146447844, 0.12873245014327495, 1.149444390846909, 0.42864695516032525, -1.1115050927941224]]])
    # treinado_dino = gerador.novo_com_pesos([[[-0.45460863982925775, 0.38309804586148477, 0.9745392643628302], [0.06610716921043079, -0.6938545212328919, 0.8039103091351163], [0.6977239519492605, -0.8802853819971583, -0.09788953056196971], [-0.21171199885041544, -0.22245699435377436, -0.00862236617046079], [0.2968632261164436, 0.6447029079774614, -1.014573883865802]], [[-0.3363894682330789, -0.10654744940762151, -0.30185558692171255, -0.20618977972316102, 1.028870509389277], [0.17306708634986473, -1.2483662877507116, -0.05630986810337752, -0.6969283458908233, 0.9793052819808964]]])
    # carros_iniciais = [treinado_interlagos, treinado_dino]

    algoritmo_genetico = AlgoritmoGenetico(tamanho_populacao=TAMANHO_POPULACAO, taxa_mutacao=TAXA_MUTACAO, gerador_carro=gerador, populacao_inicial=carros_iniciais)

    config = {
        "Geração": 0,
        "Iteração": 0,
        "Delay": 20,
        "Grid": False,
        "Rastro": False,
        "Sensores": False
    }

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # Atualiza geração e desenha
        config["Geração"] += 1
        config["Iteração"] = 0
        processa_geracao(circuito, algoritmo_genetico, config, screen)

        pygame.display.flip()

    pygame.quit()

def processa_geracao(circuito: Circuito, algoritmo_genetico:AlgoritmoGenetico, config , screen):

    algum_carro_vivo = True
    encerra_rodada = False
    while algum_carro_vivo and config["Iteração"] < circuito.iteracoes_maximas and not encerra_rodada:
        screen.fill((255, 255, 0))
        circuito.draw(screen)
        algum_carro_vivo = False
        config["Iteração"] += 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            encerra_rodada = True
        if keys[pygame.K_g]:
            config["Grid"] = True
        if keys[pygame.K_h]:
            config["Grid"] = False
        if keys[pygame.K_0]:
            config["Delay"] = 0
        if keys[pygame.K_1]:
            config["Delay"] = 10
        if keys[pygame.K_2]:
            config["Delay"] = 20
        if keys[pygame.K_3]:
            config["Delay"] = 30
        if keys[pygame.K_4]:
            config["Delay"] = 40
        if keys[pygame.K_5]:
            config["Delay"] = 50
        if keys[pygame.K_r]:
            config["Rastro"] = True
        if keys[pygame.K_t]:
            config["Rastro"] = False
        if keys[pygame.K_s]:
            config["Sensores"] = True
        if keys[pygame.K_d]:
            config["Sensores"] = False

        for carro in algoritmo_genetico.populacao:


            carro.update(circuito)
            carro.draw(screen)
            carro.set_color((255, 0, 0))  
            
            if carro.vivo:
                algum_carro_vivo = True
            
            pygame.event.pump() 
            
        pygame.time.delay(config["Delay"])

        rank = sorted( algoritmo_genetico.populacao,  key=algoritmo_genetico.funcao_rank, reverse=True)
        draw_sidebar(screen, config)

        rank[0].set_color((0, 0, 255))
        rank[1].set_color((0, 255, 0))

        if config["Rastro"]:
            circuito.grid.draw_celulas_visitados(screen, rank[0].rastro)
        if config["Sensores"]:
            rank[0].draw_sensors(screen, rank[0].sensores(circuito))
        if (config["Grid"]):
            circuito.grid.draw_grid(screen)

        pygame.display.flip()

    # Todos morreram: gera próxima geração
    algoritmo_genetico.nova_geracao()

def draw_sidebar(surface, info):

    font = pygame.font.SysFont("Courier New", 14)

    sidebar_rect = pygame.Rect(
        WIDTH, 0,
        200, 600
    )
    pygame.draw.rect(surface, (30, 30, 30), sidebar_rect)

    padding = 10
    x = sidebar_rect.x + padding
    y = padding
    line_height = font.get_linesize() + 4

    surface.blit(font.render(f"(q)   Geração:   {info["Geração"]}", True, (240, 240, 240)), (x, y))
    y += line_height

    surface.blit(font.render(f"      Iteração:  {info["Iteração"]}", True, (240, 240, 240)), (x, y))
    y += line_height

    surface.blit(font.render(f"(0-5) Delay:     {info["Delay"]}", True, (240, 240, 240)), (x, y))
    y += line_height

    surface.blit(font.render(f"(g/h) Grid:      {info["Grid"]}", True, (240, 240, 240)), (x, y))
    y += line_height

    surface.blit(font.render(f"(r/t) Rastro:    {info["Rastro"]}", True, (240, 240, 240)), (x, y))
    y += line_height

    surface.blit(font.render(f"(s/d) Sensores:  {info["Sensores"]}", True, (240, 240, 240)), (x, y))

if __name__ == '__main__':
    main()
