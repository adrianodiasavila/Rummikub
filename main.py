import pygame
import graphics
import random
import operator
import os

FPS = 60
WIDTH, HEIGHT = 1600, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
WIN.fill('black')

pygame.init()
clock = pygame.time.Clock()

numero_jogadores = 2
jogador_da_vez = 0
jogadas_feitas = []


class Button():

    def __init__(self, image):
        self.pressed = False
        self.ativado = False
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

    def draw(self, x, y):
        self.rect.topleft = (x, y)
        WIN.blit(self.image, (self.rect.x, self.rect.y))

    def clicou(self):

        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
            else:
                if self.pressed:
                    self.pressed = False
                    return True


botao_passa_compra = Button(r'graphics\PASS_BUY.png')
botao_jogada_pronta = Button(r'graphics\OK.png')


class Pedra(Button):

    def __init__(self, valor, cor, imagem):
        super().__init__(imagem)
        self.valor = valor
        self.cor = cor
        self.rect = self.image.get_rect()

    def marca_selecao(self):
        green_surface = pygame.Surface((self.rect.width, self.rect.height))
        green_surface.set_alpha(40)  # Define a transparência
        green_surface.fill((0, 255, 0))  # Define a cor verde
        WIN.blit(self.image, self.rect)
        WIN.blit(green_surface, self.rect)


valores = list(range(1, 14))
cores = ['B', 'R', 'Y', 'K']

imagens_subdir = r'graphics\pedras'

pedras_disponiveis = []

for valor_pedra in valores:
    for cor_pedra in cores:
        imagem_pedra = os.path.join(imagens_subdir, f'{str(cor_pedra)}{str(valor_pedra)}.png')

        pedra = Pedra(valor_pedra, cor_pedra, imagem_pedra)
        pedra2 = Pedra(valor_pedra, cor_pedra, imagem_pedra)
        pedras_disponiveis.append(pedra)
        pedras_disponiveis.append(pedra2)


class Jogador:

    def __init__(self, numero, mao):
        self.numero = numero
        self.mao = mao
        self.vez = False
        self.fez_jogada = False
        self.comprou = False
        self.passou_a_vez = False
        self.jogada_atual = []
        self.trintou = False


jogadores = []
for idx in range(numero_jogadores):

    mao_criada = random.sample(pedras_disponiveis, 14)

    for pedra in mao_criada:
        pedras_disponiveis.remove(pedra)

    jogador = Jogador(idx, mao_criada)
    jogadores.append(jogador)


def posiciona_pedras_p1(player):
    i = 0
    x, y = 415, 730
    for peca in player.mao:
        peca.draw(x, y)
        x += 55
        i += 1
        if i % 14 == 0:
            x = 415
            y -= 105


def posiciona_pedras_p2(player):
    i = 0
    x, y = 415, 50
    for peca in player.mao:
        peca.draw(x, y)
        x += 55
        i += 1
        if i % 14 == 0:
            x = 415
            y += 105


def jogada_pc(player):

    def pc_jogada_seq(player_seq):

        # ordena as pedras da mão por cor depois por valor
        mao_sorted = sorted(player_seq.mao, key=lambda obj: (obj.cor, obj.valor))

        # agrupa itens de mesma cor em sublistas
        lst = []
        for i, stone in enumerate(mao_sorted):
            if i == 0:
                lst.append([stone])
                continue
            if stone.cor == mao_sorted[i - 1].cor:
                lst[-1].append(stone)
            else:
                lst.append([stone])

        # move as peças de mesmo valor para o fim da sua sublista
        for sublst in lst:
            for i in range(len(sublst)-1):
                if sublst[i].valor == sublst[i+1].valor:
                    pedra_movida = sublst[i+1]
                    sublst.remove(pedra_movida)
                    sublst.append(pedra_movida)

        # flatten lista
        lst_flatten = [peca for sublist in lst for peca in sublist]

        # separa itens de valores consecutivos (e mesma cor) e sua própria lista
        lst_consec = []
        for i, stone in enumerate(lst_flatten):
            if i == 0:
                lst_consec.append([stone])
                continue
            if stone.cor == lst_flatten[i - 1].cor and stone.valor == lst_flatten[i - 1].valor + 1:
                lst_consec[-1].append(stone)
            else:
                lst_consec.append([stone])

        # adiciona a lista se maior que 3 itens na jogada_atual do player
        for lst in lst_consec:
            if len(lst) >= 3:
                for peca in lst:
                    player_seq.jogada_atual.append(peca)

        lanca_jogada(player_seq)

    # -----------------------------------------------------------------------------------------

    def pc_jogada_eq(player_eq):

        # ordena as pedras da mão por valores depois por cor
        mao_sorted = sorted(player_eq.mao, key=lambda obj: (obj.valor, obj.cor))

        # agrupa itens de mesmo valor em sublistas
        lst = []
        for i, stone in enumerate(mao_sorted):
            if i == 0:
                lst.append([stone])
                continue
            if stone.valor == mao_sorted[i - 1].valor:
                lst[-1].append(stone)
            else:
                lst.append([stone])

        # move as peças de cores repetidas para o fim da sua sublista
        for sublst in lst:
            for i in range(len(sublst) - 1):
                if sublst[i].cor == sublst[i + 1].cor:
                    pedra_movida = sublst[i + 1]
                    sublst.remove(pedra_movida)
                    sublst.append(pedra_movida)

        # flatten lista
        lst_flatten = [peca for sublist in lst for peca in sublist]

        # separa itens de valores iguais (e cores diferentes) e sua própria lista
        lst_eq = []

        for peca in lst_flatten:
            valor = peca.valor
            cor = peca.cor

            found = False
            for s in lst_eq:
                if s[0].valor == valor and cor not in [x.cor for x in s]:
                    s.append(peca)
                    found = True
                    break

            if not found:
                lst_eq.append([peca])

        # adiciona a lista se maior que 3 itens na jogada_atual do player
        for lst in lst_eq:
            if len(lst) >= 3:
                for peca in lst:
                    player_eq.jogada_atual.append(peca)

                lanca_jogada(player_eq)

    # executa as funções para criar possíveis jogadas
    pc_jogada_seq(player)
    pc_jogada_eq(player)
    player.fez_jogada = False
    player.jogada_atual = []

    # compra peça e/ou passa a vez, dependendo de jogadas feitas
    global jogador_da_vez, numero_jogadores

    if not player.fez_jogada:
        nova_pedra = random.choice(pedras_disponiveis)
        player.mao.append(nova_pedra)
        pedras_disponiveis.remove(nova_pedra)

    jogador_da_vez += 1
    if jogador_da_vez == numero_jogadores:
        jogador_da_vez = 0


def passar_ou_comprar(player):

    global jogador_da_vez, numero_jogadores

    if botao_passa_compra.clicou():
        if not player.fez_jogada:
            nova_pedra = random.choice(pedras_disponiveis)
            player.mao.append(nova_pedra)
            pedras_disponiveis.remove(nova_pedra)
        else:
            player.fez_jogada = False

        jogador_da_vez += 1
        if jogador_da_vez == numero_jogadores:
            jogador_da_vez = 0


def numeros_consecutivos(player):

    for i in range(len(player.jogada_atual) - 1):

        if player.jogada_atual[i + 1].valor - player.jogada_atual[i].valor != 1:
            player.fez_jogada = False
            player.jogada_atual = []
            return False

    return True


def numeros_iguais(player):

    for i in range(len(player.jogada_atual) - 1):

        if player.jogada_atual[i].valor != player.jogada_atual[i + 1].valor:
            player.jogada_atual = []
            player.fez_jogada = False
            return False

    return True


def ja_fez_30(player):

    trintou = 0
    for i in range(len(player.jogada_atual)):
        trintou += player.jogada_atual[i].valor

    if trintou >= 30:
        player.trintou = True

    if player.trintou:
        return True


def resetar_jogada(player):

    player.fez_jogada = False
    player.jogada_atual = []


def criar_jogada_padrao(player):

    for peca in player.mao:
        if peca.clicou():
            peca.ativado = not peca.ativado

            if peca.ativado:
                player.jogada_atual.append(peca)
                player.jogada_atual = sorted(player.jogada_atual, key=operator.attrgetter('valor'))
            else:
                if peca in player.jogada_atual:
                    player.jogada_atual.remove(peca)
                    peca.ativado = False

        for selecao in player.jogada_atual:
            selecao.marca_selecao()

        if botao_jogada_pronta.clicou() and len(player.jogada_atual) >= 3:
            return True


def jogada_valida(player):

    if not criar_jogada_padrao(player):
        return False

    cores_na_jogada = set([player.jogada_atual[i].cor for i in range(len(player.jogada_atual))])

    if len(cores_na_jogada) == len(player.jogada_atual):

        if not numeros_iguais(player):
            resetar_jogada(player)
        if not ja_fez_30(player):
            resetar_jogada(player)

        lanca_jogada(player)
        return True

    elif len(cores_na_jogada) == 1:

        if not numeros_consecutivos(player):
            resetar_jogada(player)
        if not ja_fez_30(player):
            resetar_jogada(player)

        lanca_jogada(player)
        return True

    else:
        player.fez_jogada = False
        player.jogada_atual = []
        return False


# coloca jogada válida como lista em jogadas feitas.
def lanca_jogada(player):

    m = [peca for peca in player.jogada_atual]
    jogadas_feitas.append(m)

    for peca in player.jogada_atual:
        if peca in player.mao:
            player.mao.remove(peca)

    player.jogada_atual = []
    player.fez_jogada = True


# desenha as jogadas realizadas na tela
def desenha_jogadas_feitas():
    x = 5
    x_tab = 25

    for jogada in jogadas_feitas:
        for peca in jogada:
            peca.draw(x, 300)
            x += 50
        x += x_tab


def main():
    jogadores[0].vez = True
    run = True
    while run:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

            pygame.display.update()
            clock.tick(FPS)

            WIN.blit(graphics.bg1, (0, 0))

            botao_jogada_pronta.draw(0, 5)
            botao_passa_compra.draw(55, 5)

            posiciona_pedras_p1(jogadores[0])
            posiciona_pedras_p2(jogadores[1])

            if jogador_da_vez == 0:
                # jogada_pc(jogadores[0])
                passar_ou_comprar(jogadores[0])
                jogada_valida(jogadores[0])

            elif jogador_da_vez == 1:
                passar_ou_comprar(jogadores[1])
                jogada_valida(jogadores[1])

            desenha_jogadas_feitas()


if __name__ == '__main__':
    main()
