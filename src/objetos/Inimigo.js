import { P, hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { INIMIGOS } from '../quadros.js';

// Comportamento por tipo. Distâncias em pixels, tempos em ms.
const ESCUDO = 6; // tiros que o escudo aguenta
const QUEIMA = 2200; // ms pegando fogo
const DANO_QUEIMA = 0.5; // dano a cada QUEIMA_TICK ms
const QUEIMA_TICK = 450;

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
  // opcoes.escudo: soldado da Volante com escudo de tábuas, que segura os tiros de frente.
  constructor(cena, x, y, tipo, opcoes = {}) {
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
    this.temEscudo = !!opcoes.escudo;
    if (this.temEscudo) this.escudo = cena.add.image(x, y, 'escudo', 0).setOrigin(0.5, 1).setDepth(10);
    this.reiniciar();
  }

  // Tiro vindo pela frente acerta o escudo e não o soldado.
  bloqueia(vx) {
    return this.vidaEscudo > 0 && Math.sign(vx) === -this.direcao;
  }

  danoEscudo(dano, x, y) {
    const cena = this.scene;
    this.vidaEscudo -= dano;
    this.escudo.setTint(P.branco).setTintMode(Phaser.TintModes.FILL);
    cena.time.delayedCall(50, () => this.escudo.clearTint());
    cena.efeitos.impacto(x, y, 'comum');
    cena.efeitos.lascas(x, y);
    if (this.vidaEscudo <= ESCUDO / 2) this.escudo.setFrame(1);
    if (this.vidaEscudo <= 0) {
      this.escudo.setVisible(false);
      cena.efeitos.tabuas(this.escudo.x, this.escudo.y - 13);
      this.grito.setText('MEU ESCUDO!').setPosition(this.x, this.y - 54).setVisible(true).setAlpha(1);
      cena.tweens.killTweensOf(this.grito);
      cena.tweens.add({ targets: this.grito, alpha: 0, delay: 700, duration: 300 });
    }
  }

  reiniciar() {
    this.vivo = true;
    this.vida = this.cfg.vida;
    this.direcao = -1;
    this.estado = 'andando';
    this.proximoTiro = 0;
    this.fimEstado = 0;
    this.passo = 0;
    this.queimaAte = 0;
    this.proximaQueima = 0;
    this.vidaEscudo = this.temEscudo ? ESCUDO : 0;
    if (this.escudo) this.escudo.setVisible(true).setFrame(0).clearTint();
    this.proximaChama = 0;
    this.setRotation(0).setVisible(true).clearTint().setAlpha(1);
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

  // Candeeiro: sai correndo apavorado, pegando fogo, e perde vida aos poucos.
  queimar() {
    const agora = this.scene.time.now;
    if (this.queimaAte < agora) {
      this.proximaQueima = agora + QUEIMA_TICK;
      this.grito.setText(this.tipo === 'xeremita' ? 'IIIIH!' : 'TÔ QUEIMANDO!').setPosition(this.x, this.y - 54)
        .setVisible(true).setAlpha(1);
      this.scene.tweens.killTweensOf(this.grito);
      this.scene.tweens.add({ targets: this.grito, alpha: 0, delay: 700, duration: 300 });
    }
    this.queimaAte = agora + QUEIMA;
  }

  levarDano(dano, origemX, forte = false, morte = null, queima = false) {
    if (!this.vivo) return;
    const ef = this.scene.efeitos;
    if (queima) this.queimar();
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
    this.queimaAte = 0;
    if (this.escudo && this.vidaEscudo > 0) {
      // O escudo cai no chão quando o soldado morre.
      this.vidaEscudo = 0;
      this.escudo.setVisible(false);
      ef.tabuas(this.escudo.x, this.escudo.y - 13);
    }
    if (morte === 'fogo') {
      // Vira carvão, fica parado um instante e desmancha em cinza.
      this.setFrame(this.q.tostado);
      this.body.setVelocity(0, 0);
      this.body.checkCollision.none = true;
      this.body.allowGravity = false;
      ef.parar(50);
      cena.time.delayedCall(550, () => {
        ef.fumaca(this.x, this.y - 30);
        ef.fumaca(this.x - 4, this.y - 18);
        ef.cinzas(this.x, this.y - 20);
        this.setVisible(false);
        this.body.enable = false;
        this.body.allowGravity = true;
      });
      cena.time.delayedCall(2600, () => this.renascer());
      return;
    }
    if (morte === 'costas') {
      // Papo-amarelo: o tiro derruba de costas, deslizando no chão.
      this.setFrame(this.q.morte);
      this.body.setVelocity(lado * 90, -140).setDragX(260);
      cena.tweens.add({ targets: this, rotation: -lado * Math.PI / 2 * (this.flipX ? -1 : 1), duration: 260 });
      ef.parar(80);
      ef.tremer(0.006, 140);
      this.gritar();
      cena.time.delayedCall(900, () => {
        cena.tweens.add({ targets: this, alpha: 0, duration: 200, yoyo: true, repeat: 2,
          onComplete: () => { this.setVisible(false); this.body.enable = false; } });
      });
      cena.time.delayedCall(2600, () => this.renascer());
      return;
    }
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
    // Chumbo do bacamarte arremessa longe; explosão manda alto girando.
    const longe = morte === 'arremessa';
    this.setFrame(this.q.morte);
    this.body.checkCollision.none = true;
    this.body.setVelocity(lado * (longe ? 240 : forte ? 150 : 80), longe ? -200 : forte ? -320 : -220);
    this.body.setAngularVelocity(lado * (forte || longe ? 900 : 500));
    ef.parar(forte ? 90 : 60);
    ef.tremer(0.006, 140);
    this.gritar();

    cena.time.delayedCall(420, () => {
      if (this.tipo === 'xeremita') ef.gosma(this.x, this.y - 16, 36);
      else ef.poeira(this.x, this.y, 10);
      ef.faisca(this.x, this.y - 16, 6);
      this.setVisible(false);
      this.body.enable = false;
    });
    cena.time.delayedCall(2600, () => this.renascer());
  }

  gritar() {
    this.grito.setText(Phaser.Utils.Array.GetRandom(this.cfg.gritos)).setPosition(this.x, this.y - 54)
      .setVisible(true).setAlpha(1);
    this.scene.tweens.killTweensOf(this.grito);
    this.scene.tweens.add({ targets: this.grito, y: this.y - 70, alpha: 0, duration: 800, onComplete: () => this.grito.setVisible(false) });
  }

  renascer() {
    // Numa fase quem morre não volta: sai da cena de vez.
    if (!this.scene.tudoVolta) {
      this.setVisible(false);
      this.body.enable = false;
      this.grito.setVisible(false);
      if (this.escudo) this.escudo.setVisible(false);
      this.fora = true;
      return;
    }
    this.reiniciar();
    this.body.enable = true;
    this.body.checkCollision.none = false;
    this.body.setAngularVelocity(0).setDragX(0);
    this.body.reset(this.inicioX, this.inicioY - 140);
    this.caindo = true;
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (this.escudo && this.escudo.visible) {
      // O escudo vai na frente do corpo, na altura da barriga.
      this.escudo.setPosition(Math.round(this.x + this.direcao * 9), Math.round(this.y)).setFlipX(this.direcao < 0);
    }
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
    if (this.queimaAte > t) {
      this.correrQueimando(t, dt);
      return;
    }
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
    // Fora da tela, entra andando (até pulando de uma pedra) antes de parar ou atirar.
    const v = cena.cameras.main.worldView;
    const foraDaTela = this.x < v.x + 14 || this.x > v.right - 14;
    if (foraDaTela && !j.morto) this.virar(this.x < v.x + 14 ? 1 : -1);
    const anda = foraDaTela || (dist > cfg.distancia && dist < cfg.alcance * 1.4 && !j.morto && this.temChaoAFrente());
    if (anda) {
      this.body.setVelocityX(this.direcao * cfg.velocidade * (this.vidaEscudo > 0 ? 0.6 : 1) * (foraDaTela ? 1.5 : 1));
      this.passo += dt;
      this.setFrame(q.andar[Math.floor(this.passo / 150) % q.andar.length]);
    } else {
      this.body.setVelocityX(0);
      this.setFrame(q.parado);
    }
    if (!foraDaTela && dist < cfg.alcance && !j.morto && t > this.proximoTiro && this.body.blocked.down) {
      this.atirar(t);
    }
  }

  // Pegando fogo: corre para lá e para cá agitando os braços, soltando chamas.
  correrQueimando(t, dt) {
    const cena = this.scene;
    if (t > this.proximaChama) {
      cena.efeitos.chama(this.x + Phaser.Math.Between(-5, 5), this.y - Phaser.Math.Between(18, 36));
      this.proximaChama = t + 110;
    }
    if (Math.floor(t / 700) % 2 === 0 !== this.direcao > 0) this.virar(-this.direcao);
    this.body.setVelocityX(this.temChaoAFrente() ? this.direcao * this.cfg.velocidade * 2.4 : 0);
    this.setFrame(Math.floor(t / 120) % 2 ? this.q.panico : this.q.andar[0]);
    if (t > this.proximaQueima) {
      this.proximaQueima = t + QUEIMA_TICK;
      this.vida -= DANO_QUEIMA;
      this.setTint(P.laranja_fogo).setTintMode(Phaser.TintModes.FILL);
      cena.time.delayedCall(50, () => this.vivo && this.clearTint());
      if (this.vida <= 0) this.morrer(this.direcao, false, 'fogo');
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
