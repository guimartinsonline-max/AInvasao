import { P, hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { ALIEN } from '../quadros.js';

const VIDA = 14;
const GRITOS = ['AAAI!', 'UÉÉÉ!', 'GLUB!', 'IIIH!'];

// Alienígena parado para testar tiro e game feel. Ao morrer, renasce caindo do céu.
export class Alvo extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, x, y) {
    super(cena, x, y, 'alien', ALIEN.aberto);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.setOrigin(ALIEN.peX / ALIEN.largura, ALIEN.peY / ALIEN.altura);
    this.ajustarCorpo();
    this.proximaPiscada = 0;
    this.inicioX = x;
    this.inicioY = y;
    this.vivo = true;
    this.vida = VIDA;
    this.grito = cena.add.text(0, 0, '', estiloTexto(hex('branco'))).setOrigin(0.5).setVisible(false).setDepth(30);
  }

  ajustarCorpo() {
    this.body.setSize(16, 36).setOffset(12, 6);
  }

  levarDano(dano, origemX, forte = false) {
    if (!this.vivo) return;
    const ef = this.scene.efeitos;
    this.vida -= dano;

    // Pisca branco.
    this.setTint(P.branco).setTintMode(Phaser.TintModes.FILL);
    this.scene.time.delayedCall(forte ? 90 : 50, () => this.vivo && this.clearTint());

    const lado = Math.sign(this.x - origemX) || 1;
    this.x += lado;
    if (forte) ef.parar(60);

    if (this.vida <= 0) this.morrer(lado, forte);
  }

  morrer(lado, forte) {
    const cena = this.scene;
    const ef = cena.efeitos;
    this.vivo = false;
    this.clearTint();

    // Morte exagerada: voa girando, grita e estoura em gosma.
    this.body.checkCollision.none = true;
    this.body.setVelocity(lado * (forte ? 140 : 70), forte ? -320 : -230);
    this.body.setAngularVelocity(lado * 900);
    ef.parar(forte ? 90 : 60);
    ef.tremer(0.006, 140);

    this.grito.setText(Phaser.Utils.Array.GetRandom(GRITOS)).setPosition(this.x, this.y - 48).setVisible(true).setAlpha(1);
    cena.tweens.add({ targets: this.grito, y: this.y - 64, alpha: 0, duration: 700, onComplete: () => this.grito.setVisible(false) });

    cena.time.delayedCall(380, () => {
      ef.gosma(this.x, this.y - 20, 36);
      ef.faisca(this.x, this.y - 20, 8);
      ef.tremer(0.008, 160);
      this.setVisible(false);
      this.body.enable = false;
    });
    cena.time.delayedCall(2000, () => this.renascer());
  }

  renascer() {
    this.vida = VIDA;
    this.vivo = true;
    this.setRotation(0).setVisible(true).setScale(1);
    this.body.enable = true;
    this.body.checkCollision.none = false;
    this.body.setAngularVelocity(0);
    this.body.reset(this.inicioX, this.inicioY - 140);
    this.caindo = true;
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    // Pisca os olhos de vez em quando.
    if (this.vivo && t > this.proximaPiscada) {
      this.setFrame(this.frame.name === ALIEN.fechado ? ALIEN.aberto : ALIEN.fechado);
      this.proximaPiscada = t + (this.frame.name === ALIEN.fechado ? 120 : Phaser.Math.Between(1500, 4000));
    }
    if (this.caindo && this.body.blocked.down) {
      this.caindo = false;
      this.scene.efeitos.poeira(this.x, this.y, 8);
    }
  }
}
