from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_joint_heat_cotangent_reverse_seed.py"
ARTIFACT = ROOT / "artifacts" / "flagship_integration" / "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json"


def test_joint_heat_cotangent_reverse_seed() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["exact_heat_seed"]["sector_seed"].startswith("Q_heat=")
    assert payload["inverse_free_seam_reverse"]["q_M_f"] == "Omega_S"
    assert payload["inverse_free_seam_reverse"]["q_M_C2"].startswith("U_R*")
    assert payload["inverse_free_seam_reverse"]["covariant_transport_rule"].startswith("nabla_U_R=0")
    assert payload["adjudication"]["additional_seam_source"] == "FORBIDDEN"
    assert payload["adjudication"]["internal_block_zeroing"] == "FORBIDDEN"
    assert payload["matching_audit"]["actual_complete_joint_operator_value"] == "ACTUALLY_MISSING"
    assert payload["claim_boundary"]["finite_1222_core_promoted_to_endpoint"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_direct_block_and_schur_witnesses_close() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    witness = payload["witness"]
    assert witness["joint_matrix_positive"] is True
    assert witness["direct_block_absolute_residual"] < 1.0e-14
    assert witness["direct_centered_absolute_residual"] < 1.0e-9
    assert witness["direct_schur_logdet_absolute_residual"] < 1.0e-14
    assert witness["direct_schur_derivative_absolute_residual"] < 1.0e-14
