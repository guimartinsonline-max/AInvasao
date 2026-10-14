import { P } from './paleta.js';

// Cria uma textura a partir de linhas de texto: cada caractere é um pixel e o
// mapa diz qual cor da paleta ele usa. "." é transparente.
export function texturaDeTexto(cena, chave, linhas, mapa, largura, altura) {
  const w = largura || Math.max(...linhas.map((l) => l.length));
  const h = altura || linhas.length;
  const tex = cena.textures.createCanvas(chave, w, h);
  const ctx = tex.getContext();
  const topo = h - linhas.length; // alinha pelo pé
  linhas.forEach((linha, y) => {
    for (let x = 0; x < linha.length; x++) {
      const nome = mapa[linha[x]];
      if (!nome) continue;
      ctx.fillStyle = '#' + P[nome].toString(16).padStart(6, '0');
      ctx.fillRect(x, y + topo, 1, 1);
    }
  });
  tex.refresh();
  return tex;
}

// Desenha numa textura nova usando o contexto 2D do canvas.
export function texturaDesenhada(cena, chave, w, h, desenhar) {
  const tex = cena.textures.createCanvas(chave, w, h);
  const ctx = tex.getContext();
  ctx.imageSmoothingEnabled = false;
  desenhar(ctx, (nome) => '#' + P[nome].toString(16).padStart(6, '0'));
  tex.refresh();
  return tex;
}

// Disco pixelado (sem antisserrilhado).
export function disco(ctx, cx, cy, r, cor) {
  ctx.fillStyle = cor;
  for (let y = -r; y <= r; y++) {
    const meia = Math.floor(Math.sqrt(r * r - y * y) + 0.3);
    ctx.fillRect(cx - meia, cy + y, meia * 2 + 1, 1);
  }
}
