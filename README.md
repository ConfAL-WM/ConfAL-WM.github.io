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
