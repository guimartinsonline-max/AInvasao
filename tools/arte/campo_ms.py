"""Trecho 4 da fase 1 (campo de pouso) no jeito do Metal Slug (ESTILO.md, Cenários).

Continua a pintura da vila alta (`vila_alta_ms`) sem emenda: chão, morros, chapada e o
plano de trás são a mesma pintura, só que vão até o fim do campo de pouso, e por cima entram
as peças dele: o hangar de zinco da Aviação Militar (com o lado e o teto em arco recuando),
a pista com marca de pneu, balizas e pedras caiadas, o tanque de gasolina, a trincheira e a
cerca da guarda; atrás, a caixa d'água de madeira, o galpão, o mastro do rádio e a casinha
do telegrafista.

Mesmas regras: sem contorno, cor de ambiente da tarde (rampas `amb_*`; o zinco usa a rampa
`azul`, cinza puxado para o lilás da sombra), formas grandes com textura dentro (chapa
ondulada, ferrugem escorrendo, tábua, rebite), luz da esquerda. A emenda com o estilo antigo
fica fora da tela enquanto a câmera está no campo (até CAMERA_FIM) e só aparece quando se
entra no rio seco.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

import caatinga_ms as cm
import vila_alta_ms as va
from caatinga_ms import Quadro, ambientar, nevoa, quantiza_limpo, ruido
from base_detalhe import ACENTOS, FONTE5

CAMPO_INI = va.ALTA_FIM         # 4860
CAMPO_FIM = 5980                # x do mundo onde começa o leito do rio seco
TELA_W = cm.TELA_W
CAMERA_FIM = CAMPO_FIM - TELA_W


def limite(fator):
    """x da camada até onde vai o jeito novo (caatinga, vila, vila alta e campo)."""
    return int(CAMERA_FIM * fator + TELA_W)


def antigo(x, fator):
    """A peça antiga nessa posição da camada continua (fica depois do campo de pouso)."""
    return x >= limite(fator)


def texto(t):
    """Máscara das letras 5x7, com acento em cima e cedilha embaixo."""
    w = len(t) * 6 - 1
    m = np.zeros((11, w), bool)
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
        elif ac == "cedilha":
            m[9, x + 2] = m[10, x + 1] = True
    return m


def letreiro(q, t, x, y, fundo="cal", tinta="telha", lz_fundo=0.8, lz_tinta=0.3, folga=3):
    """Placa pintada com as letras e a sombra delas (sem contorno). Devolve a largura."""
    X, Y = q.xx, q.yy
    m = texto(t)
    lh, lw = m.shape
    faixa = (X >= x - folga) & (X < x + lw + folga) & (Y >= y - 1) & (Y < y + lh + 1)
    q.pinta(faixa, fundo, np.where(Y == y - 1, min(0.99, lz_fundo + 0.15),
                                   np.where(Y == y + lh, lz_fundo - 0.35, lz_fundo - 0.1 * (X > x + lw * 0.6))))
    letra = np.zeros(q.a.shape, bool)
    letra[y:y + lh, x:x + lw] = m
    q.pinta(np.roll(np.roll(letra, 1, 0), 1, 1) & faixa & ~letra, fundo, np.full(q.a.shape, 0.2))
    q.pinta(letra, tinta, np.full(q.a.shape, lz_tinta))
    return lw + 2 * folga


# ---------------------------------------------------------------- hangar de zinco
def hangar(FW=150, H=124, SW=30, SH=12, sem=4, nome="AVIAÇÃO MILITAR", estrela=True, dentro=True):
    """Hangar da Aviação Militar: frente de chapa ondulada com o teto em arco, e o arco
    recuando para trás (o teto e o lado direito aparecem, na sombra), portão de correr
    aberto com as folhas de zinco empurradas para os lados, lá dentro o escuro com a
    bancada, a hélice de reserva na parede, pneus, tambores e o sol entrando pelo chão.
    Ferrugem escorrendo, remendo de chapa, rebite, marca de bala, estrela e letreiro."""
    W = FW + SW
    q = Quadro(W, H)
    X, Y = q.xx, q.yy
    rng = np.random.default_rng(sem)
    rz = lambda e, s_: ruido(H, W, e, sem * 17 + s_)  # noqa: E731
    top = SH + 3
    ry = int(FW * 0.29)                                  # altura do arco
    yb = top + ry                                        # nascença do arco
    cx, rx = FW / 2, FW / 2

    def arco_y(xx, dx=0.0, dy=0.0):
        u = np.clip((xx + 0.5 - dx - cx) / rx, -1, 1)
        return yb + dy - ry * np.sqrt(1 - u ** 2)

    frente = (X < FW) & (Y >= arco_y(X))
    q.pinta(frente, "madeira", np.full((H, W), 0.3))              # fundo: nenhum furo na frente
    # --- teto e lado recuando: o contorno da frente arrastado para trás (cima-direita)
    ang = np.full((H, W), np.nan)
    lado = np.zeros((H, W), bool)
    na = int(np.pi * rx * 2.5)
    a = np.linspace(0, np.pi, na)
    for t in np.linspace(1, 0, SW * 3):
        dx, dy = t * SW, -t * SH
        px = np.round(cx + rx * np.cos(a) * 0.999 - 0.5 + dx).astype(int)
        py = np.round(yb - ry * np.sin(a) + dy).astype(int)
        ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        ang[py[ok], px[ok]] = a[ok]
        xl = int(round(FW - 1 + dx))
        y0, y1 = int(round(yb + dy)), int(round(H - 1 + dy))
        if 0 <= xl < W:
            lado[max(0, y0):y1 + 1, xl] = True
            ang[max(0, y0):y1 + 1, xl] = np.nan
    teto = ~np.isnan(ang) & ~frente
    lado &= ~frente & ~teto
    # teto: chapa ondulada correndo para trás, luz pela inclinação do arco
    a_ = np.nan_to_num(ang)
    dot = -0.55 * np.cos(a_) + 0.8 * np.sin(a_)
    onda = np.sin(a_ * rx / 2.4)
    lz = 0.30 + 0.45 * dot + 0.12 * (onda > 0.55) - 0.12 * (onda < -0.55)
    lz = np.where(a_ > 2.7, lz + 0.12, lz)                       # quina do arco virada pro sol
    q.pinta(teto, "azul", np.clip(lz, 0.02, 0.999))
    ferr = teto & (ruido(H, W, (1.2, 4), sem + 3) > 1.3)
    q.pinta(ferr, "telha", np.clip(0.2 + 0.25 * dot, 0, 0.999))
    # lado direito: chapa na sombra, ondas na horizontal, pé escurecendo
    ylado = Y - (yb - (X - FW) * SH / SW)
    lz = 0.30 + 0.08 * (np.sin(Y * np.pi / 2) > 0.5) - 0.06 * (ylado > (H - yb) - 10)
    q.pinta(lado, "azul", np.clip(lz, 0, 0.999))
    janela = lado & (np.abs(X - (FW + SW * 0.5)) < SW * 0.22) & (ylado > 14) & (ylado < 30)
    q.pinta(janela, "madeira", np.where(ylado < 17, 0.05, 0.15))
    # chão de terra no pé do lado (o hangar avança para trás) com a sombra dele
    cunha = (X >= FW) & (Y > H - 1 - (X - FW) * SH / SW) & ~lado & ~teto
    q.pinta(cunha, "terra", np.where(Y > H - 3, 0.35, 0.25))
    # --- frente: borda do arco (perfil da chapa ondulada visto de frente)
    yarc = arco_y(X)
    borda = frente & (Y < yarc + 4) & (Y < yb + 1)
    u = (X + 0.5 - cx) / rx
    perfil = np.sin((np.arcsin(np.clip(u, -1, 1)) + np.pi / 2) * rx / 2.4)
    lz = 0.78 - 0.22 * u + 0.12 * (perfil > 0.3) - 0.14 * (perfil < -0.3)
    lz = np.where(Y < yarc + 1, lz + 0.12, lz)
    # empena: chapas verticais onduladas, juntas a cada 24 px com rebite
    emp = frente & ~borda & (Y < yb + 2)
    k4 = X % 4
    lze = np.select([k4 == 0, k4 == 1, k4 == 2], [0.74, 0.62, 0.42], 0.55) - 0.14 * u
    lze = lze - 0.18 * np.clip((Y - yarc - 4) / 4, 0, 1) * (Y < yarc + 8)        # sombra da borda
    lze = lze + 0.03 * rz(8, 4)
    junta = ((X - 3) % 24) == 0
    lze = np.where(junta, 0.3, lze)
    lze = np.where(junta & ((Y % 5) == 2), 0.95, lze)
    remendo = emp & (np.abs(X - (cx + rx * 0.5)) < 9) & (np.abs(Y - (yb - ry * 0.28)) < 7)
    lze = np.where(remendo, lze - 0.1 + 0.12 * ((X + Y) % 3 == 0), lze)
    q.pinta(emp, "azul", quantiza_limpo(np.clip(lze, 0.02, 0.999), 6))
    q.pinta(borda, "azul", np.clip(lz, 0.02, 0.999))
    q.pinta(remendo & ((np.abs(X - (cx + rx * 0.5)) > 7.5) | (np.abs(Y - (yb - ry * 0.28)) > 5.5)),
            "terra", np.full((H, W), 0.35))
    # ferrugem escorrendo da borda e das juntas
    for _ in range(int(FW / 11)):
        x = int(rng.uniform(6, FW - 6))
        y0 = int(arco_y(np.array([x]))[0]) + 3
        n = int(rng.integers(5, 30))
        larg = np.clip(1.6 - (Y - y0) / n * 1.4, 0.5, 2)              # mancha larga em cima, fio embaixo
        m = (np.abs(X + 0.5 - x - 0.4 * np.sin((Y - y0) / 3.0)) < larg) & (Y >= y0) & (Y < y0 + n) & emp
        q.pinta(m, "telha", np.clip(0.42 - (Y - y0) / n * 0.2 - 0.12 * (X + 0.5 > x), 0, 0.999))
    # estrela pintada (desbotada) e o letreiro numa tábua
    if estrela:
        ex, ey, er = cx, top + ry * 0.42, ry * 0.24
        th = np.arctan2(Y - ey, X + 0.5 - ex) + np.pi / 2
        rr = np.hypot(X + 0.5 - ex, Y - ey)
        raio = er * (0.45 + 0.55 * (np.cos(th * 5) * 0.5 + 0.5) ** 2.2)
        est = (rr < raio) & emp
        q.pinta(est, "terra", np.where(X + 0.5 < ex, 0.97, 0.8) - 0.15 * (k4 == 2))
        q.pinta(est & (rz(1.0, 9) > 1.2), "azul", np.full((H, W), 0.6))
        q.pinta((rr < er * 0.32) & emp, "telha", np.where(X + 0.5 < ex, 0.62, 0.45))
    if nome:
        lw = len(nome) * 6 - 1
        ly = yb - 14
        tab = (X >= cx - lw / 2 - 5) & (X < cx + lw / 2 + 5) & (Y >= ly - 2) & (Y < ly + 13)
        tb = (X - int(cx - lw / 2 - 5)) % 7
        q.pinta(tab, "madeira", np.where(Y == ly - 2, 0.99, np.where(Y == ly + 12, 0.2, 0.8 - 0.1 * (Y % 4 == 0))))
        letreiro(q, nome, int(cx - lw / 2), ly, fundo="cal", tinta="telha", lz_fundo=0.86, lz_tinta=0.28, folga=2)
        # pregos e a sombra da tábua na chapa
        q.pinta(tab & ((X == int(cx - lw / 2 - 3)) | (X == int(cx + lw / 2 + 2))) & ((Y == ly) | (Y == ly + 10)),
                "madeira", np.full((H, W), 0.05))
        sb = (X >= cx - lw / 2 - 3) & (X < cx + lw / 2 + 7) & (Y == ly + 13) & emp
        q.pinta(sb, "azul", np.full((H, W), 0.15))
        del tb
    # --- viga do portão (trilho) na nascença do arco
    vg = (X < FW) & (Y >= yb) & (Y < yb + 6)
    q.pinta(vg, "madeira", np.where(Y == yb, 0.99, np.where(Y >= yb + 4, 0.2, 0.62 - 0.12 * X / FW)))
    q.pinta((X < FW) & (Y == yb + 6), "madeira", np.full((H, W), 0.08))
    # --- vão do portão e o escuro lá dentro
    d0, d1 = int(FW * 0.2), int(FW * 0.8)
    vy0, vy1 = yb + 7, H - 3
    vao = (X >= d0) & (X < d1) & (Y >= vy0) & (Y < vy1)
    if dentro:
        fundo = 0.03 + 0.10 * np.clip((Y - vy0) / (vy1 - vy0), 0, 1) + 0.05 * (((X - d0) % 8) == 0)
        q.pinta(vao, "madeira", fundo)
        # tesouras do telhado lá no fundo
        for k in range(3):
            tx = d0 + (d1 - d0) * (k + 0.5) / 3
            ts = vao & (Y < vy0 + 12) & ((np.abs(X - tx - (Y - vy0) * 1.6) < 0.8) | (np.abs(X - tx + (Y - vy0) * 1.6) < 0.8))
            q.pinta(ts, "madeira", np.full((H, W), 0.14))
        q.pinta(vao & (Y == vy0 + 12), "madeira", np.full((H, W), 0.14))
        # hélice de reserva pendurada na parede do fundo
        hx, hy = d0 + 14, vy0 + 30
        hel = vao & (np.abs(X - hx) < 2.2 - np.abs(Y - hy) / 22) & (np.abs(Y - hy) < 24)
        q.pinta(hel, "madeira", np.where(X < hx, 0.5, 0.3))
        q.pinta(vao & (np.hypot(X - hx, Y - hy) < 2.5), "azul", np.full((H, W), 0.4))
        # bancada com torno e ferramentas na parede
        bx0, bx1, by = d1 - 34, d1 - 6, vy1 - 18
        q.pinta(vao & (X >= bx0) & (X < bx1) & (Y >= by) & (Y < by + 3), "madeira", np.where(Y == by, 0.6, 0.3))
        for lx_ in (bx0 + 2, bx1 - 4):
            q.pinta(vao & (X >= lx_) & (X < lx_ + 2) & (Y >= by + 3) & (Y < vy1), "madeira", np.full((H, W), 0.22))
        q.pinta(vao & (X >= bx0 + 6) & (X < bx0 + 12) & (Y >= by - 4) & (Y < by), "azul", np.where(X < bx0 + 8, 0.45, 0.25))
        for k in range(4):
            fx = bx0 + 4 + k * 6
            q.pinta(vao & (X == fx) & (Y >= by - 22) & (Y < by - 12 + k % 2 * 3), "azul", np.full((H, W), 0.35))
            q.pinta(vao & (np.abs(X - fx) <= 1) & (Y == by - 22), "azul", np.full((H, W), 0.42))
        # dois tambores
        for k in range(2):
            tx = d0 + (d1 - d0) * 0.66 + k * 9
            tb_ = vao & (X >= tx) & (X < tx + 8) & (Y >= vy1 - 13) & (Y < vy1)
            q.pinta(tb_, "verde", np.where(X < tx + 2, 0.35, np.where(X > tx + 5, 0.1, 0.2)) - 0.1 * ((Y - vy1 + 13) % 5 == 0))
        # sol da tarde entrando pelo chão (o portão aberto)
        sol = vao & (Y >= vy1 - 4) & (X < d0 + 34 - (vy1 - Y) * 3)
        q.pinta(sol, "terra", np.where(Y == vy1 - 1, 0.4, 0.32))
        # lâmpada pendurada com a cúpula de lata
        lx_ = int((d0 + d1) / 2)
        q.pinta(vao & (X == lx_) & (Y < vy0 + 16), "madeira", np.full((H, W), 0.2))
        cup = vao & (np.abs(X + 0.5 - lx_) < (Y - vy0 - 16) * 1.2 + 1) & (Y >= vy0 + 16) & (Y < vy0 + 20)
        q.pinta(cup, "azul", np.where(X < lx_, 0.55, 0.35))
        q.pinta(vao & (np.abs(X + 0.5 - lx_) < 2) & (Y == vy0 + 20), "terra", np.full((H, W), 0.95))
    else:
        q.pinta(vao, "madeira", np.full((H, W), 0.12))
    # ombreira: sombra dura do lado esquerdo e do alto dentro do vão
    q.pinta(vao & ((X < d0 + 3) | (Y < vy0 + 2)), "madeira", np.full((H, W), 0.02))
    # soleira de cimento
    q.pinta((X >= d0 - 2) & (X < d1 + 2) & (Y >= vy1) & (Y < H), "cal", np.where(Y == vy1, 0.8, 0.45 - 0.1 * (X > cx)))
    # --- folhas do portão empurradas para os lados: quadro de tábua, chapa e mão-francesa em X
    for f0, f1 in ((2, d0 - 1), (d1 + 1, FW - 2)):
        fo = (X >= f0) & (X < f1) & (Y >= yb + 6) & (Y < H - 1)
        k4f = (X - f0) % 4
        lzf = np.select([k4f == 0, k4f == 1, k4f == 2], [0.66, 0.55, 0.36], 0.48) - 0.12 * (X > cx)
        lzf = lzf - 0.12 * np.clip((Y - (H - 14)) / 14, 0, 1)
        q.pinta(fo, "azul", lzf)
        qd = fo & ((X < f0 + 2) | (X >= f1 - 2) | (Y < yb + 9) | (Y >= H - 4) | (np.abs(Y - (yb + H) / 2) < 1))
        q.pinta(qd, "madeira", np.where(X < f0 + 1, 0.85, np.where(Y < yb + 7, 0.8, 0.45)) - 0.15 * (X > cx))
        ym = (yb + H) / 2
        for ya, yz in ((yb + 9, ym - 1), (ym + 1, H - 4)):
            s = (f1 - f0 - 4) / max(1, yz - ya)
            dg = fo & (Y >= ya) & (Y < yz) & (np.abs((X - f0 - 2) - (Y - ya) * s) < 1.1)
            q.pinta(dg, "madeira", np.full((H, W), 0.5 - 0.15 * (f0 > cx)))
        # ferrugem no pé e marca de bala
        q.pinta(fo & (ruido(H, W, 1.2, sem + f0) > 1.4) & (Y > H - 20), "telha", np.full((H, W), 0.3))
        for _ in range(2):
            bx_, by_ = int(rng.uniform(f0 + 3, f1 - 3)), int(rng.uniform(yb + 12, H - 10))
            q.pinta((X == bx_) & (Y == by_), "madeira", np.full((H, W), 0.0))
            q.pinta((X == bx_ + 1) & (Y == by_ + 1), "azul", np.full((H, W), 0.99))
        # rodinhas no trilho
        for rx_ in (f0 + 4, f1 - 5):
            q.pinta((np.hypot(X + 0.5 - rx_, Y - (yb + 6)) < 2), "azul", np.where(X < rx_, 0.6, 0.25))
    # sombra das folhas na parede e cunhais
    q.pinta((X < 2) & frente & (Y >= yb + 6), "madeira", np.where(X == 0, 0.7, 0.5))
    q.pinta((X >= FW - 2) & (X < FW) & frente & (Y >= yb + 6), "madeira", np.full((H, W), 0.25))
    # lampião de lata em cima do portão
    lx_ = int(cx)
    q.pinta((X >= lx_ - 1) & (X < lx_ + 1) & (Y >= yb - 1) & (Y < yb + 3), "madeira", np.full((H, W), 0.08))
    # sapata de pedra e o barro subindo
    pe = frente & (Y >= H - 3) & ~((X >= d0 - 2) & (X < d1 + 2))
    q.pinta(pe, "cal", np.where(Y == H - 3, 0.55, 0.3))
    pe = frente & (Y >= H - 9) & (Y < H - 3) & (ruido(H, W, (1, 3), sem + 8) > 0.5 - (Y - H + 9) * 0.25) & ~vao
    q.img[pe] = cm.escurecer(q.img[pe], 1)
    q.a[:] = q.a & (frente | teto | lado | cunha)
    return q


# ---------------------------------------------------------------- tanque, baliza e miúdos
def tanque(sem=2):
    """Tanque de gasolina deitado em berços de tábua: chapa rebitada oliva com o brilho
    comprido em cima e a luz de baixo refletida do chão, tampas nas pontas, boca de visita
    em cima, escada, registro com a mangueira enrolada, placa GASOLINA, ferrugem."""
    W, H = 90, 50
    q = Quadro(W, H)
    X, Y = q.xx, q.yy
    cy, r = 21, 14
    x0, x1 = 12, 74
    n = (Y - cy) / r
    corpo = (np.abs(n) <= 1) & (X >= x0) & (X < x1)
    lz = 0.52 - 0.42 * n + 0.22 * ((n > -0.72) & (n < -0.45)) + 0.1 * (n > 0.8) - 0.08 * (X - x0) / (x1 - x0)
    q.pinta(corpo, "verde", quantiza_limpo(np.clip(lz, 0.02, 0.999), 7))
    tl = ((X + 0.5 - x0) / 5) ** 2 + n ** 2 < 1                     # tampa da esquerda (no sol)
    q.pinta(tl & (X < x0), "verde", np.clip(0.75 - 0.3 * n, 0, 0.999))
    tr = ((X + 0.5 - x1) / 5) ** 2 + n ** 2 < 1                     # tampa da direita (na sombra)
    q.pinta(tr & (X >= x1), "verde", np.clip(0.3 - 0.2 * n, 0, 0.999))
    tanq = corpo | (tl & (X < x0)) | (tr & (X >= x1))
    for sx in (x0 + 15, x0 + 31, x0 + 47):                       # juntas de chapa com rebites
        q.pinta(tanq & (X == sx), "verde", np.full((H, W), 0.12))
        q.pinta(tanq & (X == sx + 1) & ((Y % 3) == 0), "verde", np.clip(0.9 - 0.4 * n, 0, 0.999))
    for sx in (x0, x1 - 1):
        q.pinta(tanq & (X == sx), "verde", np.full((H, W), 0.2 if sx > x0 else 0.85))
    # ferrugem e escorrido
    fer = tanq & (ruido(H, W, 1.4, sem) > 1.45)
    q.pinta(fer, "telha", np.clip(0.38 - 0.2 * n, 0, 0.999))
    for x in (x0 + 8, x0 + 40, x0 + 55):
        q.pinta(tanq & (X == x) & (Y > cy + 4), "telha", np.full((H, W), 0.25))
    # placa GASOLINA
    lw = 8 * 6 - 1
    letreiro(q, "GASOLINA", int((x0 + x1) / 2 - lw / 2), cy - 6, fundo="cal", tinta="telha", lz_fundo=0.85, lz_tinta=0.3)
    # boca de visita em cima
    q.pinta((X >= 38) & (X < 48) & (Y >= cy - r - 4) & (Y < cy - r + 1), "verde",
            np.where(Y == cy - r - 4, 0.95, np.where(X > 45, 0.25, 0.6)))
    q.pinta((X >= 36) & (X < 50) & (Y == cy - r - 5), "azul", np.full((H, W), 0.7))
    # berços de tábua e toras no chão
    for bx in (x0 + 10, x1 - 14):
        be = (np.abs(X + 0.5 - bx) < 5 + (Y - (cy + 8)) * 0.25) & (Y >= cy + 8) & (Y < H - 5) & ~tanq
        q.pinta(be, "madeira", np.where(X + 0.5 < bx, 0.72, 0.42) - 0.12 * ((Y % 4) == 0))
    tora = (X >= x0 - 4) & (X < x1 + 4) & (Y >= H - 5) & (Y < H)
    q.pinta(tora, "madeira", np.where(Y == H - 5, 0.8, np.where(Y == H - 1, 0.15, 0.48)) - 0.1 * ((X % 11) == 0))
    q.pinta((np.hypot(X + 0.5 - (x1 + 4), (Y - (H - 2.5)) * 1.0) < 2.5), "madeira", np.where(X < x1 + 4, 0.85, 0.6))
    # escada de ferro do lado direito
    for ex in (x1 + 6, x1 + 12):
        q.pinta((X == ex) & (Y >= cy - r - 2) & (Y < H - 5), "azul", np.full((H, W), 0.3 if ex > x1 + 8 else 0.55))
    q.pinta((X > x1 + 6) & (X < x1 + 12) & (Y >= cy - r) & (Y < H - 6) & ((Y - cy) % 5 == 0), "azul", np.full((H, W), 0.5))
    # registro, cano e a mangueira enrolada no chão
    q.pinta((X >= x0 + 2) & (X < x0 + 5) & (Y >= cy + r - 2) & (Y < cy + r + 8), "azul", np.where(X == x0 + 2, 0.7, 0.35))
    q.pinta(np.hypot(X + 0.5 - (x0 + 3.5), Y - (cy + r + 5)) < 2.6, "telha", np.where(X < x0 + 3, 0.62, 0.35))
    for k in range(3):
        an = (np.abs(np.hypot((X + 0.5 - (x0 - 2)) / 7, (Y - (H - 3)) / 2.2) - 1 + k * 0.18) < 0.12)
        q.pinta(an & (Y > H - 6) & ~tora, "madeira", np.full((H, W), 0.1 + 0.08 * k))
    q.a[:] = q.a
    return q


def baliza(sem=0):
    """Baliza da pista: tambor meio enterrado em listras de telha e cal desbotadas."""
    q = Quadro(12, 12)
    X, Y = q.xx, q.yy
    u = (X + 0.5 - 6) / 5
    corpo = (np.abs(u) < 1) & (Y >= 2)
    lz = 0.62 - 0.38 * u + 0.15 * (np.abs(u + 0.4) < 0.2)
    lista = ((Y - 2) // 3) % 2 == 0
    q.pinta(corpo & lista, "telha", np.clip(lz, 0, 0.999))
    q.pinta(corpo & ~lista, "cal", np.clip(lz + 0.1, 0, 0.999))
    q.pinta((np.abs(u) < 1) & (Y < 2), "cal", np.where(Y == 0, 0.6, 0.4))
    q.pinta(corpo & (ruido(12, 12, 0.8, sem) > 1.4), "telha", np.full((12, 12), 0.2))
    return q


def pedra_caiada(sem=0):
    """Pedra pintada de cal marcando a beira da pista."""
    q = Quadro(9, 5)
    X, Y = q.xx, q.yy
    m = ((X + 0.5 - 4.5) / 4.5) ** 2 + ((Y - 4.5) / 4.2) ** 2 < 1
    q.pinta(m, "cal", np.clip(0.95 - 0.12 * (X - 2) - 0.1 * Y + 0.0 * sem, 0.05, 0.999))
    return q


def pneus(n=3, sem=0):
    """Pneus velhos de avião deitados uns sobre os outros: cada um é uma rosca vista de
    lado (ponta redonda, banda com sulco), o de cima mostra o furo do meio."""
    q = Quadro(28, 7 * n + 5)
    X, Y = q.xx, q.yy
    for k in range(n):
        cy = q.h - 4.5 - k * 7
        cx = 14 + ((k * 5 + sem) % 3 - 1) * 1.2
        rx, ry = 12.5, 3.6
        an = (np.abs(X + 0.5 - cx) < rx - ry + np.sqrt(np.clip(ry ** 2 - (Y - cy) ** 2, 0, None)))
        an &= np.abs(Y - cy) < ry
        lz = 0.3 - 0.28 * (Y - cy) / ry - 0.1 * (X + 0.5 - cx) / rx
        lz = np.where(np.abs(Y - cy) < 0.6, lz - 0.12, lz)                    # sulco da banda
        q.pinta(an, "madeira", np.clip(lz, 0.0, 0.999))
        if k == n - 1:
            topo = (((X + 0.5 - cx) / rx) ** 2 + ((Y - (cy - ry + 0.5)) / 2.2) ** 2 < 1) & (Y < cy - ry + 1.5)
            q.pinta(topo, "madeira", np.full(q.a.shape, 0.42))
            furo = ((X + 0.5 - cx) / 6) ** 2 + ((Y - (cy - ry + 1)) / 1.3) ** 2 < 1
            q.pinta(furo, "madeira", np.full(q.a.shape, 0.02))
    return q


def helice(alt=46):
    """Hélice de reserva encostada na parede, de pau envernizado."""
    q = Quadro(12, alt)
    X, Y = q.xx, q.yy
    meio = alt / 2
    eixo = 6 + (Y - meio) * 0.08                         # encostada: o topo pende para a direita
    d = np.abs(Y - meio) / (alt / 2)
    larg = 1.2 + 2.6 * np.sin(np.clip(d, 0, 1) * np.pi) ** 0.8 * (d > 0.12) + 1.6 * (d <= 0.12)
    m = (np.abs(X + 0.5 - eixo) < larg) & (d < 0.98)
    lz = np.where(X + 0.5 < eixo, 0.92, 0.5) - 0.3 * (d > 0.86)       # ponta pintada de escuro
    q.pinta(m, "madeira", lz)
    q.pinta(np.hypot(X + 0.5 - eixo, Y - meio) < 2.6, "azul", np.where(X + 0.5 < eixo, 0.75, 0.35))
    return q


# ---------------------------------------------------------------- peças do plano de trás
def caixa_dagua(alt=132, sem=7):
    """Caixa d'água de madeira em torre: tonel de aduelas com cintas de ferro e o chapéu de
    zinco, plataforma de tábua, quatro pernas abertas com mão-francesa em X (as de trás no
    escuro), escada e o cano descendo."""
    W = 64
    q = Quadro(W, alt)
    X, Y = q.xx, q.yy
    cx = W / 2
    t0, t1 = 12, 52                                  # tonel
    ty0, ty1 = 10, 50
    # pernas de trás (escuro), depois as da frente
    for (xa, xb, lzp) in ((cx - 9, cx - 14, 0.12), (cx + 9, cx + 14, 0.1), (cx - 17, cx - 28, 0.6), (cx + 17, cx + 28, 0.32)):
        s = (xb - xa) / (alt - ty1)
        p = (np.abs(X + 0.5 - (xa + (Y - ty1) * s)) < 1.6) & (Y >= ty1)
        q.pinta(p, "madeira", np.full((alt, W), lzp) + 0.15 * (X + 0.5 < xa + (Y - ty1) * s) * (lzp > 0.2))
    # mão-francesa em X entre as pernas da frente
    for k in range(3):
        ya, yz = ty1 + 4 + k * 26, ty1 + 4 + (k + 1) * 26
        if yz > alt - 2:
            break
        xl_a, xr_a = cx - 17 - (ya - ty1) * 11 / (alt - ty1), cx + 17 + (ya - ty1) * 11 / (alt - ty1)
        xl_z, xr_z = cx - 17 - (yz - ty1) * 11 / (alt - ty1), cx + 17 + (yz - ty1) * 11 / (alt - ty1)
        for (xa, xz) in ((xl_a, xr_z), (xr_a, xl_z)):
            s = (xz - xa) / (yz - ya)
            dg = (np.abs(X + 0.5 - (xa + (Y - ya) * s)) < 1.0) & (Y >= ya) & (Y < yz)
            q.pinta(dg, "madeira", np.full((alt, W), 0.42))
        q.pinta((Y == ya) & (X > xl_a) & (X < xr_a), "madeira", np.full((alt, W), 0.5))
    # cano descendo pelo meio
    q.pinta((np.abs(X + 0.5 - (cx + 3)) < 1.5) & (Y >= ty1), "azul", np.where(X < cx + 3, 0.6, 0.3))
    # plataforma
    q.pinta((X >= t0 - 4) & (X < t1 + 4) & (Y >= ty1) & (Y < ty1 + 4), "madeira", np.where(Y == ty1, 0.9, np.where(Y == ty1 + 3, 0.2, 0.55)))
    # tonel de aduelas (cilindro com luz da esquerda)
    u = (X + 0.5 - cx) / ((t1 - t0) / 2)
    ton = (np.abs(u) < 1) & (Y >= ty0) & (Y < ty1)
    lz = 0.62 - 0.42 * u + 0.12 * (np.abs(u + 0.45) < 0.15) - 0.15 * ((X % 5) == 0)
    q.pinta(ton, "madeira", quantiza_limpo(np.clip(lz, 0.02, 0.999), 6))
    for yc_ in (ty0 + 6, ty0 + 20, ty1 - 6):
        q.pinta(ton & (np.abs(Y - yc_) < 1), "azul", np.clip(0.55 - 0.35 * u, 0, 0.999))
    q.pinta(ton & (ruido(alt, W, (3, 0.6), sem) > 1.4) & (Y > ty0 + 10), "madeira", np.full((alt, W), 0.15))
    # chapéu de zinco cônico
    cap = (np.abs(X + 0.5 - cx) < (Y + 1) * 2.6) & (Y < ty0 + 1) & (np.abs(X + 0.5 - cx) < (t1 - t0) / 2 + 3)
    q.pinta(cap, "azul", np.where(X + 0.5 < cx, 0.72, 0.35) - 0.12 * ((X % 3) == 0))
    q.pinta(cap & (Y == ty0), "azul", np.full((alt, W), 0.18))
    # escada na perna da esquerda
    for ex in (cx - 23, cx - 19):
        q.pinta((np.abs(X - ex) < 0.6) & (Y >= ty1 + 4), "madeira", np.full((alt, W), 0.3))
    q.pinta((X > cx - 23) & (X < cx - 19) & (Y > ty1 + 4) & ((Y % 5) == 0), "madeira", np.full((alt, W), 0.35))
    return q


def mastro_radio(alt=120):
    """Mastro do rádio da Aviação: treliça de ferro afinando para cima (perna clara na luz,
    a outra na sombra, travessas e diagonais), isolador branco no alto e dois estais retos
    descendo até as estacas."""
    W = 56
    q = Quadro(W, alt)
    X, Y = q.xx, q.yy
    cx = W / 2
    meia = 1.5 + 4.5 * Y / alt
    for s_ in (-1, 1):
        q.pinta(np.abs(X + 0.5 - (cx + s_ * meia)) < 0.9, "azul", np.full((alt, W), 0.62 if s_ < 0 else 0.25))
    trav = ((Y % 9) == 0) & (np.abs(X + 0.5 - cx) < meia) & (Y > 4)
    q.pinta(trav, "azul", np.full((alt, W), 0.45))
    fase = (Y % 9) / 9.0
    dg = (np.abs(X + 0.5 - (cx - meia + 2 * meia * fase)) < 0.7) & (Y > 4)
    q.pinta(dg, "azul", np.full((alt, W), 0.35))
    q.pinta((np.abs(X + 0.5 - cx) < 1.5) & (Y < 5), "cal", np.where(X < cx, 0.95, 0.6))
    q.pinta((np.abs(X + 0.5 - cx) < 0.6) & (Y < 2), "azul", np.full((alt, W), 0.3))
    for xe in (2, W - 3):
        for k in range(300):
            t = k / 299
            x_, y_ = cx + (xe - cx) * t, 6 + (alt - 3 - 6) * t
            q.img[int(y_), int(x_)] = cm.RGB["madeira"][2]
            q.a[int(y_), int(x_)] = True
        q.pinta((np.abs(X - xe) < 1) & (Y >= alt - 4), "madeira", np.full((alt, W), 0.5))
    return q


# ---------------------------------------------------------------- camadas
def camada_paredao(h=130):
    return va.camada_paredao(h, ate=limite(0.2))


def camada_frente(h=44):
    return va.camada_frente(h, ate=limite(1.1))


def camada_meio(h=124):
    """Os morros continuam por planos; árvores ralas, moitas, uma cerca e um sítio ao longe."""
    fator = 0.45
    lim = limite(fator)
    q = va.camada_meio(h, ate=lim)
    rng = np.random.default_rng(51)
    x0 = va.limite(fator) - 10
    topo = np.argmax(q.a, axis=0)
    for _ in range(22):
        cx = rng.uniform(x0, lim); r = rng.uniform(3, 6)
        cy = topo[int(cx)] + rng.uniform(3, 24)
        d = np.hypot(q.xx - cx, (q.yy - cy) * 1.4) / r
        q.pinta((d < 1) & (q.yy < cy + 2), "verde",
                np.clip((0.5 - 0.35 * (q.xx - cx) / r - 0.45 * (q.yy - cy) / r) * 0.5 + 0.2, 0, 0.999))
    x = x0 + 30.0
    while x < lim - 10:
        p = nevoa(cm.arvore(int(rng.uniform(32, 48)), sem=int(x) + 9, folhas=rng.random() > 0.35), 0.42)
        py = topo[int(min(x, q.w - 1))] + rng.uniform(2, 8) - p.h
        if py >= 0:
            q.colar(p, x - p.w / 2, py)
        x += rng.uniform(55, 115)
    sx = int(x0 + (lim - x0) * 0.62)
    c = nevoa(cm.casinha_longe(42, 18, sem=44), 0.36)
    q.colar(c, sx, topo[sx + c.w // 2] + 6 - c.h)
    cv = nevoa(cm.cerca_varas(70, 14, sem=45), 0.36)
    cxv = int(x0 + (lim - x0) * 0.2)
    q.colar(cv, cxv, topo[cxv + 35] + 8 - cv.h)
    return q


def camada_perto(h=160):
    """Plano de trás (0,75): atrás da pista, a caixa d'água de madeira, o galpão de zinco,
    o mastro do rádio com a casinha do telegrafista, árvores e mandacarus, moitas no pé."""
    fator = 0.75
    lim = limite(fator)
    q = va.camada_perto(h, ate=lim)
    chao = h - 1
    rng = np.random.default_rng(62)
    x0 = va.limite(fator)
    x = float(x0 - 10)
    while x < lim:
        if rng.random() < 0.75:
            p = cm.moita(int(rng.integers(30, 56)), int(rng.integers(14, 22)), sem=int(x) + 5, seca=rng.uniform(0.3, 0.8))
        else:
            p = cm.xiquexique(int(rng.integers(22, 32)), int(rng.integers(16, 22)), sem=int(x) + 6)
        q.colar(p, x, chao - p.h + 3)
        x += rng.integers(28, 66)
    casa = lambda *a, **k: nevoa(cm.casa(*a, sombra_beiral=True, **k), 0.16)  # noqa: E731
    # (x na camada, peça): a caixa d'água fica à direita do hangar enquanto ele está na tela
    pecas = [
        (3700, cm.arvore(128, sem=160, folhas=False)),
        (3850, cm.mandacaru(86, sem=260)),
        (3990, nevoa(caixa_dagua(132), 0.1)),
        (4060, cm.arvore(140, sem=161, folhas=True)),
        (4250, nevoa(hangar(118, 92, 22, 9, sem=11, nome=None, estrela=False, dentro=False), 0.16)),
        (4396, nevoa(mastro_radio(118), 0.12)),
        (4446, casa(74, 46, 28, sem=64, alpendre=False, lado=12, porta=(10, 16, 30), janela=(46, 10, 14))),
        (4566, cm.mandacaru(70, sem=261, bracos=((15, 30, 56),))),
    ]
    for x, p in sorted(pecas, key=lambda e: -e[1].h):
        if x + p.w <= lim + 40:
            q.colar(p, x, chao - p.h + 2)
    return q


def camada_jogo(fase, alt=176, topo_mundo=40):
    """Plano do jogo: o chão continua pela pista (marcas de pneu, pedras caiadas, balizas),
    o hangar, pneus e hélice de reserva, o tanque de gasolina com a mancha de óleo, a
    trincheira de sacos e a cerca de arame da guarda, na luz da cena."""
    import fase1 as f1
    CH = f1.CHAO
    q = va.camada_jogo(fase, alt, topo_mundo, ate=CAMPO_FIM + 40)
    y = lambda wy: wy - topo_mundo  # noqa: E731
    yc = y(CH) - 1
    rng = np.random.default_rng(93)
    w = CAMPO_FIM + 120
    # pedrinhas encaixadas no chão
    for _ in range(int((w - CAMPO_INI) / 548 * 30)):
        px = rng.uniform(CAMPO_INI - 20, w); py = rng.uniform(y(CH) + 3, alt + 2)
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
    # pista: duas trilhas de pneu (terra calcada, mais escura, com o desenho da banda)
    p0, p1 = f1.HANGAR_X + 40, CAMPO_FIM - 30
    for k, (ty, larg) in enumerate(((yc + 5, 3), (yc + 11, 4))):
        ond = np.round(0.8 * np.sin(q.xx / 90.0 + k))
        tr = (q.xx >= p0 + k * 30) & (q.xx < p1) & (q.yy >= ty + ond) & (q.yy < ty + larg + ond) & q.a
        tr &= ruido(alt, q.w, (1, 6), 300 + k) > -0.9
        q.img[tr] = cm.escurecer(q.img[tr], 1)
        banda = tr & (((q.xx + q.yy) % 4) == 0)
        q.img[banda] = cm.escurecer(q.img[banda], 1)
    # pedras caiadas na beira de trás da pista
    for x in range(int(f1.HANGAR_X + 190), int(CAMPO_FIM - 60), 26):
        q.colar(pedra_caiada(x), x + rng.uniform(-3, 3), yc - 2)
    # manchas de óleo na frente do hangar e embaixo do tanque
    for mx, ml in ((f1.HANGAR_X + 70, 22), (f1.HANGAR_X + 120, 12), (5608, 14), (5180, 18)):
        m = (((q.xx - mx) / ml) ** 2 + ((q.yy - (yc + 4)) / 2.5) ** 2 < 1) & q.a
        m &= ruido(alt, q.w, 1.2, mx) > -0.6
        q.img[m] = cm.escurecer(q.img[m], 2)
    # capim no pé das coisas
    x = CAMPO_INI - 20.0
    while x < CAMPO_FIM:
        if not (f1.HANGAR_X - 4 < x < f1.HANGAR_X + 150):
            c = cm.capim(rng.uniform(4, 8), int(x) + 3, folhas=int(rng.integers(3, 6)))
            q.colar(c, x, yc - c.h + 2)
        x += rng.uniform(22, 56)
    # hangar, com a hélice de reserva encostada e os pneus do lado
    hg = hangar(sem=4)
    q.sombra(f1.HANGAR_X + hg.w / 2 + 6, yc + 1, hg.w * 1.05, 3.5)
    q.colar(hg, f1.HANGAR_X, y(CH) - hg.h + 1)
    q.assentar(helice(46), f1.HANGAR_X - 8, yc, afundar=1)
    q.assentar(pneus(3, 1), f1.HANGAR_X + hg.w + 2, yc, afundar=1)
    # balizas da pista
    for x in range(5110, 5560, 96):
        q.assentar(baliza(x), x, yc, afundar=3)
    # tanque de gasolina, trincheira e cerca de arame
    q.assentar(tanque(2), 5594, yc, afundar=1)
    amb = lambda t: ambientar(t.imagem())  # noqa: E731
    q.assentar(amb(f1.sacos_detalhados(4, 3, 4)), 5700 - 3, yc, afundar=3)
    q.assentar(amb(f1.cerca_farpada(84, 6)), 5890, yc)
    for x in (5150, 5772, 5948):
        q.assentar(cm.xiquexique(int(rng.integers(22, 30)), int(rng.integers(16, 22)), sem=x), x, yc, afundar=2)
    q.assentar(cm.pedra(22, 12, sem=95), 5520, yc, afundar=2)
    # a passagem para o rio seco: o chão novo some em manchas sobre o antigo
    ini = CAMPO_FIM
    corte = np.clip((CAMPO_FIM + 60 - q.xx) / (CAMPO_FIM + 60 - ini), 0, 1) + 0.25 * ruido(alt, q.w, 3, 299)
    q.a &= (corte > 0.5) | (q.xx < ini)
    return q


if __name__ == "__main__":
    import sys
    out = sys.argv[1]
    pecas = [hangar(), tanque(), caixa_dagua(), mastro_radio(), baliza(), pneus(), helice(),
             hangar(118, 92, 22, 9, sem=11, nome=None, estrela=False, dentro=False)]
    W = sum(p.w + 6 for p in pecas)
    Hm = max(p.h for p in pecas)
    im = Image.new("RGBA", (W, Hm), (255, 0, 255, 255))
    x = 0
    for p in pecas:
        im.alpha_composite(Image.fromarray(p.rgba(), "RGBA"), (x, Hm - p.h))
        x += p.w + 6
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(out)
