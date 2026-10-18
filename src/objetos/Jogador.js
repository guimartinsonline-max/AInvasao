import { LAMPIAO } from '../quadros.js';
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

export class Jogador {
  constructor(cena, x, y) {
    this.cena = cena;
    this.corpo = cena.physics.add.image(x, y, 'px').setVisible(false);
    this.corpo.body.setSize(14, ALTURA_EM_PE).setMaxVelocityY(420);
    this.visual = cena.add.sprite(x, y, 'lampiao', LAMPIAO.parado).setDepth(10);


    this.direcao = 1;
    this.beirada = 0;
    this.memoriaPulo = 0;
    this.desdeTiro = 1000;
    this.noChao = false;
    this.agachado = false;
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
      if (corpo.blocked.down) corpo.setVelocityX(corpo.velocity.x * 0.85);
      this.visual.setFrame(LAMPIAO.susto);
      this.visual.setPosition(Math.round(this.x), Math.round(this.pe));
      return;
    }
    if (this.invulneravel) this.visual.setVisible(Math.floor(this.cena.time.now / 70) % 2 === 0);
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
    corpo.setVelocityX(c.eixoX * (this.agachado ? VEL_AGACHADO : VEL_CORRER));

    // Pular, com tolerância de beirada e memória do botão.
    if (this.memoriaPulo > 0 && this.beirada > 0) {
      this.memoriaPulo = 0;
      this.beirada = 0;
      if (this.agachado) {
        this.agachado = false;
        this.ajustarAltura(ALTURA_EM_PE);
      }
      corpo.setVelocityY(VEL_PULO);
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

    this.miraCima = c.estado.cima && !this.agachado;
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
    return this.nivel === 2 ? 1.5 : 1;
  }

  // Um tiro mata, como no Metal Slug: careta de susto, voa para trás e renasce piscando.
  morrer(vxBala = 0) {
    if (this.morto || this.invulneravel) return;
    const cena = this.cena;
    this.morto = true;
    this.vidas--;
    const lado = Math.sign(vxBala) || -this.direcao;
    this.corpo.body.setVelocity(lado * 90, -240);
    cena.efeitos.parar(120);
    cena.efeitos.tremer(0.01, 220);
    cena.efeitos.faisca(this.x, this.pe - 24, 10);
    cena.time.delayedCall(1300, () => this.renascer());
  }

  // Depois do "continuar?": vidas cheias e volta ao jogo.
  continuar() {
    this.vidas = VIDAS;
    this.renascer();
  }

  renascer() {
    const corpo = this.corpo.body;
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

    // Peixeira automática quando o inimigo está colado.
    if (mira === 'frente') {
      const alvo = cena.alvoProximo(this.x, this.pe - 18, d, ALCANCE_PEIXEIRA);
      if (alvo) {
        // Facada como no Metal Slug: mata na hora quem está colado.
        this.facada = 180;
        cena.peixeirada(this.x + d * 22, this.pe - 22, d, alvo);
        return;
      }
    }

    let x, y, ang;
    if (mira === 'baixo') {
      x = this.x; y = this.pe + 2; ang = Math.PI / 2;
    } else {
      // Tiro sai da boca da arma, na pose do Lampião segurando aquela arma (a padrão é a pistola).
      const folha = this.arma === 'padrao' ? 'pistola' : this.arma;
      const [bx, by] = BOCAS[folha][mira === 'cima' ? 'cima' : this.agachado ? 'agachado' : 'frente'];
      x = this.x + d * bx;
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
    if (this.facada > 0 && !this.agachado) quadro = 'facada';
    else if (this.arremesso > 0 && !this.agachado) quadro = 'arremesso';
    else if (this.agachado) quadro = 'agachado';
    else if (this.miraCima) quadro = 'mira_cima';
    else if (!this.noChao) quadro = 'pulo';
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
    const folha = this.arma === 'padrao' ? 'lampiao' : `lampiao_${this.arma}`;
    if (v.texture.key !== folha) v.setTexture(folha);
    v.setFrame(LAMPIAO[quadro]);
    v.setFlipX(this.direcao < 0);
    // O pé fica na origem; ao virar, o desenho espelha e o centro muda de lado.
    const ox = this.direcao > 0 ? LAMPIAO.peX : LAMPIAO.largura - LAMPIAO.peX;
    v.setOrigin(ox / LAMPIAO.largura, LAMPIAO.peY / LAMPIAO.altura);

    const recuo = this.recuo > 0 ? -this.direcao : 0;
    this.recuo -= dt;
    v.setPosition(Math.round(this.x + recuo), Math.round(this.pe));
  }
}
