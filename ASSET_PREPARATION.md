# ConfAL-WM Project Page — Asset Preparation Guide

Target URL: **https://ConfAL-WM.github.io**

The supplied `index.html` is a zero-build GitHub Pages page: CSS and JavaScript are embedded in the HTML. You only need to place the assets below in the expected folders and replace the TODO URLs.

## 1. Recommended repository layout

```text
ConfAL-WM.github.io/
├── index.html
├── ASSET_PREPARATION.md
└── assets/
    ├── meta/
    │   ├── favicon.png
    │   └── og-cover.jpg
    ├── videos/
    │   └── teaser.mp4
    ├── figures/
    │   └── figure2_confidence_probe.webp
    ├── confidence/
    │   ├── group-01/
    │   │   ├── task-01/
    │   │   │   ├── 01.mp4   # Ground-truth frame/video
    │   │   │   ├── 02.mp4   # Predicted frame/video
    │   │   │   ├── 03.mp4   # Predicted latent error
    │   │   │   ├── 04.mp4   # Predicted confidence
    │   │   │   ├── 05.mp4   # Predicted risk
    │   │   │   └── 06.mp4   # Risk overlay
    │   │   ├── task-02/ ... task-05/
    │   ├── group-02/ ... group-10/
    ├── evolution/
    │   ├── ep130/
    │   │   ├── gt.mp4
    │   │   ├── base.mp4
    │   │   ├── v1.mp4
    │   │   ├── frame.mp4
    │   │   └── frame_patch.mp4
    │   ├── ep294/
    │   ├── ep282/
    │   ├── ep325/
    │   ├── ep087/
    │   ├── ep310/
    │   └── extra-01/ ...                    # optional additional episodes
    └── confidence_eval/
        ├── fig5_multiscale_validity.webp
        ├── fig10_risk_aggregation.webp
        ├── fig11_spatial_agreement.webp
        ├── fig12_calibration.webp
        ├── fig14_sensitivity.webp
        └── fig09_ema_threshold.webp
```

## 2. Hero / top section

No background image is required. The technology-style background is generated in JavaScript using a responsive canvas: trajectory-like lines, moving action signals, reference-frame planes, and future-frame planes.

Prepare:

- `assets/meta/favicon.png`: square, ideally 256×256 or 512×512.
- `assets/meta/og-cover.jpg`: social preview, recommended 1200×630.
- `assets/videos/teaser.mp4`: the first large project video. Recommended 16:7 to 16:9, H.264 MP4, 1080p if possible, muted-friendly.

Replace the five TODO links in `index.html`:

- arXiv
- Paper
- Code
- Checkpoints
- Datasets

Each is already configured with `target="_blank"`.

Also replace the anonymous author line when the page is public.

## 3. Method section

Export the final **Figure 2: Training and inference of the confidence probe in the UNet latent diffusion world model** as:

```text
assets/figures/figure2_confidence_probe.webp
```

Recommended:

- crop tightly around the figure itself;
- width 2200–3200 px;
- WebP quality 90–95, or edit the HTML to use PNG/SVG;
- transparent or dark-compatible background is ideal, but white is also supported.

The four method callout cards are already written in HTML and require no asset.

## 4. Confidence visualization — 50 tasks

The page uses **10 groups × 5 tasks**, with **6 videos per task**. Use the large Previous / Next buttons or drag the group progress slider. Navigation wraps cyclically from Group 10 back to Group 1 and vice versa.

Column order is fixed:

1. Ground-truth frame/video
2. Predicted frame/video
3. Predicted latent error
4. Predicted confidence
5. Predicted risk
6. Risk overlay

For each task create six MP4 files named `01.mp4` ... `06.mp4` in the exact folder pattern shown above.

The page currently knows the first few paper task names and uses TODO task labels for the rest. Search in `index.html` for:

```js
const KNOWN_TASKS = ...
const CONF_TASKS = ...
```

Replace this with your exact 50 task names. The folder IDs can remain `task-01` ... `task-50`; only visible titles need to change.

### Video encoding recommendation

For the many gallery videos, keep files small:

```bash
ffmpeg -i input.mp4 -an -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p -movflags +faststart output.mp4
```

Recommended width: 480–720 px per cell. The HTML lazy-loads and pauses off-screen videos, but 300 videos can still be heavy; compressed MP4 is important.

## 5. Active-learning numerical results

### Tables

**No table-image assets are required.** The detailed, aggregated, and bootstrap values are embedded directly in `index.html`. Tables are rendered on a bright paper-like surface so the green / yellow / light-red ranking highlights remain clear.

The staged animation is implemented in HTML/CSS:

1. table frame, headers, text, and numbers appear together;
2. first-place cells turn green and bold;
3. second-place cells turn yellow;
4. third-place cells turn light red.

Ranking is computed independently inside the selection-only and additional-weighting blocks. Table 5 uses the bootstrap **paired mean** for the ranking color; its parenthetical gain/loss is also rendered in green/red text according to sign.

### Figure 6

**No Figure-6 image assets are required anymore.** The 2×4 bar-chart grid is generated directly in JavaScript from the embedded experiment values, following the paper plotting style. Mean / seed 42 / seed 3407 / seed 123 are all rendered from code.

Animation order is:

1. axes, titles, labels, grid, and legend;
2. all bars rise together;
3. all improvement/degradation arrows and percentage labels appear together.

If you change final experiment values later, update the `PAPER_DATA` object in `index.html`; no figure re-export is necessary.

## 6. Qualitative evolution videos

The default paper episodes are already configured:

```text
place burger fries   ep130
place empty cup      ep294
put object cabinet  ep282
stack blocks two    ep325
stack bowls three   ep087
turn switch          ep310
```

Each episode needs five synchronized videos:

```text
gt.mp4
base.mp4
v1.mp4
frame.mp4
frame_patch.mp4
```

The corresponding Table-9-style metrics are already embedded. The page renders them as a **compact responsive table** beside each five-video episode strip. No additional metric-table asset is required. The table automatically fits the available width and highlights the hovered row with a subtle gray background.

The evolution gallery uses five cyclic groups of six episodes. Group 1 is the six paper episodes. For extra episodes, create folders such as `assets/evolution/extra-01/` and replace the placeholder names, IDs, and metrics in the JavaScript. The large Previous / Next buttons and the progress slider control the group.

## 7. Detailed confidence evaluation

The shared result panel switches among six compact figures. Export the paper/appendix plots to:

```text
assets/confidence_eval/fig5_multiscale_validity.webp
assets/confidence_eval/fig10_risk_aggregation.webp
assets/confidence_eval/fig11_spatial_agreement.webp
assets/confidence_eval/fig12_calibration.webp
assets/confidence_eval/fig14_sensitivity.webp
assets/confidence_eval/fig09_ema_threshold.webp
```

Recommended width: 1600–2400 px. Crop away paper margins/captions and keep only the plot itself.

The page also displays a compact metric strip derived from the paper:

- Patch / Frame / Task Spearman: 0.540 / 0.590 / 0.595
- Top-5% patch AUROC: 0.761
- Adjacent-frame top-region IoU: 0.740
- Risk flicker: 0.005
- Peak temporal correlation: 0.602

## 8. Models and datasets section

No binary assets are needed locally; replace the TODO links with Hugging Face / GitHub URLs.

### Models planned on the page

1. EVAC Warmup v1
2. EVAC-v2 — weighting None
3. EVAC-v2 — weighting Frame
4. EVAC-v2 — weighting Frame + Patch
5. Confidence Probe — RoboTwin2.0
6. Confidence Probe — AgiBot World
7. YOLO — RoboTwin2.0 trajectory detector

### Data / evaluation artifacts planned on the page

1. **50-task prescreen package** — EVAC-v1 inference, confidence scores / risk maps, and JSON metadata.
2. **EVAC-v2 training · inference + JSON** — precomputed inference outputs and episode metadata for the selected training pool.
3. **EVAC-v2 training · dense confidence + JSON** — dense confidence/risk outputs and scoring metadata used for confidence-guided retraining.
4. **Baseline selection · v1 inference results** — v1 inference results for samples selected by other acquisition baselines.
5. **Baseline weighting · v2 frame-scoring data** — frame-level scoring artifacts used by the additional-weighting baselines.
6. **YOLO RoboTwin2.0 annotations** — robot-arm trajectory labels derived from RoboTwin2.0 action conditions.
7. **Evaluation tables & bootstrap JSON** — mean / seed-wise metrics and pooled paired-bootstrap statistics.

There is no AgiBot demo-video strip in the page now. The AgiBot-trained confidence probe remains listed as a downloadable model checkpoint only.

## 9. Citation

Search for this block in `index.html` and replace it once the paper becomes public:

```bibtex
@article{confalwm2026,
  title   = {ConfAL-WM: Confidence-Guided Active Learning for Action-Conditioned World Models},
  author  = {Anonymous Authors},
  journal = {arXiv preprint},
  year    = {2026},
  url     = {https://ConfAL-WM.github.io}
}
```

The page already has a one-click copy button.

## 10. Deployment to GitHub Pages

The simplest deployment is a repository named:

```text
ConfAL-WM/ConfAL-WM.github.io
```

Place `index.html` and `assets/` at repository root, then enable GitHub Pages from the default branch. With the repository/organization setup matching the URL, the page will be served at:

```text
https://ConfAL-WM.github.io
```

No npm, bundler, or build step is required.

## 11. Final checklist

- [ ] Replace five top buttons with real URLs.
- [ ] Replace anonymous authors / affiliations.
- [x] Add favicon and OG preview. *(generated placeholders in `assets/meta/`; replace with branded versions if desired)*
- [ ] Add teaser video. *(01 · Overview still shows the TODO overlay until `assets/videos/teaser.mp4` exists)*
- [x] Export Figure 2. *(from `Confidence probe training and inference.pdf` @3×, autocropped → `assets/figures/figure2_confidence_probe.webp`)*
- [x] Prepare 50 × 6 confidence visualization videos. *(300 clips, ~66 MB total, CRF 26 @512px; real task names wired into `KNOWN_TASKS`; mapping in `assets/confidence/task_index.json`)*
- [x] Add six default qualitative-evolution episode video sets. *(+ 4 extras → group 2; `EVO_GROUP_COUNT=2`)*
- [x] Add optional additional evolution episodes. *(extra-01…04 with real metrics embedded in `EVO_EXTRA`)*
- [x] Export six compact confidence-evaluation figures. *(see mapping in `assets/README.md`; tab labels updated to match the actual plots)*
- [ ] Replace all model/data TODO download links.
- [ ] If additional corrected single-seed bootstrap CIs are produced later, update the corresponding `PAPER_DATA.bootstrap` entries.
- [ ] Update BibTeX when public.
- [ ] Test desktop, 13-inch laptop, tablet, and phone widths.
- [ ] Test Safari/Chrome autoplay: all gallery videos are muted + playsinline.
- [x] Keep the repository reasonably small. *(90 MB total assets; GitHub Pages soft limit 1 GB — fine without LFS.)*

## 12. Notes from the first asset pass (2026-08)

- The PDF `ConfAL_WM__Confidence_Guided_Active_Learning_for_Action_Conditioned_World_Models.pdf`
  in this folder is **corrupted** (passed through a UTF-8 text channel: ~2.5 M U+FFFD
  replacement bytes; every Flate stream is destroyed — no tool can open it). Re-export
  from the LaTeX source if you need to re-read the paper here. Figure/Table numbers on
  the page were therefore kept from the earlier draft and cross-checked against
  `EVAC-C3/1_paper_figure/**` outputs.
- Confidence-gallery column 3 ("Predicted latent error") uses the **latent oracle**
  `|latent_pred − latent_gt|` mean-pooled to the 20×32 conf grid — identical pooling to
  `eval/confidence_eval/core/io_utils.py`, and identical colorization to
  `eval/al_results/visualize_val_results.py`, so page videos match the paper's
  qualitative panels.
- The evolution "Episode metrics" side tables use the **aggregate** columns
  (Reconstruction = (PSNR+SSIM)/2, Scene, Semantics, Motion) from
  `1_paper_figure/al_progression_demos/DELIVERY_SUMMARY.md` — the same source the
  paper's Table-9-style numbers come from.

