import { LARGURA, ALTURA } from '../config.js';
import { Efeitos } from '../efeitos.js';
import { Jogador } from '../objetos/Jogador.js';
import { Alvo } from '../objetos/Alvo.js';
import { Balas } from '../objetos/Balas.js';

const LARGURA_MUNDO = LARGURA * 3;
const CHAO_Y = 192;
const RAIO_GRANADA = 44;

// Campo de treino da etapa 2: correr, pular, atirar e explodir alvos parados.
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
    for (const [x, y] of [[300, c], [624, 150], [930, c]]) {
      const alvo = new Alvo(this, x, y);
      alvo.setDepth(9);
      this.alvos.add(alvo);
      alvo.ajustarCorpo();
    }
    this.physics.add.collider(this.alvos, this.solidos);

    this.balas = new Balas(this, this.solidos, this.alvos, (alvo, bala) => {
      alvo.levarDano(1, bala.x);
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
    this.efeitos.explosao(x, y - 4, 1);
    for (const alvo of this.alvos.getChildren()) {
      if (alvo.vivo && Phaser.Math.Distance.Between(x, y, alvo.x, alvo.y - 18) < RAIO_GRANADA) {
        alvo.levarDano(10, x, true);
      }
    }
  }

  update(t, dt) {
    const c = this.controles;
    c.atualizar();
    if (c.apertou('voltar')) {
      this.scene.start('Menu');
      return;
    }

    if (!this.efeitos.congelado) this.jogador.atualizar(dt, c);
    this.balas.atualizar();
    this.efeitos.atualizar();

    for (const g of this.granadas.getChildren()) {
      if (g.active && t >= g.explodeEm) this.explodirGranada(g);
    }

    // A câmera olha um pouco para onde o Lampião está virado.
    const cam = this.cameras.main;
    this.olhar += (this.jogador.direcao * -40 - this.olhar) * 0.04;
    cam.setFollowOffset(Math.round(this.olhar), 0);

    this.ventoNuvens += dt * 0.004;
    for (const [camada, fator] of this.camadas) camada.tilePositionX = Math.round(cam.scrollX * fator);
    this.nuvens[0].tilePositionX = Math.round(cam.scrollX * this.nuvens[1] + this.ventoNuvens);
  }
}
