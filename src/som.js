// Som feito em código (Web Audio), no estilo sfxr/chiptune: efeitos sintetizados
// na hora, músicas compostas em notas e a voz do locutor (síntese de fala do
// próprio aparelho, de graça). Volumes vêm dos ajustes (0 a 10).
import { ajustes, aoMudarAjustes } from './ajustes.js';

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
  return ctx;
}

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

const SONS = {
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
  if (!pronto() || !SONS[nome]) return;
  const agora = performance.now();
  if (agora - (ultimo[nome] || 0) < (INTERVALO[nome] || 25)) return;
  ultimo[nome] = agora;
  SONS[nome](ctx.currentTime, ...args);
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

// ---------------------------------------------------------------- locutor
// "MADSEN!", como o locutor do Metal Slug, com a voz do aparelho em português,
// grave e firme.
export function falar(texto) {
  if (!window.speechSynthesis || ajustes.efeitos === 0) return;
  try {
    const u = new SpeechSynthesisUtterance(texto);
    u.lang = 'pt-BR';
    u.pitch = 0.55;
    u.rate = 1.05;
    u.volume = Math.min(1, ajustes.efeitos / 10 + 0.1);
    const voz = window.speechSynthesis.getVoices().find((v) => v.lang && v.lang.toLowerCase().startsWith('pt'));
    if (voz) u.voice = voz;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  } catch (e) {
    // Sem voz no aparelho: segue sem locutor.
  }
}

// ---------------------------------------------------------------- músicas
const N = (nome) => {
  const base = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  const m = nome.match(/^([A-G])([b#]?)(\d)$/);
  const semis = base[m[1]] + (m[2] === 'b' ? -1 : m[2] === '#' ? 1 : 0) + (Number(m[3]) - 4) * 12;
  return 440 * 2 ** ((semis - 9) / 12);
};

// Cada música: andamento, melodia [nota, semicolcheias], baixo (um acorde por
// compasso), jeito do baixo e se repete. Escalas nordestinas (mixolídio/dório)
// e, no chefe, menor harmônico.
const MUSICAS = {
  // Tela de início: baião em sol mixolídio.
  tema: {
    bpm: 112, loop: true, baixo: ['G2', 'G2', 'F2', 'F2', 'G2', 'C3', 'F2', 'G2'], ritmo: 'baiao',
    melodia: [['G4', 2], ['B4', 2], ['D5', 3], ['C5', 1], ['B4', 2], ['A4', 2], ['G4', 4],
      ['F4', 2], ['G4', 2], ['A4', 2], ['B4', 2], ['C5', 3], ['B4', 1], ['A4', 4],
      ['G4', 2], ['B4', 2], ['D5', 3], ['E5', 1], ['F5', 2], ['E5', 2], ['D5', 4],
      ['C5', 2], ['A4', 2], ['F4', 2], ['A4', 2], ['G4', 6], [null, 2]],
  },
  // Fase 1: xaxado ligeiro em ré dório (sanfona danada).
  caatinga: {
    bpm: 138, loop: true, baixo: ['D2', 'D2', 'C3', 'C3', 'D2', 'G2', 'C3', 'D2'], ritmo: 'baiao',
    melodia: [['D5', 1], ['E5', 1], ['F5', 2], ['E5', 1], ['D5', 1], ['C5', 2], ['D5', 2], ['A4', 2], [null, 2], ['A4', 1], ['B4', 1],
      ['C5', 2], ['B4', 1], ['A4', 1], ['G4', 2], ['A4', 2], ['E4', 4], [null, 4],
      ['D5', 1], ['E5', 1], ['F5', 2], ['G5', 2], ['A5', 2], ['G5', 1], ['F5', 1], ['E5', 2], ['D5', 2], ['C5', 2], [null, 2],
      ['B4', 2], ['C5', 2], ['A4', 2], ['G4', 2], ['A4', 6], [null, 2]],
  },
  // Chefe: lá menor harmônico, baixo galopando em colcheias.
  chefe: {
    bpm: 156, loop: true, baixo: ['A2', 'A2', 'F2', 'F2', 'D2', 'D2', 'E2', 'E2'], ritmo: 'galope',
    melodia: [['A4', 2], ['C5', 2], ['E5', 2], ['A5', 2], ['G#5', 2], ['E5', 2], ['B4', 4],
      ['C5', 2], ['A4', 2], ['F4', 2], ['A4', 2], ['G#4', 6], [null, 2],
      ['A4', 2], ['C5', 2], ['E5', 2], ['F5', 2], ['E5', 2], ['D5', 2], ['C5', 2], ['B4', 2],
      ['A4', 2], ['B4', 2], ['G#4', 2], ['E4', 2], ['A4', 6], [null, 2]],
  },
  // Missão cumprida: fanfarra curta.
  vitoria: {
    bpm: 132, loop: false, baixo: ['C3', 'G2', 'C3'], ritmo: 'baiao',
    melodia: [['C5', 2], ['E5', 2], ['G5', 2], ['C6', 4], ['B5', 1], ['C6', 1], ['D6', 4], ['B5', 2], ['G5', 2], ['C6', 8], [null, 8]],
  },
  // Sem vidas: lamento descendo.
  derrota: {
    bpm: 90, loop: false, baixo: ['A2', 'E2'], ritmo: 'lento',
    melodia: [['E5', 4], ['D5', 4], ['C5', 4], ['B4', 4], ['A4', 12], [null, 4]],
  },
};

let tocando = null;
let faixa = null; // ganho só desta música: desligar corta tudo o que já foi agendado
let atual = null;

export function tocarMusica(nome) {
  if (!iniciar() || !MUSICAS[nome]) return;
  if (atual === nome && tocando) return;
  pararMusica();
  atual = nome;
  const m = MUSICAS[nome];
  const SEMI = 60 / m.bpm / 4;
  faixa = ctx.createGain();
  faixa.connect(mestreMusica);
  const saida = faixa;
  const compasso = SEMI * 16;
  const duracao = compasso * m.baixo.length;
  let inicioLoop = ctx.currentTime + 0.1;
  let vezes = 0;
  const agendar = () => {
    if (!tocando || ctx.state !== 'running') return;
    // Som estava travado (antes do primeiro toque): começa do agora, sem despejar notas atrasadas.
    if (inicioLoop < ctx.currentTime) inicioLoop = ctx.currentTime + 0.05;
    while (inicioLoop < ctx.currentTime + 1.5 && (m.loop || vezes === 0)) {
      vezes++;
      let t = inicioLoop;
      for (const [n, d] of m.melodia) {
        if (n) nota(saida, N(n), t, d * SEMI * 0.9, { vol: 0.35 });
        t += d * SEMI;
      }
      m.baixo.forEach((b, k) => {
        const c0 = inicioLoop + k * compasso;
        if (m.ritmo === 'galope') {
          // Baixo em colcheias: tônica, tônica, oitava, tônica...
          [0, 0, 12, 0, 7, 0, 12, 7].forEach((st, i) => {
            nota(saida, N(b) * 2 ** (st / 12), c0 + i * SEMI * 2, SEMI * 1.6, { onda: 'triangle', vol: 0.8 });
          });
          for (let s = 0; s < 16; s += 4) nota(saida, 3000, c0 + s * SEMI, 0.03, { onda: 'square', vol: 0.05 });
        } else if (m.ritmo === 'lento') {
          nota(saida, N(b), c0, compasso * 0.9, { onda: 'triangle', vol: 0.7 });
        } else {
          // Zabumba do baião: "tum ... tum-tum".
          for (const [pos, acento] of [[0, 1], [6, 0.7], [8, 0.9]]) {
            nota(saida, N(b), c0 + pos * SEMI, SEMI * 2.2, { onda: 'triangle', vol: 0.9 * acento });
          }
          // Triângulo nas semicolcheias, abafado e aberto.
          for (let s = 0; s < 16; s += 2) {
            nota(saida, 4200, c0 + s * SEMI, s % 4 === 2 ? 0.06 : 0.02, { onda: 'square', vol: 0.05 });
          }
        }
      });
      inicioLoop += duracao;
    }
  };
  tocando = setInterval(agendar, 400);
  agendar();
}

export function pararMusica() {
  if (tocando) clearInterval(tocando);
  tocando = null;
  atual = null;
  if (faixa) faixa.disconnect();
  faixa = null;
}

// Nomes antigos (tela de início).
export const tocarTema = () => tocarMusica('tema');
export const pararTema = pararMusica;
