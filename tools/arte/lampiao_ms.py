"""Lampião no padrão novo (20/10): corpo do Metal Slug (cabeça ~1/4 da altura, tronco
largo arredondado, mãos e alpercatas grandes, joelho dobrado), volume de cúpula com
luz de um lado (volume3d.sombrear2d) e as rampas saturadas da paleta.

Mantém o que foi aprovado antes: sem bornal, sem óculos (olho branco com pupila),
chapéu de couro em meia-lua com moedas e a estrela, cartucheira de balas de latão.

Mesma folha, mesma ordem de quadros e mesmo pé (14, 63) do lampiao_armas.py antigo,
então o jogo não muda: só o desenho. Chamado por tools/arte/exportar.py.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import armas as ar  # noqa: E402
from gente import R, bota, mao, tronco_forma  # noqa: E402
from motor import IDX, VAZIO, Tela  # noqa: E402
from volume3d import sombrear2d  # noqa: E402

W, H = 60, 72
PE = (14, 63)
CHAO = 63

PELE = R("carne", 1, 7)
NARIZ = R("carne", 2, 7)
CAMISA = R("osso", 1, 5)
CALCA = R("aco", 1, 6)
COURO = R("fuba", 1, 6)
CHAPEU = R("fuba", 1, 6)
CABELO = R("negro", 1, 4)
LENCO = R("rubro", 1, 6)
LATAO = R("latao", 2, 6)

QUADROS = ["parado", "atirando", "corre1", "corre2", "corre3", "corre4", "corre5", "corre6",
           "pulo", "agachado", "mira_cima", "susto", "arremesso", "facada", "facada1", "mira_baixo", "recarga",
           "morte1", "morte2", "morte3", "espera1", "espera2", "espera3", "parado2"]
ROSTO = {"parado": "serio", "parado2": "serio", "agachado": "serio", "susto": "susto", "mira_baixo": "baixo",
         "mira_cima": "cima", "espera1": "boceja", "espera2": "olha", "espera3": "suor"}

BX = 13          # meio do tronco
QUADRIL = 49
TOPO, BASE = 34, 50  # tronco
CABECA = (16, 29)    # centro do rosto
OMBRO_F = (17, 37)
OMBRO_T = (12, 37)

# Pegada de cada arma (mesma ideia do lampiao_armas.py): punho = mão de trás no cabo,
# cot_* = cotovelos, apoio = a mão da frente segura o guarda-mão.
POSES = {
    "pistola": {"punho": (24, 40), "cot_frente": (22, 41), "um_braco": True},
    "madsen": {"punho": (22, 43), "cot_tras": (15, 45), "cot_frente": (22, 45), "apoio": True},
    "bacamarte": {"punho": (19, 45), "cot_tras": (14, 46), "cot_frente": (21, 47), "apoio": True},
    "papo_amarelo": {"punho": (18, 37), "cot_tras": (14, 42), "cot_frente": (22, 42), "apoio": True},
    "rojao": {"punho": (12, 44), "cot_tras": (10, 43), "cot_frente": (19, 42), "apoio": True},
    "desintegrador": {"punho": (23, 40), "cot_frente": (21, 41), "um_braco": True},
    "candeeiro": {"punho": (22, 44), "cot_tras": (15, 46), "cot_frente": (21, 46), "apoio": True,
                  "recorte": (8, 32), "costas": (0, 8)},
    "estilingue": {"punho": (27, 36), "cot_frente": (22, 38), "um_braco": True, "puxa": (19, 33)},
    "buscape": {"punho": (18, 45), "cot_tras": (14, 45), "cot_frente": (20, 45), "apoio": True},
}

# Pernas: (pé de trás, pé da frente) em relação ao quadril, e quanto o corpo desce.
PERNAS = {
    "parado": ((-6, 14), (6, 14), 0),
    "pulo": ((-7, 9), (5, 8), 0),
    "agachado": ((-8, 7), (8, 7), 7),
    "esticado": ((-2, 14), (3, 14), 0),
}
# Corrida em 6 tempos: (dx do pé, quanto o pé sobe do chão).
CICLO = [(8, 0), (4, 0), (-1, 0), (-6, 1), (-6, 5), (2, 5)]
for _k in range(6):
    a, b = CICLO[(_k + 3) % 6], CICLO[_k]
    PERNAS[f"corre{_k + 1}"] = ((a[0], 14 - a[1]), (b[0], 14 - b[1]), -1 if _k in (1, 4) else 0)


# ---------------------------------------------------------------- peças
def _borda_baixo(t, m, cor, y_min):
    """Separação da peça de trás: a beirada de baixo leva o tom mais escuro."""
    from scipy import ndimage
    borda = m & ~ndimage.binary_erosion(m)
    baixo = np.zeros_like(m)
    baixo[:-1] = ~m[1:]
    t.px[borda & baixo & (t.yy > y_min)] = IDX[cor]


def perna(t, quadril, pe, atras=False):
    """Calça de brim azulada até o joelho, perneira de couro até a alpercata."""
    d = -1.2 if atras else 0.0
    hx, hy = quadril
    px, py = pe
    jx = (hx + px) / 2 + 2.2
    jy = (hy + py) / 2 - (1 if py < CHAO else 0)
    coxa = t.capsula(hx, hy, jx, jy, 3.1, 2.7)
    sombrear2d(t, coxa, CALCA, d)
    canela = t.capsula(jx, jy, px, py - 2, 2.6, 2.3) & ~coxa
    sombrear2d(t, canela, COURO, d)
    _borda_baixo(t, coxa | canela, "aco_1", hy + 1)
    # Correia da perneira e a fivela de latão.
    t.linha(jx - 2, jy + 2, jx + 2, jy + 1.5, "fuba_1")
    if not atras:
        t.ponto(jx + 1, jy + 2, "latao_5")
    bota(t, px - 2, py, d)


def braco(t, ombro, cotovelo, punho, atras=False, mao_aberta=True):
    d = -1.2 if atras else 0.0
    m = t.capsula(*ombro, *cotovelo, 2.4, 2.1) | t.capsula(*cotovelo, *punho, 2.1, 1.8)
    sombrear2d(t, m, CAMISA, d)
    _borda_baixo(t, m, "osso_1", ombro[1] + 1)
    # Punho da manga dobrado.
    vx, vy = punho[0] - cotovelo[0], punho[1] - cotovelo[1]
    n = max(1e-6, (vx * vx + vy * vy) ** 0.5)
    t.ponto(punho[0] - vx / n * 1.5, punho[1] - vy / n * 1.5, "osso_2")
    return m


def punho_fechado(t, x, y, atras=False):
    sombrear2d(t, t.elipse(x, y, 2.1, 1.9), PELE, -1 if atras else 0)
    t.ponto(x + 1, y + 1, "carne_3")


def tronco(t, dy, costas=False):
    """Camisa de brim, cartucheira cruzada com balas de latão, cinturão de balas e o punhal."""
    topo, base = TOPO + dy, BASE + dy
    m = tronco_forma(t, BX, topo, base)
    sombrear2d(t, m, CAMISA)
    # Bolso do peito com a lapela.
    t.linha(BX + 3, topo + 6, BX + 6, topo + 6, "osso_2")
    t.ponto(BX + 4, topo + 7, "latao_4")
    # Cartucheira do ombro de trás ao quadril da frente: couro e balas de latão.
    for k in range(13):
        x = BX - 3 + k * 0.85
        y = topo + 1 + k * 1.05
        if not m[int(y), int(x)]:
            continue
        t.ponto(x, y, "fuba_2")
        t.ponto(x + 1, y, "fuba_3")
        if k % 2 == 0:
            t.ponto(x - 1, y, "latao_3")
            t.ponto(x - 1, y - 1, "latao_6")
        else:
            t.ponto(x - 1, y, "latao_2")
    # Cinturão de balas com a fivela no meio.
    cy = base - 3
    cinto = t.retangulo(BX - 5, cy, 13, 2.2) & m
    t.chapado(cinto, "fuba_2")
    for x in range(BX - 4, BX + 8, 2):
        if m[cy, x]:
            t.ponto(x, cy, "latao_5")
            t.ponto(x, cy + 1, "latao_3")
    t.chapado(t.retangulo(BX + 2, cy, 2, 2.2) & m, "latao_4")
    t.ponto(BX + 2, cy, "latao_6")
    # Punhal comprido atravessado na frente da barriga (cabo de osso, bainha de couro).
    t.linha(BX - 1, cy + 2, BX + 5, cy - 3, "fuba_1")
    t.linha(BX - 2, cy + 3, BX - 1, cy + 2, "fuba_2")
    t.linha(BX + 5, cy - 3, BX + 7, cy - 5, "osso_4")
    t.ponto(BX + 6, cy - 5, "osso_5")
    t.ponto(BX + 5, cy - 2, "latao_5")
    return m


def chapeu(t, x, y, ang=0.0):
    """Chapéu de couro em meia-lua: abas da frente e de trás viradas para cima, faixa com
    moedas de prata e a estrela de ouro na aba da frente. (x, y) = centro do rosto."""
    def P(dx, dy):
        c, s = np.cos(ang), np.sin(ang)
        return (x + dx * c - dy * s, y + dx * s + dy * c)
    copa = t.poligono([P(-4.5, -4), P(-4, -7.5), P(-1, -9), P(2.5, -9), P(4.8, -7.5), P(5, -4)])
    sombrear2d(t, copa, CHAPEU)
    aba = t.poligono([P(-10.5, -8.5), P(-8.5, -8.5), P(-6, -6.2), P(-2, -5.2), P(3, -5.2), P(7, -6.2),
                      P(9.5, -9), P(11.5, -9.2), P(11.5, -6.5), P(8, -3.8), P(3, -2.6), P(-2, -2.6), P(-7, -3.6),
                      P(-10.5, -6)])
    sombrear2d(t, aba, CHAPEU, 0.2)
    # Faixa de couro escuro no pé da copa com as moedas.
    for k in range(5):
        cx, cy = P(-3.5 + k * 2.2, -4.6)
        t.ponto(cx, cy, "fuba_1")
    for k, dx in enumerate((-6.5, -4, 4.5, 7)):
        cx, cy = P(dx, -5 - abs(dx) * 0.15)
        t.ponto(cx, cy, "pelo_7")
        t.ponto(cx, cy + 1, "pelo_4")
    # Estrela de ouro na frente da aba.
    sx, sy = P(1, -4)
    t.pontos([(sx, sy - 1), (sx - 1, sy), (sx, sy), (sx + 1, sy), (sx - 1, sy + 1), (sx + 1, sy + 1)], "latao_5")
    t.ponto(sx, sy - 1, "latao_6")
    t.ponto(sx, sy, "latao_6")
    # Barbicacho de couro descendo até o queixo.
    t.linha(*P(-3, -2), *P(1, 4.5), "fuba_1")
    return copa | aba


def cabelo(t, x, y, solto=False):
    """Cabeleira preta de cangaceiro (aparece sem o chapéu e na nuca)."""
    m = t.elipse(x - 3.5, y + 2.5, 3.2, 4.6)
    if solto:
        m |= t.elipse(x - 0.5, y - 3.2, 5.6, 3.6) | t.elipse(x - 5, y + 1, 3, 5.5)
    sombrear2d(t, m, CABELO)
    if solto:
        t.linha(x - 3, y - 5, x + 3, y - 5.5, "negro_4")


def cabeca(t, x, y, rosto="serio", com_chapeu=True, chapeu_sobe=0):
    """Cabeça pequena (10x11) do Lampião. (x, y) = centro do rosto."""
    x, y = int(round(x)), int(round(y))
    cabelo(t, x, y, solto=not com_chapeu or chapeu_sobe > 0)
    # Lenço vermelho no pescoço, com a ponta caindo no peito.
    sombrear2d(t, t.poligono([(x - 4, y + 3), (x + 3, y + 4), (x + 3, y + 7), (x + 1, y + 9), (x - 1, y + 7),
                              (x - 4, y + 6)]), LENCO)
    sombrear2d(t, t.elipse(x - 4, y + 1, 1.3, 1.7), PELE)  # orelha
    sombrear2d(t, t.elipse(x, y, 5, 5.3), PELE, 0.8)
    # Costeleta e a barba rala de cangaceiro no queixo.
    t.linha(x - 2, y - 3, x - 2, y + 1, "negro_2")
    t.ponto(x - 1, y - 3, "negro_2")
    for px_, py_ in ((x - 1, y + 4), (x + 1, y + 5), (x + 3, y + 5), (x, y + 3)):
        t.ponto(px_, py_, "carne_3")
    # Narigão.
    sombrear2d(t, t.elipse(x + 5, y + 0.5, 1.9, 1.6), NARIZ)
    t.ponto(x + 4, y + 2, "carne_2")
    _rosto(t, x, y, rosto)
    if com_chapeu:
        chapeu(t, x, y - chapeu_sobe)
        if rosto == "suor":
            for gx, gy in ((x - 2, y - 3), (x + 4, y - 4)):
                t.ponto(gx, gy, "ceu_claro")
                t.ponto(gx, gy + 1, "branco")


def _rosto(t, x, y, rosto):
    ex, ey = x + 2, y - 1  # olho
    sob = "negro_1"
    olhos_x = rosto in ("morto", "morto2")
    if olhos_x:
        t.pontos([(ex - 1, ey - 1), (ex + 1, ey - 1), (ex, ey), (ex - 1, ey + 1), (ex + 1, ey + 1)], "negro_1")
    elif rosto == "boceja":
        t.linha(ex - 1, ey, ex + 1, ey, "negro_1")
        t.linha(ex - 1, ey - 2, ex + 2, ey - 2, sob)
    elif rosto == "dor":
        t.pontos([(ex - 1, ey - 1), (ex, ey), (ex + 1, ey), (ex + 2, ey - 1)], "negro_1")
        t.linha(ex - 1, ey - 3, ex + 2, ey - 2, sob)
    else:
        grande = rosto == "susto"
        t.chapado(t.retangulo(ex - (1 if grande else 0), ey - 1 - (1 if grande else 0), 3 if grande else 2,
                              3 if grande else 2), "branco")
        pup = {"cima": (ex + 1, ey - 1), "baixo": (ex + 1, ey), "olha": (ex, ey), "susto": (ex + 1, ey)}
        t.ponto(*pup.get(rosto, (ex + 1, ey)), "negro_1")
        if rosto == "olha":
            t.ponto(ex, ey - 1, "negro_1")
        # Sobrancelha grossa: brava no grito, levantada no susto.
        if rosto in ("grito", "cima", "baixo"):
            t.linha(ex - 1, ey - 3, ex + 2, ey - 2, sob)
            t.ponto(ex - 1, ey - 2, sob)
        elif rosto == "susto":
            t.linha(ex - 1, ey - 4, ex + 2, ey - 4, sob)
        else:
            t.linha(ex - 1, ey - 2, ex + 2, ey - 2, sob)
    # Boca.
    bx, by = x + 3, y + 3
    if rosto in ("grito", "cima", "baixo"):
        t.chapado(t.elipse(bx, by + 0.5, 2.2, 1.7), "negro_1")
        t.linha(bx - 1, by - 1, bx + 1, by - 1, "pelo_7")
        t.ponto(bx, by + 1, "rubro_4")
    elif rosto == "susto":
        t.chapado(t.elipse(bx, by + 0.5, 1.4, 1.8), "negro_1")
        t.ponto(bx, by + 1, "rubro_3")
    elif rosto == "boceja":
        t.chapado(t.elipse(bx - 0.5, by + 0.5, 1.8, 2.3), "negro_1")
        t.ponto(bx - 0.5, by + 1.5, "rubro_4")
    elif rosto == "dor":
        t.linha(bx - 2, by, bx + 1, by, "negro_1")
        t.linha(bx - 1, by - 1, bx + 1, by - 1, "pelo_7")
        t.ponto(bx + 2, by - 1, "negro_1")
    elif rosto == "morto2":
        t.chapado(t.elipse(bx, by + 0.5, 1.8, 1.3), "negro_1")
        t.linha(bx + 1, by + 1, bx + 2, by + 3, "rubro_4")  # língua de fora
    elif rosto == "morto":
        t.chapado(t.elipse(bx, by + 0.5, 1.6, 1.2), "negro_1")
    else:
        t.linha(bx - 1, by, bx + 1, by + 0.5, "carne_1")


# ---------------------------------------------------------------- armas
def _arma(arma, girar=None, recorte=None):
    """Desenho da arma (Tela) e as âncoras depois do giro: (tela, punho, apoio, boca)."""
    src = ar.ARMAS[arma]()
    px = src.px.copy()
    if recorte:
        x0, x1 = recorte
        px[:, :x0] = VAZIO
        px[:, x1:] = VAZIO
    p, a, b = ar.ANCORAS[arma]
    hh, ww = px.shape

    def gira(pt):
        x, y = pt
        if girar == "cima":   # anti-horário: o cano aponta para o céu
            return (y, ww - 1 - x)
        if girar == "baixo":  # horário: o cano aponta para o chão
            return (hh - 1 - y, x)
        return (x, y)
    if girar == "cima":
        px = np.rot90(px, 1)
    elif girar == "baixo":
        px = np.rot90(px, -1)
    t = Tela(px.shape[1], px.shape[0])
    t.px = px.copy()
    return t, gira(p), gira(a), gira(b)


def colar_arma(t, arma, mao_xy, girar=None, recorte=None):
    tela, p, a, b = _arma(arma, girar, recorte)
    ox, oy = mao_xy[0] - p[0], mao_xy[1] - p[1]
    t.colar(tela, ox, oy)
    return (ox + a[0], oy + a[1]), (ox + b[0], oy + b[1])


# ---------------------------------------------------------------- quadros
def _pernas(t, nome):
    tras, frente, dy = PERNAS[nome]
    q = QUADRIL + dy
    perna(t, (BX - 1, q), (BX - 1 + tras[0], q + tras[1]), atras=True)
    return frente, dy, q


def _perna_frente(t, frente, q):
    perna(t, (BX + 2, q), (BX + 2 + frente[0], q + frente[1]))


def _desloca(p, dy):
    return (p[0], p[1] + dy)


def quadro(nome, arma="pistola", bocas=None):
    if nome.startswith("morte"):
        return quadro_morte(nome)
    t = Tela(W, H)
    rosto = ROSTO.get(nome, "grito")
    pose = POSES[arma]
    pernas = nome if nome.startswith("corre") or nome in ("pulo", "agachado") else "parado"
    if nome == "mira_baixo":
        pernas = "pulo"
    frente, dy, q = _pernas(t, pernas)
    if nome == "parado2":
        dy += 1
    of, ot = _desloca(OMBRO_F, dy), _desloca(OMBRO_T, dy)
    hx, hy = CABECA[0], CABECA[1] + dy
    maos = []

    # Lata do Candeeiro amarrada nas costas (antes de tudo).
    if pose.get("costas"):
        x0, x1 = pose["costas"]
        lata, p, _, _ = _arma(arma, recorte=(x0, x1))
        t.colar(lata, BX - 9 - x0, TOPO + dy - 2)

    if nome == "mira_cima":
        braco(t, ot, (ot[0] + 4, ot[1] + 4), (26, 30 + dy), atras=True)
        tronco(t, dy)
        _perna_frente(t, frente, q)
        cabeca(t, hx - 1, hy + 1, rosto)
        apoio, boca = colar_arma(t, arma, (27, 30 + dy), "cima", pose.get("recorte"))
        braco(t, of, (of[0] + 6, of[1] + 2), (27, 24 + dy))
        punho_fechado(t, 26, 30 + dy, atras=True)
        punho_fechado(t, 27, 24 + dy)
        if bocas is not None:
            bocas["cima"] = [boca[0] - PE[0], PE[1] - boca[1]]
        return _fim(t)

    if nome == "mira_baixo":
        braco(t, ot, (ot[0] + 3, ot[1] + 6), (20, 44 + dy), atras=True)
        tronco(t, dy)
        _perna_frente(t, frente, q)
        cabeca(t, hx + 1, hy + 2, rosto)
        mx, my = 21, 48 + dy
        tela, p, a, b = _arma(arma, "baixo", pose.get("recorte"))
        my -= max(0, (my - p[1] + tela.h - 1) - (H - 2))  # arma comprida: não sai do quadro
        apoio, boca = colar_arma(t, arma, (mx, my), "baixo", pose.get("recorte"))
        braco(t, of, (of[0] + 5, of[1] + 5), (mx, my))
        punho_fechado(t, mx - 1, my - 4, atras=True)
        punho_fechado(t, mx, my)
        if bocas is not None:
            bocas["baixo"] = [boca[0] - PE[0], PE[1] - boca[1]]
        return _fim(t)

    arremesso = nome == "arremesso"
    facada = nome in ("facada", "facada1")
    gx, gy = pose["punho"]
    if arma == "estilingue" and nome not in ("recarga", "atirando"):
        gx, gy = gx - 2, gy + 6  # baladeira descansando no peito
    gy += dy
    um = pose.get("um_braco")
    # Braço de trás (atrás do tronco).
    if arremesso:
        braco(t, ot, (ot[0] - 7, ot[1] - 7), (ot[0] - 6, ot[1] - 17), atras=True)
    elif facada:
        if nome == "facada1":
            braco(t, ot, (ot[0] - 7, ot[1] - 3), (ot[0] - 4, ot[1] - 11), atras=True)
    elif not um:
        braco(t, ot, _desloca(pose["cot_tras"], dy), (gx, gy), atras=True)
    elif pose.get("puxa"):
        pxa, pya = puxa_baladeira(nome, pose)
        braco(t, ot, (ot[0] + 1, ot[1] + 5), (pxa, pya + dy), atras=True)
    tronco(t, dy)
    if pose.get("costas"):
        t.linha(BX - 4, TOPO + dy + 1, BX + 4, BASE + dy - 4, "fuba_1")  # alça da lata
    _perna_frente(t, frente, q)
    sobe = 2 if rosto == "suor" else 0
    cabeca(t, hx, hy, rosto, chapeu_sobe=sobe)
    if rosto == "suor":
        # Ajeitando o chapéu: mão na aba.
        pass
    # Arma e braço da frente.
    apoio, boca = colar_arma(t, arma, (gx, gy), None, pose.get("recorte"))
    if arremesso or facada or um:
        braco(t, of, _desloca(pose.get("cot_frente", (20, 41)), dy), (gx, gy))
        maos.append((gx, gy, False))
    else:
        braco(t, of, _desloca(pose["cot_frente"], dy), apoio)
        maos += [(gx, gy, True), (apoio[0], apoio[1], False)]
    if arremesso:
        maos.append((ot[0] - 6, ot[1] - 17, True))
    if nome == "facada1":
        fx, fy = ot[0] - 4, ot[1] - 11
        for k in range(9):  # peixeira de pé, pronta para descer
            x, y = fx + 1 + k // 4, fy - 2 - k
            t.ponto(x, y, "pelo_7" if k < 6 else "pelo_5")
            t.ponto(x + 1, y, "pelo_4")
        maos.append((fx, fy, True))
    elif nome == "facada":
        fx, fy = 29, 40 + dy
        braco(t, (of[0] - 2, of[1]), (22, 42 + dy), (fx, fy))
        for k in range(12):  # golpe: peixeira comprida na horizontal
            x, y = fx + 2 + k, fy + k // 6
            t.ponto(x, y, "pelo_7" if k < 9 else "pelo_5")
            t.ponto(x, y + 1, "pelo_4" if k < 10 else "pelo_2")
        maos.append((fx, fy, False))
    if pose.get("puxa") and not arremesso and not facada:
        pxa, pya = puxa_baladeira(nome, pose)
        (l1x, l1y), (l2x, l2y) = ar.LIGA
        ox, oy = gx - ar.ANCORAS[arma][0][0], gy - ar.ANCORAS[arma][0][1]
        if nome == "atirando":
            t.linha(ox + l1x, oy + l1y, ox + l2x, oy + l2y, "rubro_3")
        else:
            for tx, ty in ((ox + l1x, oy + l1y), (ox + l2x, oy + l2y)):
                t.linha(pxa, pya + dy, tx, ty, "rubro_3")
        maos.append((pxa, pya + dy, True))
    for mx, my, atras in maos:
        punho_fechado(t, mx, my, atras)
    if bocas is not None:
        chave = "agachado" if nome == "agachado" else ("frente" if nome == "parado" else None)
        if chave:
            bocas[chave] = [boca[0] - PE[0], PE[1] - boca[1]]
    return _fim(t)


def puxa_baladeira(nome, pose):
    px_, py_ = pose["puxa"]
    if nome == "recarga":
        return px_, py_
    if nome == "atirando":
        return px_ - 2, py_ + 2
    return pose["punho"][0] - 7, pose["punho"][1] + 9


def _fim(t):
    t.contorno("negro_1")
    return t


def quadro_morte(nome):
    """morte1: voa para trás de braços para cima, careta de dor, sem o chapéu (voa à parte).
    morte2/morte3: estatelado de costas no chão, olhos em X (no 3 com a língua de fora)."""
    t = Tela(W, H)
    if nome == "morte1":
        frente, dy, q = _pernas(t, "pulo")
        of, ot = OMBRO_F, OMBRO_T
        braco(t, ot, (ot[0] - 5, ot[1] - 6), (ot[0] - 6, ot[1] - 13), atras=True)
        tronco(t, 0)
        _perna_frente(t, frente, q)
        cabeca(t, CABECA[0], CABECA[1], "dor", com_chapeu=False)
        braco(t, of, (of[0] + 6, of[1] - 6), (of[0] + 10, of[1] - 12))
        punho_fechado(t, ot[0] - 6, ot[1] - 13, True)
        punho_fechado(t, of[0] + 10, of[1] - 12)
        return _fim(t)
    # Desenhado em pé (pernas esticadas, braços para trás da cabeça) e girado 90 graus:
    # as costas ficam retas no chão e as alpercatas apontam para o céu.
    g = Tela(W, H)
    q = QUADRIL
    perna(g, (BX - 1, q), (BX - 2, q + 14), atras=True)
    of, ot = OMBRO_F, OMBRO_T
    braco(g, ot, (ot[0] - 3, ot[1] - 7), (ot[0] - 3, ot[1] - 15), atras=True)
    tronco(g, 0)
    perna(g, (BX + 2, q), (BX + 4, q + 14) if nome == "morte2" else (BX + 8, q + 9))
    cabeca(g, CABECA[0], CABECA[1], nome, com_chapeu=False)
    braco(g, of, (of[0] + 3, of[1] - 7), (of[0] + 4, of[1] - 15))
    punho_fechado(g, ot[0] - 3, ot[1] - 15, True)
    punho_fechado(g, of[0] + 4, of[1] - 15)
    rot = np.rot90(g.px, 1)  # anti-horário: a cabeça vai para a esquerda, as costas para baixo
    ys, xs = np.where(rot != VAZIO)
    desce = (CHAO - 1) - ys.max()
    esq = (W - (xs.max() - xs.min() + 1)) // 2 - xs.min()
    for y, x in zip(ys, xs):
        ny, nx = y + desce, x + esq
        if 0 <= ny < H and 0 <= nx < W:
            t.px[ny, nx] = rot[y, x]
    return _fim(t)


def folha_da_arma(arma, bocas=None):
    return [quadro(n, arma, bocas) for n in QUADROS]


def gravar_bocas(caminho):
    """Gera src/maos.js: de onde sai o tiro de cada arma, em relação ao pé."""
    linhas = ["// Gerado por tools/arte/lampiao_ms.py (exportar.py). Não editar à mão.",
              "// Boca do cano de cada arma pesada nas mãos do Lampião, em relação ao pé",
              "// (x para a frente, y para cima), em pé, agachado e mirando para cima.",
              "export const BOCAS = {"]
    for arma in ar.ANCORAS:
        b = {}
        for n in ("parado", "agachado", "mira_cima", "mira_baixo"):
            quadro(n, arma, b)
        linhas.append(f"  {arma}: {{ frente: {b['frente']}, agachado: {b['agachado']}, cima: {b['cima']}, "
                      f"baixo: {b['baixo']} }},")
    linhas.append("};")
    Path(caminho).write_text("\n".join(linhas) + "\n")


def chapeu_solto():
    """Chapéu sozinho (voa da cabeça quando ele morre)."""
    t = Tela(26, 12)
    chapeu(t, 13, 14)
    t.contorno("negro_1")
    ys, xs = np.where(t.px != VAZIO)
    s = Tela(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
    s.px = t.px[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    return s


if __name__ == "__main__":
    from PIL import Image
    nomes = sys.argv[1:] or ["parado", "atirando", "corre1", "corre3", "pulo", "agachado", "mira_cima", "morte2"]
    arma = "pistola"
    qs = [quadro(n, arma) for n in nomes]
    img = Image.new("RGBA", (W * len(qs), H), (120, 170, 210, 255))
    for k, q in enumerate(qs):
        img.alpha_composite(q.imagem(), (k * W, 0))
    img.resize((img.width * 3, img.height * 3), Image.NEAREST).save("/tmp/claude-0/s/lamp.png")
