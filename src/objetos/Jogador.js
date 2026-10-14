// Lampião (provisório). A física usa um corpo invisível; o sprite visível só
// acompanha, para poder esticar e amassar sem mexer na colisão.

const VEL_CORRER = 100;
const VEL_AGACHADO = 36;
const VEL_PULO = -310;
const CORTE_PULO = -110; // soltar o botão no meio do pulo corta a subida
const TOLERANCIA_BEIRADA = 100; // ms para ainda pular depois de sair da beirada
const MEMORIA_PULO = 110; // ms que um pulo apertado antes de tocar o chão fica guardado
const INTERVALO_TIRO = 150; // segurando o botão
const INTERVALO_TIRO_TOQUE = 70; // apertando repetido
const ALCANCE_PEIXEIRA = 22;
const GRANADAS = 10;

export class Jogador {
  constructor(cena, x, y) {
    this.cena = cena;
    this.corpo = cena.physics.add.image(x, y, 'px').setVisible(false);
    this.corpo.body.setSize(10, 20).setMaxVelocityY(420);
    this.visual = cena.add.sprite(x, y, 'lamp_parado').setOrigin(0.5, 1).setDepth(10);

    this.direcao = 1;
    this.beirada = 0;
    this.memoriaPulo = 0;
    this.desdeTiro = 1000;
    this.noChao = false;
    this.agachado = false;
    this.passo = 0;
    this.recuo = 0;
    this.granadas = GRANADAS;
    this.desdeGranada = 1000;
  }

  get x() { return this.corpo.body.center.x; }
  get pe() { return this.corpo.body.bottom; }

  atualizar(dt, c) {
    const corpo = this.corpo.body;
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
      this.ajustarAltura(this.agachado ? 14 : 20);
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
        this.ajustarAltura(20);
      }
      corpo.setVelocityY(VEL_PULO);
      this.cena.efeitos.poeira(this.x, this.pe, 6);
      this.esticar(0.75, 1.3);
    }
    if (!c.estado.pular && corpo.velocity.y < CORTE_PULO) corpo.setVelocityY(CORTE_PULO);

    // Atirar.
    this.desdeTiro += dt;
    const apertou = c.apertou('atirar');
    if ((apertou && this.desdeTiro >= INTERVALO_TIRO_TOQUE) || (c.estado.atirar && this.desdeTiro >= INTERVALO_TIRO)) {
      this.desdeTiro = 0;
      this.atirar(c);
    }

    // Granada.
    this.desdeGranada += dt;
    // Campo de treino: repõe as granadas depois de um tempo sem nenhuma.
    if (this.granadas === 0 && this.desdeGranada > 3000) this.granadas = GRANADAS;
    if (c.apertou('granada') && this.granadas > 0 && this.desdeGranada > 300) {
      this.desdeGranada = 0;
      this.granadas--;
      this.cena.lancarGranada(this.x + this.direcao * 6, this.pe - 18, this.direcao, corpo.velocity.x);
    }

    this.animar(dt);
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
      const alvo = cena.alvoProximo(this.x, this.pe - 10, d, ALCANCE_PEIXEIRA);
      if (alvo) {
        cena.peixeirada(this.x + d * 12, this.pe - 12, d, alvo);
        return;
      }
    }

    let x, y, ang;
    if (mira === 'cima') {
      x = this.x + d * 2; y = this.pe - 26; ang = -Math.PI / 2;
    } else if (mira === 'baixo') {
      x = this.x; y = this.pe + 2; ang = Math.PI / 2;
    } else {
      x = this.x + d * 12;
      y = this.pe - (this.agachado ? 6 : 10) + Phaser.Math.Between(-1, 1);
      ang = d > 0 ? 0 : Math.PI;
    }
    cena.balas.disparar(x, y, ang);
    ef.disparo(x, y, ang);
    ef.capsula(this.x + d * 3, this.pe - 12, d);
    this.recuo = 50;
  }

  // Muda a altura do corpo mantendo o pé no mesmo lugar (o corpo é centrado).
  ajustarAltura(altura) {
    const diferenca = this.corpo.body.height - altura;
    this.corpo.body.setSize(10, altura);
    this.corpo.y += diferenca / 2;
  }

  aterrissar() {
    this.cena.efeitos.poeira(this.x, this.pe, 5);
    this.esticar(1.25, 0.75);
  }

  esticar(sx, sy) {
    const tw = this.cena.tweens;
    tw.killTweensOf(this.visual);
    this.visual.setScale(sx, sy);
    tw.add({ targets: this.visual, scaleX: 1, scaleY: 1, duration: 140, ease: 'Quad.easeOut' });
  }

  animar(dt) {
    const v = this.visual;
    const corpo = this.corpo.body;
    let quadro = 'lamp_parado';
    if (this.agachado) quadro = 'lamp_agachado';
    else if (!this.noChao) quadro = 'lamp_pulo';
    else if (corpo.velocity.x !== 0) {
      this.passo += dt;
      quadro = Math.floor(this.passo / 110) % 2 ? 'lamp_corre2' : 'lamp_corre1';
      if (Math.floor(this.passo / 220) !== Math.floor((this.passo - dt) / 220)) {
        this.cena.efeitos.poeira(this.x - this.direcao * 4, this.pe, 2);
      }
    } else {
      this.passo = 0;
    }
    if (v.texture.key !== quadro) v.setTexture(quadro);
    v.setFlipX(this.direcao < 0);

    // O sprite tem a arma para a frente; desloca para o corpo ficar centrado.
    const recuo = this.recuo > 0 ? -this.direcao : 0;
    this.recuo -= dt;
    v.setPosition(Math.round(this.x + this.direcao * 2 + recuo), Math.round(this.pe));
  }
}
