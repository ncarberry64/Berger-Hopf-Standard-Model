"""Generate deterministic claim-safe BHSM gallery SVGs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.plotting import generate_gallery_plots  # noqa: E402


if __name__ == "__main__":
    os.chdir(ROOT)
    manifest = generate_gallery_plots(Path("artifacts/plots"))
    print(json.dumps(manifest, indent=2, sort_keys=True))
