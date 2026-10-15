import { texturaDeTexto, texturaDesenhada, disco } from './pixelart.js';
import { TOUCEIRA } from './quadros.js';

// Personagens e cenário vêm de PNGs gerados por tools/arte/exportar.py.
// Aqui ficam só as texturas pequenas de efeitos, desenhadas em código.

export function carregarSprites(cena) {
  const s = 'assets/sprites/';
  cena.load.spritesheet('lampiao', s + 'lampiao.png', { frameWidth: 56, frameHeight: 52 });
  cena.load.spritesheet('alien', s + 'alien.png', { frameWidth: 40, frameHeight: 44 });
  cena.load.image('maria_bonita', s + 'maria_bonita.png');
  cena.load.spritesheet('touceiras', s + 'touceiras.png', { frameWidth: TOUCEIRA.largura, frameHeight: TOUCEIRA.altura });
  for (const nome of ['ceu', 'nuvens', 'serras', 'paredoes', 'planicie', 'caatinga', 'chao', 'caixote', 'laje']) {
    cena.load.image(nome, s + nome + '.png');
  }
}

export function gerarSprites(cena) {
  const g = cena.make.graphics({ x: 0, y: 0 }, false);
  g.fillStyle(0xffffff, 1).fillRect(0, 0, 2, 2);
  g.generateTexture('px', 1, 1);
  g.generateTexture('px2', 2, 2);
  g.destroy();

  // Bala alongada com núcleo branco, como um rastro.
  texturaDeTexto(cena, 'bala', ['..oyyyW.', 'oyyWWWWW', '..oyyyW.'], { o: 'laranja_fogo', y: 'amarelo_fogo', W: 'branco' });
  texturaDeTexto(cena, 'capsula', ['ee'], { e: 'amarelo_fogo' });
  texturaDeTexto(cena, 'granada', ['.g.', 'GGG', 'GgG', 'GGG'], { g: 'cinza', G: 'caatinga_esc' });
  // Clarão do cano, voltado para a direita (a origem fica na boca do cano).
  texturaDeTexto(cena, 'clarao', [
    '..o.......',
    '...oo..o..',
    '.oyyyyo...',
    'oyWWWWyyoo',
    'yWWWWWWyyo',
    'oyWWWWyyoo',
    '.oyyyyo...',
    '...oo..o..',
    '..o.......',
  ], { o: 'laranja_fogo', y: 'amarelo_fogo', W: 'branco' });
  texturaDeTexto(cena, 'corte', [
    '....wwww....',
    '..ww....ww..',
    '.w........w.',
    'w..........w',
    'w...........',
    'w...........',
  ], { w: 'branco' });

  texturaDesenhada(cena, 'disco', 16, 16, (ctx) => disco(ctx, 8, 8, 7, '#ffffff'));
  texturaDesenhada(cena, 'bola', 6, 6, (ctx) => disco(ctx, 3, 3, 2, '#ffffff'));
}
