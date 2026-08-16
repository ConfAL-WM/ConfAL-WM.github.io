# assets/ — project-page assets

Generated from the EVAC-C3 repo (`lx/EVAC-C3`). Regeneration scripts live in
[`../tools/`](../tools/).

```text
assets/
├── meta/
│   ├── favicon.png                # generated placeholder (256×256 patch-grid mark)
│   └── og-cover.jpg               # generated placeholder (1200×630, task-01 stills)
├── figures/
│   ├── figure2_confidence_probe.webp   # Method figure (used by the page)
│   └── figure2_confidence_probe.png    # same, lossless source (2726×1501)
├── confidence/                    # 50 tasks × 9 videos = 450 clips
│   ├── task_index.json            # group/slot -> task -> prescreen episode mapping
│   └── group-XX/task-XX/
│       ├── 01.mp4                 # ground-truth frames (aligned to rollout range)
│       ├── 02.mp4                 # EVAC-v1 predicted frames
│       ├── 03.mp4                 # latent error |z_pred − z_gt| pooled to 20×32 (magma)
│       ├── 04.mp4                 # C3 confidence map (RdBu)
│       ├── 05.mp4                 # risk = 1 − confidence (inferno)
│       ├── 06.mp4                 # risk overlaid on the prediction
│       ├── 01l.mp4                # GT latent magnitude (viridis) — latent-space view
│       ├── 02l.mp4                # predicted latent magnitude — latent-space view
│       └── 06l.mp4                # risk overlay on pred latent — latent-space view
├── evolution/                     # 10 episodes × 5 videos (~24 MB)
│   ├── episode_index.json
│   ├── ep130/ ep294/ ep282/ ep325/ ep087/ ep310/   # the six paper episodes
│   └── extra-01 … extra-04/       # blocks_ranking_size, shake_bottle, hanging_mug, dump_bin_bigbin
│       └── {gt,base,v1,frame,frame_patch}.mp4
└── confidence_eval/               # ten webp diagnostics in five groups
    ├── signal_auroc_auprc.webp           # high-error AUROC/AUPRC (latent & pixel)
    ├── signal_traj_scatter.webp          # trajectory scatter · mean aggregation
    ├── reliability_sweep_latent.webp     # reliability across τ (latent)  ── page toggle
    ├── reliability_sweep_pixel.webp      # reliability across τ (pixel)   ── page toggle
    ├── ece_brier_tau_latent.webp         # ECE/Brier vs τ · latent
    ├── ece_brier_tau_pixel.webp          # ECE/Brier vs τ · pixel
    ├── probe_tau_localization.webp       # probe-τ sensitivity: localization (wide)
    ├── probe_tau_calibration.webp        # probe-τ sensitivity: calibration (narrow)
    ├── ema_threshold.webp                # EMA threshold band · full run
    └── ema_threshold_zoom.webp           # EMA threshold band · warmup zoom
```

## Sources

| Asset | EVAC-C3 source |
|---|---|
| confidence videos | `al_runs/robotwin_al/pool_scores/{pred/task_prescreen, c3_task_prescreen_scores}` + RoboTwin2.0 GT frames |
| evolution videos | `1_paper_figure/al_progression_demos/episodes/<ep>/<variant>/` |
| confidence_eval figures | `1_paper_figure/eval_confidence/{01_signal_validity,02_calibration,06_param_sweeps}` |
| figure2 | `Confidence probe training and inference.pdf` (rendered @3×, margins autocropped) |

## Regenerate

```bash
/share/project/robocoin/hywu/miniconda3/envs/enerverse_lx/bin/python3 tools/make_confidence_gallery.py   # ~25 min, 450 videos (768 px, crisp patch grid)
/share/project/robocoin/hywu/miniconda3/envs/enerverse_lx/bin/python3 tools/make_evolution_sets.py       # ~1 min
/share/project/robocoin/hywu/miniconda3/envs/enerverse_lx/bin/python3 tools/make_eval_figures.py         # seconds
```

`--only <task>` rebuilds a single confidence task; `--width` controls clip width
(default 768 px). Map columns (03/04/05/latent views) render the 20×32 grid
nearest-upsampled so patch blocks stay crisp.
