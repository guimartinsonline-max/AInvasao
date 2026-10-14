"""Gera os ícones do app (provisórios) com as cores da paleta.

Uso: python3 tools/gerar_icones.py
Desenha em 32x32 pixels e amplia sem borrar.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
CORES = json.loads((RAIZ / "assets/paleta.json").read_text())["cores"]
SAIDA = RAIZ / "assets/icons"


def desenhar(margem=0):
    img = Image.new("RGB", (32, 32), CORES["ceu"])
    d = ImageDraw.Draw(img)
    # Chão de terra.
    d.rectangle([0, 22, 31, 31], fill=CORES["areia"])
    d.line([0, 22, 31, 22], fill=CORES["barro"])
    # Mandacaru.
    d.rectangle([6, 12, 8, 21], fill=CORES["caatinga"])
    d.rectangle([3, 14, 4, 17], fill=CORES["caatinga"])
    d.rectangle([4, 17, 6, 18], fill=CORES["caatinga"])
    d.rectangle([10, 13, 11, 16], fill=CORES["caatinga"])
    d.rectangle([8, 16, 10, 17], fill=CORES["caatinga"])
    # Disco voador com feixe.
    d.polygon([(17, 12), (27, 12), (30, 21), (14, 21)], fill=CORES["alien_brilho"])
    d.ellipse([18, 4, 26, 10], fill=CORES["horizonte"])
    d.ellipse([13, 8, 31, 13], fill=CORES["cinza"])
    d.line([15, 11, 29, 11], fill=CORES["cinza_escuro"])
    for x in (16, 21, 26):
        d.point((x, 10), fill=CORES["alien"])
    if margem:
        # Versão "maskable": encolhe o desenho para caber na área segura.
        fundo = Image.new("RGB", (32 + margem * 2, 32 + margem * 2), CORES["ceu"])
        fundo.paste(img, (margem, margem))
        img = fundo
    return img


def salvar(img, tamanho, nome):
    img.resize((tamanho, tamanho), Image.NEAREST).save(SAIDA / nome, optimize=True)


SAIDA.mkdir(parents=True, exist_ok=True)
base = desenhar()
salvar(base, 192, "icon-192.png")
salvar(base, 512, "icon-512.png")
salvar(base, 180, "apple-touch-icon.png")
salvar(desenhar(margem=8), 512, "icon-512-maskable.png")
print("Ícones gerados em", SAIDA)
