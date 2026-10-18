import { hex, P } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { som } from '../som.js';

// Chefe da fase 1: o trem blindado da Volante ("A JARARACA"). Entra pelos
// trilhos, apita e para de frente para o Lampião. Partes que quebram separadas:
// - metralhadoras do limpa-trilhos: avisam e soltam rajada ALTA (agacha) ou BAIXA (pula);
// - chaminé: cospe carvão em brasa em arco;
// - torre da cabine: obus de canhão em arco;
// - vagão de trás: soldados pulam dos sacos de areia.
// Quebradas as metralhadoras e a chaminé, a porta da fornalha abre (ponto fraco)
// e o trem fica bravo: avança e recua. A porta arrebentada explode a caldeira.

export const TREM = {
  loco: { largura: 210, altura: 116 },
  vagao: { largura: 150, altura: 92 },
  // Encaixes das partes na locomotiva (canto de cima à esquerda) e o tamanho de cada uma.
  partes: {
    mg: { x: 2, y: 58, largura: 16, altura: 30, vida: 30, pontos: 1000 },
    chamine: { x: 34, y: 2, largura: 22, altura: 40, vida: 26, pontos: 1000 },
    torre: { x: 156, y: 0, largura: 44, altura: 26, vida: 34, pontos: 1500 },
    porta: { x: 8, y: 46, largura: 24, altura: 30, vida: 40, pontos: 5000 },
  },
};

class Parte extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, trem, nome) {
    const cfg = TREM.partes[nome];
    super(cena, 0, 0, `trem_${nome}`, 0);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.trem = trem;
    this.nome = nome;
    this.cfg = cfg;
    this.setOrigin(0.5, 1).setDepth(9);
    this.body.allowGravity = false;
    this.body.setImmovable(true);
    this.voa = true; // não colide com o chão
    this.vida = cfg.vida;
    this.vivo = true;
    this.persegue = true;
  }

  // Sem chegar no ponto fraco, o tiro só bate na chapa (faísca).
  get vulneravel() {
    return this.nome !== 'porta' || this.trem.portaAberta;
  }

  levarDano(dano, origemX, forte = false, morte = null) {
    if (!this.vivo || !this.trem.lutando) return;
    const cena = this.scene;
    if (!this.vulneravel) {
      cena.efeitos.faisca(this.x, this.y - this.cfg.altura / 2, 3);
      return;
    }
    if (morte === 'facada') dano = 4;
    this.vida -= dano;
    this.setTint(P.branco).setTintMode(Phaser.TintModes.FILL);
    cena.time.delayedCall(45, () => this.vivo && this.clearTint());
    if (this.vida <= 0) this.trem.quebrou(this);
  }
}

export class TremBlindado {
  constructor(cena, opcoes = {}) {
    this.cena = cena;
    this.opcoes = opcoes;
    const cam = cena.cameras.main;
    this.chao = cena.chaoAbaixo(cam.worldView.right - 10, 60);
    this.alvoX = Math.round(cam.worldView.x + 290);
    this.x = cam.worldView.right + 40;
    this.vivo = true;
    this.lutando = false;
    this.portaAberta = false;
    // Locomotiva e vagão: sólidos para o Lampião (não dá para atravessar o trem).
    this.loco = cena.physics.add.sprite(this.x, this.chao, 'trem_loco', 0).setOrigin(0, 1).setDepth(8);
    this.vagao = cena.physics.add.sprite(this.x + TREM.loco.largura - 4, this.chao, 'trem_vagao', 0).setOrigin(0, 1).setDepth(7);
    for (const s of [this.loco, this.vagao]) {
      s.body.allowGravity = false;
      s.body.setImmovable(true);
      cena.physics.add.collider(cena.jogador.corpo, s);
    }
    this.partes = {};
    for (const nome of Object.keys(TREM.partes)) {
      const p = new Parte(cena, this, nome);
      cena.alvos.add(p);
      p.body.allowGravity = false;
      this.partes[nome] = p;
    }
    this.texto = cena.add.text(0, 0, '', estiloTexto(hex('branco'))).setOrigin(0.5).setDepth(30).setVisible(false);
    this.proximo = { mg: 0, chamine: 0, torre: 0, soldado: 0, fumaca: 0 };
    this.soldados = [];
    this.estado = 'chegando';
    this.passo = 0;
    this.posicionar();
    cena.mostrar?.('CUIDADO!', 'TREM BLINDADO "A JARARACA"', 2200);
  }

  // Recuo de uma peça ao disparar: deslocamento curto aplicado em posicionar().
  tranco(peca, dx, dy = 0) {
    if (!peca || !peca.vivo) return;
    peca.recuo = { dx, dy, ate: this.cena.time.now + 70 };
  }

  falar(texto, x, y, ms = 800) {
    this.texto.setText(texto).setPosition(x, y).setVisible(true).setAlpha(1);
    this.cena.tweens.killTweensOf(this.texto);
    this.cena.tweens.add({ targets: this.texto, alpha: 0, delay: ms, duration: 300 });
  }

  posicionar() {
    // Corpos dinâmicos: reposiciona pelo corpo (senão a física desfaz).
    const x = Math.round(this.x);
    this.loco.body.reset(x, this.chao);
    this.vagao.body.reset(x + TREM.loco.largura - 4, this.chao);
    const topo = this.chao - TREM.loco.altura;
    for (const [nome, p] of Object.entries(this.partes)) {
      const c = TREM.partes[nome];
      const r = p.recuo && this.cena.time.now < p.recuo.ate ? p.recuo : null;
      p.body.reset(x + c.x + c.largura / 2 + (r ? r.dx : 0), topo + c.y + c.altura + (r ? r.dy : 0));
    }
  }

  // Ponto de saída de cada ataque.
  bocaMg(k) {
    const c = TREM.partes.mg;
    return [this.x + c.x, this.chao - TREM.loco.altura + c.y + (k ? 20 : 6)];
  }

  atualizar(t, dt) {
    if (!this.vivo && this.estado !== 'morrendo') return;
    const cena = this.cena;
    const s = dt / 1000;
    // Rodas e fumaça da chaminé.
    if (this.estado !== 'morto') {
      if (t > this.proximo.fumaca) {
        this.proximo.fumaca = t + (this.estado === 'chegando' ? 70 : 220);
        const ch = this.partes.chamine;
        if (ch.vivo) cena.efeitos.fumacaSobe(ch.x, ch.y - TREM.partes.chamine.altura);
        else cena.efeitos.fumaca(ch.x, ch.y - 10);
      }
    }
    if (this.estado === 'chegando') {
      const falta = this.x - this.alvoX;
      const vel = Math.max(60, Math.min(220, falta * 1.8));
      this.x -= vel * s;
      this.passo += dt * vel / 120;
      this.loco.setFrame(Math.floor(this.passo / 90) % 2);
      if (falta <= 1) {
        this.x = this.alvoX;
        this.estado = 'lutando';
        this.lutando = true;
        this.base = this.alvoX;
        som('apito');
        this.falar('PIIUÍÍ!', this.partes.chamine.x, this.partes.chamine.y - 50, 900);
        for (let k = 0; k < 6; k++) cena.efeitos.fumacaSobe(this.x + 20 + k * 14, this.chao - 70);
        cena.efeitos.tremer(0.006, 300);
        this.proximo.mg = t + 1200;
        this.proximo.chamine = t + 2600;
        this.proximo.torre = t + 3600;
        this.proximo.soldado = t + 2000;
      }
      this.posicionar();
      return;
    }
    if (this.estado === 'morrendo') return;
    // Vai e vem nos trilhos; bravo (porta aberta) avança mais perto do Lampião.
    const amplitude = this.portaAberta ? 70 : 24;
    const alvo = this.base - (Math.sin(t / (this.portaAberta ? 900 : 1600)) * 0.5 + 0.5) * amplitude;
    const dx = alvo - this.x;
    this.x += Phaser.Math.Clamp(dx, -60 * s, 60 * s);
    if (Math.abs(dx) > 0.5) {
      this.passo += dt;
      this.loco.setFrame(Math.floor(this.passo / 120) % 2);
    }
    this.posicionar();
    this.atacar(t);
  }

  atacar(t) {
    const cena = this.cena;
    const j = cena.jogador;
    if (j.morto) return;
    const p = this.partes;
    const pressa = this.portaAberta ? 0.65 : 1;
    // Metralhadoras: avisam piscando e soltam rajada alta ou baixa.
    if (p.mg.vivo && t > this.proximo.mg) {
      this.proximo.mg = t + 2700 * pressa;
      const baixa = Math.random() < 0.5;
      const [ax, ay] = this.bocaMg(baixa ? 1 : 0);
      this.falar(baixa ? 'PULA!' : '!', ax - 6, ay - 12, 400);
      som('alerta');
      cena.efeitos.faisca(ax, ay, 4);
      p.mg.setFrame(1);
      cena.time.delayedCall(520, () => {
        if (!p.mg.vivo) return;
        for (let k = 0; k < 4; k++) {
          cena.time.delayedCall(k * 120, () => {
            if (!p.mg.vivo || !this.lutando) return;
            // Alta: na altura da cabeça (agachado escapa). Baixa: na canela (só pulando).
            const y = this.chao - (baixa ? 12 : 37);
            cena.balasInimigas.disparar(ax, y, -1, 'pesada');
            cena.efeitos.disparo(ax, y, Math.PI, 'grande');
            cena.efeitos.capsula(ax + 12, y - 2, 1);
            this.tranco(p.mg, 2);
          });
        }
        cena.time.delayedCall(560, () => p.mg.vivo && p.mg.setFrame(0));
      });
    }
    // Chaminé: brasa acesa e três pedaços de carvão em arco em volta do Lampião.
    if (p.chamine.vivo && t > this.proximo.chamine) {
      this.proximo.chamine = t + 3900 * pressa;
      p.chamine.setFrame(1);
      cena.time.delayedCall(350, () => {
        if (!p.chamine.vivo || !this.lutando) return;
        p.chamine.setFrame(0);
        const bx = p.chamine.x;
        const by = p.chamine.y - TREM.partes.chamine.altura;
        for (const desvio of [-40, 0, 40]) {
          cena.balasInimigas.lancarCarvao(bx, by, j.x + desvio);
        }
        cena.efeitos.fumacaSobe(bx, by);
        cena.efeitos.fumacaSobe(bx, by - 8);
        cena.efeitos.faisca(bx, by, 12);
        this.tranco(p.chamine, 0, -3);
      });
    }
    // Torre: obus de canhão em arco.
    if (p.torre.vivo && t > this.proximo.torre) {
      this.proximo.torre = t + 4600 * pressa;
      p.torre.setFrame(1);
      cena.time.delayedCall(160, () => p.torre.vivo && p.torre.setFrame(0));
      const bx = p.torre.x - TREM.partes.torre.largura / 2;
      const by = p.torre.y - 13;
      cena.balasInimigas.lancarObus(bx, by, -1, Math.abs(j.x - bx));
      cena.efeitos.disparo(bx, by, Math.PI, 'canhao');
      for (let k = 0; k < 3; k++) cena.efeitos.fumaca(bx - k * 6, by - k * 2);
      this.tranco(p.torre, 4);
      cena.efeitos.tremer(0.006, 120);
    }
    // Soldados pulam do vagão (no máximo 3 de cada vez).
    if (t > this.proximo.soldado) {
      this.proximo.soldado = t + 5200;
      this.soldados = this.soldados.filter((s) => s.vivo);
      if (this.soldados.length < 3) {
        const x = this.vagao.x + Phaser.Math.Between(20, 70);
        const y = this.chao - TREM.vagao.altura + 22;
        const tipo = Phaser.Utils.Array.GetRandom(['volante', 'volante', 'granadeiro', 'facao']);
        const ini = cena.adicionarInimigo(x, cena.chaoAbaixo(x - 160, 60), tipo, {});
        ini.body.reset(x, y);
        ini.virar(-1);
        ini.body.setVelocity(-90, -220);
        ini.caindo = true;
        this.soldados.push(ini);
        this.opcoes.aoSoltar?.(ini);
      }
    }
  }

  quebrou(parte) {
    const cena = this.cena;
    parte.vivo = false;
    parte.clearTint().setFrame(parte.nome === 'porta' ? 1 : 2);
    cena.pontuar(parte.cfg.pontos, parte.x, parte.y - parte.cfg.altura - 8);
    cena.efeitos.explosao(parte.x, parte.y - parte.cfg.altura / 2, 1);
    cena.efeitos.faisca(parte.x, parte.y - parte.cfg.altura / 2, 14);
    cena.efeitos.tremer(0.01, 220);
    if (parte.nome === 'porta') {
      this.explodirCaldeira();
      return;
    }
    if (!this.portaAberta && !this.partes.mg.vivo && !this.partes.chamine.vivo) {
      // Porta da fornalha abre: a caldeira em brasa fica à mostra.
      this.portaAberta = true;
      const porta = this.partes.porta;
      porta.setFrame(1);
      this.falar('A CALDEIRA! ATIRA NA PORTA!', this.x + 60, this.chao - TREM.loco.altura - 14, 1800);
      cena.efeitos.chama(porta.x, porta.y - 15);
    }
  }

  // Fim do chefe: explosões em cadeia pelo trem e a caldeira arrebenta.
  explodirCaldeira() {
    const cena = this.cena;
    this.lutando = false;
    this.estado = 'morrendo';
    // Os soldados que pularam do vagão vão pelos ares junto.
    for (const s of this.soldados) if (s.vivo) s.levarDano(999, this.x, true, 'arremessa');
    som('apito');
    this.falar('PIIIIIIUUUÍ...!', this.x + 60, this.chao - TREM.loco.altura - 14, 1500);
    for (let k = 0; k < 14; k++) {
      cena.time.delayedCall(k * 170, () => {
        const sobre = k % 3 === 2 ? this.vagao : this.loco;
        const w = sobre === this.loco ? TREM.loco.largura : TREM.vagao.largura;
        const h = sobre === this.loco ? TREM.loco.altura : TREM.vagao.altura;
        cena.efeitos.explosao(sobre.x + Phaser.Math.Between(10, w - 10), this.chao - Phaser.Math.Between(10, h - 10), k === 13 ? 2 : 1.2);
      });
    }
    cena.time.delayedCall(14 * 170, () => {
      this.loco.setFrame(2);
      this.vagao.setFrame(1);
      for (const p of Object.values(this.partes)) p.setVisible(false);
      cena.efeitos.tremer(0.02, 600);
      cena.cameras.main.flash(200, 255, 230, 180);
      this.estado = 'morto';
      this.vivo = false;
      // A carcaça fica, mas não segura mais o Lampião: dá para seguir em frente.
      this.loco.body.enable = false;
      this.vagao.body.enable = false;
      this.loco.setDepth(4);
      this.vagao.setDepth(4);
      // Vapor e fogo saindo da carcaça um bom tempo.
      cena.time.addEvent({
        delay: 160, repeat: 50, callback: () => {
          cena.efeitos.fumacaSobe(this.x + Phaser.Math.Between(20, 180), this.chao - 80);
          if (Math.random() < 0.4) cena.efeitos.chama(this.x + Phaser.Math.Between(20, 180), this.chao - Phaser.Math.Between(20, 90));
        },
      });
    });
  }
}
