import { hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { DISCO, FEIXE, BODE } from '../quadros.js';

const ALTURA_VOO = 44;
const VIDA = 10;
const PUXADA = 14; // px/s que a vítima sobe
// O raio só levanta o Lampião bem no centro e depois de um tempo dentro dele;
// nas laterais do disco dá para ficar embaixo e atirar para cima sem ser sugado.
const MEIO_RAIO = 6;
const DEMORA_PUXAR = 450; // ms dentro do raio antes de começar a subir

// Disco abdutor: voa até uma vítima (refém ou bode) e puxa com o raio.
// Atirar nele derruba a vítima; ficar dentro do raio levanta o Lampião.
export class Disco extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, x, vitimas) {
    super(cena, x, ALTURA_VOO, 'disco_voador', 0);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.body.allowGravity = false;
    this.voa = true; // não colide com o chão
    this.body.setSize(118, 31).setOffset(3, 20);
    this.setDepth(12);
    this.vitimas = vitimas;
    this.feixe = cena.add.sprite(x, ALTURA_VOO, 'feixe', 0).setOrigin(0.5, 0).setAlpha(0.55).setDepth(11).setVisible(false);
    this.grito = cena.add.text(0, 0, '', estiloTexto(hex('branco'))).setOrigin(0.5).setVisible(false).setDepth(30);
    this.inicioX = x;
    this.reiniciar();
  }

  reiniciar() {
    this.vivo = true;
    this.caindo = false;
    this.vida = VIDA;
    this.alvo = null;
    this.puxando = false;
    this.setVisible(true).clearTint();
    this.body.enable = true;
  }

  levarDano(dano, origemX) {
    if (!this.vivo) return;
    this.vida -= dano;
    this.setTint(0xffffff).setTintMode(Phaser.TintModes.FILL);
    this.scene.time.delayedCall(50, () => this.vivo && this.clearTint());
    if (this.vida <= 0) this.explodir();
  }

  // Derrubado: rodopia soltando fumaça e faísca, cai e explode no chão,
  // deixando o raio desintegrador.
  explodir() {
    const cena = this.scene;
    this.vivo = false;
    this.caindo = true;
    cena.pontuar(1000, this.x, this.y - 10);
    this.soltarVitima();
    this.feixe.setVisible(false);
    this.body.enable = false;
    this.velQueda = { x: (Math.random() < 0.5 ? -1 : 1) * 40, y: -60 };
    this.proximaFumaca = 0;
    cena.efeitos.explosao(this.x, this.y + 4, 0.5);
    this.grito.setText('BLÚRP!').setPosition(this.x, this.y - 20).setVisible(true).setAlpha(1);
    cena.tweens.add({ targets: this.grito, alpha: 0, delay: 500, duration: 300 });
  }

  cair(t, dt) {
    const cena = this.scene;
    const s = dt / 1000;
    this.velQueda.y = Math.min(this.velQueda.y + 420 * s, 260);
    this.x += this.velQueda.x * s;
    this.y += this.velQueda.y * s;
    this.rotation += 9 * s * Math.sign(this.velQueda.x);
    if (t > this.proximaFumaca) {
      cena.efeitos.fumaca(this.x, this.y);
      cena.efeitos.faisca(this.x, this.y, 2);
      this.proximaFumaca = t + 60;
    }
    if (this.y + 6 >= cena.chaoAbaixo(this.x, this.y)) {
      this.caindo = false;
      this.setVisible(false).setRotation(0);
      cena.explodir(this.x, this.y, 40, 6, 1.3);
      cena.soltarItem(this.x, this.y - 10, 'desintegrador');
      if (!cena.tudoVolta) return;
      cena.time.delayedCall(9000, () => {
        this.reiniciar();
        this.setPosition(this.inicioX, ALTURA_VOO);
        this.body.reset(this.inicioX, ALTURA_VOO);
      });
    }
  }

  soltarVitima() {
    const v = this.alvo;
    if (v && v.abduzido) {
      v.abduzido = false;
      if (v.estado === 'amarrado') v.vivo = true;
      v.body.allowGravity = true;
      v.body.setVelocity(0, 0);
    }
    this.puxando = false;
  }

  escolherAlvo() {
    let melhor = null;
    for (const v of this.vitimas) {
      if (!v.visible || v.abduzido || !v.body.enable) continue;
      if (v.estado && v.estado !== 'amarrado' && v.estado !== 'andando') continue;
      if (!melhor || Math.abs(v.x - this.x) < Math.abs(melhor.x - this.x)) melhor = v;
    }
    return melhor;
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (this.caindo) {
      this.cair(t, dt);
      return;
    }
    if (!this.vivo) return;
    this.setFrame(Math.floor(t / 150) % 2);
    this.feixe.setFrame(Math.floor(t / 100) % 2);
    this.y = ALTURA_VOO + Math.round(Math.sin(t / 400) * 2);
    if (!this.alvo || !this.alvo.visible) this.alvo = this.escolherAlvo();
    const v = this.alvo;
    if (!v) {
      this.body.setVelocityX(0);
      this.feixe.setVisible(false);
      return;
    }
    const dx = v.x - this.x;
    if (!this.puxando) {
      this.body.setVelocityX(Phaser.Math.Clamp(dx * 2, -50, 50));
      if (Math.abs(dx) < 3) {
        this.puxando = true;
        v.abduzido = true;
        v.vivo = false; // as balas passam pela vítima e acertam o disco
        v.body.allowGravity = false;
        v.body.setVelocity(0, -PUXADA);
        if (v.texture.key === 'bode') v.setFrame(BODE.abduzido);
        this.grito.setText(v.texture.key === 'bode' ? 'BÉÉÉÉ!' : 'SOCORRO!').setPosition(v.x, v.y - 40).setVisible(true).setAlpha(1);
        this.scene.tweens.add({ targets: this.grito, alpha: 0, delay: 900, duration: 300 });
      }
    } else {
      this.body.setVelocityX(0);
      v.body.setVelocity(0, -PUXADA);
      v.x = this.x;
      if (v.y < this.y + 22) {
        // Abduzido: some dentro do disco e volta ao chão depois (campo de treino).
        this.puxando = false;
        v.setVisible(false);
        v.body.enable = false;
        if (v.esconder && !this.scene.tudoVolta) v.esconder();
        if (!this.scene.tudoVolta) {
          this.alvo = null;
          return;
        }
        this.scene.time.delayedCall(6000, () => {
          v.abduzido = false;
          v.body.allowGravity = true;
          if (v.reiniciar) v.reiniciar();
          v.setVisible(true);
          v.body.enable = true;
          v.body.reset(v.inicioX, v.inicioY - 30);
        });
        this.alvo = null;
      }
    }
    // Raio do disco até o chão.
    this.feixe.setVisible(this.puxando).setPosition(this.x, this.y + 22);
    this.feixe.setCrop(0, 0, FEIXE.largura, Math.max(0, 192 - (this.y + 22)));
    // Lampião dentro do raio sobe junto.
    const j = this.scene.jogador;
    const dentro = this.puxando && !j.morto && Math.abs(j.x - this.x) < MEIO_RAIO && j.pe > this.y + 24;
    this.noRaio = dentro ? (this.noRaio || 0) + dt : 0;
    if (this.noRaio > DEMORA_PUXAR) {
      j.corpo.body.setVelocityY(Math.max(j.corpo.body.velocity.y - dt * 1.2, -50));
    }
  }
}

export class Bode extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, x, y) {
    super(cena, x, y, 'bode', BODE.parado);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.setOrigin(BODE.peX / BODE.largura, BODE.peY / BODE.altura).setDepth(8);
    this.body.setSize(22, 14).setOffset(BODE.peX - 11, BODE.peY - 14);
    this.inicioX = x;
    this.inicioY = y;
    this.reiniciar();
  }

  reiniciar() {
    this.estado = 'andando';
    this.abduzido = false;
    this.direcao = 1;
    this.proximaVolta = 0;
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (this.abduzido) return;
    // Pasta para lá e para cá, mastigando.
    if (t > this.proximaVolta) {
      this.direcao = Math.abs(this.x - this.inicioX) > 40 ? Math.sign(this.inicioX - this.x) : (Math.random() < 0.5 ? -1 : 1);
      this.proximaVolta = t + Phaser.Math.Between(1200, 2600);
    }
    const anda = Math.floor(t / 900) % 3 !== 0;
    this.body.setVelocityX(anda ? this.direcao * 14 : 0);
    this.setFlipX(this.direcao < 0);
    this.setFrame(anda ? BODE.parado : (Math.floor(t / 200) % 2 ? BODE.mastiga : BODE.parado));
  }
}
