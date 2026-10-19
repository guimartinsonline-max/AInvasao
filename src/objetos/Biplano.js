import { hex, P } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { AVIAO } from '../quadros.js';
import { som } from '../som.js';

// Subchefe da fase 1: biplano da Aviação Militar, "O GAVIÃO".
// Parado no campo de pouso com o rabo no chão. Quando a onda começa, o motor
// engasga umas vezes até pegar e o avião taxia acelerando (a hélice mata quem
// encostar, o rabo levanta com a velocidade). Se o Lampião não derrubar antes,
// ele decola, some e volta em passadas: alto soltando bombas e, de vez em
// quando, num rasante com o artilheiro varrendo o chão. O artilheiro do banco
// de trás é uma parte à parte: morto, o avião para de atirar.

const Q = AVIAO.biplano;
const VIDA = 135; // mais duro (pedido do Guilherme)
const VIDA_ARTILHEIRO = 19;
const RABO = 0.24; // rad: inclinação parado no chão, com a bequilha apoiada
const ACEL = 75; // px/s² taxiando (decola rápido: ninguém vence ele parado no chão)
const VEL_DECOLA = 125;
const VEL_VOO = 105;
const VEL_RASANTE = 150;
// Pontos do desenho (virado para a direita) medidos a partir da roda no chão.
const NARIZ = [22, -31];
const CABINE = [-46, -38];
const BARRIGA = [-8, -24];
const ESCAPE = [-4, -23];

class Artilheiro extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, aviao) {
    super(cena, 0, 0, 'artilheiro', 0);
    this.aviao = aviao;
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.setOrigin(0.5, 22 / 24).setDepth(9);
    this.voa = true;
    this.body.allowGravity = false;
    this.body.setSize(12, 16).setOffset(8, 4);
    this.vivo = true;
  }

  levarDano(dano, origemX, forte, morte) {
    this.aviao.danoArtilheiro(dano, morte);
  }
}

export class Biplano extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, x, pe) {
    super(cena, x, pe, 'biplano', 0);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.setDepth(8);
    this.voa = true;
    this.body.allowGravity = false;
    this.vivo = true;
    this.vida = VIDA;
    this.vidaMax = VIDA;
    this.etapa = 0;
    this.helice = 0;
    this.chao = pe;
    this.vx = 0;
    this.vy = 0;
    this.estado = 'pousado';
    this.passadas = 0;
    this.furioso = false;
    this.virar(1);
    this.setRotation(-RABO);
    this.artilheiro = new Artilheiro(cena, this);
    cena.alvos.add(this.artilheiro);
    this.artilheiro.body.allowGravity = false;
    this.artVida = VIDA_ARTILHEIRO;
    this.proximoTiro = 0;
    this.proximoMotor = 0;
    this.proximaFumaca = 0;
    this.texto = cena.add.text(0, 0, '', estiloTexto(hex('branco'))).setOrigin(0.5).setDepth(30).setVisible(false);
    this.mostrar();
    this.seguirArtilheiro();
  }

  virar(d) {
    this.direcao = d;
    this.setFlipX(d < 0);
    const ox = d > 0 ? Q.rodaX : Q.largura - Q.rodaX;
    this.setOrigin(ox / Q.largura, 1);
    // Corpo de acerto: fuselagem e asas (a cauda baixa no chão fica de fora).
    this.body.setSize(104, 40).setOffset(d > 0 ? 10 : Q.largura - 114, 10);
  }

  // Ponto do desenho (dx para a frente, dy para cima negativo) no mundo, com a inclinação.
  ponto(dx, dy) {
    const x = dx * this.direcao;
    const c = Math.cos(this.rotation);
    const s = Math.sin(this.rotation);
    return [this.x + x * c - dy * s, this.y + x * s + dy * c];
  }

  mostrar() {
    this.setFrame(this.etapa * Q.n + this.helice);
  }

  falar(texto, ms = 900, cor = 'branco') {
    const [x, y] = this.ponto(0, -64);
    this.texto.setText(texto).setColor(hex(cor)).setPosition(x, y).setVisible(true).setAlpha(1);
    this.scene.tweens.killTweensOf(this.texto);
    this.scene.tweens.add({ targets: this.texto, alpha: 0, y: y - 12, delay: ms, duration: 300 });
  }

  // A onda começou: dá a partida (o motor engasga antes de pegar).
  partir() {
    if (!this.vivo || this.estado !== 'pousado') return;
    const cena = this.scene;
    this.estado = 'partida';
    const ef = cena.efeitos;
    const tossir = (k, fala) => cena.time.delayedCall(150 + k * 350, () => {
      if (this.estado !== 'partida') return;
      som('engasgo');
      this.helice = (this.helice % 3) + 1;
      this.mostrar();
      const [nx, ny] = this.ponto(NARIZ[0] - 4, NARIZ[1]);
      for (let i = 0; i < 3; i++) {
        const f = ef.animar('fumaca', nx - this.direcao * i * 5, ny + i, { anim: 'fumaca_lenta', escala: 1.2 });
        f.setTint(0x3a3634);
      }
      this.falar(fala, 500);
      cena.time.delayedCall(140, () => { if (this.estado === 'partida') { this.helice = 0; this.mostrar(); } });
    });
    tossir(0, 'PÓ!');
    tossir(1, 'PÓ-PÓ!');
    tossir(2, 'PUF...');
    cena.time.delayedCall(1250, () => {
      if (this.estado !== 'partida') return;
      this.estado = 'taxi';
      this.falar('VRUUUM!', 900, 'amarelo_fogo');
      cena.efeitos.tremer(0.004, 300);
      if (this.artVida > 0) cena.time.delayedCall(500, () => this.artilheiro.vivo && this.artilheiro.setFrame(0));
    });
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (!this.body.enable) return;
    const s = dt / 1000;
    if (this.estado === 'taxi') this.taxiar(t, s);
    else if (this.estado === 'decolando') this.decolar(t, s);
    else if (this.estado === 'voo') this.voar(t, s);
    else if (this.estado === 'fora') this.esperarFora(t);
    else if (this.estado === 'caindo') this.cair(t, s);
    if (this.vivo && ['taxi', 'decolando', 'voo'].includes(this.estado)) {
      // Hélice girando e o ronco do motor.
      this.helice = 1 + (Math.floor(t / 40) % 3);
      this.mostrar();
      if (t > this.proximoMotor) {
        this.proximoMotor = t + 150;
        som('motor', this.estado === 'taxi' ? 0.6 + this.vx / 300 : 1);
      }
      this.fumegar(t);
      this.atirarArtilheiro(t);
      this.atropelar();
    }
    this.body.updateFromGameObject?.();
    this.seguirArtilheiro();
  }

  taxiar(t, s) {
    const cena = this.scene;
    this.vx = Math.min(VEL_DECOLA, this.vx + ACEL * s);
    this.x += this.direcao * this.vx * s;
    // O rabo levanta conforme pega velocidade.
    const k = Phaser.Math.Clamp((this.vx - 40) / 60, 0, 1);
    this.setRotation(-this.direcao * RABO * (1 - k));
    if (t > this.proximaFumaca) {
      this.proximaFumaca = t + 90;
      const [rx, ry] = this.ponto(-4, 0);
      cena.efeitos.poeira(rx, ry, 2);
      // Vento da hélice levantando poeira atrás.
      const [px, py] = this.ponto(-60, -2);
      if (Math.random() < 0.6) cena.efeitos.poeiraPasso(px, this.chao, this.direcao > 0);
      const [ex, ey] = this.ponto(ESCAPE[0], ESCAPE[1]);
      cena.efeitos.fumaca(ex - this.direcao * 6, ey);
      void py;
    }
    // Esmaga caixote e barril no caminho.
    const frente = this.x + this.direcao * 26;
    for (const c of cena.caixotes.vivos()) {
      if (Math.abs(c.x - frente) < 18 && Math.abs(c.y - this.y) < 30) c.levarDano(99);
    }
    const v = cena.cameras.main.worldView;
    if (this.vx >= VEL_DECOLA || (this.direcao > 0 ? this.x > v.right - 30 : this.x < v.x + 30)) {
      this.estado = 'decolando';
      this.vy = 0;
      this.falar('ELE VAI FUGIR!', 1200, 'amarelo_fogo');
    }
  }

  decolar(t, s) {
    this.vx = Math.min(VEL_DECOLA + 40, this.vx + ACEL * 2 * s);
    this.vy = Math.max(-95, this.vy - 140 * s);
    this.x += this.direcao * this.vx * s;
    this.y += this.vy * s;
    this.setRotation(Phaser.Math.Linear(this.rotation, -this.direcao * 0.28, 0.06));
    const v = this.scene.cameras.main.worldView;
    if (this.y < v.y - 40 || this.x > v.right + 120 || this.x < v.x - 120) {
      this.sairDaTela(1300);
      this.scene.mostrar?.('ELE VOLTA!', 'CUIDADO COM AS BOMBAS', 1500);
    }
  }

  sairDaTela(ms) {
    this.estado = 'fora';
    this.setVisible(false);
    this.artilheiro.setVisible(false);
    this.voltaEm = this.scene.time.now + ms;
  }

  esperarFora(t) {
    if (t < this.voltaEm) return;
    // Nova passada pelo lado oposto: alta soltando bombas ou, a cada três, rasante.
    const v = this.scene.cameras.main.worldView;
    this.passadas++;
    // Fúria: com menos de 40% da vida ele fica mais rápido, bombardeia mais e dá rasante
    // a cada duas passadas.
    const furia = this.vida < this.vidaMax * 0.4;
    if (furia && !this.furioso) {
      this.furioso = true;
      this.scene.mostrar?.('O GAVIÃO ENFURECEU!', '', 1300);
    }
    this.rasante = this.passadas % (furia ? 2 : 3) === 0;
    this.virar(this.passadas % 2 === 1 ? -1 : 1);
    this.x = this.direcao > 0 ? v.x - 90 : v.right + 90;
    this.altura = this.rasante ? 112 : Phaser.Math.Between(18, 46);
    this.y = this.altura;
    this.vx = (this.rasante ? VEL_RASANTE : VEL_VOO) * (furia ? 1.25 : 1);
    this.bombas = this.rasante ? 0 : furia ? 7 : 5;
    this.rajadasNariz = this.rasante ? (furia ? 3 : 2) : 0;
    this.proximoNariz = 0;
    this.proximaBomba = 0;
    this.estado = 'voo';
    this.setRotation(0).setVisible(true);
    if (this.artVida > 0) this.artilheiro.setVisible(true);
    if (this.rasante) {
      som('mergulho');
      this.scene.mostrar?.('RASANTE!', '', 900);
    }
  }

  voar(t, s) {
    const cena = this.scene;
    const j = cena.jogador;
    this.x += this.direcao * this.vx * s;
    // Balanço do voo; no rasante, mergulha e arremete no fim.
    const v = cena.cameras.main.worldView;
    const prog = Phaser.Math.Clamp((this.x - v.x) / v.width, 0, 1);
    const p = this.direcao > 0 ? prog : 1 - prog;
    if (this.rasante) {
      this.y = this.altura + Math.sin(p * Math.PI) * 12 - (p > 0.75 ? (p - 0.75) * 200 : 0);
      this.setRotation(this.direcao * (p < 0.4 ? 0.12 : p > 0.75 ? -0.22 : 0));
    } else {
      this.y = this.altura + Math.sin(t / 300) * 3;
      this.setRotation(Math.sin(t / 420) * 0.04);
    }
    if (this.bombas > 0 && Math.abs(this.x + this.direcao * 30 - j.x) < 120 && t > this.proximaBomba) {
      this.bombas--;
      // Fileira de bombas com espaço entre elas: dá para passar no vão, mas não parado.
      this.proximaBomba = t + (this.furioso ? 270 : 320);
      const [bx, by] = this.ponto(BARRIGA[0], BARRIGA[1]);
      cena.balasInimigas.soltarBomba(bx, by, this.direcao * this.vx * 0.55);
    }
    // Rasante: a metralhadora do nariz solta rajadas mirando onde o Lampião estava
    // (pisca antes; correndo ou pulando dá para escapar).
    if (this.rajadasNariz > 0 && t > this.proximoNariz && p > 0.12 && p < 0.7 && !j.morto) {
      this.rajadasNariz--;
      this.proximoNariz = t + 700;
      const [nx, ny] = this.ponto(NARIZ[0] + 6, NARIZ[1] + 6);
      cena.efeitos.faisca(nx, ny, 4);
      const ang = Math.atan2(j.pe - 18 - ny, j.x - nx);
      cena.time.delayedCall(220, () => {
        for (let k = 0; k < (this.furioso ? 5 : 4); k++) {
          cena.time.delayedCall(k * 90, () => {
            if (!this.vivo || this.estado !== 'voo') return;
            const [bx, by] = this.ponto(NARIZ[0] + 6, NARIZ[1] + 6);
            const a = ang + Phaser.Math.FloatBetween(-0.05, 0.05);
            cena.balasInimigas.dispararAngulo(bx, by, a);
            cena.efeitos.disparo(bx, by, a, 'normal');
            som('tiro_inimigo');
          });
        }
      });
    }
    if (this.direcao > 0 ? this.x > v.right + 110 : this.x < v.x - 110) this.sairDaTela(this.rasante ? 900 : this.furioso ? 1000 : 1400);
  }

  // A hélice e as rodas matam quem encosta; no ar, só no rasante dá para trombar.
  atropelar() {
    const j = this.scene.jogador;
    if (j.morto || j.invulneravel) return;
    const [nx, ny] = this.ponto(NARIZ[0], NARIZ[1]);
    const naHelice = Math.abs(j.x - nx) < 10 && j.pe > ny - 18 && j.pe - 36 < ny + 18;
    const b = this.body;
    const noCorpo = j.x > b.x + 6 && j.x < b.right - 6 && j.pe > b.y + 8 && j.pe - 30 < b.bottom - 4;
    if ((this.estado === 'taxi' && (naHelice || (noCorpo && this.vx > 30))) || (this.estado === 'voo' && noCorpo)) {
      j.morrer(this.direcao * 220);
    }
  }

  // Artilheiro do banco de trás: rajadas de 3 só para trás (e para baixo no rasante).
  atirarArtilheiro(t) {
    if (this.artVida <= 0 || t < this.proximoTiro) return;
    const cena = this.scene;
    const j = cena.jogador;
    if (j.morto) return;
    const a = this.artilheiro;
    const mx = a.x - this.direcao * 13;
    const my = a.y - 8;
    const dx = j.x - mx;
    const dy = j.pe - 20 - my;
    if (dx * this.direcao > -10) {
      a.setFrame(0);
      return; // o Lampião está na frente: o artilheiro não alcança
    }
    const desce = Math.atan2(dy, Math.abs(dx));
    if (desce < -0.15 || desce > 1.2) return;
    this.proximoTiro = t + (this.furioso ? Phaser.Math.Between(800, 1200) : Phaser.Math.Between(1100, 1600));
    const ang = this.direcao > 0 ? Math.PI - desce : desce;
    for (let k = 0; k < (this.furioso ? 5 : 4); k++) {
      cena.time.delayedCall(k * 120, () => {
        if (this.artVida <= 0 || !this.vivo) return;
        a.setFrame(2);
        cena.time.delayedCall(70, () => this.artVida > 0 && a.setFrame(desce > 0.35 ? 1 : 0));
        const bx = a.x - this.direcao * 13;
        const by = a.y - 8;
        cena.balasInimigas.dispararAngulo(bx, by, ang + Phaser.Math.FloatBetween(-0.04, 0.04));
        cena.efeitos.disparo(bx, by, ang, 'normal');
        cena.efeitos.capsula(a.x, a.y - 6, this.direcao);
      });
    }
  }

  seguirArtilheiro() {
    const a = this.artilheiro;
    const [x, y] = this.ponto(CABINE[0], CABINE[1] + 1);
    a.setPosition(Math.round(x), Math.round(y)).setFlipX(this.direcao < 0).setRotation(this.rotation);
    a.body.updateFromGameObject?.();
  }

  danoArtilheiro(dano, morte) {
    if (this.artVida <= 0 || !this.vivo || this.estado === 'pousado') return;
    const cena = this.scene;
    const a = this.artilheiro;
    this.artVida -= morte === 'facada' ? 99 : dano;
    a.setTint(P.branco).setTintMode(Phaser.TintModes.FILL);
    cena.time.delayedCall(50, () => a.clearTint());
    cena.efeitos.sangue(a.x, a.y - 8, 5);
    if (this.artVida <= 0) {
      a.vivo = false;
      a.setFrame(3);
      cena.pontuar(500, a.x, a.y - 20);
      cena.efeitos.sangue(a.x, a.y - 8, 16);
      this.falar('ACERTARAM O ARTILHEIRO!', 1100);
    }
  }

  levarDano(dano, origemX, forte = false, morte = null) {
    if (!this.vivo) return;
    const cena = this.scene;
    if (this.estado === 'pousado') {
      // Antes da partida (durante a faixa do subchefe) a lataria só solta faísca.
      const [fx, fy] = this.ponto(Phaser.Math.Between(-60, 20), Phaser.Math.Between(-44, -16));
      cena.efeitos.faisca(fx, fy, 2);
      return;
    }
    if (morte === 'facada') dano = 5;
    this.vida -= dano;
    const [fx, fy] = this.ponto(Phaser.Math.Between(-60, 20), Phaser.Math.Between(-44, -16));
    cena.efeitos.faisca(fx, fy, 3);
    const etapa = Math.min(3, Math.floor((1 - Math.max(0, this.vida) / this.vidaMax) * 4));
    if (etapa > this.etapa) {
      this.etapa = etapa;
      // Lona rasgando: estilhaços de madeira e pano, estalo.
      cena.efeitos.explosao(fx, fy, 0.6);
      cena.efeitos.tabuas(fx, fy);
      this.mostrar();
    }
    this.setTint(0xffffff).setTintMode(Phaser.TintModes.FILL);
    cena.time.delayedCall(45, () => this.vivo && this.clearTint());
    if (this.vida <= 0) this.destruir();
  }

  // Etapa 2 solta fumaça preta; etapa 3 pega fogo no motor.
  fumegar(t) {
    if (this.etapa < 2 || t < (this.proximoDano || 0)) return;
    this.proximoDano = t + (this.etapa === 3 ? 80 : 160);
    const ef = this.scene.efeitos;
    const [x, y] = this.ponto(NARIZ[0] - 14, NARIZ[1] + Phaser.Math.Between(-6, 6));
    const f = ef.animar('fumaca', x, y, { anim: 'fumaca_lenta', escala: 1 });
    f.setTint(0x3a3634);
    if (this.etapa === 3 && Math.random() < 0.7) ef.chama(x, y);
  }

  destruir() {
    const cena = this.scene;
    this.vivo = false;
    this.clearTint();
    cena.pontuar(5000, this.x, this.y - 70);
    if (this.artVida > 0) {
      this.artVida = 0;
      this.artilheiro.vivo = false;
      this.artilheiro.setFrame(3);
    }
    this.artilheiro.body.enable = false;
    if (this.estado === 'voo' || this.estado === 'decolando') {
      // Abatido no ar: entra em parafuso soltando fogo e cai dentro da tela.
      this.estado = 'caindo';
      this.vy = 20;
      const v = cena.cameras.main.worldView;
      this.alvoQueda = Phaser.Math.Clamp(this.x + this.direcao * 140, v.x + 90, v.right - 90);
      cena.mostrar?.('ABATIDO!', '', 1400);
      cena.efeitos.explosao(this.x, this.y - 30, 1.2);
      return;
    }
    // Destruído no chão antes de decolar: bônus.
    this.estado = 'destruido';
    cena.pontuar(3000, this.x, this.y - 90);
    cena.mostrar?.('NEM DECOLOU!', 'BÔNUS 3000', 1600);
    this.explodirCarcaca();
  }

  cair(t, s) {
    const ef = this.scene.efeitos;
    this.vy = Math.min(260, this.vy + 260 * s);
    this.x += (this.alvoQueda - this.x) * Math.min(1, 1.6 * s);
    this.y += this.vy * s;
    this.setRotation(this.rotation + this.direcao * 2.2 * s);
    this.helice = 1 + (Math.floor(t / 70) % 3);
    this.mostrar();
    if (t > (this.proximoDano || 0)) {
      this.proximoDano = t + 50;
      const [x, y] = this.ponto(NARIZ[0] - 10, NARIZ[1]);
      ef.chama(x, y);
      const f = ef.animar('fumaca', x, y, { anim: 'fumaca_lenta', escala: 1.4 });
      f.setTint(0x2e2a28);
    }
    this.seguirArtilheiro();
    if (this.y >= this.chao) {
      // Bateu no chão: o mesmo avião vira a carcaça ali mesmo (sem sumir e reaparecer).
      this.y = this.chao;
      this.estado = 'destruido';
      this.virarCarcaca();
      this.explodirCarcaca();
    }
  }

  // Explosões em cadeia pela fuselagem e a carcaça queimando no chão.
  // Troca na hora para o quadro destroçado, acertando a inclinação num tranco curto
  // com quique (a explosão do impacto cobre a troca).
  virarCarcaca() {
    const cena = this.scene;
    this.setFrame(Q.destruido);
    this.artilheiro.setVisible(false);
    cena.tweens.killTweensOf(this);
    cena.tweens.add({ targets: this, rotation: 0, duration: 160, ease: 'Quad.easeOut' });
    cena.tweens.add({ targets: this, y: this.chao - 6, duration: 110, yoyo: true, ease: 'Quad.easeOut' });
    cena.explodir(this.x, this.y - 20, 40, 4, 1.6);
    cena.efeitos.poeira(this.x, this.chao, 16);
  }

  explodirCarcaca() {
    const cena = this.scene;
    if (this.estado !== 'destruido' || this.frame.name !== Q.destruido) this.setRotation(0);
    for (let k = 0; k < 6; k++) {
      cena.time.delayedCall(k * 130, () => {
        const [x, y] = this.ponto(Phaser.Math.Between(-80, 20), Phaser.Math.Between(-40, -10));
        cena.explodir(x, y, 34, 4, k === 5 ? 1.8 : 1.1);
      });
    }
    cena.time.delayedCall(700, () => {
      this.setFrame(Q.destruido).setRotation(0);
      this.artilheiro.setVisible(false);
      cena.efeitos.estilhacos(this.x - 30, this.y - 30, 10, 100, this.y);
      cena.efeitos.tremer(0.02, 500);
      cena.efeitos.tabuas(this.x, this.y - 30);
      this.queimando = cena.time.addEvent({
        delay: 150, loop: true, callback: () => {
          const [x, y] = this.ponto(Phaser.Math.Between(-80, 20), Phaser.Math.Between(-30, -8));
          cena.efeitos.chama(x, y);
          if (Math.random() < 0.5) cena.efeitos.fumacaSobe(x, y - 10);
        },
      });
      cena.time.delayedCall(10000, () => {
        this.queimando.remove();
        cena.time.addEvent({ delay: 700, repeat: 24, callback: () => {
          const [x, y] = this.ponto(Phaser.Math.Between(-60, 10), -16);
          cena.efeitos.fumacaSobe(x, y);
        } });
      });
    });
  }
}
