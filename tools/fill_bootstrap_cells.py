#!/usr/bin/env python3
"""Fill the three missing single-seed paired-bootstrap cells in index.html.

Authoritative source: each per-seed eval JSON's `paired_bootstrap_delta_0.95CI`
block (evaluate_al_round.py output; seed convention: no filename suffix = seed 42).
The seed-42 roboreward row reproduces the page's embedded values to 4 decimals,
so the same files are used to fill:

  seed 42  c3_mean_risk_frame          -> c3_mean_risk_frame.json
  seed 42  gvl_mean_risk_none          -> gvl_mean_risk_none.json
  seed 3407 c3_mean_risk_frame_patch   -> c3_mean_risk_frame_patch_3407.json

Page cell fields: Reconstruction / scene_consistency / Motion / Semantics.
"""
import json
import re
import sys
from pathlib import Path

EVAL = Path("/share/project/robocoin/hywu/lx/EVAC-C3/al_runs/robotwin_al/eval")
PAGE = Path("/share/project/robocoin/hywu/lx/ConfAL-WM.github.io/index.html")

TARGETS = {
    ("42", "c3_mean_risk_frame"): "c3_mean_risk_frame.json",
    ("42", "gvl_mean_risk_none"): "gvl_mean_risk_none.json",
    ("3407", "c3_mean_risk_frame_patch"): "c3_mean_risk_frame_patch_3407.json",
}

AGG_FIELDS = {
    "Reconstruction": "ewmbench.Reconstruction",
    "scene_consistency": "ewmbench.scene_consistency",
    "Motion": "ewmbench.Motion",
    "Semantics": "ewmbench.Semantics",
}


def main() -> None:
    html = PAGE.read_text()
    m = re.search(r'"bootstrap":(\{.*?\}),"evolution":', html, re.S)
    boot = json.loads(m.group(1))

    for (seed, key), fname in TARGETS.items():
        ci = json.loads((EVAL / fname).read_text())["paired_bootstrap_delta_0.95CI"]
        row = next(r for r in boot[seed] if r["key"] == key)
        for field, jkey in AGG_FIELDS.items():
            v = ci[jkey]
            row[field] = {"mean": v["mean"], "lower": v["lower"], "upper": v["upper"]}
            print(
                f"seed {seed:4s} {key:28s} {field:18s} "
                f"[{v['lower']:+.4f}, {v['upper']:+.4f}] ({v['mean']:+.4f})"
            )

    new_json = json.dumps(boot, separators=(",", ":"))
    html = html[: m.start(1)] + new_json + html[m.end(1):]
    PAGE.write_text(html)

    # post-check: no null aggregate cells remain in any seed
    nulls = [
        (s, r["key"], f)
        for s, rows in boot.items()
        for r in rows
        for f in AGG_FIELDS
        if r.get(f) is None
    ]
    print("remaining null cells:", nulls)
    if nulls:
        sys.exit(1)
    print("index.html patched, all cells filled.")


if __name__ == "__main__":
    main()
