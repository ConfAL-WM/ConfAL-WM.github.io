#!/usr/bin/env python3
"""Embed per-seed self-bootstrap CIs for the Figure 6 seed views into index.html.

Source: each per-seed eval JSON's `self_bootstrap_0.95CI` (the pipeline behind
al_runs/robotwin_al/eval/pooled_mean_risk_episode_level.json; seed convention:
no filename suffix = seed 42). The JSON aggregates use the raw per-episode sums:

  Reconstruction = psnr + ssim          -> page bars use (psnr+ssim)/2  => /2
  Semantics      = logics+CLIP+BLEU     -> page bars use (logics+CLIP+BLEU)/3 => /3
  Motion         = hsd+dyn+ndtw         -> same scale                    => x1
  scene_consistency                     -> same scale                    => x1

The resulting `const SEED_CI = {...};` block is injected right after PAPER_DATA
and consumed by renderFigure6 for seed != 'mean' error bars.
"""
import json
import re
from pathlib import Path

EVAL = Path("/share/project/robocoin/hywu/lx/EVAC-C3/al_runs/robotwin_al/eval")
PAGE = Path("/share/project/robocoin/hywu/lx/ConfAL-WM.github.io/index.html")

SEEDS = ["42", "3407", "123"]

# figure-6 variant keys -> eval json stem ('' seed suffix = seed 42)
KEYS = [
    "warmup",
    "random",
    "roboreward_mean_risk_none",
    "gvl_mean_risk_none",
    "robometer_prog_mean_risk_none",
    "robometer_prog_mean_risk_frame",
    "robometer_pref_mean_risk_none",
    "robometer_pref_mean_risk_frame",
    "prm_judge_mean_risk_none",
    "prm_judge_mean_risk_frame",
    "lrms_mean_risk_none",
    "lrms_mean_risk_frame",
    "c3_mean_risk_none",
    "c3_mean_risk_frame",
    "c3_mean_risk_frame_patch",
]

# JSON aggregate -> (page category, scale factor)
MAP = {
    "ewmbench.Reconstruction": ("Reconstruction", 0.5),
    "ewmbench.scene_consistency": ("Scene", 1.0),
    "ewmbench.Motion": ("Motion", 1.0),
    "ewmbench.Semantics": ("Semantics", 1.0 / 3.0),
}

SHARED = {"warmup": "warmup_none", "random": "random_random_none"}


def json_for(key: str, seed: str) -> Path:
    if key in SHARED:
        return EVAL / f"{SHARED[key]}.json"
    return EVAL / f"{key}_{seed}.json" if seed != "42" else EVAL / f"{key}.json"


def main() -> None:
    seed_ci: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    for seed in SEEDS:
        for key in KEYS:
            path = json_for(key, seed)
            if not path.exists():
                print(f"[warn] missing {path.name}")
                continue
            sb = json.loads(path.read_text()).get("self_bootstrap_0.95CI", {})
            for jkey, (cat, scale) in MAP.items():
                v = sb.get(jkey)
                if v is None:
                    print(f"[warn] {path.name}: no {jkey}")
                    continue
                seed_ci.setdefault(seed, {}).setdefault(key, {})[cat] = {
                    "lower": v["lower"] * scale,
                    "upper": v["upper"] * scale,
                }
    for seed in SEEDS:
        n = sum(len(v) for v in seed_ci.get(seed, {}).values())
        print(f"seed {seed}: {n} CI entries")

    html = PAGE.read_text()
    anchor = re.search(r'const PAPER_DATA\s*=.*?\n', html)
    js = f"\nconst SEED_CI = {json.dumps(seed_ci, separators=(',', ':'))};\n"
    html = html[: anchor.end()] + js + html[anchor.end():]
    PAGE.write_text(html)
    print("SEED_CI embedded after PAPER_DATA")


if __name__ == "__main__":
    main()
