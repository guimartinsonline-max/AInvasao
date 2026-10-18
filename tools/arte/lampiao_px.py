"""Lampião pixel a pixel, no estilo Metal Slug: base agachada, inclinado para a
frente, rosto expressivo. Gera tools/arte/pixel/lampiao.txt (a fonte editável).

Cada desenho é montado por blocos: cabeça (com expressão), tronco/braço/arma
(com pose) e pernas (com pose). As coordenadas são do quadro final.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pixel  # noqa: E402

# Quadro folgado: as armas compridas (e o cano apontado para o céu) não saem cortadas.
W, H = 60, 72
MARGEM = 22  # espaço em cima para a arma apontada para o céu

# ---------------------------------------------------------------- cabeça
# Bloco de 20 colunas colocado em x=6. Chapéu de couro em meia-lua.
CHAPEU = [  # 24 colunas, colocado em x=3: meia-lua com as pontas para cima
    ".OO.................OOO.",
    ".OhO.....OOOOO.....OhgO.",
    ".OhgO..OOgghhgOO..OhgfO.",
    "..OgfOOgghhhhhggOOhgAfO.",
    "..OgffgghhhhhhhggfgAHAdO",
    "...OsffddAdddAddddffAdsO",
    "....OOsssssssssssssssOO.",
    "......OOOOOOOOOOOOOOO...",
]
# Cabelo do Lampião, para quando o chapéu voa (morte): cabeleira preta comprida
# de cangaceiro com brilho, testa de fora. 20 colunas em x=7, linhas 3 a 7 (o rosto começa na 8).
CABELO = [
    "......OOOOOOOO......",
    "....OOKKKxxKKKOO....",
    "...OKKKKxKKKxKKKO...",
    "..OKKKKKKKKKK33KKO..",
    "..OKKKKK3445555KO...",
]
# Mecha caindo atrás da nuca, por cima do pescoço (linhas 8 a 12, coluna 4).
MECHA = ["OKO", "OKKO", "OKKO", ".OKO", "..O"]

ROSTOS = {  # 20 colunas, colocado em x=7, começando na linha 7
    # Bravo, gritando (ação).
    "grito": [
        "....OKK3445555556O..",
        "....OKK3445KKKK66O..",
        "....OK32455OOOOK66O.",
        "....OK2345OOBWBO67O.",
        "....O323455OBKBO666O",
        "....O3344555OOO5665O",
        "....O4445555554KK32O",
        "....O3445555KKKKKKO.",
        ".....O3445OWWWWWO...",
        "......O334ORTTTRO...",
        ".......O23OWWWWO....",
        "........OOOOOOO.....",
    ],
    # Durão, boca fechada (parado).
    "serio": [
        "....OKK3445555556O..",
        "....OKK3445KKKK66O..",
        "....OK32455OOOOK66O.",
        "....OK2345OOBWBO67O.",
        "....O323455OBKBO666O",
        "....O3344555OOO5665O",
        "....O4445555554KK32O",
        "....O3445555KKKKKKO.",
        ".....O34455544OOO...",
        "......O33444433O....",
        ".......O2333332O....",
        "........OOOOOOO.....",
    ],
    # Olhando para baixo (no pulo, mirando o chão): pupila no fundo do olho, gritando.
    "baixo": [
        "....OKK3445555556O..",
        "....OKK3445KKKK66O..",
        "....OK32455OOOOK66O.",
        "....OK2345OOBBBO67O.",
        "....O323455OBKKO666O",
        "....O3344555OOO5665O",
        "....O4445555554KK32O",
        "....O3445555KKKKKKO.",
        ".....O3445OWWWWWO...",
        "......O334ORTTTRO...",
        ".......O23OWWWWO....",
        "........OOOOOOO.....",
    ],
    # Olhando para cima (mirando para o alto), de dor (levou tiro) e morto (olhos em X).
    "cima": [
        "....OKK3445555556O..",
        "....OKK3445KKKK66O..",
        "....OK32455OOOOK66O.",
        "....OK2345OOBKKO67O.",
        "....O323455OBBWO666O",
        "....O3344555OOO5665O",
        "....O4445555554KK32O",
        "....O3445555KKKKKKO.",
        ".....O3445OWWWWWO...",
        "......O334ORTTTRO...",
        ".......O23OWWWWO....",
        "........OOOOOOO.....",
    ],
    "dor": [
        "....OKK3445555556O..",
        "....OKK3445KKKK66O..",
        "....OK32455OOOOK66O.",
        "....OK23455OO55567O.",
        "....O32345555OO5666O",
        "....O33445555555665O",
        "....O4445555554KK32O",
        "....O3445555KKKKKKO.",
        ".....O3445OWWWWWO...",
        "......O334ORTTTRO...",
        ".......O23OWWWWO....",
        "........OOOOOOO.....",
    ],
    "morto": [
        "....OKK3445555556O..",
        "....OKK3445KKKK66O..",
        "....OK32455OOOOK66O.",
        "....OK23455O5O5567O.",
        "....O3234555O555666O",
        "....O334455O5O55665O",
        "....O4445555554KK32O",
        "....O3445555KKKKKKO.",
        ".....O3445OWWWWWO...",
        "......O334ORTTTRO...",
        ".......O23OWWWWO....",
        "........OOOOOOO.....",
    ],
    "morto2": [
        "....OKK3445555556O..",
        "....OKK3445KKKK66O..",
        "....OK32455OOOOK66O.",
        "....OK23455O5O5567O.",
        "....O3234555O555666O",
        "....O334455O5O55665O",
        "....O4445555554KK32O",
        "....O3445555KKKKKKO.",
        ".....O3445OWWWWWO...",
        "......O334OTTTTO....",
        ".......O23ORRRO.....",
        "........OOORRO......",
    ],
    # Assustado: olho arregalado, boca em O.
    "susto": [
        "....OKK3445555556O..",
        "....OKK34455KKK66O..",
        "....OK3245OOOOO666O.",
        "....OK234OBBWBBO67O.",
        "....O32345OBKKBO666O",
        "....O33445OBBBBO665O",
        "....O44455OOOOO4K32O",
        "....O3445555KKKKKKO.",
        ".....O344555OOOO....",
        "......O3344OTTO.....",
        ".......O2333OO......",
        "........OOOOO.......",
    ],
}

# ---------------------------------------------------------------- tronco
TRONCO = [  # (linha, x, texto)
    (19, 11, "OOTUUTTTEOO"),
    (20, 9, "OOiuOTUTTTEERO"),
    (21, 8, "OiiuuyOREERRsyO"),
    (22, 7, "OiiuuyyyyyyAswyO"),
    (23, 7, "OiuuyyyyyyAsdtyyO"),
    (24, 6, "OiuuyyyyyAsdttyyO"),
    (25, 6, "OiuyyyyyAsdtttyO"),
    (26, 6, "OiuyyyyAsdttteyO"),
    (27, 6, "OuyyyyAsdtttteeO"),
    (28, 6, "OuyyyAsdttteeewO"),
    (29, 6, "OyyyAsdtttteewwO"),
    (30, 6, "OssssGAGssssssssO"),
    (31, 6, "OdfdfAAAfdfdfdfdO"),
]
BRACO_FRENTE = [  # braço da frente segurando o fuzil na altura do quadril
    (21, 15, "OyytO"),
    (22, 15, "OyyttwO"),
    (23, 15, "OytteewO"),
    (24, 16, "OytteeO"),
    (25, 16, "OtteewwO"),
    (26, 17, "OteewOO566O"),
    (27, 17, "OOOOOO53464O"),
]
FUZIL_FRENTE = [
    (27, 10, "Ohggffd"),
    (28, 9, "OhggffddsO"),
    (29, 10, "OOddssO"),
    (25, 24, "OOOOOOOOOOOOOOOOOOOO"),
    (26, 28, "VVVVVVVVVVVVVVvO"),
    (27, 28, "cccccOggffdddsO"),
    (28, 27, "OxxXO"),
]

FUZIL_CIMA_ATRAS = []
BRACO_CIMA = [  # braços erguidos segurando o fuzil na vertical, na frente do rosto
    (-4, 23, "OO"),
    (-3, 23, "OVO"),
    (-2, 23, "OVcO"),
    (-1, 23, "OVcO"),
    (0, 23, "OVcO"),
    (1, 23, "OVcO"),
    (2, 23, "OVcO"),
    (3, 23, "OVcO"),
    (4, 23, "OVcO"),
    (5, 23, "OVcO"),
    (6, 23, "OVcO"),
    (7, 22, "OgVcfO"),
    (8, 22, "OgVcfO"),
    (9, 22, "OgVcfO"),
    (10, 22, "OgXcdO"),
    (11, 21, "O566XO"),
    (12, 21, "O456xO"),
    (13, 21, "OO33OO"),
    (14, 22, "OgfdO"),
    (15, 22, "OgfdO"),
    (16, 22, "OgfdO"),
    (17, 22, "OgfdO"),
    (18, 21, "O5664O"),
    (19, 21, "O3443O"),
    (20, 18, "OyytOOOO"),
    (21, 16, "OyyteewO"),
    (22, 15, "OyytteewO"),
    (23, 15, "OyytteeO"),
    (24, 16, "OytteO"),
]
# braço de cima (punho perto do rosto) liga o ombro à mão erguida
BRACO_CIMA += [(12, 17, "OyytO"), (13, 16, "OyyttO"), (14, 16, "OyyteO"), (15, 16, "OyyteO"),
               (16, 16, "OytteO"), (17, 16, "OytteO"), (18, 16, "OyttwO"), (19, 16, "OtteO")]

# ---------------------------------------------------------------- pernas
import numpy as np  # noqa: E402

CALCA = "CcXxZ"      # claro -> escuro (luz da esquerda)
PERNEIRA = "hgfds"
QUADRIL_Y = 32
# Posições (joelho, pé) relativas ao quadril, para o ciclo de corrida.
CICLO = [((4, 4), (5, 9)), ((2, 4), (1, 9)), ((-1, 4), (-3, 9)),
         ((-3, 4), (-7, 8)), ((-2, 4), (-6, 5)), ((3, 2), (1, 6))]
POSES_PERNAS = {
    "parado": (((-2, 4), (-4, 9)), ((2, 4), (3, 9)), 0),
    "pulo": (((-2, 2), (-6, 5)), ((4, 1), (2, 5)), 0),
    "agachado": (((-1, 3), (-6, 3)), ((6, 1), (5, 3)), 5),
}
for k in range(6):
    POSES_PERNAS[f"corre{k + 1}"] = (CICLO[(k + 3) % 6], CICLO[k], -1 if k in (1, 4) else 0)


def segmento(mask_shape, a, b, r):
    yy, xx = np.mgrid[0:mask_shape[0], 0:mask_shape[1]]
    px, py = xx + 0.5 - a[0], yy + 0.5 - a[1]
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = max(vx * vx + vy * vy, 1e-6)
    t = np.clip((px * vx + py * vy) / L2, 0, 1)
    dx, dy = px - t * vx, py - t * vy
    return np.hypot(dx, dy) <= r, dx


def pintar_tons(g, mascara, lado, tons, escurecer=0):
    """Pinta a máscara com tons pelo lado do eixo: esquerda clara, direita escura."""
    n = len(tons)
    for y, x in zip(*np.where(mascara)):
        f = (lado[y, x] + 2.6) / 5.2
        g[y][x] = tons[min(n - 1, max(0, int(f * n) + escurecer))]


def contorno(g, mascara):
    m = np.pad(mascara, 1)
    viz = m[:-2, 1:-1] | m[2:, 1:-1] | m[1:-1, :-2] | m[1:-1, 2:]
    borda = viz & ~mascara
    for y, x in zip(*np.where(borda)):
        if g[y][x] == ".":
            g[y][x] = "O"


def perna(g, quadril, joelho, pe, atras):
    forma = (len(g), len(g[0]))
    hx, hy = quadril
    k = (hx + joelho[0], hy + joelho[1])
    p = (hx + pe[0], hy + pe[1])
    esc = 1 if atras else 0
    coxa, lado1 = segmento(forma, (hx + 0.5, hy + 0.5), (k[0] + 0.5, k[1] + 0.5), 2.6)
    canela, lado2 = segmento(forma, (k[0] + 0.5, k[1] + 0.5), (p[0] + 0.5, p[1] - 1.5), 2.3)
    # Alpercata: sola larga apontando para a frente.
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]]
    bota = (((xx + 0.5 - (p[0] + 1.8)) / 3.6) ** 2 + ((yy + 0.5 - (p[1] - 0.6)) / 1.7) ** 2) <= 1
    pintar_tons(g, coxa, lado1, CALCA, esc)
    pintar_tons(g, canela & ~coxa, lado2, PERNEIRA, esc)
    for y, x in zip(*np.where(bota)):
        g[y][x] = "s" if y >= p[1] else ("g" if x < p[0] + 1 else "d")
    if not atras:
        g[min(len(g) - 1, k[1] + 1)][k[0]] = "A"  # fivela da perneira
    contorno(g, coxa | canela | bota)


def pintar(g, y, x, txt):
    for k, ch in enumerate(txt):
        if ch != "." and 0 <= y < len(g) and 0 <= x + k < len(g[0]):
            g[y][x + k] = ch


def quadro(rosto="grito", pernas="parado", mira="frente"):
    g = [["."] * W for _ in range(H)]
    tras, frente, dy = POSES_PERNAS[pernas]
    dy += MARGEM
    qy = QUADRIL_Y + dy
    perna(g, (11, qy), *tras, atras=True)
    perna(g, (16, qy), *frente, atras=False)
    if mira == "cima":
        for y, x, txt in FUZIL_CIMA_ATRAS:
            pintar(g, y + dy, x, txt)
    for y, x, txt in TRONCO + (FUZIL_FRENTE if mira == "frente" else []):
        pintar(g, y + dy, x, txt)
    for k, txt in enumerate(ROSTOS[rosto]):
        pintar(g, 8 + k + dy, 7, txt)
    for k, txt in enumerate(CHAPEU):
        pintar(g, 1 + k + dy, 4, txt)
    for y, x, txt in (BRACO_FRENTE if mira == "frente" else BRACO_CIMA):
        pintar(g, y + dy, x, txt)
    return "\n".join("".join(l) for l in g)


if __name__ == "__main__":
    for nome, rows in ROSTOS.items():
        assert all(len(r) == 20 for r in rows), (nome, [len(r) for r in rows])
    assert all(len(r) == 24 for r in CHAPEU), [len(r) for r in CHAPEU]
    quadros = {"parado": quadro("serio"), "atirando": quadro("grito"), "susto": quadro("susto")}
    for k in range(6):
        quadros[f"corre{k + 1}"] = quadro("grito", f"corre{k + 1}")
    quadros["pulo"] = quadro("grito", "pulo")
    quadros["agachado"] = quadro("serio", "agachado")
    quadros["mira_cima"] = quadro("grito", "parado", "cima")
    pixel.PASTA.mkdir(exist_ok=True)
    texto = "# Legenda em tools/arte/pixel.py. '.' é transparente.\n"
    texto += "\n".join(f"== {n}\n{q}\n" for n, q in quadros.items())
    (pixel.PASTA / "lampiao.txt").write_text(texto)
    print("ok")
