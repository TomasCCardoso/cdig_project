#!/usr/bin/env python3
"""
Semana 1 - Deteção de trama (Secção 2.2 do paper): coeficiente de autocorrelação c[n].

Reproduz em NumPy a cadeia de blocos do flowgraph:

    a[n] = sum_{k=0}^{N-1} s[n-k] * conj(s[n-k-16])      (Delay 16 + Conj + Multiply + FIR [1]*N)
    p[n] = sum_{k=0}^{N-1} |s[n-k]|^2                    (Complex to Mag^2 + FIR [1]*N)
    c[n] = |a[n]| / p[n]                                 (Complex to Mag + Divide)

e permite:
  1. validar contra a saída real do GNU Radio (File Sink ligado ao Divide);
  2. fazer o varrimento de N_win sem voltar a correr o flowgraph;
  3. gerar figuras e um CSV de estatísticas para a wiki.

Exemplos:
  python3 scripts/plot_autocorr.py --samples captures/Sample1_20MHz_Channel36.bin
  python3 scripts/plot_autocorr.py --samples captures/Sample1_20MHz_Channel36.bin \
      --gr-output results/c_gr.bin --windows 8 16 32 48 96 192
"""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

LAG = 16          # período do preâmbulo curto (amostras)
FS = 20e6         # taxa de amostragem (Hz)


# --------------------------------------------------------------------------- #
# Cálculo
# --------------------------------------------------------------------------- #
def moving_sum(x, n):
    """Soma móvel causal de n termos (equivalente ao FIR [1]*n, sem compensar atraso)."""
    cs = np.cumsum(x, dtype=np.complex128 if np.iscomplexobj(x) else np.float64)
    out = cs.copy()
    out[n:] = cs[n:] - cs[:-n]
    return out


def autocorr_coeff(s, n_win, lag=LAG):
    """Devolve (|a|, p, c) alinhados com s (mesmo comprimento)."""
    s = s.astype(np.complex128)
    prod = np.zeros_like(s)
    prod[lag:] = s[lag:] * np.conj(s[:-lag])      # Delay(16) -> zeros iniciais
    a = np.abs(moving_sum(prod, n_win))
    p = moving_sum(np.abs(s) ** 2, n_win).real
    c = a / np.maximum(p, 1e-20)
    return a, p, c


def find_plateaus(c, thr, min_len):
    """Índices de início de cada patamar: >= min_len amostras consecutivas com c > thr."""
    above = c > thr
    edges = np.diff(above.astype(np.int8), prepend=0, append=0)
    starts = np.flatnonzero(edges == 1)
    ends = np.flatnonzero(edges == -1)
    return [(s, e) for s, e in zip(starts, ends) if e - s >= min_len]


def stats(c, plateaus):
    """Nível do patamar, piso de ruído e largura média dos patamares."""
    mask = np.zeros(len(c), dtype=bool)
    for s, e in plateaus:
        mask[s:e] = True
    return {
        "n_plateaus": len(plateaus),
        "plateau_mean": float(c[mask].mean()) if mask.any() else float("nan"),
        "noise_mean": float(c[~mask].mean()),
        "noise_std": float(c[~mask].std()),
        "noise_max": float(c[~mask].max()),
        "plateau_width_mean": float(np.mean([e - s for s, e in plateaus])) if plateaus else float("nan"),
    }


# --------------------------------------------------------------------------- #
# Figuras
# --------------------------------------------------------------------------- #
def fig_overview(c, plateaus, thr, n_win, out):
    # max-pooling por blocos: mantém os patamares visíveis em ficheiros grandes
    blk = max(1, len(c) // 20000)
    cp = c[: len(c) // blk * blk].reshape(-1, blk).max(axis=1)
    t = np.arange(len(cp)) * blk / FS * 1e3
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.plot(t, cp, lw=0.6)
    ax.axhline(thr, color="r", ls="--", lw=0.8, label=f"threshold = {thr}")
    for s, e in plateaus:
        ax.axvspan(s / FS * 1e3, e / FS * 1e3, color="g", alpha=0.25)
    ax.set(xlabel="tempo (ms)", ylabel="c[n]", ylim=(0, 1.05),
           title=f"Coeficiente de autocorrelação, N_win={n_win}  ({len(plateaus)} patamares)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def fig_zoom(c, a, p, start, length, thr, n_win, out):
    idx = np.arange(start, start + length)
    fig, axs = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
    axs[0].plot(idx, c[idx]); axs[0].axhline(thr, color="r", ls="--", lw=0.8)
    axs[0].set(ylabel="c[n]", ylim=(0, 1.05), title=f"Zoom na primeira trama (N_win={n_win})")
    axs[1].plot(idx, a[idx], color="C1"); axs[1].set_ylabel("|a[n]|")
    axs[2].plot(idx, p[idx], color="C2"); axs[2].set(ylabel="p[n]", xlabel="amostra n")
    for ax in axs:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def fig_sweep(s, windows, start, length, thr, out):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    idx = np.arange(start, start + length)
    for n in windows:
        _, _, c = autocorr_coeff(s, n)
        ax.plot(idx, c[idx], lw=1, label=f"N_win = {n}")
    ax.axhline(thr, color="k", ls="--", lw=0.8)
    ax.set(xlabel="amostra n", ylabel="c[n]", ylim=(0, 1.05),
           title="Efeito de N_win no coeficiente de autocorrelação")
    ax.legend(ncol=2, fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def fig_validation(c_np, c_gr, start, length, out):
    """Compara NumPy vs saída do GNU Radio numa janela; procura desfasamento fixo (+-64 amostras)."""
    m = min(len(c_np), len(c_gr))
    n = min(length, m - start - 128)
    ref = c_np[start + 64: start + 64 + n]
    best_lag, best_err = 0, np.inf
    for lag in range(-64, 65):
        b = c_gr[start + 64 + lag: start + 64 + lag + n]
        err = np.mean(np.abs(ref - b))
        if err < best_err:
            best_lag, best_err = lag, err
    idx = np.arange(start + 64, start + 64 + n)
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(idx, ref, label="NumPy")
    ax.plot(idx, c_gr[start + 64 + best_lag: start + 64 + best_lag + n], "--",
            label=f"GNU Radio (desfasamento {best_lag})")
    ax.set(xlabel="amostra n", ylabel="c[n]", title=f"Validação (erro médio absoluto = {best_err:.2e})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return best_lag, best_err


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples", required=True, help="ficheiro de amostras complexas (complex64, formato GNU Radio)")
    ap.add_argument("--gr-output", help="saída float32 do File Sink ligado ao Divide (validação)")
    ap.add_argument("--n-win", type=int, default=48, help="janela principal (default 48)")
    ap.add_argument("--windows", type=int, nargs="+", default=[8, 16, 32, 48, 96, 192])
    ap.add_argument("--threshold", type=float, default=0.8)
    ap.add_argument("--min-plateau", type=int, default=3, help="amostras consecutivas acima do threshold")
    ap.add_argument("--max-samples", type=int, default=20_000_000,
                    help="nº máx. de amostras lidas (default 20M = 1 s; 0 = todas, precisa de muita RAM)")
    ap.add_argument("--zoom-length", type=int, default=600)
    ap.add_argument("--out", default="results", help="pasta de saída")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    s = np.fromfile(args.samples, dtype=np.complex64, count=args.max_samples or -1)
    print(f"{len(s)} amostras lidas ({len(s) / FS * 1e3:.2f} ms @ 20 Msps)")

    a, p, c = autocorr_coeff(s, args.n_win)
    plateaus = find_plateaus(c, args.threshold, args.min_plateau)
    st = stats(c, plateaus)
    print("Estatísticas (N_win=%d):" % args.n_win)
    for k, v in st.items():
        print(f"  {k}: {v}")

    fig_overview(c, plateaus, args.threshold, args.n_win, out / "w1_c_overview.png")

    if plateaus:
        first = plateaus[0][0]
        z0 = max(first - 100, 0)
        fig_zoom(c, a, p, z0, args.zoom_length, args.threshold, args.n_win, out / "w1_c_zoom.png")
        fig_sweep(s, args.windows, z0, args.zoom_length, args.threshold, out / "w1_window_sweep.png")
    else:
        print("Nenhum patamar encontrado: baixa o threshold ou verifica o formato do ficheiro.")
        z0 = 0

    # estatísticas por janela -> CSV
    with open(out / "w1_window_stats.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n_win", "n_plateaus", "plateau_mean", "plateau_width_mean",
                    "noise_mean", "noise_std", "noise_max"])
        for n in args.windows:
            _, _, cn = autocorr_coeff(s, n)
            sn = stats(cn, find_plateaus(cn, args.threshold, args.min_plateau))
            w.writerow([n, sn["n_plateaus"], f"{sn['plateau_mean']:.4f}", f"{sn['plateau_width_mean']:.1f}",
                        f"{sn['noise_mean']:.4f}", f"{sn['noise_std']:.4f}", f"{sn['noise_max']:.4f}"])
    print(f"CSV: {out / 'w1_window_stats.csv'}")

    if args.gr_output:
        c_gr = np.fromfile(args.gr_output, dtype=np.float32, count=len(s))
        lag, err = fig_validation(c, c_gr, z0, args.zoom_length, out / "w1_validation.png")
        print(f"Validação vs GNU Radio: desfasamento={lag} amostras, erro médio abs={err:.2e}")

    print(f"Figuras guardadas em {out}/")


if __name__ == "__main__":
    main()
