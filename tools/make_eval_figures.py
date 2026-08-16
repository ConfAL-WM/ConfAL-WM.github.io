#!/usr/bin/env python3

"""Export the confidence-evaluation figures for the project page.

Five figure groups (per the 2026-08-17 spec), each shown side-by-side on the page:

  01 signal validity        auroc/auprc combined  +  trajectory scatter (mean)
  02 reliability sweep      latent vs pixel (page-side toggle)
  03 ece/brier vs tau       latent + pixel
  04 probe-tau sensitivity  localization + calibration  (0.62 : 0.35 width ratio)
  05 ema threshold          evolution + evolution_zoom

Sources are autocropped (white margins) and written as WebP q92 into
assets/confidence_eval/.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path("/share/project/robocoin/hywu/lx/EVAC-C3/1_paper_figure/eval_confidence")
OUT = Path(__file__).resolve().parents[1] / "assets/confidence_eval"

MAPPING = {
    # out name                    repo-relative source                    max width
    "signal_auroc_auprc":       ("01_signal_validity/auroc_auprc/high_error_auroc_auprc_combined.png", 1600),
    "signal_traj_scatter":      ("01_signal_validity/trajectory_scatter/trajectory_scatter_mean.png", 1600),
    "reliability_sweep_latent": ("02_calibration/reliability_sweep_latent.png", 2200),
    "reliability_sweep_pixel":  ("02_calibration/reliability_sweep_pixel.png", 2200),
    "ece_brier_tau_latent":     ("02_calibration/ece_brier_vs_tau_latent.png", 1600),
    "ece_brier_tau_pixel":      ("02_calibration/ece_brier_vs_tau_pixel.png", 1600),
    "probe_tau_localization":   ("06_param_sweeps/probe_tau_localization.png", 2000),
    "probe_tau_calibration":    ("06_param_sweeps/probe_tau_calibration.png", 1400),
    "ema_threshold":            ("06_param_sweeps/ema_threshold_evolution.png", 1600),
    "ema_threshold_zoom":       ("06_param_sweeps/ema_threshold_evolution_zoom.png", 1600),
}


def autocrop(im: Image.Image, thresh: int = 248, pad: int = 12) -> Image.Image:
    a = np.asarray(im.convert("L"))
    mask = a < thresh
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if len(rows) == 0:
        return im
    t, b = max(0, rows[0] - pad), min(im.height, rows[-1] + pad + 1)
    l, r = max(0, cols[0] - pad), min(im.width, cols[-1] + pad + 1)
    return im.crop((l, t, r, b))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (rel, width) in MAPPING.items():
        im = Image.open(SRC / rel).convert("RGB")
        im = autocrop(im)
        if im.width > width:
            h = round(im.height * width / im.width)
            im = im.resize((width, h), Image.Resampling.LANCZOS)
        dst = OUT / f"{name}.webp"
        im.save(dst, "WEBP", quality=92, method=6)
        print(f"[ok] {name}: {im.size} -> {dst.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
