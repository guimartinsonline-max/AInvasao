import { hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { VEICULOS } from '../quadros.js';
import { som } from '../som.js';

// Veículos da Volante. Os dois são alvos (levam tiro, granada e explosão) e,
// andando, atropelam o Lampião e esmagam caixotes no caminho.

class Veiculo extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, tipo, x, pe, opcoes) {
    super(cena, x, pe, tipo, 0);
    this.tipo = tipo;
    this.q = VEICULOS[tipo];
    this.opcoes = opcoes;
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.setOrigin(0.5, 1).setDepth(8);
    this.persegue = true;
    this.vivo = true;
    this.vida = opcoes.vida;
    this.vidaMax = opcoes.vida;
    this.etapa = 0; // dano na lataria: 0 inteiro a 3 arrebentado
    this.base = 0; // quadro sem a etapa somada
    this.giro = 0; // distância rodada (gira as rodas)
    this.proximaPoeira = 0;
    this.proximoDano = 0;
    this.direcao = opcoes.direcao || -1;
    this.setFlipX(this.direcao < 0);
    this.body.setCollideWorldBounds(false);
    // Roda por cima do terreno: não bate em lajedo baixo nem em sacos de areia,
    // acompanha o chão debaixo do meio do veículo.
    this.voa = true;
    this.body.allowGravity = false;
    this.passo = 0;
    this.proximaFumaca = 0;
    this.texto = cena.add.text(0, 0, '', estiloTexto(hex('branco'))).setOrigin(0.5).setDepth(30).setVisible(false);
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (!this.body.enable) return;
    const chao = this.scene.chaoAbaixo(this.x, this.y - 24) - 1;
    this.y += Phaser.Math.Clamp(chao - this.y, -3, 4);
    this.body.updateFromGameObject?.();
    if (this.vivo) this.fumegar(t);
  }

  // Mostra um quadro da etapa de dano atual.
  mostrar(i) {
    this.base = i;
    this.setFrame(i + this.etapa * this.q.n);
  }

  // Quadro de rodar conforme a distância andada (as rodas giram no ritmo do chão).
  quadroRoda(lista, dist) {
    this.giro += Math.abs(dist);
    return lista[Math.floor(this.giro / 2.2) % lista.length];
  }

  // Lataria arrebentada solta fumaça (etapa 2) e pega fogo (etapa 3).
  fumegar(t) {
    if (this.etapa < 2 || t < this.proximoDano) return;
    this.proximoDano = t + (this.etapa === 3 ? 180 : 420);
    const ef = this.scene.efeitos;
    const [x, y] = this.ponto(Phaser.Math.Between(-this.q.largura / 3, this.q.largura / 4), Phaser.Math.Between(14, 34));
    if (this.etapa === 3 && Math.random() < 0.6) ef.chama(x, y);
    ef.fumacaSobe(x, y - 6);
  }

  // Poeira das rodas: partículas saindo de baixo de cada roda e nuvenzinha atrás.
  poeiraRodas(t, velocidade) {
    if (t < this.proximaPoeira) return;
    this.proximaPoeira = t + Math.max(50, 160 - velocidade * 0.7);
    const ef = this.scene.efeitos;
    for (const dx of this.q.rodas) {
      const [px, py] = this.ponto(dx - 6, 1);
      ef.poeira(px, py, velocidade > 90 ? 3 : 2);
    }
    if (Math.random() < 0.5) {
      const [px, py] = this.ponto(this.q.rodas[0] - 12, 0);
      ef.poeiraPasso(px, py, this.direcao > 0);
    }
  }

  // Ponto do veículo medido no desenho virado para a direita (dx a partir do centro, dy a partir do chão).
  ponto(dx, dy) {
    return [this.x + dx * this.direcao, this.y - dy];
  }

  levarDano(dano, origemX, forte = false, morte = null) {
    if (!this.vivo) return;
    // Peixeira não corta lataria: conta como um golpe forte.
    if (morte === 'facada') dano = 4;
    this.vida -= dano;
    // Faísca no lado que levou o tiro.
    const lado = Math.sign((origemX ?? this.x) - this.x) || -this.direcao;
    this.scene.efeitos.faisca(this.x + lado * Phaser.Math.Between(10, this.q.largura / 2 - 8),
      this.y - Phaser.Math.Between(10, this.q.altura - 20), 3);
    const etapa = this.vida <= 0 ? this.etapa : Math.min(3, Math.floor((1 - this.vida / this.vidaMax) * 4));
    if (etapa > this.etapa) {
      // A lataria arrebenta mais um pouco: estilhaços de chapa, estalo e a folha da etapa nova.
      this.etapa = etapa;
      const [x, y] = this.ponto(Phaser.Math.Between(-this.q.largura / 3, this.q.largura / 3), Phaser.Math.Between(16, 36));
      this.scene.efeitos.explosao(x, y, 0.6);
      this.scene.efeitos.detritoEm.explode(10, x, y);
      this.scene.efeitos.faisca(x, y, 10);
      this.mostrar(this.base);
    }
    this.setTint(0xffffff).setTintMode(Phaser.TintModes.FILL);
    this.scene.time.delayedCall(45, () => this.vivo && this.clearTint());
    this.aoDano?.();
    if (this.vida <= 0) this.destruir();
  }

  // Anda na direção atual: rodas girando, fumaça do escapamento e poeira.
  rodar(t, dt, velocidade) {
    this.body.setVelocityX(this.direcao * velocidade);
    if (velocidade === 0) return;
    this.passo += dt;
    this.mostrar(this.quadroRoda(this.q.andar, velocidade * dt / 1000));
    if (t > this.proximaFumaca) {
      this.proximaFumaca = t + 120;
      const [ex, ey] = this.ponto(-this.q.largura / 2 + 2, 14);
      this.scene.efeitos.fumaca(ex, ey);
    }
    this.poeiraRodas(t, velocidade);
    this.esmagar(velocidade);
  }

  // Andando, passa por cima de caixote e atropela o Lampião.
  esmagar(velocidade) {
    const cena = this.scene;
    const frente = this.x + this.direcao * (this.q.largura / 2 - 4);
    for (const c of cena.caixotes.vivos()) {
      if (Math.abs(c.x - frente) < 22 && Math.abs(c.y - this.y) < 30) c.levarDano(99);
    }
    const j = cena.jogador;
    if (velocidade > 30 && !j.morto && !j.invulneravel && Math.abs(j.x - this.x) < this.q.largura / 2 - 6
      && j.pe > this.y - 40) {
      j.morrer(this.direcao * 200);
    }
  }

  // Explosões em cadeia pela lataria e a carcaça queimando no lugar.
  destruir() {
    const cena = this.scene;
    this.vivo = false;
    this.clearTint();
    this.body.setVelocityX(0);
    cena.pontuar(this.opcoes.pontos, this.x, this.y - this.q.altura - 6);
    const n = this.opcoes.explosoes;
    for (let k = 0; k < n; k++) {
      cena.time.delayedCall(k * 140, () => {
        const x = this.x + Phaser.Math.Between(-this.q.largura / 2 + 12, this.q.largura / 2 - 12);
        const y = this.y - Phaser.Math.Between(10, this.q.altura - 16);
        cena.explodir(x, y, 30, 4, k === n - 1 ? 1.4 : 1);
      });
    }
    cena.time.delayedCall(n * 140 - 100, () => {
      this.setFrame(this.q.destruido);
      cena.efeitos.tremer(0.016, 400);
      this.queimando = cena.time.addEvent({
        delay: 140, loop: true, callback: () => {
          const x = this.x + Phaser.Math.Between(-this.q.largura / 3, this.q.largura / 3);
          cena.efeitos.chama(x, this.y - Phaser.Math.Between(8, 26));
          if (Math.random() < 0.5) cena.efeitos.fumacaSobe(x, this.y - 30);
        },
      });
      // A carcaça queima um tempo e se apaga.
      cena.time.delayedCall(9000, () => this.queimando.remove());
    });
    this.aoDestruir?.();
  }

  sair() {
    this.vivo = false;
    this.setVisible(false);
    this.body.enable = false;
  }

  foraDaTela(margem = 0) {
    const v = this.scene.cameras.main.worldView;
    return this.x < v.x - this.q.largura / 2 - margem || this.x > v.right + this.q.largura / 2 + margem;
  }
}

// Caminhão da Volante: chega, freia, abre a lona e os soldados pulam lá de trás.
// Depois vai embora por onde veio. opcoes: para (x onde freia), soldados (tipos),
// aoSoltar(inimigo) para a onda contar quem desceu.
export class Caminhao extends Veiculo {
  constructor(cena, x, pe, opcoes) {
    super(cena, 'caminhao', x, pe, { vida: 26, pontos: 500, explosoes: 3, ...opcoes });
    this.body.setSize(112, 34).setOffset(6, 28);
    this.estado = 'chegando';
    this.fila = [...(opcoes.soldados || ['volante', 'volante'])];
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (!this.vivo) return;
    const cena = this.scene;
    if (this.estado === 'chegando') {
      const falta = (this.opcoes.para - this.x) * this.direcao;
      this.rodar(t, dt, falta < 40 ? Math.max(40, falta * 3) : 150);
      if (falta <= 2) {
        // Freada: derrapa levantando poeira e a carroceria balança.
        this.estado = 'descarregando';
        this.body.setVelocityX(0);
        this.mostrar(this.q.aberto);
        cena.efeitos.poeira(this.x, this.y, 10);
        cena.tweens.add({ targets: this, angle: this.direcao * 2, duration: 90, yoyo: true });
        this.proximo = t + 500;
      }
    } else if (this.estado === 'descarregando') {
      if (t < this.proximo) return;
      if (this.fila.length) {
        this.proximo = t + 520;
        this.soltarSoldado(this.fila.shift());
      } else {
        this.estado = 'esperando';
        this.proximo = t + 1400;
      }
    } else if (this.estado === 'esperando') {
      if (t < this.proximo) return;
      // Vai embora de ré, para o lado de onde veio.
      this.estado = 'saindo';
      this.mostrar(this.q.andar[0]);
      this.direcao = -this.direcao;
      this.setFlipX(this.direcao < 0);
    } else if (this.estado === 'saindo') {
      this.rodar(t, dt, 120);
      if (this.foraDaTela(30)) this.sair();
    }
  }

  // Soldado pula lá de trás da carroceria, por cima da tampa.
  soltarSoldado(tipo) {
    const cena = this.scene;
    const [x, y] = this.ponto(-this.q.largura / 2 + 6, 26);
    const inimigo = cena.adicionarInimigo(x, cena.chaoAbaixo(x, y), tipo, {});
    inimigo.body.reset(x, y);
    const dir = cena.jogador.x > x ? 1 : -1;
    inimigo.virar(dir);
    inimigo.body.setVelocity(-this.direcao * 60, -200);
    inimigo.caindo = true;
    inimigo.setDepth(7);
    cena.time.delayedCall(250, () => inimigo.setDepth(9));
    this.opcoes.aoSoltar?.(inimigo);
  }

  destruir() {
    // Quem não desceu ainda fica pelo caminho (a onda deixa de esperar por eles).
    for (const _ of this.fila) this.opcoes.aoPerder?.();
    this.fila = [];
    super.destruir();
  }
}

// Carro blindado: o "tanque" da Volante. Anda para lá e para cá numa faixa,
// metralha reto na altura do peito (agachado escapa) e solta obus em arco pelo
// canhão. Com metade da vida a torre quebra: perde o canhão e a metralhadora
// fica mais rápida. opcoes: para (centro da faixa onde fica lutando).
export class Blindado extends Veiculo {
  constructor(cena, x, pe, opcoes) {
    super(cena, 'blindado', x, pe, { vida: 90, pontos: 2000, explosoes: 7, ...opcoes });
    this.body.setSize(118, 44).setOffset(7, 46);
    this.estado = 'chegando';
    this.vidaMax = this.vida;
    this.torre = true;
    this.proximoTiro = 0;
    this.proximoCanhao = 0;
    this.proximaVolta = 0;
  }

  aoDano() {
    if (this.torre && this.vida <= this.vidaMax / 2) {
      // A torre arrebenta: o canhão voa longe soltando faísca.
      this.torre = false;
      const cena = this.scene;
      const [x, y] = this.ponto(30, 58);
      cena.explodir(x, y, 20, 0, 1);
      cena.efeitos.faisca(x, y, 14);
      cena.efeitos.detritoEm.explode(14, x, y);
      cena.efeitos.tremer(0.01, 200);
      this.texto.setText('CABRUNCO!').setPosition(this.x, this.y - this.q.altura - 8).setVisible(true).setAlpha(1);
      cena.tweens.add({ targets: this.texto, alpha: 0, delay: 700, duration: 300 });
    }
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (!this.vivo) return;
    const cena = this.scene;
    const j = cena.jogador;
    if (!this.torre && t > this.proximaFumaca + 60) {
      const [x, y] = this.ponto(4, 58);
      cena.efeitos.fumacaSobe(x, y);
    }
    if (this.estado === 'chegando') {
      const falta = (this.opcoes.para - this.x) * this.direcao;
      this.rodar(t, dt, 70);
      if (falta <= 0) {
        this.estado = 'lutando';
        this.proximaVolta = t + 1800;
        this.proximoTiro = t + 600;
        this.proximoCanhao = t + 1400;
      }
      return;
    }
    // Faixa de vai-e-vem em volta do ponto de parada, sempre de frente para o Lampião.
    const frente = j.x < this.x ? -1 : 1;
    if (frente !== this.direcao && t > this.proximaVolta) {
      this.direcao = frente;
      this.setFlipX(this.direcao < 0);
    }
    // Vai e vem em volta do ponto de parada (avança, para, recua), sem nunca virar de costas.
    if (t > this.proximaVolta) {
      this.proximaVolta = t + Phaser.Math.Between(1600, 2600);
      this.alvoX = this.opcoes.para + Phaser.Utils.Array.GetRandom([-50, 0, 40]);
    }
    const lista = this.torre ? this.q.andar : this.q.quebrado;
    const quadroParado = lista[0];
    if (!this.avisando && this.alvoX !== undefined && Math.abs(this.alvoX - this.x) > 4) {
      const sentido = Math.sign(this.alvoX - this.x);
      this.body.setVelocityX(sentido * 40);
      this.passo += dt;
      this.mostrar(this.quadroRoda(lista, 40 * dt / 1000));
      this.poeiraRodas(t, 40);
      this.esmagar(sentido === this.direcao ? 40 : 0);
    } else {
      this.body.setVelocityX(0);
      if (this.base !== this.q.tiro) this.mostrar(quadroParado);
    }
    if (j.morto) return;
    // Metralhadora: avisa antes (faísca no cano e o carro para), depois uma rajada curta
    // reta na altura da cabeça. Agachado escapa; dá para pular por cima com tempo.
    if (t > this.proximoTiro && !this.avisando) {
      this.avisando = true;
      som('alerta');
      const [ax, ay] = this.ponto(this.q.largura / 2 + 2, 37);
      cena.efeitos.faisca(ax, ay, 5);
      this.texto.setText('!').setPosition(ax, ay - 12).setVisible(true).setAlpha(1);
      cena.tweens.killTweensOf(this.texto);
      cena.tweens.add({ targets: this.texto, alpha: 0, delay: 350, duration: 150 });
      cena.time.delayedCall(500, () => {
        this.avisando = false;
        const rajada = this.torre ? 3 : 4;
        this.proximoTiro = this.scene.time.now + (this.torre ? 2800 : 2000);
        for (let k = 0; k < rajada; k++) {
          cena.time.delayedCall(k * 130, () => {
            if (!this.vivo) return;
            const [x, y] = this.ponto(this.q.largura / 2 + 2, 37);
            cena.balasInimigas.disparar(x, y, this.direcao, 'pesada');
            cena.efeitos.disparo(x, y, this.direcao > 0 ? 0 : Math.PI, 'grande');
            cena.efeitos.capsula(x - this.direcao * 14, y + 2, -this.direcao);
          });
        }
      });
    }
    // Canhão: obus em arco no Lampião.
    if (this.torre && t > this.proximoCanhao) {
      this.proximoCanhao = t + 4200;
      this.proximoTiro = Math.max(this.proximoTiro, t + 1200); // não atira a metralhadora junto
      this.mostrar(this.q.tiro);
      cena.time.delayedCall(160, () => this.vivo && this.torre && this.mostrar(this.q.andar[0]));
      const [x, y] = this.ponto(this.q.largura / 2 - 8, 58);
      cena.balasInimigas.lancarObus(x, y, this.direcao, Math.abs(j.x - x));
      cena.efeitos.disparo(x, y, this.direcao > 0 ? 0 : Math.PI, 'canhao');
      for (let k = 0; k < 3; k++) cena.efeitos.fumaca(x + this.direcao * k * 6, y - k * 2);
      cena.efeitos.poeira(this.x, this.y, 6);
      this.setX(this.x - this.direcao * 3); // o carro todo dá o tranco do canhão
      cena.efeitos.tremer(0.008, 140);
    }
  }
}
