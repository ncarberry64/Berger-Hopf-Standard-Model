from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "adjudicate_n12_gate7_rank72_maximal_tail_routes.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_RANK72_MAXIMAL_TAIL_ROUTE_ADJUDICATION.json"
)


def _run() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_rank72_maximal_tail_routes_are_adjudicated_without_promotion() -> None:
    payload = _run()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["finite_core_shortcut"] == "CLOSED_INSUFFICIENT"
    assert payload["claim_boundary"]["finite_optical_NHIM_absolute_route"] == "CLOSED_NO_GO"
    assert payload["claim_boundary"]["rank72_signed_relative_form_tail"] == "OPEN_CURRENT_OWNER"
    assert payload["seed_and_asymptotic_audit"]["coordinate_block_rank"] == 37
    assert payload["finite_core_nonpromotion"]["duration_growth_factor"] > 1.0
    assert 0.0 < payload["finite_core_nonpromotion"]["representative_gap_ratio_1222_over_1064"] < 1.0
    assert payload["nested_core_adjudication"]["current_Weyl_net"] == "NOT_CONVERGED"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_rank72_maximal_tail_route_artifact_is_deterministic() -> None:
    first = _run()
    first_hash = hashlib.sha256(RESULT.read_bytes()).hexdigest()
    second = _run()
    second_hash = hashlib.sha256(RESULT.read_bytes()).hexdigest()
    assert first == second
    assert first_hash == second_hash
