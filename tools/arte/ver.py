"""Renderiza todos os desenhos de um .txt de tools/arte/pixel lado a lado, ampliados."""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import pixel  # noqa: E402

arquivo, saida = sys.argv[1], Path(sys.argv[2])
escala = int(sys.argv[3]) if len(sys.argv) > 3 else 8
desenhos = pixel.ler(arquivo)
w = sum(d.w + 4 for d in desenhos.values())
h = max(d.h for d in desenhos.values())
img = Image.new("RGBA", (w, h), (79, 154, 214, 255))
x = 0
for d in desenhos.values():
    img.alpha_composite(d.imagem(), (x, h - d.h))
    x += d.w + 4
img.resize((w * escala, h * escala), Image.NEAREST).save(saida)
print(saida)
