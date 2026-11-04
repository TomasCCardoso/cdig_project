# Semana 2: OFDM Sync Short

## 1. O que faz o bloco
Atua como uma válvula: recebe as amostras e o coeficiente de autocorrelação normalizado. Se deteta um plateau (3 amostras consecutivas acima do threshold), deixa passar um número fixo de amostras; caso contrário descarta.

## 2. Significado dos parâmetros
- Threshold: ...
- Min Plateau: ...
- Max Samples: ...
Localizar cada um no código do bloco e explicar o papel.

## 3. Experiência: variar thresholds
Script: `experiments/week02_sync_short/`

Plano:
1. Threshold = 0,5 / 0,7 / 0,8 / 0,9 / 0,95
2. Para cada um: frames detetadas, falsos positivos, frames perdidas (usar o mesmo ficheiro de amostras)
3. Repetir variando o ganho (ou o nível do sinal/ruído adicionado) para ver a interação threshold × SNR

Tabela de resultados:

| Threshold | Frames detetadas | Falsos positivos | Notas |
|---|---|---|---|
| | | | |

## 4. Limitações e caso em que falha
O paper admite duas limitações:
1. Tamanho máximo da frame limitado a um número fixo de símbolos
2. Frames seguidas (ex.: CTS logo após RTS) perdem-se porque o bloco está a copiar amostras

Demonstrar (2) com uma captura com RTS/CTS, ou construir sinal sintético com duas frames próximas. Outros casos a testar: ruído impulsivo, sinais periódicos que provoquem autocorrelação alta, SNR baixo.

## Problemas e soluções
- ...
