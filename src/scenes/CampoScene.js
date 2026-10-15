import { LARGURA, ALTURA } from '../config.js';
import { Efeitos } from '../efeitos.js';
import { Jogador } from '../objetos/Jogador.js';
import { Inimigo } from '../objetos/Inimigo.js';
import { BalasInimigas } from '../objetos/BalasInimigas.js';
import { Balas } from '../objetos/Balas.js';
import { ARMAS } from '../armas.js';
import { Refem } from '../objetos/Refem.js';
import { Disco, Bode } from '../objetos/Disco.js';

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
    for (const [x, y] of [[176, c - 18], [412, c - 18], [436, c - 18], [424, c - 36], [860, c - 18]]) {
      this.add.image(x, y, 'caixote').setOrigin(0).setDepth(6);
      this.solido(x, y, 24, 18);
    }
    for (const [x, y, n] of [[560, 150, 4], [740, 162, 2], [980, 146, 3]]) {
      this.add.tileSprite(x, y, 32 * n, 12, 'laje').setOrigin(0).setDepth(6);
      this.solido(x, y, 32 * n, 12);
    }

    this.efeitos = new Efeitos(this, this.solidos);

    this.alvos = this.physics.add.group({ runChildUpdate: false });
    for (const [x, y, tipo] of [[320, c, 'xeremita'], [624, 150, 'volante'], [880, c, 'volante'], [1060, c, 'xeremita']]) {
      const inimigo = new Inimigo(this, x, y, tipo);
      inimigo.setDepth(9);
      this.alvos.add(inimigo);
      inimigo.ajustarCorpo();
    }
    // Refém (pode ser atingido pelas balas do Lampião, que soltam a corda) e o bode Fubá.
    this.refem = new Refem(this, 340, c);
    this.alvos.add(this.refem);
    this.refem.reiniciar();
    this.bode = new Bode(this, 720, c);
    this.physics.add.collider(this.bode, this.solidos);
    this.disco = new Disco(this, 560, [this.refem, this.bode]);
    this.alvos.add(this.disco);
    this.disco.body.allowGravity = false;
    this.physics.add.collider(this.alvos, this.solidos, null, (a) => a !== this.disco);

    this.balas = new Balas(this, this.solidos, this.alvos, (alvo, bala) => {
      alvo.levarDano(bala.tipo.dano, bala.x, false, bala.tipo.morte);
      this.efeitos.faisca(bala.x, bala.y, 4);
    });

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
    this.criarCaixasDeArma(c);

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
    for (const alvo of this.alvos.getChildren()) {
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
    alvo.levarDano(5, this.jogador.x, true);
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
    for (const alvo of this.alvos.getChildren()) {
      if (alvo.vivo && Phaser.Math.Distance.Between(x, y, alvo.x, alvo.y - 18) < raio) {
        alvo.levarDano(dano, x, true);
      }
    }
  }

  // Caixas de arma espalhadas pelo campo de treino; voltam depois de um tempo.
  criarCaixasDeArma(chao) {
    this.caixasArma = this.physics.add.staticGroup();
    for (const [x, arma] of [[240, 'madsen'], [520, 'bacamarte'], [780, 'rojao'], [1010, 'desintegrador']]) {
      const caixa = this.caixasArma.create(x, chao, `caixa_${ARMAS[arma].letra}`).setOrigin(0.5, 1).setDepth(7);
      caixa.refreshBody();
      caixa.arma = arma;
    }
    this.caixasTemp = [];
    for (let k = 0; k < 3; k++) {
      const caixa = this.caixasArma.create(-100, -100, 'caixa_M').setOrigin(0.5, 1).setDepth(7);
      caixa.temporaria = true;
      caixa.disableBody(true, true);
      this.caixasTemp.push(caixa);
    }
    this.physics.add.overlap(this.jogador.corpo, this.caixasArma, (corpo, caixa) => {
      if (!caixa.active || this.jogador.morto) return;
      this.pegarArma(caixa);
    });
  }

  pegarArma(caixa) {
    const arma = ARMAS[caixa.arma];
    this.jogador.trocarArma(caixa.arma);
    caixa.disableBody(true, true);
    this.efeitos.faisca(caixa.x, caixa.y - 8, 10);
    this.events.emit('arma', arma.nome);
    if (!caixa.temporaria) this.time.delayedCall(8000, () => caixa.enableBody(false, 0, 0, true, true));
  }

  // Caixa deixada por um refém (pool de caixas temporárias).
  soltarCaixa(x, y, arma) {
    const caixa = this.caixasTemp.find((cx) => !cx.active) || this.caixasTemp[0];
    caixa.setTexture(`caixa_${ARMAS[arma].letra}`);
    caixa.arma = arma;
    const chao = this.chaoAbaixo(x, y);
    caixa.enableBody(true, x, chao, true, true);
    caixa.refreshBody();
    // Cai do ponto onde o refém estava até o chão.
    caixa.y = y;
    this.tweens.add({ targets: caixa, y: chao, duration: Math.max(80, (chao - y) * 4), ease: 'Quad.easeIn' });
  }

  // Primeira superfície sólida abaixo de (x, y).
  chaoAbaixo(x, y) {
    for (let yy = Math.floor(y); yy < ALTURA; yy += 2) {
      if (this.physics.overlapRect(x - 1, yy, 2, 2, false, true).length) return yy;
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
