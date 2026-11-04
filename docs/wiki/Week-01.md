# Semana 1: parâmetros 802.11a, tags e autocorrelação

## 1. Parâmetros do sistema OFDM 802.11a
Confirmar na norma/slides e preencher.

| Parâmetro | Valor |
|---|---|
| Largura de banda | 20 MHz |
| Taxa de amostragem | 20 Msps |
| Tamanho FFT/IFFT | 64 |
| Espaçamento entre subportadoras | 312,5 kHz (20 MHz / 64) |
| Subportadoras usadas / dados / pilotos | 52 / 48 / 4 |
| Subportadoras não usadas | 12 (DC + guardas) |
| Duração do símbolo OFDM | 4 µs (80 amostras) |
| Prefixo cíclico | 16 amostras (0,8 µs) |
| Preâmbulo curto | 10 repetições de 16 amostras = 160 amostras (8 µs) |

Perguntas a responder com justificação:
- Porque existem subportadoras não usadas e onde estão? (relacionar com DC e filtragem nas bordas da banda)
- Como se chega ao valor de 4 µs a partir de 64 + 16 amostras a 20 Msps?

## 2. Secção 2.1 do paper: tags
- Onde estão as tags mencionadas? Identificar no flowgraph e no código dos blocos (início da frame, comprimento/encoding).

## 3. Secção 2.2: deteção de frame
- Blocos que calculam a autocorrelação (eq. 1): ...
- Blocos que calculam a potência (eq. 2): ...
- Normalização (eq. 3): ...
- Porque se usa lag 16 e porque a janela atua como filtro passa-baixo (média móvel)?

## 4. Experiência: gráfico tipo Fig. 2 e efeito de NWin
Script: `experiments/week01_autocorr/`

Plano:
1. Gravar c[n] para uma frame (File Sink após o Divide)
2. Plot de c[n] com threshold (0,8 a título de exemplo) e marcação do plateau
3. Repetir para NWin = 16, 32, 48, 64, 96
4. Medir para cada: largura do plateau, atraso do início, ruído fora do plateau

Resultados: (figuras em `results/figures/`)

Análise: (efeito de NWin no compromisso entre ruído e resolução temporal)

## Problemas e soluções
- ...
