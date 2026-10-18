import { texturaDeTexto, texturaDesenhada, disco } from './pixelart.js';
import { TOUCEIRA, LAMPIAO, INIMIGOS, REFEM, DISCO, FEIXE, BODE, EFEITOS, VEICULOS } from './quadros.js';
import { BOCAS } from './maos.js';
import { VERSAO } from './config.js';
import { PEDACOS } from './fase1_pedacos.js';

// Personagens e cenário vêm de PNGs gerados por tools/arte/exportar.py.
// Aqui ficam só as texturas pequenas de efeitos, desenhadas em código.

export function carregarSprites(cena) {
  const s = (nome) => `assets/sprites/${nome}.png?v=${VERSAO}`;
  cena.load.spritesheet('lampiao', s('lampiao'), { frameWidth: LAMPIAO.largura, frameHeight: LAMPIAO.altura });
  cena.load.spritesheet('alien', s('alien'), { frameWidth: 40, frameHeight: 44 });
  for (const [nome, q] of Object.entries({ ...INIMIGOS, ...VEICULOS, refem: REFEM, disco_voador: DISCO, feixe: FEIXE, bode: BODE })) {
    cena.load.spritesheet(nome, s(nome === 'disco_voador' ? 'disco' : nome), { frameWidth: q.largura, frameHeight: q.altura });
  }
  for (const [nome, q] of Object.entries(EFEITOS)) {
    cena.load.spritesheet(nome, s(nome), { frameWidth: q.largura, frameHeight: q.altura });
  }
  cena.load.spritesheet('barril', s('barril'), { frameWidth: 18, frameHeight: 24 });
  cena.load.spritesheet('escudo', s('escudo'), { frameWidth: 12, frameHeight: 26 });
  // Lampião com cada arma pesada nas mãos.
  for (const arma of Object.keys(BOCAS).filter((a) => a !== 'pistola')) {
    cena.load.spritesheet(`lampiao_${arma}`, s(`lampiao_${arma}`), { frameWidth: LAMPIAO.largura, frameHeight: LAMPIAO.altura });
  }
  cena.load.image('maria_bonita', s('maria_bonita'));
  cena.load.spritesheet('touceiras', s('touceiras'), { frameWidth: TOUCEIRA.largura, frameHeight: TOUCEIRA.altura });
  for (const nome of ['ceu', 'nuvens', 'serras', 'paredoes', 'planicie', 'caatinga', 'chao', 'caixote', 'laje']) {
    cena.load.image(nome, s(nome));
  }
  // Camadas da fase 1, em pedaços.
  for (const [nome, n] of Object.entries(PEDACOS)) {
    for (let k = 0; k < n; k++) cena.load.image(`${nome}_${k}`, s(`${nome}_${k}`));
  }
}

export function gerarSprites(cena) {
  const g = cena.make.graphics({ x: 0, y: 0 }, false);
  g.fillStyle(0xffffff, 1).fillRect(0, 0, 2, 2);
  g.generateTexture('px', 1, 1);
  g.generateTexture('px2', 2, 2);
  g.destroy();

  // Raio verde do xeremita.
  texturaDeTexto(cena, 'raio', ['..0!??*.', '90!?*WW*', '..0!??*.'], { '*': 'alien_brilho', W: 'branco', '?': 'alien_luz', '!': 'alien', 0: 'alien_medio', 9: 'alien_esc' });
  gerarItens(cena);
  texturaDeTexto(cena, 'capsula', ['ee'], { e: 'amarelo_fogo' });
  // Banana de dinamite do granadeiro, com o pavio aceso.
  texturaDeTexto(cena, 'dinamite', ['.....yW', 'ORRRRo.', 'OTTTTRo', 'ORRRRo.'], { O: 'sombra', R: 'vermelho_esc', T: 'vermelho', o: 'couro_escuro', y: 'amarelo_fogo', W: 'branco' });
  // Infinito da arma padrão no painel de munição.
  texturaDeTexto(cena, 'infinito', [
    '.WWW.....WWW...',
    'WW.WW...WW.WWo.',
    'W...WW.WW...Wo.',
    'W....WWW....Wo.',
    'W...WW.WW...Wo.',
    'WW.WW.o.WW.WWo.',
    '.WWWo....WWWo..',
    '..ooo.....ooo..',
  ], { W: 'branco', o: 'sombra' });
  texturaDeTexto(cena, 'granada', ['.g.', 'GGG', 'GgG', 'GGG'], { g: 'cinza', G: 'caatinga_esc' });
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

// Itens de arma no estilo Metal Slug: letra grande e grossa, com volume
// (degradê de cima para baixo), extrusão escura para dar profundidade,
// contorno preto e brilho no canto. A chave é item_<nome da arma>.
const LETRAS = {
  M: ['XXX......XXX', 'XXXX....XXXX', 'XXXXX..XXXXX', 'XXX.XXXX.XXX', 'XXX..XX..XXX', 'XXX......XXX',
    'XXX......XXX', 'XXX......XXX', 'XXX......XXX', 'XXX......XXX', 'XXX......XXX', 'XXX......XXX'],
  B: ['XXXXXXXX..', 'XXXXXXXXX.', 'XXX....XXX', 'XXX....XXX', 'XXX...XXX.', 'XXXXXXXX..',
    'XXXXXXXXX.', 'XXX....XXX', 'XXX....XXX', 'XXX....XXX', 'XXXXXXXXX.', 'XXXXXXXX..'],
  R: ['XXXXXXXX..', 'XXXXXXXXX.', 'XXX....XXX', 'XXX....XXX', 'XXX....XXX', 'XXXXXXXXX.',
    'XXXXXXXX..', 'XXX..XXX..', 'XXX...XXX.', 'XXX...XXX.', 'XXX....XXX', 'XXX....XXX'],
  D: ['XXXXXXX...', 'XXXXXXXX..', 'XXX...XXX.', 'XXX....XXX', 'XXX....XXX', 'XXX....XXX',
    'XXX....XXX', 'XXX....XXX', 'XXX....XXX', 'XXX...XXX.', 'XXXXXXXX..', 'XXXXXXX...'],
  C: ['..XXXXXXX.', '.XXXXXXXXX', 'XXX.....XX', 'XXX.......', 'XXX.......', 'XXX.......',
    'XXX.......', 'XXX.......', 'XXX.......', 'XXX.....XX', '.XXXXXXXXX', '..XXXXXXX.'],
  P: ['XXXXXXXX..', 'XXXXXXXXX.', 'XXX....XXX', 'XXX....XXX', 'XXX....XXX', 'XXXXXXXXX.',
    'XXXXXXXX..', 'XXX.......', 'XXX.......', 'XXX.......', 'XXX.......', 'XXX.......'],
  E: ['XXXXXXXXXX', 'XXXXXXXXXX', 'XXX.......', 'XXX.......', 'XXX.......', 'XXXXXXXX..',
    'XXXXXXXX..', 'XXX.......', 'XXX.......', 'XXX.......', 'XXXXXXXXXX', 'XXXXXXXXXX'],
  F: ['XXXXXXXXXX', 'XXXXXXXXXX', 'XXX.......', 'XXX.......', 'XXX.......', 'XXXXXXXX..',
    'XXXXXXXX..', 'XXX.......', 'XXX.......', 'XXX.......', 'XXX.......', 'XXX.......'],
  G: ['..XXXXXX..', '.XXXXXXXX.', 'XXX....XXX', 'XXX.......', 'XXX.......', 'XXX..XXXXX',
    'XXX..XXXXX', 'XXX....XXX', 'XXX....XXX', 'XXX....XXX', '.XXXXXXXX.', '..XXXXXX..'],
};

// Degradê de cada cor: brilho, claro, médio, escuro (extrusão).
const RAMPAS = {
  vermelho: ['amarelo_claro', 'laranja_fogo', 'vermelho', 'vermelho_esc'],
  ouro: ['branco', 'amarelo_claro', 'ouro_escuro', 'laranja_escuro'],
  laranja_fogo: ['amarelo_claro', 'amarelo_fogo', 'laranja_fogo', 'vermelho_medio'],
  alien: ['branco', 'alien_brilho', 'alien', 'alien_profundo'],
  caatinga: ['amarelo_claro', 'mandacaru_luz', 'mandacaru', 'caatinga_esc'],
  azul: ['branco', 'ceu_luz', 'ceu', 'azul_medio'],
  aco: ['branco', 'aco_brilho', 'cinza_luz', 'cinza_escuro'],
  couro: ['areia_clara', 'couro_luz', 'couro_claro', 'couro_escuro'],
  lilas: ['branco', 'lilas_claro', 'lilas', 'roxo_escuro'],
};

export const ITENS = {
  madsen: { letra: 'M', rampa: 'vermelho' },
  bacamarte: { letra: 'B', rampa: 'ouro' },
  rojao: { letra: 'R', rampa: 'laranja_fogo' },
  desintegrador: { letra: 'D', rampa: 'alien' },
  candeeiro: { letra: 'C', rampa: 'azul' },
  papo_amarelo: { letra: 'P', rampa: 'aco' },
  estilingue: { letra: 'E', rampa: 'couro' },
  buscape: { letra: 'F', rampa: 'lilas' },
  granadas: { letra: 'G', rampa: 'caatinga' },
};

function gerarItens(cena) {
  for (const [nome, { letra, rampa }] of Object.entries(ITENS)) {
    const glifo = LETRAS[letra];
    const [brilho, claro, medio, escuro] = RAMPAS[rampa];
    const w = glifo[0].length + 4;
    const h = glifo.length + 4;
    const grade = Array.from({ length: h }, () => Array(w).fill(null));
    const cheio = (x, y) => glifo[y] && glifo[y][x] === 'X';
    // Extrusão: a letra repetida 1 px para baixo e para a direita, em tom escuro.
    glifo.forEach((l, y) => [...l].forEach((ch, x) => { if (ch === 'X') grade[y + 2][x + 2] = escuro; }));
    // Letra com degradê vertical e brilho na quina de cima à esquerda.
    glifo.forEach((l, y) => [...l].forEach((ch, x) => {
      if (ch !== 'X') return;
      let cor = y < 3 ? claro : medio;
      if (y >= glifo.length - 3) cor = medio;
      if (!cheio(x - 1, y) && !cheio(x, y - 1)) cor = brilho;
      else if (!cheio(x, y - 1) && y < 6) cor = brilho;
      grade[y + 1][x + 1] = cor;
    }));
    // Contorno preto em volta de tudo.
    const contorno = grade.map((l) => l.slice());
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        if (grade[y][x]) continue;
        let perto = false;
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) if (grade[y + dy]?.[x + dx]) perto = true;
        if (perto) contorno[y][x] = 'preto';
      }
    }
    texturaDesenhada(cena, `item_${nome}`, w, h, (ctx, cor) => {
      contorno.forEach((l, y) => l.forEach((c, x) => {
        if (!c) return;
        ctx.fillStyle = cor(c);
        ctx.fillRect(x, y, 1, 1);
      }));
    });
  }
  // Tábua de caixote quebrado.
  texturaDeTexto(cena, 'tabua', ['ssss.', 'ffffs', 'ddddd'], { s: 'couro_luz', f: 'couro_claro', d: 'couro' });
}
