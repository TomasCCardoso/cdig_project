# Plano e mapeamento para a avaliação

Início do trabalho: 2026-11-04 (semanas 1-3 em atraso, a recuperar primeiro).

## Grelha de avaliação → onde fica evidência

| Critério | Pontos | Evidência no repo/wiki |
|---|---|---|
| Funciona a partir dos ficheiros disponibilizados | Implementação (38) | `flowgraphs/`, Wiki: Semana 1 |
| Pacotes over the air | Implementação | `captures/`, Wiki: Semana 8 |
| Real time Wireshark | Implementação | `captures/*.pcap`, print do Wireshark na Wiki |
| Variação: threshold | Implementação | `experiments/week02_sync_short/` |
| Variação: janela (NWin) | Implementação | `experiments/week01_autocorr/` |
| Variação: ganho | Implementação | `experiments/week02_sync_short/` (ganho do USRP/ficheiro) |
| Tentativa de novo bloco | Implementação | branch `feat/novo-bloco`, Wiki: Extras |
| Extras | Implementação | Wiki: Extras |
| Profundidade teórica / rigor | Wiki (30) | respostas às perguntas do roadmap, com equações |
| Análise de resultados | Wiki | figuras + discussão por experiência |
| Estrutura | Wiki | `docs/wiki/Home.md` como índice |
| Wiki + GitHub consistentes | Processo | commits regulares, página por semana |
| Version control | Processo | branches, mensagens claras |
| Problem solving | Processo | secção "Problemas e soluções" em cada semana |

## Calendário (recuperação)

Preencher as datas quando souberes a entrega.

| Semana | Tema | Experiência principal | Estado |
|---|---|---|---|
| 1 | Parâmetros 802.11a, tags, autocorrelação (sec. 2.1-2.2) | Gráfico tipo Fig. 2, varrer NWin | [ ] |
| 2 | OFDM Sync Short, thresholds | Varrer thresholds, caso em que falha | [ ] |
| 3 | Sync Long, offset de frequência (sec. 2.3) | Efeito do atraso/parâmetros | [ ] |
| 4 | Alinhamento de símbolo (sec. 2.4) | Fig. 3, eq. 6-8 no código | [ ] |
| 5 | Correção de fase (sec. 2.5) | Pilotos e regressão linear | [ ] |
| 6 | Equalização e Signal Field (sec. 2.6-2.7) | Descodificar o SIGNAL | [ ] |
| 7 | Payload: demod, deinterleaving, descrambling (sec. 2.8) | | [ ] |
| 8 | Descodificação e AP real (sec. 2.8, 3) | Over the air + Wireshark | [ ] |
