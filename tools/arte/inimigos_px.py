"""Inimigos pixel a pixel no estilo Metal Slug: soldado da Volante e soldado
xeremita. Gera tools/arte/pixel/volante.txt e xeremita.txt.

Desenhados virados para a direita, como o Lampião; o jogo espelha.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import boneco as b  # noqa: E402
import lampiao_px as lp  # noqa: E402
import pixel  # noqa: E402

W, H, MARGEM = 44, 46, 4
QUADRIL = (11, 36)

# ================================================================ Volante
QUEPE = [  # 20 colunas em x=7, a partir da linha 2
    "....OOOOOOOOOO......",
    "...OPPkkkkkkkJO.....",
    "...OPkkkkAkkkJjO....",
    "...OPkkkkkkkkJjO....",
    "...OjjjjjjjjjjjO....",
    "...OKKKKKKKKKKKKKO..",
    "....OOOOOOOOOOOOOOO.",
]
ROSTO_VOLANTE = {  # 20 colunas em x=7, a partir da linha 9
    "serio": [
        "....ON45555555556O..",
        "....ON4555KKKK566O..",
        "....ON3455WWWO666O..",
        "....ON2345WWKO67O...",
        "....O323455OOO6666O.",
        "....O3344555556665O.",
        "....O4445555554KK3O.",
        "....O3445555KKKKKKO.",
        ".....O3445544KKKKO..",
        "......O33444433O....",
        ".......O2333332O....",
        "........OOOOOOO.....",
    ],
    "grito": [
        "....ON45555555556O..",
        "....ON4555KKKK566O..",
        "....ON3455WWWO666O..",
        "....ON2345WWKO67O...",
        "....O323455OOO6666O.",
        "....O3344555556665O.",
        "....O4445555554KK3O.",
        "....O3445555KKKKKKO.",
        ".....O3445OWWWWWO...",
        "......O334ORTTTRO...",
        ".......O23OWWWWO....",
        "........OOOOOOO.....",
    ],
    # Pânico (o soldado do Metal Slug que se apavora): olhos esbugalhados, boca enorme.
    "panico": [
        "....ON45KKK5555556O.",
        "....ON455555KKK66O..",
        "....ON345WWWWOO66O..",
        "....ON23WWKWWO67O...",
        "....O3234WWWWO6666O.",
        "....O33445OOOO6665O.",
        "....O4445555554KK3O.",
        "....O3445555KKKKKKO.",
        ".....O344OOOOOOO....",
        "......O33ORTTTTRO...",
        ".......O2ORRTTRO....",
        "........OOOOOOO.....",
    ],
}
OLIVA = {"i": "p", "u": "P", "y": "k", "t": "k", "e": "J", "w": "j",
         "T": "J", "U": "k", "E": "j", "R": "j", "A": "f", "G": "d"}


def volante(rosto="serio", pernas="parado", tiro=False):
    g = b.grade(W, H)
    if pernas == "parado":
        tras, frente = ((-2, 4), (-4, 9)), ((2, 4), (3, 9))
    else:
        k = int(pernas[-1]) - 1
        tras, frente = b.CICLO_ANDAR[(k + 2) % 4], b.CICLO_ANDAR[k]
    dy = -1 if pernas in ("anda2", "anda4") else 0
    q = (QUADRIL[0], QUADRIL[1] + dy)
    kw = dict(coxa_tons="PkkJj", canela_tons="hgfds", sola="KO", gaspea="xK")
    b.perna(g, q, *tras, atras=True, **kw)
    b.perna(g, (q[0] + 5, q[1]), *frente, atras=False, **kw)
    m = MARGEM + dy
    tronco = b.trocar(lp.TRONCO, OLIVA)
    for y, x, t in tronco + b.trocar(lp.FUZIL_FRENTE, {}):
        b.pintar(g, y + m, x, t)
    # Botões dourados da túnica.
    for y in (24, 27):
        b.pintar(g, y + m, 20, "A")
    b.bloco(g, 9 + m, 7, ROSTO_VOLANTE[rosto])
    b.bloco(g, 2 + m, 7, QUEPE)
    for y, x, t in b.trocar(lp.BRACO_FRENTE, OLIVA):
        b.pintar(g, y + m, x, t)
    if tiro:
        b.bloco(g, 23 + m, 43 - 3, ["..U", ".UH", "UHW", ".UH", "..U"])
    return g


# ================================================================ Xeremita
CABECA_XEREMITA = [  # 22 colunas em x=6, a partir da linha 4
    "........O.............",
    "........O*O...........",
    ".........O............",
    "......OOOOOOO.........",
    "....OO??***?!OO.......",
    "...O?**???!!!!0O......",
    "..O?*??!!!!!!!!0O.....",
    "..O??!!!!!!!!!!09O....",
    ".O??!!!!!!!!!!!!09O...",
    ".O?!!!!!!!!OOOO!!09O..",
    ".O!!!!!!!!OKKKKO!09O..",
    ".O!!!!!!!OKKWKKKO09O..",
    ".O0!!!!!!OKKKKKKO!9O..",
    ".O00!!!!!!OKKKKO!09O..",
    "..O00!!!!!!OOOO!009O..",
    "...O900!!!!!!!!0099O..",
    "....O99000!!!0099OO...",
    ".....OO990!99999O.....",
    ".......OO9OO99OO......",
    ".........OOOO.........",
]
BOCA_XEREMITA = {
    "normal": [],
    "grito": [(18, 15, "OKKO"), (19, 15, "OKRO"), (20, 16, "OO")],
}
CORPO_XEREMITA = [  # (linha, x, texto) sem margem
    (23, 12, "OOOOOO"),
    (24, 10, "OOvVVvCcO"),
    (25, 9, "OVvvCCcXxO"),
    (26, 9, "OvCC*cXxxO"),
    (27, 9, "OCCc**XxxO"),
    (28, 9, "OCcc*XxxZO"),
    (29, 9, "OccXXxxZZO"),
    (30, 10, "OxxxxZZO"),
    (31, 10, "OxXXxZZO"),
    (32, 10, "OOOOOOOO"),
]
BRACO_XEREMITA = [
    (25, 15, "OvCO"),
    (26, 15, "OCcXO"),
    (27, 16, "OcXxOOOOOOOOOO"),
    (28, 17, "O?!0OVvvCccx*O"),
    (29, 17, "O!09OCcXxxxx*O"),
    (30, 18, "OOOOOOOOOOOOO"),
]


def xeremita(boca="normal", pernas="parado", tiro=False):
    g = b.grade(W, H)
    if pernas == "parado":
        tras, frente = ((-1, 4), (-2, 9)), ((1, 4), (2, 9))
    else:
        k = int(pernas[-1]) - 1
        tras, frente = b.CICLO_ANDAR[(k + 2) % 4], b.CICLO_ANDAR[k]
    dy = -1 if pernas in ("anda2", "anda4") else 0
    q = (13, QUADRIL[1] + dy)
    kw = dict(coxa_tons="vCcXx", canela_tons="vCcXx", sola="90", gaspea="!0", r_coxa=1.9, r_canela=1.6, pe_largo=3.0)
    b.perna(g, q, *tras, atras=True, **kw)
    b.perna(g, (q[0] + 3, q[1]), *frente, atras=False, **kw)
    m = MARGEM + dy
    for y, x, t in CORPO_XEREMITA:
        b.pintar(g, y + m - 1, x, t)
    b.bloco(g, 4 + m - 1, 6, CABECA_XEREMITA)
    for y, x, t in BOCA_XEREMITA[boca]:
        b.pintar(g, y + m - 1, x, t)
    for y, x, t in BRACO_XEREMITA:
        b.pintar(g, y + m - 1, x, t)
    if tiro:
        b.bloco(g, 26 + m - 1, 31, [".*.", "*W*", ".*."])
    return g


def gravar(arquivo, quadros):
    pixel.PASTA.mkdir(exist_ok=True)
    t = "# Legenda em tools/arte/pixel.py. '.' é transparente.\n"
    t += "\n".join(f"== {n}\n{b.texto(g)}\n" for n, g in quadros.items())
    (pixel.PASTA / arquivo).write_text(t)


if __name__ == "__main__":
    for nome, linhas in {**{f"quepe": QUEPE}, **{f"rosto_{k}": v for k, v in ROSTO_VOLANTE.items()}}.items():
        assert all(len(l) == 20 for l in linhas), (nome, [len(l) for l in linhas])
    assert all(len(l) == 22 for l in CABECA_XEREMITA), [len(l) for l in CABECA_XEREMITA]
    vol = {"parado": volante(), "atira": volante("grito", tiro=True), "panico": volante("panico")}
    for k in range(1, 5):
        vol[f"anda{k}"] = volante("serio", f"anda{k}")
    gravar("volante.txt", vol)
    xer = {"parado": xeremita(), "atira": xeremita("grito", tiro=True), "grito": xeremita("grito")}
    for k in range(1, 5):
        xer[f"anda{k}"] = xeremita("normal", f"anda{k}")
    gravar("xeremita.txt", xer)
    print("ok")
