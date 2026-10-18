import { hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { REFEM } from '../quadros.js';

const PREMIOS = ['madsen', 'bacamarte', 'rojao', 'desintegrador', 'granadas'];

// Romeiro amarrado. Um tiro ou um toque solta a corda: ele bate continência,
// deixa um item e sai correndo (como os prisioneiros do Metal Slug).
export class Refem extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, x, y) {
    super(cena, x, y, 'refem', REFEM.amarrado[0]);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.setOrigin(REFEM.peX / REFEM.largura, REFEM.peY / REFEM.altura).setDepth(8);
    this.inicioX = x;
    this.inicioY = y;
    this.fala = cena.add.text(0, 0, '', estiloTexto(hex('branco'))).setOrigin(0.5).setVisible(false).setDepth(30);
    this.reiniciar();
  }

  reiniciar() {
    this.estado = 'amarrado';
    this.vivo = true; // "vivo" = ainda pode ser atingido (para as balas do jogador)
    this.abduzido = false;
    this.setVisible(true).setFlipX(false).setRotation(0);
    this.body.setSize(18, 24).setOffset(REFEM.peX - 9, REFEM.peY - 24);
    this.body.allowGravity = true;
    this.body.enable = true;
  }

  levarDano() {
    if (this.estado !== 'amarrado' || this.abduzido) return;
    this.soltar();
  }

  soltar() {
    const cena = this.scene;
    this.estado = 'continencia';
    this.vivo = false;
    this.fim = cena.time.now + 700;
    this.setFrame(REFEM.continencia);
    cena.efeitos.faisca(this.x, this.y - 18, 8);
    this.fala.setText('OBRIGADO!').setPosition(this.x, this.y - 44).setVisible(true).setAlpha(1);
    cena.tweens.add({ targets: this.fala, alpha: 0, delay: 600, duration: 300 });
    cena.soltarItem(this.x + 12, this.y - 20, Phaser.Utils.Array.GetRandom(PREMIOS));
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (this.abduzido) return;
    if (this.estado === 'amarrado') {
      // Se debate de vez em quando.
      this.setFrame(REFEM.amarrado[Math.floor(t / 180) % 6 === 0 ? 1 : 0]);
      const j = this.scene.jogador;
      if (!j.morto && Math.abs(j.x - this.x) < 14 && Math.abs(j.pe - this.y) < 20) this.soltar();
    } else if (this.estado === 'continencia') {
      this.body.setVelocityX(0);
      if (t > this.fim) this.estado = 'fugindo';
    } else if (this.estado === 'fugindo') {
      this.setFlipX(true);
      this.body.setVelocityX(-110);
      this.setFrame(REFEM.corrida[Math.floor(t / 90) % REFEM.corrida.length]);
      if (this.x < this.scene.cameras.main.worldView.x - 30) {
        this.estado = 'longe';
        this.setVisible(false);
        this.body.enable = false;
        this.scene.time.delayedCall(10000, () => {
          this.reiniciar();
          this.body.reset(this.inicioX, this.inicioY - 40);
        });
      }
    }
  }
}
