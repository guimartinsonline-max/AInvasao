// Som do jogo (Web Audio). Tiros, explosões e a bateria são amostras em mp3
// (assets/sons/, geradas por tools/som/gerar_sons.py: camadas de estalo,
// estrondo, mecânica e eco). O resto é sintetizado na hora. A trilha é tocada
// em tempo real: bateria de amostras, guitarra distorcida, baixo, metais e
// sanfona. Volumes vêm dos ajustes (0 a 10).
import { ajustes, aoMudarAjustes } from './ajustes.js';
import { VERSAO } from './config.js';

let ctx = null;
let mestreEfeitos = null;
let mestreMusica = null;
let ruido = null;

function iniciar() {
  if (ctx) return ctx;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return null;
  ctx = new AC();
  mestreEfeitos = ctx.createGain();
  mestreMusica = ctx.createGain();
  // Um compressor segura as explosões em cadeia sem estourar o alto-falante.
  const comp = ctx.createDynamicsCompressor();
  comp.threshold.value = -14;
  comp.ratio.value = 6;
  mestreEfeitos.connect(comp).connect(ctx.destination);
  mestreMusica.connect(ctx.destination);
  // Ruído branco (1 s) para tiros, explosões e chiados.
  ruido = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
  const d = ruido.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  aplicarVolumes();
  carregarAmostras();
  return ctx;
}

// ---------------------------------------------------------------- amostras
const AMOSTRAS = ['pistola', 'madsen', 'bacamarte', 'papo_amarelo', 'rojao', 'desintegrador', 'candeeiro',
  'estilingue', 'buscape', 'metralha_jumento', 'tiro_inimigo', 'tiro_pesado', 'canhao', 'explosao_p',
  'explosao_m', 'explosao_g', 'impacto', 'ricochete', 'faca', 'recarga',
  'bumbo', 'caixa', 'chimbal', 'chimbal_aberto', 'prato', 'surdo', 'zabumba'];
const buf = {};

function carregarAmostras() {
  for (const nome of AMOSTRAS) {
    fetch(`assets/sons/${nome}.mp3?v=${VERSAO}`)
      .then((r) => r.arrayBuffer())
      .then((dados) => new Promise((ok, erro) => ctx.decodeAudioData(dados, ok, erro)))
      .then((b) => { buf[nome] = b; })
      .catch(() => {}); // sem a amostra, fica o som sintetizado
  }
}

// Toca uma amostra; varia um pouco o tom a cada disparo para não soar repetido.
function amostra(nome, t, { vol = 1, tom = 1, varia = 0.05, destino = null } = {}) {
  const b = buf[nome];
  if (!b) return false;
  const f = ctx.createBufferSource();
  f.buffer = b;
  f.playbackRate.value = tom * (1 + (Math.random() * 2 - 1) * varia);
  const g = ctx.createGain();
  g.gain.value = vol;
  f.connect(g).connect(destino || mestreEfeitos);
  f.start(t);
  return true;
}

// Que amostra cada efeito usa (nome, volume, tom).
const EFEITO = {
  pistola: ['pistola', 0.9], madsen: ['madsen', 0.8], bacamarte: ['bacamarte', 1], papo_amarelo: ['papo_amarelo', 1],
  rojao: ['rojao', 0.9], desintegrador: ['desintegrador', 0.7], candeeiro: ['candeeiro', 0.6],
  estilingue: ['estilingue', 0.8], buscape: ['buscape', 0.7], metralha_jumento: ['metralha_jumento', 0.85],
  tiro_inimigo: ['tiro_inimigo', 0.45], tiro_pesado: ['tiro_pesado', 0.6], canhao: ['canhao', 0.9],
  impacto: ['impacto', 0.35], faca: ['faca', 0.9], chamine: ['explosao_p', 0.35, 1.4],
};

function aplicarVolumes() {
  if (!ctx) return;
  // Curva quadrática: o meio do controle soa como meio volume.
  mestreEfeitos.gain.value = (ajustes.efeitos / 10) ** 2 * 0.5;
  mestreMusica.gain.value = (ajustes.musica / 10) ** 2 * 0.22;
}
aoMudarAjustes(aplicarVolumes);

// O iPhone só libera o som depois de um toque ou tecla.
export function liberarSom() {
  const c = iniciar();
  if (c && c.state === 'suspended') c.resume();
}
for (const ev of ['pointerdown', 'keydown', 'touchend']) window.addEventListener(ev, liberarSom, { passive: true });

const pronto = () => iniciar() && ctx.state === 'running';

function nota(destino, freq, inicio, dur, { onda = 'square', vol = 1, desliza = 0, vibrato = 0 } = {}) {
  const o = ctx.createOscillator();
  const g = ctx.createGain();
  o.type = onda;
  o.frequency.setValueAtTime(freq, inicio);
  if (desliza) o.frequency.exponentialRampToValueAtTime(Math.max(30, freq * desliza), inicio + dur);
  if (vibrato) {
    const lfo = ctx.createOscillator();
    const lg = ctx.createGain();
    lfo.frequency.value = vibrato;
    lg.gain.value = freq * 0.06;
    lfo.connect(lg).connect(o.frequency);
    lfo.start(inicio);
    lfo.stop(inicio + dur + 0.02);
  }
  g.gain.setValueAtTime(0.0001, inicio);
  g.gain.exponentialRampToValueAtTime(vol, inicio + 0.006);
  g.gain.exponentialRampToValueAtTime(0.0001, inicio + dur);
  o.connect(g).connect(destino);
  o.start(inicio);
  o.stop(inicio + dur + 0.02);
}

// Chiado de ruído filtrado (tiro, explosão, fogo, madeira).
function chiado(inicio, dur, { vol = 1, filtro = 'lowpass', de = 4000, ate = 400, q = 0.7 } = {}) {
  const s = ctx.createBufferSource();
  s.buffer = ruido;
  const f = ctx.createBiquadFilter();
  f.type = filtro;
  f.Q.value = q;
  f.frequency.setValueAtTime(de, inicio);
  f.frequency.exponentialRampToValueAtTime(Math.max(40, ate), inicio + dur);
  const g = ctx.createGain();
  g.gain.setValueAtTime(vol, inicio);
  g.gain.exponentialRampToValueAtTime(0.0001, inicio + dur);
  s.connect(f).connect(g).connect(mestreEfeitos);
  s.start(inicio, Math.random() * 0.5);
  s.stop(inicio + dur + 0.02);
}

// ---------------------------------------------------------------- efeitos
const ultimo = {};
const INTERVALO = { tiro_inimigo: 60, impacto: 40, grito: 90, madeira: 50, explosao: 50, quique: 60 };

// Versões sintetizadas: tocam enquanto as amostras ainda carregam e cobrem os
// sons que não têm amostra (menus, comida, galinha...).
const SINTE = {
  // Armas do Lampião.
  pistola: (t) => { chiado(t, 0.07, { vol: 0.7, de: 6000, ate: 800 }); nota(mestreEfeitos, 900, t, 0.08, { vol: 0.35, desliza: 0.2 }); },
  madsen: (t) => { chiado(t, 0.05, { vol: 0.6, de: 5000, ate: 900 }); nota(mestreEfeitos, 520, t, 0.05, { vol: 0.3, desliza: 0.3 }); },
  bacamarte: (t) => { chiado(t, 0.28, { vol: 1, de: 3000, ate: 150 }); nota(mestreEfeitos, 120, t, 0.2, { onda: 'sine', vol: 0.9, desliza: 0.4 }); },
  papo_amarelo: (t) => { chiado(t, 0.16, { vol: 0.9, filtro: 'highpass', de: 3000, ate: 600 }); nota(mestreEfeitos, 1400, t, 0.12, { vol: 0.35, desliza: 0.15 }); },
  rojao: (t) => { chiado(t, 0.35, { vol: 0.6, filtro: 'bandpass', de: 600, ate: 3000, q: 2 }); },
  desintegrador: (t) => { nota(mestreEfeitos, 300, t, 0.22, { onda: 'sine', vol: 0.6, desliza: 5, vibrato: 30 }); },
  candeeiro: (t) => { chiado(t, 0.16, { vol: 0.6, de: 1500, ate: 300 }); },
  estilingue: (t) => { nota(mestreEfeitos, 620, t, 0.08, { onda: 'triangle', vol: 0.6, desliza: 0.45 }); },
  buscape: (t) => { nota(mestreEfeitos, 1500, t, 0.18, { onda: 'sawtooth', vol: 0.25, desliza: 1.7 }); chiado(t, 0.18, { vol: 0.3, filtro: 'highpass', de: 4000, ate: 6000 }); },
  metralha_jumento: (t) => { chiado(t, 0.06, { vol: 0.65, de: 4500, ate: 700 }); nota(mestreEfeitos, 380, t, 0.05, { vol: 0.3, desliza: 0.3 }); },
  // Inimigos e mundo.
  raio_et: (t) => { nota(mestreEfeitos, 900, t, 0.18, { onda: 'sine', vol: 0.4, desliza: 0.3, vibrato: 40 }); chiado(t, 0.08, { vol: 0.2, filtro: 'bandpass', de: 3000, ate: 1500, q: 2 }); },
  chamine: (t) => { chiado(t, 0.35, { vol: 0.5, de: 1200, ate: 200 }); },
  tiro_inimigo: (t) => { chiado(t, 0.06, { vol: 0.35, de: 3500, ate: 700 }); nota(mestreEfeitos, 480, t, 0.07, { vol: 0.15, desliza: 0.25 }); },
  explosao: (t, tam = 1) => {
    chiado(t, 0.45 * tam + 0.15, { vol: Math.min(1.2, 0.7 * tam + 0.3), de: 2500, ate: 80 });
    nota(mestreEfeitos, 90, t, 0.35 * tam + 0.1, { onda: 'sine', vol: 1, desliza: 0.35 });
  },
  impacto: (t) => chiado(t, 0.03, { vol: 0.25, filtro: 'highpass', de: 5000, ate: 3000 }),
  faca: (t) => { chiado(t, 0.1, { vol: 0.6, filtro: 'highpass', de: 3000, ate: 8000 }); nota(mestreEfeitos, 2200, t, 0.08, { onda: 'triangle', vol: 0.25, desliza: 1.4 }); },
  grito: (t) => { const f = 500 + Math.random() * 300; nota(mestreEfeitos, f, t, 0.22, { onda: 'square', vol: 0.18, desliza: 0.45, vibrato: 18 }); },
  madeira: (t) => { chiado(t, 0.14, { vol: 0.6, filtro: 'bandpass', de: 900, ate: 400, q: 1.5 }); nota(mestreEfeitos, 160, t, 0.08, { onda: 'triangle', vol: 0.4 }); },
  item: (t) => [880, 1175, 1568].forEach((f, k) => nota(mestreEfeitos, f, t + k * 0.05, 0.09, { vol: 0.35 })),
  comer: (t) => { nota(mestreEfeitos, 520, t, 0.06, { vol: 0.35, desliza: 0.7 }); nota(mestreEfeitos, 700, t + 0.08, 0.08, { vol: 0.35, desliza: 0.7 }); },
  pulo: (t) => nota(mestreEfeitos, 280, t, 0.09, { onda: 'square', vol: 0.12, desliza: 2 }),
  morte: (t) => { nota(mestreEfeitos, 700, t, 0.7, { onda: 'sawtooth', vol: 0.3, desliza: 0.1, vibrato: 9 }); chiado(t, 0.2, { vol: 0.5, de: 2000, ate: 300 }); },
  refem: (t) => [523, 659, 784, 1046].forEach((f, k) => nota(mestreEfeitos, f, t + k * 0.08, 0.12, { vol: 0.3 })),
  zurro: (t) => [300, 170, 300, 170].forEach((f, k) => nota(mestreEfeitos, f, t + k * 0.16, 0.16, { onda: 'sawtooth', vol: 0.25, vibrato: 12 })),
  apito: (t) => { nota(mestreEfeitos, 880, t, 0.9, { onda: 'sine', vol: 0.35, vibrato: 6 }); nota(mestreEfeitos, 1108, t, 0.9, { onda: 'sine', vol: 0.3, vibrato: 6 }); chiado(t, 0.9, { vol: 0.2, filtro: 'highpass', de: 5000, ate: 4000 }); },
  quique: (t) => nota(mestreEfeitos, 320, t, 0.05, { onda: 'triangle', vol: 0.3 }),
  arremesso: (t) => chiado(t, 0.1, { vol: 0.3, filtro: 'bandpass', de: 800, ate: 2500, q: 1.5 }),
  alerta: (t) => { nota(mestreEfeitos, 1000, t, 0.06, { vol: 0.25 }); nota(mestreEfeitos, 1000, t + 0.1, 0.06, { vol: 0.25 }); },
  galinha: (t) => [900, 1200, 800].forEach((f, k) => nota(mestreEfeitos, f, t + k * 0.06, 0.06, { onda: 'square', vol: 0.12 })),
  engordar: (t) => nota(mestreEfeitos, 400, t, 0.4, { onda: 'square', vol: 0.25, desliza: 0.35, vibrato: 8 }),
};

export function som(nome, ...args) {
  if (!pronto()) return;
  const agora = performance.now();
  if (agora - (ultimo[nome] || 0) < (INTERVALO[nome] || 25)) return;
  ultimo[nome] = agora;
  const t = ctx.currentTime;
  if (nome === 'explosao') {
    const tam = args[0] ?? 1;
    const chave = tam < 0.7 ? 'explosao_p' : tam < 1.25 ? 'explosao_m' : 'explosao_g';
    if (amostra(chave, t, { vol: Math.min(1.1, 0.6 + tam * 0.35) })) return;
  } else if (nome === 'impacto') {
    // De vez em quando a bala ricocheteia.
    if (amostra(Math.random() < 0.15 ? 'ricochete' : 'impacto', t, { vol: 0.35, varia: 0.15 })) return;
  } else if (EFEITO[nome]) {
    const [a, vol, tom = 1] = EFEITO[nome];
    if (amostra(a, t, { vol, tom })) return;
  }
  if (SINTE[nome]) SINTE[nome](t, ...args);
}

// Bipes dos menus.
export function bip(tipo = 'mover') {
  if (!pronto()) return;
  const t = ctx.currentTime;
  if (tipo === 'mover') nota(mestreEfeitos, 660, t, 0.06, { vol: 0.5 });
  else if (tipo === 'confirmar') {
    nota(mestreEfeitos, 523, t, 0.07, { vol: 0.6 });
    nota(mestreEfeitos, 784, t + 0.07, 0.12, { vol: 0.6 });
  } else if (tipo === 'voltar') nota(mestreEfeitos, 440, t, 0.12, { vol: 0.5, desliza: 0.6 });
  else if (tipo === 'erro') nota(mestreEfeitos, 150, t, 0.15, { onda: 'sawtooth', vol: 0.4 });
}


// ---------------------------------------------------------------- músicas
// Trilha de ação no espírito do Metal Slug, com sotaque nordestino: bateria de
// rock com zabumba de baião, guitarra distorcida, baixo em colcheias, metais
// nas viradas e a melodia na sanfona (na segunda volta, na guitarra solo).
const N = (nome) => {
  const base = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  const m = nome.match(/^([A-G])([b#]?)(\d)$/);
  const semis = base[m[1]] + (m[2] === 'b' ? -1 : m[2] === '#' ? 1 : 0) + (Number(m[3]) - 4) * 12;
  return 440 * 2 ** ((semis - 9) / 12);
};

// Levadas em 16 semicolcheias. x = toque, o = chimbal aberto, m = guitarra abafada.
const LEVADAS = {
  baiao: {
    bumbo: 'x.....x.x.....x.', caixa: '....x.......x...', chimbal: 'x.x.x.x.x.x.x.xo', zabumba: 'x.....x.x.......',
    guitarra: 'x.m.m.x.x.m.m.x.', baixo: [0, 0, 12, 0, 0, 7, 12, 7],
  },
  galope: {
    bumbo: 'x.xxx.xxx.xxx.xx', caixa: '....x.......x...', chimbal: 'x.x.x.x.x.x.x.x.', zabumba: '................',
    guitarra: 'x.mmx.mmx.mmx.mm', baixo: [0, 0, 0, 0, 0, 0, 0, 0],
  },
  marcha: {
    bumbo: 'x.......x.x.....', caixa: '....x..x....x.xx', chimbal: 'x.x.x.x.x.x.x.x.', zabumba: '................',
    guitarra: 'x.......x.......', baixo: [0, 0, 7, 0, 0, 0, 7, 12],
  },
  lento: {
    bumbo: 'x...............', caixa: '................', chimbal: '................', zabumba: '........x.......',
    guitarra: 'x...............', baixo: [0, null, null, null, null, null, null, null],
  },
};

// Cada música: andamento, levada e seções (acorde por compasso + melodia em
// [nota, semicolcheias], 16 por compasso). As seções se alternam em loop.
const MUSICAS = {
  // Tela de início: baião-rock em sol mixolídio, heroico.
  tema: {
    bpm: 124, loop: true, levada: 'baiao',
    secoes: [{
      acordes: ['G2', 'G2', 'F2', 'F2', 'G2', 'C3', 'F2', 'G2'],
      melodia: [['G4', 2], ['B4', 2], ['D5', 3], ['C5', 1], ['B4', 2], ['A4', 2], ['G4', 4],
        ['F4', 2], ['G4', 2], ['A4', 2], ['B4', 2], ['C5', 3], ['B4', 1], ['A4', 4],
        ['G4', 2], ['B4', 2], ['D5', 3], ['E5', 1], ['F5', 2], ['E5', 2], ['D5', 4],
        ['C5', 2], ['A4', 2], ['F4', 2], ['A4', 2], ['G4', 6], [null, 2],
        ['D5', 2], ['D5', 1], ['E5', 1], ['F5', 2], ['G5', 2], ['A5', 4], ['G5', 4],
        ['F5', 2], ['E5', 2], ['D5', 2], ['C5', 2], ['D5', 8],
        ['B4', 2], ['C5', 2], ['D5', 2], ['E5', 2], ['F5', 4], ['E5', 2], ['C5', 2],
        ['D5', 4], ['B4', 4], ['G4', 8]],
    }],
  },
  // Fase 1: xaxado-rock ligeiro em ré dório.
  caatinga: {
    bpm: 150, loop: true, levada: 'baiao',
    secoes: [{
      acordes: ['D2', 'D2', 'C3', 'C3', 'D2', 'G2', 'C3', 'D2'],
      melodia: [['D5', 1], ['E5', 1], ['F5', 2], ['E5', 1], ['D5', 1], ['C5', 2], ['D5', 2], ['A4', 2], [null, 2], ['A4', 1], ['B4', 1],
        ['C5', 2], ['B4', 1], ['A4', 1], ['G4', 2], ['A4', 2], ['E4', 4], [null, 4],
        ['D5', 1], ['E5', 1], ['F5', 2], ['G5', 2], ['A5', 2], ['G5', 1], ['F5', 1], ['E5', 2], ['D5', 2], ['C5', 2],
        ['B4', 2], ['C5', 2], ['A4', 2], ['G4', 2], ['A4', 6], [null, 2],
        ['D5', 1], ['E5', 1], ['F5', 2], ['E5', 1], ['D5', 1], ['C5', 2], ['D5', 2], ['A4', 2], [null, 2], ['A4', 1], ['B4', 1],
        ['C5', 2], ['B4', 1], ['A4', 1], ['G4', 2], ['A4', 2], ['E4', 4], [null, 4],
        ['F5', 2], ['E5', 2], ['D5', 2], ['C5', 2], ['B4', 2], ['C5', 2], ['D5', 4],
        ['A4', 4], ['D5', 4], ['D5', 8]],
    }, {
      acordes: ['F2', 'F2', 'C3', 'C3', 'G2', 'G2', 'A2', 'A2'],
      melodia: [['A5', 2], ['G5', 2], ['F5', 2], ['E5', 2], ['F5', 4], ['D5', 4],
        ['C5', 4], ['D5', 2], ['E5', 2], ['F5', 6], [null, 2],
        ['G5', 2], ['F5', 2], ['E5', 2], ['D5', 2], ['E5', 4], ['C5', 4],
        ['G4', 4], ['A4', 2], ['C5', 2], ['D5', 6], [null, 2],
        ['D5', 1], ['E5', 1], ['F5', 1], ['G5', 1], ['A5', 4], ['G5', 2], ['F5', 2], ['E5', 2], ['D5', 2],
        ['E5', 2], ['F5', 2], ['G5', 4], ['A5', 4], [null, 4],
        ['A5', 2], ['C6', 2], ['A5', 2], ['G5', 2], ['F5', 2], ['E5', 2], ['D5', 2], ['C5', 2],
        ['A4', 4], ['E5', 4], ['A5', 4], [null, 4]],
    }],
  },
  // Chefe: lá menor harmônico, galope de bumbo duplo.
  chefe: {
    bpm: 172, loop: true, levada: 'galope',
    secoes: [{
      acordes: ['A2', 'A2', 'F2', 'F2', 'D2', 'D2', 'E2', 'E2'],
      melodia: [['A4', 2], ['C5', 2], ['E5', 2], ['A5', 2], ['G#5', 2], ['E5', 2], ['B4', 4],
        ['C5', 2], ['A4', 2], ['F4', 2], ['A4', 2], ['G#4', 6], [null, 2],
        ['A4', 2], ['C5', 2], ['E5', 2], ['F5', 2], ['E5', 2], ['D5', 2], ['C5', 2], ['B4', 2],
        ['A4', 2], ['B4', 2], ['G#4', 2], ['E4', 2], ['A4', 6], [null, 2],
        ['F5', 2], ['E5', 2], ['D5', 2], ['C5', 2], ['D5', 4], ['A4', 4],
        ['D5', 2], ['F5', 2], ['A5', 4], ['G#5', 4], ['F5', 4],
        ['E5', 2], ['G#5', 2], ['B5', 2], ['E6', 2], ['D6', 4], ['B5', 4],
        ['G#5', 2], ['E5', 2], ['B4', 2], ['G#4', 2], ['E4', 8]],
    }, {
      acordes: ['D2', 'D2', 'A2', 'A2', 'F2', 'G2', 'E2', 'E2'],
      melodia: [['D5', 2], ['F5', 2], ['A5', 4], ['G#5', 2], ['A5', 2], ['F5', 4],
        ['E5', 2], ['D5', 2], ['C5', 2], ['B4', 2], ['C5', 4], ['D5', 4],
        ['E5', 2], ['C5', 2], ['A4', 4], ['C5', 2], ['E5', 2], ['A5', 4],
        ['G#5', 4], ['F5', 2], ['E5', 2], ['F5', 4], ['E5', 4],
        ['F5', 2], ['A5', 2], ['C6', 4], ['B5', 2], ['A5', 2], ['G#5', 4],
        ['G5', 2], ['F5', 2], ['E5', 2], ['D5', 2], ['G5', 4], ['B4', 4],
        ['E5', 1], ['F5', 1], ['E5', 1], ['D#5', 1], ['E5', 4], ['G#5', 4], ['B5', 4],
        ['E6', 4], ['D6', 2], ['C6', 2], ['B5', 4], ['G#5', 4]],
    }],
  },
  // Missão cumprida: fanfarra de metais com caixa marcial.
  vitoria: {
    bpm: 132, loop: false, levada: 'marcha',
    secoes: [{
      acordes: ['C3', 'G2', 'F2', 'C3'],
      melodia: [['C5', 2], ['E5', 2], ['G5', 2], ['C6', 4], ['B5', 1], ['C6', 1], ['D6', 4],
        ['B5', 2], ['G5', 2], ['A5', 4], ['F5', 4], ['A5', 2], ['C6', 2],
        ['C6', 16]],
    }],
  },
  // Sem vidas: lamento descendo.
  derrota: {
    bpm: 84, loop: false, levada: 'lento',
    secoes: [{
      acordes: ['A2', 'E2'],
      melodia: [['E5', 4], ['D5', 4], ['C5', 4], ['B4', 4], ['A4', 12], [null, 4]],
    }],
  },
};

// Melodia de cada seção quebrada por compasso: [compasso, início em semis, nota, duração].
for (const m of Object.values(MUSICAS)) {
  for (const s of m.secoes) {
    s.porCompasso = s.acordes.map(() => []);
    let pos = 0;
    for (const [n, d] of s.melodia) {
      const c = Math.floor(pos / 16);
      if (n && c < s.acordes.length) s.porCompasso[c].push([pos - c * 16, N(n), d]);
      pos += d;
    }
  }
}

// Curva de distorção (válvula saturada).
function curvaDistorcao(k) {
  const n = 1024;
  const c = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const x = (i / (n - 1)) * 2 - 1;
    c[i] = ((1 + k) * x) / (1 + k * Math.abs(x));
  }
  return c;
}

// Instrumentos de uma música (cadeias de efeito criadas uma vez por faixa).
function montarBanda(saida) {
  const b = { saida };
  // Guitarra base: acordes de quinta somados numa distorção pesada e caixa de som.
  b.guitarra = ctx.createGain();
  b.guitarra.gain.value = 0.5;
  const dist = ctx.createWaveShaper();
  dist.curve = curvaDistorcao(60);
  dist.oversample = '2x';
  const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 90;
  const caixaSom = ctx.createBiquadFilter(); caixaSom.type = 'lowpass'; caixaSom.frequency.value = 3200; caixaSom.Q.value = 0.9;
  const medio = ctx.createBiquadFilter(); medio.type = 'peaking'; medio.frequency.value = 800; medio.gain.value = -5;
  const volG = ctx.createGain(); volG.gain.value = 0.16;
  b.guitarra.connect(dist).connect(hp).connect(medio).connect(caixaSom).connect(volG).connect(saida);
  // Guitarra solo: distorção mais macia, com eco.
  b.solo = ctx.createGain();
  const dist2 = ctx.createWaveShaper(); dist2.curve = curvaDistorcao(25);
  const lp2 = ctx.createBiquadFilter(); lp2.type = 'lowpass'; lp2.frequency.value = 3800;
  const volS = ctx.createGain(); volS.gain.value = 0.14;
  const eco = ctx.createDelay(1); eco.delayTime.value = 0.18;
  const voltaEco = ctx.createGain(); voltaEco.gain.value = 0.28;
  b.solo.connect(dist2).connect(lp2).connect(volS).connect(saida);
  volS.connect(eco).connect(voltaEco).connect(eco);
  voltaEco.connect(saida);
  // Baixo: serra com sub e filtro fechado, levemente sujo.
  b.baixo = ctx.createGain();
  const lpB = ctx.createBiquadFilter(); lpB.type = 'lowpass'; lpB.frequency.value = 700; lpB.Q.value = 2;
  const distB = ctx.createWaveShaper(); distB.curve = curvaDistorcao(4);
  const volB = ctx.createGain(); volB.gain.value = 0.42;
  b.baixo.connect(distB).connect(lpB).connect(volB).connect(saida);
  // Sanfona e metais vão direto, com um pouco do eco.
  b.lead = ctx.createGain(); b.lead.gain.value = 0.2;
  b.lead.connect(saida);
  b.lead.connect(eco);
  b.bateria = ctx.createGain(); b.bateria.gain.value = 1.1;
  b.bateria.connect(saida);
  return b;
}

function osc(destino, tipo, freq, t, dur, vol, ataque = 0.005, solta = 0.05, detune = 0) {
  const o = ctx.createOscillator();
  o.type = tipo;
  o.frequency.value = freq;
  o.detune.value = detune;
  const g = ctx.createGain();
  g.gain.setValueAtTime(0.0001, t);
  g.gain.linearRampToValueAtTime(vol, t + ataque);
  g.gain.setValueAtTime(vol, t + Math.max(ataque, dur - solta));
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g).connect(destino);
  o.start(t);
  o.stop(t + dur + 0.02);
  return o;
}

// Acorde de quinta (tônica, quinta, oitava) na guitarra distorcida.
function powerChord(b, f, t, dur, abafado) {
  const v = abafado ? 0.5 : 0.8;
  const d = abafado ? Math.min(dur, 0.09) : dur;
  for (const [st, det] of [[0, -6], [7, 5], [12, 0]]) osc(b.guitarra, 'sawtooth', f * 2 * 2 ** (st / 12), t, d, v / 3, 0.003, 0.03, det);
}

function sanfona(b, f, t, dur) {
  // Duas palhetas desafinadas de leve e um vibrato de fole.
  for (const det of [-7, 7]) {
    const o = osc(b.lead, 'square', f, t, dur, 0.22, 0.015, 0.04, det);
    const lfo = ctx.createOscillator(); lfo.frequency.value = 5.5;
    const prof = ctx.createGain(); prof.gain.value = 6;
    lfo.connect(prof).connect(o.detune);
    lfo.start(t); lfo.stop(t + dur + 0.02);
  }
}

function guitarraSolo(b, f, t, dur) {
  const o = osc(b.solo, 'sawtooth', f, t, dur, 0.5, 0.004, 0.06);
  // Puxada de corda no começo da nota e vibrato no fim das longas.
  o.frequency.setValueAtTime(f * 0.97, t);
  o.frequency.linearRampToValueAtTime(f, t + 0.04);
  if (dur > 0.3) {
    const lfo = ctx.createOscillator(); lfo.frequency.value = 6;
    const prof = ctx.createGain(); prof.gain.setValueAtTime(0, t); prof.gain.linearRampToValueAtTime(25, t + dur);
    lfo.connect(prof).connect(o.detune);
    lfo.start(t); lfo.stop(t + dur + 0.02);
  }
}

// Ataque de metais: serra com filtro que abre e fecha (trompete e trombone juntos).
function metais(b, f, t, dur) {
  for (const [st, v] of [[0, 0.3], [7, 0.22], [12, 0.25]]) {
    const o = ctx.createOscillator(); o.type = 'sawtooth'; o.frequency.value = f * 2 ** (st / 12);
    const fil = ctx.createBiquadFilter(); fil.type = 'lowpass'; fil.Q.value = 3;
    fil.frequency.setValueAtTime(400, t);
    fil.frequency.linearRampToValueAtTime(3500, t + 0.04);
    fil.frequency.exponentialRampToValueAtTime(1200, t + dur);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(v, t + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(fil).connect(g).connect(b.lead);
    o.start(t); o.stop(t + dur + 0.02);
  }
}

function bateria(b, nome, t, vol = 1) {
  if (!amostra(nome, t, { vol, varia: 0.01, destino: b.bateria }) && nome !== 'chimbal_aberto' && nome !== 'prato') {
    // Amostras ainda carregando: um toque sintetizado no lugar.
    if (nome === 'bumbo' || nome === 'zabumba' || nome === 'surdo') nota(b.bateria, 90, t, 0.12, { onda: 'sine', vol: vol, desliza: 0.5 });
    else if (nome === 'caixa') nota(b.bateria, 220, t, 0.08, { onda: 'triangle', vol: vol * 0.6 });
  }
}

// Agenda um compasso inteiro da música.
function tocarCompasso(b, m, idx, t0) {
  const SEMI = 60 / m.bpm / 4;
  const nSec = m.secoes.length;
  const tamSec = m.secoes[0].acordes.length;
  const volta = Math.floor(idx / (tamSec * nSec));
  const sec = m.secoes[Math.floor(idx / tamSec) % nSec];
  const c = idx % tamSec;
  const raiz = N(sec.acordes[c]);
  const lev = LEVADAS[m.levada];
  const ultimo = c === tamSec - 1;
  // Bateria (no último compasso da seção, virada de caixa e surdo).
  for (let s = 0; s < 16; s++) {
    const t = t0 + s * SEMI;
    if (lev.bumbo[s] === 'x') bateria(b, 'bumbo', t, 0.9);
    if (lev.zabumba[s] === 'x') bateria(b, 'zabumba', t, 0.5);
    if (ultimo && s >= 8 && m.loop) {
      bateria(b, s % 4 === 2 ? 'surdo' : 'caixa', t, 0.5 + (s - 8) * 0.06);
      continue;
    }
    if (lev.caixa[s] === 'x') bateria(b, 'caixa', t, 0.8);
    if (lev.chimbal[s] === 'x') bateria(b, 'chimbal', t, s % 4 === 0 ? 0.45 : 0.3);
    if (lev.chimbal[s] === 'o') bateria(b, 'chimbal_aberto', t, 0.35);
  }
  if (c === 0) bateria(b, 'prato', t0, 0.55);
  // Guitarra base.
  for (let s = 0; s < 16; s++) {
    const g = lev.guitarra[s];
    if (g === '.') continue;
    let len = 1;
    while (s + len < 16 && lev.guitarra[s + len] === '.') len++;
    powerChord(b, raiz, t0 + s * SEMI, (g === 'x' ? len : 1) * SEMI * 0.95, g === 'm');
  }
  // Baixo em colcheias.
  lev.baixo.forEach((st, i) => {
    if (st === null) return;
    const dur = m.levada === 'lento' ? SEMI * 15 : SEMI * 1.7;
    osc(b.baixo, 'sawtooth', raiz * 2 ** (st / 12), t0 + i * SEMI * 2, dur, 0.6, 0.004, 0.04);
    osc(b.baixo, 'square', raiz * 2 ** (st / 12) / 2, t0 + i * SEMI * 2, dur, 0.35, 0.004, 0.04);
  });
  if (m.levada === 'galope') {
    for (let s = 1; s < 16; s += 2) osc(b.baixo, 'sawtooth', raiz, t0 + s * SEMI, SEMI * 0.8, 0.45, 0.003, 0.02);
  }
  // Melodia: sanfona na primeira volta, guitarra solo na segunda; a fanfarra é dos metais.
  const instrumento = m.levada === 'marcha' ? metais : m.levada === 'galope' ? (volta % 2 ? sanfona : guitarraSolo)
    : (volta % 2 ? guitarraSolo : sanfona);
  for (const [pos, f, d] of sec.porCompasso[c]) instrumento(b, f, t0 + pos * SEMI, d * SEMI * 0.92);
  // Metais pontuando a virada da seção.
  if (m.loop && (c === 3 || ultimo)) {
    metais(b, raiz * 2, t0 + 12 * SEMI, SEMI * 1.5);
    metais(b, raiz * 2, t0 + 14 * SEMI, SEMI * 2);
  }
}

let tocando = null;
let faixa = null; // ganho só desta música: desligar corta tudo o que já foi agendado
let atual = null;

export function tocarMusica(nome) {
  if (!iniciar() || !MUSICAS[nome]) return;
  if (atual === nome && tocando) return;
  pararMusica();
  atual = nome;
  const m = MUSICAS[nome];
  const compasso = 60 / m.bpm * 4;
  const total = m.secoes.length * m.secoes[0].acordes.length;
  faixa = ctx.createGain();
  faixa.connect(mestreMusica);
  const banda = montarBanda(faixa);
  let proximo = ctx.currentTime + 0.1;
  let idx = 0;
  const agendar = () => {
    if (!tocando || ctx.state !== 'running') return;
    // Som estava travado (antes do primeiro toque): começa do agora, sem despejar notas atrasadas.
    if (proximo < ctx.currentTime) proximo = ctx.currentTime + 0.05;
    while (proximo < ctx.currentTime + 1.2 && (m.loop || idx < total)) {
      tocarCompasso(banda, m, idx, proximo);
      idx++;
      proximo += compasso;
    }
  };
  tocando = setInterval(agendar, 300);
  agendar();
}

export function pararMusica() {
  if (tocando) clearInterval(tocando);
  tocando = null;
  atual = null;
  if (faixa) {
    const f = faixa;
    // Desliga com uma rampa curta, sem estalo.
    f.gain.setTargetAtTime(0, ctx.currentTime, 0.03);
    setTimeout(() => f.disconnect(), 200);
  }
  faixa = null;
}

// Nomes antigos (tela de início).
export const tocarTema = () => tocarMusica('tema');
export const pararTema = pararMusica;
