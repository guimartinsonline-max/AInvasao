import { LARGURA, ALTURA } from '../config.js';
import { P, hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';

const RAIO_DIRECIONAL = 18;
const ZONA_DIRECIONAL = 0.45; // fração da tela, à esquerda, que vira direcional

const BOTOES = [
  { acao: 'atirar', x: 346, y: 170, r: 21, rotulo: 'TIRO' },
  { acao: 'pular', x: 300, y: 192, r: 16, rotulo: 'PULO' },
  { acao: 'granada', x: 356, y: 122, r: 13, rotulo: 'GR' },
];

const DICAS = {
  teclado: 'SETAS MOVER  Z TIRO  X PULO  C GRANADA',
  controle: 'A PULO  X TIRO  B GRANADA',
  toque: '',
};

// Interface por cima do jogo: botões de toque, granadas e dicas de controle.
export class HudScene extends Phaser.Scene {
  constructor() {
    super('Hud');
  }

  init(dados) {
    this.jogador = dados.jogador;
  }

  create() {
    this.controles = this.game.controles;
    this.dedos = new Map(); // id do toque -> 'direcional' ou ação de botão

    this.granadas = this.add.text(4, 4, '', estiloTexto(hex('branco')));
    this.fps = this.add.text(LARGURA - 4, 4, '', estiloTexto(hex('branco'))).setOrigin(1, 0).setAlpha(0.6);
    this.dica = this.add.text(LARGURA / 2, ALTURA - 10, '', estiloTexto(hex('branco'))).setOrigin(0.5);

    this.criarToque();
    this.mostrarFonte(this.controles.fonte);
    const desligar = this.controles.aoMudarFonte((f) => this.mostrarFonte(f));
    this.events.once('shutdown', () => {
      desligar();
      this.soltarTudo();
    });
  }

  criarToque() {
    this.toque = this.add.container(0, 0);
    this.base = this.add.circle(0, 0, RAIO_DIRECIONAL + 4, P.branco, 0.12).setStrokeStyle(1, P.branco, 0.35);
    this.pino = this.add.circle(0, 0, 8, P.branco, 0.35);
    this.toque.add([this.base, this.pino]);
    this.pinoVisivel(false);

    for (const b of BOTOES) {
      b.circulo = this.add.circle(b.x, b.y, b.r, P.branco, 0.15).setStrokeStyle(1, P.branco, 0.45);
      b.texto = this.add.text(b.x, b.y, b.rotulo, estiloTexto(hex('branco'))).setOrigin(0.5).setAlpha(0.7);
      this.toque.add([b.circulo, b.texto]);
    }

    this.input.on('pointerdown', (p) => this.tocar(p));
    this.input.on('pointermove', (p) => this.mover(p));
    this.input.on('pointerup', (p) => this.soltar(p));
    this.input.on('pointerupoutside', (p) => this.soltar(p));
  }

  mostrarFonte(fonte) {
    this.toque.setVisible(fonte === 'toque');
    this.dica.setText(DICAS[fonte] || '').setAlpha(1);
    this.tweens.killTweensOf(this.dica);
    this.tweens.add({ targets: this.dica, alpha: 0, delay: 4000, duration: 600 });
  }

  pinoVisivel(v) {
    this.base.setVisible(v);
    this.pino.setVisible(v);
  }

  tocar(p) {
    if (!p.wasTouch) return;
    this.controles.mudarFonte('toque');
    if (p.x < LARGURA * ZONA_DIRECIONAL && ![...this.dedos.values()].includes('direcional')) {
      this.dedos.set(p.id, 'direcional');
      this.origem = { x: p.x, y: p.y };
      this.base.setPosition(p.x, p.y);
      this.pinoVisivel(true);
      this.mover(p);
      return;
    }
    this.apertarBotao(p);
  }

  apertarBotao(p) {
    let melhor = null;
    let menor = Infinity;
    for (const b of BOTOES) {
      const d = Phaser.Math.Distance.Between(p.x, p.y, b.x, b.y);
      if (d < b.r + 16 && d - b.r < menor) {
        melhor = b;
        menor = d - b.r;
      }
    }
    const antes = this.dedos.get(p.id);
    if (antes && antes !== 'direcional' && (!melhor || melhor.acao !== antes)) this.definir(antes, false);
    if (melhor) {
      this.dedos.set(p.id, melhor.acao);
      this.definir(melhor.acao, true);
    } else {
      this.dedos.delete(p.id);
    }
  }

  mover(p) {
    const papel = this.dedos.get(p.id);
    if (!papel || !p.isDown) return;
    if (papel !== 'direcional') {
      // Deslizar o dedo de um botão para outro troca a ação.
      this.apertarBotao(p);
      return;
    }
    let dx = p.x - this.origem.x;
    let dy = p.y - this.origem.y;
    const dist = Math.hypot(dx, dy);
    // Direcional flutuante: se o dedo vai longe, a base acompanha.
    const maximo = RAIO_DIRECIONAL * 1.5;
    if (dist > maximo) {
      this.origem.x = p.x - (dx / dist) * maximo;
      this.origem.y = p.y - (dy / dist) * maximo;
      this.base.setPosition(this.origem.x, this.origem.y);
      dx = p.x - this.origem.x;
      dy = p.y - this.origem.y;
    }
    const k = Math.min(1, RAIO_DIRECIONAL / Math.max(dist, 1));
    this.pino.setPosition(this.origem.x + dx * k, this.origem.y + dy * k);

    const nx = dx / RAIO_DIRECIONAL;
    const ny = dy / RAIO_DIRECIONAL;
    const t = this.controles.toque;
    t.x = nx > 0.35 ? 1 : nx < -0.35 ? -1 : 0;
    t.cima = ny < -0.55;
    t.baixo = ny > 0.55;
  }

  soltar(p) {
    const papel = this.dedos.get(p.id);
    if (!papel) return;
    this.dedos.delete(p.id);
    if (papel === 'direcional') {
      const t = this.controles.toque;
      t.x = 0;
      t.cima = false;
      t.baixo = false;
      this.pinoVisivel(false);
    } else if (![...this.dedos.values()].includes(papel)) {
      this.definir(papel, false);
    }
  }

  soltarTudo() {
    for (const id of [...this.dedos.keys()]) this.soltar({ id });
  }

  definir(acao, valor) {
    this.controles.definirToque(acao, valor);
    const b = BOTOES.find((x) => x.acao === acao);
    b.circulo.setFillStyle(P.branco, valor ? 0.45 : 0.15);
  }

  update() {
    // Segurança: se o sistema engolir um "soltar" (ex.: notificação no iPhone), libera o dedo.
    for (const p of this.input.manager.pointers) {
      if (this.dedos.has(p.id) && !p.isDown) this.soltar(p);
    }
    this.granadas.setText(`GRANADAS ${this.jogador.granadas}`);
    this.fps.setText(`${Math.round(this.game.loop.actualFps)}`);
  }
}
