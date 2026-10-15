import { texturaDeTexto, texturaDesenhada, disco } from './pixelart.js';
import { TOUCEIRA, LAMPIAO, INIMIGOS } from './quadros.js';
import { VERSAO } from './config.js';

// Personagens e cenário vêm de PNGs gerados por tools/arte/exportar.py.
// Aqui ficam só as texturas pequenas de efeitos, desenhadas em código.

export function carregarSprites(cena) {
  const s = (nome) => `assets/sprites/${nome}.png?v=${VERSAO}`;
  cena.load.spritesheet('lampiao', s('lampiao'), { frameWidth: LAMPIAO.largura, frameHeight: LAMPIAO.altura });
  cena.load.spritesheet('alien', s('alien'), { frameWidth: 40, frameHeight: 44 });
  for (const [nome, q] of Object.entries(INIMIGOS)) {
    cena.load.spritesheet(nome, s(nome), { frameWidth: q.largura, frameHeight: q.altura });
  }
  cena.load.image('maria_bonita', s('maria_bonita'));
  cena.load.spritesheet('touceiras', s('touceiras'), { frameWidth: TOUCEIRA.largura, frameHeight: TOUCEIRA.altura });
  for (const nome of ['ceu', 'nuvens', 'serras', 'paredoes', 'planicie', 'caatinga', 'chao', 'caixote', 'laje']) {
    cena.load.image(nome, s(nome));
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
  // Raio verde do xeremita.
  texturaDeTexto(cena, 'raio', ['..0!??*.', '90!?*WW*', '..0!??*.'], { '*': 'alien_brilho', W: 'branco', '?': 'alien_luz', '!': 'alien', 0: 'alien_medio', 9: 'alien_esc' });
  // Balas das armas pickup.
  texturaDeTexto(cena, 'chumbo', ['xC', 'CW'], { x: 'cinza_medio', C: 'cinza_claro', W: 'branco' });
  texturaDeTexto(cena, 'rojao', ['..ddRRTTU.', 'adddRTTTUH', '..ddRRTTU.'], { a: 'couro_escuro', d: 'couro', R: 'vermelho_esc', T: 'vermelho', U: 'laranja_fogo', H: 'amarelo_claro' });
  texturaDeTexto(cena, 'desintegra', ['..00!!??**W.', '0!!??**WWWWW', '..00!!??**W.'], { 0: 'alien_medio', '!': 'alien', '?': 'alien_luz', '*': 'alien_brilho', W: 'branco' });
  gerarCaixasDeArma(cena);
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

// Caixa de madeira com a letra da arma (como as caixas de arma do Metal Slug).
const LETRAS = {
  M: ['X...X', 'XX.XX', 'X.X.X', 'X...X', 'X...X'],
  B: ['XXXX.', 'X...X', 'XXXX.', 'X...X', 'XXXX.'],
  R: ['XXXX.', 'X...X', 'XXXX.', 'X..X.', 'X...X'],
  D: ['XXXX.', 'X...X', 'X...X', 'X...X', 'XXXX.'],
  G: ['.XXX.', 'X....', 'X.XXX', 'X...X', '.XXX.'],
  L: ['X....', 'X....', 'X....', 'X....', 'XXXXX'],
  F: ['XXXXX', 'X....', 'XXXX.', 'X....', 'X....'],
  O: ['.XXX.', 'X...X', 'X...X', 'X...X', '.XXX.'],
  C: ['.XXXX', 'X....', 'X....', 'X....', '.XXXX'],
};

function gerarCaixasDeArma(cena) {
  const base = [
    'OOOOOOOOOOOOOO',
    'OcvvvvvvvvvvxO',
    'OvhggggggggfxO',
    'OvgffffffffdxO',
    'OvgffffffffdxO',
    'OvgffffffffdxO',
    'OvgffffffffdxO',
    'OvgffffffffdxO',
    'OvgffffffffdxO',
    'OvgddddddddsxO',
    'OcxxxxxxxxxxXO',
    'OOOOOOOOOOOOOO',
  ];
  const mapa = { O: 'sombra', c: 'cinza', v: 'cinza_claro', x: 'cinza_escuro', X: 'cinza_medio', h: 'couro_luz',
    g: 'couro_claro', f: 'couro_medio', d: 'couro', s: 'couro_escuro', W: 'amarelo_fogo', K: 'couro_profundo' };
  for (const [letra, glifo] of Object.entries(LETRAS)) {
    const linhas = base.map((l) => l.split(''));
    glifo.forEach((l, y) => [...l].forEach((ch, x) => {
      if (ch === 'X') {
        linhas[3 + y][5 + x] = 'W';
        linhas[4 + y][6 + x] = linhas[4 + y][6 + x] === 'W' ? 'W' : 'K';
      }
    }));
    texturaDeTexto(cena, `caixa_${letra}`, linhas.map((l) => l.join('')), mapa);
  }
}
