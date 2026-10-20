import { LARGURA, ALTURA } from '../config.js';
import { P, hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { ARMAS } from '../armas.js';
import { ajustes, salvarAjustes, nomeTecla } from '../ajustes.js';
import { bip } from '../som.js';

// Os botões foram feitos para a tela de 384x216; K mantém o mesmo tamanho no vidro
// do celular na resolução atual, contando a partir do canto de baixo à direita.
const K = LARGURA / 384;
const RAIO_DIRECIONAL = 18 * K;
const ZONA_DIRECIONAL = 0.45; // fração da tela, à esquerda, que vira direcional

const BOTOES = [
  { acao: 'atirar', x: 346, y: 170, r: 21, rotulo: 'TIRO' },
  { acao: 'pular', x: 300, y: 192, r: 16, rotulo: 'PULO' },
  { acao: 'granada', x: 356, y: 122, r: 13, rotulo: 'GR' },
].map((b) => ({ ...b, x: LARGURA - (384 - b.x) * K, y: ALTURA - (216 - b.y) * K, r: b.r * K }));

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
    this.pausado = false; // a cena é reaproveitada: não começa com a pausa de antes
    this.jogador = dados.jogador;
    this.chaveCena = dados.cena || 'Campo';
  }

  create() {
    this.controles = this.game.controles;
    this.dedos = new Map(); // id do toque -> 'direcional' ou ação de botão

    this.criarPainel();
    this.fps = this.add.text(LARGURA - 4, 14, '', estiloTexto(hex('branco'))).setOrigin(1, 0).setAlpha(0.5);
    this.dica = this.add.text(LARGURA / 2, ALTURA - 10, '', estiloTexto(hex('branco'))).setOrigin(0.5);

    // Nome da arma "gritado" no meio da tela ao pegar, como no Metal Slug.
    this.anuncio = this.add.text(LARGURA / 2, 60, '', estiloTexto(hex('amarelo_fogo'), 16)).setOrigin(0.5).setVisible(false);
    const campo = this.scene.get(this.chaveCena);
    const anunciar = (nome) => {
      this.anuncio.setText(nome + '!').setVisible(true).setScale(2).setAlpha(1);
      this.tweens.killTweensOf(this.anuncio);
      this.tweens.add({ targets: this.anuncio, scale: 1, duration: 160, ease: 'Back.easeOut' });
      this.tweens.add({ targets: this.anuncio, alpha: 0, delay: 1300, duration: 300 });
    };
    campo.events.on('arma', anunciar);
    this.events.once('shutdown', () => campo.events.off('arma', anunciar));
    campo.events.on('arma', () => { this.alegreAte = this.time.now + 700; });
    // Dica de jogo no pé da tela (ex.: o jumento kamikaze na primeira montada).
    const dicar = (txt) => {
      this.dica.setText(txt).setAlpha(1);
      this.tweens.killTweensOf(this.dica);
      this.tweens.add({ targets: this.dica, alpha: 0, delay: 4500, duration: 600 });
    };
    campo.events.on('dica', dicar);
    this.events.once('shutdown', () => campo.events.off('dica', dicar));
    this.criarToque();
    this.criarPausa();
    this.mostrarFonte(this.controles.fonte);
    const desligar = this.controles.aoMudarFonte((f) => this.mostrarFonte(f));
    this.events.once('shutdown', () => {
      desligar();
      this.soltarTudo();
    });
  }

  // Painel de munição no canto, como o ARMS / BOMB do Metal Slug.
  criarPainel() {
    const x = 4;
    const y = 4;
    const g = this.add.graphics();
    g.fillStyle(P.sombra, 0.82).fillRect(x, y, 140, 34);
    g.lineStyle(1, P.areia_luz, 0.9).strokeRect(x + 0.5, y + 0.5, 139, 33);
    g.lineStyle(1, P.areia_luz, 0.4).lineBetween(x + 74.5, y + 4, x + 74.5, y + 30);
    const rotulo = estiloTexto(hex('amarelo_claro'));
    this.icone = this.add.image(x + 12, y + 17, 'item_madsen').setVisible(false);
    this.rotuloArma = this.add.text(x + 24, y + 5, 'ARMA', rotulo);
    this.numArma = this.add.text(x + 24, y + 15, '', estiloTexto(hex('branco'), 16));
    this.infinito = this.add.image(x + 26, y + 18, 'infinito').setOrigin(0);
    this.rotuloGranada = this.add.text(x + 80, y + 5, 'GRANADA', rotulo);
    this.blindagem = this.add.text(x, y + 48, '', estiloTexto(hex('amarelo_claro'))).setVisible(false);
    this.numGranada = this.add.text(x + 80, y + 15, '', estiloTexto(hex('branco'), 16));
    // Retrato do Lampião com as vidas (a cara muda: atirando, levando susto, morto, gordo).
    g.fillStyle(P.sombra, 0.82).fillRect(x + 144, y, 56, 34);
    g.lineStyle(1, P.areia_luz, 0.9).strokeRect(x + 144.5, y + 0.5, 55, 33);
    this.retrato = this.add.image(x + 147, y + 7, 'retrato', 0).setOrigin(0);
    this.vidas = this.add.text(x + 176, y + 13, '', estiloTexto(hex('branco')));
    this.alegreAte = 0;
    this.super = this.add.text(x + 4, y + 26, 'SUPER', estiloTexto(hex('amarelo_fogo'))).setVisible(false);
    // Pontos e relógio (o relógio só aparece nas missões).
    this.pontos = this.add.text(LARGURA - 4, 4, '0', estiloTexto(hex('amarelo_claro'))).setOrigin(1, 0);
    this.relogio = this.add.text(LARGURA / 2, 4, '', estiloTexto(hex('amarelo_fogo'), 16)).setOrigin(0.5, 0);
  }

  criarToque() {
    this.toque = this.add.container(0, 0);
    this.base = this.add.circle(0, 0, RAIO_DIRECIONAL + 4, P.branco, 0.12).setStrokeStyle(1, P.branco, 0.35);
    this.pino = this.add.circle(0, 0, 8 * K, P.branco, 0.35);
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
    // No teclado, a dica mostra as teclas escolhidas nas opções.
    const tk = ajustes.teclas;
    const dica = fonte === 'teclado'
      ? `SETAS MOVER  ${nomeTecla(tk.atirar)} TIRO  ${nomeTecla(tk.pular)} PULO  ${nomeTecla(tk.granada)} GRANADA  ESC PAUSA`
      : fonte === 'controle' ? 'A PULO  X TIRO  B GRANADA  BACK PAUSA' : DICAS[fonte];
    this.dica.setText(dica || '').setAlpha(1);
    this.tweens.killTweensOf(this.dica);
    this.tweens.add({ targets: this.dica, alpha: 0, delay: 4000, duration: 600 });
  }

  pinoVisivel(v) {
    this.base.setVisible(v);
    this.pino.setVisible(v);
  }

  tocar(p) {
    if (this.pausado) return;
    // Botão de pausa no canto de cima.
    if (p.x > LARGURA - 34 && p.y > 18 && p.y < 52) {
      this.abrirPausa();
      return;
    }
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
      if (d < b.r + 16 * K && d - b.r < menor) {
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

  // ------------------------------------------------------------ pausa
  criarPausa() {
    this.botaoPausa = this.add.text(LARGURA - 18, 34, 'II', estiloTexto(hex('branco'), 8)).setOrigin(0.5).setAlpha(0.7);
    this.add.circle(LARGURA - 18, 34, 10, P.branco, 0.12).setStrokeStyle(1, P.branco, 0.4);
    this.pausaGrupo = this.add.container(0, 0).setDepth(100).setVisible(false);
    const fundo = this.add.rectangle(0, 0, LARGURA, ALTURA, P.sombra, 0.75).setOrigin(0).setInteractive();
    const titulo = this.add.text(LARGURA / 2, 56, 'PAUSA', estiloTexto(hex('amarelo_fogo'), 16)).setOrigin(0.5);
    this.pausaGrupo.add([fundo, titulo]);
    this.pausaItens = [];
    for (let k = 0; k < 5; k++) {
      const y = 96 + k * 28;
      const img = this.add.image(LARGURA / 2, y, 'placa').setInteractive();
      const txt = this.add.text(LARGURA / 2, y, '', estiloTexto(hex('branco'))).setOrigin(0.5);
      img.on('pointerdown', (p, lx) => {
        this.escolhaPausa = k;
        const id = this.itensPausa()[k].id;
        if (['efeitos', 'musica', 'tremida'].includes(id)) this.ajustarPausa(id, lx < 75 ? -1 : 1);
        else this.escolherPausa();
      });
      this.pausaGrupo.add([img, txt]);
      this.pausaItens.push({ img, txt });
    }
  }

  itensPausa() {
    return [
      { texto: 'CONTINUAR', id: 'continuar' },
      { texto: `EFEITOS: ${ajustes.efeitos}`, id: 'efeitos' },
      { texto: `MÚSICA: ${ajustes.musica}`, id: 'musica' },
      { texto: `TREMIDA: ${ajustes.tremida ? 'SIM' : 'NÃO'}`, id: 'tremida' },
      { texto: 'SAIR PARA O MENU', id: 'sair' },
    ];
  }

  montarPausa() {
    this.itensPausa().forEach((it, k) => {
      const sel = k === this.escolhaPausa;
      this.pausaItens[k].img.setTexture(sel ? 'placa_sel' : 'placa');
      this.pausaItens[k].txt.setText(it.texto).setColor(sel ? hex('amarelo_fogo') : hex('branco'));
    });
  }

  abrirPausa() {
    if (this.pausado) return;
    this.pausado = true;
    this.escolhaPausa = 0;
    this.scene.pause(this.chaveCena);
    for (const id of [...this.dedos.keys()]) this.soltar({ id });
    this.pausaGrupo.setVisible(true);
    this.montarPausa();
    bip('confirmar');
  }

  fecharPausa() {
    this.pausado = false;
    this.pausaGrupo.setVisible(false);
    this.scene.resume(this.chaveCena);
    bip('voltar');
  }

  ajustarPausa(id, lado) {
    if (id === 'efeitos') ajustes.efeitos = Phaser.Math.Clamp(ajustes.efeitos + lado, 0, 10);
    else if (id === 'musica') ajustes.musica = Phaser.Math.Clamp(ajustes.musica + lado, 0, 10);
    else if (id === 'tremida') ajustes.tremida = !ajustes.tremida;
    else return;
    salvarAjustes();
    bip('mover');
    this.montarPausa();
  }

  escolherPausa() {
    const id = this.itensPausa()[this.escolhaPausa].id;
    if (id === 'continuar') this.fecharPausa();
    else if (id === 'sair') {
      this.pausado = false;
      this.scene.stop(this.chaveCena);
      this.scene.start('Menu');
    } else this.ajustarPausa(id, 1);
  }

  atualizarPausa() {
    const c = this.controles;
    c.atualizar();
    const n = this.pausaItens.length;
    if (c.apertou('baixo')) { this.escolhaPausa = (this.escolhaPausa + 1) % n; bip('mover'); this.montarPausa(); }
    if (c.apertou('cima')) { this.escolhaPausa = (this.escolhaPausa + n - 1) % n; bip('mover'); this.montarPausa(); }
    const lado = c.lado();
    if (lado) this.ajustarPausa(this.itensPausa()[this.escolhaPausa].id, lado);
    if (c.apertou('confirmar') || c.apertou('atirar')) this.escolherPausa();
    else if (c.apertou('voltar')) this.fecharPausa();
  }

  update() {
    if (this.pausado) {
      this.atualizarPausa();
      return;
    }
    // Segurança: se o sistema engolir um "soltar" (ex.: notificação no iPhone), libera o dedo.
    for (const p of this.input.manager.pointers) {
      if (this.dedos.has(p.id) && !p.isDown) this.soltar(p);
    }
    const j = this.jogador;
    const padrao = j.arma === 'padrao';
    this.infinito.setVisible(padrao);
    this.icone.setVisible(!padrao);
    if (!padrao) this.icone.setTexture(`item_${j.arma}`);
    // Pouca munição: o número pisca em vermelho.
    const pouca = !padrao && j.municao <= Math.max(3, ARMAS[j.arma].municao * 0.15);
    const pisca = pouca && Math.floor(this.time.now / 200) % 2 === 0;
    this.numArma.setText(padrao ? '' : `${j.municao}`).setColor(pisca ? hex('vermelho') : hex('branco'));
    // Montado no jumento: o número de granadas vira o de bombas do canhão, e aparece a blindagem.
    const bombas = j.montaria ? j.montaria.bombas : j.granadas;
    this.numGranada.setText(`${bombas}`).setColor(bombas === 0 ? hex('vermelho') : hex('branco'));
    this.rotuloGranada.setText(j.montaria ? 'BOMBA' : 'GRANADA');
    if (j.montaria) {
      const b = j.montaria.blindagem;
      this.blindagem.setVisible(true).setText(`JUMENTO ${'='.repeat(b)}${'-'.repeat(Math.max(0, 6 - b))}`)
        .setColor(b <= 2 && Math.floor(this.time.now / 200) % 2 ? hex('vermelho') : hex('amarelo_claro'));
    } else this.blindagem.setVisible(false);
    this.vidas.setText(`x${j.vidas}`);
    // Cara do Lampião no painel.
    let cara = 0;
    if (j.morto) cara = j.bateu ? 4 : 3;
    else if (j.invulneravel) cara = 2;
    else if (j.desdeTiro < 160 || this.time.now < this.alegreAte || j.montaria) cara = 1;
    this.retrato.setTexture(j.gordo ? 'retrato_gordo' : 'retrato', cara);
    this.super.setVisible(j.nivel === 2 && Math.floor(this.time.now / 300) % 2 === 0);
    const cena = this.scene.get(this.chaveCena);
    this.pontos.setText(`${cena.pontos || 0}`);
    if (cena.tempo !== undefined) {
      this.relogio.setText(`${cena.tempo}`).setColor(cena.tempo <= 10 ? hex('vermelho') : hex('amarelo_fogo'));
    }
    this.fps.setText(`${Math.round(this.game.loop.actualFps)}`);
  }
}
