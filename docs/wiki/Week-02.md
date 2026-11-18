# Semana 2 — OFDM Sync Short

## 1. Objetivos para esta semana

- Compreender como o OFDM Sync Short identifica o início de uma possível trama IEEE 802.11a.
- Interpretar os parâmetros de deteção e estudar o seu efeito em simulação.
- Identificar as limitações da deteção por autocorrelação e demonstrar uma delas em simulação.

## 2. O que faz o bloco OFDM Sync Short?

O preâmbulo curto de uma trama 802.11a começa com um padrão de 16 amostras que se repete dez vezes. O OFDM Sync Short usa essa repetição para decidir quando começar a encaminhar as amostras recebidas para o Sync Long. Para tomar essa decisão, observa o coeficiente de autocorrelação normalizado `c[n]`, calculado pelos blocos estudados na [Semana 1](Week-01.md).

No estado `SEARCH`, o bloco descarta as amostras enquanto procura um patamar de autocorrelação. Quando o patamar satisfaz os critérios de deteção, o bloco marca a primeira amostra encaminhada com a tag `wifi_start` e passa ao estado `COPY`. A tag assinala um possível início de trama e transporta uma estimativa do desvio de frequência. O bloco obtém essa estimativa a partir da fase da autocorrelação complexa, `arg(a[n])/16`, e usa-a para corrigir as amostras que encaminha.

## 3. Qual é o significado dos limiares de deteção?

| Parâmetro | Valor no flowgraph | Significado |
|---|---:|---|
| `threshold` | 0,8 | Define a altura mínima do patamar. Uma amostra conta quando o coeficiente normalizado `c[n]` é estritamente superior a 0,8. |
| `min_plateau` | 2 | Define a persistência exigida. Na implementação estudada, o contador tem de atingir 2 antes de a amostra seguinte poder desencadear a deteção. |

Com estes valores, a deteção em `SEARCH` ocorre na **terceira amostra consecutiva** com `c[n] > 0,8`. Se surgir uma amostra com `c[n] ≤ 0,8` antes da deteção, o contador volta a zero.

## 4. Efeito da variação dos limiares de deteção

## 5. Limitações do método e demonstração de um caso de falha

- **Deteções falsas.** O bloco procura repetição a uma distância de 16 amostras. Outros sinais periódicos podem apresentar autocorrelação elevada e satisfazer o mesmo critério do preâmbulo Wi-Fi.
- **Inícios de trama próximos.** A secção 2.2 do artigo descreve um recetor que pode perder a segunda trama enquanto copia a primeira. Na implementação estudada (`sync_short.cc`, revisão `ad0598e`), o bloco continua a procurar patamares durante a cópia, mas só aceita outro início após ter copiado mais de 480 amostras desde a última deteção. Um segundo patamar que termine dentro desse intervalo pode passar despercebido.
- **Comprimento máximo de cópia.** Após copiar 43 200 amostras desde a última deteção (2,16 ms a 20 MHz), o bloco regressa a `SEARCH`. Se a trama continuar para além desse ponto, a parte final pode ficar por encaminhar.

### Demonstração em simulação

## 6. Conclusão

Na Semana 1, observámos que a repetição do preâmbulo curto produz um patamar no coeficiente de autocorrelação `c[n]`. Nesta semana, a leitura do código mostrou como o Sync Short usa esse patamar para decidir quando encaminhar amostras para o Sync Long. Na configuração do projeto, três amostras consecutivas com `c[n] > 0,8` desencadeiam a deteção em `SEARCH`. O bloco marca então o possível início de trama com a tag `wifi_start` e aplica uma correção inicial do desvio de frequência.

A principal limitação deste critério é que outros sinais periódicos também podem produzir um patamar. Por isso, cada tag representa um candidato a início de trama. Fica por avaliar em simulação como a escolha dos limiares afeta as deteções na captura e em que condições surge um falso candidato.

### Pontos em aberto (para a Semana 3)

- **Estimativa do desvio de frequência.** O Sync Short guarda em `wifi_start` a rotação estimada em radianos por amostra. Se introduzirmos um desvio de frequência conhecido na mesma captura, de quanto muda essa estimativa? Comparar a tag da mesma trama antes e depois de introduzir o desvio, convertendo a diferença para hertz com `Fs/(2π)`.
- **Entrada atrasada do Sync Long.** Uma entrada recebe a saída do Sync Short diretamente. A outra recebe as mesmas amostras com um atraso de 240 amostras (12 µs a 20 MHz). Que amostras ficam disponíveis neste segundo ramo quando o Sync Long localiza o preâmbulo longo? Seguir os dois ramos no código e verificar como uma alteração do atraso afeta o alinhamento dos símbolos.
