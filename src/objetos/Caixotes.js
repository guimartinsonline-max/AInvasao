import { PREMIOS } from '../armas.js';

// Caixotes de madeira destrutíveis. Bloqueiam a passagem até serem quebrados
// por tiro, peixeira ou explosão; viram tábuas voando e podem soltar um item.
// Um caixote empilhado cai quando o de baixo quebra. No campo de treino voltam.

const LARGURA = 24;
const ALTURA = 18;
const VIDA = 3;
const VOLTA = 10000; // ms para o caixote reaparecer (campo de treino)
const CHANCE_PREMIO = 0.6;

class Caixote {
  constructor(cena, x, y) {
    this.cena = cena;
    this.inicio = { x, y };
    this.img = cena.add.image(x, y, 'caixote').setOrigin(0).setDepth(6);
    this.zona = cena.add.zone(x, y, LARGURA, ALTURA).setOrigin(0);
    cena.solidos.add(this.zona);
    this.zona.caixote = this;
    this.vivo = true;
    this.vida = VIDA;
  }

  // Posição do "pé" (base do caixote, centro), no mesmo padrão dos inimigos.
  get x() { return this.img.x + LARGURA / 2; }
  get y() { return this.img.y + ALTURA; }

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
    if (this.vida <= 0) this.quebrar();
  }

  quebrar() {
    const cena = this.cena;
    const ef = cena.efeitos;
    const cx = this.x;
    const cy = this.y - ALTURA / 2;
    const topo = this.img.y;
    this.vivo = false;
    // Se estava caindo de uma pilha, para a queda antes de sair do mapa.
    if (this.queda) this.queda.stop();
    this.img.setVisible(false);
    this.mover(-500, -500);
    ef.tabuas(cx, cy);
    ef.poeira(cx, this.inicio.y + ALTURA, 8);
    ef.tremer(0.004, 90);
    if (Math.random() < CHANCE_PREMIO) cena.soltarItem(cx, cy, Phaser.Utils.Array.GetRandom(PREMIOS));
    cena.caixotes.derrubarSobre(cx, topo);
    cena.time.delayedCall(VOLTA, () => this.voltar());
  }

  voltar() {
    const { x, y } = this.inicio;
    const j = this.cena.jogador;
    const ocupado = j.x > x - 8 && j.x < x + LARGURA + 8 && j.pe > y - 4 && j.pe - 36 < y + ALTURA;
    // Lugar ocupado (pelo Lampião ou por outro caixote que caiu ali): tenta de novo depois.
    const outro = this.cena.caixotes.lista.some((c) => c !== this && c.vivo && Math.abs(c.img.x - x) < LARGURA && Math.abs(c.img.y - y) < ALTURA);
    if (ocupado || outro) {
      this.cena.time.delayedCall(1000, () => this.voltar());
      return;
    }
    this.vivo = true;
    this.vida = VIDA;
    this.mover(x, y);
    this.img.setVisible(true).clearTint();
    this.cena.efeitos.poeira(x + LARGURA / 2, y + ALTURA, 6);
  }
}

export class Caixotes {
  constructor(cena, posicoes) {
    this.cena = cena;
    this.lista = posicoes.map(([x, y]) => new Caixote(cena, x, y));
  }

  // Caixotes apoiados em cima de um que quebrou caem até o próximo apoio.
  derrubarSobre(cx, topo) {
    const cena = this.cena;
    for (const c of this.lista) {
      if (!c.vivo || c.queda || Math.abs(c.x - cx) >= LARGURA || Math.abs(c.y - topo) > 1) continue;
      const destino = cena.chaoAbaixo(c.x, c.y + 1) - ALTURA;
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
