"""Lampião, Maria Bonita e o alienígena, desenhados por partes.

Cada pose é um dicionário de deslocamentos; as partes são sempre as mesmas,
o que mantém a consistência entre quadros.
"""
from motor import Tela

W, H = 56, 52
PE = 50  # linha do chão dentro do quadro

PELE = ["couro", "pele_escura", "pele", "pele_clara"]
ROSTO = ["pele_escura", "pele", "pele_clara", "pele_clara"]
CAQUI = ["terra_escura", "terra", "barro", "areia"]
CAQUI_CLARO = ["terra", "barro", "areia", "areia_clara"]
MESCLA = ["sombra", "azul_sombra", "cinza_escuro", "cinza"]
COURO = ["couro_escuro", "couro", "couro_claro", "barro"]
CHAPEU = ["couro_escuro", "couro", "couro_claro", "areia"]
ACO = ["sombra", "cinza_escuro", "cinza", "cinza_claro"]
MADEIRA = ["couro_escuro", "couro", "couro_claro", "barro"]
VERMELHO = ["vermelho_esc", "vermelho_esc", "vermelho", "laranja_fogo"]
AZUL = ["sombra", "azul_sombra", "ceu_escuro", "ceu"]
CABELO = ["preto", "preto", "sombra", "azul_sombra"]
ALIEN = ["sombra", "alien_esc", "alien", "alien_brilho"]
METAL_ALIEN = ["sombra", "azul_sombra", "cinza", "cinza_claro"]

PERNAS = {
    # (quadril, joelho, pé) da perna de trás e da perna da frente, relativos ao centro.
    "parado": [((-2, 37), (-3, 43), (-4, PE)), ((3, 37), (4, 43), (5, PE))],
    "corre1": [((-1, 37), (-6, 41), (-10, 47)), ((2, 37), (7, 41), (7, PE))],
    "corre2": [((0, 37), (2, 43), (-1, PE)), ((1, 37), (4, 42), (1, 47))],
    "corre3": [((-1, 37), (3, 41), (6, PE)), ((2, 37), (-3, 42), (-7, 47))],
    "pulo": [((-2, 36), (-6, 40), (-4, 45)), ((3, 36), (8, 39), (6, 44))],
    "agachado": [((-2, 41), (-7, 44), (-6, PE)), ((3, 41), (8, 43), (6, PE))],
}


def perna(t, ox, quadril, joelho, pe, atras):
    d = -1 if atras else 0
    (hx, hy), (jx, jy), (px, py) = [(ox + a, b) for a, b in (quadril, joelho, pe)]
    t.cel(t.capsula(hx, hy, jx, jy, 3.0, 2.6), MESCLA, deslocar=d)
    # Perneira de couro.
    t.cel(t.capsula(jx, jy, px, py - 2.5, 2.7, 2.4), COURO, deslocar=d)
    # Alpercata.
    t.cel(t.elipse(px + 1.5, py - 1.2, 4.0, 1.9), COURO, deslocar=d - 1, sombra=1)
    t.chapado(t.retangulo(px - 2.2, py - 0.3, 7.5, 1), "couro_escuro")


def lampiao(pose=None):
    p = {"dx": 0, "dy": 0, "pernas": "parado", "mira": "frente", "boca": "sorriso"}
    p.update(pose or {})
    t = Tela(W, H)
    ox = 24 + p["dx"]
    agachado = p["pernas"] == "agachado"
    yo = p["dy"] + (5 if agachado else 0)

    tras, frente = PERNAS[p["pernas"]]
    perna(t, ox, *tras, atras=True)
    perna(t, ox, *frente, atras=False)

    # Embornal bordado pendurado atrás.
    t.cel(t.elipse(ox - 8, 34 + yo, 3.8, 4.2), VERMELHO)
    t.pontos([(ox - 9, 33 + yo), (ox - 8, 34 + yo), (ox - 9, 35 + yo), (ox - 7, 36 + yo)], "amarelo_fogo")
    t.linha(ox - 6, 26 + yo, ox - 8, 30 + yo, "couro_escuro")

    if p["mira"] != "cima":
        # Braço de trás, segurando o fuzil por baixo.
        t.cel(t.capsula(ox - 2, 27 + yo, ox + 7, 31 + yo, 2.6, 2.3), CAQUI, deslocar=-1)

    # Tronco atarracado: gibão cáqui.
    t.cel(t.elipse(ox, 31 + yo, 8.2, 7.8), CAQUI_CLARO, sombra=3)
    # Cartucheiras cruzadas com balas douradas.
    for sinal in (1, -1):
        t.cel(t.capsula(ox - 7 * sinal, 25 + yo, ox + 6 * sinal, 37 + yo, 1.5), COURO, sombra=1, luz=0)
    for k in range(5):
        t.ponto(int(ox - 5 + k * 2.6), int(26.5 + yo + k * 2.3), "amarelo_fogo")
        t.ponto(int(ox + 4.5 - k * 2.6), int(26.5 + yo + k * 2.3), "amarelo_fogo")
    # Cinturão com fivela.
    t.cel(t.retangulo(ox - 8, 36 + yo, 16, 3), COURO, sombra=1)
    t.chapado(t.retangulo(ox, 36.5 + yo, 3, 2), "amarelo_fogo")
    t.ponto(ox + 1, 37 + int(yo), "couro")

    # Lenço vermelho.
    t.cel(t.elipse(ox + 1, 24 + yo, 5.2, 2.2), VERMELHO, sombra=1)
    t.cel(t.poligono([(ox - 3, 24 + yo), (ox - 7, 29 + yo), (ox - 1, 26 + yo)]), VERMELHO, sombra=1)

    cabeca_lampiao(t, ox + 2, 16 + yo, p["boca"])
    arma(t, ox, 30 + yo, p["mira"])
    t.contorno("sombra")
    return t


def chapeu_meia_lua(t, hx, hy, largura=12.5, altura=8.0, copa=(6.5, 4.0)):
    """Chapéu de couro de cangaceiro: de perfil a aba virada forma uma meia-lua
    com as pontas para cima, a copa aparece no meio."""
    cx, cy = hx - 0.5, hy - 5
    t.cel(t.elipse(cx - 1, cy - 2.5, *copa), CHAPEU, sombra=1, deslocar=-1)
    lua = t.elipse(cx, cy - 4, largura, altura) & ~t.elipse(cx - 0.5, cy - 9.5, largura - 1.5, altura + 1.5)
    lua &= t.yy < cy + 2.5
    t.cel(lua, CHAPEU, sombra=1)
    # Friso escuro na borda de cima da aba.
    friso = lua & ~t.elipse(cx, cy - 3.5, largura - 0.8, altura - 0.8)
    t.chapado(friso & (t.yy < cy + 1), "couro_escuro")
    return cx, cy


def cabeca_lampiao(t, hx, hy, boca):
    # Cabeça grande, caricata.
    t.cel(t.elipse(hx, hy, 6.6, 6.6), ROSTO, sombra=1, linha=False)
    # Orelha.
    t.pontos([(int(hx - 4), int(hy)), (int(hx - 4), int(hy + 1)), (int(hx - 3), int(hy + 2))], "pele")
    # Nariz de batata.
    t.cel(t.elipse(hx + 6.3, hy + 1.6, 2.4, 2.1), ROSTO, sombra=1)
    # Bigode curto.
    t.chapado(t.retangulo(hx + 3, hy + 3.5, 4, 1), "couro_escuro")
    # Boca.
    if boca == "sorriso":
        t.chapado(t.retangulo(hx + 3, hy + 5, 4, 2), "sombra")
        t.chapado(t.retangulo(hx + 3, hy + 5, 3, 1), "branco")
    else:
        t.chapado(t.retangulo(hx + 2, hy + 5, 5, 3), "sombra")
        t.chapado(t.retangulo(hx + 3, hy + 7, 3, 1), "vermelho")
        t.chapado(t.retangulo(hx + 3, hy + 5, 3, 1), "branco")
    # Óculos redondos, a marca do Lampião.
    t.chapado(t.elipse(hx + 3.2, hy - 0.4, 2.6, 2.6), "sombra")
    t.chapado(t.elipse(hx + 3.2, hy - 0.4, 1.5, 1.5), "ceu_claro")
    t.ponto(int(hx + 2), int(hy - 2), "branco")
    t.ponto(int(hx + 3), int(hy), "sombra")
    t.linha(int(hx - 3), int(hy - 1), int(hx), int(hy - 1), "sombra")
    t.linha(int(hx + 1), int(hy - 4), int(hx + 5), int(hy - 3), "couro_escuro")
    cx, cy = chapeu_meia_lua(t, hx, hy)
    # Estrela de Salomão na frente da aba e moedas no friso.
    sx, sy = int(cx + 1), int(cy - 1)
    t.pontos([(sx, sy - 2), (sx - 1, sy - 1), (sx, sy - 1), (sx + 1, sy - 1), (sx - 2, sy), (sx - 1, sy),
              (sx, sy), (sx + 1, sy), (sx + 2, sy), (sx - 1, sy + 1), (sx + 1, sy + 1)], "amarelo_fogo")
    t.ponto(sx, sy - 1, "branco")
    for mx, my in ((cx - 7, cy - 2), (cx - 4, cy), (cx + 5, cy), (cx + 8, cy - 2)):
        t.ponto(int(mx), int(my), "amarelo_fogo")


def arma(t, ox, y, mira):
    if mira == "cima":
        t.cel(t.retangulo(ox + 3, y - 30, 2.5, 16), ACO, sombra=1)
        t.chapado(t.retangulo(ox + 2.5, y - 31, 3.5, 1), "cinza_claro")
        t.cel(t.retangulo(ox + 2.5, y - 15, 3.5, 9), ACO, sombra=1)
        t.cel(t.poligono([(ox + 2, y - 7), (ox + 6.5, y - 7), (ox + 6, y + 3), (ox + 1.5, y + 2)]), MADEIRA, sombra=1)
        t.cel(t.capsula(ox - 1, y - 2, ox + 3, y - 9, 2.6, 2.3), CAQUI, sombra=1)
        t.cel(t.elipse(ox + 4.2, y - 9.5, 2.2, 2.0), PELE, sombra=1)
        t.cel(t.capsula(ox - 3, y - 1, ox + 3, y + 1, 2.4), CAQUI, deslocar=-1, sombra=1)
        t.cel(t.elipse(ox + 4, y + 1.5, 2, 1.9), PELE, sombra=1)
        return
    # Fuzil para a frente: coronha de madeira, ferrolho e cano longo.
    t.cel(t.poligono([(ox - 4, y - 2), (ox + 6, y - 1.5), (ox + 6, y + 1.5), (ox - 3, y + 4.5)]), MADEIRA, sombra=1)
    t.cel(t.retangulo(ox + 5, y - 2, 10, 3.5), MADEIRA, sombra=1)
    t.cel(t.retangulo(ox + 7, y - 3, 6, 1.5), ACO, sombra=0)
    t.cel(t.retangulo(ox + 14, y - 1.8, 14, 2.2), ACO, sombra=1)
    t.chapado(t.retangulo(ox + 27, y - 2.8, 1, 1), "cinza_claro")
    # Braço da frente e mãos.
    t.cel(t.capsula(ox + 1, y - 5, ox + 6, y, 2.7, 2.4), CAQUI, sombra=1)
    t.cel(t.elipse(ox + 7.2, y + 0.4, 2.2, 2.0), PELE, sombra=1)
    t.cel(t.elipse(ox + 14.5, y + 1.2, 2.0, 1.8), PELE, sombra=1)


def maria_bonita(pose=None):
    p = {"dx": 0, "dy": 0, "pernas": "parado", "mira": "frente", "boca": "sorriso"}
    p.update(pose or {})
    t = Tela(W, H)
    ox = 24 + p["dx"]
    agachado = p["pernas"] == "agachado"
    no_ar = p["pernas"] == "pulo"
    yo = p["dy"] + (5 if agachado else 0)
    # Pernas com botas de couro (as mesmas posições do Lampião).
    for k, (quadril, joelho, pe) in enumerate(PERNAS[p["pernas"]]):
        d = -1 if k == 0 else 0
        (jx, jy), (px, py) = (ox + joelho[0], joelho[1]), (ox + pe[0], pe[1])
        t.cel(t.capsula(ox + quadril[0], quadril[1] + 2, jx, jy, 2.3, 2.1), PELE, deslocar=d, sombra=1)
        t.cel(t.capsula(jx, jy, px, py - 2.5, 2.3, 2.1), COURO, deslocar=d, sombra=1)
        t.cel(t.elipse(px + 1.5, py - 1.2, 3.5, 1.8), COURO, deslocar=d - 1, sombra=1)
    # Cabelo comprido atrás (balança no pulo).
    t.cel(t.elipse(ox - 3 - (2 if no_ar else 0), 24 + yo - (1 if no_ar else 0), 4.8, 8), CABELO, sombra=1)
    # Saia rodada azul com pregas; abre no pulo.
    abre = 3 if no_ar else 0
    fundo = 44 + yo - (3 if no_ar else 0)
    t.cel(t.poligono([(ox - 6, 32 + yo), (ox + 7, 32 + yo), (ox + 10 + abre, fundo), (ox - 10 - abre, fundo)]), AZUL, sombra=2)
    for k in range(4):
        t.linha(int(ox - 5 + k * 4), int(35 + yo), int(ox - 7 - abre + k * (5 + abre * 0.6)), int(fundo - 1), "azul_sombra")
    t.chapado(t.retangulo(ox - 10 - abre, fundo - 1, 20 + abre * 2, 1), "ceu")
    # Blusa cáqui e cartucheira.
    t.cel(t.elipse(ox, 28 + yo, 6.4, 5.8), CAQUI_CLARO, sombra=2)
    t.cel(t.capsula(ox - 5, 24 + yo, ox + 5, 33 + yo, 1.3), COURO, sombra=1, luz=0)
    for k in range(4):
        t.ponto(int(ox - 3 + k * 2.4), int(26 + yo + k * 2.2), "amarelo_fogo")
    t.cel(t.retangulo(ox - 6, 32 + yo, 13, 2), COURO, sombra=1)
    t.cel(t.elipse(ox + 1, 22.5 + yo, 4.4, 1.9), VERMELHO, sombra=1)
    # Cabeça.
    hx, hy = ox + 2, 15 + yo
    t.cel(t.elipse(hx, hy, 5.8, 6.2), ROSTO, sombra=1, linha=False)
    t.cel(t.elipse(hx + 5.5, hy + 1.2, 1.6, 1.5), ROSTO, sombra=1)
    # Olho grande com cílios, batom vermelho, pinta.
    t.chapado(t.elipse(hx + 3, hy - 0.3, 1.5, 2), "branco")
    t.chapado(t.retangulo(hx + 3, hy - 1, 2, 2), "sombra")
    t.pontos([(int(hx + 2), int(hy - 3)), (int(hx + 3), int(hy - 3)), (int(hx + 5), int(hy - 3))], "preto")
    if p["boca"] == "grito":
        t.chapado(t.retangulo(hx + 3, hy + 3, 3, 3), "sombra")
        t.chapado(t.retangulo(hx + 3, hy + 3, 3, 1), "vermelho")
    else:
        t.chapado(t.retangulo(hx + 3, hy + 4, 3, 1), "vermelho")
    t.ponto(int(hx + 1), int(hy + 2), "couro")
    t.ponto(int(hx + 1), int(hy + 1), "pele_clara")
    # Franja escura.
    t.cel(t.elipse(hx - 1.5, hy - 3.5, 5.6, 3.2), CABELO, sombra=1)
    # Chapéu de couro em meia-lua, menor.
    cx, cy = chapeu_meia_lua(t, hx, hy - 1.5, largura=10, altura=6.5, copa=(5.5, 3.4))
    t.pontos([(int(cx + 1), int(cy - 2)), (int(cx), int(cy - 1)), (int(cx + 2), int(cy - 1)), (int(cx + 1), int(cy))], "amarelo_fogo")
    # Braço com revólver.
    y = 27 + yo
    if p["mira"] == "cima":
        t.cel(t.capsula(ox + 1, y - 1, ox + 5, y - 7, 2.4, 2.1), CAQUI, sombra=1)
        t.cel(t.retangulo(ox + 4.5, y - 17, 2.2, 9), ACO, sombra=1)
        t.cel(t.retangulo(ox + 3, y - 9, 4, 3), MADEIRA, sombra=1)
        t.cel(t.elipse(ox + 5, y - 8, 2.1, 2), PELE, sombra=1)
    else:
        t.cel(t.capsula(ox + 1, y - 2, ox + 7, y + 2, 2.4, 2.1), CAQUI, sombra=1)
        t.cel(t.retangulo(ox + 8, y - 0.5, 8, 2.2), ACO, sombra=1)
        t.cel(t.retangulo(ox + 7, y + 1, 3, 4), MADEIRA, sombra=1)
        t.cel(t.elipse(ox + 8, y + 2, 2.1, 2), PELE, sombra=1)
    t.contorno("sombra")
    return t


def alien(pose=None):
    """Soldado xeremita, virado para a esquerda.

    pose: dy (sobe/desce o corpo), olho (aberto/fechado), boca (normal/grito),
    pes [(dx, ergue), (dx, ergue)] das pernas de trás e da frente, tiro (brilho no cano).
    """
    p = {"dy": 0, "olho": "aberto", "boca": "normal", "pes": [(0, 0), (0, 0)], "tiro": False}
    p.update(pose or {})
    t = Tela(40, 44)
    ox, oy = 20, p["dy"]
    base = 42
    for k, x in enumerate((ox + 3, ox - 4)):
        d = -1 if k == 0 else 0
        dx, ergue = p["pes"][k]
        t.cel(t.capsula(x, 30 + oy, x + 1 + dx, base - 2 - ergue, 1.8, 1.5), ALIEN, deslocar=d, sombra=1)
        t.cel(t.elipse(x - 1 + dx, base - 1 - ergue, 3.2, 1.6), ALIEN, deslocar=d - 1, sombra=1)
    # Corpo com macacão metálico e luz no peito.
    t.cel(t.elipse(ox, 27 + oy, 6, 6.2), METAL_ALIEN, sombra=2)
    t.cel(t.retangulo(ox - 5, 28 + oy, 10, 2), ["sombra", "cinza_escuro", "cinza", "cinza_claro"], sombra=1)
    t.chapado(t.elipse(ox - 1, 25 + oy, 1.5, 1.5), "alien_brilho")
    t.ponto(ox - 2, 24 + oy, "branco")
    # Braço com pistola de raios apontada para a esquerda.
    t.cel(t.capsula(ox, 24 + oy, ox - 7, 28 + oy, 1.7, 1.5), ALIEN, sombra=1)
    t.cel(t.retangulo(ox - 13, 26.5 + oy, 7, 2.6), ["sombra", "cinza_escuro", "cinza", "cinza_claro"], sombra=1)
    t.chapado(t.retangulo(ox - 14, 27 + oy, 1, 1.6), "alien_brilho")
    if p["tiro"]:
        t.chapado(t.elipse(ox - 15, 27.8 + oy, 2.2, 2.2), "alien_brilho")
        t.ponto(ox - 15, 27 + oy, "branco")
    t.cel(t.elipse(ox - 7, 28 + oy, 1.8, 1.7), ALIEN, sombra=1)
    # Cabeçona.
    hx, hy = ox, 12 + oy
    t.cel(t.elipse(hx, hy, 10, 9), ALIEN, sombra=3)
    t.cel(t.elipse(hx, hy + 7.5, 3.5, 2.5), ALIEN, sombra=1, deslocar=-1)
    t.pontos([(hx - 3, hy - 6), (hx - 2, hy - 5), (hx - 2, hy - 4), (hx + 2, hy - 6), (hx + 3, hy - 7)], "alien_esc")
    for ex in (hx - 5, hx + 2):
        if p["olho"] == "aberto":
            t.chapado(t.elipse(ex, hy + 1, 3.2, 3.8, ang=0.3), "preto")
            t.ponto(ex - 2, hy - 1, "branco")
            t.ponto(ex - 1, hy, "alien_brilho")
        else:
            t.chapado(t.retangulo(ex - 3, hy + 1, 6, 1), "preto")
    if p["boca"] == "grito":
        t.chapado(t.elipse(hx - 2, hy + 6.5, 2, 1.8), "preto")
    else:
        t.chapado(t.retangulo(hx - 3, hy + 6, 3, 1), "alien_esc")
    t.linha(hx + 1, hy - 9, hx + 3, hy - 13, "alien_esc")
    t.chapado(t.elipse(hx + 3.5, hy - 13.5, 1.5, 1.5), "alien_brilho")
    t.contorno("sombra")
    return t
