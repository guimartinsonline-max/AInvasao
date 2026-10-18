# A Invasão — documento do projeto

Jogo de tiro coop em 2D, estilo Metal Slug, com cangaceiros contra alienígenas no sertão.
Este arquivo reúne tudo o que já foi decidido. Leia antes de qualquer tarefa.

## Como trabalhar comigo (Guilherme)

- Responda em português, de forma direta e concisa. Sem repetir informação.
- Decisões criativas (visual, história, fases, chefes): proponha opções e espere eu aprovar antes de implementar.
- Eu testo no iPhone e no PC pelo endereço do ramo `dev` no Netlify.
- **Custo zero:** nada pago. Nenhuma ferramenta, asset, serviço ou biblioteca paga.

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
- Ataque corpo a corpo: peixeira (equivalente à faca do Metal Slug).
- Com arma pesada, o Lampião segura o desenho da arma (`assets/sprites/armas.png`, empunhadura e boca em `src/quadros.js`).

## Inimigos e refém

- **Caricatos, igual ao Metal Slug:** cabeça grande, olhos e nariz exagerados, poses cômicas. Desenhados em `tools/arte/caricatos.py` (gera os `.txt` em `tools/arte/pixel/`).
- **Soldado da Volante:** quepe, narigão, bigodão, barriga; pânico com suor; variante com escudo de tábuas que segura tiros de frente (granada e peixeira quebram).
- **Xeremita:** cabeçona verde, olho gigante, tentáculos e pistola de raio. O raio sai reto, sem mirar.
- **Morte por arma:** fogo vira carvão e cinza (quadro "tostado"), chumbo arremessa longe, Papo-amarelo derruba de costas, desintegrador derrete, explosão manda alto girando.
- **Refém:** romeiro do mesmo porte do Lampião (chapéu de palha com fitas, barba branca, terço, bornal). Amarrado se debate; solto pula, procura no bornal, entrega o item, bate continência e foge.
- **Disco abdutor:** raio estreito (dá para atirar de lado sem ser puxado); derrubado, cai girando, explode e deixa o item D.

## Fases (rascunho aprovado)

1. Caatinga: primeiro contato e queda do disco.
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
- Armas pickup com munição limitada, além da arma padrão infinita. Itens no chão são letras grandes no estilo Metal Slug.
- **Armas aprovadas:** M Metralhadora Madsen, B Bacamarte, R Rojão de São João, D Raio Desintegrador, C Candeeiro (lança-chamas; deixa o inimigo pegando fogo), P Papo-amarelo (atravessa a fila), E Baladeira (pedras que quicam), F Fogos Buscapé (perseguem o inimigo). Item G dá granadas. Tabela em `src/armas.js`.
- Painel de munição no canto (ARMA e GRANADA), como no Metal Slug.
- Granadas.
- Reféns que dão itens.
- Objetos destrutíveis no cenário: caixotes (podem soltar item, refém ou o bode Fubá) e barris de querosene que explodem em cadeia.
- Checkpoints.
- Coop: reviver o parceiro caído e câmera compartilhada que não deixa ninguém para trás.
- Chefes com máquina de estados, padrões que mudam conforme a vida cai e partes que quebram separadas.

## Técnica

- **Motor:** Phaser (versão estável atual), carregado por CDN. Física Arcade.
- **Estrutura:** projeto com vários arquivos, não HTML único.
  - `index.html`
  - `src/`: código separado por cena (menu, fase, chefe, etc.)
  - `assets/`: sprites, sons, mapas
- **Resolução:** baixa e fixa (cerca de 384×216), ampliada sem borrar (modo pixel art).
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

- **Estilo exatamente igual ao do Metal Slug** (proporções, contorno escuro, volume com vários tons, rostos expressivos, poses exageradas). O que muda é a **paleta** e o tema (sertão), não o estilo.
- Pixel art original. Não copiar sprites, personagens ou cenários do Metal Slug (são da SNK): mesmo estilo, desenhos nossos.
- Personagens e inimigos são desenhados pixel a pixel em `tools/arte/pixel/*.txt` (um caractere por cor, legenda em `tools/arte/pixel.py`).
- Spritesheets PNG geradas por script (`tools/arte/exportar.py`).
- Efeitos de tiro desenhados quadro a quadro em `tools/arte/efeitos_tiro.py`: clarão do cano, balas, impacto, explosão em 8 quadros, fumaça, chama.
- Paleta de cores fixa: `assets/paleta.json` (64 cores: as 32 originais e degraus intermediários). Céu azul e sombras frias equilibrando a terra quente, como no trailer de Metal Slug: Awakening. Não deixar o ambiente todo em tons quentes.
- Sprites de tamanho médio e animações com poucos quadros bem escolhidos, onde a consistência entre quadros se mantém.
- Renderizar e conferir visualmente cada sprite antes de usar.
- Cenário em camadas com parallax.
- O impacto visual vem dos efeitos: explosões grandes, partículas, fumaça, faíscas, cápsulas de bala.

### Game feel (prioridade máxima)

- Tremida de tela nas explosões.
- Inimigo piscando branco ao levar tiro.
- Pequena pausa no impacto forte.
- Tolerância no pulo: ainda pular uma fração de segundo depois de sair da beirada.
- Mortes exageradas e cômicas.

## Som

- Efeitos gerados por script, no estilo sfxr.
- Música chiptune composta em código.
- Voz anunciando a arma ao pegar, gerada em código.

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

**Próximo passo:** etapa 3 (arte base) em teste no iPhone e no PC: armas, inimigos, refém e efeitos. Depois, etapa 4 (fase 1 completa).


