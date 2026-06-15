"""Generate primitive cyclic monodromy boundary-action audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_primitive_cyclic_monodromy import export_primitive_cyclic_monodromy_outputs  # noqa: E402


if __name__ == "__main__":
    export_primitive_cyclic_monodromy_outputs(ROOT)
