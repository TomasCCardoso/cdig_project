# Semana 1: parâmetros 802.11a, tags e autocorrelação

## 1. Parâmetros do sistema OFDM 802.11a
Valores de memória; confirmar na norma/slides antes de dar como definitivos.

| Parâmetro | Valor |
|---|---|
| Largura de banda | 20 MHz |
| Taxa de amostragem | 20 Msps |
| Tamanho FFT/IFFT | 64 |
| Espaçamento entre subportadoras | 312,5 kHz (20 MHz / 64) |
| Subportadoras usadas / dados / pilotos | 52 / 48 / 4 (pilotos em k = ±7, ±21) |
| Subportadoras não usadas | 12 (DC + 11 nas bordas) |
| Duração do símbolo OFDM | 4 µs (80 amostras) |
| Prefixo cíclico | 16 amostras (0,8 µs) |
| Preâmbulo curto | 10 repetições de 16 amostras = 160 amostras (8 µs) |
| Preâmbulo longo | 32 (GI2) + 2 × 64 = 160 amostras (8 µs) |

Perguntas a responder com justificação:
- Porque existem subportadoras não usadas e onde estão? (DC por causa de offsets do conversor; bordas como banda de guarda para a filtragem)
- Como se chega a 4 µs a partir de 64 + 16 amostras a 20 Msps? (80 / 20 MHz)
- O STS usa só subportadoras múltiplas de 4 (12 não nulas): porque isso dá período de 16 amostras (64 / 4)?

Nota: no flowgraph, o `samp_rate` do `wifi_rx.grc` é escolhível (5, 10, 20 MHz). Com 10 MHz (802.11p) tudo dura o dobro, mas o número de amostras é igual.

## 2. Secção 2.1 do paper: tags
- Onde estão as tags mencionadas? Identificar no código dos blocos `ieee802_11_sync_short`, `sync_long`, `frame_equalizer` e `decode_mac` (início da frame, símbolo dentro da frame, comprimento/encoding). **A preencher com o código.**

## 3. Secção 2.2: deteção de frame (no `wifi_rx.grc` e `wifi_phy_hier.grc`)
Cadeia que calcula c[n] (eq. 1 a 3):

| Passo | Blocos |
|---|---|
| s[n-16] | `Delay` com atraso 16 |
| conj(s[n-16]) | `Conjugate` |
| s[n] · conj(s[n-16]) | `Multiply` (amostras atuais × ramo atrasado e conjugado) |
| a[n], eq. 1 | `Moving Average` complexo, comprimento `window_size` (48), scale 1 |
| \|a[n]\| | `Complex to Mag` |
| p[n], eq. 2 | `Complex to Mag^2` → `Moving Average` real, comprimento `window_size + 16` |
| c[n] = \|a\|/p, eq. 3 | `Divide` (numerador \|a\|, denominador p) |

O resultado do `Divide` vai para a entrada 2 do `OFDM Sync Short` (e para o `QT GUI Time Sink`, que mostra o gráfico tipo Fig. 2). O `Sync Short` recebe ainda as amostras atrasadas e a autocorrelação complexa `a[n]` (para a estimativa do offset de frequência).

Diferenças entre os ficheiros disponibilizados e o paper:
- Threshold: 0,56 (paper mostra ~0,75 na Fig. 2)
- `min_plateau`: 2 (paper: 3 amostras consecutivas)
- Janela da potência: `window_size + 16` (o paper usa a mesma janela nas eq. 1 e 2)
- Atraso para o `Sync Long`: `sync_length` = 320 (a Fig. 1 do paper mostra 240)

## 4. Experiência: gráfico tipo Fig. 2 e efeito de NWin
Código: `experiments/week01_autocorr/autocorr_sim.py` (simulação em numpy da mesma cadeia, sem hardware).

Figuras:
- `results/figures/week01_autocorr_nwin.png`: c[n] para NWin = 16, 32, 48, 64, 96 (SNR 15 dB, threshold 0,56)
- `results/figures/week01_tradeoff_threshold_nwin.png`: probabilidade de deteção (SNR 5 dB) e falsos alarmes só com ruído, por threshold e NWin
- `results/figures/week01_tradeoff_threshold_nwin.csv`: os mesmos dados em tabela

Observações da simulação (a validar com o flowgraph real, ver abaixo):
1. **A altura do plateau depende de NWin.** Como a potência usa `NWin + 16` amostras e a autocorrelação `NWin`, o plateau fica em ≈ NWin / (NWin + 16): 0,50 (NWin=16), 0,67 (32), 0,75 (48), 0,80 (64), 0,86 (96) em SNR alto. Nas simulações a 15 dB os máximos ficaram em ≈ 0,49, 0,66, 0,74, 0,78 e 0,84.
2. **Com NWin = 16 nunca se deteta com threshold 0,56**, porque o plateau (0,5) fica abaixo do threshold. O threshold de 0,56 só faz sentido para NWin ≥ ~32.
3. **O plateau sobe e desce lentamente**: sobe durante ≈ NWin amostras depois do início da frame (+16 do atraso) e desce durante ≈ NWin depois do fim do STS. NWin grande dá curva mais suave (menos ruído), mas deteta mais tarde e o plateau fica mais largo. No threshold 0,56 o primeiro cruzamento ocorre ≈ 36 a 39 amostras depois do início da frame.
4. **Falsos alarmes só com ruído:** com threshold ≥ 0,4 não houve nenhum em 200 000 amostras para nenhum NWin; abaixo de 0,35 aparecem, mais para NWin pequeno.
5. **Deteção por SNR:** a 5 dB, com NWin = 48 a deteção fica a 100 % até threshold 0,55 e cai a zero acima de 0,7, que é o que a altura do plateau prevê. Quanto menor o SNR, mais baixo o plateau (o ruído soma à potência do denominador).

Limitações da simulação: o plateau é "2 amostras consecutivas acima do threshold", uma aproximação do bloco; o sinal tem canal AWGN apenas, sem offset de frequência nem multipercurso.

**Próximo passo (validação):** gravar c[n] do flowgraph real (File Sink de floats depois do `Divide`) e comparar a altura do plateau com a simulação, para NWin = 32, 48, 64 (variável `window_size`).

## Problemas e soluções
- Autenticação SSH no GitHub falhava mesmo com a chave registada; resolvido a usar HTTPS com Personal Access Token.
