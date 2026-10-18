import { hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { REFEM } from '../quadros.js';

// Quanto tempo (ms) dura cada etapa depois de solto, como os prisioneiros do Metal Slug:
// pula de alegria, procura no bornal, entrega o item, bate continência e sai correndo.
const ETAPAS = { solto: 380, procura: 420, entrega: 450, continencia: 520 };
const SEGUINTE = { solto: 'procura', procura: 'entrega', entrega: 'continencia', continencia: 'fugindo' };

// Romeiro amarrado. Um tiro ou um toque solta a corda.
export class Refem extends Phaser.Physics.Arcade.Sprite {
  // opcoes.pendurado: y do galho; o refém fica pendurado pelas mãos numa corda até
  // um tiro cortar a corda (ou acertar nele).
  constructor(cena, x, y, opcoes = {}) {
    super(cena, x, y, 'refem', REFEM.amarrado[0]);
    this.galho = opcoes.pendurado || null;
    this.corda = cena.add.graphics().setDepth(7);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.setOrigin(REFEM.peX / REFEM.largura, REFEM.peY / REFEM.altura).setDepth(8);
    this.inicioX = x;
    this.inicioY = y;
    this.fala = cena.add.text(0, 0, '', estiloTexto(hex('branco'))).setOrigin(0.5).setVisible(false).setDepth(30);
    this.reiniciar();
  }

  reiniciar() {
    this.estado = this.galho ? 'pendurado' : 'amarrado';
    this.vivo = true; // "vivo" = ainda pode ser atingido (para as balas do jogador)
    this.abduzido = false;
    this.setVisible(true).setFlipX(false).setRotation(0);
    this.setOrigin(REFEM.peX / REFEM.largura, REFEM.peY / REFEM.altura);
    if (this.galho) {
      // Pendurado: o corpo de acerto vai do galho até os pés (a corda conta).
      const alto = this.inicioY - this.galho;
      this.body.setSize(16, alto).setOffset(REFEM.peX - 6, REFEM.peY - alto);
      this.body.allowGravity = false;
      this.body.setVelocity(0, 0);
    } else {
      this.body.setSize(18, 30).setOffset(REFEM.peX - 8, REFEM.peY - 30);
      this.body.allowGravity = true;
    }
    this.body.enable = true;
  }

  // Tiro na corda (ou no refém pendurado): a corda arrebenta e ele cai.
  cair() {
    const cena = this.scene;
    this.estado = 'caindo';
    this.body.allowGravity = true;
    this.body.setSize(18, 30).setOffset(REFEM.peX - 8, REFEM.peY - 30);
    this.y += 0;
    cena.efeitos.faisca(this.x + REFEM.maosX, this.galho + 6, 6);
    this.falar('VALEI-ME!');
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
    if (this.estado === 'pendurado') {
      this.cair();
      return;
    }
    if (this.estado !== 'amarrado' || this.abduzido) return;
    this.soltar();
  }

  soltar() {
    const cena = this.scene;
    this.vivo = false;
    cena.refensSalvos = (cena.refensSalvos || 0) + 1;
    cena.pontuar(500, this.x, this.y - 56);
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
      this.scene.soltarItem(this.x + 18, this.y - 26, Phaser.Utils.Array.GetRandom(this.scene.premios));
    }
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (this.abduzido) return;
    // Corda até o galho (cortada: só um pedaço balançando no galho).
    this.corda.clear();
    if (this.galho && this.visible) {
      const cx = this.x + (this.flipX ? -REFEM.maosX : REFEM.maosX);
      this.corda.lineStyle(1, 0x9d784f, 1);
      const fim = this.estado === 'pendurado' ? this.y - REFEM.maosY : this.galho + 7;
      this.corda.lineBetween(Math.round(this.x + REFEM.maosX) + 0.5, this.galho, Math.round(cx) + 0.5, fim);
    }
    if (this.estado === 'pendurado') {
      this.setFrame(REFEM.pendurado[Math.floor(t / 400) % 2]);
      this.x = this.inicioX + Math.round(Math.sin(t / 400));
      return;
    }
    if (this.estado === 'caindo') {
      this.setFrame(REFEM.amarrado[1]);
      if (this.body.blocked.down) {
        this.scene.efeitos.poeira(this.x, this.y, 8);
        this.soltar();
      }
      return;
    }
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
