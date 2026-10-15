"""Gera os PNGs usados pelo jogo em assets/sprites/.

Uso: python3 tools/arte/exportar.py
A ordem dos quadros das folhas está em src/quadros.js e precisa bater com a daqui.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import cenario as cn  # noqa: E402
import personagens as pg  # noqa: E402
from motor import RAIZ, folha  # noqa: E402

SAIDA = RAIZ / "assets/sprites"
SAIDA.mkdir(parents=True, exist_ok=True)

PERNAS_LAMPIAO = ["parado", "corre1", "corre2", "corre3", "pulo"]


def lampiao():
    quadros = []
    for mira in ("frente", "cima"):
        for pernas in PERNAS_LAMPIAO:
            boca = "grito" if pernas == "pulo" else "sorriso"
            quadros.append(pg.lampiao({"pernas": pernas, "mira": mira, "boca": boca}))
    quadros.append(pg.lampiao({"pernas": "agachado"}))
    quadros.append(pg.lampiao({"boca": "grito"}))
    return quadros


folha(lampiao(), SAIDA / "lampiao.png")
folha([pg.maria_bonita()], SAIDA / "maria_bonita.png")
folha([pg.alien(), pg.alien({"olho": "fechado"})], SAIDA / "alien.png")

for nome, tela in {
    "ceu": cn.ceu(),
    "nuvens": cn.nuvens(),
    "serras": cn.serras(),
    "paredoes": cn.paredoes(),
    "planicie": cn.planicie(),
    "caatinga": cn.caatinga(),
    "chao": cn.chao_tile(),
    "caixote": cn.caixote(),
    "laje": cn.laje(),
}.items():
    tela.imagem().save(SAIDA / f"{nome}.png", optimize=True)
folha([cn.touceira(k) for k in range(4)], SAIDA / "touceiras.png")

# Aumenta a versão dos assets para o navegador não usar cópias velhas.
config = RAIZ / "src/config.js"
texto = config.read_text()
import re  # noqa: E402
versao = int(re.search(r"VERSAO = (\d+)", texto).group(1)) + 1
config.write_text(re.sub(r"VERSAO = \d+", f"VERSAO = {versao}", texto))

total = sum(f.stat().st_size for f in SAIDA.glob("*.png"))
print(f"Sprites em {SAIDA} ({total // 1024} KB), versão {versao}")
