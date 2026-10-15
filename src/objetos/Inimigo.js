import { P, hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { INIMIGOS } from '../quadros.js';

// Comportamento por tipo. Distâncias em pixels, tempos em ms.
const TIPOS = {
  volante: {
    vida: 2, velocidade: 34, alcance: 230, distancia: 110, recarga: [1100, 1900],
    bala: 'volante', gritos: ['AAAI!', 'MÃE!', 'SOCORRO!', 'AI, CAPITÃO!'], panico: 46,
  },
  xeremita: {
    vida: 3, velocidade: 26, alcance: 240, distancia: 130, recarga: [1500, 2400],
    bala: 'raio', gritos: ['GLUB!', 'BZZT!', 'IIIH!', 'XERÉM!'], panico: 0,
  },
};

// Inimigo comum: anda até o Lampião, para a uma distância e atira.
// Ao morrer voa ou derrete de forma cômica; no campo de treino renasce.
export class Inimigo extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, x, y, tipo) {
    const q = INIMIGOS[tipo];
    super(cena, x, y, tipo, q.parado);
    this.tipo = tipo;
    this.q = q;
    this.cfg = TIPOS[tipo];
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.inicioX = x;
    this.inicioY = y;
    this.grito = cena.add.text(0, 0, '', estiloTexto(hex('branco'))).setOrigin(0.5).setVisible(false).setDepth(30);
    this.reiniciar();
  }

  reiniciar() {
    this.vivo = true;
    this.vida = this.cfg.vida;
    this.direcao = -1;
    this.estado = 'andando';
    this.proximoTiro = 0;
    this.fimEstado = 0;
    this.passo = 0;
    this.setRotation(0).setVisible(true).clearTint();
    this.ajustarCorpo();
  }

  ajustarCorpo() {
    const q = this.q;
    this.body.setSize(q.corpoL, q.corpoA);
    this.virar(this.direcao || -1);
  }

  virar(d) {
    this.direcao = d;
    const q = this.q;
    // Desenhado para a direita; espelha quando olha para a esquerda.
    this.setFlipX(d < 0);
    const ox = d > 0 ? q.peX : q.largura - q.peX;
    this.setOrigin(ox / q.largura, q.peY / q.altura);
    this.body.setOffset(ox - q.corpoL / 2, q.peY - q.corpoA);
  }

  levarDano(dano, origemX, forte = false, morte = null) {
    if (!this.vivo) return;
    const ef = this.scene.efeitos;
    this.vida -= dano;
    this.setTint(P.branco).setTintMode(Phaser.TintModes.FILL);
    this.scene.time.delayedCall(forte ? 90 : 50, () => this.vivo && this.clearTint());
    const lado = Math.sign(this.x - origemX) || 1;
    this.x += lado;
    if (forte) ef.parar(60);
    if (this.vida <= 0) this.morrer(lado, forte, morte);
  }

  morrer(lado, forte, morte = null) {
    const cena = this.scene;
    const ef = cena.efeitos;
    this.vivo = false;
    this.clearTint();
    if (morte === 'derrete') {
      // Raio desintegrador: fica verde, treme e vira gosma no lugar.
      this.setFrame(this.q.morte).setTint(P.alien).setTintMode(Phaser.TintModes.FILL);
      this.body.setVelocity(0, 0);
      this.body.checkCollision.none = true;
      this.body.allowGravity = false;
      this.grito.setText('BZZZT!').setPosition(this.x, this.y - 50).setVisible(true).setAlpha(1);
      cena.tweens.add({ targets: this.grito, y: this.y - 66, alpha: 0, duration: 700, onComplete: () => this.grito.setVisible(false) });
      cena.time.delayedCall(260, () => {
        ef.gosma(this.x, this.y - 18, 40);
        this.setVisible(false);
        this.body.enable = false;
        this.body.allowGravity = true;
      });
      cena.time.delayedCall(2600, () => this.renascer());
      return;
    }
    this.setFrame(this.q.morte);
    this.body.checkCollision.none = true;
    this.body.setVelocity(lado * (forte ? 150 : 80), forte ? -320 : -220);
    this.body.setAngularVelocity(lado * (forte ? 900 : 500));
    ef.parar(forte ? 90 : 60);
    ef.tremer(0.006, 140);

    this.grito.setText(Phaser.Utils.Array.GetRandom(this.cfg.gritos)).setPosition(this.x, this.y - 50)
      .setVisible(true).setAlpha(1);
    cena.tweens.add({ targets: this.grito, y: this.y - 66, alpha: 0, duration: 800, onComplete: () => this.grito.setVisible(false) });

    cena.time.delayedCall(420, () => {
      if (this.tipo === 'xeremita') ef.gosma(this.x, this.y - 16, 36);
      else ef.poeira(this.x, this.y, 10);
      ef.faisca(this.x, this.y - 16, 6);
      this.setVisible(false);
      this.body.enable = false;
    });
    cena.time.delayedCall(2600, () => this.renascer());
  }

  renascer() {
    this.reiniciar();
    this.body.enable = true;
    this.body.checkCollision.none = false;
    this.body.setAngularVelocity(0);
    this.body.reset(this.inicioX, this.inicioY - 140);
    this.caindo = true;
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (!this.vivo) return;
    const cena = this.scene;
    if (this.caindo) {
      if (this.body.blocked.down) {
        this.caindo = false;
        cena.efeitos.poeira(this.x, this.y, 8);
      }
      return;
    }
    if (cena.efeitos.congelado) return;
    const j = cena.jogador;
    const dx = j.x - this.x;
    const dist = Math.abs(dx);
    const q = this.q;
    const cfg = this.cfg;

    if (this.estado === 'panico') {
      // Foge correndo, de costas para o Lampião, gritando.
      this.body.setVelocityX(this.temChaoAFrente() ? this.direcao * cfg.velocidade * 2.2 : 0);
      this.passo += dt;
      this.setFrame(q.panico);
      if (t > this.fimEstado) this.estado = 'andando';
      return;
    }
    if (cfg.panico && dist < cfg.panico && !j.morto) {
      this.estado = 'panico';
      this.fimEstado = t + 900;
      this.virar(dx > 0 ? -1 : 1);
      this.grito.setText('AAAH!').setPosition(this.x, this.y - 50).setVisible(true).setAlpha(1);
      cena.tweens.add({ targets: this.grito, alpha: 0, delay: 500, duration: 300 });
      return;
    }

    if (dist < cfg.alcance && !j.morto) this.virar(dx > 0 ? 1 : -1);
    if (this.estado === 'atirando') {
      this.body.setVelocityX(0);
      if (t > this.fimEstado) {
        this.estado = 'andando';
        this.setFrame(q.parado);
      }
      return;
    }
    if (dist > cfg.distancia && dist < cfg.alcance * 1.4 && !j.morto && this.temChaoAFrente()) {
      this.body.setVelocityX(this.direcao * cfg.velocidade);
      this.passo += dt;
      this.setFrame(q.andar[Math.floor(this.passo / 150) % q.andar.length]);
    } else {
      this.body.setVelocityX(0);
      this.setFrame(q.parado);
    }
    if (dist < cfg.alcance && !j.morto && t > this.proximoTiro && this.body.blocked.down) {
      this.atirar(t);
    }
  }

  // Não anda para fora da beirada de uma plataforma.
  temChaoAFrente() {
    const x = this.x + this.direcao * 10;
    return this.scene.physics.overlapRect(x - 1, this.y + 1, 2, 4, false, true).length > 0;
  }

  atirar(t) {
    const q = this.q;
    this.estado = 'atirando';
    this.fimEstado = t + 350;
    this.proximoTiro = t + Phaser.Math.Between(...this.cfg.recarga);
    this.setFrame(q.atira);
    const x = this.x + this.direcao * q.cano[0];
    const y = this.y - q.cano[1];
    const j = this.scene.jogador;
    this.scene.balasInimigas.disparar(x, y, this.direcao, this.cfg.bala, j.x, j.pe - 20);
  }
}
