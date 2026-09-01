"""Run the expanded full-action cancelled-theta enclosure from node 1221."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "certify_n12_c2_1221_cancelled_theta_step.py"


def main() -> None:
    os.environ["BHSM_N12_EXPANDED_CANCELLED_THETA"] = "1"
    spec = importlib.util.spec_from_file_location("expanded_cancelled_theta", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load cancelled theta source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


if __name__ == "__main__":
    main()
