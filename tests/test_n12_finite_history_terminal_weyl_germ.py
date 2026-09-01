import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_finite_history_terminal_weyl_germ.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_HISTORY_TERMINAL_WEYL_GERM.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("terminal_weyl_germ", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_terminal_weyl_germ_builds_validated_payload() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["terminal_M_C_Laurent_germ"] == "CERTIFIED"
    assert payload["claim_boundary"][
        "total_physical_D_common_scale_M_C"
    ].startswith("OPEN")
    assert payload["claim_boundary"]["zero_source_force_value"].startswith("OPEN")
    pair_constant = np.asarray(
        payload["weyl_Laurent_germs"][
            "chirality_pair_common_scale_constant"
        ]
    )
    pair_duration = np.asarray(
        payload["weyl_Laurent_germs"][
            "chirality_pair_common_scale_duration"
        ]
    )
    assert np.linalg.norm(pair_constant) < 1.0e-14
    assert np.linalg.norm(pair_duration) > 0.0


def test_terminal_weyl_germ_script_is_reproducible() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    payload = json.loads(first)
    assert payload["validation_passed"] is True
