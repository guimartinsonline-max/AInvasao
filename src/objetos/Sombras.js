// Sombra no chão e pegadas (chão largo, 22/10): cada personagem, bicho, item e veículo tem
// uma sombra achatada embaixo (menor quanto mais alto ele está) e quem anda no chão deixa
// pegadas que somem devagar. Tudo em pool: nada é criado durante o jogo.
const PEGADAS = 60;
const VIDA_PEGADA = 3600; // ms
const ALFA_PEGADA = 0.34; // suave
const PASSO = 14; // px entre uma pegada e outra

export class Sombras {
  // solidos: [[x, y, w, h], ...] do mapa, para achar o chão embaixo de quem pula.
  constructor(cena, solidos) {
    this.cena = cena;
    this.solidos = solidos.map(([x, y, w]) => [x, y, w]).sort((a, b) => a[1] - b[1]);
    if (!cena.textures.exists('sombra_chao')) {
      const g = cena.make.graphics({ x: 0, y: 0 }, false);
      g.fillStyle(0x1a1016, 0.32).fillEllipse(16, 4, 32, 8);
      g.fillStyle(0x1a1016, 0.26).fillEllipse(16, 4, 20, 5);
      g.generateTexture('sombra_chao', 32, 8);
      g.clear();
      // Pegada em forma de pé visto de cima, achatado pela perspectiva: calcanhar atrás,
      // vão do arco e a planta com os dedos na frente (aponta para a direita); borda mais clara.
      g.fillStyle(0x1a1016, 0.55).fillRect(0, 1, 3, 2).fillRect(5, 0, 4, 4).fillRect(9, 1, 1, 2);
      g.fillStyle(0x1a1016, 1).fillRect(1, 1, 2, 2).fillRect(6, 1, 3, 2);
      g.generateTexture('pegada', 10, 4);
      g.destroy();
    }
    this.sombras = new Map(); // alvo -> imagem
    this.pegadas = [];
    for (let k = 0; k < PEGADAS; k++) {
      this.pegadas.push(cena.add.image(-50, -50, 'pegada').setOrigin(0.5, 0.5).setDepth(4.8).setVisible(false));
    }
    this.proxima = 0;
  }

  // Topo do sólido mais alto embaixo de (x, y).
  chao(x, y) {
    for (const [sx, sy, sw] of this.solidos) {
      if (sy >= y - 2 && x >= sx && x <= sx + sw) return sy;
    }
    return 194;
  }

  sombraDe(alvo, largura) {
    let s = this.sombras.get(alvo);
    if (!s) {
      s = this.cena.add.image(0, 0, 'sombra_chao').setOrigin(0.5, 0.5).setDepth(4.9);
      s.largura = largura;
      this.sombras.set(alvo, s);
    }
    return s;
  }

  pisar(x, y, dir, t) {
    const p = this.pegadas[this.proxima];
    this.proxima = (this.proxima + 1) % PEGADAS;
    p.setPosition(Math.round(x), Math.round(y)).setFlipX(dir < 0).setVisible(true).setAlpha(ALFA_PEGADA);
    p.nasceu = t;
    p.setDepth(y < 192 ? 10.6 : 4.8);
  }

  // alvos: [{ alvo, x, pe, largura, visivel, anda }] montados pela cena a cada quadro.
  atualizar(t, alvos) {
    const vistos = new Set();
    for (const a of alvos) {
      vistos.add(a.alvo);
      const s = this.sombraDe(a.alvo, a.largura);
      if (!a.visivel) {
        s.setVisible(false);
        continue;
      }
      const chao = this.chao(a.x, a.pe);
      const alto = Math.max(0, chao - a.pe);
      const k = Math.max(0.35, 1 - alto / 110);
      s.setVisible(true).setPosition(Math.round(a.x), chao + 1)
        .setScale((a.largura / 32) * k, k).setAlpha(Math.max(0.4, k));
      // em cima de peça 2.5D (lajedo, girau): a sombra vai no tampo, na frente da peça
      s.setDepth(chao < 192 ? 10.6 : 4.9);
      // pegadas: um passo a cada PASSO px andados no chão
      if (a.anda && alto < 1) {
        const ult = a.alvo.ultimaPegada;
        if (ult === undefined || Math.abs(a.x - ult) >= PASSO) {
          a.alvo.ultimaPegada = a.x;
          a.alvo.passo = !a.alvo.passo;
          const dir = ult === undefined ? 1 : Math.sign(a.x - ult);
          this.pisar(a.x - dir * 3, chao + (a.alvo.passo ? 2 : -1), dir, t);
        }
      } else if (alto >= 1) {
        a.alvo.ultimaPegada = undefined;
      }
    }
    for (const [alvo, s] of this.sombras) {
      if (!vistos.has(alvo)) s.setVisible(false);
    }
    for (const p of this.pegadas) {
      if (!p.visible) continue;
      const idade = t - p.nasceu;
      if (idade > VIDA_PEGADA) p.setVisible(false);
      else p.setAlpha(ALFA_PEGADA * (1 - idade / VIDA_PEGADA));
    }
  }
}
