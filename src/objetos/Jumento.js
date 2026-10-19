import { hex, P } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { LAMPIAO } from '../quadros.js';
import { som } from '../som.js';

// Jumento blindado: o "tanque" do Lampião, como o Metal Slug do Metal Slug.
// Parado esperando com a placa SUBA!; o Lampião monta pulando em cima (ou
// apertando para baixo encostado). Montado: anda, pula, a metralhadora gira
// para onde o Lampião mira (frente, diagonal, cima e, no ar, para baixo) e o
// botão de granada dispara o canhão (bombas contadas no painel). A blindagem
// aguenta alguns tiros; quando estoura, o Lampião é jogado para cima e o
// jumento foge zurrando. Para descer: baixo + pulo. Baixo + granada: o Lampião
// salta e o jumento dispara contra os inimigos e explode (como o Slug Attack).

export const JUMENTO = { largura: 72, altura: 60, peX: 36, peY: 59, sela: 34 };
const BLINDAGEM = 6;
const BOMBAS = 10;
const VEL = 88;
const PULO = -290;
const CADENCIA = 75; // ms entre balas da metralhadora
const GIRO = Math.PI * 1.8; // rad/s da metralhadora girando
const CORPO = { l: 40, a: 46 };
const KAMI_VEL = 230; // px/s do jumento kamikaze
const KAMI_TEMPO = 1700; // ms até explodir sozinho

export class Jumento {
  constructor(cena, x, pe) {
    this.cena = cena;
    this.inicio = { x, pe };
    this.s = cena.add.sprite(x, pe, 'jumento', 0).setDepth(9)
      .setOrigin(JUMENTO.peX / JUMENTO.largura, JUMENTO.peY / JUMENTO.altura);
    this.mg = cena.add.image(x, pe, 'metralha_jumento').setOrigin(0.15, 0.5).setDepth(11);
    this.placa = cena.add.text(x, pe - 74, 'SUBA!', estiloTexto(hex('amarelo_fogo'))).setOrigin(0.5).setDepth(30);
    this.direcao = 1;
    this.ang = 0; // 0 = frente, -PI/2 = cima, PI/2 = baixo (no espaço "virado para a direita")
    this.livre = true; // parado esperando alguém montar
    this.fugindo = false;
    this.blindagem = BLINDAGEM;
    this.bombas = BOMBAS;
    this.desdeTiro = 0;
    this.passo = 0;
    this.pousar();
  }

  get montado() {
    return !this.livre && !this.fugindo;
  }

  // Parado no chão, esperando.
  pousar() {
    this.s.setFrame(0).setFlipX(this.direcao < 0);
    this.posicionarMg();
  }

  // Chamado pela cena a cada quadro.
  atualizar(t, dt) {
    if (this.kami) {
      this.correrKamikaze(t, dt);
      return;
    }
    if (this.fugindo) {
      this.fugir(t, dt);
      return;
    }
    if (!this.livre) return;
    this.placa.setVisible(Math.floor(t / 300) % 2 === 0).setPosition(this.s.x, this.s.y - 74);
    const j = this.cena.jogador;
    if (j.morto || j.montaria) return;
    const perto = Math.abs(j.x - this.s.x) < 22;
    const caindoEmCima = j.corpo.body.velocity.y > 0 && j.pe > this.s.y - 44 && j.pe < this.s.y - 20;
    if (perto && (caindoEmCima || this.cena.controles.estado.baixo)) this.montar(j);
  }

  montar(j) {
    const cena = this.cena;
    this.livre = false;
    this.placa.setVisible(false);
    this.j = j;
    j.montaria = this;
    j.agachado = false;
    j.arremesso = 0;
    j.facada = 0;
    // O corpo de colisão vira o do jumento, com o pé no mesmo lugar.
    const b = j.corpo.body;
    const fundo = b.bottom;
    b.setSize(CORPO.l, CORPO.a);
    j.corpo.x = this.s.x;
    j.corpo.y = fundo - CORPO.a / 2;
    b.reset(this.s.x, fundo - CORPO.a / 2);
    this.direcao = j.direcao;
    cena.events.emit('arma', 'JUMENTO BLINDADO!');
    if (!cena.dicaKamikaze) {
      cena.dicaKamikaze = true;
      cena.time.delayedCall(1600, () => cena.events.emit('dica', 'BAIXO + GRANADA: JUMENTO KAMIKAZE'));
    }
    som('zurro');
    cena.efeitos.poeira(this.s.x, this.s.y, 10);
  }

  // Lampião desce (ou é jogado longe quando a blindagem estoura).
  desmontar(jogado = false) {
    const j = this.j;
    if (!j) return;
    const b = j.corpo.body;
    const fundo = b.bottom;
    b.setSize(14, 36);
    j.corpo.y = fundo - 18;
    b.reset(j.corpo.x, fundo - 18);
    b.setVelocity(jogado ? -this.direcao * 60 : 0, jogado ? -330 : -200);
    j.visual.setCrop();
    j.montaria = null;
    j.invulneravel = true;
    this.cena.time.delayedCall(700, () => { if (!j.morto) j.invulneravel = false; });
    this.j = null;
    if (!jogado) {
      // Fica parado ali esperando de novo.
      this.livre = true;
      this.pousar();
    }
  }

  controlar(dt, c) {
    const j = this.j;
    const cena = this.cena;
    const b = j.corpo.body;
    // Segurança: atravessou o chão num tranco de quadro? volta para cima.
    if (j.pe > 240) {
      b.reset(j.corpo.x, cena.chaoAbaixo(j.x, -60) - 30);
      b.setVelocity(0, 0);
    }
    // Nunca afunda: se o pé afundou uns poucos pixels no chão, volta para cima dele.
    // Só corrige afundada pequena; plataforma ou caixote mais alto na frente não é
    // chão (antes ele "teletransportava" para cima de toldo, sacos e caixotes).
    const chao = cena.chaoAbaixo(j.x, j.pe - 8);
    if (j.pe > chao + 2 && j.pe - chao <= 8 && b.velocity.y >= 0) {
      j.corpo.y -= j.pe - chao;
      b.setVelocityY(0);
      b.updateFromGameObject?.();
    }
    const noChao = b.blocked.down || b.touching.down || Math.abs(chao - j.pe) < 3;
    this.noAr = noChao ? 0 : (this.noAr || 0) + dt;
    // Descer: baixo + pulo.
    if (c.estado.baixo && c.apertou('pular') && noChao) {
      this.desmontar();
      return;
    }
    // Kamikaze: baixo + granada.
    if (c.estado.baixo && c.apertou('granada') && noChao) {
      this.kamikaze();
      return;
    }
    if (c.eixoX !== 0) this.direcao = c.eixoX;
    j.direcao = this.direcao;
    b.setVelocityX(c.eixoX * VEL);
    if (c.apertou('pular') && noChao) {
      b.setVelocityY(PULO);
      cena.efeitos.poeira(j.x, j.pe, 8);
    }
    if (noChao && !this.estavaNoChao) cena.efeitos.poeira(j.x, j.pe, 6);
    this.estavaNoChao = noChao;

    // Mira: frente, diagonal, cima; no ar, para baixo. A metralhadora gira até lá.
    let alvo = 0;
    if (c.estado.cima) alvo = c.eixoX !== 0 ? -Math.PI / 4 : -Math.PI / 2;
    // Para baixo só no ar de verdade (pulando alto), nunca andando no chão.
    else if (c.estado.baixo && this.noAr > 150 && chao - j.pe > 14) alvo = Math.PI / 2;
    const passo = GIRO * dt / 1000;
    this.ang += Phaser.Math.Clamp(alvo - this.ang, -passo, passo);

    // Metralhadora: segurou, atira sem parar.
    this.desdeTiro += dt;
    if (c.estado.atirar && this.desdeTiro >= CADENCIA) {
      this.desdeTiro = 0;
      const a = this.direcao > 0 ? this.ang : Math.PI - this.ang;
      const [bx, by] = this.boca();
      const espalha = Phaser.Math.FloatBetween(-0.05, 0.05);
      cena.balas.disparar(bx, by, a + espalha, 'pesada', 1);
      som('metralha_jumento');
      cena.efeitos.disparo(bx, by, a, 'normal');
      cena.efeitos.capsula(this.mg.x, this.mg.y, -this.direcao);
      this.recuo = 40;
    }
    // Canhão: o botão de granada dispara uma bomba (rojão) para a frente.
    j.desdeGranada += dt;
    if (c.apertou('granada') && this.bombas > 0 && j.desdeGranada > 350) {
      j.desdeGranada = 0;
      this.bombas--;
      const x = j.x + this.direcao * 30;
      const y = j.pe - 30;
      cena.balas.disparar(x, y, this.direcao > 0 ? -0.08 : Math.PI + 0.08, 'rojao', 1.3);
      som('canhao');
      cena.efeitos.disparo(x, y, this.direcao > 0 ? 0 : Math.PI, 'grande');
      cena.efeitos.fumaca(x - this.direcao * 6, y);
      cena.efeitos.tremer(0.004, 80);
    }
    this.animar(dt, noChao, c.eixoX !== 0);
  }

  // Boca da metralhadora no mundo.
  boca() {
    const a = this.direcao > 0 ? this.ang : Math.PI - this.ang;
    return [this.mg.x + Math.cos(a) * 27, this.mg.y + Math.sin(a) * 27];
  }

  posicionarMg() {
    const d = this.direcao;
    // Arma baixa no ombro do jumento (como a do camelo): o tiro sai na altura dos soldados.
    const sobe = this.s.frame && (this.s.frame.name === 1 || this.s.frame.name === 3) ? 1 : this.s.frame && this.s.frame.name === 5 ? 3 : 0;
    this.mg.setPosition(Math.round(this.s.x + d * 17), Math.round(this.s.y - 26 - sobe));
    this.mg.setFlipY(d < 0).setRotation(d > 0 ? this.ang : Math.PI - this.ang);
  }

  animar(dt, noChao, andando) {
    const j = this.j;
    const s = this.s;
    const recuo = (this.recuo = (this.recuo || 0) - dt) > 0 ? -this.direcao : 0;
    s.setPosition(Math.round(j.x + recuo), Math.round(j.pe)).setFlipX(this.direcao < 0);
    if (!noChao) s.setFrame(5);
    else if (andando) {
      this.passo += dt;
      s.setFrame(1 + (Math.floor(this.passo / 110) % 4));
    } else s.setFrame(0);
    // Lampião sentado na sela: só o tronco aparece (as pernas ficam atrás do jumento).
    const v = j.visual;
    if (v.texture.key !== 'lampiao') v.setTexture('lampiao');
    v.setFrame(LAMPIAO.parado).setFlipX(this.direcao < 0);
    v.setOrigin((this.direcao > 0 ? LAMPIAO.peX : LAMPIAO.largura - LAMPIAO.peX) / LAMPIAO.largura, LAMPIAO.peY / LAMPIAO.altura);
    v.setCrop(0, 0, LAMPIAO.largura, LAMPIAO.peY - 11); // só da cintura para cima
    const sobe = s.frame.name === 1 || s.frame.name === 3 ? 1 : 0;
    v.setPosition(Math.round(s.x - this.direcao * 5), Math.round(s.y - 23 - sobe)).setVisible(!j.invulneravel || Math.floor(this.cena.time.now / 70) % 2 === 0);
    this.posicionarMg();
  }

  // Tiro, facão ou explosão no Lampião montado: a blindagem segura.
  levarDano() {
    const cena = this.cena;
    if (this.j && this.j.invulneravel) return;
    this.blindagem--;
    this.s.setTint(P.branco).setTintMode(Phaser.TintModes.FILL);
    cena.time.delayedCall(60, () => this.s.clearTint());
    cena.efeitos.faisca(this.s.x, this.s.y - 30, 8);
    cena.efeitos.tremer(0.006, 100);
    if (this.j) {
      // Pisca um instante para não tomar uma rajada inteira de uma vez.
      this.j.invulneravel = true;
      cena.time.delayedCall(450, () => { if (this.j) this.j.invulneravel = false; });
    }
    if (this.blindagem <= 0) this.estourar();
  }

  // Blindagem estoura: chapas voam, o Lampião é jogado para cima e o jumento foge zurrando.
  estourar() {
    const cena = this.cena;
    const { x, y } = this.s;
    cena.efeitos.explosao(x, y - 28, 1.2);
    cena.efeitos.tabuas(x, y - 30);
    cena.efeitos.faisca(x, y - 30, 16);
    this.desmontar(true);
    this.fugindo = true;
    this.livre = false;
    this.mg.setVisible(false);
    this.direcao = -this.direcao;
    this.passo = 0;
    this.vyFuga = -220; // pulo de susto; depois cai e corre pelo chão
    som('zurro');
    this.texto = cena.add.text(x, y - 70, 'IÓÓÓ!', estiloTexto(hex('branco'))).setOrigin(0.5).setDepth(30);
    cena.tweens.add({ targets: this.texto, alpha: 0, y: y - 90, delay: 600, duration: 500 });
  }

  // O Lampião salta para trás e o jumento dispara para a frente com o pavio aceso.
  kamikaze() {
    const cena = this.cena;
    const j = this.j;
    const dir = this.direcao;
    this.desmontar(true);
    j.corpo.body.setVelocity(-dir * 90, -340);
    this.livre = false;
    this.kami = true;
    this.kamiFim = cena.time.now + KAMI_TEMPO;
    this.passo = 0;
    this.placa.setVisible(false);
    som('zurro');
    this.texto = cena.add.text(this.s.x, this.s.y - 70, 'IÓÓÓ!!', estiloTexto(hex('amarelo_fogo'))).setOrigin(0.5).setDepth(30);
    cena.tweens.add({ targets: this.texto, alpha: 0, y: this.s.y - 92, delay: 500, duration: 500 });
    cena.efeitos.poeira(this.s.x, this.s.y, 12);
    cena.events.emit('arma', 'JUMENTO KAMIKAZE');
  }

  correrKamikaze(t, dt) {
    const cena = this.cena;
    const s = this.s;
    this.passo += dt;
    s.x += this.direcao * KAMI_VEL * dt / 1000;
    // Segue o chão: desce de beirada, sobe só degrau pequeno (nada de pular para cima de plataforma).
    const chao = cena.chaoAbaixo(s.x, s.y - 8);
    s.y += Phaser.Math.Clamp(chao - 1 - s.y, -3, 6);
    s.setFlipX(this.direcao < 0).setFrame(6 + (Math.floor(this.passo / 70) % 2));
    this.posicionarMg();
    // Pavio aceso na sela soltando faísca e poeira atrás das patas.
    if (Math.floor(this.passo / 50) % 2 === 0) cena.efeitos.faisca(s.x - this.direcao * 6, s.y - 46, 2);
    if (Math.floor(this.passo / 90) % 2 === 0) cena.efeitos.poeira(s.x - this.direcao * 18, s.y, 2);
    const frente = s.x + this.direcao * 28;
    const alvos = [...cena.alvos.getChildren(), ...(cena.trens || [])];
    const bateu = alvos.some((a) => a.vivo && !a.temporario && !a.segredo && a.levarDano && Math.abs((a.x ?? 0) - frente) < 26 && Math.abs((a.y ?? s.y) - s.y) < 50)
      || cena.caixotes.vivos().some((c) => Math.abs(c.x - frente) < 16 && Math.abs(c.y - s.y) < 30)
      || cena.physics.overlapRect(frente - 1, s.y - 40, 2, 26, false, true).length > 0;
    const v = cena.cameras.main.worldView;
    if (bateu || t > this.kamiFim || s.x < v.x - 20 || s.x > v.right + 20) this.explodirKamikaze();
  }

  explodirKamikaze() {
    const cena = this.cena;
    const { x, y } = this.s;
    this.kami = false;
    this.s.setVisible(false);
    this.mg.setVisible(false);
    // Explosão grande em cadeia: o jumento leva tudo junto.
    cena.explodir(x, y - 24, 72, 30, 2);
    cena.time.delayedCall(120, () => cena.explodir(x - 22, y - 14, 40, 10, 1.2));
    cena.time.delayedCall(220, () => cena.explodir(x + 22, y - 30, 40, 10, 1.2));
    cena.efeitos.tabuas(x, y - 30);
    cena.efeitos.tremer(0.02, 450);
    cena.efeitos.fumacaFica(x, y - 30, 2.2);
    if (cena.tudoVolta) {
      cena.time.delayedCall(8000, () => {
        this.blindagem = BLINDAGEM;
        this.bombas = BOMBAS;
        this.direcao = 1;
        this.ang = 0;
        this.livre = true;
        this.s.setPosition(this.inicio.x, this.inicio.pe).setVisible(true);
        this.mg.setVisible(true);
        this.pousar();
      });
    }
  }

  fugir(t, dt) {
    const s = this.s;
    const seg = dt / 1000;
    this.passo += dt;
    s.x += this.direcao * 160 * seg;
    // Gravidade de verdade: se estourou no ar, cai até o chão antes de correr (nada de
    // galopar no vento); no chão, acompanha o terreno (desce beirada, sobe degrau pequeno).
    const chao = this.cena.chaoAbaixo(s.x, s.y - 8) - 1;
    this.vyFuga = Math.min((this.vyFuga || 0) + 900 * seg, 500);
    const noAr = s.y < chao - 1 || this.vyFuga < 0;
    if (noAr) {
      s.y = Math.min(s.y + this.vyFuga * seg, chao);
      if (s.y >= chao && this.vyFuga > 0) {
        this.vyFuga = 0;
        this.cena.efeitos.poeira(s.x, s.y, 6);
      }
    } else {
      this.vyFuga = 0;
      s.y += Phaser.Math.Clamp(chao - s.y, -3, 6);
    }
    // No ar, patas encolhidas (quadro de pulo); no chão, galope desesperado.
    s.setFlipX(this.direcao < 0).setFrame(noAr ? 5 : 6 + (Math.floor(this.passo / 90) % 2));
    const v = this.cena.cameras.main.worldView;
    if (s.x < v.x - 60 || s.x > v.right + 60) {
      s.setVisible(false);
      this.fugindo = false;
      if (this.cena.tudoVolta) {
        // Campo de treino: volta blindado depois de um tempo.
        this.cena.time.delayedCall(8000, () => {
          this.blindagem = BLINDAGEM;
          this.bombas = BOMBAS;
          this.direcao = 1;
          this.ang = 0;
          this.livre = true;
          s.setPosition(this.inicio.x, this.inicio.pe).setVisible(true);
          this.mg.setVisible(true);
          this.pousar();
        });
      }
    }
  }
}
