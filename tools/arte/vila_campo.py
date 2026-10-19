"""Trechos novos da fase 1 (lote de 18/10):

- Vila alta: casario de platibanda (fachadas coloridas e desbotadas, uma
  colada na outra) com telhados por onde dá para seguir por cima, toldo de
  bodega e sacada servindo de degrau. Caminho por cima ou pela rua.
- Campo de pouso da Aviação Militar: hangar de tábuas com telhado de zinco
  arqueado, marcas de pneu na pista, balizas e o depósito de gasolina.
- Segredos que soltam prêmio quando levam tiro: cacimba (refém escondido),
  ninho de galinha no telhado (arma) e a canoa do rio seco (buchada).
Usado por tools/arte/fase1.py e tools/arte/exportar.py.
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from motor import CORES, IDX, VAZIO, Tela, BAYER4  # noqa: E402
import fase1 as f  # noqa: E402


def _lum(nome):
    c = CORES[nome]
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return 0.3 * r + 0.59 * g + 0.11 * b


def rampa(*nomes):
    """Rampa do escuro para o claro (ordena pela luminosidade)."""
    return sorted(nomes, key=_lum)


# Cores de fachada do sertão, desbotadas pelo sol.
FACHADAS = {
    "azul": rampa("azul_sombra", "azul_medio", "ceu_medio", "ceu", "ceu_claro"),
    "rosa": rampa("vermelho_esc", "vermelho_medio", "rosa_poeira", "pele_luz", "pele_brilho"),
    "ocre": rampa("terra", "barro", "ouro_escuro", "areia_media", "areia", "areia_luz"),
    "verde": rampa("caatinga_esc", "caatinga_media", "caatinga", "mandacaru", "mandacaru_luz"),
    "cal": rampa("cinza_medio", "cinza", "cinza_luz", "cinza_claro", "branco"),
}
# Cor das esquadrias (portas e janelas pintadas) que combina com cada fachada.
ESQUADRIA = {"azul": "verde", "rosa": "azul", "ocre": "verde", "verde": "madeira", "cal": "azul"}
PINTURA = {
    "verde": rampa("sombra", "caatinga_esc", "caatinga_media", "caatinga"),
    "azul": rampa("sombra", "azul_sombra", "azul_medio", "ceu_medio"),
    "madeira": rampa("marrom_noite", "couro_profundo", "couro_escuro", "couro", "couro_medio"),
}
ZINCO = rampa("sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro")
FERRUGEM = ["couro_profundo", "couro_escuro", "laranja_escuro"]
PEDRA = f.PEDRA
LONA = rampa("vermelho_esc", "vermelho_medio", "vermelho")
LONA_CLARA = rampa("areia_media", "areia_luz", "areia_clara")

PLATIBANDA = 12  # altura da platibanda: o topo dela é onde se anda


def adobe_caido(t, parede, semente, acima=0):
    """Reboco caído em manchas mostrando os tijolos de adobe com junta."""
    h, w = parede.shape
    caido = (f.ruido(h, w, 3.0, semente + 1) > 1.45) & parede & (t.yy > acima)
    xi = t.xx.astype(int)
    yi = t.yy.astype(int)
    fila = yi // 4
    junta = ((yi % 4) == 0) | (((xi + (fila % 2) * 4) % 8) == 0)
    tons = np.array([IDX["barro"], IDX["terra_media"], IDX["areia_media"], IDX["terra"]])
    tijolo = tons[((xi + (fila % 2) * 4) // 8 * 7 + fila * 3) % 4]
    t.px[caido] = tijolo[caido]
    t.px[caido & junta] = IDX["terra_escura"]
    borda = ndimage.binary_dilation(caido) & ~caido & parede
    t.px[borda] = IDX["areia_luz"]
    sob = ndimage.binary_dilation(caido) & ~caido & parede & np.roll(caido, 1, 0)
    t.px[sob] = IDX["terra"]


def esquadria(t, x, y, w, h, cor, semente, tipo="porta", aberta=False):
    """Porta de duas folhas com bandeira em arco, ou janela de veneziana."""
    pint = PINTURA[cor]
    if tipo == "porta":
        arco = t.elipse(x + w / 2, y + w / 2, w / 2, w / 2) & (t.yy < y + w / 2)
        vao = t.retangulo(x, y + w / 2, w, h - w / 2) | arco
        t.chapado(vao, "marrom_noite")
        # Bandeira de vidro em leque.
        t.chapado(arco, "azul_sombra")
        for k in range(3):
            a = math.pi * (0.25 + k * 0.25)
            t.linha(x + w / 2, y + w / 2, x + w / 2 + math.cos(a) * w / 2, y + w / 2 - math.sin(a) * w / 2, "sombra")
        t.chapado(t.retangulo(x, y + w / 2, w, 1), "sombra")
        if aberta:
            folha = f.tabuas(max(3, int(w * 0.3)), int(h - w / 2 - 1), vertical=True, semente=semente, rampa=pint)
            f.colar(t, folha, x, y + w / 2 + 1)
        else:
            for lado in (0, 1):
                fx = x + lado * w / 2
                fol = t.retangulo(fx + 0.5, y + w / 2 + 1, w / 2 - 1, h - w / 2 - 1)
                t.volume(fol, pint, achatado=1.2, suave=0.4, ambiente=0.3)
                for yy in (y + w / 2 + 4, y + h - 8):
                    t.chapado(t.retangulo(fx + 1.5, yy, w / 2 - 3, 4) & fol, pint[0])
            t.ponto(x + w / 2 + 1, y + h * 0.6, "amarelo_fogo")
    else:
        t.chapado(t.retangulo(x - 1, y - 1, w + 2, h + 2), "sombra")
        for lado in (0, 1):
            fx = x + lado * w / 2
            fol = t.retangulo(fx, y, w / 2, h)
            t.volume(fol, pint, achatado=1, suave=0.3, ambiente=0.3)
            for yy in range(int(y) + 2, int(y + h) - 1, 2):
                t.linha(fx + 1, yy, fx + w / 2 - 1, yy, pint[0])
        t.chapado(t.retangulo(x - 2, y + h + 1, w + 4, 2), "cinza_luz")  # peitoril
        t.chapado(t.retangulo(x - 2, y + h + 3, w + 4, 1), "sombra")


def sobrado(w, h, cor="azul", semente=0, sacada=False, frontao=True):
    """Casa de platibanda colada nas vizinhas: o topo da platibanda é chão (telhado
    por onde o Lampião anda). Fachada pintada desbotando, barra suja embaixo,
    cornija, reboco caído mostrando adobe, portas com bandeira e janelas."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    cores = FACHADAS[cor]
    parede = t.retangulo(1, PLATIBANDA - 2, w - 2, h - PLATIBANDA + 2)
    t.volume(parede, cores, achatado=3, suave=1.0, ambiente=0.45, textura=0.05, semente=semente, luz=(-0.3, -0.9))
    # Pintura lisa (sem granulado), como a caiação da capela.
    moda = ndimage.generic_filter(t.px, lambda v: np.bincount(v.astype(int) + 1).argmax() - 1, size=3)
    t.px[parede] = moda[parede]
    # Desbotado em manchas mais claras (sol) e pintura velha descascando.
    clara = (f.ruido(h, w, 4.0, semente + 9) > 1.0) & parede
    sobe = {IDX[a]: IDX[b] for a, b in zip(cores[:-1], cores[1:])}
    t.px[clara] = np.vectorize(lambda v: sobe.get(int(v), int(v)))(t.px[clara])
    adobe_caido(t, parede, semente, acima=PLATIBANDA + 8)
    # Barra pintada de outra cor embaixo (até a cintura), suja de terra.
    barra = parede & (t.yy > h - 14)
    esc = FACHADAS["ocre" if cor != "ocre" else "verde"]
    t.volume(barra, esc[:4], achatado=1.5, suave=0.6, ambiente=0.25, textura=0.08, semente=semente + 3)
    t.chapado(t.retangulo(1, h - 15, w - 2, 1), "sombra")
    # Platibanda: faixa com moldura em cima (cornija saliente) e frisos.
    plat = t.retangulo(0, 0, w, PLATIBANDA)
    t.volume(plat, cores, achatado=2, suave=0.6, ambiente=0.5, luz=(-0.3, -0.9))
    t.chapado(t.retangulo(0, 0, w, 2), cores[-1])  # topo pegando sol
    t.chapado(t.retangulo(0, 2, w, 1), cores[1])
    t.chapado(t.retangulo(0, PLATIBANDA - 3, w, 2), cores[-2])  # cornija
    t.chapado(t.retangulo(0, PLATIBANDA - 1, w, 1), "sombra")
    # Almofadas em relevo na platibanda.
    n = max(2, w // 26)
    for k in range(n):
        ax = 4 + k * (w - 8) / n
        aw = (w - 8) / n - 4
        t.chapado(t.retangulo(ax, 4, aw, 4), cores[1])
        t.chapado(t.retangulo(ax + 1, 4, aw - 1, 1), cores[0])
    # Pináculos nos cantos.
    for px_ in (2, w - 4):
        t.chapado(t.retangulo(px_, 0, 2, 2), cores[-1])
    # Portas e janelas.
    cor_e = ESQUADRIA[cor]
    n_vaos = max(2, int(w // 34))
    passo = w / n_vaos
    for k in range(n_vaos):
        cx = passo * (k + 0.5)
        if k % 2 == 0 or n_vaos == 2 and k == 0:
            pw, ph = 14, min(40, h - PLATIBANDA - 10)
            esquadria(t, cx - pw / 2, h - ph - 1, pw, ph, cor_e, semente + k, "porta", aberta=rng.random() < 0.35)
        else:
            jw, jh = 12, 14
            esquadria(t, cx - jw / 2, h - 38, jw, jh, cor_e, semente + k, "janela")
        if h > 96:
            # Andar de cima: janelas de sacada.
            jw, jh = 10, 16
            esquadria(t, cx - jw / 2, PLATIBANDA + 8, jw, jh, cor_e, semente + 30 + k, "janela")
    if sacada:
        # Sacada de ferro batido no andar de cima (dá para pisar).
        sy = PLATIBANDA + 26
        t.chapado(t.retangulo(6, sy, w - 12, 3), "cinza_escuro")
        t.chapado(t.retangulo(6, sy, w - 12, 1), "cinza_luz")
        for x in range(8, w - 8, 3):
            t.linha(x, sy - 8, x, sy - 1, "sombra")
        t.chapado(t.retangulo(6, sy - 9, w - 12, 1.5), "sombra")
        for x in range(10, w - 10, 12):
            t.linha(x, sy + 3, x + 3, sy + 7, "sombra")  # mão-francesa
    # Fios de rachadura e escorridos de água da platibanda.
    for _ in range(3):
        x, y = rng.uniform(6, w - 6), rng.uniform(PLATIBANDA + 2, h - 20)
        for kk in range(9):
            x += rng.uniform(-1.2, 1.2)
            y += 1
            if 0 <= int(y) < h and parede[int(y), int(x)]:
                t.px[int(y), int(x)] = f.ESCURO[t.px[int(y), int(x)]]
    f.envelhecer(t, parede, PLATIBANDA, semente)
    t.contorno("sombra")
    return t


def sacada_y(h):
    """y (no desenho) do piso da sacada de um sobrado de altura h."""
    return PLATIBANDA + 26


def toldo(w=60, alt=42, semente=0):
    """Toldo de lona listrada da bodega, inclinado, com duas varas até o chão.
    O topo do toldo (y=0..3) serve de plataforma."""
    t = Tela(w, alt)
    lona = t.poligono([(0, 0), (w, 0), (w, 8), (0, 5)])
    xi = t.xx.astype(int)
    for k, r in enumerate((LONA, LONA_CLARA)):
        m = lona & (((xi // 6) % 2) == k)
        t.volume(m, r, achatado=1, suave=0.3, ambiente=0.35, linha=False)
    # Bambinela recortada na frente.
    for x in range(0, w, 6):
        t.chapado(t.elipse(x + 3, 8, 3, 2) & (t.yy > 7), "vermelho_esc" if (x // 6) % 2 == 0 else "areia_media")
    for x in (2, w - 4):
        t.volume(t.retangulo(x, 7, 2, alt - 7), f.MADEIRA, achatado=0.8, suave=0.3)
    t.contorno("sombra")
    return t


def hangar(w=150, h=96, semente=0):
    """Hangar de tábuas com telhado de zinco em arco, portão aberto e o escuro lá dentro
    com tambores e ferramentas; ferrugem escorrendo do zinco."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    beiral = 34
    # Paredes de tábua (dos lados do portão).
    parede = t.retangulo(4, beiral - 4, w - 8, h - beiral + 4)
    tab = f.tabuas(w - 8, h - beiral + 4, vertical=True, semente=semente, rampa=f.MADEIRA)
    f.colar(t, tab, 4, beiral - 4)
    # Portão aberto: o escuro de dentro.
    pw = w * 0.62
    px_ = (w - pw) / 2
    vao = t.retangulo(px_, beiral + 2, pw, h - beiral - 2)
    t.chapado(vao, "marrom_noite")
    fundo = vao & (t.yy > h - 20)
    t.chapado(fundo, "preto")
    # Tambores e uma hélice de reserva encostada lá dentro.
    for k in range(3):
        tx = px_ + 6 + k * 9
        t.volume(t.retangulo(tx, h - 16, 8, 15), rampa("sombra", "caatinga_esc", "caatinga_media"), achatado=1.5, suave=0.4,
                 ambiente=0.15)
        t.chapado(t.retangulo(tx, h - 12, 8, 1), "sombra")
    t.volume(t.capsula(px_ + pw - 14, h - 40, px_ + pw - 10, h - 4, 1.4), f.MADEIRA, achatado=1, suave=0.3, ambiente=0.15)
    # Bancada com ferramentas.
    t.chapado(t.retangulo(px_ + pw / 2 - 10, h - 22, 22, 2), "couro_escuro")
    for k in range(4):
        t.ponto(px_ + pw / 2 - 7 + k * 5, h - 24, "cinza")
    # Folhas do portão abertas para os lados (tábuas com travessa em Z).
    for lado in (-1, 1):
        fx = px_ - 10 if lado < 0 else px_ + pw
        fol = f.tabuas(10, int(h - beiral - 2), vertical=True, semente=semente + 5 + lado, rampa=f.MADEIRA)
        f.colar(t, fol, fx, beiral + 2)
        t.linha(fx, h - 6, fx + 9, beiral + 8, "couro_profundo")
    # Telhado de zinco em arco com as ondas da chapa e a ferrugem.
    arco = t.elipse(w / 2, beiral, w / 2, beiral - 2) & (t.yy <= beiral)
    t.volume(arco, ZINCO, achatado=4, suave=1.2, ambiente=0.4, brilho=1.2)
    xi = t.xx.astype(int)
    t.px[arco & ((xi % 4) == 0)] = IDX["cinza_escuro"]
    t.px[arco & ((xi % 4) == 1)] = IDX["cinza_luz"]
    ferr = (f.ruido(h, w, (6, 1.5), semente + 3) > 0.9) & arco
    t.px[ferr] = IDX["couro_escuro"]
    for _ in range(14):
        x = int(rng.integers(6, w - 6))
        y0 = int(rng.integers(beiral - 12, beiral))
        for d in range(int(rng.integers(3, 12))):
            if 0 <= y0 + d < h and t.px[y0 + d, x] != VAZIO:
                t.px[y0 + d, x] = IDX[FERRUGEM[min(2, d // 4)]]
    t.chapado(t.retangulo(0, beiral, w, 2), "sombra")
    # Estrela pintada na empena (a Aviação Militar), meio apagada.
    cx, cy = w / 2, beiral - 14
    est = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        r = 6 if k % 2 == 0 else 2.5
        est.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    estrela = t.poligono(est) & arco
    t.chapado(estrela, "amarelo_fogo")
    t.px[estrela & (f.ruido(h, w, 1.5, 7) > 0.6)] = IDX["ouro_escuro"]
    f.envelhecer(t, parede & ~vao, beiral, semente, escorridos=False)
    t.contorno("sombra")
    return t


def baliza(semente=0):
    """Baliza da pista: tambor pintado de faixas brancas e vermelhas, meio enterrado."""
    t = Tela(12, 12)
    corpo = t.retangulo(1, 2, 10, 10)
    t.volume(corpo, ZINCO, achatado=1.5, suave=0.4, ambiente=0.4)
    for y in (2, 7):
        t.chapado(t.retangulo(1, y, 10, 3) & corpo, "vermelho")
    t.chapado(t.retangulo(1, 2, 10, 1), "cinza_claro")
    t.contorno("sombra")
    return t


def marcas_pneu(t, x0, x1, y, semente=0):
    """Duas trilhas de pneu riscadas na terra da pista."""
    rng = np.random.default_rng(semente)
    for x in range(int(x0), int(x1)):
        for dy in (0, 5):
            if rng.random() < 0.7:
                yy = y + dy + (1 if (x // 23) % 3 == 0 else 0)
                if 0 <= yy < t.h and t.px[yy, x] != VAZIO:
                    t.px[yy, x] = f.ESCURO[t.px[yy, x]]


def tanque_gasolina(semente=0):
    """Depósito de gasolina: tanque cilíndrico deitado sobre cavaletes."""
    t = Tela(64, 34)
    corpo = t.capsula(8, 14, 56, 14, 11)
    t.volume(corpo, rampa("sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru"), achatado=4, suave=1.2,
             ambiente=0.35, textura=0.05, semente=semente)
    for x in (18, 32, 46):
        t.chapado(t.retangulo(x, 3, 1, 22) & corpo, "caatinga_esc")
    t.chapado(t.retangulo(26, 10, 12, 6) & corpo, "areia_clara")  # placa
    t.chapado(t.retangulo(28, 12, 8, 2) & corpo, "vermelho")
    for x in (14, 48):
        t.volume(t.poligono([(x - 5, 33), (x, 22), (x + 5, 33)]), f.MADEIRA, achatado=1, suave=0.3)
    t.contorno("sombra")
    return t


# ---------------------------------------------------------------- segredos
def cacimba(q=0):
    """Cacimba de pedra com sarilho de pau, corda e balde (32x40). q=1: o tiro
    arrebentou a corda e o sarilho (o refém escondido lá dentro sobe)."""
    t = Tela(32, 40)
    boca = t.retangulo(3, 22, 26, 18)
    t.volume(boca, PEDRA, achatado=2, suave=0.7, ambiente=0.35, textura=0.12, semente=4)
    # Pedras do muro, uma a uma.
    for fila in range(3):
        y = 23 + fila * 6
        for k in range(4):
            x = 3 + k * 7 + (3 if fila % 2 else 0)
            t.linha(x, y, x, y + 5, "sombra")
        t.linha(3, y + 5, 28, y + 5, "sombra")
    t.chapado(t.retangulo(3, 22, 26, 2), "cinza_luz")
    t.chapado(t.elipse(16, 22, 11, 1.5), "preto")  # a boca escura
    # Forquilhas e o sarilho.
    for x in (5, 26):
        f.tora(t, x, 22, x + (1 if x < 16 else -1), 4, 1.3, semente=x, pontas=False)
    if q == 0:
        f.tora(t, 6, 6, 26, 6, 1.6, semente=3)
        t.linha(16, 7, 16, 16, "areia_media")
        t.volume(t.retangulo(13, 15, 7, 6), f.MADEIRA, achatado=1, suave=0.3)  # balde
        t.chapado(t.retangulo(13, 15, 7, 1), "cinza")
        t.linha(26, 6, 30, 3, "couro")  # manivela
    else:
        f.tora(t, 6, 8, 18, 3, 1.6, semente=3)  # sarilho caído torto
        t.linha(20, 9, 21, 22, "areia_media")
        t.volume(t.retangulo(18, 34, 8, 6), f.MADEIRA, achatado=1, suave=0.3)  # balde no chão
    t.contorno("sombra")
    return t


def ninho(q=0):
    """Ninho de palha na quina do telhado (24x16). q=0 com a galinha choca; q=1 vazio."""
    import fase1_extra as fx
    t = Tela(24, 16)
    palha = t.elipse(12, 13, 10, 3.5)
    t.volume(palha, rampa("terra", "barro", "areia_media", "areia", "areia_luz"), achatado=1.5, suave=0.4,
             ambiente=0.4, textura=0.2, semente=2)
    for x in range(3, 22, 2):
        t.linha(x, 11, x + 1, 15, "terra")
    if q == 0:
        g = fx.galinha(0)
        f.colar(t, g, 12 - g.w / 2, 12 - g.h)
    else:
        t.chapado(t.elipse(9, 11, 1.6, 1.2), "branco")  # um ovo que sobrou
    t.contorno("sombra")
    return t


def canoa(q=0):
    """A canoa encalhada do rio seco como segredo: q=1 arrebentada (debaixo dela, a buchada)."""
    import fase1_extra as fx
    c = fx.canoa()
    if q == 0:
        return c
    t = Tela(c.w, c.h)
    t.px = c.px.copy()
    rng = np.random.default_rng(5)
    for _ in range(5):
        x, y = rng.integers(6, c.w - 6), rng.integers(2, c.h - 2)
        t.chapado(t.elipse(x, y, rng.uniform(2, 4), rng.uniform(1.5, 3)) & (t.px != VAZIO), "marrom_noite")
    meio = t.xx > c.w * 0.45
    t.px[meio & (t.xx < c.w * 0.5)] = VAZIO  # partida ao meio
    return t
