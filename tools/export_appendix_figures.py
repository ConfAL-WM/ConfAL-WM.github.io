#!/usr/bin/env python3
"""Export the B.3/B.5 figures from the paper at 432 dpi (without captions).

Usage: python tools/export_appendix_figures.py PAPER.pdf [--pdftoppm PATH]
Requires Poppler and Pillow. Crop rectangles are in PDF points (72 dpi).
"""
import argparse
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

FIGURES = {
    "fig15-shared-thresholds": (24, (120, 208, 489, 344)),
    "fig16-paired-effects": (26, (120, 82, 489, 212)),
    "fig17-noise-transfer": (26, (120, 273, 489, 409)),
    "fig18-error-alignment": (27, (120, 82, 489, 209)),
    "fig19-qualitative": (27, (124, 272, 490, 418)),
    "fig21-budget-curves": (29, (108, 265, 504, 572)),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pdftoppm", default="pdftoppm")
    args = parser.parse_args()
    out = Path(__file__).resolve().parents[1] / "assets/experiments"
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, (page, (x0, y0, x1, y1)) in FIGURES.items():
            prefix = Path(tmp) / name
            subprocess.run([args.pdftoppm, "-f", str(page), "-l", str(page),
                            "-singlefile", "-r", "432", "-x", str(x0 * 6), "-y", str(y0 * 6),
                            "-W", str((x1 - x0) * 6), "-H", str((y1 - y0) * 6),
                            "-png", str(args.pdf), str(prefix)], check=True)
            with Image.open(prefix.with_suffix(".png")) as image:
                image.convert("RGB").save(out / f"{name}.webp", "WEBP", quality=96, method=6)
                print(f"{name}: {image.size}")


if __name__ == "__main__":
    main()
