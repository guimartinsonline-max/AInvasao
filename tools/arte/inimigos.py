"""Inimigos, reféns, bode e efeitos grandes (explosão e mortes cômicas).

Inimigos são desenhados virados para a esquerda (vão ao encontro do jogador);
o jogo espelha quando precisam virar.
"""
import numpy as np

from motor import IDX, VAZIO, Tela
from personagens import (ACO, CAQUI, COURO, MADEIRA, PE, PELE, ROSTO, H, W, alien, arma)

OLIVA = ["caatinga_esc", "caatinga_esc", "caatinga", "mandacaru"]
OLIVA_ESC = ["sombra", "caatinga_esc", "caatinga_esc", "caatinga"]
BRANCO = ["cinza", "cinza_claro", "branco", "branco"]
PALHA = ["terra", "barro", "areia", "areia_clara"]
DISCO = ["sombra", "cinza_escuro", "cinza", "cinza_claro", "branco"]
VIDRO = ["ceu_escuro", "ceu", "ceu_claro", "horizonte"]
CHIFRE = ["couro_escuro", "couro", "couro_claro", "areia"]

PERNAS_VOLANTE = {
    "parado": [((-2, 37), (-3, 43), (-4, PE)), ((3, 37), (4, 43), (5, PE))],
    "anda1": [((-1, 37), (-5, 42), (-8, PE)), ((2, 37), (6, 42), (7, PE))],
    "anda2": [((0, 37), (1, 43), (0, PE)), ((1, 37), (3, 43), (2, PE - 2))],
}


# ---------------------------------------------------------------- Volante
def volante(pose=None):
    """Soldado da Volante: farda verde-oliva, quepe e fuzil. Desenhado para a
    direita e espelhado no fim."""
    p = {"pernas": "parado", "boca": "bravo", "tiro": False}
    p.update(pose or {})
    t = Tela(W, H)
    ox = 24
    for k, (quadril, joelho, pe) in enumerate(PERNAS_VOLANTE[p["pernas"]]):
        d = -1 if k == 0 else 0
        (hx, hy), (jx, jy), (px, py) = [(ox + a, b) for a, b in (quadril, joelho, pe)]
        t.cel(t.capsula(hx, hy, jx, jy, 3.0, 2.6), OLIVA_ESC, deslocar=d)
        t.cel(t.capsula(jx, jy, px, py - 2.5, 2.7, 2.4), COURO, deslocar=d)
        t.cel(t.elipse(px + 1.5, py - 1.2, 4.0, 1.9), ["sombra", "preto", "couro_escuro", "couro"], deslocar=d, sombra=1)
    # Braço de trás.
    t.cel(t.capsula(ox - 2, 27, ox + 7, 31, 2.6, 2.3), OLIVA, deslocar=-1)
    # Túnica com botões dourados, cinto e talabarte.
    t.cel(t.elipse(ox, 31, 8.0, 7.6), OLIVA, sombra=3)
    t.cel(t.capsula(ox - 6, 25, ox + 5, 36, 1.2), COURO, sombra=1, luz=0)
    for y in (26, 29, 32):
        t.ponto(ox + 2, y, "amarelo_fogo")
    t.cel(t.retangulo(ox - 8, 36, 16, 3), COURO, sombra=1)
    t.chapado(t.retangulo(ox, 36.5, 3, 2), "cinza_claro")
    # Gola.
    t.cel(t.elipse(ox + 1, 24, 5, 2), OLIVA_ESC, sombra=1)
    # Cabeça: queixo grande, bigodão e cara de bravo.
    hx, hy = ox + 2, 16
    t.cel(t.elipse(hx, hy, 6.4, 6.6), ROSTO, sombra=1, linha=False)
    t.cel(t.elipse(hx + 3, hy + 4.5, 4.2, 3), ROSTO, sombra=1)
    t.cel(t.elipse(hx + 6.2, hy + 0.8, 2.2, 2.0), ROSTO, sombra=1)
    t.chapado(t.retangulo(hx + 1, hy + 2.5, 8, 2), "preto")
    t.pontos([(int(hx + 1), int(hy + 4)), (int(hx + 8), int(hy + 4))], "preto")
    if p["boca"] == "grito":
        t.chapado(t.retangulo(hx + 3, hy + 5, 4, 3), "sombra")
        t.chapado(t.retangulo(hx + 3, hy + 7, 3, 1), "vermelho")
    t.chapado(t.retangulo(hx + 3, hy - 1.5, 2, 2), "preto")
    t.linha(int(hx + 1), int(hy - 4), int(hx + 6), int(hy - 2), "preto")
    # Quepe: copa, faixa e pala preta.
    t.cel(t.retangulo(hx - 6, hy - 11, 11, 6), OLIVA, sombra=1)
    t.cel(t.retangulo(hx - 6, hy - 6, 11, 2), ["sombra", "preto", "sombra", "azul_sombra"], sombra=0)
    t.cel(t.poligono([(hx + 3, hy - 5), (hx + 10, hy - 4), (hx + 9, hy - 3), (hx + 3, hy - 3.5)]), ["preto", "preto", "sombra", "azul_sombra"], sombra=0)
    t.pontos([(int(hx), int(hy - 9)), (int(hx - 1), int(hy - 8)), (int(hx + 1), int(hy - 8))], "amarelo_fogo")
    # Fuzil.
    arma(t, ox, 30, "frente")
    if p["tiro"]:
        t.chapado(t.elipse(ox + 30, 28.5, 2.2, 2.2), "amarelo_fogo")
        t.ponto(ox + 30, 28, "branco")
    t.contorno("sombra")
    return t.espelhar()


# ---------------------------------------------------------------- Disco abdutor
def disco(quadro=0):
    t = Tela(48, 24)
    cx, cy = 24, 13
    # Cúpula de vidro com piloto.
    t.cel(t.elipse(cx, cy - 4, 9, 7) & (t.yy < cy - 1), VIDRO, sombra=2, luz=2)
    t.cel(t.elipse(cx + 1, cy - 4, 3.5, 3.2), ["sombra", "alien_esc", "alien", "alien_brilho"], sombra=1)
    t.pontos([(cx, cy - 5), (cx + 2, cy - 5)], "preto")
    t.pontos([(cx - 5, cy - 8), (cx - 4, cy - 9)], "branco")
    # Casco.
    t.cel(t.elipse(cx, cy + 2, 22, 5.5), DISCO, sombra=2, luz=1)
    t.cel(t.elipse(cx, cy + 5.5, 12, 3), DISCO, sombra=1, deslocar=-1)
    t.px[int(cy + 2), 3:45][t.px[int(cy + 2), 3:45] != VAZIO] = IDX["cinza_escuro"]
    # Luzes do aro piscando em sequência.
    for k, x in enumerate(range(6, 44, 6)):
        cor = "alien_brilho" if (k + quadro) % 3 == 0 else "alien_esc"
        t.pontos([(x, int(cy + 3)), (x + 1, int(cy + 3))], cor)
    # Emissor do raio embaixo.
    t.chapado(t.elipse(cx, cy + 8, 3, 1.2), "alien_brilho" if quadro % 2 == 0 else "alien")
    t.contorno("sombra")
    return t


def feixe(quadro=0, w=26, h=110):
    """Raio abdutor: cone listrado que o jogo desenha meio transparente."""
    t = Tela(w, h)
    meio = w / 2
    for y in range(h):
        larg = 3 + (meio - 3) * y / h
        x0, x1 = int(round(meio - larg)), int(round(meio + larg))
        for x in range(x0, x1):
            faixa = (y + quadro * 4) // 6 % 2 == 0
            borda = x in (x0, x1 - 1)
            t.px[y, x] = IDX["branco" if borda else ("alien_brilho" if faixa else "horizonte")]
    return t


# ---------------------------------------------------------------- Bode Fubá
def bode(quadro="parado"):
    t = Tela(32, 26)
    base = 25
    ergue = quadro == "abduzido"
    pernas = [(9, 0), (12, 0), (20, 0), (23, 0)]
    for k, (x, _) in enumerate(pernas):
        d = -1 if k % 2 == 0 else 0
        fim = base - 1 - (4 if ergue and k % 2 else 0) - (2 if ergue else 0)
        dx = (2 if ergue and k % 2 == 0 else 0)
        t.cel(t.capsula(x, 16, x + dx, fim - 1, 1.3, 1.0), BRANCO, deslocar=d, sombra=1, luz=0)
        t.chapado(t.retangulo(x + dx - 1, fim - 1, 2, 2), "preto")
    # Corpo e rabinho.
    t.cel(t.elipse(16, 14, 10, 5.5), BRANCO, sombra=2)
    t.cel(t.elipse(6, 10, 1.6, 2.4, ang=-0.6), BRANCO, sombra=1)
    # Manchas.
    t.cel(t.elipse(13, 12, 3, 2), ["terra", "terra", "barro", "barro"], sombra=1, luz=0)
    # Cabeça, chifres, barbicha e orelha.
    hx, hy = 26, 8
    t.cel(t.capsula(hx - 2, hy + 1, hx + 3, hy + 3, 3.2, 2.5), BRANCO, sombra=1)
    t.cel(t.capsula(hx - 2, hy - 2, hx - 6, hy - 6, 1.2, 0.7), CHIFRE, sombra=1, luz=0)
    t.cel(t.capsula(hx - 4, hy + 1, hx - 7, hy + 3, 1.4, 1.0), BRANCO, sombra=1, deslocar=-1)
    t.cel(t.capsula(hx + 3, hy + 5, hx + 3, hy + 8, 1.0, 0.6), ["couro_escuro", "couro_escuro", "couro", "couro_claro"], sombra=0, luz=0)
    t.chapado(t.retangulo(hx, hy, 2, 2), "preto")
    t.ponto(hx, hy, "amarelo_fogo")
    if quadro == "mastiga":
        t.chapado(t.retangulo(hx + 4, hy + 4, 2, 1), "vermelho_esc")
    elif ergue:
        t.chapado(t.retangulo(hx + 3, hy + 4, 3, 2), "sombra")
    t.contorno("sombra")
    return t


# ---------------------------------------------------------------- Refém
def refem(quadro="amarrado1"):
    """Romeiro amarrado, ajoelhado. Solto, pula de alegria."""
    t = Tela(36, 40)
    ox = 18
    solto = quadro.startswith("solto")
    pulo = 4 if quadro == "solto2" else 0
    base = 38 - pulo
    # Pernas (ajoelhado ou em pé).
    if solto:
        for k, dx in enumerate((-3, 3)):
            t.cel(t.capsula(ox + dx, base - 10, ox + dx * 1.3, base - 2, 2.4), BRANCO, deslocar=-1 if k == 0 else 0, sombra=1)
            t.cel(t.elipse(ox + dx * 1.3 + 1, base - 1, 3, 1.5), COURO, sombra=1)
    else:
        t.cel(t.capsula(ox - 6, base - 3, ox + 4, base - 3, 3), BRANCO, sombra=1)
        t.cel(t.elipse(ox - 7, base - 2, 2.5, 1.5), COURO, sombra=1)
    # Corpo de camisa branca.
    tronco_y = base - (17 if solto else 12)
    balanco = 1 if quadro == "amarrado2" else 0
    t.cel(t.elipse(ox + balanco, tronco_y, 6.5, 7), BRANCO, sombra=2)
    if solto:
        for lado in (-1, 1):
            t.cel(t.capsula(ox + lado * 5, tronco_y - 3, ox + lado * 8, tronco_y - 11, 2, 1.8), BRANCO, sombra=1)
            t.cel(t.elipse(ox + lado * 8, tronco_y - 12, 1.8, 1.8), PELE, sombra=1)
    else:
        # Corda enrolada no corpo.
        for dy in (-3, 0, 3):
            t.linha(int(ox - 6 + balanco), int(tronco_y + dy), int(ox + 6 + balanco), int(tronco_y + dy - 1), "couro_claro")
    # Cabeça com chapéu de palha.
    hx, hy = ox + 1 + balanco, tronco_y - 10
    t.cel(t.elipse(hx, hy, 5, 5.2), ROSTO, sombra=1, linha=False)
    if solto:
        t.chapado(t.retangulo(hx + 1, hy + 2, 3, 2), "sombra")
        t.pontos([(hx + 1, hy - 1), (hx + 3, hy - 1)], "preto")
    else:
        t.pontos([(hx + 1, hy), (hx + 3, hy)], "preto")
        t.pontos([(hx + 1, hy - 2), (hx + 4, hy - 1)], "couro")
        t.chapado(t.retangulo(hx + 1, hy + 3, 3, 1), "couro")
        # Mordaça.
        t.chapado(t.retangulo(hx - 4, hy + 2, 9, 1.5), "couro_claro")
    t.cel(t.elipse(hx, hy - 4, 8.5, 1.6), PALHA, sombra=1)
    t.cel(t.elipse(hx, hy - 6, 4.5, 2.8) & (t.yy < hy - 4), PALHA, sombra=1)
    t.chapado(t.retangulo(hx - 4, hy - 5, 9, 1), "vermelho")
    t.contorno("sombra")
    return t


# ---------------------------------------------------------------- Explosão
def explosao(quadro, n=7, tam=56, semente=5):
    """Bola de fogo que cresce, escurece em fumaça e se desfaz."""
    t = Tela(tam, tam)
    rng = np.random.default_rng(semente)
    c = tam / 2
    f = quadro / (n - 1)
    raio = 7 + 16 * min(1, f * 2.2)
    fogo = [["amarelo_fogo", "amarelo_fogo", "branco", "branco"],
            ["laranja_fogo", "laranja_fogo", "amarelo_fogo", "branco"],
            ["vermelho", "laranja_fogo", "amarelo_fogo", "amarelo_fogo"],
            ["vermelho_esc", "vermelho", "laranja_fogo", "amarelo_fogo"],
            ["sombra", "azul_sombra", "vermelho_esc", "laranja_fogo"],
            ["sombra", "azul_sombra", "cinza_escuro", "cinza"],
            ["azul_sombra", "cinza_escuro", "cinza", "cinza_claro"]][quadro]
    sobe = f * 10
    puffs = []
    for k in range(9):
        ang = k / 9 * 2 * np.pi + rng.uniform(-0.3, 0.3)
        d = raio * rng.uniform(0.35, 0.65)
        r = raio * rng.uniform(0.38, 0.55) * (1 - max(0, f - 0.7) * 1.2)
        puffs.append((c + np.cos(ang) * d, c + np.sin(ang) * d * 0.8 - sobe, r))
    puffs.append((c, c - sobe, raio * 0.55))
    for x, y, r in sorted(puffs, key=lambda q: q[1]):
        if r > 1:
            t.cel(t.elipse(x, y, r, r), fogo, sombra=2, luz=2, linha=False, rebaixo=True)
    if quadro <= 1:
        t.cel(t.elipse(c, c, raio * 0.45, raio * 0.45), ["amarelo_fogo", "branco", "branco", "branco"], sombra=1, luz=0, linha=False)
    if 2 <= quadro <= 4:
        # Brasas soltas.
        for _ in range(8):
            a = rng.uniform(0, 2 * np.pi)
            d = raio * rng.uniform(1.0, 1.25)
            t.ponto(int(c + np.cos(a) * d), int(c + np.sin(a) * d - sobe), "amarelo_fogo")
    if quadro >= 5:
        # Fumaça se desfazendo: tira pixels em padrão pontilhado.
        buraco = (np.add.outer(np.arange(tam), np.arange(tam)) % (2 if quadro == 6 else 3)) == 0
        t.px[buraco] = VAZIO
    return t


# ---------------------------------------------------------------- Mortes
def carbonizar(tela):
    """Versão queimada: tudo vira carvão, menos os olhos (que ficam brancos)."""
    t = Tela(tela.w, tela.h)
    m = tela.px != VAZIO
    preto = tela.px == IDX["preto"]
    t.px[m] = IDX["sombra"]
    t.px[m & ((t.yy.astype(int) + t.xx.astype(int)) % 3 == 0)] = IDX["preto"]
    t.px[preto] = IDX["branco"]
    t.px[m & ~np.roll(m, 1, axis=0)] = IDX["cinza_escuro"]
    return t


def derretendo(quadro):
    """Alienígena derretendo em poça de gosma (3 quadros)."""
    if quadro == 0:
        # Amolece: achata o corpo para baixo e escorrem pingos.
        orig = alien({"boca": "grito", "olho": "aberto"})
        t = Tela(40, 44)
        base = 42
        for y in range(t.h):
            fonte = int(round(base - (base - y) / 0.72))
            if 0 <= fonte < t.h:
                t.px[y] = orig.px[fonte]
        for x in (12, 19, 27):
            col = t.px[:, x]
            ys = np.where(col != VAZIO)[0]
            if len(ys):
                t.px[ys.max():min(t.h, ys.max() + 3), x] = IDX["alien"]
        t.chapado(t.elipse(20, 42, 11, 1.6), "alien_esc")
        return t
    t = Tela(40, 44)
    alt = 10 if quadro == 1 else 4
    larg = 12 if quadro == 1 else 17
    t.cel(t.elipse(20, 42 - alt / 2, larg, alt / 2 + 1) & (t.yy < 43), ["sombra", "alien_esc", "alien", "alien_brilho"], sombra=1, luz=1)
    for ex in (16, 23):
        t.chapado(t.elipse(ex, 41 - alt, 2, 2.2), "preto")
        t.ponto(ex - 1, 40 - alt, "branco")
    t.contorno("sombra")
    return t
