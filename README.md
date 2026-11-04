# Recetor IEEE 802.11a em GNU Radio

Projeto de Digital Communications (SDR), 2025-26. Estudo, experimentação e extensão do recetor OFDM 802.11a/g/p de Bloessl et al. (SRIF'13) em GNU Radio.

## Objetivos
- Fazer o recetor funcionar a partir dos ficheiros disponibilizados
- Receber pacotes *over the air* e vê-los em tempo real no Wireshark
- Variar threshold, janela (NWin) e ganho, e analisar o efeito
- Tentar implementar um novo bloco
- Documentar tudo na wiki, com rigor teórico e análise de resultados

## Estrutura do repositório
```
docs/PLANO.md          plano semanal e mapeamento para a grelha de avaliação
docs/wiki/             páginas da wiki (uma por semana) para copiar/sincronizar com a wiki do GitHub
flowgraphs/            flowgraphs .grc (cada variante com nome descritivo)
captures/              ficheiros de amostras IQ e .pcap (ficheiros grandes fora do git)
experiments/weekNN_*/  scripts e notas de cada experiência
results/figures/       figuras usadas na wiki
scripts/               utilitários (plots, análise de .pcap, etc.)
```

## Convenções de trabalho
- Um commit por passo lógico, mensagens no formato `weekNN: o que mudou` (ex.: `week01: gráfico da autocorrelação com NWin=48`)
- Uma branch por experiência maior (`exp/threshold-sweep`, `feat/novo-bloco`), merge para `main` quando estiver validada
- Cada figura na wiki tem o script que a gerou em `experiments/` ou `scripts/`
- Registar problemas e como foram resolvidos em "Problemas e soluções" na página da semana (conta para *problem solving*)

## Estado
Ver [docs/PLANO.md](docs/PLANO.md).

## Referência
B. Bloessl, M. Segata, C. Sommer, F. Dressler, *An IEEE 802.11a/g/p OFDM Receiver for GNU Radio*, SRIF'13.
