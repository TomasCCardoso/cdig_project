#!/usr/bin/env python3
"""Semana 1 - Autocorrelação do preâmbulo curto 802.11a (equivalente a Fig. 2 do paper).

Reproduz em numpy a cadeia de deteção do flowgraph (wifi_phy_hier.grc / wifi_rx.grc):

    prod[n] = s[n] * conj(s[n-16])             (Delay 16 + Conjugate + Multiply)
    a[n]    = moving_average(prod, N)          (soma, scale=1)       -> eq. (1)
    p[n]    = moving_average(|s|^2, N + 16)    (soma, scale=1)       -> eq. (2)
    c[n]    = |a[n]| / p[n]                    (Complex to Mag / Divide) -> eq. (3)

N = window_size (NWin). No ficheiro original: window_size = 48, threshold = 0.56, min_plateau = 2.

Nota: a regra "plateau = min_plateau amostras consecutivas acima do threshold" é uma aproximação
do bloco OFDM Sync Short. Confirmar contra lib/sync_short.cc do gr-ieee802-11.

Uso:
    python3 autocorr_sim.py [--outdir ../../results/figures]
"""
import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- sinal 802.11a
# STS: subportadoras k = -26..26, apenas k múltiplos de 4 não nulos (periodo 16 amostras)
_STS_NZ = {-24: 1 + 1j, -20: -1 - 1j, -16: 1 + 1j, -12: -1 - 1j, -8: -1 - 1j, -4: 1 + 1j,
           4: -1 - 1j, 8: -1 - 1j, 12: 1 + 1j, 16: 1 + 1j, 20: 1 + 1j, 24: 1 + 1j}
# LTS: 64 valores em ordem "shifted" (DC no índice 32), tal como em wifi_phy_hier.grc
_LTS = np.array([0, 0, 0, 0, 0, 0, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, -1, -1, 1, 1,
                 -1, 1, -1, 1, 1, 1, 1, 0, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1,
                 1, -1, -1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 0, 0, 0, 0], dtype=complex)


def _ifft_shifted(vec64):
    return np.fft.ifft(np.fft.ifftshift(vec64))


def make_frame(rng, n_data_syms=10):
    """Frame sem ruído: 10x16 (STS) + 32 GI2 + 2x64 (LTS) + símbolos de dados (QPSK, CP 16)."""
    S = np.zeros(64, dtype=complex)
    for k, v in _STS_NZ.items():
        S[32 + k] = v * np.sqrt(13 / 6)
    sts64 = _ifft_shifted(S)
    assert np.allclose(sts64[:16], sts64[16:32]), "STS devia ter período 16"
    sts = np.tile(sts64[:16], 10)                          # 160 amostras
    lts64 = _ifft_shifted(_LTS)
    lts = np.concatenate([lts64[-32:], lts64, lts64])      # 160 amostras
    data = []
    used = [k for k in range(-26, 27) if k != 0]
    for _ in range(n_data_syms):
        X = np.zeros(64, dtype=complex)
        for k in used:
            X[32 + k] = (rng.choice([-1, 1]) + 1j * rng.choice([-1, 1])) / np.sqrt(2)
        t = _ifft_shifted(X)
        data.append(np.concatenate([t[-16:], t]))
    frame = np.concatenate([sts, lts] + data)
    return frame / np.sqrt(np.mean(np.abs(frame) ** 2)), len(sts)


def awgn(n, var, rng):
    return np.sqrt(var / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))


def scenario(rng, snr_db, pad_front=300, pad_tail=300, n_data_syms=10):
    frame, n_sts = make_frame(rng, n_data_syms)
    nvar = 10 ** (-snr_db / 10)                            # potência do sinal = 1
    x = np.concatenate([np.zeros(pad_front), frame, np.zeros(pad_tail)]).astype(complex)
    x += awgn(len(x), nvar, rng)
    return x, pad_front, n_sts


# --------------------------------------------------------------- cadeia de deteção
def moving_sum(x, n):
    c = np.cumsum(np.concatenate([[0], x]))
    out = np.empty(len(x), dtype=c.dtype)
    out[n - 1:] = c[n:] - c[:-n]
    out[:n - 1] = c[1:n]                                   # arranque parcial (sem importância)
    return out


def autocorr_coeff(s, nwin, lag=16):
    s_del = np.concatenate([np.zeros(lag, dtype=complex), s[:-lag]])
    prod = s * np.conj(s_del)
    a = moving_sum(prod, nwin)
    p = moving_sum(np.abs(s) ** 2, nwin + lag)
    return np.abs(a) / np.maximum(p, 1e-12)


def triggers(c, thr, min_plateau=2):
    """Índices onde começa um plateau (>= min_plateau amostras consecutivas acima de thr)."""
    above = c > thr
    idx, run = [], 0
    for i, v in enumerate(above):
        run = run + 1 if v else 0
        if run == min_plateau:
            idx.append(i)
    return idx


# --------------------------------------------------------------------- experiências
def fig_nwin(outdir, rng_seed=1, snr_db=15, thr=0.56, windows=(16, 32, 48, 64, 96)):
    rng = np.random.default_rng(rng_seed)
    x, start, n_sts = scenario(rng, snr_db)
    fig, axs = plt.subplots(len(windows), 1, figsize=(9, 9), sharex=True)
    rows = []
    for ax, nw in zip(axs, windows):
        c = autocorr_coeff(x, nw)
        above = np.where(c > thr)[0]
        above = above[(above > start - 50) & (above < start + n_sts + 200)]
        first = above[0] if len(above) else None
        last = above[-1] if len(above) else None
        ax.plot(c, lw=1)
        ax.axhline(thr, ls="--", c="r", lw=0.8)
        ax.axvline(start, c="g", lw=0.8)
        ax.axvline(start + n_sts, c="g", ls=":", lw=0.8)
        ax.set_ylabel(f"NWin={nw}")
        ax.set_ylim(0, 1.1)
        if first is not None:
            rows.append((nw, first - start, last - first + 1))
    axs[0].set_title(f"c[n] para vários NWin (SNR={snr_db} dB, threshold={thr})")
    axs[-1].set_xlabel("índice da amostra  (verde: início da frame e fim do STS)")
    axs[-1].set_xlim(start - 100, start + n_sts + 150)
    fig.tight_layout()
    path = os.path.join(outdir, "week01_autocorr_nwin.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return rows, path


def fig_tradeoff(outdir, snr_db=5, windows=(16, 32, 48, 64, 96),
                 thrs=np.round(np.arange(0.3, 0.96, 0.05), 2), trials=200, noise_len=200_000, seed=2):
    rng = np.random.default_rng(seed)
    noise = awgn(noise_len, 1.0, rng)                      # só ruído, para falsos alarmes
    scen = [scenario(rng, snr_db) for _ in range(trials)]
    pd = np.zeros((len(windows), len(thrs)))
    pfa = np.zeros_like(pd)                                # triggers por milhão de amostras
    for i, nw in enumerate(windows):
        cn = autocorr_coeff(noise, nw)
        cs = [autocorr_coeff(x, nw) for x, _, _ in scen]
        for j, thr in enumerate(thrs):
            pfa[i, j] = len(triggers(cn, thr)) / noise_len * 1e6
            hit = 0
            for c, (_, st, nsts) in zip(cs, scen):
                tr = [t for t in triggers(c, thr) if st - 20 <= t < st + nsts + nw]
                hit += bool(tr)
            pd[i, j] = hit / trials
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    for i, nw in enumerate(windows):
        a1.plot(thrs, pd[i], marker="o", ms=3, label=f"NWin={nw}")
        a2.semilogy(thrs, np.maximum(pfa[i], 1e-1), marker="o", ms=3, label=f"NWin={nw}")
    a1.set(xlabel="threshold", ylabel="P(deteção)", title=f"Deteção da frame (SNR={snr_db} dB)")
    a2.set(xlabel="threshold", ylabel="falsos alarmes / 1M amostras",
           title="Só ruído (mínimo representado: 0,1)")
    a1.grid(alpha=0.3)
    a2.grid(alpha=0.3)
    a1.legend(fontsize=8)
    fig.tight_layout()
    path = os.path.join(outdir, "week01_tradeoff_threshold_nwin.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    csv = os.path.join(outdir, "week01_tradeoff_threshold_nwin.csv")
    with open(csv, "w") as f:
        f.write("nwin,threshold,pd,false_alarms_per_Msamples\n")
        for i, nw in enumerate(windows):
            for j, thr in enumerate(thrs):
                f.write(f"{nw},{thr},{pd[i, j]:.3f},{pfa[i, j]:.2f}\n")
    return path, csv


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(__file__), "..", "..", "results", "figures"))
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    rows, p1 = fig_nwin(args.outdir)
    print("NWin | atraso do 1.º cruzamento vs início da frame (amostras) | largura do plateau (amostras)")
    for r in rows:
        print(f"{r[0]:4d} | {r[1]:5d} | {r[2]:5d}")
    p2, csv = fig_tradeoff(args.outdir)
    print("figuras:", p1, p2, csv)
