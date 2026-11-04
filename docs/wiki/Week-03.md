# Semana 3: OFDM Sync Long e correção de offset de frequência

## 1. Algoritmo (secção 2.3, eq. 4-5)
Se há offset de frequência, s[n]·conj(s[n+16]) deixa de ser real: o argumento da soma corresponde a 16 vezes a rotação por amostra.

df = (1/16) · arg( Σ s[n]·conj(s[n+16]) ), com s[n] ← s[n]·e^(j·n·df)

Notas para explicar:
- Porque se usa o argumento da soma e não a média dos argumentos (amostras pequenas pesam menos, mais robusto a ruído)
- Gama de offsets estimável sem ambiguidade com lag 16: |df| < π/16 rad/amostra, ou seja ±625 kHz a 20 Msps (confirmar contas)

## 2. Questões do roadmap
- Onde está implementado? (ficheiro e função no bloco Sync Long)
- Que parâmetros se podem variar?
- Porque há uma entrada atrasada (Delay: 240 no flowgraph)? Se se alterar o valor, qual o impacto? Relacionar com o tempo de processamento do Sync Short e com a posição do preâmbulo longo na janela de amostras.

## 3. Experiência
Script: `experiments/week03_freq_offset/`

Plano:
1. Aplicar offset de frequência conhecido a um ficheiro de amostras (multiplicar por e^(j2πΔf·t/fs))
2. Comparar o df estimado com o real para Δf = 0, ±10, ±50, ±100 kHz
3. Verificar quando a descodificação deixa de funcionar
4. Variar o atraso e observar o efeito

Tabela:

| Δf real (kHz) | Δf estimado (kHz) | Frame descodificada? |
|---|---|---|
| | | |

## Problemas e soluções
- ...
