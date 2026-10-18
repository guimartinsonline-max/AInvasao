import { texturaDeTexto, texturaDesenhada, disco } from './pixelart.js';
import { TOUCEIRA, LAMPIAO, LAMPIAO_GORDO, COMIDAS, INIMIGOS, REFEM, DISCO, FEIXE, BODE, EFEITOS, VEICULOS } from './quadros.js';
import { BOCAS } from './maos.js';
import { AMBIENTE } from './objetos/Ambiente.js';
import { TREM } from './objetos/Trem.js';
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
  cena.load.image('chapeu', s('chapeu'));
  cena.load.spritesheet('jumento', s('jumento'), { frameWidth: 72, frameHeight: 60 });
  cena.load.image('metralha_jumento', s('metralha_jumento'));
  // Chefe da fase 1: trem blindado e suas partes.
  cena.load.spritesheet('trem_loco', s('trem_loco'), { frameWidth: TREM.loco.largura, frameHeight: TREM.loco.altura });
  cena.load.spritesheet('trem_vagao', s('trem_vagao'), { frameWidth: TREM.vagao.largura, frameHeight: TREM.vagao.altura });
  for (const [nome, c] of Object.entries(TREM.partes)) {
    cena.load.spritesheet(`trem_${nome}`, s(`trem_${nome}`), { frameWidth: c.largura, frameHeight: c.altura });
  }
  cena.load.spritesheet('carvao', s('carvao'), { frameWidth: 8, frameHeight: 8 });
  // Lampião gordo com cada arma, e as comidas.
  cena.load.spritesheet('lampiao_gordo', s('lampiao_gordo'), { frameWidth: LAMPIAO_GORDO.largura, frameHeight: LAMPIAO_GORDO.altura });
  for (const arma of Object.keys(BOCAS).filter((a) => a !== 'pistola')) {
    cena.load.spritesheet(`lampiao_${arma}_gordo`, s(`lampiao_${arma}_gordo`), { frameWidth: LAMPIAO_GORDO.largura, frameHeight: LAMPIAO_GORDO.altura });
  }
  for (const nome of Object.keys(COMIDAS)) cena.load.image(`comida_${nome}`, s(`comida_${nome}`));
  // Cenário vivo da fase 1.
  for (const [nome, q] of Object.entries(AMBIENTE)) {
    cena.load.spritesheet(nome, s(nome), { frameWidth: q.largura, frameHeight: q.altura });
  }
  cena.load.spritesheet('casa_vila_0', s('casa_vila_0'), { frameWidth: 130, frameHeight: 84 });
  cena.load.spritesheet('casa_vila_1', s('casa_vila_1'), { frameWidth: 110, frameHeight: 72 });
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
  // Poça de sangue no chão (elipse achatada pixelada, borda escura e brilho).
  texturaDesenhada(cena, 'poca', 30, 6, (ctx, cor) => {
    for (let y = 0; y < 6; y++) {
      const meia = Math.floor(Math.sqrt(1 - ((y - 2.5) / 3) ** 2) * 15);
      ctx.fillStyle = cor(y === 0 || y === 5 ? 'vermelho_esc' : 'vermelho_medio');
      ctx.fillRect(15 - meia, y, meia * 2, 1);
      ctx.fillStyle = cor('vermelho_esc');
      ctx.fillRect(15 - meia, y, 1, 1);
      ctx.fillRect(15 + meia - 1, y, 1, 1);
    }
    ctx.fillStyle = cor('vermelho');
    ctx.fillRect(9, 1, 6, 1);
    ctx.fillStyle = cor('laranja_fogo');
    ctx.fillRect(10, 1, 2, 1);
  });
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

// Caixa do item, como no Metal Slug: quadrado de chapa com bisel (luz em cima à
// esquerda, sombra embaixo à direita), rebites nos cantos, fundo afundado escuro
// e a letra grossa colorida da arma no meio, com extrusão e contorno.
export const CAIXA_ITEM = { largura: 24, altura: 22 };

function gerarItens(cena) {
  const { largura: W, altura: H } = CAIXA_ITEM;
  for (const [nome, { letra, rampa }] of Object.entries(ITENS)) {
    const glifo = LETRAS[letra];
    const [brilho, claro, medio, escuro] = RAMPAS[rampa];
    const grade = Array.from({ length: H }, () => Array(W).fill(null));
    const pinta = (x, y, c) => { if (y >= 0 && y < H && x >= 0 && x < W) grade[y][x] = c; };
    // Chapa da caixa (1 px de contorno preto em volta).
    for (let y = 1; y < H - 1; y++) {
      for (let x = 1; x < W - 1; x++) {
        const borda = Math.min(x - 1, y - 1, W - 2 - x, H - 2 - y);
        let c = 'cinza';
        if (borda <= 1) c = (x - 1 < 2 || y - 1 < 2) && x + y < W + H - 8 ? 'cinza_claro' : 'cinza_escuro';
        if (borda === 0 && (x === 1 || y === 1)) c = 'branco';
        if (borda === 0 && (x === W - 2 || y === H - 2)) c = 'sombra';
        pinta(x, y, c);
      }
    }
    // Fundo afundado onde fica a letra (sombra em cima/esquerda, luz embaixo/direita).
    for (let y = 4; y < H - 4; y++) {
      for (let x = 4; x < W - 4; x++) {
        let c = 'sombra';
        if (y === 4 || x === 4) c = 'preto';
        if (y === H - 5 || x === W - 5) c = 'cinza_medio';
        pinta(x, y, c);
      }
    }
    // Rebites.
    for (const [x, y] of [[3, 3], [W - 4, 3], [3, H - 4], [W - 4, H - 4]]) {
      pinta(x, y, 'cinza_luz');
      pinta(x + 1, y + 1, 'sombra_media');
    }
    // Faixa colorida da arma no topo da chapa.
    for (let x = 6; x < W - 6; x++) pinta(x, 2, medio);
    // Letra: centralizada no fundo, com extrusão escura e degradê.
    const lw = glifo[0].length;
    const lh = glifo.length;
    const ox = Math.floor((W - lw) / 2) - 1;
    const oy = Math.floor((H - lh) / 2) - 1;
    const cheio = (x, y) => glifo[y] && glifo[y][x] === 'X';
    glifo.forEach((l, y) => [...l].forEach((ch, x) => {
      if (ch !== 'X') return;
      pinta(ox + x + 1, oy + y + 1, escuro);
      pinta(ox + x + 2, oy + y + 1, 'preto');
    }));
    glifo.forEach((l, y) => [...l].forEach((ch, x) => {
      if (ch !== 'X') return;
      let cor = y < lh / 2 ? claro : medio;
      if (!cheio(x - 1, y) && !cheio(x, y - 1)) cor = brilho;
      else if (!cheio(x, y - 1) && y < 5) cor = brilho;
      pinta(ox + x, oy + y, cor);
    }));
    // Contorno preto em volta da caixa.
    const final = grade.map((l) => l.slice());
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        if (grade[y][x]) continue;
        let perto = false;
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) if (grade[y + dy]?.[x + dx]) perto = true;
        if (perto) final[y][x] = 'preto';
      }
    }
    texturaDesenhada(cena, `item_${nome}`, W, H, (ctx, cor) => {
      final.forEach((l, y) => l.forEach((c, x) => {
        if (!c) return;
        ctx.fillStyle = cor(c);
        ctx.fillRect(x, y, 1, 1);
      }));
    });
  }
  // Tábua de caixote quebrado.
  texturaDeTexto(cena, 'tabua', ['ssss.', 'ffffs', 'ddddd'], { s: 'couro_luz', f: 'couro_claro', d: 'couro' });
}
