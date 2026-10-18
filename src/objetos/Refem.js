import { hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { REFEM } from '../quadros.js';
import { PREMIOS } from '../armas.js';

// Quanto tempo (ms) dura cada etapa depois de solto, como os prisioneiros do Metal Slug:
// pula de alegria, procura no bornal, entrega o item, bate continência e sai correndo.
const ETAPAS = { solto: 380, procura: 420, entrega: 450, continencia: 520 };
const SEGUINTE = { solto: 'procura', procura: 'entrega', entrega: 'continencia', continencia: 'fugindo' };

// Romeiro amarrado. Um tiro ou um toque solta a corda.
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
    this.setOrigin(REFEM.peX / REFEM.largura, REFEM.peY / REFEM.altura);
    this.body.setSize(18, 30).setOffset(REFEM.peX - 8, REFEM.peY - 30);
    this.body.allowGravity = true;
    this.body.enable = true;
  }

  // Pool de reféns escondidos em caixotes.
  esconder() {
    this.estado = 'longe';
    this.vivo = false;
    this.setVisible(false);
    this.body.enable = false;
  }

  aparecer(x, pe) {
    this.reiniciar();
    this.body.reset(x, pe - 6);
    this.scene.efeitos.poeira(x, pe, 8);
    this.falar('ME SOLTA!');
  }

  levarDano() {
    if (this.estado !== 'amarrado' || this.abduzido) return;
    this.soltar();
  }

  soltar() {
    const cena = this.scene;
    this.vivo = false;
    this.mudar('solto');
    this.body.setVelocityY(-120);
    cena.efeitos.faisca(this.x, this.y - 18, 8);
    cena.efeitos.poeira(this.x, this.y, 6);
    this.falar('OBRIGADO!');
  }

  falar(texto) {
    this.fala.setText(texto).setPosition(this.x, this.y - 52).setVisible(true).setAlpha(1);
    this.scene.tweens.killTweensOf(this.fala);
    this.scene.tweens.add({ targets: this.fala, alpha: 0, delay: 600, duration: 300 });
  }

  mudar(estado) {
    this.estado = estado;
    this.fim = this.scene.time.now + (ETAPAS[estado] || 0);
    if (REFEM[estado] !== undefined) this.setFrame(REFEM[estado]);
    if (estado === 'entrega') {
      // O item sai da mão levantada.
      this.scene.soltarItem(this.x + 18, this.y - 26, Phaser.Utils.Array.GetRandom(PREMIOS));
    }
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (this.abduzido) return;
    if (this.estado === 'amarrado') {
      // Se debate: balança para um lado e para o outro, com um pulinho de vez em quando.
      const ciclo = Math.floor(t / 160) % 8;
      this.setFrame(REFEM.amarrado[ciclo === 3 ? 1 : ciclo === 5 ? 2 : 0]);
      const j = this.scene.jogador;
      if (!j.morto && Math.abs(j.x - this.x) < 14 && Math.abs(j.pe - this.y) < 20) this.soltar();
    } else if (ETAPAS[this.estado]) {
      this.body.setVelocityX(0);
      if (t > this.fim) this.mudar(SEGUINTE[this.estado]);
    } else if (this.estado === 'fugindo') {
      if (!this.flipX) {
        // Espelhado, o pé fica do outro lado do desenho.
        this.setFlipX(true).setOrigin((REFEM.largura - REFEM.peX) / REFEM.largura, REFEM.peY / REFEM.altura);
        this.body.setOffset(REFEM.largura - REFEM.peX - 8, REFEM.peY - 30);
      }
      this.body.setVelocityX(-110);
      this.setFrame(REFEM.corrida[Math.floor(t / 90) % REFEM.corrida.length]);
      if (this.x < this.scene.cameras.main.worldView.x - 30) {
        this.estado = 'longe';
        this.setVisible(false);
        this.body.enable = false;
        if (this.temporario || !this.scene.tudoVolta) return;
        this.scene.time.delayedCall(10000, () => {
          this.reiniciar();
          this.body.reset(this.inicioX, this.inicioY - 40);
        });
      }
    }
  }
}
