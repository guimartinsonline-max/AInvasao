# A Invasão — o que falta para o jogo ficar "pronto"

Proposta de escopo para a **versão 1.0**: Missão 1 (Caatinga) + Missão 2 (Base da cratera) completas, com começo, meio e fim. Coop online e as fases 3 a 6 ficam para depois do 1.0.
Cada item cabe numa conversa. Ordem = prioridade.

## 1. Fechar o fluxo do jogo (prioridade alta)

1. **Missão 1 emenda na Missão 2.** Hoje o placar da fase 1 volta para o menu. Depois da medalha, ir para a `Fase2` levando pontos, vidas e granadas (como a fase 2 já faz com a 2b). — `src/scenes/Fase1Scene.js` (`contarPontos`), `src/scenes/Fase2Scene.js`
2. **Salvar progresso no aparelho.** Guardar a missão liberada e a melhor medalha/pontos de cada missão; no menu, MISSÃO 2 só liberada depois de vencer a 1 (ou mostrar a medalha ao lado). — `src/ajustes.js`, `src/scenes/MenuScene.js`
3. **Tirar o que está "em breve" do menu.** Esconder COOP ONLINE no 1.0 e atualizar a descrição da MISSÃO 2 ("só a borda da cratera" já está errado). Campo de treino pode ficar. — `src/scenes/MenuScene.js` (linhas 138–142)
4. **Tela de fim de jogo e créditos.** Depois do chefe da fase 2: o alien escapa e chama os outros (gancho), "FIM DA PRIMEIRA PARTE", créditos e volta ao menu. — nova cena em `src/scenes/`, `src/main.js`

## 2. Terminar a Missão 2 (prioridade alta)

5. **Trecho 3: descida no elevador.** Elevador descendo com soldados e contaminados pulando dos andaimes, disco aparecendo. Mostrar uma peça antes de fazer tudo (regra do CLAUDE.md). — `tools/arte/` (novo `fase2c.py`), nova `src/scenes/Fase2cScene.js`, `src/scenes/Fase2bScene.js` (trocar "CONTINUA..." pela passagem)
6. **Trecho 4: laboratório no casco do disco.** Tubos, máquinas, alien na maca, gás verde em trechos. — `tools/arte/`, nova cena, `src/objetos/Base.js`
7. **Gás verde.** Nuvem que deixa lento por uns segundos (já aprovado, falta fazer). — `src/objetos/Ambiente.js` ou `Base.js`, `src/objetos/Jogador.js`
8. **Chefe: professor injetado.** Começa humano atirando e vira monstro em 2–3 estágios; partes que quebram como o trem. Propor opções de golpes antes. — novo `src/objetos/Professor.js`, `tools/arte/`
9. **Desintegrador só na fase 2** e **reféns vaqueiros/romeiros** confirmados nos trechos novos. — `src/objetos/Refem.js`, `assets/fases/fase2*.json`

## 3. Diversão e equilíbrio (prioridade média)

10. **Passada de dificuldade.** Jogar a fase 1 inteira no iPhone e anotar onde morre demais ou fica fácil: vida dos chefes, cadência de tiro da Volante, tempo de 60 s por trecho, quantidade de comida/armas. Ajustar números só nos dados. — `assets/fases/fase1.json`, `src/objetos/Inimigo.js` (`TIPOS`), `src/armas.js`
11. **Primeira vez jogando (tutorial leve).** Dicas curtas no começo da fase 1 (pular, agachar, granada, montar no jumento), só na primeira partida salva. — `src/scenes/Fase1Scene.js`, `src/ajustes.js`
12. **Ritmo da fase 1 (8.600 px).** Ver se algum trecho fica longo sem novidade; se sim, encurtar ou pôr um evento (caminhão, segredo, cena cômica). — `assets/fases/fase1.json`
13. **Nível de dificuldade no menu (opcional).** FÁCIL (mais vidas e continues infinitos) / NORMAL. Ajuda quem joga no toque. — `src/ajustes.js`, `src/scenes/MenuScene.js`, `src/scenes/Fase1Scene.js`

## 4. Acabamento e publicação (prioridade média/baixa)

14. **Funcionar offline como app instalado.** Não há service worker, e o Phaser vem do CDN: sem internet o app instalado não abre. Copiar o `phaser.min.js` para o repositório e adicionar um `sw.js` simples com cache por `VERSAO`. — `index.html`, novo `sw.js`, `src/config.js`
15. **Cache para a versão final.** `netlify.toml` está com `no-cache` em tudo (modo desenvolvimento); no 1.0, deixar cache longo nos `assets/` (já versionados com `?v=`). — `netlify.toml`
16. **Tirar ferramentas de teste do jogo publicado.** Tecla P abre a `PaletaScene` no menu; esconder no ramo `main`. — `src/scenes/MenuScene.js` (linha 39), `src/main.js`
17. **Teste final em aparelho.** 60 fps no iPhone nas partes pesadas (chefe trem, holofotes da 2b), PC com controle e tela grande. Corrigir o que cair. — geral
18. **Atualizar o CLAUDE.md** com o escopo do 1.0 e marcar o que ficou para depois (coop, fases 3–6, carro de boi, Maria Bonita). — `CLAUDE.md`

## Depois do 1.0

- Coop online (WebRTC, já planejado no CLAUDE.md).
- Fases 3 a 6 e veículos novos (carro de boi, disco roubado).
