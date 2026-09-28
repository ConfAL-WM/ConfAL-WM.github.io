# ConfAL-WM.github.io

## Hero background

The three 15-second reels in `assets/video/hero/` show ground truth, predicted
risk, and risk overlay (the default view), using matching middle 3-second
excerpts from five chapter 3 tasks. `clips.json` records the source
columns and exact frame ranges. Rebuild with:

```sh
python tools/make_hero_reels.py
```

Requires ffmpeg on PATH, or the Python `imageio-ffmpeg` package. Playback uses
one active video; changing views seeks to the same timestamp before revealing
the next video and preserves the user's pause preference. For local preview,
use a server with HTTP byte-range support (as on GitHub Pages) so video seeking
works correctly. Python's basic `http.server` does not provide this support.

## More experiments

Chapter 06 contains confidence diagnostics, the Appendix B.3 probe ablations
(Tables 9–11, Figures 15–19), and the Appendix B.5 budget sweep (Tables 13–14,
Figure 21). Run `python tools/update_experiments.py` to rebuild its HTML and
the Oracle reference rows from the transcribed manuscript data. Export the
high-resolution figures with `python tools/export_appendix_figures.py PAPER.pdf`
(Poppler and Pillow required).

Oracle error is a single seed-42 run. It is repeated as a fixed reference in
all four seed selectors, and its four aggregate values are derived from the
reported nine component scores. It does not represent additional seed runs.
