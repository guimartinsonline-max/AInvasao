"""Quadros de efeitos de tiro desenhados por script, só com cores da paleta:
clarão do cano, balas, impacto, explosão, fumaça, chama, raio alienígena.

PROPOSTA: aguardando aprovação antes de virar spritesheet do jogo.
Cada função recebe o número do quadro e devolve uma Tela.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela, IDX, VAZIO, BAYER4  # noqa: E402

FOGO = ["vermelho_esc", "laranja_escuro", "laranja_fogo", "amarelo_fogo"]
FOGO_CLARO = ["laranja_escuro", "laranja_fogo", "amarelo_fogo", "amarelo_claro"]
FUMACA = ["sombra", "cinza_escuro", "cinza_medio", "cinza"]
FUMACA_CLARA = ["cinza_escuro", "cinza", "cinza_luz", "cinza_claro"]
ALIEN = ["alien_profundo", "alien_medio", "alien", "alien_brilho"]


def ralo(t, mascara, fracao, semente=0):
    """Apaga parte dos pixels da máscara com pontilhado ordenado (fumaça sumindo)."""
    h, w = t.px.shape
    lim = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    t.px[mascara & (lim < fracao)] = VAZIO


# ---------------------------------------------------------------- clarão do cano
def clarao(k, grande=False):
    """Estrela de fogo na boca do cano, voltada para a direita (3 quadros)."""
    e = 1.4 if grande else 1.0
    t = Tela(int(24 * e), int(18 * e))
    cy = t.h / 2
    r = [5.5, 4, 2.2][k] * e
    pontas = ((0, 3.2, 0.5), (-0.55, 2.0, 0.42), (0.55, 2.0, 0.42), (-1.4, 1.3, 0.35), (1.4, 1.3, 0.35))
    for camada, (cor, folga) in enumerate((("vermelho_medio", 1.0), ("laranja_fogo", 0.0))):
        if k < 2:
            for ang, comp, grossura in pontas:
                L = r * comp + folga
                x1, y1 = r + math.cos(ang) * L, cy + math.sin(ang) * L
                t.chapado(t.capsula(r, cy, x1, y1, r * grossura + folga, 0.4), cor)
        t.chapado(t.elipse(r, cy, r * 1.2 + folga, r * 0.9 + folga), cor)
    if k < 2:
        for ang, comp, grossura in pontas[:3]:
            L = r * comp * 0.7
            t.chapado(t.capsula(r, cy, r + math.cos(ang) * L, cy + math.sin(ang) * L, r * grossura * 0.6, 0.3), "amarelo_fogo")
    t.chapado(t.elipse(r, cy, r * 0.9, r * 0.66), "amarelo_fogo")
    t.chapado(t.elipse(r * 0.95, cy, r * 0.55, r * 0.42), "branco")
    return t


# ---------------------------------------------------------------- balas
def tracer(k, cores=("laranja_fogo", "amarelo_fogo", "branco")):
    """Bala com rastro (2 quadros piscando)."""
    o, y, w = cores
    comp = 12 if k == 0 else 9
    t = Tela(12, 3)
    x0 = 12 - comp
    t.chapado(t.retangulo(x0, 1, comp, 1), o)
    t.chapado(t.retangulo(x0 + comp // 3, 1, comp - comp // 3, 1), y)
    t.chapado(t.retangulo(8, 0, 3, 3), y)
    t.chapado(t.retangulo(9, 1, 3, 1), w)
    return t



def bala_papo(k):
    """Bala da Papo-amarelo: risco comprido e branco, rápido."""
    t = Tela(20, 3)
    t.chapado(t.retangulo(0, 1, 20, 1), "amarelo_claro" if k else "amarelo_fogo")
    t.chapado(t.retangulo(10, 1, 10, 1), "branco")
    t.chapado(t.retangulo(15, 0, 4, 3), "amarelo_claro")
    t.chapado(t.retangulo(16, 1, 4, 1), "branco")
    return t


def chumbo(k):
    t = Tela(3, 3)
    t.chapado(t.retangulo(0, 0, 3, 3), "cinza_escuro")
    t.chapado(t.retangulo(0, 0, 2, 2), "cinza_claro")
    t.ponto(0, 0, "branco")
    return t


def pedra(k):
    """Pedra da Baladeira, girando (2 quadros)."""
    t = Tela(7, 7)
    m = t.elipse(3.5, 3.5, 3.2, 2.7) if k == 0 else t.elipse(3.5, 3.5, 2.7, 3.2)
    t.cel(m, ["sombra", "cinza_escuro", "cinza", "cinza_claro"], sombra=1)
    t.contorno("sombra")
    t.ponto(2 if k == 0 else 4, 2, "branco")
    return t


def foguete(k):
    """Rojão voando: corpo de papel vermelho, ponta de metal e fogo na cauda."""
    t = Tela(22, 7)
    t.cel(t.retangulo(8, 2, 10, 3), ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"], sombra=1)
    t.chapado(t.retangulo(11, 2, 2, 3), "amarelo_fogo")
    t.cel(t.poligono([(18, 2), (21, 3.5), (18, 5)]), ["sombra", "cinza_escuro", "cinza", "cinza_claro"], sombra=0)
    t.chapado(t.poligono([(8, 1), (10, 2), (8, 2)]), "vermelho_esc")
    t.chapado(t.poligono([(8, 5), (10, 5), (8, 6)]), "vermelho_esc")
    t.contorno("sombra")
    comp = 7 if k == 0 else 5
    t.chapado(t.capsula(7, 3.5, 7 - comp, 3.5, 1.6, 0.4), "laranja_fogo")
    t.chapado(t.capsula(7, 3.5, 7 - comp * 0.6, 3.5, 0.9, 0.3), "amarelo_fogo")
    t.ponto(6, 3, "branco")
    return t


def buscape(k):
    """Buscapé: foguetinho que serpenteia soltando faísca."""
    t = Tela(12, 5)
    t.cel(t.retangulo(4, 1, 6, 3), FOGO_CLARO, sombra=1)
    t.cel(t.poligono([(10, 1), (12, 2.5), (10, 4)]), ["sombra", "cinza_escuro", "cinza", "cinza_claro"], sombra=0)
    t.contorno("sombra")
    t.pontos([(2, 2), (1, 1 + k % 2 * 2)], "amarelo_fogo")
    t.ponto(0, 2 if k else 1, "branco")
    return t


def anel(k):
    """Disparo do raio desintegrador: anel verde que pulsa."""
    t = Tela(10, 16)
    rx, ry = (3.5, 7) if k == 0 else (3, 6)
    fora = t.elipse(5, 8, rx, ry)
    dentro = t.elipse(5.6, 8, rx - 1.6, ry - 2)
    t.chapado(fora & ~dentro, "alien")
    t.chapado(t.elipse(4.2, 8, rx * 0.5, ry * 0.85) & fora & ~dentro, "alien_brilho")
    t.chapado(t.elipse(3.8, 8, 0.8, ry * 0.6) & fora & ~dentro, "branco")
    return t


# ---------------------------------------------------------------- impactos
def impacto(k):
    """Impacto da bala (4 quadros): clarão, estrela, estilhaços, fumacinha."""
    t = Tela(14, 14)
    c = 7
    if k == 0:
        t.chapado(t.elipse(c, c, 3, 3), "amarelo_fogo")
        t.chapado(t.elipse(c, c, 2, 2), "branco")
    elif k == 1:
        for ang in range(0, 360, 45):
            a = math.radians(ang + 22)
            L = 6 if ang % 90 == 0 else 4.5
            t.chapado(t.capsula(c, c, c + math.cos(a) * L, c + math.sin(a) * L, 1.1, 0.3), "laranja_fogo")
        t.chapado(t.elipse(c, c, 3.4, 3.4), "amarelo_fogo")
        t.chapado(t.elipse(c - 0.5, c - 0.5, 1.8, 1.8), "branco")
    elif k == 2:
        anelm = t.elipse(c, c, 5.5, 5.5) & ~t.elipse(c, c, 3.5, 3.5)
        t.chapado(anelm, "laranja_fogo")
        ralo(t, anelm, 0.45)
        for ang in (30, 150, 250, 320):
            a = math.radians(ang)
            t.ponto(int(c + math.cos(a) * 6), int(c + math.sin(a) * 6), "amarelo_fogo")
        t.chapado(t.elipse(c, c, 1.5, 1.5), "amarelo_claro")
    else:
        for dx, dy, r in ((-2, -1, 2.2), (2, -2, 1.8), (0, 1, 1.6)):
            t.cel(t.elipse(c + dx, c + dy - 1, r, r), FUMACA_CLARA, sombra=1, linha=False)
        ralo(t, t.px != VAZIO, 0.3)
    return t


def impacto_verde(k):
    """Impacto do raio desintegrador: anéis verdes se abrindo."""
    t = Tela(20, 20)
    r = [3, 6, 8.5, 9.5][k]
    m = t.elipse(10, 10, r, r) & ~t.elipse(10, 10, r - (2 if k < 2 else 1.2), r - (2 if k < 2 else 1.2))
    t.chapado(m, ["alien_brilho", "alien", "alien_medio", "alien_esc"][k])
    if k < 2:
        t.chapado(t.elipse(10, 10, r * 0.45, r * 0.45), "branco")
    if k >= 2:
        ralo(t, m, 0.25 * (k - 1))
    return t


# ---------------------------------------------------------------- explosão
FOGO_VOL = ["vermelho_esc", "vermelho_medio", "laranja_escuro", "laranja_fogo", "ouro_escuro", "amarelo_fogo",
            "amarelo_claro"]
BRASA_VOL = ["marrom_noite", "vermelho_esc", "vermelho_medio", "laranja_escuro", "laranja_fogo", "ouro_escuro"]
FUMACA_VOL = ["preto", "sombra", "sombra_media", "cinza_escuro", "cinza_medio", "cinza"]
FUMACA_CLARA_VOL = ["sombra_media", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"]

# Gomos da nuvem de fogo: (x, y) relativos ao raio e tamanho. Desenhados de trás para a frente.
LOBULOS = [(0, -0.75, 0.55), (-0.8, -0.2, 0.5), (0.85, -0.25, 0.5), (-0.55, 0.5, 0.55), (0.6, 0.5, 0.55),
           (-0.35, -0.35, 0.62), (0.4, -0.4, 0.6), (0, 0.15, 0.7)]


def gomos(t, cx, cy, raio, rampa, semente=0, achatado=2.5):
    """Nuvem feita de bolas, cada uma com volume e linha interna (estilo Metal Slug)."""
    rng = np.random.default_rng(semente)
    total = np.zeros(t.px.shape, dtype=bool)
    for dx, dy, f in LOBULOS:
        jx, jy = rng.uniform(-0.08, 0.08, 2)
        m = t.elipse(cx + (dx + jx) * raio, cy + (dy + jy) * raio, raio * f, raio * f * 0.92)
        t.volume(m, rampa, achatado=achatado, suave=0.8, ambiente=0.15, brilho=1.1)
        total |= m
    return total


def explosao(k, tamanho=40):
    """Explosão em 8 quadros: clarão branco, bola de fogo em gomos com volume,
    brasa escurecendo e fumaça que sobe e se desfaz."""
    t = Tela(tamanho, tamanho)
    c = tamanho / 2
    s = tamanho / 40
    if k == 0:
        t.chapado(t.elipse(c, c, 7 * s, 7 * s), "amarelo_fogo")
        t.chapado(t.elipse(c, c, 5.5 * s, 5.5 * s), "branco")
        return t
    if k == 1:
        t.chapado(t.elipse(c, c, 12 * s, 12 * s), "laranja_fogo")
        t.chapado(t.elipse(c, c, 10.5 * s, 10.5 * s), "amarelo_fogo")
        t.chapado(t.elipse(c, c, 8 * s, 8 * s), "branco")
        return t
    raio = [0, 0, 11, 13, 14, 14.5, 15, 15][k] * s
    sobe = [0, 0, 0, 1, 2, 4, 6, 8][k] * s
    rampa = {2: FOGO_VOL, 3: FOGO_VOL, 4: BRASA_VOL, 5: FUMACA_VOL, 6: FUMACA_CLARA_VOL, 7: FUMACA_CLARA_VOL}[k]
    total = gomos(t, c, c - sobe, raio, rampa, semente=k)
    if k == 2:
        t.chapado(t.elipse(c, c, raio * 0.45, raio * 0.42), "amarelo_claro")
        t.chapado(t.elipse(c - 1, c - 1, raio * 0.25, raio * 0.25), "branco")
    elif k == 3:
        t.chapado(t.elipse(c, c + 1, raio * 0.3, raio * 0.28), "amarelo_claro")
    elif k == 5:
        # Brasa ainda acesa por baixo da fumaça.
        brasa = t.elipse(c, c - sobe + raio * 0.45, raio * 0.45, raio * 0.28) & total
        t.chapado(brasa, "laranja_escuro")
        t.chapado(t.elipse(c, c - sobe + raio * 0.5, raio * 0.25, raio * 0.14) & total, "laranja_fogo")
    if k >= 6:
        ralo(t, total, 0.3 if k == 6 else 0.65)
    return t


def fumaca(k):
    """Nuvenzinha de fumaça (bacamarte, rastro do rojão), 4 quadros."""
    t = Tela(14, 14)
    r = [2.4, 3.4, 4.2, 4.8][k]
    m = t.elipse(6, 8 - k, r, r * 0.9)
    t.volume(m, FUMACA_CLARA_VOL, achatado=2, suave=0.6, ambiente=0.25)
    m2 = t.elipse(6 + r * 0.6, 9 - k, r * 0.65, r * 0.6)
    t.volume(m2, FUMACA_CLARA_VOL, achatado=2, suave=0.6, ambiente=0.25)
    if k >= 2:
        ralo(t, m | m2, 0.3 if k == 2 else 0.6)
    return t


def chama(k):
    """Bola de fogo do Candeeiro: nasce branca, cresce, escurece e vira fumaça."""
    t = Tela(22, 22)
    c = 11
    r = [3, 5, 7, 8, 8][k]
    rampa = [FOGO_VOL, FOGO_VOL, FOGO_VOL, BRASA_VOL, FUMACA_VOL][k]
    if k == 0:
        t.chapado(t.elipse(c, c, r, r * 0.85), "amarelo_fogo")
        t.chapado(t.elipse(c, c, r * 0.6, r * 0.5), "branco")
        return t
    total = gomos(t, c, c, r, rampa, semente=10 + k, achatado=2)
    if k == 1:
        t.chapado(t.elipse(c, c, r * 0.4, r * 0.35), "amarelo_claro")
    if k == 4:
        ralo(t, total, 0.45)
    return t
