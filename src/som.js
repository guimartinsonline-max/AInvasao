// Som feito em código (Web Audio), no estilo chiptune. Por enquanto: bipes dos
// menus e a música da tela de início. Os efeitos do jogo e as outras músicas
// entram na etapa de som. Volumes vêm dos ajustes (0 a 10).
import { ajustes, aoMudarAjustes } from './ajustes.js';

let ctx = null;
let mestreEfeitos = null;
let mestreMusica = null;

function iniciar() {
  if (ctx) return ctx;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return null;
  ctx = new AC();
  mestreEfeitos = ctx.createGain();
  mestreMusica = ctx.createGain();
  mestreEfeitos.connect(ctx.destination);
  mestreMusica.connect(ctx.destination);
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

function nota(destino, freq, inicio, dur, { onda = 'square', vol = 1, desliza = 0 } = {}) {
  const o = ctx.createOscillator();
  const g = ctx.createGain();
  o.type = onda;
  o.frequency.setValueAtTime(freq, inicio);
  if (desliza) o.frequency.exponentialRampToValueAtTime(Math.max(30, freq * desliza), inicio + dur);
  g.gain.setValueAtTime(0.0001, inicio);
  g.gain.exponentialRampToValueAtTime(vol, inicio + 0.008);
  g.gain.exponentialRampToValueAtTime(0.0001, inicio + dur);
  o.connect(g).connect(destino);
  o.start(inicio);
  o.stop(inicio + dur + 0.02);
}

// Bipes dos menus.
export function bip(tipo = 'mover') {
  if (!iniciar() || ctx.state !== 'running') return;
  const t = ctx.currentTime;
  if (tipo === 'mover') nota(mestreEfeitos, 660, t, 0.06, { vol: 0.5 });
  else if (tipo === 'confirmar') {
    nota(mestreEfeitos, 523, t, 0.07, { vol: 0.6 });
    nota(mestreEfeitos, 784, t + 0.07, 0.12, { vol: 0.6 });
  } else if (tipo === 'voltar') nota(mestreEfeitos, 440, t, 0.12, { vol: 0.5, desliza: 0.6 });
  else if (tipo === 'erro') nota(mestreEfeitos, 150, t, 0.15, { onda: 'sawtooth', vol: 0.4 });
}

// ---------------------------------------------------------------- música
// Tema da tela de início: baião em escala mixolídia (sétima abaixada, cara de
// sanfona nordestina), com zabumba no grave e triângulo. 8 compassos em loop.
const BPM = 112;
const SEMI = 60 / BPM / 4; // semicolcheia
const N = (nome) => {
  const base = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  const m = nome.match(/^([A-G])(b?)(\d)$/);
  const semis = base[m[1]] - (m[2] ? 1 : 0) + (Number(m[3]) - 4) * 12;
  return 440 * 2 ** ((semis - 9) / 12);
};
// [nota, duração em semicolcheias] (null = pausa). Sol mixolídio: Fá natural.
const MELODIA = [
  ['G4', 2], ['B4', 2], ['D5', 3], ['C5', 1], ['B4', 2], ['A4', 2], ['G4', 4],
  ['F4', 2], ['G4', 2], ['A4', 2], ['B4', 2], ['C5', 3], ['B4', 1], ['A4', 4],
  ['G4', 2], ['B4', 2], ['D5', 3], ['E5', 1], ['F5', 2], ['E5', 2], ['D5', 4],
  ['C5', 2], ['A4', 2], ['F4', 2], ['A4', 2], ['G4', 6], [null, 2],
];
const BAIXO = ['G2', 'G2', 'F2', 'F2', 'G2', 'C3', 'F2', 'G2']; // um por compasso

let tocando = null;
let faixa = null; // ganho só desta música: desligar corta tudo o que já foi agendado

export function tocarTema() {
  if (!iniciar()) return;
  if (tocando) return;
  faixa = ctx.createGain();
  faixa.connect(mestreMusica);
  const saida = faixa;
  const compasso = SEMI * 16;
  const duracao = compasso * 8;
  let inicioLoop = ctx.currentTime + 0.1;
  const agendar = () => {
    if (!tocando || ctx.state !== 'running') return;
    // Som estava travado (antes do primeiro toque): começa do agora, sem despejar notas atrasadas.
    if (inicioLoop < ctx.currentTime) inicioLoop = ctx.currentTime + 0.05;
    // Agenda o próximo loop um pouco antes de este acabar.
    while (inicioLoop < ctx.currentTime + 1.5) {
      let t = inicioLoop;
      for (const [n, d] of MELODIA) {
        if (n) nota(saida, N(n), t, d * SEMI * 0.9, { vol: 0.35 });
        t += d * SEMI;
      }
      BAIXO.forEach((b, k) => {
        const c0 = inicioLoop + k * compasso;
        // Zabumba: "tum ... tum-tum" do baião.
        for (const [pos, acento] of [[0, 1], [6, 0.7], [8, 0.9]]) {
          nota(saida, N(b), c0 + pos * SEMI, SEMI * 2.2, { onda: 'triangle', vol: 0.9 * acento });
        }
        // Triângulo nas semicolcheias, abafado e aberto.
        for (let s = 0; s < 16; s += 2) {
          nota(saida, 4200, c0 + s * SEMI, s % 4 === 2 ? 0.06 : 0.02, { onda: 'square', vol: 0.05 });
        }
      });
      inicioLoop += duracao;
    }
  };
  tocando = setInterval(agendar, 400);
  agendar();
}

export function pararTema() {
  if (tocando) clearInterval(tocando);
  tocando = null;
  if (faixa) faixa.disconnect();
  faixa = null;
}
