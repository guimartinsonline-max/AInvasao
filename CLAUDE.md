# A Invasão — documento do projeto

Jogo de tiro coop em 2D, estilo Metal Slug, com cangaceiros contra alienígenas no sertão.
Este arquivo reúne tudo o que já foi decidido. Leia antes de qualquer tarefa.

## Como trabalhar comigo (Guilherme)

- Responda em português, de forma direta e concisa. Sem repetir informação.
- Decisões criativas (visual, história, fases, chefes): proponha opções e espere eu aprovar antes de implementar.
- Eu testo no iPhone e no PC pelo endereço do ramo `dev` no Netlify.
- **Custo zero:** nada pago. Nenhuma ferramenta, asset, serviço ou biblioteca paga.
- **Economia de créditos (Claude):**
  - Uma conversa nova por etapa ou por lote de pedidos; este arquivo guarda tudo o que foi decidido. Conversa longa encarece cada passo.
  - Conferir visual com imagens pequenas e recortadas só na área que mudou (uma folha de comparação por rodada, nada de print inteiro de 1096 px a cada ajuste).
  - Antes de mudança visual grande, testar numa peça só e só depois aplicar em tudo.
  - Ler só o trecho do arquivo que vai mexer; saída de comando sempre resumida (`tail`).
  - Teste automático longo (`autoplay`) só no fim do lote, não a cada ajuste.

## Conceito

- **Nome:** A Invasão
- **Gênero:** run and gun 2D com rolagem lateral, estilo Metal Slug.
- **Plataformas:** iPhone e PC, as duas como plataformas principais, com o mesmo código no navegador.
  - **iPhone:** instalado como app na Tela de Início. Modo paisagem, tela cheia, controles de toque.
  - **PC:** instalável como app pelo navegador (Chrome/Edge). Tela cheia, teclado e controle (gamepad), com a imagem escalada em proporção inteira para monitores grandes.
- **Jogadores:** 1 ou 2, coop online entre dois aparelhos quaisquer (iPhone com iPhone, PC com PC ou iPhone com PC).
- **Sem ranking e sem banco de dados.**

## História

Sertão, 1936. Um disco voador cai no Raso da Catarina e os alienígenas começam a abduzir bodes, vaqueiros e romeiros.

O governo manda a Volante (a força militar que caçava cangaceiros) para conter a invasão, mas o comandante quer a tecnologia alienígena para si e vira um segundo inimigo. Lampião e Maria Bonita ficam no meio do fogo cruzado: alienígenas de um lado e Volante do outro.

Na reta final, a Volante é dominada pelos alienígenas e o comandante pede trégua. Os cangaceiros salvam o sertão, que nunca vai agradecer.

**Elementos aprovados:**
- Coronel traidor: fez pacto com os alienígenas em troca da água do açude. Chefe dentro de uma casa-grande que vira robô.
- Beato do fim do mundo: prega que os alienígenas são anjos e é possuído por eles. Chefe com romeiros hipnotizados.
- Reféns: romeiros e vaqueiros amarrados que, soltos, dão arma ou item.
- Bode abduzido: easter egg que aparece em toda fase.

**Rejeitado:** cenas de história em estilo xilogravura. Não usar esse estilo. Granada como "bomba de São João".

## Personagens jogáveis

- **Lampião** e **Maria Bonita**, caricatos no estilo Metal Slug: corpo atarracado, expressões exageradas, animações cômicas.
- Por enquanto só o **Lampião** é jogável; Maria Bonita fica para depois.
- Visual em construção: desenhado **pixel a pixel** (`tools/arte/pixel/lampiao.txt`, gerado por `tools/arte/lampiao_px.py`), estilo Metal Slug: base agachada, inclinado para a frente, poucos acessórios. O mais importante é o **rosto expressivo** e as **poses**.
- Ataque corpo a corpo: peixeira, como a faca do Metal Slug: sai sozinha quando o inimigo está colado e **mata na hora**. Golpe em dois tempos (quadros "facada1" levantando e "facada" descendo) com arco de corte largo (`corte_arco`).
- **No pulo apertando para baixo:** curva a cabeça olhando o chão e aponta a arma para baixo (quadro "mira_baixo", boca `baixo` em `src/maos.js`), como no Metal Slug.
- **Baladeira** anima a cada tiro: solta a liga ("atirando") e puxa a próxima pedra até o rosto ("recarga"). **Madsen** gira a mira aos poucos entre frente e cima, varrendo na diagonal (como a HMG).
- **Morte do Lampião:** sem o chapéu aparece a cabeleira preta de cangaceiro (`CABELO` e `MECHA` em `lampiao_px.py`). Espirra sangue, voa para trás de braços para cima com careta de dor ("morte1") enquanto o chapéu voa girando à parte (`chapeu.png`) e cai do lado; bate de costas no chão com um quique e poeira e fica deitado reto, olhos em X ("morte2", desenhado com as costas no chão e as alpercatas para cima), com a poça de sangue crescendo; pisca e renasce.
- **Gordo:** comer 6 comidas seguidas deixa o Lampião gordo (folhas `*_gordo.png`, esticadas 5 px no meio do corpo): mais lento, pula menos, tiro maior. Emagrece depois de 25 s sem comer ou ao morrer.
- **Jumento blindado** (`tools/arte/jumento.py`, `src/objetos/Jumento.js`): o "tanque" do Lampião. Jegue caricato (cabeçona dentuça, orelhas de ponta preta, crina espetada, pelo riscado, ferraduras) com testeira de ferro com a estrela do cangaço, peitoral de couro cravejado, manta bordada vermelha e amarela com chapas rebitadas, sela de arção alto, alforje, cabaça e joelheiras. **Metralhadora de três canos baixa no ombro** (como a do camelo do Metal Slug): o tiro sai na altura dos soldados; só aponta para baixo no ar de verdade. Nunca afunda no chão. Espera com a placa SUBA!; monta pulando em cima ou apertando para baixo encostado. Metralhadora giratória (frente, diagonal, cima, baixo no ar), canhão no botão de granada (10 bombas no painel), blindagem de 6 tiros (barra JUMENTO no painel). Estourou: o Lampião é jogado para cima e o jumento foge zurrando. Desce com baixo + pulo. Na fase 1 espera no fim da caatinga (x 2680).
- **Mirando para cima** inclina a cabeça para trás e olha para o alto (rosto "cima"); no pulo para baixo, curva a cabeça olhando o chão.
- Arma inicial: **pistola Mauser semiautomática** (um tiro por toque), numa mão só.
- **Cada arma tem o jeito próprio de segurar** (quadros em `tools/arte/lampiao_armas.py`, folhas `lampiao_<arma>.png`): Madsen no quadril, Bacamarte baixo na cintura, Papo-amarelo no ombro mirando, Rojão apoiado no ombro, Desintegrador numa mão só, Candeeiro com a lata nas costas, Baladeira puxando a liga, Buscapé no peito. Braços atrás da arma, só as mãos por cima. **Armas desenhadas à mão, pixel a pixel**, em `tools/arte/pixel/armas_mao.txt` (até 32x15, cerca de 2/3 da altura do Lampião, com coronha, ferrolho, gatilho, pente, braçadeiras e brilho, no tamanho das armas do Metal Slug); âncoras de mão e boca em `tools/arte/armas.py`. Boca do cano gerada em `src/maos.js`.

## Inimigos e refém

- **Caricatos, igual ao Metal Slug, mas no porte do Lampião** (cabeça do tamanho da dele, nada absurdo): olhos e nariz exagerados na medida, poses cômicas. Desenhados em `tools/arte/caricatos.py` (gera os `.txt` em `tools/arte/pixel/`).
- **Soldado da Volante:** quepe, narigão, bigodão, barriga; pânico com suor; variante com **escudo de chapa de aço** (`escudo()` em `objetos.py`, 16x30): oliva gasto mostrando o aço nas quinas, aro rebitado, visor, seteira vazada por onde passa o cano do fuzil, estrela pintada, riscos e amassados; a mão do soldado agarra a borda; balança no passo e dá tranco no tiro; tiro nele solta faísca e, arrebentado, voa em pedaços de chapa. Segura tiros de frente (granada e peixeira quebram).
- **Outros soldados:** granadeiro (dinamite em arco), metralhador (rajada de 4, 5 de vida), sargento do facão (corre e golpeia), soldado de rojão (rojão em arco de longe).
- **Distraídos:** soldados sentados cochilando (Zz) até ver o Lampião ou levar tiro; pulam de susto com "!?".
- **Saem de esconderijo:** nas ondas, pulam de buracos, de trás dos sacos de areia e do lajedo (`salta:x` em `fase1.json`).
- **Sangue** nas mortes dos soldados (o xeremita espirra gosma verde).
- **Xeremita:** cabeçona verde, olho gigante, tentáculos e pistola de raio. O raio sai reto, sem mirar.
- **Morte na peixeira** (como no Metal Slug): grita com a mão para o alto e recua, cai de joelhos e desaba de cara no chão (quadros `facada` em `INIMIGOS`, gerados no exportador por `ajoelhar()` e `deitar()`), poeira, sangue e poça; fica estirado e some piscando.
- **Morte por arma:** fogo vira carvão e cinza (quadro "tostado"), chumbo arremessa longe, Papo-amarelo derruba de costas, desintegrador derrete, explosão manda alto girando.
- **Refém:** romeiro do mesmo porte do Lampião (chapéu de palha com fitas, barba branca, terço, bornal). Amarrado se debate; solto pula, procura no bornal, entrega o item, bate continência e foge. Alguns ficam **pendurados** pelas mãos num galho seco (ou embaixo da ponte): o tiro corta a corda e ele cai. Depois de salvo, foge correndo pela esquerda e pula o que estiver no caminho.
- **Tiro dos soldados sempre reto** (nada de diagonal); dinamite e rojão continuam em arco.
- **Armas inimigas animadas:** todo tiro tem clarão na boca (verde no xeremita), cápsula saltando e tranco do recuo; rojão com jato de fumaça para trás; granadeiro solta faísca do pavio; facão com arco de corte. Veículos: metralhadoras e canhão do trem e do blindado dão o tranco, soltam cápsula e fumaça.
- **Ninguém surge do nada:** soldados entram pela borda da tela, pulam de esconderijos (`salta:x`), saem de portas de casas, capela e barracas (`porta:x`) ou descem de caminhão. No campo de treino, quem renasce entra andando pela borda.
- **Veículos da Volante** (`tools/arte/veiculos.py`, `src/objetos/Veiculos.js`): **caminhão** (chega, freia, abre a lona e despeja soldados, depois vai embora; dá para explodir) e **carro blindado** (detalhado: tripulante na escotilha, antena com flâmula, estepe, pá, galão, farol, rebites e lama; vai e vem, metralhadora em torreta de bola que **avisa antes** (faísca, "!" e o carro para meio segundo) e solta rajada curta de bala grossa na altura da cabeça (agachado escapa, dá para pular por cima), canhão com obus de latão em arco, clarão grande e explosão maior; com metade da vida a torre quebra e perde o canhão; explosão em cadeia). Andando, atropelam o Lampião e esmagam caixotes. Acompanham o terreno.
- **Inteligência dos soldados:** obstáculo baixo (até 26 px) eles pulam, alto (até 74 px) escalam agarrados na borda; na beirada, descem pulando se o Lampião estiver embaixo. Nunca ficam presos (pulo tem tempo limite).
- **Rendição:** chegando perto com arma pesada, soldado às vezes se rende ("NÃO ATIRA!"), treme e foge da tela.
- **Refém de escudo** (`refem: true`): soldado segura um romeiro na frente; tiro de frente não passa (o romeiro grita). Peixeira, granada ou tiro por trás matam o soldado e soltam o romeiro.
- **Oficial** (`oficial`): quepe dourado, medalhas, espada erguida gritando ordens ("AVANÇAR!"), atira de pistola; levou tiro ou o Lampião chegou perto, foge chorando. 500 pontos.
- **Alienígenas só a partir da fase 2** (a fase 1 é só contra a Volante). Campo de treino mantém xeremita e disco.
- **Disco abdutor:** 123x56 (redesenhado 1,4x quando a tela subiu para 548x308), com o piloto xeremita visível na cúpula de vidro; raio estreito (dá para atirar de lado sem ser puxado); derrubado, cai girando, explode e deixa o item D.

## Lote de 18/10 (nível Metal Slug) — feito

- **Cenas cômicas** (`cena` em `inimigos` do `fase1.json`: `truco`, `cozinha`, `foto`; `olha` = lado; `prop: false` no parceiro): soldados jogando truco num caixote ("TRUCO!", "ZAP!"), mexendo o feijão na panela sobre a fogueira, mostrando a foto da noiva chorando para o colega que cochila. Quadros 14 a 19 da folha `volante` (`comico()` em `caricatos.py`), objetos em `tools/arte/cenas_comicas.py`. Ao ver o Lampião: "!?", largam tudo (cartas voando, panela virada, retrato caindo), corridinha de pânico e só então lutam.
- **Medo coletivo** (`Inimigo.js`): granada caindo perto, metade deita de bruços com a mão na cabeça (quadro 13, `brucos`; o corpo fica baixo) e metade foge gritando; colega morreu do lado, às vezes um medroso (volante, granadeiro, rojão, oficial) foge da tela.
- **Jumento kamikaze:** montado, **baixo + granada**: o Lampião salta para trás e o jumento dispara com o pavio aceso e explode no que bater (ou em 1,7 s). Dica aparece na primeira montada.
- **Biplano "O GAVIÃO" (subchefe)** (`tools/arte/aviao.py`, `src/objetos/Biplano.js`): parado de rabo no chão no campo de pouso; na onda o motor engasga ("PÓ! PÓ-PÓ!") e taxia acelerando (hélice e rodas matam); derrubado no chão dá bônus "NEM DECOLOU!". Se decola, volta em passadas alternando o lado: alto soltando 3 bombas e, a cada três, rasante. Artilheiro de trás é parte separada (morto, para de atirar). 4 etapas de dano, fumaça e fogo, cai em parafuso.
- **Fase 1 com 8.600 px:** depois da vila entram a **vila alta** (3.880 a 4.880) e o **campo de pouso** (4.880 a 5.980); o resto andou 2.100 px.
  - **Vila alta** (`tools/arte/vila_campo.py`): casario de platibanda colorido e desbotado; o topo de cada casa é plataforma de um lado só, toldos de bodega são o degrau para subir, degrau sólido só lá em cima entre casas coladas de alturas diferentes. **Por cima:** menos soldados e o ninho-segredo. **Pela rua:** mais luta (metralhador nos sacos, oficial, escudo) e um refém extra.
  - **Campo de pouso:** hangar de zinco, marcas de pneu, balizas, tanque de gasolina, tambores na pista (o biplano esmaga e explodem nele), biruta.
- **Tiros passam pelas plataformas de um lado só** (telhado, girau, toldo), menos quando descem.
- **Segredos** (`segredos` no `fase1.json`, `src/objetos/Segredos.js`): cacimba (refém escondido), ninho de galinha no telhado (arma), canoa do rio seco (buchada), biruta (granadas). Brilham discreto de vez em quando; abertos dão 1000 e "SEGREDO!".
- **Entrada de chefe** (`chefe` na onda): música corta, chão treme crescendo, poeira cai, apito (trem) ou motor engasgando (biplano), e a faixa vermelha com CHEFE/SUBCHEFE, nome e título. Depois do subchefe a música da fase volta.
- **Fim da missão:** o Lampião pula atirando para o alto (montado, a metralhadora do jumento), os reféns salvos chegam correndo, pulam e batem continência ("VIVA O CAPITÃO!") e o bode Fubá passa berrando; depois o placar.
- **Carcaças destroçadas** (`tools/arte/destrocos.py`): o último quadro de caminhão, blindado e trem não é só queimado: teto amassado, corpo partido com a ponta caída, rasgos (os de cima atravessam, os do meio mostram o escuro de dentro), chapa virada, brasas e pedaços no chão. Biplano (`destrocado()` em `aviao.py`): lona queimada mostrando o esqueleto, cauda partida no chão, asa de cima desabada, hélice de uma pá só. Ao explodir voam pedaços de chapa (`estilhacos` em `src/efeitos.js`) e depois do fogo fica um fio de fumaça.
- **Jumento sem teletransporte:** a correção de "afundar no chão" só age em afundada de até 8 px; plataforma ou caixote mais alto não puxa mais o jumento para cima.
- **Espera do Lampião:** parado 3,5 s sem fazer nada, olha para trás, ajeita o chapéu suando (aparece a cabeleira) e boceja (quadros `espera1` a `espera3`, rostos `boceja`, `olha`, `suor`).
- **Vida dos chefes +40%:** biplano 100 (artilheiro 14); trem: metralhadoras 42, chaminé 36, torre 48, porta 56. O biplano decola rápido (engasga ~1 s e taxia ~2 s) e não leva dano antes da partida.
- **Arena do trem com giraus de carga** em dois níveis (`GIRAUS_ARENA` em `fase1.py`): do alto, o tiro reto alcança a chaminé e a torre. Bravo, o trem avança só 44 px (não encosta nos giraus).
- **Trem redesenhado no nível do Metal Slug** (`trem.py`): cabine com janelas acesas e o maquinista em contraluz, placa "07" de latão, escada e lanterna; caldeira com reflexo, cintas, saia blindada, corrimão, canos de cobre com flanges, válvulas vermelhas, bomba de ar, sino, apito, arame farpado e sacos; farol grande, placa redonda, estribo e limpa-trilhos listrados; rodas com contrapeso e manivelas. Vagão com janelas acesas e a tropa, ninho de metralhadora de sacos, caixotes, tambor, lona, letreiro e truques com molas. Chaminé com cintas e tela de faíscas; torre com canhão de freio de boca, artilheiro espiando e flâmula. Vapor saindo dos cilindros e da válvula.
- **Barril de querosene detalhado** (`objetos.py`): cilindro com luz de lado, aros salientes, tampa com bujão e respiro, losango de inflamável, tinta descascada, ferrugem, amassado e mancha na base; furado esguicha querosene.
- **Projéteis em arco** (dinamite, rojão, obus, carvão do trem, bomba do biplano) atravessam plataformas de um lado só: girau e telhado não protegem quem está embaixo nem seguram o tiro do trem.
- **Transformação** (além do gordo): fica para a fase 3. Recusados: Maria Bonita agora; faixa com o nome da arma pega.

## Fases (rascunho aprovado)

1. Caatinga: só contra a Volante, **sem alienígenas**. **Em construção** (`src/scenes/Fase1Scene.js`; arte e dados em `tools/arte/fase1.py`, que gera as camadas `f1_*.png` e `assets/fases/fase1.json`): 8.600 px em 6 trechos: caatinga (casa de taipa com a Volante entrincheirada, lajedo em degraus, curral com cata-vento, barranco), **vila de taipa** (casas, capela e cruzeiro; soldados saem pelas portas e chega um caminhão), **vila alta** e **campo de pouso** (ver lote de 18/10), **leito de rio seco** (barrancos, ponte de tábuas por cima, carnaúbas, canoa encalhada) e **acampamento da Volante** (barracas, trincheiras, torre de vigia, mastro, caminhão e o **carro blindado** no fim). **Arena do chefe** no fim com trilhos. 10 ondas que travam a câmera (a borda desliza até a trava, nunca pula), câmera que não volta, "CONTINUAR?" no lugar (sem checkpoint, como no Metal Slug). Caixotes e reféns não soltam o desintegrador nesta fase. **Final:** um disco voador passa pegando fogo pelo céu e cai atrás dos morros com explosão ao longe e coluna de fumaça (gancho para a fase 2), depois a contagem de pontos.
   - **Chefe: trem blindado "A JARARACA"** (`tools/arte/trem.py`, `src/objetos/Trem.js`): locomotiva da Great Western blindada com vagão de soldados; entra pelos trilhos e apita. Partes que quebram separadas: metralhadoras do limpa-trilhos (avisam e atiram ALTO, agacha, ou BAIXO, pula), chaminé (cospe carvão em brasa em arco), torre do canhão (obus). Sem metralhadoras e chaminé, a porta da fornalha abre (ponto fraco) e o trem avança e recua; porta arrebentada explode a caldeira em cadeia.
   - **Cenário vivo** (`src/objetos/Ambiente.js`): urubus que voam quando o Lampião chega, galinhas que fogem do tiro e viram galinha assada no fogo (800), varal que a explosão arrebenta, casas da vila que perdem o telhado, ponte que a granada quebra por pedaços.
   - **Comidas** (`tools/arte/comidas.py`): cajá 100, rapadura 300, queijo coalho 500, galinha assada 800, cuscuz 1000, buchada 2000. Saem de caixotes e reféns.
2. Cidade do interior em dia de feira: invasão e chegada da Volante.
3. Trem da Great Western: fase em movimento.
4. Açude e casa-grande: chefe coronel.
5. Romaria: chefe beato.
6. Raso da Catarina, nave-mãe: chefe final.

Uma fase na fazenda pode entrar depois, como conteúdo extra.

## Veículos

- Jumento blindado com metralhadora (veículo principal, equivalente ao tanque do Metal Slug).
- Carro de boi com canhão.
- Disco alienígena roubado, na fase final.

## Mecânicas

- Correr, pular, agachar, atirar para frente, para cima e para baixo no ar.
- Armas pickup com munição limitada, além da arma padrão infinita. Itens no chão são **caixas quadradas de chapa com a letra da arma** no meio, no estilo Metal Slug. Drop de armas reduzido: caixote solta arma em ~17% das vezes (e comida em ~25%); refém dá arma (30%), granadas (25%) ou comida (45%).
- **Armas aprovadas:** M Metralhadora Madsen, B Bacamarte, R Rojão de São João, D Raio Desintegrador, C Candeeiro (lança-chamas; deixa o inimigo pegando fogo), P Papo-amarelo (atravessa a fila), E Baladeira (pedras que quicam), F Fogos Buscapé (perseguem o inimigo). Item G dá granadas. Tabela em `src/armas.js`.
- Painel de munição no canto (ARMA e GRANADA), como no Metal Slug.
- Caixas de arma no chão dão um clarão leve de tempos em tempos (não ficam brancas).
- **Arma grande:** pegar a mesma arma de novo deixa ela SUPER (tiro 1,5x maior e mais forte, munição somada).
- **Pontos:** sobem no lugar de cada inimigo (100 a 300), disco 1000, refém 500, caixote 10, barril 50. No fim da missão: pontos, reféns salvos x 1000 e total. Sem ranking.
- **Tempo:** 60 por trecho (anda devagar, como no fliperama); zerou, perde uma vida. Recomeça a cada onda vencida.
- Granadas.
- Reféns que dão itens.
- Objetos destrutíveis no cenário: caixotes (podem soltar item, refém ou o bode Fubá) e barris de querosene que explodem em cadeia.
- Checkpoints.
- Coop: reviver o parceiro caído e câmera compartilhada que não deixa ninguém para trás.
- Chefes com máquina de estados, padrões que mudam conforme a vida cai e partes que quebram separadas.

## Tela de início e opções

- No jeito do Metal Slug (`src/scenes/MenuScene.js`): cena pintada em pixel art no pôr do sol (Lampião grande atirando, disco puxando o bode, blindado e soldados, explosões ao fundo), coluna da direita com o logo e placas penduradas em correntes, caixa de baixo explicando o item escolhido.
- Menu: MISSÃO 1, CAMPO DE TREINO, COOP ONLINE (apagado, em breve), OPÇÕES.
- Opções no mesmo layout: volume dos efeitos e da música (0 a 10), tremida de tela (sim/não), troca das teclas do teclado (some no toque), restaurar padrão. Guardado no aparelho (`src/ajustes.js`, localStorage).
- **Pausa** (ESC, Back do controle ou botão II no toque): continuar, volumes, tremida, sair para o menu.
- **Painel:** retrato do Lampião com as vidas, mudando de cara (atirando, susto, dor, morto, gordo).
- **Fim da missão:** pontos, reféns, precisão dos tiros, vidas perdidas e **medalha de bronze, prata ou ouro do cangaço**.

## Técnica

- **Motor:** Phaser (versão estável atual), carregado por CDN. Física Arcade.
- **Estrutura:** projeto com vários arquivos, não HTML único.
  - `index.html`
  - `src/`: código separado por cena (menu, fase, chefe, etc.)
  - `assets/`: sprites, sons, mapas
- **Resolução:** fixa em **548×308** (era 384×216; subiu para os personagens ficarem 30% menores na tela, com pixels menores, como no Metal Slug), ampliada sem borrar. O mundo mantém o chão em y=192; a câmera começa em y=-DY (`DY` em `src/config.js`) e o que é preso à tela desce DY. Botões de toque escalados para manter o tamanho no vidro.
- **Camadas grandes** da fase vão em pedaços de 2048 px (`f1_*_N.png`, contagem em `src/fase1_pedacos.js`, gerado pelo exportador), por causa do limite de textura do iPhone.
- **Segurança contra queda:** chão sólido com 200 px de espessura; Lampião, jumento e inimigos que caírem abaixo do mapa voltam para o chão.
- **Desempenho:** meta de 60 fps estáveis no iPhone. Reaproveitar balas, inimigos e partículas (object pooling), sem criar e destruir objetos durante o jogo.
- **Cache:** todo arquivo de `assets/` é carregado com `?v=VERSAO` (`src/config.js`). Ao mudar qualquer asset, aumentar a versão (`tools/arte/exportar.py` já faz isso).
- **Fases:** feitas por Claude em código ou dados. Tiled pode ser adotado depois, se eu quiser desenhar fases.

### Coop online

- P2P via WebRTC, como no meu jogo anterior (Treta na Fazenda).
- TURN grátis do Open Relay (Metered) para funcionar entre redes diferentes.
- Um celular é o host e decide inimigos, tiros e drops. O outro replica.
- Enviar só o que mudou, compactado, para não pesar na rede.
- Implementar só depois de a primeira fase estar boa no modo solo.

## Arte

- **Passagem entre ambientes sempre suave** (regra fixa): nenhum trecho começa com corte reto. Chão de outro tipo entra misturando (`colar_suave`), barrancos descem em curva e espalham terra no chão, pedras e construções usam o material da região. Vale para toda fase nova.
- **Nível de detalhe do cenário:** o das referências do Metal Slug que o Guilherme mandou (MS2/MS3): volume em tudo, textura, rachaduras, líquen, chão em corte com camadas e pedras, várias camadas de parallax e uma de frente.
- **Estilo exatamente igual ao do Metal Slug** (proporções, contorno escuro, volume com vários tons, rostos expressivos, poses exageradas). O que muda é a **paleta** e o tema (sertão), não o estilo.
- Pixel art original. Não copiar sprites, personagens ou cenários do Metal Slug (são da SNK): mesmo estilo, desenhos nossos.
- **Repintura** (`tools/arte/repintar.py`), aplicada na exportação: Lampião (camisa em 7 tons com vincos do cinturão e dobra no peito, couro com brilho na borda de cima, costura na faixa do chapéu e marcas de uso, calça com volume; rosto e arma intocados), soldados e refém (luz no corpo inteiro, farda e roupa com volume e dobras suaves).
- **Lataria dos veículos e do trem** (`tools/arte/blindagem.py`, aplicada na exportação): pintura lisa em faixas (sem granulado), chapas com emenda e rebite, quinas com brilho e sombra, tinta descascada mostrando o metal, ferrugem escorrendo de rebites e lama na parte de baixo (só na pintura, rodas limpas).
- **Rodas girando de verdade:** 4 quadros por volta, no ritmo da distância andada (para trás quando recua), com poeira saindo de cada roda e nuvenzinha atrás; o trem também gira as rodas com a biela e solta faísca no trilho.
- **Dano progressivo na lataria** (`danificar()` em `blindagem.py`): cada folha de veículo e do trem tem 4 etapas (inteiro, furos de bala e amassados, chamuscado e rachaduras, rasgos abertos com brasa); a etapa sobe a cada 25% da vida (no trem, a cada parte quebrada) com estalo e estilhaços de chapa; na etapa 2 sai fumaça e na 3 pega fogo. Folhas: `n` quadros por etapa e o destruído no fim (`VEICULOS` em `src/quadros.js`).
- Personagens e inimigos são desenhados pixel a pixel em `tools/arte/pixel/*.txt` (um caractere por cor, legenda em `tools/arte/pixel.py`). Quadros: Lampião 60x72 (pé em 14,63), inimigos e refém 52x46, com folga para as armas (mirando para cima e para baixo) não cortarem.
- Spritesheets PNG geradas por script (`tools/arte/exportar.py`).
- Efeitos de tiro desenhados quadro a quadro em `tools/arte/efeitos_tiro.py`: clarão do cano, balas, impacto, fumaça, chama. **Explosão no nível do Metal Slug** (`explosao_ms`, 12 quadros, 56 px e 34 px na pequena): clarão com raios, bola de fogo em gomos com línguas de fogo e estilhaços, fumaça escura crescendo por cima do fogo e cogumelo que sobe e se desfaz. Depois dela fica **fumaça pairando** no ar (`fumacaFica` em `src/efeitos.js`). **Poeira desenhada** (`poeira_passo`) nos passos, no pulo e na queda. Cápsulas quicam mais e ficam 2,6 s no chão.
- Paleta de cores fixa: `assets/paleta.json` (64 cores: as 32 originais e degraus intermediários). Céu azul e sombras frias equilibrando a terra quente, como no trailer de Metal Slug: Awakening. Não deixar o ambiente todo em tons quentes.
- Sprites de tamanho médio e animações com poucos quadros bem escolhidos, onde a consistência entre quadros se mantém.
- Renderizar e conferir visualmente cada sprite antes de usar.
- Cenário em camadas com parallax. Paredão de arenito (768 px) e chão em corte gerados em `tools/arte/rocha.py`: blocos irregulares com volume próprio, juntas, rachaduras, líquen, moitas, tálus e perspectiva aérea (fundo mais claro e de menor contraste). Serras em duas fileiras com volume; morros com textura de capim, pedrinhas e moitas. **Giraus** (`girau()` em `fase1.py`): forquilhas de tronco com casca, travessas em X amarradas com corda, viga roliça, piso de tábuas com tábua empenada e cabaça pendurada. **Sacos de estopa** (`sacos_detalhados()`): estufados, com orelhas amarradas, costura, vincos e um furado vazando areia. **Barrancos do rio seco** (`cabeceira()`): encosta em curva com camadas acompanhando o corte, raízes, capim pendendo, rampa de terra espalhando no chão do lado de fora e cabeceira de pedra bruta encaixada (sem tijolo) com viga de tora por baixo da ponte. **Caixotes de munição** (`caixas_municao()`): com face de cima (tampa), um aberto com os pentes de latão e a tampa largada no chão; ficam atrás da barricada e ao pé da torre de vigia. **Lajedo** com faces lascadas, líquen em manchas, escorridos e pedregulhos na base. Construções passam por `envelhecer()` (`fase1.py`): sujeira subindo da base e escorridos do beiral; caiação da capela lisa; lona da barraca com dobras; mandacaru com gomos de aresta clara.
- O impacto visual vem dos efeitos: explosões grandes, partículas, fumaça, faíscas, cápsulas de bala.

### Game feel (prioridade máxima)

- Tremida de tela nas explosões.
- Inimigo piscando branco ao levar tiro.
- Pequena pausa no impacto forte.
- Tolerância no pulo: ainda pular uma fração de segundo depois de sair da beirada.
- Mortes exageradas e cômicas.

## Som

Tudo em `src/som.js` (Web Audio):
- **Tiros, explosões e bateria são amostras mp3** em `assets/sons/` (27 arquivos, ~180 KB), geradas por `tools/som/gerar_sons.py` (numpy + ffmpeg): cada tiro em camadas (estalo, estrondo grave, corpo, mecânica da arma e eco do sertão), saturado e comprimido no espírito do Metal Slug. Um som por arma, fuzil da Volante, bala pesada (blindado/trem), canhão, explosão pequena/média/grande, impacto e ricochete, peixeira. Tom varia um pouco a cada disparo. Se o Guilherme mandar um pacote CC0 de tiros gravados, é só trocar os mp3.
- O resto (menus, comida, refém, zurro, apito, galinha) é sintetizado na hora; também cobre os tiros enquanto as amostras carregam.
- **Trilha de ação** tocada em tempo real: bateria de rock com zabumba, guitarra distorcida em acordes de quinta, baixo em colcheias, metais nas viradas e melodia na sanfona (na segunda volta, guitarra solo com eco). Tema baião-rock (início), xaxado-rock em ré dório com duas seções (fase 1), galope com bumbo duplo em lá menor harmônico (chefe), fanfarra de metais (vitória), lamento (continuar?).
- **Sem locutor/dublagem** (removido a pedido).

## Publicação

- Repositório no GitHub: `AInvasao`.
- **Ramos:**
  - `dev`: todo o desenvolvimento. O Netlify publica como branch deploy, grátis e ilimitado.
  - `main`: versão oficial. Só recebe o `dev` nos marcos (fim de cada etapa).
- Claude envia as mudanças direto para o `dev` (autorizado), além do ramo de trabalho da sessão.
- Cada deploy de produção (`main`) custa 15 créditos do Netlify. Tenho 1.000 créditos por mês no plano Personal, compartilhados com outros projetos. Nunca publicar direto no `main` durante o desenvolvimento.
- No Netlify:
  - Ativar branch deploys para o ramo `dev`.
  - Desligar o selo em Project configuration → General → Powered by Netlify badge.
- Manter os arquivos leves, porque o tráfego também consome créditos.

## Ferramentas grátis permitidas

- Phaser, GitHub, Netlify, Open Relay.
- Piskel ou LibreSprite (retoque de sprites, opcional).
- Tiled (opcional).
- BeepBox (música, opcional).
- Google Fonts (fonte pixel).

## Plano de etapas

1. **Estrutura:** projeto Phaser, ramos `main` e `dev`, Netlify ligado, resolução e paleta definidas.
2. **Controle e sensação:** controles de toque no iPhone (direcional virtual, tiro, pulo, granada), teclado e controle no PC, com detecção automática do que está em uso; movimento e tiro do Lampião; game feel. Só avança quando correr e atirar com um inimigo parado já for divertido no iPhone e no PC.
3. **Arte base:** personagens com todas as animações, 2 ou 3 inimigos comuns, cenário com parallax, explosões.
4. **Fase 1 completa:** rolagem, ondas de inimigos, armas pickup, granadas, reféns, destrutíveis, trecho de veículo, checkpoints.
5. **Chefe da fase 1.**
6. **Som:** efeitos, voz das armas e música.
7. **Coop online.**
8. **Desempenho:** 60 fps no iPhone e no PC, testando também em tela grande.
9. **Acabamento:** tela de título, seleção de personagem, pausa, game over com "continuar?", progresso salvo no celular.
10. **Mais conteúdo:** fases 2 a 6, repetindo as etapas 4 a 6.

**Próximo passo:** fase 1 com chefe, veículo e som prontos; ajustar com o teste do Guilherme antes da fase 2. Campo de treino continua no menu.


