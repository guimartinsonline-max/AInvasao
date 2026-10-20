# A Invasão — guia de estilo visual

Padrão que **toda arte nova** segue (personagens, NPCs, inimigos, itens, cenários, efeitos) e que a arte antiga vai alcançar nas próximas rodadas.
Leia antes de desenhar qualquer coisa. Detalhes técnicos de cada peça continuam no `CLAUDE.md`; aqui ficam as regras.

## 1. A ideia em uma frase

**Metal Slug no sertão:** mesmo jeito de desenhar (pixel art à mão, contorno escuro, volume com muitos tons, caricatura, exagero e humor bizarro), com tema, paleta e desenhos nossos.
Pode e deve estudar imagens, vídeos e rips da franquia como referência de estilo e mecânica. **Não pode** copiar sprite, personagem ou cenário pixel por pixel (são da SNK): cada desenho é original.

## 2. O que faz o Metal Slug parecer Metal Slug (pesquisa, para não refazer)

Resumo de estudo dos jogos (MS1 a MS3, MSX, MS6, Awakening) e de entrevistas do time da Nazca/SNK:

- **Animação demais, de propósito.** Tudo tem mais quadros do que precisa: o soldado que coça a cabeça, o que foge tropeçando, o tanque que treme parado. O próprio artista Akio contou que as animações eram tão longas que os programadores tinham que otimizar o jogo para aguentar. Para nós: poucos quadros, mas **cada ação com antecipação, ação e exagero** (ver seção 6).
- **Caricatura com peso.** Corpos atarracados, cabeça grande, mãos e botas grandes, inclinados para a frente. Tudo parece pesado e macio ao mesmo tempo, como borracha.
- **Rostos que falam.** Olhos e boca mudam em quase toda ação: grito, pânico, suor, choro, risada. O inimigo é engraçado antes de ser perigoso.
- **Contorno escuro só por fora** e volume por dentro com rampas de 5 a 7 tons. A luz vem de cima e um pouco da frente.
- **Máquinas gordas e cheias de coisa:** rebites, chapas, canos, sacos, lona, ferrugem, lama, gente dentro. Toda máquina tem um "rosto" (farol, janela, boca de canhão) e explode em pedaços.
- **Cenário lotado e contando história:** ruínas, cartazes, roupa no varal, carcaças, bichos. Fundo cheio até o alto, várias camadas de parallax e uma de frente.
- **Explosões e efeitos são as estrelas:** clarão, bola de fogo em gomos, fumaça escura subindo, estilhaços, cápsulas quicando.
- **Humor de guerra bizarro:** soldados que se rendem chorando, que fogem pelados do banho, que jogam bola no meio da guerra; e o horror nojento ao lado (zumbis, múmias, aliens de carne, transformações do jogador em gordo, múmia, zumbi, macaco, boneco de neve).
- **Paleta saturada mas não berrante:** terra quente equilibrada por céu azul e sombras frias (azuladas/roxas). No Awakening isso fica bem claro.

## 3. Resolução, escala e tamanhos

- Tela fixa **548×308**, chão do mundo em y=192, ampliada só em proporção inteira (sem borrar).
- 1 pixel do desenho = 1 pixel do jogo. **Nunca** escalar sprite no código para "caber" (nem 1,5x): se o tamanho está errado, redesenha.

| Categoria | Quadro (L×A) | Corpo visível (altura) | Referência |
|---|---|---|---|
| Lampião / Maria Bonita | 60×72 | ~42 px | pé em (14,63) |
| Soldados, NPCs humanos, refém | 52×46 | 38 a 42 px | mesma cabeça do Lampião |
| Aliens pequenos/médios | 60×52 a 60×60 | 44 a 58 px | podem passar do humano |
| Armas na mão | até 32×15 | ~2/3 da altura do Lampião | coronha, ferrolho, gatilho, brilho |
| Itens de chão (comida, caixa de arma) | 10×10 a 24×20 | — | legíveis a 1x no iPhone |
| Caixote / barril | 24×18 / 18×24 | — | — |
| Veículos | 70 a 130 px de largura | 50 a 62 px | trem e chefes podem passar disso |
| Chefes | livre | ocupa 1/3 a 1/2 da tela | partes que quebram separadas |

- Camadas de cenário em pedaços de **até 2048 px** de largura (limite do iPhone).

## 4. Paleta

- Paleta fixa em `assets/paleta.json` (151 cores hoje). **Toda cor usada tem nome lá.** Precisa de cor nova? Adiciona na paleta com nome, nunca hex solto no desenho.
- **Rampas por material** (5 a 7 tons, do mais escuro ao brilho): pele, couro, tecido cáqui/oliva da Volante, madeira, lona, pedra/arenito, metal, carne de alien, gosma.
- **Rampas saturadas (padrão novo, 20/10):** `pelo_1-7` (branco/pano claro), `fuba_1-7` (marrom alaranjado, pena, couro claro), `carne_1-7` (pele), `verde_1-7` (farda oliva), `negro_1-6` (preto com brilho azulado), `rubro_1-6`, `latao_1-6`, `osso_1-5` (chifre, palha, cru), `aco_1-6` (calça, metal escuro). Cada degrau muda de matiz, não só de claridade: a sombra puxa para o azul/roxo e a luz para o amarelo. Personagens e bichos usam essas; as antigas ficam para o cenário.
- Sombras puxam para o **frio** (azul/roxo: `sombra`, `azul_sombra`, `sombra_media`); luzes puxam para o **quente** (`areia_clara`, `amarelo_claro`). Nunca escurecer só misturando preto.
- **Céu azul sempre presente** para equilibrar a terra quente. Não deixar a tela toda em laranja/marrom.
- **Verde-alien** (`alien_*`) é reservado para coisa alienígena, gás, gosma e raio. Humano e cenário normal não usam esse verde vivo (a caatinga usa os verdes acinzentados `caatinga*` e `mandacaru*`).
- Noite e crepúsculo: usar as cores próprias (`*_n*`, `*_q*`) já pintando a peça na hora certa, em vez de escurecer depois.

## 5. Contorno, luz e textura

- **Contorno de 1 px escuro só na silhueta** (`sombra` em personagens, `mad_n1` em madeira/cenário). Por dentro, divisões só com tom, sem linha preta.
- Luz de cima e da frente: **beirada de cima acesa**, miolo médio, base e lado de trás na sombra, e um **ponto de brilho** no que é liso ou molhado (metal, olho, gosma, couro engraxado).
- Volume calculado pela forma (cilindro para tora, braço e cano; plano para lona e parede; relevo para carne de alien).
- **Volume 3D (padrão novo para personagens e bichos, `tools/arte/volume3d.py`):** o boneco é montado com formas 3D (elipsoides e cápsulas) ou cúpulas sobre a forma 2D (`sombrear2d`), iluminado de um lado só, desenhado 4x maior e reduzido em manchas limpas. **Proibido o sombreado de travesseiro** (borda toda clara em volta) e pixel solto no meio de mancha. A luz forma uma área clara grande e contínua no lado de cima-esquerda; a sombra fica embaixo e atrás.
- Onde uma peça passa na frente de outra (perna sobre barriga, braço sobre tronco), linha escura do material de trás.
- **Sem pontilhado em xadrez (Bayer)** da fase 2 em diante. Transição de tom e de terreno em manchas orgânicas.
- **Textura e desgaste em tudo:** veio, racha, nó, costura, remendo, mancha d'água, barro, ferrugem, farpa, tinta descascada, amassado. Nada fica liso e novo.
- Letreiros e placas: fonte **5x7 com sombra** (`letreiro()`), pintada à mão e gasta.

## 6. Animação

- Poucos quadros bem escolhidos, mas **sempre com exagero**. Mínimos por ação:
  - Parado: 2 a 4 (respirando, balançando a arma). Espera longa: animação de tédio própria.
  - Andar/correr: 6 a 8 (Lampião), 4 a 6 (soldados), 4 (bichos).
  - Pulo: subindo, topo, caindo (3).
  - Tiro: tranco do recuo (2), clarão na boca, cápsula saltando.
  - Golpe corpo a corpo: levantar e descer (2) + arco de corte.
  - Morte: mínimo 4 (tranco, grito de braço para cima, tombando, estirado no chão). Cada tipo de morte (tiro, faca, fogo, explosão, raio) com reação diferente.
  - Pânico/susto: "!?" + 2 quadros + corridinha.
- **Antecipação antes do ataque:** todo inimigo avisa antes de causar dano (faísca, "!", olho acendendo, parada curta).
- **Nada que se mexe fica pintado no fundo:** fogo, fumaça, água, bandeira, luz piscando viram sprite animado em loop.
- Consistência entre quadros: mesma cabeça, mesmo tamanho, mesmo ponto do pé. Conferir lado a lado antes de exportar.

## 7. Regras por categoria

### Personagens jogáveis
- Atarracados, inclinados para a frente, base agachada. Cabeça ~1/3 da altura.
- **O rosto é o mais importante:** pelo menos neutro, grito, dor, olhando para cima, olhando para baixo, suor, bocejo.
- Cada arma com o seu jeito de segurar (quadril, ombro, cintura, uma mão).
- Acessórios do cangaço lidos de longe: chapéu de couro com a meia-lua e moedas, cartucheiras de latão, bornal bordado, punhal. Não encher de detalhe pequeno que vira ruído.
- Toda transformação (gordo, zumbi, futuras) reaproveita as poses do personagem normal e muda só o que precisa.

### Inimigos humanos (a Volante e companhia)
- Mesmo porte do Lampião, **caricatos**: narigão, bigode, barriga, olhos exagerados "na medida".
- Silhueta diferente por tipo (mochila, escudo, fita de bala, quepe dourado, máscara de gás) para o jogador reconhecer de longe.
- Têm vida própria: cochilam, jogam truco, cozinham, choram com a foto da noiva, se rendem, fogem.
- Sangue vermelho em quantidade "de desenho", nunca realista.

### Aliens e monstros
- **Bizarros e nojentos:** carne, olhos demais, corpo errado, gosma, veias, pústulas, partes translúcidas mostrando órgão aceso.
- Desenho por relevo (campo de altura vira luz e sombra) com brilho molhado.
- Tecnologia alien com cara de anos 30: latão, vidro, bobina, bulbo aceso. Raio sempre verde.
- Gosma verde no lugar de sangue. Sem medo, sem rendição: o humor vem do nojo e do exagero, não do pânico.

### NPCs, reféns e bichos
- Mesmo porte e mesmo nível de detalhe dos inimigos.
- Refém: romeiros, vaqueiros, gente do sertão. Amarrado se debate, solto agradece de um jeito engraçado e entrega item.
- Bichos (bode, galinha, jumento, urubu) caricatos, com 2 a 4 quadros de movimento e reação ao tiro.

### Itens
- **Caixa de arma:** caixa quadrada de chapa com a letra no meio, clarão leve de tempos em tempos.
- **Comida:** comida do sertão, com volume e brilho apetitoso, legível a 10–20 px.
- Todo item tem contorno escuro e contraste forte com o chão, para não sumir no cenário.

### Veículos e máquinas
- Gordos e pesados, cheios de chapa, rebite, cano, saco, lona e gente dentro.
- Lataria em faixas lisas, quinas com brilho, ferrugem escorrendo, lama embaixo.
- **4 etapas de dano** (inteiro, furado, chamuscado, rasgado com brasa) e carcaça destroçada no fim.
- Rodas girando de verdade, com poeira.

### Cenários
- Nível mínimo: o da barraca LAB (`tools/arte/base_detalhe.py`).
- Camadas: céu, fundo distante (mais claro e de menor contraste, `nevoa()`), meio, perto, chão de jogo, frente (1,1 de parallax). **Fundo cheio até o alto.**
- Fundo pintado inteiro para o trecho: **sem repetição visível**.
- Coerência: nada flutuando, fumaça sempre sai de um fogo visível, passagem entre ambientes suave (sem corte reto).
- Objetos de apoio em volta de tudo (corda, estaca, saco, caixote, garrafão) e coisas que contam história (carcaça, cartaz, roupa no varal).
- Cenário reage: coisas quebram, telhado cai, varal arrebenta, bicho foge.

### Efeitos
- Explosão no padrão `explosao_ms`: clarão com raios, bola de fogo em gomos, estilhaços, fumaça escura subindo por cima e cogumelo.
- Tiros grandes e gordos, cada arma com o seu desenho. Todo tiro com clarão na boca e cápsula.
- Poeira em passo, pulo e queda. Fumaça que fica pairando depois da explosão.
- Game feel: tremida de tela, piscar branco no acerto, pausa curta no impacto forte.

## 8. Ideias bizarras no espírito Metal Slug (para as próximas fases)

Ideias originais, para propor e aprovar antes de fazer:

1. **Lampião múmia de couro seco:** atingido pelo sopro de um cangaceiro morto-vivo do Raso da Catarina, vira múmia esturricada de sol; mais lento, só peixeira e pistola, e um segundo acerto mata.
2. **Lampião cabra-macho (bode):** o raio de um alien transforma o Lampião em bode de chapéu de couro; pula mais alto, dá cabeçada e atira com uma baladeira presa no chifre.
3. **Lampião de barro:** cai no açude de lama e vira boneco de barro rachando; tem que balançar para quebrar a casca.
4. **Soldado da Volante tomando banho na cacimba** foge pelado tapando com o chapéu; outro está fazendo a barba e foge com meia cara ensaboada.
5. **Cerebrão de mandacaru:** alien que se disfarça de cacto; quando o jogador passa, o mandacaru abre olhos nos gomos.
6. **Vaca abduzida caindo do céu** em cima dos soldados no meio da fase (e às vezes um bode voltando com um capacete alien).
7. (Detalhe do chefe já aprovado) **Coronel numa cadeira de balanço blindada** carregada por quatro jagunços, atirando de bacamarte duplo (chefe da fase 4).
8. (Detalhe do chefe já aprovado) **Beato com o cajado que solta raio** e romeiros hipnotizados de olho verde (fase 5); salvar o romeiro quebra o transe com uma cajadada.
9. **Bode devolvido:** o bode abduzido volta do disco gigante e mutante (três chifres, olho de alien no peito), como miniboss que berra soltando raio; derrotado, encolhe e vira o Fubá de novo.
10. **Sanfoneiro refém** que, solto, toca forró e faz os soldados perto pararem para dançar por uns segundos.
11. **Alien que imita cangaceiro** com chapéu de couro torto e roupa costurada errado (três mangas), revelado ao levar tiro.
12. **Urubu ciborgue** dos aliens fazendo rasante com olho de câmera.

## 9. Fluxo para cada peça nova

1. Ver referência (Metal Slug e foto real do objeto do sertão).
2. Rascunho pequeno de uma peça só, num recorte, para aprovação.
3. Aplicar as regras deste guia (tamanho, paleta, contorno, rampas, desgaste, animação).
4. Conferir a 1x e a 2x lado a lado com o Lampião e com uma peça já aprovada.
5. Só então aplicar no resto e exportar (`tools/arte/exportar.py`, que sobe a versão do cache).

## 10. Checklist rápido antes de aprovar

- [ ] Tamanho certo para a categoria e sem escala no código
- [ ] Só cores da paleta, rampa de 5 a 7 tons por material
- [ ] Contorno escuro só na silhueta, beirada de cima acesa, sombra fria
- [ ] Desgaste e textura (nada liso e novo)
- [ ] Rosto expressivo (se tiver rosto) e pose exagerada
- [ ] Animações com antecipação e reação
- [ ] Lê bem a 1x na tela do iPhone e contrasta com o fundo
- [ ] Desenho original, sem copiar sprite do Metal Slug

Fontes da pesquisa: [Automaton, entrevista com Akio](https://automaton-media.com/en/news/metal-slug-artist-akio-says-his-elaborate-pixel-animations-made-his-programmers-want-to-rip-their-hair-out-but-it-was-so-worth-it/), [Polycade, história do MS1](https://polycade.com/blogs/history-fun-facts/metal-slug-1996), [Foro3D, Metal Slug aos 30](https://foro3d.com/en/2026/abril/metal-slug-a-los-30-anos-cuando-el-exceso-de-arte-2d-supera-al-3d-mode.html), [Giant Bomb, Metal Slug 2](https://www.giantbomb.com/games/3030-840/), [Metal Slug Wiki, Utan](https://breezewiki.discard.no/metalslug/wiki/Utan).
