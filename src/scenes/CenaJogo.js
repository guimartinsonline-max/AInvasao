import { LARGURA, ALTURA, DY } from '../config.js';
import { Efeitos } from '../efeitos.js';
import { Jogador } from '../objetos/Jogador.js';
import { Inimigo } from '../objetos/Inimigo.js';
import { BalasInimigas } from '../objetos/BalasInimigas.js';
import { Balas } from '../objetos/Balas.js';
import { ARMAS, PREMIOS } from '../armas.js';
import { Refem } from '../objetos/Refem.js';
import { Itens } from '../objetos/Itens.js';
import { Caixotes } from '../objetos/Caixotes.js';
import { Caminhao, Blindado } from '../objetos/Veiculos.js';
import { estiloTexto } from '../texto.js';
import { hex } from '../paleta.js';

export const CHAO_Y = 192;
const RAIO_GRANADA = 44;

// Base das cenas jogáveis (campo de treino e fases): Lampião, armas, granadas,
// inimigos, reféns, itens, caixotes, efeitos e câmera.
// A cena filha define: configurar() -> { largura, inicio }, criarFundo(), montarCenario(),
// povoar(), e pode usar atualizarFundo(cam, dt) e atualizarFase(t, dt).
export class CenaJogo extends Phaser.Scene {
  create() {
    this.controles = this.game.controles;
    const { largura, inicio } = this.configurar();
    this.larguraMundo = largura;
    // A cena é reaproveitada ao recomeçar: tira os ouvintes de explosão da vez anterior.
    this.events.off('explosao');
    this.physics.world.setBounds(0, -200, largura, ALTURA + 400);
    this.solidos = this.physics.add.staticGroup();

    this.criarFundo();
    this.efeitos = new Efeitos(this, this.solidos);
    this.alvos = this.physics.add.group({ runChildUpdate: false });
    this.montarCenario();
    if (!this.caixotes) this.caixotes = new Caixotes(this, []);
    // Quem voa (o disco) não colide com o chão.
    this.physics.add.collider(this.alvos, this.solidos, null, (a) => !a.voa);

    // Reféns escondidos em caixotes (pool); só aparecem quando um caixote quebra.
    this.refensExtras = [];
    for (let k = 0; k < 2; k++) {
      const r = new Refem(this, -200, CHAO_Y);
      r.temporario = true;
      this.alvos.add(r);
      r.esconder();
      this.refensExtras.push(r);
    }

    this.balas = new Balas(this, this.solidos, this.alvos, (alvo, bala) => {
      const tipo = bala.tipo;
      if (alvo.bloqueia && alvo.bloqueia(bala.body.velocity.x)) {
        alvo.danoEscudo(Math.max(1, tipo.dano), bala.x, bala.y);
        if (tipo.atravessa) this.balas.recolher(bala);
        return;
      }
      alvo.levarDano(tipo.dano * (bala.forca || 1), bala.x, false, tipo.morte, tipo.queima);
      if (tipo.impacto) this.efeitos.impacto(bala.x, bala.y, tipo.impacto);
      if (tipo.pausa) this.efeitos.parar(tipo.pausa);
    }, (caixote, bala) => caixote.levarDano(bala.tipo.dano || 1));

    // Granada como a do Metal Slug: arco, um quique e explode no segundo toque
    // no chão ou quando encosta num inimigo.
    this.granadas = this.physics.add.group({ defaultKey: 'granada_g', maxSize: 6 });
    this.physics.add.collider(this.granadas, this.solidos, (g) => {
      if (!g.active || !g.body.blocked.down || this.time.now - g.ultimoQuique < 150) return;
      g.ultimoQuique = this.time.now;
      g.quiques++;
      this.efeitos.poeira(g.x, g.y + 4, 3);
      if (g.quiques >= 2) this.explodirGranada(g);
    });
    this.physics.add.overlap(this.granadas, this.alvos, (g, alvo) => {
      if (g.active && alvo.vivo) this.explodirGranada(g);
    });

    this.jogador = new Jogador(this, inicio.x, inicio.y);
    this.physics.add.collider(this.jogador.corpo, this.solidos);
    this.balasInimigas = new BalasInimigas(this, this.solidos, this.jogador);
    this.itens = new Itens(this, this.solidos, this.jogador, (arma, item) => this.pegarItem(arma, item));
    this.corte = this.add.image(0, 0, 'corte').setVisible(false).setDepth(20);

    const cam = this.cameras.main;
    cam.setBounds(0, -DY, largura, ALTURA);
    cam.startFollow(this.jogador.corpo, true, 0.12, 0.12);
    cam.setDeadzone(24, ALTURA);
    this.olhar = 0;

    this.povoar();

    this.scene.launch('Hud', { jogador: this.jogador, cena: this.scene.key });
    this.events.once('shutdown', () => this.scene.stop('Hud'));
  }

  solido(x, y, w, h, umLado = false) {
    const r = this.add.zone(x, y, w, h).setOrigin(0);
    this.solidos.add(r);
    if (umLado) {
      // Plataforma que dá para atravessar pulando por baixo.
      r.body.checkCollision.down = false;
      r.body.checkCollision.left = false;
      r.body.checkCollision.right = false;
    }
    return r;
  }

  adicionarInimigo(x, y, tipo, opcoes = {}) {
    const inimigo = new Inimigo(this, x, y, tipo, opcoes);
    inimigo.setDepth(9);
    this.alvos.add(inimigo);
    inimigo.ajustarCorpo();
    return inimigo;
  }

  // Veículo entra pela borda da tela (caminhão traz soldados; blindado luta).
  // Numa onda, os soldados que descem entram na conta dela.
  chegarVeiculo(tipo, lado, opcoes = {}, onda = null) {
    const v = this.cameras.main.worldView;
    const direcao = lado === 'esq' ? 1 : -1;
    const x = lado === 'esq' ? v.x - 80 : v.right + 80;
    const para = opcoes.para ?? (lado === 'esq' ? v.x + 110 : v.right - 120);
    let veiculo;
    if (tipo === 'caminhao') {
      const soldados = opcoes.soldados || ['volante', 'volante', 'volante'];
      if (onda) onda.faltam += soldados.length;
      veiculo = new Caminhao(this, x, this.chaoAbaixo(x, 60), {
        direcao, para, soldados,
        aoSoltar: (inimigo) => { if (onda) { onda.vivos.push(inimigo); onda.faltam--; } },
        aoPerder: () => { if (onda) onda.faltam--; },
      });
    } else {
      veiculo = new Blindado(this, x, this.chaoAbaixo(x, 60), { direcao, para });
      this.mostrar?.('CUIDADO!', 'CARRO BLINDADO', 1600);
    }
    this.alvos.add(veiculo);
    veiculo.body.allowGravity = false;
    if (onda) onda.vivos.push(veiculo);
    return veiculo;
  }

  alvoProximo(x, y, direcao, alcance) {
    for (const alvo of [...this.alvos.getChildren(), ...this.caixotes.vivos()]) {
      if (!alvo.vivo) continue;
      const dx = (alvo.x - x) * direcao;
      if (dx > -6 && dx < alcance && Math.abs(alvo.y - 18 - y) < 22) return alvo;
    }
    return null;
  }

  peixeirada(x, y, direcao, alvo) {
    // Arco largo da peixeira, desenhado quadro a quadro, logo depois de levantar a faca.
    this.time.delayedCall(55, () => this.efeitos.animar('corte_arco', x + direcao * 2, y, { espelhar: direcao < 0, profundidade: 20 }));
    // A peixeirada mata na hora (como a faca do Metal Slug) e racha o escudo de uma vez.
    if (alvo.vidaEscudo > 0) alvo.danoEscudo(alvo.vidaEscudo, alvo.x, alvo.y - 20);
    if (alvo.zona) alvo.levarDano(99); // caixote ou barril
    else alvo.levarDano(999, this.jogador.x, true, 'facada');
    this.efeitos.parar(70);
    this.efeitos.faisca(alvo.x, alvo.y - 20, 6);
    this.efeitos.tremer(0.004, 80);
  }

  lancarGranada(x, y, direcao, vx) {
    const g = this.granadas.get(x, y, 'granada_g');
    if (!g) return;
    g.setActive(true).setVisible(true).setRotation(0).setDepth(14).setFlipX(direcao < 0);
    g.body.reset(x, y);
    g.body.setSize(7, 7).setOffset(2, 2);
    g.body.setBounce(0.45).setDrag(30, 0);
    g.body.setVelocity(direcao * 150 + vx * 0.4, -230);
    g.quiques = 0;
    g.ultimoQuique = 0;
    g.explodeEm = this.time.now + 2500; // segurança, se ficar presa
  }

  explodirGranada(g) {
    const x = g.x;
    const y = g.y;
    g.setActive(false).setVisible(false);
    g.body.stop();
    g.body.reset(-100, -100);
    this.explodir(x, y - 6, RAIO_GRANADA, 10, 1.2);
  }

  // Rajada do bacamarte: cone curto e largo; acerta tudo dentro dele de uma vez.
  rajada(x, y, ang, cfg0, direcao, forca = 1) {
    // Arma grande: rajada maior, mais longa e mais forte.
    const cfg = { ...cfg0, alcance: cfg0.alcance * (forca > 1 ? 1.3 : 1), dano: cfg0.dano * forca };
    this.efeitos.animar('rajada', x, y, { rotacao: ang, origemX: 0.02, profundidade: 20, escala: forca > 1 ? 1.3 : 1 });
    this.efeitos.parar(40);
    const c = Math.cos(ang);
    const s = Math.sin(ang);
    const tg = Math.tan(cfg.abertura);
    for (const alvo of [...this.alvos.getChildren(), ...this.caixotes.vivos()]) {
      if (!alvo.vivo) continue;
      const dx = alvo.x - x;
      const dy = alvo.y - 16 - y;
      const lx = dx * c + dy * s;
      const ly = -dx * s + dy * c;
      if (lx < -6 || lx > cfg.alcance || Math.abs(ly) > 10 + lx * tg) continue;
      if (alvo.bloqueia && alvo.bloqueia(direcao * c || 1)) alvo.danoEscudo(cfg.dano, alvo.x, alvo.y - 16);
      else alvo.levarDano(cfg.dano, x, true, 'arremessa');
      this.efeitos.impacto(alvo.x, alvo.y - 16, 'comum');
    }
  }

  // Explosão com dano em área (granada, rojão, barril).
  explodir(x, y, raio, dano, tamanho = 1) {
    this.efeitos.explosao(x, y, tamanho);
    this.events.emit('explosao', x, y, raio); // cenário vivo: varal, telhados, ponte
    for (const alvo of [...this.alvos.getChildren(), ...this.caixotes.vivos()]) {
      if (alvo.vivo && Phaser.Math.Distance.Between(x, y, alvo.x, alvo.y - 18) < raio) {
        if (alvo.vidaEscudo > 0) alvo.danoEscudo(3, alvo.x, alvo.y - 13);
        alvo.levarDano(dano, x, true);
      }
    }
  }

  pegarItem(arma, item) {
    if (arma.startsWith('comida_')) {
      this.jogador.comer(arma.slice(7), item);
      return;
    }
    this.efeitos.faisca(item.x, item.y - 8, 12);
    if (arma === 'granadas') {
      this.jogador.granadas = Math.min(this.jogador.granadas + 5, 20);
      this.events.emit('arma', 'GRANADAS +5');
      return;
    }
    const grande = this.jogador.trocarArma(arma);
    this.events.emit('arma', (grande ? 'SUPER ' : '') + ARMAS[arma].nome);
  }

  // ------------------------------------------------------------ pontos
  // Pontos ganhos aparecem subindo no lugar (como no Metal Slug).
  pontuar(pontos, x, y) {
    if (!pontos) return;
    this.pontos = (this.pontos || 0) + pontos;
    if (!this.textosPontos) {
      this.textosPontos = [];
      for (let k = 0; k < 8; k++) {
        this.textosPontos.push(this.add.text(0, 0, '', estiloTexto(hex('amarelo_claro'))).setOrigin(0.5).setDepth(31)
          .setVisible(false));
      }
      this.proximoTexto = 0;
    }
    const t = this.textosPontos[this.proximoTexto++ % this.textosPontos.length];
    this.tweens.killTweensOf(t);
    t.setText(`${pontos}`).setPosition(Math.round(x), Math.round(y)).setVisible(true).setAlpha(1);
    this.tweens.add({ targets: t, y: y - 18, alpha: 0, delay: 350, duration: 500, onComplete: () => t.setVisible(false) });
  }

  // Item que sai saltando de um caixote quebrado ou de um refém solto.
  // Comida sorteada: as baratas aparecem mais, a buchada é rara.
  comidaSorteada() {
    const r = Math.random();
    if (r < 0.35) return 'comida_caja';
    if (r < 0.6) return 'comida_rapadura';
    if (r < 0.8) return 'comida_queijo';
    if (r < 0.94) return 'comida_cuscuz';
    return 'comida_buchada';
  }

  soltarItem(x, y, arma) {
    this.itens.colocar(x, y, arma, { pulo: true });
  }

  // Refém amarrado que estava dentro do caixote.
  surpresaRefem(x, pe) {
    const r = this.refensExtras.find((rr) => !rr.visible);
    if (r) r.aparecer(x, pe);
    else this.soltarItem(x, pe - 10, 'granadas');
  }

  // O bode Fubá estava dentro do caixote: sai correndo e berrando.
  surpresaBode(x, pe) {
    const lado = this.jogador.x < x ? 1 : -1;
    const b = this.add.sprite(x, pe, 'bode', 0).setOrigin(0.5, 1).setDepth(8).setFlipX(lado < 0);
    const grito = this.add.text(x, pe - 34, 'BÉÉÉÉ!', estiloTexto(hex('branco'))).setOrigin(0.5).setDepth(30);
    this.tweens.add({ targets: grito, y: pe - 48, alpha: 0, duration: 900, onComplete: () => grito.destroy() });
    this.tweens.add({ targets: b, y: pe - 10, duration: 140, yoyo: true, repeat: 5 });
    this.tweens.add({ targets: b, x: x + lado * 260, duration: 1600, onComplete: () => b.destroy() });
    this.efeitos.poeira(x, pe, 6);
  }

  // Primeira superfície sólida abaixo de (x, y).
  chaoAbaixo(x, y) {
    for (let yy = Math.floor(y); yy < ALTURA; yy++) {
      // O retângulo de teste conta como tocando quando a borda de baixo encosta no sólido.
      if (this.physics.overlapRect(x - 1, yy, 2, 1, false, true).length) return yy + 1;
    }
    return CHAO_Y + 2;
  }

  // No campo de treino tudo volta (inimigos, caixotes, disco); numa fase, não.
  // Armas que caixotes e reféns podem soltar nesta cena.
  get premios() {
    return PREMIOS;
  }

  get tudoVolta() {
    return true;
  }

  update(t, dt) {
    const c = this.controles;
    c.atualizar();
    if (c.apertou('voltar')) {
      this.scene.start('Menu');
      return;
    }
    if (this.pausado) {
      this.atualizarFase(t, dt);
      return;
    }

    if (!this.efeitos.congelado) this.jogador.atualizar(dt, c);
    this.balas.atualizar(dt);
    this.balasInimigas.atualizar();
    this.efeitos.atualizar();
    this.itens.atualizar(t);
    for (const jm of this.jumentos || []) jm.atualizar(t, dt);

    for (const g of this.granadas.getChildren()) {
      if (!g.active) continue;
      // Gira no ar, quadro a quadro.
      if (!g.body.blocked.down) g.setFrame(Math.floor(t / 55) % 4);
      if (t >= g.explodeEm) this.explodirGranada(g);
    }

    // A câmera olha um pouco para onde o Lampião está virado.
    // Suavizações independentes da taxa de quadros (60, 144 ou 240 Hz).
    const cam = this.cameras.main;
    const k = dt / (1000 / 60);
    const lerp = 1 - Math.pow(1 - 0.12, k);
    cam.setLerp(lerp, lerp);
    this.olhar += (this.jogador.direcao * -40 - this.olhar) * (1 - Math.pow(1 - 0.04, k));
    cam.setFollowOffset(Math.round(this.olhar), 0);
    this.atualizarFundo(cam, dt);
    this.atualizarFase(t, dt);
  }

  atualizarFundo() {}

  atualizarFase() {}
}

export { LARGURA, ALTURA, DY };
