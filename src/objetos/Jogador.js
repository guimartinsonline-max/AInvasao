import { LAMPIAO, LAMPIAO_GORDO, COMIDAS } from '../quadros.js';
import { BOCAS } from '../maos.js';
import { ARMAS } from '../armas.js';

// Lampião. A física usa um corpo invisível; o sprite visível só acompanha,
// para poder esticar e amassar sem mexer na colisão.

const VEL_CORRER = 100;
const VEL_AGACHADO = 36;
const VEL_PULO = -310;
const CORTE_PULO = -110; // soltar o botão no meio do pulo corta a subida
const TOLERANCIA_BEIRADA = 100; // ms para ainda pular depois de sair da beirada
const MEMORIA_PULO = 110; // ms que um pulo apertado antes de tocar o chão fica guardado
const ALCANCE_PEIXEIRA = 26;
const ALTURA_EM_PE = 36;
const ALTURA_AGACHADO = 28;
const GRANADAS = 10;
export const VIDAS = 3;
const INVULNERAVEL = 2000; // ms piscando depois de renascer
const MORTE = 1900; // ms da animação de morte até renascer
const ENGORDA = 6; // comidas seguidas para ficar gordo
const DIGERE = 9000; // ms para a barriga baixar uma comida
const TEMPO_GORDO = 25000; // ms gordo até emagrecer

export class Jogador {
  constructor(cena, x, y) {
    this.cena = cena;
    this.corpo = cena.physics.add.image(x, y, 'px').setVisible(false);
    this.corpo.body.setSize(14, ALTURA_EM_PE).setMaxVelocityY(420);
    this.visual = cena.add.sprite(x, y, 'lampiao', LAMPIAO.parado).setDepth(10);
    // Poça de sangue debaixo do corpo quando ele morre.
    this.poca = cena.add.image(0, 0, 'poca').setOrigin(0.5, 0.5).setDepth(7).setVisible(false);
    this.chapeu = cena.add.image(0, 0, 'chapeu').setOrigin(0.5, 1).setDepth(11).setVisible(false);


    this.direcao = 1;
    this.beirada = 0;
    this.memoriaPulo = 0;
    this.desdeTiro = 1000;
    this.noChao = false;
    this.passo = 0;
    this.recuo = 0;
    this.miraCima = false;
    this.morto = false;
    this.invulneravel = false;
    this.vidas = VIDAS;
    this.arma = 'padrao';
    this.nivel = 1;
    this.municao = Infinity;
    this.granadas = GRANADAS;
    this.desdeGranada = 1000;
  }

  get x() { return this.corpo.body.center.x; }
  get pe() { return this.corpo.body.bottom; }

  atualizar(dt, c) {
    const corpo = this.corpo.body;
    if (this.morto) {
      // Morte como no Metal Slug: voa para trás de braços para cima, cai estatelado,
      // a perna treme duas vezes e ele pisca antes de renascer.
      this.desdeMorte += dt;
      const v = this.visual;
      if (corpo.blocked.down && this.desdeMorte > 150 && corpo.velocity.y >= 0) {
        corpo.setVelocityX(corpo.velocity.x * 0.8);
        if (!this.bateu) {
          // Bate de costas no chão e dá um quique curto.
          this.bateu = true;
          corpo.setVelocityY(-75);
          this.cena.efeitos.poeira(this.x, this.pe, 10);
          this.cena.efeitos.tremer(0.005, 90);
        } else if (!this.caiuEm) {
          this.caiuEm = this.desdeMorte;
          this.cena.efeitos.poeira(this.x, this.pe, 5);
        }
      }
      this.voarChapeu(dt);
      // No ar: voando para trás. No chão: deitado morto, parado, com a poça crescendo.
      const quadro = this.bateu ? 'morte2' : 'morte1';
      if (this.caiuEm && !this.poca.visible) {
        this.poca.setPosition(Math.round(this.x), Math.round(this.pe) - 1).setVisible(true).setScale(0.2, 0.5);
        this.cena.tweens.add({ targets: this.poca, scaleX: 1, scaleY: 1, duration: 700, ease: 'Quad.easeOut' });
        this.cena.efeitos.sangue(this.x, this.pe - 6, 10);
      }
      if (v.texture.key.endsWith('_gordo')) v.setTexture(v.texture.key.slice(0, -6));
      v.setFrame(LAMPIAO[quadro]);
      // Cai de costas: a cabeça vai para o lado de onde ele voou.
      const d = this.direcaoMorte;
      v.setFlipX(d < 0);
      // Deitado, o corpo fica centrado onde ele caiu (a poça vai embaixo do meio do corpo).
      const ox = this.bateu ? LAMPIAO.largura / 2 : (d > 0 ? LAMPIAO.peX : LAMPIAO.largura - LAMPIAO.peX);
      v.setOrigin(ox / LAMPIAO.largura, LAMPIAO.peY / LAMPIAO.altura);
      if (this.desdeMorte > MORTE - 450) v.setVisible(Math.floor(this.desdeMorte / 60) % 2 === 0);
      v.setPosition(Math.round(this.x), Math.round(this.pe));
      return;
    }
    if (this.invulneravel) this.visual.setVisible(Math.floor(this.cena.time.now / 70) % 2 === 0);
    if (this.montaria) {
      // Montado no jumento blindado: ele cuida do movimento, da mira e dos tiros.
      this.montaria.controlar(dt, c);
      return;
    }
    const estavaNoChao = this.noChao;
    this.noChao = corpo.blocked.down;

    if (this.noChao) {
      this.beirada = TOLERANCIA_BEIRADA;
      if (!estavaNoChao) this.aterrissar();
    } else {
      this.beirada -= dt;
    }

    this.memoriaPulo = c.apertou('pular') ? MEMORIA_PULO : this.memoriaPulo - dt;

    // Agachar.
    const querAgachar = this.noChao && c.estado.baixo;
    if (querAgachar !== this.agachado) {
      this.agachado = querAgachar;
      this.ajustarAltura(this.agachado ? ALTURA_AGACHADO : ALTURA_EM_PE);
    }

    // Correr.
    if (c.eixoX !== 0) this.direcao = c.eixoX;
    // Gordo anda mais devagar.
    corpo.setVelocityX(c.eixoX * (this.agachado ? VEL_AGACHADO : VEL_CORRER) * (this.gordo ? 0.7 : 1));

    // Pular, com tolerância de beirada e memória do botão.
    if (this.memoriaPulo > 0 && this.beirada > 0) {
      this.memoriaPulo = 0;
      this.beirada = 0;
      if (this.agachado) {
        this.agachado = false;
        this.ajustarAltura(ALTURA_EM_PE);
      }
      corpo.setVelocityY(VEL_PULO * (this.gordo ? 0.86 : 1));
      this.cena.efeitos.poeira(this.x, this.pe, 6);
      this.esticar(0.75, 1.3);
    }
    if (!c.estado.pular && corpo.velocity.y < CORTE_PULO) corpo.setVelocityY(CORTE_PULO);

    // Atirar.
    this.desdeTiro += dt;
    const apertou = c.apertou('atirar');
    const arma = ARMAS[this.arma];
    // Semiautomática (pistola): só atira ao apertar, um tiro por toque.
    const segurando = !arma.semi && c.estado.atirar && this.desdeTiro >= arma.cadencia;
    if ((apertou && this.desdeTiro >= arma.toque) || segurando) {
      this.desdeTiro = 0;
      this.atirar(c);
    }

    // Granada.
    this.desdeGranada += dt;
    // Campo de treino: repõe as granadas depois de um tempo sem nenhuma.
    if (this.cena.tudoVolta && this.granadas === 0 && this.desdeGranada > 3000) this.granadas = GRANADAS;
    if (c.apertou('granada') && this.granadas > 0 && this.desdeGranada > 300) {
      this.desdeGranada = 0;
      this.granadas--;
      // Quadro de arremesso: o braço de trás sobe e a granada sai da mão lá em cima.
      this.arremesso = 220;
      const [gx, gy] = LAMPIAO.maoGranada;
      this.cena.lancarGranada(this.x + this.direcao * gx, this.pe - gy, this.direcao, corpo.velocity.x);
    }

    // Digestão: a barriga baixa com o tempo; gordo, emagrece depois de um tempo sem comer.
    const agora = this.cena.time.now;
    if (this.barriga > 0 && agora > this.digereEm) {
      this.barriga--;
      this.digereEm = agora + DIGERE;
    }
    if (this.gordo && agora > this.gordoAte) this.emagrecer();
    this.miraCima = c.estado.cima && !this.agachado;
    this.miraBaixo = !this.noChao && c.estado.baixo && !this.miraCima;
    // Ângulo da varredura (0 = frente, 1 = cima): gira em ~150 ms.
    const alvoVarre = this.miraCima ? 1 : 0;
    this.angVarre = Phaser.Math.Clamp((this.angVarre || 0) + Math.sign(alvoVarre - (this.angVarre || 0)) * dt / 150, 0, 1);
    if (this.arma !== 'madsen') this.angVarre = alvoVarre;
    this.animar(dt);
  }

  // Pegar a mesma arma de novo deixa ela grande (mais forte, tiro maior) e soma a munição.
  trocarArma(nome) {
    if (nome !== 'padrao' && nome === this.arma) {
      this.nivel = 2;
      this.municao += ARMAS[nome].municao;
      return true;
    }
    this.arma = nome;
    this.nivel = 1;
    this.municao = ARMAS[nome].municao;
    return false;
  }

  get forca() {
    // Arma SUPER ou Lampião gordo: tiro maior e mais forte.
    return this.nivel === 2 || this.gordo ? 1.5 : 1;
  }

  // Um tiro mata, como no Metal Slug: careta de susto, voa para trás e renasce piscando.
  morrer(vxBala = 0) {
    if (this.montaria && !this.morto) {
      // Montado: quem leva o tiro é a blindagem do jumento.
      this.montaria.levarDano();
      return;
    }
    if (this.morto || this.invulneravel) return;
    const cena = this.cena;
    this.morto = true;
    cena.mortes = (cena.mortes || 0) + 1;
    this.vidas--;
    const lado = Math.sign(vxBala) || -this.direcao;
    this.corpo.body.setVelocity(lado * 90, -240);
    // Sangue espirrando do tiro.
    cena.efeitos.sangue(this.x, this.pe - 24, 28);
    this.desdeMorte = 0;
    this.caiuEm = 0;
    this.emagrecer(true);
    this.bateu = false;
    // O chapéu voa da cabeça girando e cai do lado.
    this.chapeu.setPosition(this.x, this.pe - 44).setVisible(true).setAlpha(1).setRotation(0);
    this.chapeuVel = { x: lado * Phaser.Math.Between(40, 70), y: -260, giro: lado * 9 };
    // Voa para trás: vira de frente para quem atirou (a cabeça cai do lado de lá).
    this.direcaoMorte = -lado;
    cena.efeitos.parar(120);
    cena.efeitos.tremer(0.01, 220);
    cena.efeitos.faisca(this.x, this.pe - 24, 10);
    cena.time.delayedCall(MORTE, () => this.renascer());
  }

  // Comeu: pontos no lugar e a barriga enche; muitas seguidas e ele engorda.
  comer(nome, item) {
    const cena = this.cena;
    cena.pontuar(COMIDAS[nome] || 100, item.x, item.y - 16);
    cena.efeitos.faisca(item.x, item.y - 8, 6);
    this.barriga = (this.barriga || 0) + 1;
    this.digereEm = cena.time.now + DIGERE;
    if (!this.gordo && this.barriga >= ENGORDA) {
      this.gordo = true;
      this.gordoAte = cena.time.now + TEMPO_GORDO;
      cena.events.emit('arma', 'GORDO!');
      cena.efeitos.poeira(this.x, this.pe, 12);
      cena.efeitos.tremer(0.004, 120);
    } else if (this.gordo) {
      this.gordoAte = cena.time.now + TEMPO_GORDO; // comer mais segura a barriga
    }
  }

  emagrecer(semAviso = false) {
    if (this.gordo && !semAviso) {
      this.cena.events.emit('arma', 'EMAGRECEU');
      this.cena.efeitos.poeira(this.x, this.pe, 8);
    }
    this.gordo = false;
    this.barriga = 0;
  }

  // Chapéu solto: sobe girando, cai e assenta no chão (fica lá até ele renascer).
  voarChapeu(dt) {
    const v = this.chapeuVel;
    if (!v || !this.chapeu.visible) return;
    const s = dt / 1000;
    const c = this.chapeu;
    v.y = Math.min(v.y + 900 * s, 400);
    const chao = this.cena.chaoAbaixo(c.x, c.y - 4);
    if (c.y + v.y * s >= chao) {
      // Assentou: de boca para cima, como caiu.
      c.y = chao;
      c.setRotation(Math.PI);
      c.setOrigin(0.5, 0);
      this.chapeuVel = null;
      this.cena.efeitos.poeira(c.x, chao, 3);
      return;
    }
    c.x += v.x * s;
    c.y += v.y * s;
    c.rotation += v.giro * s;
  }

  // Depois do "continuar?": vidas cheias e volta ao jogo.
  continuar() {
    this.vidas = VIDAS;
    this.renascer();
  }

  renascer() {
    const corpo = this.corpo.body;
    this.chapeu.setVisible(false).setOrigin(0.5, 1);
    // A poça seca e some devagar depois que ele renasce.
    this.cena.tweens.killTweensOf(this.poca);
    if (this.poca.visible) {
      this.cena.tweens.add({ targets: this.poca, alpha: 0, delay: 800, duration: 600,
        onComplete: () => this.poca.setVisible(false).setAlpha(1) });
    }
    if (this.vidas <= 0) {
      // Numa fase, a cena pergunta "continuar?"; no campo de treino recomeça as vidas.
      if (this.cena.semVidas && this.cena.semVidas()) return;
      this.vidas = VIDAS;
    }
    this.morto = false;
    this.invulneravel = true;
    this.granadas = Math.max(this.granadas, 3);
    this.trocarArma('padrao');
    corpo.reset(this.x, this.cena.cameras.main.worldView.y - 20);
    this.cena.time.delayedCall(INVULNERAVEL, () => {
      this.invulneravel = false;
      this.visual.setVisible(true);
    });
  }

  atirar(c) {
    const cena = this.cena;
    const ef = cena.efeitos;
    const d = this.direcao;

    let mira = 'frente';
    if (c.estado.cima) mira = 'cima';
    else if (!this.noChao && c.estado.baixo) mira = 'baixo';
    // Madsen gira a mira aos poucos entre frente e cima, varrendo na diagonal (como a HMG do Metal Slug).
    const varre = this.arma === 'madsen' && !this.agachado && (mira === 'cima' || mira === 'frente')
      && this.angVarre > 0.05 && this.angVarre < 0.95;

    // Peixeira automática quando o inimigo está colado.
    if (mira === 'frente') {
      const alvo = cena.alvoProximo(this.x, this.pe - 18, d, ALCANCE_PEIXEIRA);
      if (alvo) {
        // Facada como no Metal Slug: mata na hora quem está colado.
        this.facada = 230;
        cena.peixeirada(this.x + d * 22, this.pe - 22, d, alvo);
        return;
      }
    }

    let x, y, ang;
    const folha = this.arma === 'padrao' ? 'pistola' : this.arma;
    // Gordo: a arma fica 5 px mais para a frente (a barriga empurra).
    const g = this.gordo ? 5 : 0;
    if (mira === 'baixo') {
      // No ar olhando para baixo: o tiro sai da arma apontada para o chão.
      const [bx, by] = BOCAS[folha].baixo;
      x = this.x + d * (bx + g); y = this.pe - by; ang = Math.PI / 2;
    } else if (varre) {
      const k = this.angVarre;
      const [fx, fy] = BOCAS[folha].frente;
      const [cx, cy] = BOCAS[folha].cima;
      x = this.x + d * (fx + (cx - fx) * k + g);
      y = this.pe - (fy + (cy - fy) * k);
      ang = d > 0 ? -k * Math.PI / 2 : Math.PI + k * Math.PI / 2;
    } else {
      // Tiro sai da boca da arma, na pose do Lampião segurando aquela arma (a padrão é a pistola).
      const [bx, by] = BOCAS[folha][mira === 'cima' ? 'cima' : this.agachado ? 'agachado' : 'frente'];
      x = this.x + d * (bx + g);
      y = this.pe - by + (mira === 'cima' ? 0 : Phaser.Math.Between(-1, 1) * (this.arma === 'padrao' ? 1 : 0));
      ang = mira === 'cima' ? -Math.PI / 2 : d > 0 ? 0 : Math.PI;
    }
    const arma = ARMAS[this.arma];
    if (arma.rajada) cena.rajada(x, y, ang, arma.rajada, d, this.forca);
    for (let k = 0; k < arma.tiros; k++) {
      let a = ang;
      if (arma.leque) a += (k / (arma.tiros - 1) - 0.5) * arma.leque;
      if (arma.espalha) a += Phaser.Math.FloatBetween(-arma.espalha, arma.espalha);
      cena.balas.disparar(x, y, a, arma.bala, this.forca);
    }
    ef.disparo(x, y, ang, arma.clarao);
    if (arma.capsula) ef.capsula(this.x + d * 10, this.pe - 17, d);
    for (let k = 0; k < (arma.fumaca || 0); k++) {
      cena.time.delayedCall(40 + k * 50, () => ef.fumaca(x + Math.cos(ang) * (6 + k * 6), y + Math.sin(ang) * (6 + k * 6) - k));
    }
    if (arma.tremor) ef.tremer(arma.tremor, 90);
    if (arma.tranco && this.noChao) this.corpo.x -= d * arma.tranco;
    this.recuo = 50;
    if (this.arma !== 'padrao' && --this.municao <= 0) this.trocarArma('padrao');
  }

  // Muda a altura do corpo mantendo o pé no mesmo lugar (o corpo é centrado).
  ajustarAltura(altura) {
    const diferenca = this.corpo.body.height - altura;
    this.corpo.body.setSize(14, altura);
    this.corpo.y += diferenca / 2;
  }

  aterrissar() {
    this.cena.efeitos.poeira(this.x, this.pe, 5);
    this.esticar(1.25, 0.75);
  }

  // Pixel art não pode ser esticado em escala quebrada (os pixels deformam);
  // o impacto do pulo e da queda fica por conta da poeira.
  esticar() {}

  animar(dt) {
    const v = this.visual;
    const corpo = this.corpo.body;
    let quadro;
    this.arremesso = (this.arremesso || 0) - dt;
    this.facada = (this.facada || 0) - dt;
    // Facada em dois tempos: levanta a peixeira e desce o golpe largo.
    if (this.facada > 0 && !this.agachado) quadro = this.facada > 170 ? 'facada1' : 'facada';
    else if (this.arremesso > 0 && !this.agachado) quadro = 'arremesso';
    else if (this.agachado) quadro = 'agachado';
    else if (this.arma === 'madsen' && this.angVarre > 0 && this.angVarre < 1) quadro = this.angVarre > 0.5 ? 'mira_cima' : 'atirando';
    else if (this.miraCima) quadro = 'mira_cima';
    else if (this.miraBaixo) quadro = 'mira_baixo';
    else if (!this.noChao) quadro = 'pulo';
    else if (this.arma === 'estilingue' && this.desdeTiro < 420) {
      // Baladeira: solta a liga e logo puxa a próxima pedra.
      quadro = this.desdeTiro < 110 ? 'atirando' : 'recarga';
    }
    else if (corpo.velocity.x !== 0) {
      this.passo += dt;
      quadro = LAMPIAO.corrida[Math.floor(this.passo / 80) % LAMPIAO.corrida.length];
      if (Math.floor(this.passo / 240) !== Math.floor((this.passo - dt) / 240)) {
        this.cena.efeitos.poeira(this.x - this.direcao * 4, this.pe, 2);
      }
    } else {
      this.passo = 0;
      // Grita ao atirar parado.
      quadro = this.desdeTiro < 160 ? 'atirando' : 'parado';
    }
    // Com arma pesada, usa a folha do Lampião segurando aquela arma.
    const folha = (this.arma === 'padrao' ? 'lampiao' : `lampiao_${this.arma}`) + (this.gordo ? '_gordo' : '');
    if (v.texture.key !== folha) v.setTexture(folha);
    v.setFrame(LAMPIAO[quadro]);
    v.setFlipX(this.direcao < 0);
    // O pé fica na origem; ao virar, o desenho espelha e o centro muda de lado.
    const Q = this.gordo ? LAMPIAO_GORDO : LAMPIAO;
    const ox = this.direcao > 0 ? Q.peX : Q.largura - Q.peX;
    v.setOrigin(ox / Q.largura, Q.peY / Q.altura);

    const recuo = this.recuo > 0 ? -this.direcao : 0;
    this.recuo -= dt;
    v.setPosition(Math.round(this.x + recuo), Math.round(this.pe));
  }
}
