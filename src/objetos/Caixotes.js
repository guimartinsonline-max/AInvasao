
// Caixotes de madeira e barris de querosene destrutíveis. Bloqueiam a passagem
// até serem quebrados por tiro, peixeira ou explosão. O caixote vira tábuas e
// pode soltar um item, um refém ou o bode Fubá; o barril explode e pode
// estourar outros barris por perto, em cadeia. Um objeto empilhado cai quando
// o de baixo quebra. No campo de treino voltam depois de um tempo.

const TIPOS = {
  caixote: { textura: 'caixote', largura: 24, altura: 18, vida: 3 },
  barril: { textura: 'barril', largura: 18, altura: 24, vida: 2, explode: { raio: 44, dano: 6, tamanho: 1.3 } },
};
const VOLTA = 10000; // ms para reaparecer (campo de treino)

// O que sai de um caixote quebrado: item, refém amarrado, bode Fubá ou nada.
function surpresa() {
  const r = Math.random();
  if (r < 0.28) return 'item'; // arma: metade do que era
  if (r < 0.40) return 'refem';
  if (r < 0.52) return 'bode';
  return null;
}

class Caixote {
  constructor(cena, x, y, tipo = 'caixote') {
    this.cena = cena;
    this.tipo = tipo;
    this.cfg = TIPOS[tipo];
    this.inicio = { x, y };
    this.img = cena.add.image(x, y, this.cfg.textura, 0).setOrigin(0).setDepth(6);
    this.zona = cena.add.zone(x, y, this.cfg.largura, this.cfg.altura).setOrigin(0);
    cena.solidos.add(this.zona);
    this.zona.caixote = this;
    this.vivo = true;
    this.vida = this.cfg.vida;
  }

  // Posição do "pé" (base, centro), no mesmo padrão dos inimigos.
  get x() { return this.img.x + this.cfg.largura / 2; }
  get y() { return this.img.y + this.cfg.altura; }

  mover(x, y) {
    this.img.setPosition(x, y);
    this.zona.setPosition(x, y);
    this.zona.body.updateFromGameObject();
  }

  levarDano(dano = 1) {
    if (!this.vivo) return;
    const cena = this.cena;
    this.vida -= Math.max(1, dano);
    this.img.setTint(0xffffff).setTintMode(Phaser.TintModes.FILL);
    // Treme um pixel para o lado a cada tiro.
    this.img.x = this.zona.x + (Math.random() < 0.5 ? -1 : 1);
    cena.time.delayedCall(50, () => {
      this.img.clearTint();
      this.img.x = this.zona.x;
    });
    if (this.cfg.explode && this.vida > 0) {
      // Barril furado: amassa e solta faísca.
      this.img.setFrame(1);
      cena.efeitos.faisca(this.x + 3, this.img.y + 11, 4);
    }
    if (this.vida <= 0) this.quebrar();
  }

  quebrar() {
    const cena = this.cena;
    const ef = cena.efeitos;
    const cx = this.x;
    const cy = this.y - this.cfg.altura / 2;
    const topo = this.img.y;
    this.vivo = false;
    cena.pontuar(this.cfg.explode ? 50 : 10, cx, cy - 10);
    // Se estava caindo de uma pilha, para a queda antes de sair do mapa.
    if (this.queda) this.queda.stop();
    this.img.setVisible(false);
    this.mover(-500, -500);
    if (this.cfg.explode) {
      // Pequeno atraso para a reação em cadeia ficar visível, barril por barril.
      const e = this.cfg.explode;
      cena.time.delayedCall(70, () => cena.explodir(cx, cy, e.raio, e.dano, e.tamanho));
    } else {
      ef.tabuas(cx, cy);
      ef.poeira(cx, this.inicio.y + this.cfg.altura, 8);
      ef.tremer(0.004, 90);
      const dentro = surpresa();
      if (dentro === 'item') cena.soltarItem(cx, cy, Phaser.Utils.Array.GetRandom(cena.premios));
      else if (dentro === 'refem') cena.surpresaRefem(cx, this.y);
      else if (dentro === 'bode') cena.surpresaBode(cx, this.y);
    }
    cena.caixotes.derrubarSobre(cx, topo);
    if (cena.tudoVolta) cena.time.delayedCall(VOLTA, () => this.voltar());
  }

  voltar() {
    const { x, y } = this.inicio;
    const j = this.cena.jogador;
    const L = this.cfg.largura;
    const A = this.cfg.altura;
    const ocupado = j.x > x - 8 && j.x < x + L + 8 && j.pe > y - 4 && j.pe - 36 < y + A;
    // Lugar ocupado (pelo Lampião ou por outro objeto que caiu ali): tenta de novo depois.
    const outro = this.cena.caixotes.lista.some((c) => c !== this && c.vivo && Math.abs(c.img.x - x) < L && Math.abs(c.img.y - y) < A);
    if (ocupado || outro) {
      this.cena.time.delayedCall(1000, () => this.voltar());
      return;
    }
    this.vivo = true;
    this.vida = this.cfg.vida;
    this.mover(x, y);
    this.img.setVisible(true).clearTint().setFrame(0);
    this.cena.efeitos.poeira(x + L / 2, y + A, 6);
  }
}

export class Caixotes {
  // posicoes: [x, y, tipo?] com x, y do canto de cima à esquerda.
  constructor(cena, posicoes) {
    this.cena = cena;
    this.lista = posicoes.map(([x, y, tipo]) => new Caixote(cena, x, y, tipo));
  }

  // Caixotes apoiados em cima de um que quebrou caem até o próximo apoio.
  derrubarSobre(cx, topo) {
    const cena = this.cena;
    for (const c of this.lista) {
      if (!c.vivo || c.queda || Math.abs(c.x - cx) >= c.cfg.largura || Math.abs(c.y - topo) > 1) continue;
      const destino = cena.chaoAbaixo(c.x, c.y + 1) - c.cfg.altura;
      const alvo = { y: c.img.y };
      c.queda = cena.tweens.add({
        targets: alvo, y: destino, duration: Math.max(80, (destino - alvo.y) * 5), ease: 'Quad.easeIn',
        onUpdate: () => c.vivo && c.mover(c.img.x, Math.round(alvo.y)),
        onComplete: () => {
          c.queda = null;
          cena.efeitos.poeira(c.x, c.y, 6);
        },
      });
    }
  }

  vivos() {
    return this.lista.filter((c) => c.vivo);
  }
}
