import { LARGURA, ALTURA } from '../config.js';
import { Efeitos } from '../efeitos.js';
import { Jogador } from '../objetos/Jogador.js';
import { Inimigo } from '../objetos/Inimigo.js';
import { BalasInimigas } from '../objetos/BalasInimigas.js';
import { Balas } from '../objetos/Balas.js';
import { ARMAS } from '../armas.js';
import { Refem } from '../objetos/Refem.js';
import { Disco, Bode } from '../objetos/Disco.js';
import { Itens } from '../objetos/Itens.js';
import { Caixotes } from '../objetos/Caixotes.js';
import { estiloTexto } from '../texto.js';
import { hex } from '../paleta.js';

const LARGURA_MUNDO = LARGURA * 3;
const CHAO_Y = 192;
const RAIO_GRANADA = 44;

// Campo de treino: correr, pular, atirar e enfrentar soldados da Volante e xeremitas.
export class CampoScene extends Phaser.Scene {
  constructor() {
    super('Campo');
  }

  create() {
    this.controles = this.game.controles;
    this.physics.world.setBounds(0, -200, LARGURA_MUNDO, ALTURA + 400);

    this.criarFundo();

    this.solidos = this.physics.add.staticGroup();
    this.add.tileSprite(0, CHAO_Y, LARGURA_MUNDO, ALTURA - CHAO_Y, 'chao').setOrigin(0).setDepth(5);
    this.solido(0, CHAO_Y + 2, LARGURA_MUNDO, ALTURA - CHAO_Y);
    // Capim seco na beira do chão.
    for (let x = 8; x < LARGURA_MUNDO; x += Phaser.Math.Between(30, 70)) {
      this.add.image(x, CHAO_Y + 3, 'touceiras', Phaser.Math.Between(0, 3)).setOrigin(0.5, 1).setDepth(6);
    }
    const c = CHAO_Y + 2;
    for (const [x, y, n] of [[560, 150, 4], [740, 162, 2], [980, 146, 3]]) {
      this.add.tileSprite(x, y, 32 * n, 12, 'laje').setOrigin(0).setDepth(6);
      this.solido(x, y, 32 * n, 12);
    }

    this.efeitos = new Efeitos(this, this.solidos);
    // Caixotes destrutíveis (o de cima, empilhado, cai quando o de baixo quebra).
    this.caixotes = new Caixotes(this, [[176, c - 18], [412, c - 18], [436, c - 18], [424, c - 36], [860, c - 18],
      [944, c - 24, 'barril'], [963, c - 24, 'barril'], [953, c - 48, 'barril']]);

    this.alvos = this.physics.add.group({ runChildUpdate: false });
    for (const [x, y, tipo, escudo] of [[320, c, 'xeremita'], [624, 150, 'volante'], [880, c, 'volante', true],
      [1060, c, 'xeremita']]) {
      const inimigo = new Inimigo(this, x, y, tipo, { escudo });
      inimigo.setDepth(9);
      this.alvos.add(inimigo);
      inimigo.ajustarCorpo();
    }
    // Refém (pode ser atingido pelas balas do Lampião, que soltam a corda) e o bode Fubá.
    this.refem = new Refem(this, 340, c);
    this.alvos.add(this.refem);
    this.refem.reiniciar();
    // Reféns escondidos em caixotes (pool); só aparecem quando um caixote quebra.
    this.refensExtras = [];
    for (let k = 0; k < 2; k++) {
      const r = new Refem(this, -200, c);
      r.temporario = true;
      this.alvos.add(r);
      r.esconder();
      this.refensExtras.push(r);
    }
    this.bode = new Bode(this, 720, c);
    this.physics.add.collider(this.bode, this.solidos);
    this.disco = new Disco(this, 560, [this.refem, this.bode]);
    this.alvos.add(this.disco);
    this.disco.body.allowGravity = false;
    this.physics.add.collider(this.alvos, this.solidos, null, (a) => a !== this.disco);

    this.balas = new Balas(this, this.solidos, this.alvos, (alvo, bala) => {
      const tipo = bala.tipo;
      if (alvo.bloqueia && alvo.bloqueia(bala.body.velocity.x)) {
        alvo.danoEscudo(Math.max(1, tipo.dano), bala.x, bala.y);
        if (tipo.atravessa) this.balas.recolher(bala);
        return;
      }
      alvo.levarDano(tipo.dano, bala.x, false, tipo.morte, tipo.queima);
      if (tipo.impacto) this.efeitos.impacto(bala.x, bala.y, tipo.impacto);
      if (tipo.pausa) this.efeitos.parar(tipo.pausa);
    }, (caixote, bala) => caixote.levarDano(bala.tipo.dano || 1));

    this.granadas = this.physics.add.group({ defaultKey: 'granada', maxSize: 6 });
    this.physics.add.collider(this.granadas, this.solidos, (g) => {
      if (g.body.blocked.down) g.body.setAngularVelocity(g.body.angularVelocity * 0.6);
    });
    this.physics.add.overlap(this.granadas, this.alvos, (g, alvo) => {
      if (g.active && alvo.vivo) this.explodirGranada(g);
    });

    this.jogador = new Jogador(this, 60, c - 20);
    this.physics.add.collider(this.jogador.corpo, this.solidos);
    this.balasInimigas = new BalasInimigas(this, this.solidos, this.jogador);
    this.criarItens(c);

    this.corte = this.add.image(0, 0, 'corte').setVisible(false).setDepth(20);

    const cam = this.cameras.main;
    cam.setBounds(0, 0, LARGURA_MUNDO, ALTURA);
    cam.startFollow(this.jogador.corpo, true, 0.12, 0.12);
    cam.setDeadzone(24, ALTURA);
    this.olhar = 0;

    this.scene.launch('Hud', { jogador: this.jogador });
    this.events.once('shutdown', () => this.scene.stop('Hud'));
  }

  solido(x, y, w, h) {
    const r = this.add.zone(x, y, w, h).setOrigin(0);
    this.solidos.add(r);
    return r;
  }

  criarFundo() {
    // Camadas em parallax: quanto mais longe, mais devagar acompanham a câmera.
    this.add.image(0, 0, 'ceu').setOrigin(0).setScrollFactor(0);
    const camada = (chave, y, fator) => [this.add.tileSprite(0, y, LARGURA, this.textures.get(chave).source[0].height, chave)
      .setOrigin(0).setScrollFactor(0), fator];
    this.nuvens = camada('nuvens', 6, 0.03);
    this.camadas = [
      this.nuvens,
      camada('serras', 96, 0.08),
      camada('paredoes', 86, 0.2),
      camada('planicie', 168, 0.35),
      camada('caatinga', 122, 0.5),
    ];
    this.ventoNuvens = 0;
  }

  alvoProximo(x, y, direcao, alcance) {
    for (const alvo of [...this.alvos.getChildren(), ...this.caixotes.vivos()]) {
      if (!alvo.vivo) continue;
      const dx = (alvo.x - x) * direcao;
      if (dx > -6 && dx < alcance && Math.abs(alvo.y - 18 - y) < 22) return alvo;
    }
    return null;
  }

  peixeirada(x, y, direcao, alvo) {
    this.corte.setPosition(x, y).setFlipX(direcao < 0).setVisible(true).setAlpha(1);
    this.tweens.killTweensOf(this.corte);
    this.tweens.add({ targets: this.corte, alpha: 0, duration: 120, onComplete: () => this.corte.setVisible(false) });
    // A peixeirada racha o escudo de uma vez.
    if (alvo.vidaEscudo > 0) alvo.danoEscudo(alvo.vidaEscudo, alvo.x, alvo.y - 20);
    else alvo.levarDano(5, this.jogador.x, true);
    this.efeitos.faisca(alvo.x, alvo.y - 20, 6);
    this.efeitos.tremer(0.004, 80);
  }

  lancarGranada(x, y, direcao, vx) {
    const g = this.granadas.get(x, y);
    if (!g) return;
    g.setActive(true).setVisible(true).setRotation(0);
    g.body.reset(x, y);
    g.body.setBounce(0.35).setDrag(40, 0).setAngularVelocity(direcao * 600);
    g.body.setVelocity(direcao * 120 + vx * 0.4, -210);
    g.explodeEm = this.time.now + 1100;
  }

  explodirGranada(g) {
    const x = g.x;
    const y = g.y;
    g.setActive(false).setVisible(false);
    g.body.stop();
    g.body.reset(-100, -100);
    this.explodir(x, y - 4, RAIO_GRANADA, 10, 1);
  }

  // Explosão com dano em área (granada, rojão).
  explodir(x, y, raio, dano, tamanho = 1) {
    this.efeitos.explosao(x, y, tamanho);
    for (const alvo of [...this.alvos.getChildren(), ...this.caixotes.vivos()]) {
      if (alvo.vivo && Phaser.Math.Distance.Between(x, y, alvo.x, alvo.y - 18) < raio) {
        if (alvo.vidaEscudo > 0) alvo.danoEscudo(3, alvo.x, alvo.y - 13);
        alvo.levarDano(dano, x, true);
      }
    }
  }

  // Itens de arma espalhados pelo campo de treino; voltam depois de pegos.
  criarItens(chao) {
    this.itens = new Itens(this, this.solidos, this.jogador, (arma, item) => this.pegarItem(arma, item));
    for (const [x, arma] of [[130, 'candeeiro'], [240, 'madsen'], [300, 'estilingue'], [520, 'bacamarte'],
      [610, 'papo_amarelo'], [700, 'buscape'], [780, 'rojao'], [1010, 'desintegrador']]) {
      this.itens.colocar(x, chao - 20, arma, { fixo: true });
    }
  }

  pegarItem(arma, item) {
    this.efeitos.faisca(item.x, item.y - 8, 12);
    if (arma === 'granadas') {
      this.jogador.granadas = Math.min(this.jogador.granadas + 5, 20);
      this.events.emit('arma', 'GRANADAS +5');
      return;
    }
    this.jogador.trocarArma(arma);
    this.events.emit('arma', ARMAS[arma].nome);
  }

  // Item que sai saltando de um caixote quebrado ou de um refém solto.
  soltarItem(x, y, arma) {
    this.itens.colocar(x, y, arma, { pulo: true });
  }

  // Refém amarrado que estava dentro do caixote.
  surpresaRefem(x, pe) {
    const r = this.refensExtras.find((rr) => !rr.visible);
    if (r) r.aparecer(x, pe);
    else this.soltarItem(x, pe - 10, 'granadas');
  }

  // O bode Fubá estava dentro do caixote: sai correndo e berrando.
  surpresaBode(x, pe) {
    const lado = this.jogador.x < x ? 1 : -1;
    const b = this.add.sprite(x, pe, 'bode', 0).setOrigin(0.5, 1).setDepth(8).setFlipX(lado < 0);
    const grito = this.add.text(x, pe - 34, 'BÉÉÉÉ!', estiloTexto(hex('branco'))).setOrigin(0.5).setDepth(30);
    this.tweens.add({ targets: grito, y: pe - 48, alpha: 0, duration: 900, onComplete: () => grito.destroy() });
    this.tweens.add({ targets: b, y: pe - 10, duration: 140, yoyo: true, repeat: 5 });
    this.tweens.add({ targets: b, x: x + lado * 260, duration: 1600, onComplete: () => b.destroy() });
    this.efeitos.poeira(x, pe, 6);
  }

  // Primeira superfície sólida abaixo de (x, y).
  chaoAbaixo(x, y) {
    for (let yy = Math.floor(y); yy < ALTURA; yy++) {
      // O retângulo de teste conta como tocando quando a borda de baixo encosta no sólido.
      if (this.physics.overlapRect(x - 1, yy, 2, 1, false, true).length) return yy + 1;
    }
    return CHAO_Y + 2;
  }

  update(t, dt) {
    const c = this.controles;
    c.atualizar();
    if (c.apertou('voltar')) {
      this.scene.start('Menu');
      return;
    }

    if (!this.efeitos.congelado) this.jogador.atualizar(dt, c);
    this.balas.atualizar(dt);
    this.balasInimigas.atualizar();
    this.efeitos.atualizar();
    this.itens.atualizar(t);

    for (const g of this.granadas.getChildren()) {
      if (g.active && t >= g.explodeEm) this.explodirGranada(g);
    }

    // A câmera olha um pouco para onde o Lampião está virado.
    // Suavizações independentes da taxa de quadros (60, 144 ou 240 Hz).
    const cam = this.cameras.main;
    const k = dt / (1000 / 60);
    const lerp = 1 - Math.pow(1 - 0.12, k);
    cam.setLerp(lerp, lerp);
    this.olhar += (this.jogador.direcao * -40 - this.olhar) * (1 - Math.pow(1 - 0.04, k));
    cam.setFollowOffset(Math.round(this.olhar), 0);

    this.ventoNuvens += dt * 0.004;
    for (const [camada, fator] of this.camadas) camada.tilePositionX = Math.round(cam.scrollX * fator);
    this.nuvens[0].tilePositionX = Math.round(cam.scrollX * this.nuvens[1] + this.ventoNuvens);
  }
}
