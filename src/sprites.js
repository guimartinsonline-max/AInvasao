import { texturaDeTexto, texturaDesenhada, disco } from './pixelart.js';
import { TOUCEIRA, LAMPIAO, LAMPIAO_GORDO, COMIDAS, INIMIGOS, REFEM, DISCO, FEIXE, BODE, EFEITOS, VEICULOS, CENAS, AVIAO, SEGREDOS, BASE } from './quadros.js';
import { BOCAS } from './maos.js';
import { AMBIENTE } from './objetos/Ambiente.js';
import { TREM } from './objetos/Trem.js';
import { VERSAO } from './config.js';
import { PEDACOS, PECAS25 } from './fase1_pedacos.js';

// Personagens e cenário vêm de PNGs gerados por tools/arte/exportar.py.
// Aqui ficam só as texturas pequenas de efeitos, desenhadas em código.

export function carregarSprites(cena) {
  const s = (nome) => `assets/sprites/${nome}.png?v=${VERSAO}`;
  cena.load.spritesheet('lampiao', s('lampiao'), { frameWidth: LAMPIAO.largura, frameHeight: LAMPIAO.altura });
  cena.load.spritesheet('alien', s('alien'), { frameWidth: 40, frameHeight: 44 });
  for (const [nome, q] of Object.entries({ ...INIMIGOS, ...VEICULOS, ...CENAS, ...AVIAO, ...SEGREDOS, refem: REFEM, disco_voador: DISCO, feixe: FEIXE, bode: BODE })) {
    cena.load.spritesheet(nome, s(nome === 'disco_voador' ? 'disco' : nome), { frameWidth: q.largura, frameHeight: q.altura });
  }
  for (const [nome, q] of Object.entries(EFEITOS)) {
    cena.load.spritesheet(nome, s(nome), { frameWidth: q.largura, frameHeight: q.altura });
  }
  cena.load.spritesheet('barril', s('barril'), { frameWidth: 18, frameHeight: 24 });
  cena.load.spritesheet('escudo', s('escudo'), { frameWidth: 16, frameHeight: 30 });
  // Lampião com cada arma pesada nas mãos.
  for (const arma of Object.keys(BOCAS).filter((a) => a !== 'pistola')) {
    cena.load.spritesheet(`lampiao_${arma}`, s(`lampiao_${arma}`), { frameWidth: LAMPIAO.largura, frameHeight: LAMPIAO.altura });
  }
  cena.load.image('maria_bonita', s('maria_bonita'));
  cena.load.image('chapeu', s('chapeu'));
  cena.load.image('cabeca_contaminado', s('cabeca_contaminado'));
  for (const c of ['f2_jogo', 'f2_perto', 'f2_meio', 'f2_longe', 'f2_borda', 'f2_frente', 'ceu_fumaca']) cena.load.image(c, s(c));
  // Fase 2, trecho 2 (acampamento da base): camadas, céus e as peças vivas.
  for (const c of ['f2b_jogo', 'f2b_perto', 'f2b_meio', 'f2b_longe', 'f2b_borda', 'f2b_frente', 'ceu_tarde', 'ceu_noite',
    'plataforma_elevador']) cena.load.image(c, s(c));
  for (const [nome, q] of Object.entries(BASE)) {
    cena.load.spritesheet(nome, s(nome), { frameWidth: q.largura, frameHeight: q.altura });
  }
  cena.load.spritesheet('lampiao_zumbi', s('lampiao_zumbi'), { frameWidth: LAMPIAO.largura, frameHeight: LAMPIAO.altura });
  cena.load.spritesheet('jumento', s('jumento'), { frameWidth: 72, frameHeight: 60 });
  cena.load.spritesheet('retrato', s('retrato'), { frameWidth: 26, frameHeight: 21 });
  cena.load.spritesheet('retrato_gordo', s('retrato_gordo'), { frameWidth: 30, frameHeight: 21 });
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
  for (const nome of ITENS) cena.load.image(`item_${nome}`, s(`item_${nome}`));
  // Cenário vivo da fase 1.
  for (const [nome, q] of Object.entries(AMBIENTE)) {
    cena.load.spritesheet(nome, s(nome), { frameWidth: q.largura, frameHeight: q.altura });
  }
  cena.load.spritesheet('casa_vila_0', s('casa_vila_0'), { frameWidth: 170, frameHeight: 124 });
  cena.load.spritesheet('casa_vila_1', s('casa_vila_1'), { frameWidth: 150, frameHeight: 112 });
  cena.load.spritesheet('touceiras', s('touceiras'), { frameWidth: TOUCEIRA.largura, frameHeight: TOUCEIRA.altura });
  for (const nome of ['ceu', 'nuvens', 'serras', 'paredoes', 'planicie', 'caatinga', 'chao', 'caixote', 'laje', 'f1_ceu', 'f1_nuvens', 'f1_chao']) {
    cena.load.image(nome, s(nome));
  }
  // Camadas da fase 1, em pedaços.
  for (const [nome, n] of Object.entries(PEDACOS)) {
    for (let k = 0; k < n; k++) cena.load.image(`${nome}_${k}`, s(`${nome}_${k}`));
  }
  // Peças baixas em 2.5D (lajedo, girau, sacos, carro de boi), na frente da linha onde se anda.
  for (let k = 0; k < PECAS25; k++) cena.load.image(`f1_p25_${k}`, s(`f1_p25_${k}`));
}

export function gerarSprites(cena) {
  const g = cena.make.graphics({ x: 0, y: 0 }, false);
  g.fillStyle(0xffffff, 1).fillRect(0, 0, 2, 2);
  g.generateTexture('px', 1, 1);
  g.generateTexture('px2', 2, 2);
  g.destroy();

  // Raio verde do xeremita.
  texturaDeTexto(cena, 'raio', ['...90!!?*...', '.90!??**WW*.', '90!?*WWWWW*?', '.90!??**WW*.', '...90!!?*...'], { '*': 'alien_brilho', W: 'branco', '?': 'alien_luz', '!': 'alien', 0: 'alien_medio', 9: 'alien_esc' });
  gerarItens(cena);
  texturaDeTexto(cena, 'capsula', ['ee'], { e: 'amarelo_fogo' });
  // Pedaços de chapa que voam quando um veículo é destroçado (e ficam no chão).
  const chapa = { S: 'sombra', c: 'cinza_escuro', l: 'cinza', b: 'laranja_fogo' };
  texturaDeTexto(cena, 'chapa0', ['.lll..', 'lcccS.', 'cccSSS', '.SS...'], chapa);
  texturaDeTexto(cena, 'chapa1', ['ll.', 'cSl', 'cSS', 'bcS', '.S.'], chapa);
  texturaDeTexto(cena, 'chapa2', ['.llll...', 'lccccll.', '.SSccccS', '...SSSb.'], chapa);
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
  // Medalhas do fim da missão (bronze, prata, ouro): fita verde e amarela e a moeda com a estrela.
  for (const [nome, cores] of Object.entries({
    medalha_bronze: ['couro_profundo', 'couro', 'couro_claro', 'couro_luz'],
    medalha_prata: ['cinza_escuro', 'cinza', 'cinza_luz', 'branco'],
    medalha_ouro: ['laranja_escuro', 'ouro_escuro', 'amarelo_fogo', 'amarelo_claro'],
  })) {
    texturaDesenhada(cena, nome, 24, 34, (ctx, cor) => {
      const px = (x, y, c, w = 1, h = 1) => { ctx.fillStyle = cor(c); ctx.fillRect(x, y, w, h); };
      // Fita em V.
      for (let y = 0; y < 14; y++) {
        px(4 + Math.floor(y / 3), y, 'sombra', 7, 1);
        px(5 + Math.floor(y / 3), y, y % 4 < 2 ? 'caatinga' : 'amarelo_fogo', 5, 1);
        px(13 - Math.floor(y / 3), y, 'sombra', 7, 1);
        px(14 - Math.floor(y / 3), y, y % 4 < 2 ? 'amarelo_fogo' : 'caatinga', 5, 1);
      }
      // Moeda com borda, brilho e estrela.
      for (let y = -10; y <= 10; y++) {
        const m = Math.floor(Math.sqrt(100 - y * y));
        px(12 - m - 1, 22 + y, 'sombra', m * 2 + 2, 1);
        px(12 - m, 22 + y, y < -3 ? cores[3] : y < 4 ? cores[2] : cores[1], m * 2, 1);
      }
      for (let y = -7; y <= 7; y++) {
        const m = Math.floor(Math.sqrt(49 - y * y));
        px(12 - m, 22 + y, cores[0], 1, 1);
        px(12 + m - 1, 22 + y, cores[0], 1, 1);
      }
      const estrela = ['...X...', '...X...', 'XXXXXXX', '.XXXXX.', '..XXX..', '.XX.XX.', 'X.....X'];
      estrela.forEach((l, y) => [...l].forEach((ch, x) => ch === 'X' && px(9 + x, 19 + y, cores[0])));
      px(7, 15, 'branco', 2, 1);
    });
  }
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

// Itens de arma no chão: caixa de chapa com a letra da arma (padrão novo do
// ESTILO.md, desenhada em tools/arte/itens_ms.py). A chave é item_<nome da arma>.
export const ITENS = ['madsen', 'bacamarte', 'rojao', 'desintegrador', 'candeeiro', 'papo_amarelo', 'estilingue', 'buscape', 'granadas'];

export const CAIXA_ITEM = { largura: 24, altura: 22 };

function gerarItens(cena) {
  // Tábua de caixote quebrado.
  texturaDeTexto(cena, 'tabua', ['ssss.', 'ffffs', 'ddddd'], { s: 'fuba_5', f: 'fuba_4', d: 'fuba_2' });
}
