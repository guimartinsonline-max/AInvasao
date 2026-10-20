"""Pixel art em texto: cada caractere é um pixel de uma cor da paleta.

Os desenhos ficam em tools/arte/pixel/*.txt, editáveis à mão.
Formato: blocos separados por uma linha "== nome"; dentro, uma linha por
linha de pixels. "." é transparente.
"""
from pathlib import Path

import numpy as np

from motor import IDX, NOMES, VAZIO, Tela

LEGENDA = {
    "K": "preto", "O": "sombra", "o": "sombra_media", "Z": "azul_sombra",
    "x": "cinza_escuro", "X": "cinza_medio", "c": "cinza", "C": "cinza_luz", "v": "cinza_claro",
    "V": "aco_brilho", "W": "branco",
    "1": "pele_sombra", "2": "pele_escura", "3": "pele_media", "4": "pele", "5": "pele_luz",
    "6": "pele_clara", "7": "pele_brilho",
    "q": "terra_escura", "w": "terra", "e": "terra_media", "r": "barro", "t": "areia_media",
    "y": "areia", "u": "areia_luz", "i": "areia_clara",
    "a": "couro_profundo", "s": "couro_escuro", "d": "couro", "f": "couro_medio", "g": "couro_claro",
    "h": "couro_luz",
    "R": "vermelho_esc", "E": "vermelho_medio", "T": "vermelho", "Y": "laranja_escuro", "U": "laranja_fogo",
    "G": "ouro_escuro", "A": "amarelo_fogo", "H": "amarelo_claro",
    "b": "azul_medio", "n": "ceu_escuro", "m": "ceu", "M": "ceu_medio", "B": "ceu_claro", "L": "ceu_luz",
    "l": "horizonte",
    "j": "caatinga_esc", "J": "caatinga_media", "k": "caatinga", "P": "mandacaru", "p": "mandacaru_luz",
    "8": "alien_profundo", "9": "alien_esc", "0": "alien_medio", "!": "alien", "?": "alien_luz", "*": "alien_brilho",
    "N": "marrom_noite",
    "(": "roxo_escuro", ")": "roxo", "[": "lilas", "]": "lilas_claro", "{": "rosa_poeira",
    # Crepúsculo (base_detalhe.py): madeira, lona, lona acesa, oliva, terra batida, corda.
    "D": "mad_n1", "F": "mad_n2", "I": "mad_n3", "Q": "mad_n4", "S": "mad_n5", "z": "mad_n6", "#": "lona_n1", "$": "lona_n2", "%": "lona_n3", "&": "lona_n4", "+": "lona_n5", ",": "lona_n6", "-": "lona_q1", "/": "lona_q2", ":": "lona_q3", ";": "lona_q4", "<": "oliva_n1", ">": "oliva_n2", "@": "oliva_n3", "^": "oliva_n4", "_": "oliva_n5", "`": "chao_n1", "|": "chao_n2", "~": "chao_n3", "á": "chao_n4", "é": "chao_n5", "í": "chao_n6", "ó": "corda_n1", "ú": "corda_n2", "ã": "corda_n3",
    # Rampas saturadas (padrão Metal Slug, 20/10).
    "à": "pelo_1", "â": "pelo_2", "ä": "pelo_3", "å": "pelo_4", "æ": "pelo_5", "ç": "pelo_6", "è": "pelo_7", "ê": "fuba_1", "ë": "fuba_2", "ì": "fuba_3", "î": "fuba_4", "ï": "fuba_5", "ñ": "fuba_6", "ò": "fuba_7", "ô": "carne_1", "ö": "carne_2", "ø": "carne_3", "ù": "carne_4", "û": "carne_5", "ü": "carne_6", "ý": "carne_7", "ÿ": "verde_1", "À": "verde_2", "Â": "verde_3", "Ä": "verde_4", "Å": "verde_5", "Æ": "verde_6", "Ç": "verde_7", "È": "negro_1", "Ê": "negro_2", "Ë": "negro_3", "Ì": "negro_4", "Î": "negro_5", "Ï": "negro_6", "Ñ": "rubro_1", "Ò": "rubro_2", "Ô": "rubro_3", "Ö": "rubro_4", "Ø": "rubro_5", "Ù": "rubro_6", "Û": "latao_1", "Ü": "latao_2", "Ý": "latao_3", "þ": "latao_4", "ß": "latao_5", "ð": "latao_6", "Ð": "osso_1", "Þ": "osso_2", "¡": "osso_3", "¿": "osso_4", "§": "osso_5", "¤": "aco_1", "£": "aco_2", "¥": "aco_3", "©": "aco_4", "®": "aco_5", "°": "aco_6",
}
CHAR = {v: k for k, v in LEGENDA.items()}
faltando = set(NOMES) - set(CHAR)
assert not faltando, f"cores sem caractere: {faltando}"

PASTA = Path(__file__).parent / "pixel"


def para_texto(tela):
    linhas = []
    for y in range(tela.h):
        linhas.append("".join("." if v == VAZIO else CHAR[NOMES[v]] for v in tela.px[y]))
    return "\n".join(linhas)


def de_texto(texto, w=None, h=None):
    linhas = [l for l in texto.strip("\n").split("\n")]
    W = w or max(len(l) for l in linhas)
    Hh = h or len(linhas)
    t = Tela(W, Hh)
    for y, l in enumerate(linhas):
        for x, ch in enumerate(l):
            if ch != "." and ch != " ":
                t.px[y, x] = IDX[LEGENDA[ch]]
    return t


def ler(arquivo):
    """Lê um .txt com vários desenhos e devolve {nome: Tela}."""
    texto = (PASTA / arquivo).read_text()
    blocos = {}
    nome = None
    linhas = []
    for l in texto.split("\n"):
        if l.startswith("== "):
            if nome:
                blocos[nome] = linhas
            nome, linhas = l[3:].strip(), []
        elif nome is not None and l.strip() != "" and not l.startswith("#"):
            linhas.append(l.rstrip())
    if nome:
        blocos[nome] = linhas
    w = max(len(l) for ls in blocos.values() for l in ls)
    return {n: de_texto("\n".join(ls), w=w, h=len(ls)) for n, ls in blocos.items()}


def salvar(arquivo, desenhos):
    """Grava {nome: Tela} em texto."""
    PASTA.mkdir(exist_ok=True)
    partes = [f"== {n}\n{para_texto(t)}\n" for n, t in desenhos.items()]
    cab = "# Legenda em tools/arte/pixel.py. '.' é transparente.\n"
    (PASTA / arquivo).write_text(cab + "\n".join(partes))
