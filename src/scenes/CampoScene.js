import { LARGURA, ALTURA } from '../config.js';
import { P } from '../paleta.js';
import { Efeitos } from '../efeitos.js';
import { Jogador } from '../objetos/Jogador.js';
import { Alvo } from '../objetos/Alvo.js';
import { Balas } from '../objetos/Balas.js';

const LARGURA_MUNDO = LARGURA * 3;
const CHAO_Y = 196;
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
    this.solido(0, CHAO_Y, LARGURA_MUNDO, ALTURA - CHAO_Y);
    for (const [x, y] of [[176, 180], [412, 180], [436, 180], [424, 164], [860, 180]]) {
      this.add.image(x, y, 'caixote').setOrigin(0).setDepth(6);
      this.solido(x, y, 24, 16);
    }
    for (const [x, y, n] of [[560, 148, 4], [740, 160, 2], [980, 140, 3]]) {
      this.add.tileSprite(x, y, 32 * n, 12, 'pedra').setOrigin(0).setDepth(6);
      this.solido(x, y, 32 * n, 12);
    }

    this.efeitos = new Efeitos(this, this.solidos);

    this.alvos = this.physics.add.group({ runChildUpdate: false });
    for (const [x, y] of [[300, CHAO_Y], [624, 148], [930, CHAO_Y]]) {
      const alvo = new Alvo(this, x, y);
      alvo.setDepth(9);
      this.alvos.add(alvo);
      alvo.body.setSize(10, 16).setOffset(3, 2);
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

    this.jogador = new Jogador(this, 60, CHAO_Y - 20);
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
    // Céu em faixas (sem degradê, para manter a paleta).
    const faixas = [[0, 'ceu_escuro'], [40, 'ceu'], [96, 'ceu_claro'], [128, 'horizonte']];
    faixas.forEach(([y, cor], i) => {
      const fim = i + 1 < faixas.length ? faixas[i + 1][0] : ALTURA;
      this.add.rectangle(0, y, LARGURA, fim - y, P[cor]).setOrigin(0).setScrollFactor(0);
    });
    this.nuvens = [];
    for (const [x, y] of [[30, 30], [180, 18], [300, 50], [420, 26]]) {
      this.nuvens.push(this.add.image(x, y, 'nuvem').setScrollFactor(0.05, 0));
    }
    this.camadas = [
      [this.add.tileSprite(0, 92, LARGURA, 60, 'serras').setOrigin(0).setScrollFactor(0), 0.15],
      [this.add.tileSprite(0, 122, LARGURA, 50, 'morros').setOrigin(0).setScrollFactor(0), 0.35],
    ];
    this.add.rectangle(0, 170, LARGURA, CHAO_Y - 170, P.areia_clara).setOrigin(0).setScrollFactor(0);
    this.camadas.push(
      [this.add.tileSprite(0, CHAO_Y - 38, LARGURA, 40, 'mato').setOrigin(0).setScrollFactor(0), 0.65],
    );
  }

  alvoProximo(x, y, direcao, alcance) {
    for (const alvo of this.alvos.getChildren()) {
      if (!alvo.vivo) continue;
      const dx = (alvo.x - x) * direcao;
      if (dx > -4 && dx < alcance && Math.abs(alvo.y - 8 - y) < 18) return alvo;
    }
    return null;
  }

  peixeirada(x, y, direcao, alvo) {
    this.corte.setPosition(x, y).setFlipX(direcao < 0).setVisible(true).setAlpha(1);
    this.tweens.killTweensOf(this.corte);
    this.tweens.add({ targets: this.corte, alpha: 0, duration: 120, onComplete: () => this.corte.setVisible(false) });
    alvo.levarDano(5, this.jogador.x, true);
    this.efeitos.faisca(alvo.x, alvo.y - 10, 6);
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
      if (alvo.vivo && Phaser.Math.Distance.Between(x, y, alvo.x, alvo.y - 8) < RAIO_GRANADA) {
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

    for (const [camada, fator] of this.camadas) camada.tilePositionX = Math.round(cam.scrollX * fator);
  }
}
