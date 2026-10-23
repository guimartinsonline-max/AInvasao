
// Caixotes de madeira e barris de querosene destrutíveis. Bloqueiam a passagem
// até serem quebrados por tiro, peixeira ou explosão. O caixote vira tábuas e
// pode soltar um item, um refém ou o bode Fubá; o barril explode e pode
// estourar outros barris por perto, em cadeia. Um objeto empilhado cai quando
// o de baixo quebra. No campo de treino voltam depois de um tempo.

const TIPOS = {
  // Caixote 2.5D (22/10); a tampa aparece por cima
  // (dy: quanto a imagem sobe acima do sólido, que fica no meio da tampa).
  // (23/10: 30% menor; o tiro em pé ainda acerta pela faixa "mira" acima da tampa)
  caixote: { textura: 'caixote', largura: 20, altura: 22, vida: 3, dy: 4, mira: 12 },
  // Barril 3D (23/10, 20% maior): a tampa em elipse aparece por cima do sólido.
  barril: { textura: 'barril', largura: 22, altura: 25, vida: 2, dy: 5, explode: { raio: 48, dano: 6, tamanho: 1.4 } },
};
// Os dados guardam o canto de cima no tamanho antigo do caixote (18 de altura).
const ALTURA_DADOS = { caixote: 18, barril: 24 };
const VOLTA = 10000; // ms para reaparecer (campo de treino)

// O que sai de um caixote quebrado: item, refém amarrado, bode Fubá ou nada.
function surpresa() {
  const r = Math.random();
  if (r < 0.17) return 'item'; // arma: bem menos que no começo
  if (r < 0.29) return 'refem';
  if (r < 0.41) return 'bode';
  if (r < 0.66) return 'comida';
  return null;
}

class Caixote {
  constructor(cena, x, y, tipo = 'caixote') {
    this.cena = cena;
    this.tipo = tipo;
    this.cfg = TIPOS[tipo];
    this.inicio = { x, y };
    this.dy = this.cfg.dy || 0;
    this.img = cena.add.image(x, y - this.dy, this.cfg.textura, 0).setOrigin(0).setDepth(6);
    this.zona = cena.add.zone(x, y, this.cfg.largura, this.cfg.altura).setOrigin(0);
    cena.solidos.add(this.zona);
    this.zona.caixote = this;
    this.vivo = true;
    this.vida = this.cfg.vida;
  }

  // Posição do "pé" (base, centro), no mesmo padrão dos inimigos.
  get x() { return this.zona.x + this.cfg.largura / 2; }
  get y() { return this.zona.y + this.cfg.altura; }

  mover(x, y) {
    this.img.setPosition(x, y - this.dy);
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
      cena.efeitos.faisca(this.x + 3, this.img.y + 16, 4);
    }
    if (this.vida <= 0) this.quebrar();
  }

  quebrar() {
    const cena = this.cena;
    const ef = cena.efeitos;
    const cx = this.x;
    const cy = this.y - this.cfg.altura / 2;
    const topo = this.zona.y;
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
      else if (dentro === 'comida') cena.soltarItem(cx, cy, cena.comidaSorteada());
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
    const outro = this.cena.caixotes.lista.some((c) => c !== this && c.vivo && Math.abs(c.zona.x - x) < L && Math.abs(c.zona.y - y) < A);
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
    // Converte do tamanho antigo: cada um apoia o pé onde apoiava; o empilhado apoia no
    // topo novo do de baixo (os de baixo primeiro).
    const pe = ([, y, tipo = 'caixote']) => y + ALTURA_DADOS[tipo];
    const postos = [];
    // Barris (23/10): nunca empilhados e um só em cada lugar (os vizinhos e os de cima saem).
    this.lista = [];
    for (const [x0, y, tipo = 'caixote'] of [...posicoes].sort((a, b) => pe(b) - pe(a))) {
      let p = pe([x0, y, tipo]);
      const baixo = postos.find((o) => Math.abs(o.x - x0) < 20 && Math.abs(o.topoVelho - p) <= 1);
      const barril = tipo === 'barril';
      const vizinho = barril && postos.some((o) => o.barril && Math.abs(o.x - x0) < 40 && Math.abs(o.pe - p) <= 30);
      if ((baixo && (barril || baixo.fora)) || vizinho) {
        postos.push({ x: x0, topoVelho: y, fora: true, barril, pe: p });
        continue;
      }
      if (baixo) p = baixo.topoNovo;
      const x = barril ? x0 - 2 : x0;
      const topo = p - TIPOS[tipo].altura;
      postos.push({ x: x0, topoVelho: y, topoNovo: topo, barril, pe: p });
      this.lista.push(new Caixote(cena, x, topo, tipo));
    }
  }

  // Caixotes apoiados em cima de um que quebrou caem até o próximo apoio.
  derrubarSobre(cx, topo) {
    const cena = this.cena;
    for (const c of this.lista) {
      if (!c.vivo || c.queda || Math.abs(c.x - cx) >= c.cfg.largura || Math.abs(c.y - topo) > 1) continue;
      const destino = cena.chaoAbaixo(c.x, c.y + 1) - c.cfg.altura;
      const alvo = { y: c.zona.y };
      c.queda = cena.tweens.add({
        targets: alvo, y: destino, duration: Math.max(80, (destino - alvo.y) * 5), ease: 'Quad.easeIn',
        onUpdate: () => c.vivo && c.mover(c.zona.x, Math.round(alvo.y)),
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
