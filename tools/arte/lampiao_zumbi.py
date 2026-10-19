"""Lampião zumbi (fase 2): o vômito do soldado contaminado acertou e ele virou zumbi,
como no Metal Slug 3. Pele verde com veias roxas, óculos rachados com o olho aceso por
trás, boca mole babando, braços esticados para a frente e corpo curvado.

Quadros (60x72, pé em 14,63): parado, anda1-4, pulo, golfada (o tiro dele).
Usa os blocos de tools/arte/lampiao_px.py e lampiao_armas.py.
Gera a folha assets/sprites/lampiao_zumbi.png (chamado por exportar.py).
Também desenha a golfada grande (o projétil) em golfada(k).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import lampiao_armas as la  # noqa: E402
import lampiao_px as lp  # noqa: E402
import pixel  # noqa: E402
from motor import IDX, VAZIO, Tela  # noqa: E402
from aliens import relevo, domo  # noqa: E402

QUADROS = ["parado", "anda1", "anda2", "anda3", "anda4", "pulo", "golfada"]
PERNAS = {"parado": "parado", "anda1": "corre2", "anda2": "corre3", "anda3": "corre5", "anda4": "corre6",
          "pulo": "pulo", "golfada": "parado"}
# Pele (tons 1-7 da legenda) vira verde doente com sombra roxa.
PELE = {"1": "(", "2": "8", "3": "9", "4": "0", "5": "!", "6": "?", "7": "?"}
GOSMA = ["alien_profundo", "alien_esc", "alien", "alien_luz", "alien_brilho"]


def rosto(boca="mole"):
    """Rosto de zumbi a partir do 'grito': lente rachada, olho aceso, boca mole."""
    r = [l for l in lp.ROSTOS["grito"]]
    # Linha do olho: lente rachada (O no meio) e olho verde aceso atrás dela.
    r[3] = r[3].replace("OOBWBO", "O(**?O")
    r[4] = r[4].replace("OBKBO", "O?*(O")
    if boca == "mole":
        # Boca caída e torta, dentes de baixo, língua roxa pendurada e baba.
        r[8] = ".....O3445OOOWWWO..."
        r[9] = "......O334O)]))O...."
        r[10] = ".......O23O))?O....."
        r[11] = "........OOOO?OO....."
    elif boca == "golfada":
        r[8] = ".....O3445OWWWWWO..."
        r[9] = "......O334O!??!!!O.."
        r[10] = ".......O23O?*?!!O..."
        r[11] = "........OOOO!!OO...."
    return r


def olho_saltado(t, lx, ly, ox, oy):
    """Olho que saltou da lente: nervo grosso em curva (vermelho com brilho), bola úmida
    com veias, íris verde em anéis, pupila, reflexo, sangue pingando e a órbita vazia."""
    # Órbita vazia atrás da lente: buraco escuro com borda de sangue.
    t.chapado(t.elipse(lx, ly, 1.2, 1.0), "preto")
    t.ponto(lx - 1, ly + 1, "vermelho_esc")
    # Nervo em curva com duas espessuras.
    pts = []
    for s_ in np.linspace(0, 1, 14):
        x = lx + (ox - lx) * s_ + np.sin(s_ * 3.1) * 1.4
        y = ly + (oy - 2.6 - ly) * s_ - np.sin(s_ * 3.1) * 0.6
        pts.append((x, y))
    for (x, y) in pts:
        t.ponto(x, y + 0.6, "vermelho_esc")
    for (x, y) in pts:
        t.ponto(x, y, "vermelho")
    for (x, y) in pts[2:9:3]:
        t.ponto(x, y - 0.4, "rosa_poeira")
    # Bola do olho com contorno escuro.
    r = 2.8
    fora = t.elipse(ox, oy, r + 0.8, r + 0.8)
    t.chapado(fora, "sombra")
    bola = t.elipse(ox, oy, r, r)
    relevo(t, bola, domo(t, ox, oy, r, r) * 3, ["cinza_medio", "cinza", "cinza_luz", "cinza_claro", "branco", "branco"],
           ambiente=0.3, brilho=1.2, linha=False)
    # Veias vermelhas da borda para a íris.
    for (a, b) in ((ox - r + 0.4, oy - 1), (ox - r + 0.6, oy + 1.2), (ox - 0.5, oy + r - 0.4), (ox + 0.3, oy - r + 0.4)):
        t.linha(a, b, a + (ox + 0.8 - a) * 0.45, b + (oy - b) * 0.45, "vermelho_medio")
    # Íris verde em anéis olhando para a frente, pupila e reflexo.
    ix, iy = ox + 1.0, oy + 0.2
    t.chapado(t.elipse(ix, iy, 1.6, 1.7) & bola, "alien_esc")
    t.chapado(t.elipse(ix, iy, 1.2, 1.3) & bola, "alien")
    t.chapado(t.elipse(ix + 0.2, iy, 0.6, 0.8) & bola, "preto")
    t.ponto(ox - 1.0, oy - 1.2, "branco")
    t.ponto(ox - 0.4, oy - 1.6, "branco")
    # Sangue pingando de baixo do olho.
    t.linha(ox - 0.5, oy + r + 0.6, ox - 0.5, oy + r + 2.2, "vermelho_medio")
    t.ponto(ox - 0.5, oy + r + 3, "vermelho")


def quadro(nome):
    pernas = PERNAS[nome]
    g, dy, _ = la.base(pernas)
    # Braço de trás esticado para a frente (vai antes do tronco).
    alto = nome == "pulo"
    oy = -3 if alto else 0
    la.braco(g, (la.OMBRO_TRAS[0], la.OMBRO_TRAS[1] + dy), (18, 25 + dy + oy), (26, 25 + dy + oy * 2), escurecer=1)
    # Corpo curvado: cabeça um pouco para a frente e para baixo.
    baixa = 2 if nome == "golfada" else 1
    for y, x, txt in lp.TRONCO:
        lp.pintar(g, y + dy, x, txt)
    for k, txt in enumerate(rosto("golfada" if nome == "golfada" else "mole")):
        lp.pintar(g, 8 + k + dy + baixa, 7 + baixa, txt)
    for k, txt in enumerate(lp.CHAPEU):
        lp.pintar(g, 1 + k + dy + baixa, 4 + baixa, txt)
    la._CORPO = [l[:] for l in g]
    # Braço da frente esticado, mão mole caída.
    mx, my = (29, 24 + dy + oy * 2) if nome != "golfada" else (27, 30 + dy)
    la.braco(g, (la.OMBRO_FRENTE[0], la.OMBRO_FRENTE[1] + dy), (23, 24 + dy + oy), (mx, my))
    for (hx, hy) in ((mx, my), (26, 25 + dy + oy * 2)):
        for k, l in enumerate(["O45O", "O3455O", ".O34O3O", "..OO.O"]):
            lp.pintar(g, hy - 1 + k, hx - 1, l)
    t = la._fim(g)
    # Pele verde.
    tab = {IDX[pixel.LEGENDA[a]]: IDX[pixel.LEGENDA[b]] for a, b in PELE.items()}
    px = t.px.copy()
    for a, b in tab.items():
        px[t.px == a] = b
    t.px = px
    # Veias roxas no rosto e na mão, baba escorrendo do queixo.
    for (x, y) in ((13, 16), (13, 17), (12, 18), (14, 20), (15, 21)):
        if t.px[y + dy + baixa, x] in (IDX["alien_medio"], IDX["alien"]):
            t.px[y + dy + baixa, x] = IDX["roxo"]
    if nome != "golfada":
        bx, by = 20 + baixa, 19 + dy + baixa
        t.linha(bx, by, bx, by + 3 + (nome == "anda2"), "alien_luz")
        t.ponto(bx, by + 4 + (nome == "anda2"), "alien_brilho")
    else:
        # Golfada saindo: jato grosso para a frente (o projétil grande sai no jogo).
        jato = golfada(1, W=30, H=18)
        jato.px[:, :3] = VAZIO
        t.colar(jato, 21, 11 + dy + baixa)
    ey = 11 + dy + baixa  # linha do olho
    balanca = {"anda1": 1, "anda3": -1, "pulo": -2}.get(nome, 0)
    corpo = t.px != VAZIO
    # Pele descascando: placas em carne viva na bochecha, na testa e nas mãos.
    for (x, y, rx, ry) in ((11.5, ey + 3.5, 2.2, 1.6), (15.5, ey - 2, 1.6, 0.9), (mx + 1, my + 1, 1.2, 0.9)):
        m = t.elipse(x, y, rx, ry) & corpo
        t.chapado(m, "vermelho_medio")
        t.chapado(m & t.elipse(x + 0.3, y + 0.3, rx * 0.55, ry * 0.55), "rosa_poeira")
        t.ponto(x - rx * 0.4, y - ry * 0.3, "pele_brilho")
        borda = m & ~np.roll(m, 1, 0)
        t.px[borda] = IDX["alien_luz"]
    # Olho saltado da lente rachada, pendurado pelo nervo e balançando.
    ox, oy_ = 26.5 + baixa + balanca * 0.6, ey + 5
    if nome == "golfada":
        ox, oy_ = 21 + baixa, ey + 9
    olho_saltado(t, 21 + baixa, ey + 1, ox, oy_)
    # Furo de bala no chapéu, com a aba rasgada.
    hx_, hy_ = 9 + baixa, 4 + dy + baixa
    t.chapado(t.elipse(hx_, hy_, 1.2, 1.0) & corpo, "couro_profundo")
    t.ponto(hx_ + 1, hy_ - 1, "couro_claro")
    # Camisa rasgada no peito mostrando as costelas.
    cy = 28 + dy
    rasgo = (t.elipse(13, cy, 3.0, 2.3) | t.elipse(11.5, cy + 1.5, 1.8, 1.4)) & corpo
    t.chapado(rasgo, "vermelho_esc")
    t.chapado(rasgo & t.elipse(13.2, cy + 0.4, 2.0, 1.4), "roxo_escuro")
    for k_, y in enumerate((cy - 1, cy + 0.6, cy + 2)):
        for x in np.arange(10.5, 16, 0.5):
            yy = int(y + (x - 13) * 0.15)
            if rasgo[yy, int(x)]:
                t.px[yy, int(x)] = IDX["cinza_claro"] if x < 13.5 else IDX["cinza_luz"]
    borda = rasgo & ~np.roll(rasgo, -1, 1)
    t.px[borda] = IDX["areia_luz"]
    # Manchas de vômito na camisa.
    for (x, y) in ((14, 27), (15, 28), (12, 30), (17, 31)):
        if t.px[y + dy, x] != VAZIO:
            t.px[y + dy, x] = IDX["alien"]
    return t


def folha():
    return [quadro(n) for n in QUADROS]


BILE = ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz", "alien_brilho", "amarelo_claro"]


def golfada(k, W=64, H=32):
    """Golfada grande do Lampião zumbi (o projétil), no nível do Metal Slug: onda grossa
    de vômito que engrossa na frente, com núcleo translúcido, brilho molhado em cada gomo,
    bolhas, pedaços (cuscuz, osso, dente), um olho boiando, fios pingando por baixo e
    respingos voando na frente. k: quadro (0-2) da ondulação."""
    t = Tela(W, H)
    fase = k * 2.1
    cy = H * 0.5
    # Corpo: gomos do rabo fino até a cabeça grossa da onda.
    gomos = []
    n = 10
    for i in range(n):
        s_ = i / (n - 1)
        x = 5 + s_ * (W - 18)
        y = cy - 1 + np.sin(i * 1.1 + fase) * 1.6 - s_ * 1.5
        r = 1.2 + H * 0.03 + s_ ** 1.4 * H * 0.22 + np.sin(i * 2.3 + fase) * 0.5
        gomos.append((x, y, r))
    m = np.zeros((H, W), bool)
    for (x, y, r) in gomos:
        m |= t.elipse(x, y, r * 1.15, r)
    # Cada gomo é uma bola molhada: luz de cima à esquerda, sombra embaixo (como o tumor).
    RAMPA = BILE[:6]
    alturas = np.stack([domo(t, x, y, r * 1.15, r) * r for (x, y, r) in gomos])
    dono = alturas.argmax(0)
    nivel = np.zeros((H, W), int)
    for i, (x, y, r) in enumerate(gomos):
        hx, hy = x - r * 0.4, y - r * 0.45
        d = np.hypot((t.xx - hx) / (r * 1.15), (t.yy - hy) / r)
        v = np.clip(1.0 - d / 1.45, 0, 0.999)
        aqui = m & (dono == i)
        nivel[aqui] = (v[aqui] * len(RAMPA)).astype(int)
    t.px[m] = np.array([IDX[c] for c in RAMPA])[nivel[m]]
    # Dobra escura entre gomos vizinhos.
    ordem = np.sort(alturas, axis=0)
    t.px[m & (ordem[-2] > 0.6) & (ordem[-1] - ordem[-2] < 0.5)] = IDX["alien_esc"]
    # Núcleo translúcido mais claro e amarelado (bile) no meio da onda.
    for (x, y, r) in gomos[5::2]:
        nucleo = t.elipse(x + r * 0.1, y + r * 0.2, r * 0.45, r * 0.28) & m
        t.px[nucleo & (t.px != IDX["alien_brilho"])] = IDX["alien"]
    for (x, y, r) in gomos[6:]:
        t.chapado(t.elipse(x, y + r * 0.2, r * 0.25, r * 0.15) & m, "amarelo_claro")
    # Sombra embaixo da onda (mais denso).
    baixo = m & ~np.roll(m, -2, 0)
    t.px[baixo] = IDX["alien_esc"]
    # Reflexo branco no alto de cada gomo grande.
    for (x, y, r) in gomos[3:]:
        t.ponto(x - r * 0.45, y - r * 0.6, "branco")
        if r > 5:
            t.ponto(x - r * 0.45 + 1, y - r * 0.6, "alien_brilho")
            t.ponto(x - r * 0.3, y - r * 0.75, "branco")
    # Bolhas com aro claro.
    rng = np.random.default_rng(11 + k)
    for (x, y, r) in ((W * 0.37, cy - 3, 1.3), (W * 0.56, cy + 2, 1.0), (W * 0.69, cy - 4, 1.5), (W * 0.47, cy + 4, 0.8), (W * 0.78, cy + 1, 1.1)):
        x += np.sin(fase + x) * 0.6
        bolha = t.elipse(x, y, r, r) & m
        aro = bolha & ~t.elipse(x, y, r - 0.6, r - 0.6)
        t.px[aro] = IDX["alien_brilho"]
        t.px[bolha & ~aro] = IDX["alien_medio"]
        t.ponto(x - r * 0.4, y - r * 0.4, "branco")
    # Pedaços boiando: cuscuz, um ossinho e um dente.
    for (x, y) in ((W * 0.25, cy), (W * 0.42, cy - 1), (W * 0.6, cy + 3), (W * 0.73, cy - 2)):
        x += np.sin(fase + y) * 0.7
        t.chapado(t.elipse(x, y, 1.1, 0.8), "amarelo_fogo")
        t.ponto(x - 0.4, y - 0.4, "amarelo_claro")
        t.ponto(x + 0.6, y + 0.4, "couro")
    if W > 40:
        t.linha(33, cy + 5, 36, cy + 4, "cinza_claro")
        t.ponto(32.5, cy + 5, "branco")
        t.ponto(36.5, cy + 3.6, "branco")
        t.chapado(t.retangulo(21, cy + 2, 2, 2), "branco")
        t.ponto(21, cy + 3, "cinza_luz")
    # Olho boiando perto da frente, girando com a onda.
    ex, ey = W - 17, cy - 2 + np.sin(fase) * 1.0
    if W < 40:
        ex = -99
    t.chapado(t.elipse(ex, ey, 2.6, 2.5), "alien_profundo")
    t.chapado(t.elipse(ex, ey, 2.0, 2.0), "branco")
    t.chapado(t.elipse(ex + 0.8 * np.cos(fase), ey + 0.5, 1.0, 1.1), "vermelho_medio")
    t.ponto(ex + 0.9 * np.cos(fase), ey + 0.5, "preto")
    t.linha(ex - 2, ey + 1, ex - 4, ey + 3, "vermelho_medio")
    # Fios pingando por baixo, com gota na ponta (crescem a cada quadro).
    for i, x in enumerate(int(W * f) for f in (0.22, 0.36, 0.48, 0.62, 0.73)):
        col = np.where(m[:, x])[0]
        if not len(col):
            continue
        y0 = col.max() + 1
        L = 1 + (i + k) % 3 + (i % 2)
        t.linha(x, y0, x, y0 + L, "alien_medio")
        t.ponto(x, y0 + L + 1, "alien_luz")
        t.ponto(x - 1, y0 + L + 1, "alien_esc")
    # Respingos voando na frente e por cima (com contorno, como gotas).
    for _ in range(9):
        x = rng.uniform(max(0, W - 16), W - 1)
        y = rng.uniform(2, H - 3)
        if not m[int(y), int(x)]:
            t.chapado(t.elipse(x, y, 0.9, 0.7), "alien_luz")
            t.ponto(x - 0.3, y - 0.3, "alien_brilho")
    for _ in range(6):
        x, y = rng.uniform(2, max(3, W - 20)), rng.uniform(0, 4)
        t.ponto(x, y, "alien")
    t.contorno("alien_profundo")
    return t


def gota(k, w=14, h=12, semente=0):
    """Gota grossa de vômito para o jato (como o do Metal Slug 3): bola molhada que
    estica e encolhe a cada quadro, com reflexo branco, miolo amarelado de bile, um
    pedaço boiando, a cauda pingando para trás e respingos em volta."""
    t = Tela(w, h)
    cx, cy = w * 0.58, h * 0.5
    estica = (1.0, 1.18, 0.88)[k % 3]
    rx, ry = w * 0.3 * estica, h * 0.34 / estica
    corpo = t.elipse(cx, cy, rx, ry)
    cauda = t.capsula(cx - rx * 0.6, cy + 0.3, cx - rx * 1.6, cy + (0.8, 0.2, 1.2)[k % 3], ry * 0.55, ry * 0.25)
    m = corpo | cauda
    hx, hy = cx - rx * 0.35, cy - ry * 0.45
    d = np.hypot((t.xx - hx) / (rx * 1.1), (t.yy - hy) / (ry * 1.1))
    v = np.clip(1.0 - d / 1.5, 0, 0.999)
    rampa = ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz"]
    n = (v * len(rampa)).astype(int)
    t.px[m] = np.array([IDX[c] for c in rampa])[n[m]]
    t.chapado(t.elipse(cx + rx * 0.15, cy + ry * 0.2, rx * 0.45, ry * 0.35) & corpo, "amarelo_claro" if k % 2 else "alien_brilho")
    t.ponto(hx, hy, "branco")
    t.ponto(hx + 1, hy, "alien_brilho")
    t.ponto(cx + rx * 0.3, cy + ry * 0.1, "couro")
    rng = np.random.default_rng(semente + k)
    for _ in range(3):
        x, y = rng.uniform(0, w * 0.4), rng.uniform(0, h)
        if not m[int(y), int(x)]:
            t.ponto(x, y, "alien_luz")
    t.contorno("alien_profundo")
    return t


if __name__ == "__main__":
    from PIL import Image
    from motor import RAIZ
    lamp = Image.open(RAIZ / "assets/sprites/lampiao.png").crop((0, 0, 60, 72))
    ims = [lamp] + [q.imagem() for q in folha()] + [golfada(k).imagem() for k in range(3)]
    W = sum(i.width for i in ims) + 6 * len(ims)
    o = Image.new("RGBA", (W, 76), (176, 142, 102, 255))
    x = 0
    for i in ims:
        o.alpha_composite(i, (x, 76 - i.height - 2))
        x += i.width + 6
    saida = sys.argv[1] if len(sys.argv) > 1 else RAIZ / "tools/arte/pixel/zumbi_previa.png"
    o.resize((W * 3, 76 * 3), Image.NEAREST).save(saida)
    print(saida)
