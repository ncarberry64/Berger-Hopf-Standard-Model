"""Materialize canonical action and third-variation inputs at C2 node 1221."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
BASE = ROOT / "artifacts" / "flagship_integration"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))

CHECKPOINT = BASE / "BHSM_N12_C2_1221_CANCELLED_CHART_CHECKPOINT.npz"
ACTION = BASE / "BHSM_N12_C2_1221_CANCELLED_CHART_ACTION_MAJORANTS_R1E8.json"
THIRD = BASE / "BHSM_N12_C2_1221_CANCELLED_CHART_THIRD_VARIATION.npz"
THIRD_META = THIRD.with_suffix(".json")

from derive_n12_c2_launch_eigenline_ball import _load as _load_canonical  # noqa: E402
from materialize_n12_c2_1221_cancelled_chart_checkpoint import (  # noqa: E402
    main as materialize,
)


def _load_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    materialize()
    os.environ.update({
        "BHSM_N12_CHECKPOINT": str(CHECKPOINT.relative_to(ROOT)),
        "BHSM_N12_ACTION_MAJORANT_RESULT": str(ACTION.relative_to(ROOT)),
        "BHSM_N12_CERTIFICATE_BALL": "1e-8",
        "BHSM_N12_THIRD_VARIATION_RESULT": str(THIRD.relative_to(ROOT)),
        "BHSM_N12_THIRD_VARIATION_METADATA": str(THIRD_META.relative_to(ROOT)),
    })
    _load_canonical("derive_n12_action_ball_majorants").main()
    third = _load_file(
        "cancelled_chart_third_variation",
        SCRIPTS / "derive_n12_center_action_third_variations.py",
    )
    third.main()


if __name__ == "__main__":
    main()
