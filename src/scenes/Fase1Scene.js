import { CenaJogo, LARGURA, ALTURA, DY } from './CenaJogo.js';
import { Refem } from '../objetos/Refem.js';
import { Disco, Bode } from '../objetos/Disco.js';
import { Caixotes } from '../objetos/Caixotes.js';
import { estiloTexto } from '../texto.js';
import { hex } from '../paleta.js';
import { PREMIOS } from '../armas.js';
import { PEDACO, PEDACOS } from '../fase1_pedacos.js';
import { Urubus, Galinha, Varal, CasaVila, Ponte } from '../objetos/Ambiente.js';
import { Jumento } from '../objetos/Jumento.js';
import { tocarMusica, pararMusica, som } from '../som.js';
import { Biplano } from '../objetos/Biplano.js';
import { Segredo } from '../objetos/Segredos.js';
import { LAMPIAO, REFEM } from '../quadros.js';

// Fase 1 é só contra a Volante: nada de arma alienígena.
const PREMIOS_F1 = PREMIOS.filter((a) => a !== 'desintegrador');

const CONTAGEM = 9; // segundos do "continuar?"
const TEMPO = 60; // segundos por trecho, como no fliperama
const TIQUE = 1300; // ms por segundo do relógio (o do Metal Slug também anda devagar)

// Fase 1: caatinga, primeiro contato e queda do disco.
// Os dados (chão, plataformas, caixotes, reféns, ondas) vêm de assets/fases/fase1.json,
// gerado junto com a arte por tools/arte/fase1.py.
export class Fase1Scene extends CenaJogo {
  constructor(chave = 'Fase1') {
    super(chave);
  }

  get missao() {
    return 'MISSÃO 1';
  }

  get premios() {
    return PREMIOS_F1;
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
    this.camadas = [this.nuvens, repete('serras', DY - 32, 0.08), repete('paredoes', 46 + DY, 0.2)];
    this.ventoNuvens = 0;
    // Camadas pintadas da fase, cada uma andando numa velocidade (parallax).
    // Camadas pintadas da fase (em pedaços lado a lado), cada uma numa velocidade (parallax).
    const pintada = (chave, base, fator, prof) => {
      for (let k = 0; k < PEDACOS[chave]; k++) {
        const img = `${chave}_${k}`;
        const h = this.textures.get(img).source[0].height;
        this.add.image(k * PEDACO, base - h + DY, img).setOrigin(0).setScrollFactor(fator, 0).setDepth(prof);
      }
    };
    pintada('f1_meio', d.meio.base, d.meio.fator, -3);
    pintada('f1_perto', d.perto.base, d.perto.fator, -2);
    pintada('f1_frente', d.frente.base, d.frente.fator, 25);
  }

  montarCenario() {
    const d = this.dados;
    for (let k = 0; k < PEDACOS.f1_jogo; k++) {
      this.add.image(k * PEDACO, d.camadas.jogo.y, `f1_jogo_${k}`).setOrigin(0).setDepth(5);
    }
    for (const [x, y, w, h, umLado] of d.solidos) this.solido(x, y, w, h, !!umLado);
    this.caixotes = new Caixotes(this, d.caixotes);
    // Cenário vivo: casas da vila (perdem o telhado), varal, ponte que quebra.
    d.casas.forEach(([x, w, h], k) => new CasaVila(this, `casa_vila_${k}`, x, 195, w, h));
    for (const x of d.varais) new Varal(this, x, 195);
    this.ponte = new Ponte(this, d.ponte);
  }

  povoar() {
    const d = this.dados;
    for (const [x, pe, tipo, opcoes] of d.inimigos) this.adicionarInimigo(x, pe, tipo, opcoes || {});
    this.refens = d.refens.map(([x, pe, opcoes]) => {
      const r = new Refem(this, x, pe, opcoes || {});
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
    this.urubus = new Urubus(this, d.urubus);
    // Subchefe parado no campo de pouso (dá a partida quando a onda dele começa).
    this.biplanos = (d.biplanos || []).map((x) => {
      const b = new Biplano(this, x, this.chaoAbaixo(x, 60));
      this.alvos.add(b);
      b.body.allowGravity = false;
      b.artilheiro.body.allowGravity = false;
      return b;
    });
    // Segredos: cacimba, ninho no telhado, canoa e biruta.
    for (const [x, pe, tipo, premio] of d.segredos || []) {
      const sg = new Segredo(this, x, pe, tipo, premio);
      this.alvos.add(sg);
      sg.body.allowGravity = false;
    }
    // Jumento blindado esperando no fim da caatinga (trecho de veículo).
    this.jumentos = (d.jumentos || []).map((x) => new Jumento(this, x, this.chaoAbaixo(x, 60)));
    for (const x of d.galinhas) {
      const g = new Galinha(this, x, this.chaoAbaixo(x, 60));
      this.alvos.add(g);
    }
    // Fogueira dos soldados distraídos (fogo baixo animado em cima da lenha).
    this.fogueiras = (d.fogueiras || []).map(([x, pe], k) => this.add.sprite(x, pe - 4, 'chama', 0)
      .setOrigin(0.5, 1).setDepth(6).setScale(0.55).play({ key: 'chama_viva', startFrame: (k * 2) % 4 }));
    this.pontos = 0;
    this.refensSalvos = 0;
    this.tempo = TEMPO;
    this.proximoTique = 0;
    if (!this.anims.exists('chama_viva')) {
      this.anims.create({ key: 'chama_viva', frames: this.anims.generateFrameNumbers('chama', { start: 0, end: 3 }),
        frameRate: 10, repeat: -1, yoyo: true });
    }

    this.ondas = d.ondas.map((o) => ({ ...o, estado: 'esperando', inimigos: o.inimigos.map((i) => [...i]) }));
    this.onda = null;
    this.minX = 0;
    this.terminou = false;

    // Mensagens no meio da tela (fora da HUD para ficarem por baixo dos botões de toque).
    this.aviso = this.add.text(LARGURA / 2, 70 + DY / 2, '', estiloTexto(hex('amarelo_fogo'), 16)).setOrigin(0.5)
      .setScrollFactor(0).setDepth(40).setVisible(false);
    this.subaviso = this.add.text(LARGURA / 2, 94 + DY / 2, '', estiloTexto(hex('branco'))).setOrigin(0.5)
      .setScrollFactor(0).setDepth(40).setVisible(false);
    this.seta = this.add.text(LARGURA - 8, 90 + DY / 2, 'VAI! >>', estiloTexto(hex('amarelo_fogo'), 8)).setOrigin(1, 0.5)
      .setScrollFactor(0).setDepth(40).setVisible(false);
    this.mostrar('MISSÃO 1', 'CAATINGA, 1936', 2200);
    tocarMusica('caatinga');
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
    // Trava da câmera do tamanho da tela (as ondas antigas foram feitas para 384 px de largura).
    // A borda esquerda desliza até o lugar da trava: a câmera nunca pula (nada parece teletransportar).
    const [x0, x1b] = onda.trava;
    const x1 = Math.max(x1b, x0 + LARGURA);
    const inicio = Math.min(x0, Math.floor(cam.scrollX));
    cam.setBounds(inicio, -DY, x1 - inicio, ALTURA);
    if (inicio < x0) {
      const borda = { x: inicio };
      this.tweens.add({
        targets: borda, x: x0, duration: Math.min(900, (x0 - inicio) * 6), ease: 'Sine.easeInOut',
        onUpdate: () => { if (this.onda === onda) cam.setBounds(borda.x, -DY, x1 - borda.x, ALTURA); },
      });
    }
    if (onda.chefe) this.entradaChefe(onda.chefe, () => this.soltarOnda(onda));
    else this.soltarOnda(onda);
  }

  soltarOnda(onda) {
    const cam = this.cameras.main;
    for (const [tipo, lado, atraso, opcoes] of onda.inimigos) {
      this.time.delayedCall(atraso, () => {
        const v = cam.worldView;
        let x;
        let y;
        if (tipo === 'biplano') {
          // O biplano já está no campo de pouso: dá a partida.
          const b = this.biplanos.find((bb) => bb.vivo && bb.estado === 'pousado');
          if (b) {
            b.partir();
            onda.vivos.push(b);
          }
          onda.faltam--;
          return;
        }
        if (tipo === 'caminhao' || tipo === 'blindado' || tipo === 'trem') {
          this.chegarVeiculo(tipo, lado, opcoes || {}, onda);
          onda.faltam--;
          return;
        }
        const porta = typeof lado === 'string' && lado.startsWith('porta:');
        if (porta) {
          // Sai pela porta de uma casa, da capela ou de uma barraca: começa atrás da parede.
          const px = Number(lado.slice(6));
          const inimigo = this.adicionarInimigo(px, this.chaoAbaixo(px, 120), tipo, opcoes || {});
          inimigo.virar(this.jogador.x > px ? 1 : -1);
          inimigo.setDepth(4);
          this.time.delayedCall(420, () => inimigo.setDepth(9));
          onda.vivos.push(inimigo);
          onda.faltam--;
          return;
        }
        const salta = typeof lado === 'string' && lado.startsWith('salta:');
        if (salta) {
          // Sai de um esconderijo (buraco, sacos de areia, atrás do lajedo) num pulo.
          x = Number(lado.slice(6));
          y = this.chaoAbaixo(x, 60);
        } else if (lado === 'ceu') {
          x = Phaser.Math.Between(Math.round(v.x + 60), Math.round(v.right - 40));
          y = -30;
        } else {
          x = lado === 'esq' ? v.x - 18 : v.right + 18;
          y = this.chaoAbaixo(x, 60);
        }
        const inimigo = this.adicionarInimigo(x, y, tipo, opcoes || {});
        if (salta) {
          const dir = this.jogador.x > x ? 1 : -1;
          inimigo.virar(dir);
          inimigo.setDepth(4); // começa escondido atrás do cenário
          inimigo.body.reset(x, y - 2);
          inimigo.body.setVelocity(dir * 55, -290);
          inimigo.caindo = true;
          inimigo.saindo = true;
          this.efeitos.poeira(x, y, 12);
          this.efeitos.detritoEm.explode(8, x, y - 4);
          this.time.delayedCall(260, () => inimigo.setDepth(9));
        } else if (lado === 'ceu') inimigo.caindo = true;
        else inimigo.virar(lado === 'esq' ? 1 : -1);
        onda.vivos.push(inimigo);
        onda.faltam--;
      });
    }
  }

  // Chefe chegando: a música corta, o chão treme cada vez mais, poeira cai do alto,
  // pedrinhas pulam no chão e entra a faixa com o nome dele. Depois solta a onda.
  entradaChefe(chefe, aoFim) {
    const cam = this.cameras.main;
    const ef = this.efeitos;
    pararMusica();
    som('ronco');
    let k = 0;
    this.time.addEvent({
      delay: 110, repeat: 15, callback: () => {
        k++;
        ef.tremer(0.0015 + k * 0.0005, 110);
        const v = cam.worldView;
        ef.detritoEm.explode(1, v.x + Phaser.Math.Between(10, v.width - 10), v.y + 4);
        if (k % 2) ef.poeira(v.x + Phaser.Math.Between(10, v.width - 10), 194, 2);
      },
    });
    if (chefe.sub) {
      this.time.delayedCall(500, () => som('engasgo'));
      this.time.delayedCall(1100, () => som('engasgo'));
    } else {
      this.time.delayedCall(600, () => som('apito'));
    }
    this.time.delayedCall(1500, () => {
      tocarMusica('chefe');
      this.faixaChefe(chefe);
    });
    this.time.delayedCall(chefe.sub ? 2600 : 3000, aoFim);
  }

  // Faixa do chefe atravessando a tela (como as do Metal Slug): barras vermelhas com o nome.
  faixaChefe(chefe) {
    const y = 104 + DY / 2;
    som('faixa');
    const cor = chefe.sub ? 0x6e1e1e : 0x8a1414;
    const barra = this.add.rectangle(-LARGURA, y, LARGURA, 46, cor, 0.9).setOrigin(0, 0.5).setScrollFactor(0).setDepth(41)
      .setStrokeStyle(2, 0x0e0d14);
    const filete = this.add.rectangle(LARGURA * 2, y + 16, LARGURA, 3, 0xe0b040).setOrigin(0, 0.5).setScrollFactor(0).setDepth(42);
    const rotulo = this.add.text(LARGURA / 2, y - 14, chefe.sub ? 'SUBCHEFE' : 'CHEFE', estiloTexto(hex('amarelo_claro'), 8))
      .setOrigin(0.5).setScrollFactor(0).setDepth(43).setAlpha(0);
    const nome = this.add.text(LARGURA / 2, y + 1, chefe.nome, estiloTexto(hex('branco'), 16)).setOrigin(0.5).setScrollFactor(0).setDepth(43)
      .setAlpha(0).setScale(2);
    const titulo = this.add.text(LARGURA / 2, y + 26, chefe.titulo, estiloTexto(hex('amarelo_fogo'), 8)).setOrigin(0.5)
      .setScrollFactor(0).setDepth(43).setAlpha(0);
    this.tweens.add({ targets: barra, x: 0, duration: 220, ease: 'Cubic.easeOut' });
    this.tweens.add({ targets: filete, x: 0, duration: 260, ease: 'Cubic.easeOut' });
    this.tweens.add({ targets: [rotulo, titulo], alpha: 1, delay: 200, duration: 150 });
    this.tweens.add({ targets: nome, alpha: 1, scale: 1, delay: 220, duration: 200, ease: 'Back.easeOut',
      onComplete: () => this.efeitos.tremer(0.006, 140) });
    this.time.delayedCall(1700, () => {
      this.tweens.add({ targets: [barra, filete], x: LARGURA, duration: 220, ease: 'Cubic.easeIn' });
      this.tweens.add({ targets: [rotulo, nome, titulo], alpha: 0, duration: 160,
        onComplete: () => [barra, filete, rotulo, nome, titulo].forEach((o) => o.destroy()) });
    });
  }

  ondaAcabou(onda) {
    return onda.faltam === 0 && onda.vivos.every((i) => !i.vivo);
  }

  terminarOnda(onda) {
    onda.estado = 'feita';
    // Depois do subchefe a música da fase volta.
    if (onda.chefe && onda.chefe.sub) {
      tocarMusica('caatinga');
      this.mostrar('MUITO BEM!', '', 1200);
    }
    this.tempo = TEMPO;
    this.onda = null;
    // Solta a câmera sem deixar voltar para trás (ela segue o Lampião suave, sem pulo).
    this.minX = Math.max(this.minX, Math.floor(this.cameras.main.scrollX));
    this.cameras.main.setBounds(this.minX, -DY, this.larguraMundo - this.minX, ALTURA);
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
    tocarMusica('derrota');
    return true;
  }

  atualizarContinuar(t) {
    const c = this.controles;
    if (c.apertou('confirmar') || c.apertou('atirar') || c.apertou('pular')) {
      this.pausado = false;
      this.aviso.setVisible(false);
      this.subaviso.setVisible(false);
      this.jogador.continuar();
      tocarMusica(this.onda && this.onda.chefe ? 'chefe' : 'caatinga');
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

  // Fim da missão: total de pontos e bônus de reféns, contando na tela.
  contarPontos() {
    const bonus = this.refensSalvos * 1000;
    this.mostrar(`${this.missao} CUMPRIDA!`, '', 0);
    tocarMusica('vitoria');
    // Faixa escura atrás do placar para ler bem sobre o cenário.
    const faixa = this.add.rectangle(LARGURA / 2, ALTURA / 2 + 10, 340, 250, 0x0e0d14, 0.7).setScrollFactor(0).setDepth(39)
      .setStrokeStyle(1, 0xd8c8a0, 0.6).setAlpha(0);
    this.tweens.add({ targets: faixa, alpha: 1, duration: 300 });
    const linhas = [
      `PONTOS ${this.pontos}`,
      `REFÉNS SALVOS ${this.refensSalvos} x 1000`,
      `TOTAL ${this.pontos + bonus}`,
    ];
    // Nota: reféns salvos, precisão dos tiros e vidas perdidas viram a medalha do cangaço.
    const totalRefens = Math.max(this.refensSalvos, this.dados.refens.length);
    const precisao = Math.min(1, (this.acertos || 0) / Math.max(1, this.tiros || 0));
    const mortes = this.mortes || 0;
    const nota = (this.refensSalvos / totalRefens) * 40 + precisao * 40 + Math.max(0, 20 - mortes * 7);
    const medalha = nota >= 75 ? 'ouro' : nota >= 50 ? 'prata' : 'bronze';
    linhas.splice(2, 0, `PRECISÃO ${Math.round(precisao * 100)}%   VIDAS PERDIDAS ${mortes}`);
    linhas.forEach((txt, k) => {
      const ultima = k === linhas.length - 1;
      const t = this.add.text(LARGURA / 2, 92 + DY / 2 + k * 14, txt, estiloTexto(hex(ultima ? 'amarelo_fogo' : 'branco')))
        .setOrigin(0.5).setScrollFactor(0).setDepth(40).setAlpha(0);
      this.tweens.add({ targets: t, alpha: 1, delay: 600 + k * 700, duration: 150 });
    });
    const atraso = 600 + linhas.length * 700 + 300;
    const img = this.add.image(LARGURA / 2, 92 + DY / 2 + linhas.length * 14 + 34, `medalha_${medalha}`)
      .setScrollFactor(0).setDepth(40).setScale(4).setAlpha(0);
    const nome = this.add.text(LARGURA / 2, img.y + 42, `MEDALHA DE ${medalha.toUpperCase()} DO CANGAÇO`,
      estiloTexto(hex(medalha === 'ouro' ? 'amarelo_claro' : 'branco'))).setOrigin(0.5).setScrollFactor(0).setDepth(40).setAlpha(0);
    this.tweens.add({ targets: img, alpha: 1, scale: 2, delay: atraso, duration: 260, ease: 'Back.easeOut',
      onComplete: () => this.efeitos.tremer(0.006, 120) });
    this.tweens.add({ targets: nome, alpha: 1, delay: atraso + 300, duration: 200 });
    this.time.delayedCall(atraso + 4200, () => this.scene.start('Menu'));
  }

  // Fim da missão: o Lampião comemora atirando para o alto e os reféns salvos
  // chegam correndo, pulando e batendo continência (o bode Fubá passa de penetra).
  comemorar(aoFim) {
    const j = this.jogador;
    const ef = this.efeitos;
    const cam = this.cameras.main;
    const d = j.direcao || 1;
    if (j.montaria) {
      const jm = j.montaria;
      jm.ang = -Math.PI / 2;
      for (let k = 0; k < 8; k++) {
        this.time.delayedCall(200 + k * 110, () => {
          jm.posicionarMg();
          const [bx, by] = jm.boca();
          ef.disparo(bx, by, -Math.PI / 2, 'normal');
          ef.capsula(jm.mg.x, jm.mg.y, -jm.direcao);
          som('metralha_jumento');
        });
      }
    } else {
      const v = j.visual;
      const y0 = v.y;
      for (let k = 0; k < 3; k++) {
        this.time.delayedCall(200 + k * 520, () => {
          v.setFrame(LAMPIAO.mira_cima);
          this.tweens.add({ targets: v, y: y0 - 16, duration: 170, yoyo: true, ease: 'Quad.easeOut' });
          this.time.delayedCall(170, () => {
            ef.disparo(v.x + d * LAMPIAO.cano.cima[0], y0 - 16 - LAMPIAO.cano.cima[1], -Math.PI / 2, 'normal');
            som('pistola');
          });
        });
      }
      this.time.delayedCall(1900, () => v.setFrame(LAMPIAO.parado));
    }
    // Reféns salvos chegando pela esquerda (até seis).
    const n = Math.min(6, this.refensSalvos);
    for (let i = 0; i < n; i++) {
      const alvoX = j.x - d * (34 + i * 20);
      const lado = alvoX < j.x ? -1 : 1;
      const x0 = lado < 0 ? cam.worldView.x - 20 - i * 26 : cam.worldView.right + 20 + i * 26;
      const r = this.add.sprite(x0, j.pe, 'refem', REFEM.corrida[0]).setDepth(9).setFlipX(lado > 0)
        .setOrigin((lado > 0 ? REFEM.largura - REFEM.peX : REFEM.peX) / REFEM.largura, REFEM.peY / REFEM.altura);
      let passo = i;
      const corre = this.time.addEvent({ delay: 90, loop: true, callback: () => r.setFrame(REFEM.corrida[++passo % 4]) });
      this.tweens.add({
        targets: r, x: alvoX, duration: 900 + i * 160, ease: 'Linear',
        onComplete: () => {
          corre.remove();
          r.setFlipX(j.x < r.x);
          // Pulando de alegria e batendo continência, cada um no seu tempo.
          this.time.addEvent({ delay: 260 + i * 30, loop: true, callback: () => {
            const pula = r.frame.name !== REFEM.continencia;
            r.setFrame(pula ? REFEM.continencia : REFEM.solto);
            if (!pula) this.tweens.add({ targets: r, y: j.pe - 8, duration: 120, yoyo: true });
          } });
          if (i === 0) {
            const viva = this.add.text(r.x, r.y - 40, 'VIVA O CAPITÃO!', estiloTexto(hex('branco'))).setOrigin(0.5).setDepth(31);
            this.tweens.add({ targets: viva, y: viva.y - 10, alpha: 0, delay: 1300, duration: 400, onComplete: () => viva.destroy() });
          }
        },
      });
    }
    // O bode Fubá atravessa a tela berrando.
    this.time.delayedCall(1200, () => {
      if (!this.anims.exists('bode_anda')) {
        this.anims.create({ key: 'bode_anda', frames: this.anims.generateFrameNumbers('bode', { start: 3, end: 6 }), frameRate: 14, repeat: -1 });
      }
      const b = this.add.sprite(cam.worldView.right + 20, j.pe, 'bode', 0).setOrigin(0.5, 1).setDepth(8).setFlipX(true).play('bode_anda');
      const berro = this.add.text(b.x, j.pe - 34, 'BÉÉÉ!', estiloTexto(hex('branco'))).setOrigin(0.5).setDepth(30);
      this.tweens.add({ targets: b, x: cam.worldView.x - 30, duration: 2600, onComplete: () => b.destroy() });
      this.tweens.add({ targets: berro, x: cam.worldView.x - 30, alpha: 0, duration: 2600, onComplete: () => berro.destroy() });
      this.tweens.add({ targets: b, y: j.pe - 5, duration: 130, yoyo: true, repeat: 9 });
    });
    this.time.delayedCall(3300, aoFim);
  }

  // ------------------------------------------------------------ a cada quadro
  atualizarFundo(cam, dt) {
    this.ventoNuvens += dt * 0.004;
    for (const [camada, fator] of this.camadas) camada.tilePositionX = Math.round(cam.scrollX * fator);
    this.nuvens[0].tilePositionX = Math.round(cam.scrollX * this.nuvens[1] + this.ventoNuvens);
  }

  atualizarFase(t, dt) {
    if (this.urubus) this.urubus.atualizar(t, dt);
    if (this.pausado === true) {
      this.atualizarContinuar(t);
      return;
    }
    if (this.pausado) return;
    const cam = this.cameras.main;
    const j = this.jogador;

    // Relógio: zerou, o Lampião perde uma vida e o tempo recomeça.
    if (t > this.proximoTique) {
      this.proximoTique = t + TIQUE;
      if (!j.morto) this.tempo--;
      if (this.tempo <= 0) {
        this.tempo = TEMPO;
        j.morrer(0);
      }
    }
    // A câmera não volta para trás (como no Metal Slug).
    if (!this.onda && cam.scrollX > this.minX) {
      this.minX = Math.floor(cam.scrollX);
      cam.setBounds(this.minX, -DY, this.larguraMundo - this.minX, ALTURA);
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

    if (!this.terminou && j.x >= this.dados.fim && !j.morto && this.ondas.every((o) => o.estado === 'feita')) {
      this.terminou = true;
      this.pausado = 'fim';
      this.quedaDoDisco();
    }
  }

  // Fim da fase: um disco voador passa pegando fogo pelo céu e cai atrás dos morros,
  // com uma explosão ao longe (o primeiro contato que a fase 2 continua).
  quedaDoDisco() {
    const cam = this.cameras.main;
    const ef = this.efeitos;
    const prof = -3.5; // atrás dos morros (f1_meio): some atrás deles ao cair
    const x0 = cam.scrollX + LARGURA + 40;
    const x1 = cam.scrollX + 110;
    const yChao = this.dados.camadas.meio.base - 22;
    const disco = this.add.image(x0, -50, 'disco_voador', 0).setDepth(prof).setScale(0.4).setTint(0xd9a07a);
    const rastro = this.time.addEvent({
      delay: 45, loop: true, callback: () => {
        const fumaca = ef.animar('fumaca', disco.x + 10, disco.y - 2, { profundidade: prof - 0.1, anim: 'fumaca_lenta', escala: 0.7 });
        this.tweens.add({ targets: fumaca, y: fumaca.y - 10, x: fumaca.x + 12, duration: 900 });
        ef.animar('chama', disco.x + Phaser.Math.Between(2, 10), disco.y + Phaser.Math.Between(-3, 2),
          { profundidade: prof + 0.05, escala: 0.55 });
      },
    });
    this.time.delayedCall(500, () => this.mostrar('OLHA LÁ!', '', 1200));
    this.tweens.add({
      targets: disco, x: x1, duration: 2400, ease: 'Linear',
      onUpdate: (tw) => {
        // Cai em curva, cada vez mais rápido, girando torto.
        const k = tw.progress;
        disco.y = -50 + (yChao + 50) * k * k;
        disco.rotation = -0.25 - k * 0.9 + Math.sin(k * 30) * 0.08;
      },
      onComplete: () => {
        rastro.remove();
        disco.setVisible(false);
        // Explosão longe: clarão, bola de fogo pequena e uma coluna de fumaça que fica.
        ef.animar('explosao', x1, yChao - 20, { profundidade: prof });
        this.time.delayedCall(90, () => ef.animar('explosao_p', x1 - 14, yChao - 14, { profundidade: prof }));
        this.time.delayedCall(160, () => ef.animar('explosao_p', x1 + 13, yChao - 24, { profundidade: prof }));
        this.time.delayedCall(260, () => ef.animar('explosao', x1 + 4, yChao - 34, { profundidade: prof }));
        cam.flash(120, 255, 240, 200);
        ef.tremer(0.008, 400);
        this.time.addEvent({
          delay: 110, repeat: 60, callback: () => {
            // Coluna de fumaça preta subindo atrás dos morros.
            const f = ef.animar('fumaca', x1 + Phaser.Math.Between(-6, 6), yChao - 16, { profundidade: prof - 0.1, anim: 'fumaca_lenta', escala: 2 });
            f.setTint(0x4a4440);
            this.tweens.add({ targets: f, y: f.y - 90, x: f.x + 20, duration: 1600 });
          },
        });
        this.time.delayedCall(1400, () => this.comemorar(() => this.contarPontos()));
      },
    });
  }
}
