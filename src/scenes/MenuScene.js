import { LARGURA, ALTURA, DY } from '../config.js';
import { hex, P } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { pedirTelaCheia } from '../escala.js';
import { LAMPIAO, INIMIGOS, VEICULOS } from '../quadros.js';
import { ajustes, salvarAjustes, restaurarPadrao, ACOES_TECLADO, NOMES_ACOES, nomeTecla } from '../ajustes.js';
import { bip, tocarTema, pararTema } from '../som.js';

// Tela de início no jeito do Metal Slug: a cena pintada ocupa a tela, o logo e
// as placas do menu ficam penduradas em correntes na coluna da direita e a
// caixa de baixo explica o item escolhido. As opções usam o mesmo layout.

const COLUNA_X = LARGURA - 86; // centro da coluna da direita
const COLUNA_L = 150;
const PLACA_A = 22;
const CAIXA = { x: 8, y: ALTURA - 50, w: COLUNA_X - COLUNA_L / 2 - 16, h: 42 };

export class MenuScene extends Phaser.Scene {
  constructor() {
    super('Menu');
  }

  create() {
    this.controles = this.game.controles;
    gerarTexturasMenu(this);
    this.montarCena();
    this.montarColuna();
    this.modo = 'principal';
    this.escolha = 0;
    this.esperando = null;
    this.saindo = false;
    this.montarMenu();
    tocarTema();
    const desligar = this.controles.aoMudarFonte(() => this.montarMenu());
    this.events.once('shutdown', () => {
      desligar();
      pararTema();
    });
    this.input.keyboard.on('keydown-P', () => this.modo === 'principal' && this.scene.start('Paleta'));
  }

  // ------------------------------------------------------------ cena pintada
  // Pôr do sol no sertão: o disco paira com o raio aceso, o carro blindado da
  // Volante avança e o Lampião, grandão em primeiro plano, mete bala.
  montarCena() {
    this.add.image(0, 0, 'ceu_titulo').setOrigin(0);
    const faixa = (chave, y, tinta, x = 0) => this.add.tileSprite(x, y, LARGURA, this.textures.get(chave).source[0].height, chave)
      .setOrigin(0).setTint(tinta);
    this.nuvens = faixa('nuvens', 4, P.rosa_poeira);
    this.nuvens2 = faixa('nuvens', 40, P.lilas_claro);
    this.nuvens2.tilePositionX = 160;
    // Chão um pouco acima da caixa de descrição, para os personagens aparecerem inteiros.
    const chao = CAIXA.y - 6;
    const sobe = chao - (194 + DY);
    faixa('serras', DY - 20 + sobe, P.roxo);
    faixa('paredoes', 70 + DY + sobe, P.rosa_poeira).tilePositionX = 90;
    faixa('planicie', 168 + DY + sobe, P.laranja_fogo);
    faixa('caatinga', 122 + DY + sobe, P.lilas).tilePositionX = 30;
    this.add.tileSprite(0, chao - 2, LARGURA, 24, 'chao').setOrigin(0);
    this.add.rectangle(0, chao + 22, LARGURA, ALTURA, P.terra_escura).setOrigin(0);

    // Disco com o raio puxando um bode.
    this.disco = this.add.sprite(170, 62, 'disco_voador', 0);
    this.feixe = this.add.image(170, 84, 'feixe', 0).setOrigin(0.5, 0).setAlpha(0.45);
    this.feixe.setCrop(0, 0, 14, chao - 84 - 14);
    this.chao = chao;
    this.bode = this.add.image(170, chao - 44, 'bode', 2).setOrigin(0.5, 1);
    // Blindado avançando com soldados atrás.
    const qb = VEICULOS.blindado;
    this.blindado = this.add.sprite(300, chao + 1, 'blindado', 0).setOrigin(0.5, 1).setFlipX(true);
    for (const [x, tipo] of [[372, 'volante'], [348, 'granadeiro']]) {
      const q = INIMIGOS[tipo];
      this.add.image(x, chao, tipo, q.parado).setFlipX(true).setOrigin((q.largura - q.peX) / q.largura, q.peY / q.altura);
    }
    this.qb = qb;
    // Lampião grande no primeiro plano (escala inteira, pixel nítido).
    this.lampiao = this.add.sprite(78, chao + 2, 'lampiao', LAMPIAO.atirando).setScale(2)
      .setOrigin(LAMPIAO.peX / LAMPIAO.largura, LAMPIAO.peY / LAMPIAO.altura);
    if (!this.anims.exists('explosao')) {
      for (const [k, n, fps] of [['explosao', 8, 20], ['clarao', 3, 50], ['fumaca', 4, 14]]) {
        this.anims.create({ key: k, frames: this.anims.generateFrameNumbers(k, { start: 0, end: n - 1 }), frameRate: fps });
      }
    }
    this.clarao = this.add.sprite(0, 0, 'clarao', 0).setScale(2).setVisible(false).setOrigin(0.05, 0.5);
    this.explosoes = [0, 1].map(() => this.add.sprite(0, 0, 'explosao', 0).setVisible(false));
    this.time.addEvent({ delay: 900, loop: true, callback: () => this.disparar() });
    this.time.addEvent({ delay: 1700, loop: true, callback: () => this.explodirAoLonge() });
  }

  disparar() {
    // Clarão no cano da pistola do Lampião.
    this.clarao.setPosition(this.lampiao.x + 30, this.lampiao.y - 46).setVisible(true).play('clarao');
    this.clarao.once('animationcomplete', () => this.clarao.setVisible(false));
    this.lampiao.setFrame(LAMPIAO.atirando);
    this.time.delayedCall(140, () => this.lampiao.setFrame(LAMPIAO.parado));
  }

  explodirAoLonge() {
    const e = this.explosoes.find((s) => !s.visible) || this.explosoes[0];
    e.setPosition(Phaser.Math.Between(230, 380), this.chao - 8 - Phaser.Math.Between(0, 30)).setVisible(true).play('explosao');
    e.once('animationcomplete', () => e.setVisible(false));
  }

  // ------------------------------------------------------------ coluna do menu
  montarColuna() {
    const x0 = COLUNA_X - COLUNA_L / 2;
    // Correntes dos dois lados da coluna, de cima a baixo.
    for (const cx of [x0 + 6, x0 + COLUNA_L - 6]) {
      this.add.tileSprite(cx, 0, 6, ALTURA, 'corrente').setOrigin(0.5, 0);
    }
    // Logo: "A" pequeno em cima e INVASÃO em letras de fogo com contorno grosso.
    const logo = this.add.image(COLUNA_X, 8, 'placa_logo').setOrigin(0.5, 0);
    this.add.text(COLUNA_X, 18, 'SERTÃO 1936', estiloTexto(hex('areia_clara'))).setOrigin(0.5);
    this.add.text(COLUNA_X, 36, 'A', fogo(this, 16)).setOrigin(0.5);
    this.add.text(COLUNA_X, 56, 'INVASÃO', fogo(this, 16)).setOrigin(0.5);
    this.tweens.add({ targets: logo, y: 9, duration: 1400, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    // Placas (reaproveitadas entre os menus).
    this.placas = [];
    for (let k = 0; k < 8; k++) {
      const img = this.add.image(COLUNA_X, 0, 'placa').setInteractive({ useHandCursor: true });
      const txt = this.add.text(COLUNA_X, 0, '', estiloTexto(hex('branco'))).setOrigin(0.5);
      img.on('pointerdown', (p, lx) => this.tocarPlaca(k, lx));
      this.placas.push({ img, txt });
    }
    // Caixa de descrição embaixo, à esquerda.
    this.add.image(CAIXA.x, CAIXA.y, 'caixa_desc').setOrigin(0);
    this.descricao = this.add.text(CAIXA.x + CAIXA.w / 2, CAIXA.y + CAIXA.h / 2, '', {
      ...estiloTexto(hex('branco')), align: 'center', lineSpacing: 4, wordWrap: { width: CAIXA.w - 24 },
    }).setOrigin(0.5);
    // Plaquinha de título dos submenus, pendurada no alto à esquerda.
    this.cabecalho = this.add.image(CAIXA.x + CAIXA.w / 2, 4, 'placa').setOrigin(0.5, 0).setVisible(false);
    this.cabecalhoTxt = this.add.text(this.cabecalho.x, 4 + PLACA_A / 2, '', estiloTexto(hex('branco'))).setOrigin(0.5).setVisible(false);
    this.versao = this.add.text(4, ALTURA - 4, '', estiloTexto(hex('areia_clara'))).setOrigin(0, 1).setAlpha(0);
  }

  itens() {
    const toque = this.controles.fonte === 'toque';
    if (this.modo === 'principal') {
      return [
        { texto: 'MISSÃO 1', desc: 'Caatinga, 1936. Lampião contra a Volante, da vila de taipa ao acampamento.', id: 'Fase1' },
        { texto: 'CAMPO DE TREINO', desc: 'Todas as armas, inimigos e veículos para treinar. Tudo volta.', id: 'Campo' },
        { texto: 'COOP ONLINE', desc: 'Lampião e Maria Bonita em dois aparelhos. Em breve.', id: 'coop', apagado: true },
        { texto: 'OPÇÕES', desc: 'Volume dos efeitos e da música, tremida de tela e teclas.', id: 'opcoes' },
      ];
    }
    if (this.modo === 'opcoes') {
      const barra = (v) => `${v}`.padStart(2, ' ');
      const lista = [
        { texto: `EFEITOS: ${barra(ajustes.efeitos)}`, desc: toque ? 'Toque na esquerda da placa para baixar e na direita para subir.' : 'Volume dos efeitos. Use as setas para os lados.', id: 'efeitos' },
        { texto: `MÚSICA: ${barra(ajustes.musica)}`, desc: 'Volume da música.', id: 'musica' },
        { texto: `TREMIDA: ${ajustes.tremida ? 'SIM' : 'NÃO'}`, desc: 'A tela treme nas explosões e nos tiros fortes.', id: 'tremida' },
      ];
      if (!toque) lista.push({ texto: 'TECLAS', desc: 'Troque a tecla de cada ação do teclado.', id: 'teclas' });
      lista.push({ texto: 'RESTAURAR', desc: 'Volta tudo para o padrão.', id: 'padrao' });
      lista.push({ texto: 'VOLTAR', desc: '', id: 'voltar', grande: true });
      return lista;
    }
    return [
      ...ACOES_TECLADO.map((a) => ({
        texto: `${NOMES_ACOES[a].split(' ')[0]}: ${this.esperando === a ? '...' : nomeTecla(ajustes.teclas[a])}`,
        desc: this.esperando === a ? 'Aperte a nova tecla. ESC cancela.' : `Tecla de ${NOMES_ACOES[a].toLowerCase()}. ENTER para trocar.`,
        acao: a,
      })),
      { texto: 'VOLTAR', desc: '', id: 'voltar', grande: true },
    ];
  }

  montarMenu() {
    const itens = this.itens();
    const topo = 84;
    const passo = Math.min(28, Math.floor((ALTURA - topo - 8) / itens.length));
    this.placas.forEach((p, k) => {
      const it = itens[k];
      p.img.setVisible(!!it).setActive(!!it);
      p.txt.setVisible(!!it);
      if (!it) return;
      // VOLTAR fica separado embaixo, como no Metal Slug.
      const y = it.grande ? ALTURA - PLACA_A / 2 - 6 : topo + k * passo + PLACA_A / 2;
      const sel = k === this.escolha;
      p.img.setPosition(COLUNA_X, y).setTexture(sel ? 'placa_sel' : 'placa');
      let cor = sel ? hex('amarelo_fogo') : hex('branco');
      if (it.apagado) cor = sel ? hex('ouro_escuro') : hex('cinza');
      p.txt.setPosition(COLUNA_X, y).setText(it.texto).setColor(cor);
    });
    const it = itens[this.escolha];
    this.descricao.setText(it ? it.desc : '');
    const titulo = { opcoes: 'OPÇÕES', teclas: 'TECLAS' }[this.modo];
    this.cabecalho.setVisible(!!titulo);
    this.cabecalhoTxt.setVisible(!!titulo).setText(titulo || '');
  }

  // ------------------------------------------------------------ ações
  mover(d) {
    const n = this.itens().length;
    this.escolha = (this.escolha + d + n) % n;
    bip('mover');
    this.montarMenu();
  }

  ajustar(id, lado) {
    if (id === 'efeitos') ajustes.efeitos = Phaser.Math.Clamp(ajustes.efeitos + lado, 0, 10);
    else if (id === 'musica') ajustes.musica = Phaser.Math.Clamp(ajustes.musica + lado, 0, 10);
    else if (id === 'tremida') ajustes.tremida = !ajustes.tremida;
    else return false;
    salvarAjustes();
    bip('mover');
    if (id === 'tremida' && ajustes.tremida) this.cameras.main.shake(160, 0.01);
    this.montarMenu();
    return true;
  }

  escolher() {
    const it = this.itens()[this.escolha];
    if (!it || this.saindo) return;
    if (it.apagado) {
      bip('erro');
      return;
    }
    if (it.acao) {
      this.trocarTecla(it.acao);
      return;
    }
    if (it.id === 'Fase1' || it.id === 'Campo') {
      this.saindo = true;
      bip('confirmar');
      pedirTelaCheia(this.game);
      this.cameras.main.fadeOut(250, 0, 0, 0);
      this.time.delayedCall(260, () => this.scene.start(it.id));
      return;
    }
    if (it.id === 'opcoes') this.trocarModo('opcoes', 0);
    else if (it.id === 'teclas') this.trocarModo('teclas', 0);
    else if (it.id === 'padrao') {
      restaurarPadrao();
      bip('confirmar');
      this.montarMenu();
    } else if (it.id === 'voltar') this.voltar();
    else this.ajustar(it.id, 1);
  }

  trocarModo(modo, escolha) {
    bip(modo === 'principal' ? 'voltar' : 'confirmar');
    this.modo = modo;
    this.escolha = escolha;
    this.montarMenu();
  }

  voltar() {
    if (this.modo === 'teclas') this.trocarModo('opcoes', 3);
    else if (this.modo === 'opcoes') this.trocarModo('principal', 3);
  }

  // Espera a próxima tecla; se ela já for de outra ação, as duas trocam de lugar.
  trocarTecla(acao) {
    this.esperando = acao;
    bip('mover');
    this.montarMenu();
    this.controles.capturarTecla((codigo) => {
      this.esperando = null;
      if (codigo === 'Escape' || codigo === 'Enter') {
        bip('voltar');
      } else {
        const dona = ACOES_TECLADO.find((a) => ajustes.teclas[a] === codigo);
        if (dona && dona !== acao) ajustes.teclas[dona] = ajustes.teclas[acao];
        ajustes.teclas[acao] = codigo;
        salvarAjustes();
        bip('confirmar');
      }
      this.montarMenu();
    });
  }

  tocarPlaca(k, lx) {
    if (this.esperando || this.saindo) return;
    const it = this.itens()[k];
    if (!it) return;
    this.escolha = k;
    // Nas opções com valor, metade esquerda da placa baixa e a direita sobe.
    if (['efeitos', 'musica', 'tremida'].includes(it.id)) this.ajustar(it.id, lx < COLUNA_L / 2 ? -1 : 1);
    else this.escolher();
    this.montarMenu();
  }

  update(t, dt) {
    this.nuvens.tilePositionX += dt * 0.004;
    this.nuvens2.tilePositionX += dt * 0.007;
    this.disco.y = 62 + Math.sin(t / 500) * 2;
    this.disco.setFrame(Math.floor(t / 150) % 2);
    this.feixe.setFrame(Math.floor(t / 100) % 2);
    this.bode.y = this.chao - 44 + Math.sin(t / 300) * 3;
    this.blindado.setFrame(Math.floor(t / 120) % 2);
    const c = this.controles;
    c.atualizar();
    if (this.esperando || this.saindo) return;
    if (c.apertou('baixo')) this.mover(1);
    else if (c.apertou('cima')) this.mover(-1);
    const lado = c.lado();
    const it = this.itens()[this.escolha];
    if (lado && it) this.ajustar(it.id, lado);
    if (c.apertou('confirmar') || c.apertou('atirar')) this.escolher();
    else if ((c.apertou('voltar') || c.apertou('granada')) && this.modo !== 'principal') this.voltar();
  }
}

// Letras de fogo do logo: degradê amarelo -> laranja -> vermelho, contorno escuro grosso e sombra.
function fogo(cena, tamanho) {
  return {
    fontFamily: '"Press Start 2P", monospace', fontSize: `${tamanho}px`, color: hex('laranja_fogo'),
    stroke: hex('marrom_noite'), strokeThickness: 4, resolution: 1,
    shadow: { offsetX: 2, offsetY: 2, color: '#0e0d14', blur: 0, fill: true, stroke: true },
  };
}

// Texturas do menu desenhadas em código: céu do pôr do sol, corrente, placas e caixa.
function gerarTexturasMenu(cena) {
  if (cena.textures.exists('placa')) return;
  const cor = (n) => hex(n);
  const tela = (chave, w, h, desenhar) => {
    const tex = cena.textures.createCanvas(chave, w, h);
    const ctx = tex.getContext();
    ctx.imageSmoothingEnabled = false;
    const px = (x, y, c, ww = 1, hh = 1) => { ctx.fillStyle = cor(c); ctx.fillRect(x, y, ww, hh); };
    desenhar(px, ctx);
    tex.refresh();
  };
  // Céu do pôr do sol em faixas com pontilhado entre elas (sem degradê liso).
  const faixas = ['roxo_escuro', 'roxo', 'lilas', 'rosa_poeira', 'laranja_escuro', 'laranja_fogo', 'amarelo_fogo', 'amarelo_claro'];
  const bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]];
  tela('ceu_titulo', LARGURA, ALTURA, (px) => {
    const alto = ALTURA - 40;
    for (let y = 0; y < ALTURA; y++) {
      const f = Math.min(faixas.length - 1.001, (y / alto) ** 1.25 * (faixas.length - 1));
      const i = Math.floor(f);
      const frac = f - i;
      for (let x = 0; x < LARGURA; x++) {
        px(x, y, frac * 16 > bayer[y % 4][x % 4] ? faixas[i + 1] : faixas[i]);
      }
    }
  });
  // Corrente: elos alternando de frente e de lado.
  tela('corrente', 6, 10, (px) => {
    px(1, 0, 'sombra', 4, 6); px(2, 1, 'cinza_medio', 2, 4); px(2, 2, 'sombra', 2, 2); px(1, 0, 'cinza', 1, 1);
    px(2, 5, 'sombra', 2, 5); px(2, 6, 'cinza', 2, 3); px(2, 6, 'cinza_luz', 1, 1);
  });
  // Placa: chapa escura com bisel, cantos de ferro rebitados e argolas da corrente.
  const placa = (chave, borda, brilho) => tela(chave, COLUNA_L, PLACA_A, (px) => {
    const w = COLUNA_L;
    const h = PLACA_A;
    px(0, 0, 'preto', w, h);
    px(1, 1, borda, w - 2, h - 2);
    px(2, 2, 'marrom_noite', w - 4, h - 4);
    px(3, 3, 'sombra', w - 6, h - 6);
    px(3, 3, brilho, w - 6, 1);
    px(3, h - 4, 'preto', w - 6, 1);
    for (const x of [1, w - 9]) {
      px(x, 1, 'cinza_escuro', 8, h - 2);
      px(x + 1, 2, 'cinza_medio', 6, h - 4);
      px(x + 1, 2, 'cinza_luz', 6, 1);
      px(x + 3, 5, 'cinza_claro', 2, 2); px(x + 4, 6, 'sombra', 1, 1);
      px(x + 3, h - 8, 'cinza_claro', 2, 2); px(x + 4, h - 7, 'sombra', 1, 1);
    }
  });
  placa('placa', 'cinza_escuro', 'sombra_media');
  placa('placa_sel', 'laranja_escuro', 'laranja_escuro');
  // Placa grande do logo atrás das letras.
  tela('placa_logo', COLUNA_L, 64, (px) => {
    px(0, 0, 'preto', COLUNA_L, 64);
    px(1, 1, 'cinza_escuro', COLUNA_L - 2, 62);
    px(3, 3, 'marrom_noite', COLUNA_L - 6, 58);
    px(4, 4, 'roxo_escuro', COLUNA_L - 8, 56);
    for (const [x, y] of [[5, 5], [COLUNA_L - 8, 5], [5, 56], [COLUNA_L - 8, 56]]) {
      px(x, y, 'cinza_claro', 2, 2); px(x + 1, y + 1, 'sombra', 1, 1);
    }
  });
  // Caixa de descrição com moldura de metal e rebites.
  tela('caixa_desc', CAIXA.w, CAIXA.h, (px) => {
    const { w, h } = CAIXA;
    px(0, 0, 'preto', w, h);
    px(1, 1, 'cinza_medio', w - 2, h - 2);
    px(1, 1, 'cinza_luz', w - 2, 1);
    px(1, 1, 'cinza_luz', 1, h - 2);
    px(4, 4, 'preto', w - 8, h - 8);
    px(5, 5, 'marrom_noite', w - 10, h - 10);
    px(5, 5, 'sombra', w - 10, h - 10);
    for (const [x, y] of [[2, 2], [w - 4, 2], [2, h - 4], [w - 4, h - 4]]) {
      px(x, y, 'cinza_claro', 2, 2); px(x + 1, y + 1, 'sombra', 1, 1);
    }
  });
}
