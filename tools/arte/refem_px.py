"""Refém (romeiro barbudo, chapéu de palha) pixel a pixel, estilo prisioneiro
do Metal Slug: amarrado se debatendo, solto batendo continência e correndo.
Gera tools/arte/pixel/refem.txt."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import boneco as b  # noqa: E402
from inimigos_px import gravar  # noqa: E402

W, H = 32, 36

CABECA = {  # 16 colunas
    "triste": [
        "....OOOOOO......",
        "...OiuuyyrO.....",
        "...OTTTTTEO.....",
        "OOOiuuyyyytrOOO.",
        "OiuuyyyyyyttrrrO",
        ".OOOOOOOOOOOOOO.",
        "...ON55666665O..",
        "...ON45KK6665O..",
        "...O345555666O..",
        "...OvvC455vvvO..",
        "....OvvCCCvvvO..",
        ".....OCCvvvCO...",
        "......OOOOOO....",
    ],
    "feliz": [
        "....OOOOOO......",
        "...OiuuyyrO.....",
        "...OTTTTTEO.....",
        "OOOiuuyyyytrOOO.",
        "OiuuyyyyyyttrrrO",
        ".OOOOOOOOOOOOOO.",
        "...ON55666665O..",
        "...ON4K6K6665O..",
        "...O345555666O..",
        "...OvvCOWWOvvO..",
        "....OvvORROvvO..",
        ".....OCCOOvCO...",
        "......OOOOOO....",
    ],
}

AMARRADO = [  # corpo ajoelhado com corda (20 colunas em x=4)
    ".....OOWWWWOO.......",
    "....OWWWWWvvCO......",
    "...OWhhhhhhhggO.....",
    "...OWWWWWWvvCcO.....",
    "...OhhhhhhhhgggO....",
    "...OWWWWWWvvCCcO....",
    "...OWWWWWvvvCCcO....",
    "...OhhhhhhhhgggO....",
    "....OWWWvvvCCcO.....",
    ".OOOOWWWWvvvCCOOOOO.",
    "OsdOWWWWWWvvvvCCccO.",
    "OsdOcCCvvvvCCCCcxxO.",
    ".OOOOOOOOOOOOOOOOOO.",
]


def amarrado(balanco=0, rosto="triste"):
    g = b.grade(W, H)
    b.bloco(g, 22, 4 + balanco, AMARRADO)
    b.bloco(g, 9, 6 + balanco, CABECA[rosto])
    return g


def solto(pernas="parado", continencia=False, dy=0):
    g = b.grade(W, H)
    if pernas == "parado":
        tras, frente = ((-1, 4), (-2, 9)), ((1, 4), (2, 9))
    else:
        k = int(pernas[-1]) - 1
        tras, frente = b.CICLO_CORRIDA[(k + 3) % 6], b.CICLO_CORRIDA[k]
    q = (12, 26 + dy)
    kw = dict(coxa_tons="WvCcx", canela_tons="WvCcx", sola="sd", gaspea="gd", r_coxa=2.2, r_canela=2.0, pe_largo=3.0)
    b.perna(g, q, *tras, atras=True, **kw)
    b.perna(g, (q[0] + 4, q[1]), *frente, atras=False, **kw)
    tronco = [".OOWWWWOO.", "OWWWWWvvCO", "OWWWWWvvCO", "OWWWWWvvCO", "OWWWWvvCCO", "OWWWWvvCCO",
              "OWWWvvvCCO", "OddddddddO"]
    b.bloco(g, 18 + dy, 8, tronco)
    if continencia:
        # Mão na aba do chapéu.
        b.bloco(g, 12 + dy, 19, ["O6O", "O56O", "OWvO", "OWvO", "OWvO", ".OO"])
    else:
        # Braço para trás, correndo.
        b.bloco(g, 19 + dy, 5, ["OWO", "OWvO", "O56O", ".OO"])
    b.bloco(g, 5 + dy, 6, CABECA["feliz"])
    return g


if __name__ == "__main__":
    for nome, l in CABECA.items():
        assert all(len(x) == 16 for x in l), nome
    assert all(len(x) == 20 for x in AMARRADO)
    gravar("refem.txt", {
        "amarrado1": amarrado(0), "amarrado2": amarrado(1),
        "continencia": solto("parado", True), "corre1": solto("corre1"), "corre2": solto("corre3"),
        "corre3": solto("corre4"), "corre4": solto("corre6"),
    })
    print("ok")
