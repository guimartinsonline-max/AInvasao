"""Trecho 3 da fase 1 (vila alta) no jeito do Metal Slug (ESTILO.md, Cenários).

Continua a pintura da vila de taipa (`vila_ms`) sem emenda: chão, morros, chapada e o
plano de trás são a mesma pintura, só que vão até o fim da vila alta, e por cima entram
as peças dela: o casario de platibanda colado (cada sobrado é uma plataforma: o topo da
platibanda é onde se anda), os toldos da bodega, a casinha baixa no fim, a igreja matriz
e os telhados de trás.

Mesmas regras: sem contorno, cor de ambiente da tarde (rampas `amb_*`; a tinta das
fachadas é desbotada e puxada para essa luz, rampas `azul` e `rosa`), formas grandes com
textura dentro (reboco caído mostrando o adobe, vãos fundos, cornija com sombra), luz da
esquerda. A emenda com o estilo antigo fica fora da tela enquanto a câmera está na vila
alta (até CAMERA_FIM) e só aparece quando se entra no campo de pouso.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

import caatinga_ms as cm
import vila_ms as vm
from caatinga_ms import Quadro, ambientar, fbm, nevoa, quantiza_limpo, ruido
from base_detalhe import ACENTOS, FONTE5

ALTA_INI = vm.VILA_FIM          # 3880
ALTA_FIM = 4860                 # x do mundo onde começa o campo de pouso
TELA_W = cm.TELA_W
CAMERA_FIM = ALTA_FIM - TELA_W


def limite(fator):
    """x da camada até onde vai o jeito novo (caatinga + vila + vila alta)."""
    return int(CAMERA_FIM * fator + TELA_W)


def antigo(x, fator):
    """A peça antiga nessa posição da camada continua (fica depois da vila alta)."""
    return x >= limite(fator)


# ---------------------------------------------------------------- tinta e letreiro
# Cor de cada fachada -> (rampa, faixa da rampa usada). A tinta é desbotada: nada de cor viva.
TINTA = {"azul": ("azul", 0.25, 1.0), "rosa": ("rosa", 0.25, 1.0), "ocre": ("terra", 0.5, 1.0),
         "verde": ("verde", 0.35, 0.86), "cal": ("cal", 0.0, 1.0)}
# Cor das portas e janelas de cada fachada (contraste com a parede, também desbotado).
ESQUADRIA = {"azul": "madeira", "rosa": "verde", "ocre": "azul", "verde": "madeira", "cal": "azul"}


NOMES = ["FARMÁCIA", "BARBEARIA", "ARMAZÉM", "CORREIO", "PADARIA", "ALFAIATE", "BODEGA"]


def tinta(q, m, cor, luz):
    r, a, b = TINTA[cor]
    q.pinta(m, r, a + (b - a) * np.clip(luz, 0, 0.999))


def texto(t):
    """Máscara das letras 5x7 (com acento nas 2 linhas de cima)."""
    w = len(t) * 6 - 1
    m = np.zeros((10, w), bool)
    for k, ch in enumerate(t):
        base, ac = ACENTOS.get(ch, (ch, None))
        g = FONTE5.get(base, FONTE5[" "])
        x = k * 6
        for j, linha in enumerate(g):
            for i, b in enumerate(linha):
                if b == "1":
                    m[j + 2, x + i] = True
        if ac == "agudo":
            m[1, x + 2] = m[0, x + 3] = True
        elif ac == "til":
            m[1, x + 1] = m[0, x + 2] = m[1, x + 3] = m[0, x + 4] = True
    return m


# ---------------------------------------------------------------- vãos fundos (porta e janela)
def vao(q, x0, y0, w, h, tipo, rampa, sem, aberta=False, arco=False):
    """Porta ou janela num vão fundo de parede grossa: ombreira e verga de cal em relevo,
    sombra da verga e da ombreira esquerda dentro do vão (luz de cima à esquerda), soleira
    ou peitoril aceso. Porta: duas folhas de tábua almofadada, uma às vezes entreaberta
    mostrando o escuro. Janela: duas folhas de veneziana, uma meio aberta."""
    X, Y = q.xx, q.yy
    rng = np.random.default_rng(sem)
    x1, y1 = x0 + w, y0 + h
    ra = w / 2
    dentro = (X >= x0) & (X < x1) & (Y >= y0) & (Y < y1)
    if arco:
        cx = x0 + ra
        dentro &= (Y >= y0 + ra) | (np.hypot(X + 0.5 - cx, Y + 0.5 - (y0 + ra)) < ra)
    # moldura de cal em relevo (2 px), acesa em cima e à esquerda, sombra embaixo à direita
    mold = ndimage.binary_dilation(dentro, np.ones((5, 5))) & ~dentro & (Y < y1 + (2 if tipo == "janela" else 0))
    q.pinta(mold, "cal", np.where((X < x0) | (Y < y0 + 1), 0.95, np.where(X >= x1, 0.5, 0.8)))
    # fundo do vão (o que fica atrás das folhas): escuro
    q.pinta(dentro, "madeira", np.full(q.a.shape, 0.02))
    # folhas
    folha = dentro & ~((X < x0 + 2) | (Y < y0 + (3 if not arco else 0)))       # recuo: sombra em cima e à esq.
    meio = x0 + w // 2
    if tipo == "porta":
        u = (X - x0) % 5
        lz = 0.55 + 0.12 * (u == 1) - 0.22 * (u == 4)
        alm = ((Y - y0) % 16 >= 3) & ((Y - y0) % 16 < 13) & (np.abs(X + 0.5 - (x0 + w * 0.25)) < w * 0.15) | \
              ((Y - y0) % 16 >= 3) & ((Y - y0) % 16 < 13) & (np.abs(X + 0.5 - (x0 + w * 0.75)) < w * 0.15)
        lz = np.where(alm, lz - 0.12, lz)
        lz = np.where(np.abs(X + 0.5 - meio) < 1, 0.05, lz)
        if aberta:                                 # a folha da direita entreaberta: o escuro aparece
            folha &= ~((X >= meio) & (X < meio + w // 4))
        lz = np.where(X >= meio, lz - 0.12, lz)
        q.pinta(folha, rampa, quantiza_limpo(np.clip(lz, 0, 0.999), 6))
        # ferrolho e dobradiças
        q.pinta((np.abs(X + 0.5 - (meio - 2)) < 1) & (np.abs(Y - (y0 + h * 0.55)) < 1.5), "madeira", np.full(q.a.shape, 0.1))
        # soleira acesa
        q.pinta((X >= x0 - 2) & (X < x1 + 2) & (Y >= y1 - 2) & (Y < y1), "cal", np.where(Y == y1 - 2, 0.95, 0.55))
    else:
        rip = (Y - y0) % 3
        lz = 0.6 + 0.2 * (rip == 0) - 0.25 * (rip == 2)
        lz = np.where(X >= meio, lz - 0.14, lz)
        if aberta:                                 # folha da esquerda aberta para fora, de lado
            fx = (X >= x0 - w // 3 - 2) & (X < x0 - 2) & (Y >= y0 + 1 - (X - x0) * 0.3) & (Y < y1 + 1 + (X - x0) * 0.3)
            q.pinta(fx, rampa, np.clip(0.75 + 0.15 * (rip == 0) - 0.2 * (rip == 2), 0, 0.999))
            folha &= X >= meio
            q.pinta(dentro & (X < meio) & (Y > y0 + h * 0.55), "madeira", np.full(q.a.shape, 0.22))  # parapeito lá dentro
        q.pinta(folha, rampa, quantiza_limpo(np.clip(lz, 0, 0.999), 6))
        q.pinta(dentro & (np.abs(X + 0.5 - meio) < 0.6), "madeira", np.full(q.a.shape, 0.05))
        # peitoril saliente: aceso em cima, sombra embaixo
        pe = (X >= x0 - 3) & (X < x1 + 3) & (Y >= y1 + 2) & (Y < y1 + 5)
        q.pinta(pe, "cal", np.where(Y == y1 + 2, 0.99, np.where(Y == y1 + 4, 0.35, 0.7)))
    # sombra da verga sobre a folha (2 px) e da ombreira esquerda
    q.pinta(dentro & (Y >= y0) & (Y < y0 + 3) & ~(X < x0), "madeira", np.full(q.a.shape, 0.08))
    q.pinta(dentro & (X < x0 + 2), "madeira", np.full(q.a.shape, 0.05))
    # verga: lintel de cal com pedra de fecho
    if not arco:
        vg = (X >= x0 - 4) & (X < x1 + 4) & (Y >= y0 - 5) & (Y < y0 - 1)
        q.pinta(vg, "cal", np.where(Y == y0 - 5, 0.99, np.where(Y == y0 - 2, 0.4, 0.82)))
        fe = (np.abs(X + 0.5 - (x0 + w / 2)) < 3 - (Y - (y0 - 7)) * 0.2) & (Y >= y0 - 7) & (Y < y0 - 1)
        q.pinta(fe, "cal", np.where(X + 0.5 < x0 + w / 2, 0.99, 0.6))


# ---------------------------------------------------------------- sobrado de platibanda
P = 14   # altura da platibanda: o topo dela é onde se anda


def sobrado(w, h, cor="azul", sem=0, sacada=False, letreiro=None):
    """Casa de platibanda do sertão, do tamanho exato do sólido (w x h): platibanda com
    cornija saliente e almofadas fundas, sombra da cornija na parede, reboco pintado e
    desbotado (a cal aparece por baixo), reboco caído mostrando o adobe, barrado de barro,
    vãos fundos com verga e peitoril, letreiro pintado, bica com escorrido, lampião de
    parede, rachaduras e marcas de bala. Sacada de ferro no sobrado alto."""
    q = Quadro(w, h)
    X, Y = q.xx, q.yy
    rng = np.random.default_rng(sem)
    rz = lambda e, s_: ruido(h, w, e, sem * 37 + s_)  # noqa: E731
    esq = ESQUADRIA[cor]
    parede = Y >= P
    # luz da parede: clara à esquerda, cai para a direita e para baixo, poeira subindo do chão
    luz = 0.80 - 0.16 * X / w - 0.10 * np.clip((Y - P) / (h - P), 0, 1) + 0.03 * rz(10, 1)
    luz -= 0.22 * np.clip((Y - (h - 26)) / 26, 0, 1)
    # reboco feito à mão: manchas miúdas de tom (não liso)
    luz += 0.07 * np.sign(fbm(h, w, sem + 21, escalas=(2.5, 1.2), pesos=(0.6, 0.4))) * (np.abs(fbm(h, w, sem + 21, escalas=(2.5, 1.2), pesos=(0.6, 0.4))) > 0.35)
    # tinta gasta: manchas grandes mais claras (a cal de baixo aparecendo)
    gasta = (fbm(h, w, sem + 3, escalas=(7, 3), pesos=(0.7, 0.3)) > 0.55) & parede
    gasta = ndimage.binary_opening(gasta, np.ones((2, 2)))
    luz = np.where(gasta, luz + 0.14, luz)
    # escorridos de chuva descendo da cornija
    esc = (ruido(1, w, 1.0, sem + 4)[0] > 1.25)[None, :] & (Y > P + 3) & (Y < P + 14 + 16 * rz(6, 5))
    luz = np.where(esc, luz - 0.13, luz)
    tinta(q, parede, cor, quantiza_limpo(np.clip(luz, 0, 0.999), 6))
    if cor != "cal":                               # onde a tinta saiu de vez: a cal por baixo
        cal = gasta & (fbm(h, w, sem + 9, escalas=(4, 2), pesos=(0.7, 0.3)) > 0.9)
        q.pinta(cal, "cal", np.clip(0.75 - 0.2 * X / w, 0, 0.999))
    # barrado de barro embaixo, com respingo
    bar = parede & (Y >= h - 13 + np.round(0.8 * rz((1, 4), 6)))
    q.pinta(bar, "terra", quantiza_limpo(np.clip(0.50 - 0.12 * X / w - 0.18 * (Y >= h - 4) + 0.04 * rz(2, 7), 0, 0.999), 5))
    q.pinta(parede & (Y == h - 14), "terra", np.full((h, w), 0.32))
    # reboco caído mostrando o adobe (borda de cima e da esquerda faz sombra no tijolo)
    caido = (fbm(h, w, sem + 11) > 0.85) & parede & (Y > P + 8) & (Y < h - 16)
    caido = ndimage.binary_opening(caido, np.ones((3, 3)))
    rot, n_ = ndimage.label(caido)                  # mancha pequena solta parece defeito: só as grandes
    if n_:
        tam = ndimage.sum(caido, rot, range(1, n_ + 1))
        caido = np.isin(rot, 1 + np.where(tam >= 60)[0])
    junta = ((Y % 5) == 0) | (((X + 4 * ((Y // 5) % 2)) % 9) == 0)
    lz = np.where(junta, 0.22, 0.58 - 0.1 * X / w + 0.12 * ((Y % 5) == 1))
    q.pinta(caido, "terra", lz)
    borda = caido & ~(np.roll(caido, 2, 0) & np.roll(caido, 2, 1))
    q.pinta(borda, "terra", np.full((h, w), 0.2))
    aro = ndimage.binary_dilation(caido, np.ones((3, 3))) & ~caido & parede
    q.pinta(aro & (np.roll(caido, -1, 0) | np.roll(caido, -1, 1)), "cal", np.full((h, w), 0.92))
    # vãos: portas embaixo, janelas entre elas; no sobrado alto, janelas em cima
    n = max(2, int(w // 34))
    passo = w / n
    portas = []
    hp = min(48, h - P - 24)
    alto = h >= 108                                # sobrado de dois andares
    for k in range(n):
        cx = passo * (k + 0.5)
        if k % 2 == 0:
            pw = 18
            vao(q, int(cx - pw / 2), h - hp - 1, pw, hp, "porta", esq, sem + k, aberta=rng.random() < 0.4,
                arco=(cor == "cal"))
            portas.append(cx)
        else:
            vao(q, int(cx - 7), h - 44, 14, 18, "janela", esq, sem + k, aberta=rng.random() < 0.5)
        if alto:
            vao(q, int(cx - 6), P + 10, 12, 18, "janela", esq, sem + 20 + k, aberta=rng.random() < 0.3)
    # sacada de ferro batido no sobrado alto, na frente das janelas de cima
    if sacada:
        sy = P + 33
        q.pinta((X >= 4) & (X < w - 4) & (Y >= sy) & (Y < sy + 3), "cal", np.where(Y == sy, 0.99, np.where(Y == sy + 2, 0.3, 0.7)))
        grade = (X >= 6) & (X < w - 6) & (Y >= sy - 10) & (Y < sy) & (((X % 3) == 0) | (Y == sy - 10) | (Y == sy - 9))
        voluta = (X >= 6) & (X < w - 6) & (Y >= sy - 7) & (Y < sy - 3) & ((X % 6) == 1) & ((Y % 2) == 0)
        q.pinta(grade | voluta, "madeira", np.where(Y == sy - 10, 0.45, 0.12))
        for x in range(10, w - 8, 14):                # mãos-francesas embaixo
            mf = (np.abs(X - (x + (Y - sy - 3) * 0.6)) < 0.8) & (Y >= sy + 3) & (Y < sy + 8)
            q.pinta(mf, "madeira", np.full((h, w), 0.12))
    # letreiro pintado acima da 1ª porta (tinta descascando), sem contorno
    if letreiro and portas and not alto:
        m = texto(letreiro)
        lw, lh = m.shape[1], m.shape[0]
        ly = P + 6
        lx = int(np.clip(portas[0] - lw / 2, 8, w - lw - 8))
        if lx + lw < w - 2:
            faixa = (X >= lx - 3) & (X < lx + lw + 3) & (Y >= ly - 1) & (Y < ly + lh + 1)
            fundo = "cal" if cor != "cal" else "azul"
            q.pinta(faixa, fundo, np.full((h, w), 0.78 if fundo == "cal" else 0.45) - 0.12 * (X > lx + lw * 0.6))
            letra = np.zeros((h, w), bool)
            letra[ly:ly + lh, lx:lx + lw] = m
            sombra = np.roll(np.roll(letra, 1, 0), 1, 1) & faixa & ~letra
            q.pinta(sombra, fundo, np.full((h, w), 0.25 if fundo == "cal" else 0.1))
            q.pinta(letra, "telha" if cor != "cal" else "cal", np.full((h, w), 0.35 if cor != "cal" else 0.95))
    # platibanda: cornija saliente em cima e embaixo, almofadas fundas no meio
    plat = Y < P
    lz = 0.86 - 0.16 * X / w + 0.02 * rz(8, 13)
    tinta(q, plat, cor, quantiza_limpo(np.clip(lz, 0, 0.999), 6))
    q.pinta(plat & (Y < 2), "cal", np.where(Y == 0, 0.99, 0.62))                 # capa de cima
    q.pinta(plat & (Y == 2), "cal", np.full((h, w), 0.3))
    q.pinta(plat & (Y >= P - 4) & (Y < P - 2), "cal", np.where(Y == P - 4, 0.95, 0.72))   # cornija
    q.pinta(plat & (Y >= P - 2), "madeira", np.where(Y == P - 2, 0.45, 0.25))
    na = max(2, w // 28)
    for k in range(na):
        ax0 = 5 + k * (w - 10) / na
        ax1 = ax0 + (w - 10) / na - 5
        alm = (X >= ax0) & (X < ax1) & (Y >= 4) & (Y < P - 5)
        if letreiro and alto and 0 < k < na - 1:
            continue
        sb = alm & ((Y == 4) | (X < ax0 + 1))                                      # funda: sombra em cima e à esq.
        lu = alm & ((Y == P - 6) | (X >= ax1 - 1))
        tinta(q, alm, cor, np.full((h, w), 0.55))
        tinta(q, sb, cor, np.full((h, w), 0.2))
        tinta(q, lu, cor, np.full((h, w), 0.95))
    # cunhais nas quinas: pilastra um tom acima da parede, quina acesa à esquerda, sombra à direita
    for px in (0, w - 6):
        cun = (X >= px) & (X < px + 6) & (Y >= P) & (Y < h - 13)
        lz = np.where(X == px, 0.99, np.where(X == px + 5, 0.35, 0.9 - 0.12 * (px > 0)))
        tinta(q, cun, cor, lz)
        q.pinta((X >= px - 1) & (X < px + 7) & (Y >= h - 16) & (Y < h - 13), "cal", np.where(Y == h - 16, 0.95, 0.5))
    # sobrado alto: o nome vai pintado na platibanda, no lugar das almofadas do meio
    if letreiro and alto:
        m = texto(letreiro)
        lw, lh = m.shape[1], m.shape[0]
        lx = (w - lw) // 2
        fx = (X >= lx - 4) & (X < lx + lw + 4) & (Y >= 2) & (Y < P - 3)
        tinta(q, fx, cor, np.where(Y == 2, 0.25, 0.75))
        letra = np.zeros((h, w), bool)
        letra[1:1 + lh, lx:lx + lw] = m
        letra &= fx
        q.pinta(np.roll(np.roll(letra, 1, 0), 1, 1) & fx & ~letra, "madeira", np.full((h, w), 0.3))
        q.pinta(letra, "telha", np.full((h, w), 0.3))
    # sombra da cornija na parede (dura, de cima à esquerda)
    som = parede & (Y < P + 4 - (X > w - 3)) & q.a
    q.img[som] = cm.escurecer(q.img[som], 2)
    # bica de água (gárgula de telha) e o escorrido escuro descendo
    bx = int(rng.uniform(10, w - 12))
    q.pinta((X >= bx) & (X < bx + 5) & (Y >= P - 2) & (Y < P + 1), "telha", np.where(Y == P - 2, 0.8, 0.4))
    escorre = (np.abs(X - (bx + 3 + 0.6 * np.sin(Y / 4.0))) < 1.2) & (Y > P + 1) & (Y < P + 10 + int(rng.integers(14, 34)))
    q.img[escorre & parede] = cm.escurecer(q.img[escorre & parede], 1)
    # lampião de parede num braço de ferro, entre a 1ª porta e a janela
    # (do lado da 1ª porta, na altura da verga: longe do letreiro e da janela)
    lx_ = int(portas[0] + 12) if portas else w
    if lx_ + 9 < w - 6:
        ly_ = h - hp + 4
        q.pinta((Y == ly_ - 2 + (X - lx_) // 3) & (X >= lx_) & (X < lx_ + 6), "madeira", np.full((h, w), 0.1))
        lamp = (X >= lx_ + 4) & (X < lx_ + 8) & (Y >= ly_) & (Y < ly_ + 6)
        q.pinta(lamp, "cal", np.where(X == lx_ + 4, 0.95, 0.6))
        q.pinta((X >= lx_ + 3) & (X < lx_ + 9) & ((Y == ly_ - 1) | (Y == ly_ + 6)), "madeira", np.full((h, w), 0.12))
    # rachaduras e marcas de bala (a vila está em guerra)
    for _ in range(3):
        x, y = rng.uniform(6, w - 6), rng.uniform(P + 6, h - 24)
        for _k in range(int(rng.integers(8, 16))):
            x += rng.uniform(-1.2, 1.2); y += 1
            if 0 <= int(y) < h and 0 <= int(x) < w and parede[int(y), int(x)]:
                q.img[int(y), int(x)] = cm.escurecer(q.img[int(y), int(x)][None], 2)[0]
    for _ in range(int(rng.integers(3, 7))):
        bx_, by_ = int(rng.uniform(4, w - 5)), int(rng.uniform(P + 6, h - 16))
        q.pinta((X >= bx_) & (X < bx_ + 2) & (Y >= by_) & (Y < by_ + 2), "madeira", np.where((X == bx_) & (Y == by_), 0.0, 0.18))
        q.pinta((X == bx_ + 2) & (Y == by_ + 2), "cal", np.full((h, w), 0.95))
    # sombra de baixo para cima no pé (o chão escurece a parede)
    pe = parede & (Y >= h - 2)
    q.img[pe] = cm.escurecer(q.img[pe], 1)
    q.a[:] = True
    return q


# ---------------------------------------------------------------- toldo, muro do beco, matriz
def toldo(w=60, alt=40, sem=0):
    """Toldo de lona listrada da bodega: o topo (y 0..3) é plataforma. Lona esticada com
    caimento e dobras, listras de telha e cru desbotadas na luz da tarde, bambinela
    recortada, varas de pau roliço e, embaixo, o caixote de frutas e os potes."""
    q = Quadro(w, alt)
    X, Y = q.xx, q.yy
    cai = 4 + 3 * X / w                                  # a lona cai para a frente (direita mais baixa)
    lona = (Y < 4 + cai) & (X < w)
    lista = ((X // 6) % 2) == 0
    lz = 0.85 - 0.5 * Y / (4 + cai) + 0.12 * np.sin(X / 2.2) - 0.1 * X / w
    q.pinta(lona & lista, "telha", quantiza_limpo(np.clip(lz, 0, 0.999), 5))
    q.pinta(lona & ~lista, "cal", quantiza_limpo(np.clip(lz + 0.05, 0, 0.999), 5))
    q.pinta(lona & (Y == 0), "cal", np.full((alt, w), 0.95))
    # bambinela em gomos: cada gomo com luz em cima e sombra embaixo
    yb = 4 + cai
    gomo = (Y >= yb) & (np.hypot(((X % 6) - 2.5) / 3.0, (Y - yb) / 3.0) < 1)
    q.pinta(gomo & lista, "telha", np.where(Y - yb < 1, 0.6, 0.25))
    q.pinta(gomo & ~lista, "cal", np.where(Y - yb < 1, 0.7, 0.35))
    # varas roliças com amarração
    for vx in (2, w - 5):
        v = (X >= vx) & (X < vx + 3) & (Y >= 5) & (Y < alt)
        q.pinta(v, "madeira", np.where(X == vx, 0.75, np.where(X == vx + 2, 0.2, 0.5)))
        q.pinta((X >= vx - 1) & (X < vx + 4) & (Y >= 7) & (Y < 10), "cal", np.where(Y == 7, 0.7, 0.4))
    # caixote de frutas embaixo
    cx0, cy0 = w // 2 - 10, alt - 11
    cx_ = (X >= cx0) & (X < cx0 + 20) & (Y >= cy0) & (Y < alt)
    q.pinta(cx_, "madeira", np.where((Y - cy0) % 4 == 0, 0.75, np.where(X >= cx0 + 17, 0.3, 0.55)))
    for k in range(5):
        fr = np.hypot(X - (cx0 + 3 + k * 3.6), (Y - (cy0 - 1)) * 1.1) < 2.2
        q.pinta(fr, "telha" if k % 2 else "verde", np.where(X < cx0 + 2 + k * 3.6, 0.85, 0.5))
    return q


def muro_beco(w, h=46, sem=0):
    """Muro de taipa fechando o beco entre dois sobrados, recuado (meio tom abaixo), com um
    portão de tábuas, telhinha em cima e o barro aparecendo."""
    q = Quadro(w, h)
    X, Y = q.xx, q.yy
    rz = lambda e, s_: ruido(h, w, e, sem + s_)  # noqa: E731
    m = Y >= 5
    lz = 0.5 - 0.12 * X / w + 0.04 * rz(3, 1) - 0.15 * np.clip((Y - (h - 14)) / 14, 0, 1)
    q.pinta(m, "cal", quantiza_limpo(np.clip(lz, 0, 0.999), 5))
    caido = (fbm(h, w, sem + 3) > 0.9) & m & (Y > 10)
    q.pinta(caido, "terra", np.where((Y % 5) == 0, 0.22, 0.45))
    q.pinta(m & (Y >= h - 9), "terra", np.full((h, w), 0.35))
    tel = Y < 6
    u = X % 5 / 5.0
    q.pinta(tel, "telha", np.clip(0.2 + 0.45 * np.cos((u - 0.38) * np.pi) - 0.15 * (Y >= 4), 0, 0.999))
    q.pinta((Y >= 6) & (Y < 8), "cal", np.full((h, w), 0.2))
    pw = min(18, w - 10)
    px = (w - pw) // 2
    porta = (X >= px) & (X < px + pw) & (Y >= h - 34) & (Y < h)
    t = (X - px) % 4
    q.pinta(porta, "madeira", np.where(t == 3, 0.12, np.where(t == 0, 0.5, 0.36)) - 0.1 * ((Y - (h - 34)) % 13 == 0))
    q.pinta((X >= px - 2) & (X < px + pw + 2) & (Y >= h - 37) & (Y < h - 34), "madeira", np.where(Y == h - 37, 0.55, 0.25))
    return q


def matriz(sem=9):
    """Igreja matriz no plano de trás: nave com frontão de volutas, óculo, porta em arco,
    e duas torres com o vão do sino, cornijas e coruchéu de telha. Pintada grande, com
    as mesmas regras (luz da esquerda, torre da direita com a face lateral na sombra)."""
    W, H = 176, 158
    q = Quadro(W, H)
    X, Y = q.xx, q.yy
    rz = lambda e, s_: ruido(H, W, e, sem * 13 + s_)  # noqa: E731
    tw = 32
    t0, t1 = 10, W - 10 - tw - 8                       # x das torres
    n0, n1 = t0 + tw, t1                               # nave entre elas
    yn = 62                                            # cornija da nave
    cx = (n0 + n1) / 2
    # nave e frontão
    d = np.abs(X + 0.5 - cx)
    meia = (n1 - n0) / 2
    topo = np.where(d < 10, 30.0, 30 + (yn - 34) * np.clip((d - 10) / (meia - 10), 0, 1) ** 0.7)
    nave = (X >= n0) & (X < n1) & (Y >= topo) & (Y < H)
    lz = 0.8 - 0.1 * (X - n0) / (n1 - n0) + 0.03 * rz(10, 1) - 0.2 * np.clip((Y - (H - 24)) / 24, 0, 1)
    q.pinta(nave, "cal", quantiza_limpo(np.clip(lz, 0, 0.999), 6))
    q.pinta(nave & ~np.roll(nave, 2, 0), "cal", np.full((H, W), 0.99))
    q.pinta((X >= n0) & (X < n1) & (Y >= yn) & (Y < yn + 3), "cal", np.where(Y == yn, 0.99, np.where(Y == yn + 2, 0.3, 0.7)))
    # óculo e porta em arco
    oc = np.hypot(X + 0.5 - cx, Y - 46) < 6
    q.pinta(oc, "madeira", np.where(X + 0.5 < cx, 0.05, 0.2))
    q.pinta((np.hypot(X + 0.5 - cx, Y - 46) < 8) & ~oc & nave, "cal", np.where(Y < 46, 0.99, 0.55))
    pw, ph = 24, 48
    pa = (np.abs(X + 0.5 - cx) < pw / 2) & ((Y >= H - ph + pw / 2) | (np.hypot(X + 0.5 - cx, Y - (H - ph + pw / 2)) < pw / 2)) & (Y < H - 2)
    tb = (X - int(cx - pw / 2)) % 5
    q.pinta(pa, "madeira", np.clip(0.42 + 0.12 * (tb == 1) - 0.2 * (tb == 4) - 0.15 * (X > cx), 0, 0.999))
    q.pinta(ndimage.binary_dilation(pa, np.ones((5, 5))) & ~pa & nave, "cal", np.where(X < cx, 0.95, 0.55))
    for jx in (cx - 22, cx + 22):
        ja = (np.abs(X + 0.5 - jx) < 4) & ((Y >= yn + 16) | (np.hypot(X + 0.5 - jx, Y - (yn + 16)) < 4)) & (Y < yn + 30)
        q.pinta(ja, "madeira", np.full((H, W), 0.12))
        q.pinta(ndimage.binary_dilation(ja, np.ones((3, 3))) & ~ja & nave, "cal", np.where(X < jx, 0.95, 0.5))
    # torres
    for k, tx in enumerate((t0, t1)):
        lado = 8 if k == 1 else 0
        corpo = (X >= tx) & (X < tx + tw) & (Y >= 34) & (Y < H)
        lz = 0.84 - 0.1 * (X - tx) / tw + 0.03 * rz(8, 2 + k) - 0.2 * np.clip((Y - (H - 24)) / 24, 0, 1)
        q.pinta(corpo, "cal", quantiza_limpo(np.clip(lz - 0.04 * k, 0, 0.999), 6))
        if lado:
            q.pinta((X >= tx + tw) & (X < tx + tw + lado) & (Y >= 36) & (Y < H), "cal",
                    quantiza_limpo(np.clip(0.3 + 0.04 * rz(3, 9), 0, 0.999), 4))
        for yc_ in (34, yn, 104):                          # cornijas
            q.pinta((X >= tx - 2) & (X < tx + tw + 2 + lado) & (Y >= yc_ - 2) & (Y < yc_ + 2), "cal",
                    np.where(Y == yc_ - 2, 0.99, np.where(Y == yc_ + 1, 0.3, 0.7)))
        sx = tx + tw / 2
        vao_ = (np.abs(X + 0.5 - sx) < 7) & ((Y >= 44) | (np.hypot(X + 0.5 - sx, Y - 44) < 7)) & (Y < 58)
        q.pinta(vao_, "madeira", np.where(X + 0.5 < sx - 4, 0.02, 0.1))
        sino = (np.abs(X + 0.5 - sx) < 2 + (Y - 44) * 0.45) & (Y >= 44) & (Y < 53)
        q.pinta(sino, "terra", np.clip(0.75 - 0.5 * (X + 0.5 - sx + 4) / 9, 0, 0.999))
        q.pinta(ndimage.binary_dilation(vao_, np.ones((3, 3))) & ~vao_ & corpo, "cal", np.where(X < sx, 0.99, 0.5))
        rel = (np.abs(X + 0.5 - sx) < 5) & (np.hypot(X + 0.5 - sx, Y - 84) < 5)
        q.pinta(rel, "cal", np.where(X + 0.5 < sx, 0.4, 0.6))
        q.pinta((np.abs(X + 0.5 - sx) < 1) & (np.abs(Y - 84) < 1), "madeira", np.full((H, W), 0.1))
        # coruchéu de telha (pirâmide) com a face da direita na sombra, e a cruz
        cor = (np.abs(X + 0.5 - sx) < (tw / 2 + 1) * (Y - 6) / 26) & (Y >= 6) & (Y < 32)
        q.pinta(cor, "telha", np.where(X + 0.5 < sx, 0.65 - 0.2 * ((Y % 4) == 0), 0.3 - 0.1 * ((Y % 4) == 0)))
        cz = ((np.abs(X + 0.5 - sx) < 1) & (Y >= 0) & (Y < 8)) | ((np.abs(X + 0.5 - sx) < 3) & (Y == 2))
        q.pinta(cz, "madeira", np.full((H, W), 0.3))
    # cruz da nave
    cz = ((np.abs(X + 0.5 - cx) < 1) & (Y >= 18) & (Y < 31)) | ((np.abs(X + 0.5 - cx) < 4) & (Y == 22))
    q.pinta(cz, "madeira", np.full((H, W), 0.3))
    # barrado e escadaria
    q.pinta(q.a & (Y >= H - 10), "terra", np.full((H, W), 0.42) - 0.1 * (X > cx))
    for k in range(3):
        dg = (np.abs(X + 0.5 - cx) < 30 - k * 5) & (Y >= H - 3 * (k + 1)) & (Y < H - 3 * k)
        q.pinta(dg, "cal", np.where(Y == H - 3 * (k + 1), 0.85, 0.45))
    return q


# ---------------------------------------------------------------- camadas
def camada_paredao(h=130, ate=None):
    """`ate`: até onde a camada vai (o trecho seguinte estende a mesma pintura)."""
    return vm.camada_paredao(h, ate=ate or limite(0.2))


def camada_frente(h=44, ate=None):
    return vm.camada_frente(h, ate=ate or limite(1.1))


def camada_meio(h=124, ate=None):
    # 124 de altura (era 90): folga em cima para as casinhas e a torre da vila alta ao longe
    # não ficarem com o telhado cortado; a base continua no mesmo lugar.
    """Os morros continuam por planos; árvores ralas, um sítio com a casinha e a cerca."""
    fator = 0.45
    lim = limite(fator)
    q = vm.camada_meio(h, ate=ate or lim)
    rng = np.random.default_rng(41)
    x0 = vm.limite(fator) - 10
    topo = np.argmax(q.a, axis=0)
    for _ in range(18):
        cx = rng.uniform(x0, lim); r = rng.uniform(3, 6)
        cy = topo[int(cx)] + rng.uniform(3, 24)
        d = np.hypot(q.xx - cx, (q.yy - cy) * 1.4) / r
        q.pinta((d < 1) & (q.yy < cy + 2), "verde",
                np.clip((0.5 - 0.35 * (q.xx - cx) / r - 0.45 * (q.yy - cy) / r) * 0.5 + 0.2, 0, 0.999))
    x = x0 + 20.0
    while x < lim - 10:
        p = nevoa(cm.arvore(int(rng.uniform(34, 50)), sem=int(x) + 7, folhas=rng.random() > 0.3), 0.42)
        py = topo[int(min(x, q.w - 1))] + rng.uniform(2, 8) - p.h
        if py >= 0:                                  # nada cortado pelo alto da camada
            q.colar(p, x - p.w / 2, py)
        x += rng.uniform(60, 120)
    sx = int((x0 + lim) / 2)
    c = nevoa(cm.casinha_longe(46, 20, sem=33), 0.36)
    q.colar(c, sx, topo[sx + c.w // 2] + 6 - c.h)
    cv = nevoa(cm.cerca_varas(60, 14, sem=34), 0.36)
    q.colar(cv, sx + c.w + 4, topo[min(q.w - 1, sx + c.w + 30)] + 8 - cv.h)
    return q


def camada_perto(h=160, ate=None):
    """Plano de trás (0,75): atrás do casario, a igreja matriz com as duas torres, os
    telhados das casas de trás (só aparecem por cima da platibanda e nos becos) e árvores."""
    fator = 0.75
    lim = limite(fator)
    q = vm.camada_perto(h, ate=ate or lim)
    chao = h - 1
    rng = np.random.default_rng(52)
    x0 = vm.limite(fator)
    x = float(x0 - 10)
    while x < lim:
        p = cm.moita(int(rng.integers(30, 56)), int(rng.integers(14, 22)), sem=int(x) + 3, seca=rng.uniform(0.2, 0.7))
        q.colar(p, x, chao - p.h + 3)
        x += rng.integers(30, 64)
    lx = lambda wx: int(wx * fator)  # noqa: E731
    casa = lambda *a, **k: nevoa(cm.casa(*a, sombra_beiral=True, **k), 0.2)  # noqa: E731
    pecas = [
        (lx(3900), cm.arvore(150, sem=150, folhas=True)),
        (lx(3990), casa(110, 84, 40, sem=61, alpendre=False, lado=18, porta=(20, 20, 36), janela=(70, 14, 18))),
        (lx(4250), nevoa(matriz(), 0.12)),
        (lx(4150), cm.arvore(136, sem=151, folhas=False)),
        (lx(4500), casa(120, 88, 42, sem=62, alpendre=False, lado=20, porta=(80, 20, 36), janela=(20, 14, 18),
                        parede="terra")),
        (lx(4690), cm.arvore(146, sem=152, folhas=True)),
        (lx(4760), casa(100, 80, 38, sem=63, alpendre=False, lado=16, porta=(24, 20, 36), janela=(66, 14, 18))),
    ]
    for x, p in sorted(pecas, key=lambda e: -e[1].h):
        if x + p.w <= lim + 40:
            q.colar(p, x, chao - p.h + 2)
    return q


def camada_jogo(fase, alt=176, topo_mundo=40, ate=None):
    """Plano do jogo: a rua continua, o casario de platibanda (sólidos), muros nos becos,
    os toldos da bodega, a casinha baixa do fim e os objetos de rua na luz da cena."""
    import fase1 as f1
    CH = f1.CHAO
    q = vm.camada_jogo(fase, alt, topo_mundo, ate=ate or ALTA_FIM + 40)
    y = lambda wy: wy - topo_mundo  # noqa: E731
    yc = y(CH) - 1
    rng = np.random.default_rng(83)
    w = ALTA_FIM + 120
    # pedrinhas encaixadas na rua
    for _ in range(int((w - ALTA_INI) / 548 * 36)):
        px = rng.uniform(ALTA_INI - 40, w); py = rng.uniform(y(CH) + 3, alt + 2)
        rx = rng.uniform(2.5, 6) * (1 + (py - y(CH)) / 30); ry = rx * rng.uniform(0.45, 0.7)
        j0, j1 = int(max(0, py - ry - 3)), int(min(alt, py + ry + 4))
        i0, i1 = int(max(0, px - rx - 3)), int(min(q.w, px + rx + 4))
        if j1 <= j0 or i1 <= i0:
            continue
        sub = Quadro(i1 - i0, j1 - j0)
        sub.img[:] = q.img[j0:j1, i0:i1]; sub.a[:] = q.a[j0:j1, i0:i1]
        X, Y = sub.xx + i0, sub.yy + j0
        d = np.hypot((X - px) / rx, (Y - py) / ry) + 0.12 * ruido(sub.h, sub.w, 0.8, int(px))
        som = (np.hypot((X - px - 1.5) / rx, (Y - py - 1.5) / ry) < 1) & (Y > py) & sub.a
        sub.img[som] = cm.escurecer(sub.img[som], 1)
        sub.pinta(d < 1, "terra", np.clip(0.55 - 0.35 * (X - px) / rx - 0.5 * (Y - py) / ry, 0, 0.999))
        q.img[j0:j1, i0:i1] = sub.img
    casas = f1.VILA_ALTA
    # muros fechando os becos entre os sobrados (recuados, atrás)
    for (xa, wa, *_), (xb, *_r) in zip(casas, casas[1:]):
        if xb - (xa + wa) > 8:
            mu = muro_beco(xb - (xa + wa) + 4, 46, sem=xa)
            q.colar(mu, xa + wa - 2, yc - mu.h + 1)
    # casario
    for k, (x, w_, h_, cor, sac) in enumerate(casas):
        q.colar(sobrado(w_, h_, cor, sem=50 + k, sacada=sac, letreiro=NOMES[k]), x, y(CH) - h_)
        q.sombra(x + w_ / 2, yc + 1, w_ * 1.02, 3)
    # casinha baixa no fim (o topo do telhado é o degrau para descer)
    cx_, cw_, ch_ = f1.CASINHA_FIM
    cs = cm.casa(40, 30, 22, sem=88, alpendre=False, lado=10, porta=(12, 14, 24), janela=False, sombra_beiral=True)
    q.sombra(cx_ + cw_ / 2, yc + 1, cw_, 3)
    q.colar(cs, cx_, y(CH) - ch_)
    # capim no pé das paredes
    x = ALTA_INI - 20.0
    while x < ALTA_FIM:
        c = cm.capim(rng.uniform(4, 8), int(x) + 1, folhas=int(rng.integers(3, 6)))
        q.colar(c, x, yc - c.h + 2)
        x += rng.uniform(24, 60)
    # toldos da bodega (o topo é plataforma em y 152)
    for x, w_ in f1.TOLDOS:
        td = toldo(w_, CH - 152, sem=x)
        q.colar(td, x, y(152))
    # objetos de rua na luz da cena
    amb = lambda t: ambientar(t.imagem())  # noqa: E731
    q.assentar(amb(f1.sacos_detalhados(4, 3, 3)), 4290 - 3, yc, afundar=3)
    for x, peca in ((3884, f1.pote_barro(9)), (4110, f1.cabacas()), (4360, f1.pilao()), (4600, f1.pote_barro(10, 12)),
                    (4588, f1.roda_carroca(8)), (4470, f1.pote_barro(11)), (4482, f1.pote_barro(12, 10))):
        q.assentar(amb(peca), x, yc)
    for x in (4100, 4600):
        q.assentar(cm.xiquexique(int(rng.integers(22, 30)), int(rng.integers(16, 22)), sem=x), x, yc, afundar=2)
    # bandeirinhas de São João esticadas de platibanda em platibanda, caindo no meio
    pares = [(casas[k][0] + casas[k][1] - 8, CH - casas[k][2] + 3, casas[k + 1][0] + 8, CH - casas[k + 1][2] + 3)
             for k in (0, 1, 3, 5)]
    pares.append((casas[2][0] + 20, CH - casas[2][2] + 3, casas[3][0] + 30, CH - casas[3][2] + 3))
    cores = [("telha", 0.55), ("cal", 0.85), ("verde", 0.6), ("azul", 0.6), ("rosa", 0.65)]
    for k, (xa, ya, xb, yb) in enumerate(pares):
        n = int(abs(xb - xa))
        for i in range(n):
            t_ = i / max(1, n - 1)
            xx = xa + (xb - xa) * t_
            yy = y(ya + (yb - ya) * t_ + 12 * 4 * t_ * (1 - t_))
            q.img[int(yy), int(xx)] = cm.RGB["madeira"][1]; q.a[int(yy), int(xx)] = True
            if i % 7 == 3 and 3 < i < n - 4:
                rampa, lz = cores[(i // 7 + k) % len(cores)]
                for dy in range(1, 6):
                    for dx in range(-(3 - dy // 2), 4 - dy // 2):
                        yyy, xxx = int(yy) + dy, int(xx) + dx
                        q.img[yyy, xxx] = cm.RGB[rampa][int(np.clip((lz - 0.25 * (dx > 0)) * len(cm.RGB[rampa]), 0, len(cm.RGB[rampa]) - 1))]
                        q.a[yyy, xxx] = True
    if ate:                          # o trecho seguinte continua daqui e faz a passagem
        return q
    # a passagem para o campo de pouso: o chão novo some em manchas sobre o antigo
    # (só depois da casinha do fim: nenhuma peça da vila alta fica furada)
    ini = cx_ + cw_ + 4
    corte = np.clip((ALTA_FIM + 40 - q.xx) / (ALTA_FIM + 40 - ini), 0, 1) + 0.25 * ruido(alt, q.w, 3, 199)
    q.a &= (corte > 0.5) | (q.xx < ini)
    return q


if __name__ == "__main__":
    import sys
    import fase1 as f1
    out = sys.argv[1]
    pecas = [sobrado(w, h, c, sem=50 + k, sacada=s, letreiro=NOMES[k]) for k, (x, w, h, c, s) in enumerate(f1.VILA_ALTA)]
    W = sum(p.w + 4 for p in pecas)
    im = Image.new("RGBA", (W, 120), (0, 0, 0, 0))
    x = 0
    for p in pecas:
        im.paste(Image.fromarray(p.rgba(), "RGBA"), (x, 120 - p.h))
        x += p.w + 4
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(out)
