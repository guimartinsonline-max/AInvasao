import { hex, P } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { SEGREDOS } from '../quadros.js';
import { som } from '../som.js';

// Segredos para quem atira em tudo (como no Metal Slug): coisas do cenário que,
// depois de alguns tiros, soltam um prêmio. Cacimba (refém escondido lá dentro),
// ninho de galinha no telhado (arma), canoa encalhada (buchada) e a biruta do
// campo de pouso (granadas). De vez em quando dão um brilho discreto.

export class Segredo extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, x, pe, tipo, premio) {
    const chave = tipo === 'biruta' ? 'biruta' : `segredo_${tipo}`;
    super(cena, x, pe, chave, 0);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.tipo = tipo;
    this.premio = premio;
    this.segredo = true;
    this.persegue = false; // o Buscapé não persegue segredo
    this.voa = true;
    this.vivo = true;
    const q = SEGREDOS[chave] || { largura: 26, altura: 46, vida: 3 };
    this.vida = q.vida;
    this.setOrigin(0.5, 1).setDepth(tipo === 'biruta' ? 5.5 : 6);
    this.body.allowGravity = false;
    this.body.setImmovable(true);
    if (tipo === 'biruta') this.body.setSize(22, 14).setOffset(4, 2); // só o pano listrado
    else this.body.setSize(q.largura - 4, q.altura - 2).setOffset(2, 2);
    this.proximoBrilho = cena.time.now + Phaser.Math.Between(1500, 4000);
  }

  get pe() { return this.y; }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (this.tipo === 'biruta' && this.vivo) this.setFrame(Math.floor(t / 260) % 3);
    if (this.vivo && t > this.proximoBrilho) {
      // Brilho discreto: uma faísca só, de vez em quando.
      this.proximoBrilho = t + Phaser.Math.Between(3500, 6000);
      this.scene.efeitos.faisca(this.x + Phaser.Math.Between(-6, 6), this.y - this.height * 0.6, 1);
    }
  }

  levarDano(dano = 1) {
    if (!this.vivo) return;
    this.vida -= Math.max(1, Math.min(dano, 3));
    this.setTint(P.branco).setTintMode(Phaser.TintModes.FILL);
    this.scene.time.delayedCall(45, () => this.clearTint());
    this.x += Math.random() < 0.5 ? -1 : 1;
    this.scene.time.delayedCall(50, () => { this.x = Math.round(this.x); });
    if (this.vida <= 0) this.abrir();
  }

  abrir() {
    const cena = this.scene;
    const ef = cena.efeitos;
    this.vivo = false;
    this.body.enable = false;
    som('segredo');
    cena.pontuar(1000, this.x, this.y - this.height - 6);
    const txt = cena.add.text(this.x, this.y - this.height - 18, 'SEGREDO!', estiloTexto(hex('amarelo_claro'))).setOrigin(0.5).setDepth(31);
    cena.tweens.add({ targets: txt, y: txt.y - 16, alpha: 0, delay: 700, duration: 500, onComplete: () => txt.destroy() });
    for (let k = 0; k < 3; k++) cena.time.delayedCall(k * 90, () => ef.faisca(this.x + Phaser.Math.Between(-8, 8), this.y - this.height / 2, 5));
    if (this.tipo === 'biruta') {
      // O mastro tomba e a biruta cai no chão.
      cena.tweens.add({ targets: this, angle: 80, duration: 500, ease: 'Bounce.easeOut' });
      ef.poeira(this.x + 20, this.y, 8);
    } else {
      this.setFrame(1);
      ef.poeira(this.x, this.y, 8);
      if (this.tipo !== 'ninho') ef.tabuas(this.x, this.y - this.height / 2);
    }
    if (this.tipo === 'ninho') {
      // A galinha choca sai voando, cacarejando.
      const g = cena.add.sprite(this.x, this.y - 6, 'galinha', 2).setDepth(21);
      som('galinha');
      const cc = cena.add.text(this.x, this.y - 30, 'CÓ-CÓ-CÓ!', estiloTexto(hex('branco'))).setOrigin(0.5).setDepth(31);
      cena.tweens.add({ targets: cc, alpha: 0, y: cc.y - 10, delay: 500, duration: 400, onComplete: () => cc.destroy() });
      cena.tweens.add({ targets: g, x: g.x + 140, y: g.y - 70, duration: 1400, ease: 'Sine.easeOut', onComplete: () => g.destroy() });
      cena.time.addEvent({ delay: 80, repeat: 16, callback: () => g.active && g.setFrame(2 + ((g.frame.name + 1) % 2)) });
    }
    // O prêmio.
    const p = this.premio;
    const y = this.y - Math.min(20, this.height / 2);
    cena.time.delayedCall(150, () => {
      if (p === 'refem') cena.surpresaRefem(this.x + 20, this.y);
      else if (p === 'arma') cena.soltarItem(this.x, y, Phaser.Utils.Array.GetRandom(cena.premios));
      else cena.soltarItem(this.x, y, p);
    });
  }
}
