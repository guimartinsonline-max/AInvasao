// Entrada unificada: teclado, controle (gamepad) e toque viram o mesmo estado.
// A "fonte" é o último tipo de entrada usado; a HUD mostra os botões de toque
// só quando a fonte é o toque.

const TECLAS = {
  esquerda: ['ArrowLeft', 'KeyA'],
  direita: ['ArrowRight', 'KeyD'],
  cima: ['ArrowUp', 'KeyW'],
  baixo: ['ArrowDown', 'KeyS'],
  pular: ['KeyX', 'KeyK', 'Space'],
  atirar: ['KeyZ', 'KeyJ'],
  granada: ['KeyC', 'KeyL'],
  confirmar: ['Enter', 'Space'],
  voltar: ['Escape'],
};
const CODIGOS_JOGO = new Set(Object.values(TECLAS).flat());

// Mapeamento padrão (Xbox): A=0, B=1, X=2, Y=3, LB=4, RB=5, LT=6, RT=7,
// Back=8, Start=9, direcional=12..15.
const BOTOES = {
  pular: [0],
  atirar: [2, 7],
  granada: [1, 5],
  confirmar: [0, 9],
  voltar: [8],
};

const ACOES = ['cima', 'baixo', 'pular', 'atirar', 'granada', 'confirmar', 'voltar'];

export class Controles {
  constructor() {
    this.fonte = window.matchMedia('(pointer: coarse)').matches ? 'toque' : 'teclado';
    this.ouvintes = new Set();
    this.teclas = new Set();
    // Teclas apertadas desde o último quadro: um toque rápido (apertar e soltar
    // antes do próximo quadro) ainda conta.
    this.batidas = new Set();
    this.eixoX = 0;
    this.estado = {};
    this.anterior = {};
    // Preenchido pela HUD de toque.
    this.toque = { x: 0 };
    this.batidasToque = new Set();
    for (const a of ACOES) {
      this.estado[a] = false;
      this.anterior[a] = false;
      this.toque[a] = false;
    }

    window.addEventListener('keydown', (e) => {
      if (CODIGOS_JOGO.has(e.code)) e.preventDefault();
      if (e.repeat) return;
      this.teclas.add(e.code);
      this.batidas.add(e.code);
      this.mudarFonte('teclado');
    });
    window.addEventListener('keyup', (e) => this.teclas.delete(e.code));
    window.addEventListener('blur', () => this.teclas.clear());
    window.addEventListener('touchstart', () => this.mudarFonte('toque'), { capture: true, passive: true });
  }

  aoMudarFonte(fn) {
    this.ouvintes.add(fn);
    return () => this.ouvintes.delete(fn);
  }

  mudarFonte(fonte) {
    if (this.fonte === fonte) return;
    this.fonte = fonte;
    for (const fn of this.ouvintes) fn(fonte);
  }

  tecla(acao) {
    for (const codigo of TECLAS[acao]) if (this.teclas.has(codigo) || this.batidas.has(codigo)) return true;
    return false;
  }

  // Chamar uma vez por quadro, antes de ler o estado.
  atualizar() {
    const pad = this.lerControle();

    let x = 0;
    if (this.tecla('esquerda')) x -= 1;
    if (this.tecla('direita')) x += 1;
    x += this.toque.x;
    if (pad) {
      const ax = pad.axes[0] || 0;
      if (Math.abs(ax) > 0.35) x += Math.sign(ax);
      if (botao(pad, 14)) x -= 1;
      if (botao(pad, 15)) x += 1;
    }
    this.eixoX = Math.max(-1, Math.min(1, x));

    for (const a of ACOES) {
      this.anterior[a] = this.estado[a];
      let v = this.toque[a] || this.batidasToque.has(a);
      if (TECLAS[a] && this.tecla(a)) v = true;
      if (pad && !v) {
        if (a === 'cima') v = (pad.axes[1] || 0) < -0.5 || botao(pad, 12);
        else if (a === 'baixo') v = (pad.axes[1] || 0) > 0.5 || botao(pad, 13);
        else v = BOTOES[a].some((i) => botao(pad, i));
      }
      this.estado[a] = v;
    }
    this.batidas.clear();
    this.batidasToque.clear();
  }

  // Chamado pela HUD de toque.
  definirToque(acao, valor) {
    this.toque[acao] = valor;
    if (valor) this.batidasToque.add(acao);
  }

  lerControle() {
    if (!navigator.getGamepads) return null;
    for (const pad of navigator.getGamepads()) {
      if (!pad || !pad.connected) continue;
      const mexeu = pad.buttons.some((b) => b.pressed) || pad.axes.some((v) => Math.abs(v) > 0.5);
      if (mexeu) this.mudarFonte('controle');
      return pad;
    }
    return null;
  }

  apertou(acao) {
    return this.estado[acao] && !this.anterior[acao];
  }

  soltou(acao) {
    return !this.estado[acao] && this.anterior[acao];
  }
}

function botao(pad, i) {
  return pad.buttons[i] ? pad.buttons[i].pressed : false;
}
