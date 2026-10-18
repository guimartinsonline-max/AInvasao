import { P, hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { INIMIGOS } from '../quadros.js';

// Comportamento por tipo. Distâncias em pixels, tempos em ms.
const ESCUDO = 6; // tiros que o escudo aguenta
// Pontos por inimigo (como no Metal Slug, aparecem subindo quando ele cai).
const PONTOS = { volante: 100, granadeiro: 150, facao: 150, rojao: 200, metralhador: 300, xeremita: 200 };
const VE_DE = 130; // px: distância em que o soldado distraído percebe o Lampião
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
  // Joga banana de dinamite em arco, que explode no chão.
  granadeiro: {
    vida: 2, velocidade: 28, alcance: 210, distancia: 110, recarga: [1700, 2600], acao: 'dinamite',
    gritos: ['VALEI-ME!', 'AI, PAVIO!', 'MÃEZINHA!'], panico: 36,
  },
  // Gordo e resistente: rajada de 4 balas.
  metralhador: {
    vida: 5, velocidade: 18, alcance: 240, distancia: 150, recarga: [2100, 2900], bala: 'volante', rajada: 4,
    gritos: ['OXE!', 'ARRE!', 'AI, MEU BUCHO!'], panico: 0,
  },
  // Lança-rojão: atira de longe um rojão em arco que explode no chão.
  rojao: {
    vida: 2, velocidade: 22, alcance: 280, distancia: 170, recarga: [2600, 3400], acao: 'rojao',
    gritos: ['MEU ROJÃO!', 'VIXE!', 'AAAI!'], panico: 30,
  },
  // Corre para cima do Lampião com o facão erguido e golpeia de perto.
  facao: {
    vida: 2, velocidade: 82, alcance: 300, distancia: 0, recarga: [700, 1000], acao: 'golpe', alcanceGolpe: 24,
    gritos: ['ARRE ÉGUA!', 'AAAI!', 'MEU FACÃO!'], panico: 0,
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
    this.comecaDistraido = !!opcoes.distraido && !!this.q.sentado;
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
    this.distraido = this.comecaDistraido;
    this.proximoZ = 0;
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

  // Distraído e cochilando até perceber o Lampião (ou levar um tiro): pula de susto.
  acordar() {
    if (!this.distraido) return;
    const cena = this.scene;
    this.distraido = false;
    this.estado = 'susto';
    this.fimEstado = cena.time.now + 550;
    this.setFrame(this.q.panico);
    this.body.setVelocityY(-170);
    this.virar(cena.jogador.x > this.x ? 1 : -1);
    this.grito.setText('!?').setPosition(this.x, this.y - 54).setVisible(true).setAlpha(1).setScale(1.5);
    cena.tweens.killTweensOf(this.grito);
    cena.tweens.add({ targets: this.grito, alpha: 0, scale: 1, delay: 450, duration: 250 });
    this.proximoTiro = cena.time.now + 700;
  }

  levarDano(dano, origemX, forte = false, morte = null, queima = false) {
    if (!this.vivo) return;
    const ef = this.scene.efeitos;
    if (this.distraido) this.acordar();
    if (this.tipo !== 'xeremita') ef.sangue(this.x, this.y - 22, 6);
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
    this.distraido = false;
    if (this.estado === 'escalando') this.body.allowGravity = true;
    this.estado = 'morto';
    cena.pontuar(PONTOS[this.tipo] || 100, this.x, this.y - 50);
    // Sangue nas mortes (menos queimado e derretido); o xeremita espirra gosma.
    if (morte !== 'fogo' && morte !== 'derrete') {
      if (this.tipo === 'xeremita') ef.gosma(this.x, this.y - 22, 14);
      else ef.sangue(this.x, this.y - 22, morte === 'facada' ? 34 : 22);
    }
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
    if (morte === 'facada') {
      // Facada: grita, recua cambaleando e cai no lugar.
      this.setFrame(this.q.morte);
      this.body.setVelocity(lado * 40, -90);
      this.gritar();
      cena.time.delayedCall(700, () => {
        cena.tweens.add({ targets: this, alpha: 0, duration: 120, yoyo: true, repeat: 2,
          onComplete: () => { this.setVisible(false); this.body.enable = false; this.setAlpha(1); } });
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
    if (this.estado === 'escalando' || this.estado === 'pulando') {
      this.atravessar(t, dt);
      return;
    }
    if (this.queimaAte > t) {
      this.correrQueimando(t, dt);
      return;
    }
    if (this.distraido) {
      this.body.setVelocityX(0);
      this.setFrame(this.q.sentado[Math.floor(t / 700) % 2]);
      if (t > this.proximoZ) {
        this.proximoZ = t + 1400;
        this.grito.setText('Zz').setPosition(this.x + this.direcao * 8, this.y - 34).setVisible(true).setAlpha(0.8).setScale(1);
        cena.tweens.killTweensOf(this.grito);
        cena.tweens.add({ targets: this.grito, y: this.y - 50, alpha: 0, duration: 1200 });
      }
      const jj = cena.jogador;
      if (!jj.morto && Math.abs(jj.x - this.x) < VE_DE && Math.abs(jj.pe - this.y) < 50) this.acordar();
      return;
    }
    if (this.estado === 'susto') {
      if (t < this.fimEstado) return;
      this.estado = 'andando';
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
    const anda = foraDaTela || (dist > cfg.distancia && dist < cfg.alcance * 1.4 && !j.morto);
    const vel = cfg.velocidade * (this.vidaEscudo > 0 ? 0.6 : 1) * (foraDaTela ? 1.5 : 1);
    if (anda && this.abrirCaminho(vel, j, foraDaTela)) {
      this.body.setVelocityX(this.direcao * vel);
      this.passo += dt;
      this.setFrame(q.andar[Math.floor(this.passo / 150) % q.andar.length]);
    } else if (this.estado === 'escalando' || this.estado === 'pulando') {
      return;
    } else {
      this.body.setVelocityX(0);
      this.setFrame(q.parado);
    }
    const alcanceAtaque = cfg.acao === 'golpe' ? cfg.alcanceGolpe : cfg.alcance;
    const naAltura = cfg.acao !== 'golpe' || Math.abs(j.pe - this.y) < 30;
    if (!foraDaTela && dist < alcanceAtaque && naAltura && !j.morto && t > this.proximoTiro
      && this.body.blocked.down) {
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

  // ------------------------------------------------------------ andar pelo cenário
  // Antes de dar o passo, vê o que tem na frente: obstáculo baixo ele pula, alto
  // (caixote empilhado, lajedo, sacos de areia) ele escala; na beirada, desce se o
  // Lampião estiver lá embaixo. Devolve true se pode simplesmente andar.
  abrirCaminho(vel, j, foraDaTela) {
    if (!this.body.blocked.down) return true;
    this.fimPulo = this.scene.time.now + 2500; // segurança: nunca fica preso no meio do pulo
    const altura = this.obstaculoAFrente();
    if (altura > 0) {
      if (altura <= 26) {
        // Pula por cima.
        this.estado = 'pulando';
        this.velPulo = Math.max(vel, 40) * 1.2;
        this.body.setVelocity(0, -Math.sqrt(2 * this.scene.physics.world.gravity.y * (altura + 12)));
        this.setFrame(this.q.andar[1]);
        return false;
      }
      if (altura <= 74) {
        // Escala: agarra na borda e sobe.
        this.estado = 'escalando';
        this.topoEscalada = this.y - altura;
        this.body.allowGravity = false;
        this.body.setVelocity(0, 0);
        return false;
      }
      return false; // alto demais: espera ali e atira
    }
    if (!this.temChaoAFrente()) {
      // Beirada: desce num pulinho se o Lampião estiver mais embaixo (ou se está entrando na tela).
      if (foraDaTela || j.pe > this.y + 10) {
        this.estado = 'pulando';
        this.velPulo = Math.max(vel, 40) * 1.3;
        this.body.setVelocity(this.velPulo * this.direcao, -130);
        this.setFrame(this.q.andar[1]);
      }
      return false;
    }
    return true;
  }

  // Altura (px) do sólido logo à frente dos pés, ou 0 se o caminho está livre.
  obstaculoAFrente() {
    const fisica = this.scene.physics;
    const x = this.x + this.direcao * (this.q.corpoL / 2 + 3);
    if (!fisica.overlapRect(x - 1, this.y - 26, 2, 22, false, true).length) return 0;
    let yy = this.y - 4;
    while (yy > this.y - 90 && fisica.overlapRect(x - 1, yy - 1, 2, 1, false, true).length) yy--;
    return this.y - yy;
  }

  // Pulando ou escalando: continua até pousar ou passar da borda de cima.
  atravessar(t, dt) {
    const q = this.q;
    if (t > this.fimPulo) {
      this.body.allowGravity = true;
      this.estado = 'andando';
      return;
    }
    if (this.estado === 'escalando') {
      // Mãos para cima, subindo agarrado na borda.
      this.setFrame(Math.floor(t / 120) % 2 ? q.panico : q.andar[0]);
      this.body.setVelocity(this.direcao * 6, -75);
      if (this.y <= this.topoEscalada + 1) {
        this.body.allowGravity = true;
        this.body.setVelocity(this.direcao * 45, -110);
        this.velPulo = 45;
        this.estado = 'pulando';
        this.scene.efeitos.poeira(this.x + this.direcao * 6, this.topoEscalada, 4);
      }
      return;
    }
    // Pulando: segue no ar até pousar.
    if (this.body.blocked.down && this.body.velocity.y >= 0) {
      this.estado = 'andando';
      this.scene.efeitos.poeira(this.x, this.y, 4);
    } else {
      // Segue empurrando para a frente: encostado na parede sobe reto e passa por cima ao alcançar o topo.
      this.body.setVelocityX(this.direcao * (this.velPulo || 40));
    }
  }

  // Não anda para fora da beirada de uma plataforma.
  temChaoAFrente() {
    const x = this.x + this.direcao * 10;
    return this.scene.physics.overlapRect(x - 1, this.y + 1, 2, 4, false, true).length > 0;
  }

  atirar(t) {
    const q = this.q;
    const cfg = this.cfg;
    const cena = this.scene;
    const j = cena.jogador;
    this.estado = 'atirando';
    this.fimEstado = t + (cfg.rajada ? 120 * cfg.rajada : 350);
    this.proximoTiro = t + Phaser.Math.Between(...cfg.recarga);
    this.setFrame(q.atira);
    const x = this.x + this.direcao * q.cano[0];
    const y = this.y - q.cano[1];
    if (cfg.acao === 'dinamite') {
      cena.balasInimigas.lancarDinamite(x, y, this.direcao, Math.abs(j.x - this.x));
      return;
    }
    if (cfg.acao === 'rojao') {
      cena.balasInimigas.lancarRojao(x, y, this.direcao, Math.abs(j.x - this.x));
      cena.efeitos.fumaca(this.x - this.direcao * 14, y);
      return;
    }
    if (cfg.acao === 'golpe') {
      // Facãozada: acerta se o Lampião estiver colado na frente.
      cena.efeitos.tremer(0.003, 60);
      if (!j.morto && !j.invulneravel && (j.x - this.x) * this.direcao > -6 && Math.abs(j.x - this.x) < cfg.alcanceGolpe + 6
        && Math.abs(j.pe - this.y) < 24) j.morrer(this.direcao * 200);
      return;
    }
    const tiro = (k) => {
      if (!this.vivo) return;
      const yy = y + (k % 2 ? 1 : 0);
      cena.balasInimigas.disparar(x, yy, this.direcao, cfg.bala, j.x, j.pe - 20);
      if (cfg.rajada) cena.efeitos.disparo(x, yy, this.direcao > 0 ? 0 : Math.PI, 'normal');
    };
    tiro(0);
    for (let k = 1; k < (cfg.rajada || 1); k++) cena.time.delayedCall(k * 110, () => tiro(k));
  }
}
