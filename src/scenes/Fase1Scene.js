import { CenaJogo, LARGURA, ALTURA } from './CenaJogo.js';
import { Refem } from '../objetos/Refem.js';
import { Disco, Bode } from '../objetos/Disco.js';
import { Caixotes } from '../objetos/Caixotes.js';
import { estiloTexto } from '../texto.js';
import { hex } from '../paleta.js';

const CONTAGEM = 9; // segundos do "continuar?"

// Fase 1: caatinga, primeiro contato e queda do disco.
// Os dados (chão, plataformas, caixotes, reféns, ondas) vêm de assets/fases/fase1.json,
// gerado junto com a arte por tools/arte/fase1.py.
export class Fase1Scene extends CenaJogo {
  constructor() {
    super('Fase1');
  }

  get tudoVolta() {
    return false;
  }

  configurar() {
    this.dados = this.cache.json.get('fase1');
    const [x, y] = this.dados.inicio;
    return { largura: this.dados.largura, inicio: { x, y } };
  }

  criarFundo() {
    const d = this.dados.camadas;
    this.add.image(0, 0, 'ceu').setOrigin(0).setScrollFactor(0).setDepth(-10);
    const repete = (chave, y, fator) => [this.add.tileSprite(0, y, LARGURA, this.textures.get(chave).source[0].height, chave)
      .setOrigin(0).setScrollFactor(0).setDepth(-8), fator];
    this.nuvens = repete('nuvens', 6, 0.03);
    this.camadas = [this.nuvens, repete('serras', 96, 0.08), repete('paredoes', 86, 0.2)];
    this.ventoNuvens = 0;
    // Camadas pintadas da fase, cada uma andando numa velocidade (parallax).
    const pintada = (chave, base, fator, prof) => {
      const h = this.textures.get(chave).source[0].height;
      return this.add.image(0, base - h, chave).setOrigin(0).setScrollFactor(fator, 0).setDepth(prof);
    };
    pintada('f1_meio', d.meio.base, d.meio.fator, -3);
    pintada('f1_perto', d.perto.base, d.perto.fator, -2);
    pintada('f1_frente', d.frente.base, d.frente.fator, 25);
  }

  montarCenario() {
    const d = this.dados;
    this.add.image(0, d.camadas.jogo.y, 'f1_jogo').setOrigin(0).setDepth(5);
    for (const [x, y, w, h, umLado] of d.solidos) this.solido(x, y, w, h, !!umLado);
    this.caixotes = new Caixotes(this, d.caixotes);
  }

  povoar() {
    const d = this.dados;
    for (const [x, pe, tipo, opcoes] of d.inimigos) this.adicionarInimigo(x, pe, tipo, opcoes || {});
    this.refens = d.refens.map(([x, pe]) => {
      const r = new Refem(this, x, pe);
      this.alvos.add(r);
      r.reiniciar();
      return r;
    });
    this.bodes = d.bodes.map(([x, pe]) => {
      const b = new Bode(this, x, pe);
      this.physics.add.collider(b, this.solidos);
      return b;
    });
    for (const [x] of d.discos) {
      // O disco abduz quem estiver por perto: reféns e o bode Fubá.
      const vitimas = [...this.refens, ...this.bodes].filter((v) => Math.abs(v.x - x) < 220);
      const disco = new Disco(this, x, vitimas);
      this.alvos.add(disco);
      disco.body.allowGravity = false;
    }
    for (const [x, y, arma] of d.itens) this.itens.colocar(x, y, arma);
    // Fogo nos destroços do disco caído.
    if (!this.anims.exists('chama_viva')) {
      this.anims.create({ key: 'chama_viva', frames: this.anims.generateFrameNumbers('chama', { start: 0, end: 3 }),
        frameRate: 10, repeat: -1, yoyo: true });
    }
    this.fogos = d.fogos.map(([x, y], k) => {
      const f = this.add.sprite(x, y, 'chama', 0).setOrigin(0.5, 0.8).setDepth(7);
      f.play({ key: 'chama_viva', startFrame: k % 4 });
      return f;
    });
    this.proximaFumaca = 0;

    this.ondas = d.ondas.map((o) => ({ ...o, estado: 'esperando', inimigos: o.inimigos.map((i) => [...i]) }));
    this.onda = null;
    this.minX = 0;
    this.terminou = false;

    // Mensagens no meio da tela (fora da HUD para ficarem por baixo dos botões de toque).
    this.aviso = this.add.text(LARGURA / 2, 70, '', estiloTexto(hex('amarelo_fogo'), 16)).setOrigin(0.5)
      .setScrollFactor(0).setDepth(40).setVisible(false);
    this.subaviso = this.add.text(LARGURA / 2, 94, '', estiloTexto(hex('branco'))).setOrigin(0.5)
      .setScrollFactor(0).setDepth(40).setVisible(false);
    this.seta = this.add.text(LARGURA - 8, 90, 'VAI! >>', estiloTexto(hex('amarelo_fogo'), 8)).setOrigin(1, 0.5)
      .setScrollFactor(0).setDepth(40).setVisible(false);
    this.mostrar('MISSÃO 1', 'CAATINGA, 1936', 2200);
  }

  mostrar(texto, sub = '', ms = 1800) {
    this.aviso.setText(texto).setVisible(true).setAlpha(1).setScale(2);
    this.subaviso.setText(sub).setVisible(!!sub).setAlpha(1);
    this.tweens.killTweensOf([this.aviso, this.subaviso]);
    this.tweens.add({ targets: this.aviso, scale: 1, duration: 180, ease: 'Back.easeOut' });
    if (ms) this.tweens.add({ targets: [this.aviso, this.subaviso], alpha: 0, delay: ms, duration: 300 });
  }

  // ------------------------------------------------------------ ondas
  comecarOnda(onda) {
    const cam = this.cameras.main;
    onda.estado = 'lutando';
    onda.vivos = [];
    onda.faltam = onda.inimigos.length;
    this.onda = onda;
    this.seta.setVisible(false);
    const [x0, x1] = onda.trava;
    cam.setBounds(x0, 0, x1 - x0, ALTURA);
    for (const [tipo, lado, atraso, opcoes] of onda.inimigos) {
      this.time.delayedCall(atraso, () => {
        const v = cam.worldView;
        let x;
        let y;
        if (lado === 'ceu') {
          x = Phaser.Math.Between(Math.round(v.x + 60), Math.round(v.right - 40));
          y = -30;
        } else {
          x = lado === 'esq' ? v.x - 18 : v.right + 18;
          y = this.chaoAbaixo(x, 60);
        }
        const inimigo = this.adicionarInimigo(x, y, tipo, opcoes || {});
        if (lado === 'ceu') inimigo.caindo = true;
        else inimigo.virar(lado === 'esq' ? 1 : -1);
        onda.vivos.push(inimigo);
        onda.faltam--;
      });
    }
  }

  ondaAcabou(onda) {
    return onda.faltam === 0 && onda.vivos.every((i) => !i.vivo);
  }

  terminarOnda(onda) {
    onda.estado = 'feita';
    this.onda = null;
    this.cameras.main.setBounds(this.minX, 0, this.larguraMundo - this.minX, ALTURA);
    this.seta.setVisible(true);
    this.tweens.killTweensOf(this.seta);
    this.seta.setAlpha(1);
    this.tweens.add({ targets: this.seta, alpha: 0.2, duration: 250, yoyo: true, repeat: 7,
      onComplete: () => this.seta.setVisible(false) });
  }

  // ------------------------------------------------------------ vidas
  // Sem vidas: pergunta "CONTINUAR?" com contagem, como no fliperama.
  semVidas() {
    this.pausado = true;
    this.contagem = CONTAGEM;
    this.proximoSegundo = this.time.now + 1000;
    this.mostrar('CONTINUAR?', `${CONTAGEM}`, 0);
    return true;
  }

  atualizarContinuar(t) {
    const c = this.controles;
    if (c.apertou('confirmar') || c.apertou('atirar') || c.apertou('pular')) {
      this.pausado = false;
      this.aviso.setVisible(false);
      this.subaviso.setVisible(false);
      this.jogador.continuar();
      return;
    }
    if (t > this.proximoSegundo) {
      this.proximoSegundo = t + 1000;
      this.contagem--;
      this.subaviso.setText(`${Math.max(0, this.contagem)}`);
      if (this.contagem < 0) {
        this.pausado = 'fim';
        this.mostrar('FIM DE JOGO', '', 0);
        this.time.delayedCall(2500, () => this.scene.start('Menu'));
      }
    }
  }

  // ------------------------------------------------------------ a cada quadro
  atualizarFundo(cam, dt) {
    this.ventoNuvens += dt * 0.004;
    for (const [camada, fator] of this.camadas) camada.tilePositionX = Math.round(cam.scrollX * fator);
    this.nuvens[0].tilePositionX = Math.round(cam.scrollX * this.nuvens[1] + this.ventoNuvens);
  }

  atualizarFase(t) {
    if (this.pausado === true) {
      this.atualizarContinuar(t);
      return;
    }
    if (this.pausado) return;
    const cam = this.cameras.main;
    const j = this.jogador;

    // A câmera não volta para trás (como no Metal Slug).
    if (!this.onda && cam.scrollX > this.minX) {
      this.minX = Math.floor(cam.scrollX);
      cam.setBounds(this.minX, 0, this.larguraMundo - this.minX, ALTURA);
    }
    // O Lampião não sai da tela.
    const v = cam.worldView;
    const corpo = j.corpo.body;
    if (j.x < v.x + 8) corpo.x = v.x + 8 - corpo.halfWidth;
    if (j.x > v.right - 8) corpo.x = v.right - 8 - corpo.halfWidth;

    if (this.onda) {
      if (this.ondaAcabou(this.onda)) this.terminarOnda(this.onda);
    } else {
      const proxima = this.ondas.find((o) => o.estado === 'esperando');
      if (proxima && j.x >= proxima.gatilho) this.comecarOnda(proxima);
    }

    // Fumaça subindo do disco caído.
    if (t > this.proximaFumaca && v.right > 2500) {
      this.proximaFumaca = t + 140;
      const [fx, fy] = Phaser.Utils.Array.GetRandom(this.dados.fogos);
      this.efeitos.fumacaSobe(fx + Phaser.Math.Between(-4, 4), fy - 14);
    }

    if (!this.terminou && j.x >= this.dados.fim && !j.morto && this.ondas.every((o) => o.estado === 'feita')) {
      this.terminou = true;
      this.pausado = 'fim';
      this.mostrar('MISSÃO 1 CUMPRIDA!', 'CONTINUA...', 0);
      this.time.delayedCall(4500, () => this.scene.start('Menu'));
    }
  }
}
