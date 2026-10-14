import { texturaDeTexto, texturaDesenhada, disco } from './pixelart.js';

// Sprites PROVISÓRIOS da etapa 2. O visual final do Lampião e dos inimigos
// ainda vai ser proposto e aprovado (etapa 3).

const MAPA_LAMPIAO = {
  H: 'couro_escuro', h: 'couro_claro', e: 'amarelo_fogo',
  p: 'pele', P: 'pele_escura', o: 'preto',
  c: 'areia', C: 'barro', b: 'couro_escuro', l: 'terra', g: 'cinza_escuro',
};

const LAMPIAO_TRONCO = [
  '.......HHH..........',
  '.....HHhhhHH........',
  '....Hhhheehhh.......',
  '....Hhhhhhhhh.......',
  '.HHHHHHHHHHHHHHH....',
  '.....pppppppp.......',
  '.....ppoopoop.......',
  '.....pppppppPp......',
  '.....PpppoopP.......',
  '......PPPPPP........',
  '....ccccccccc.......',
  '...cbcccccbcc.......',
  '...ccbcccbccpgggggg.',
  '...cccbcbcccpgg.....',
  '...cCccbccCc........',
  '....bbbbbbbbb.......',
];

const PERNAS = {
  parado: [
    '....lllllllll.......',
    '....llll.llll.......',
    '....lll...lll.......',
    '....lll...lll.......',
    '...bbbb..bbbb.......',
    '...bbbbb.bbbbb......',
  ],
  corre1: [
    '....lllllllll.......',
    '...llll..llll.......',
    '..llll....lll.......',
    '.lll......lll.......',
    'bbb......bbbb.......',
    'bbbb.....bbbbb......',
  ],
  corre2: [
    '....lllllllll.......',
    '.....lllllll........',
    '......llll..........',
    '.....lll.ll.........',
    '....bbbb.lbb........',
    '....bbbbbbbb........',
  ],
  pulo: [
    '....lllllllll.......',
    '...llllllllll.......',
    '...lll....llll......',
    '..bbb......bbb......',
    '..bbbb.....bbbb.....',
    '....................',
  ],
};

const LAMPIAO_AGACHADO = [
  ...LAMPIAO_TRONCO,
  '..llllllllllll......',
  '..bbbbb...bbbbb.....',
];

const MAPA_ALIEN = { a: 'alien_esc', A: 'alien', o: 'preto', B: 'alien_brilho' };
const ALIEN = [
  '....aaaaaaa.....',
  '...aAAAAAAAa....',
  '..aAAAAAAAAAa...',
  '..aAoooAoooAa...',
  '..aAoBoAoBoAa...',
  '..aAoooAoooAa...',
  '...aAAAAAAAa....',
  '....aAAaAAa.....',
  '.....aAAAa......',
  '......aAa.......',
  '....aaAAAaa.....',
  '...aAAAAAAAa....',
  '..aA.aAAAa.Aa...',
  '..a..aAAAa..a...',
  '.....aAAAa......',
  '.....aa.aa......',
  '....aa...aa.....',
  '....a.....a.....',
];

export const LAMPIAO_W = 20;
export const LAMPIAO_H = 22;

export function gerarSprites(cena) {
  const g = cena.make.graphics({ x: 0, y: 0 }, false);
  g.fillStyle(0xffffff, 1).fillRect(0, 0, 2, 2);
  g.generateTexture('px', 1, 1);
  g.generateTexture('px2', 2, 2);
  g.destroy();

  for (const [nome, pernas] of Object.entries(PERNAS)) {
    texturaDeTexto(cena, `lamp_${nome}`, [...LAMPIAO_TRONCO, ...pernas], MAPA_LAMPIAO, LAMPIAO_W, LAMPIAO_H);
  }
  texturaDeTexto(cena, 'lamp_agachado', LAMPIAO_AGACHADO, MAPA_LAMPIAO, LAMPIAO_W, LAMPIAO_H);
  texturaDeTexto(cena, 'alien', ALIEN, MAPA_ALIEN);

  texturaDeTexto(cena, 'bala', ['.eeeW', 'eeeWW'], { e: 'amarelo_fogo', W: 'branco' });
  texturaDeTexto(cena, 'capsula', ['ee'], { e: 'amarelo_fogo' });
  texturaDeTexto(cena, 'granada', ['.g.', 'GGG', 'GgG', 'GGG'], { g: 'cinza', G: 'caatinga_esc' });
  texturaDeTexto(cena, 'clarao', [
    '...w...',
    '.w.y.w.',
    '..yWy..',
    'wyWWWyw',
    '..yWy..',
    '.w.y.w.',
    '...w...',
  ], { w: 'amarelo_fogo', y: 'amarelo_fogo', W: 'branco' });
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

  gerarCenario(cena);
}

function gerarCenario(cena) {
  // Serras distantes, em tom frio por causa da distância.
  texturaDesenhada(cena, 'serras', 384, 60, (ctx, cor) => {
    ctx.fillStyle = cor('ceu');
    const picos = [[0, 34], [40, 18], [70, 24], [110, 8], [150, 26], [200, 14], [240, 30], [290, 12], [330, 22], [384, 34]];
    perfil(ctx, picos, 60);
    ctx.fillStyle = cor('horizonte');
    ctx.fillRect(0, 52, 384, 8);
  });
  // Morros médios de areia com sombra azulada.
  texturaDesenhada(cena, 'morros', 384, 50, (ctx, cor) => {
    ctx.fillStyle = cor('cinza_claro');
    perfil(ctx, [[0, 30], [60, 16], [120, 26], [180, 10], [250, 24], [310, 14], [384, 30]], 50);
    ctx.fillStyle = cor('areia_clara');
    perfil(ctx, [[0, 38], [80, 28], [150, 36], [220, 24], [300, 34], [384, 38]], 50);
  });
  // Caatinga: arbustos secos e mandacarus.
  texturaDesenhada(cena, 'mato', 384, 40, (ctx, cor) => {
    for (const [x, w, h] of [[10, 30, 10], [70, 22, 8], [130, 40, 12], [210, 26, 9], [270, 34, 11], [340, 30, 8]]) {
      ctx.fillStyle = cor('caatinga_esc');
      ctx.fillRect(x, 40 - h, w, h);
      ctx.fillStyle = cor('caatinga');
      ctx.fillRect(x + 2, 40 - h - 2, w - 6, 3);
    }
    for (const x of [50, 190, 320]) mandacaru(ctx, cor, x, 40);
  });
  // Chão de terra batida.
  texturaDesenhada(cena, 'chao', 32, 24, (ctx, cor) => {
    ctx.fillStyle = cor('barro');
    ctx.fillRect(0, 0, 32, 24);
    ctx.fillStyle = cor('areia');
    ctx.fillRect(0, 0, 32, 3);
    ctx.fillStyle = cor('terra');
    for (const [x, y] of [[3, 8], [12, 14], [22, 9], [28, 18], [7, 19], [17, 21]]) ctx.fillRect(x, y, 2, 1);
    ctx.fillStyle = cor('areia_clara');
    ctx.fillRect(5, 0, 3, 1);
    ctx.fillRect(20, 0, 4, 1);
  });
  // Caixote de madeira.
  texturaDesenhada(cena, 'caixote', 24, 16, (ctx, cor) => {
    ctx.fillStyle = cor('couro_escuro');
    ctx.fillRect(0, 0, 24, 16);
    ctx.fillStyle = cor('couro_claro');
    ctx.fillRect(1, 1, 22, 14);
    ctx.fillStyle = cor('couro');
    ctx.fillRect(1, 5, 22, 1);
    ctx.fillRect(1, 10, 22, 1);
    ctx.fillStyle = cor('couro_escuro');
    ctx.fillRect(3, 1, 1, 14);
    ctx.fillRect(20, 1, 1, 14);
  });
  // Laje de pedra.
  texturaDesenhada(cena, 'pedra', 32, 12, (ctx, cor) => {
    ctx.fillStyle = cor('azul_sombra');
    ctx.fillRect(0, 0, 32, 12);
    ctx.fillStyle = cor('cinza');
    ctx.fillRect(1, 1, 30, 8);
    ctx.fillStyle = cor('cinza_claro');
    ctx.fillRect(1, 1, 30, 2);
    ctx.fillStyle = cor('cinza_escuro');
    ctx.fillRect(10, 4, 4, 1);
    ctx.fillRect(22, 6, 3, 1);
  });
  // Nuvem.
  texturaDesenhada(cena, 'nuvem', 48, 16, (ctx, cor) => {
    disco(ctx, 14, 9, 6, cor('branco'));
    disco(ctx, 26, 7, 7, cor('branco'));
    disco(ctx, 36, 10, 5, cor('branco'));
    ctx.fillStyle = cor('horizonte');
    ctx.fillRect(9, 13, 32, 2);
  });
}

// Preenche coluna a coluna (sem antisserrilhado, só cores da paleta).
function perfil(ctx, pontos, base) {
  for (let i = 0; i < pontos.length - 1; i++) {
    const [x0, y0] = pontos[i];
    const [x1, y1] = pontos[i + 1];
    for (let x = x0; x < x1; x++) {
      const y = Math.round(y0 + ((y1 - y0) * (x - x0)) / (x1 - x0));
      ctx.fillRect(x, y, 1, base - y);
    }
  }
}

function mandacaru(ctx, cor, x, chao) {
  ctx.fillStyle = cor('caatinga');
  ctx.fillRect(x, chao - 24, 4, 24);
  ctx.fillRect(x - 6, chao - 18, 3, 8);
  ctx.fillRect(x - 6, chao - 11, 6, 3);
  ctx.fillRect(x + 7, chao - 20, 3, 7);
  ctx.fillRect(x + 4, chao - 14, 6, 3);
  ctx.fillStyle = cor('mandacaru');
  ctx.fillRect(x + 1, chao - 24, 1, 22);
}
