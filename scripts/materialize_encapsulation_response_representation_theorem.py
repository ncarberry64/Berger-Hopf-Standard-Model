"""Materialize the BHSM encapsulation-response representation theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.encapsulation_response_representation_theorem import (  # noqa: E402
    RSP_CLASS,
    canonical_pullback_residual,
    representation_theorem_payload,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_ENCAPSULATION_RESPONSE_REPRESENTATION_THEOREM.json"
)
MODULE = ROOT / "src/bhsm/interface/encapsulation_response_representation_theorem.py"
SCRIPT = Path(__file__).resolve()
THEORY = ROOT / "theory/bhsm_encapsulation_response_representation_theorem.md"
TEST = ROOT / "tests/test_encapsulation_response_representation_theorem.py"

SOURCES = (
    "AGENTS.md",
    "src/bhsm/interface/active_encapsulation_boundary_generator_adjudication.py",
    "src/bhsm/interface/full_field_moving_reset_graph_decision.py",
    "src/bhsm/interface/environmental_child_compatibility_selection.py",
    "src/bhsm/interface/completion/support_covariant_phase_space_v11_2.py",
    "src/bhsm/interface/envelopment/core_stratum_matching_v10_4.py",
    "src/bhsm/interface/completion/round_hessian_centrality_no_go_v14_71.py",
    "src/bhsm/interface/completion/second_shape_jacobi_triplet_v14_70.py",
    "src/bhsm/interface/completion/worldline_clifford_spin_lift_v14_44.py",
    "src/bhsm/interface/completion/round_collar_spectral_baseline_v14_58.py",
    "artifacts/action_extension/BHSM_ACTIVE_ENCAPSULATION_BOUNDARY_GENERATOR_ADJUDICATION.json",
    "artifacts/action_extension/BHSM_ENVIRONMENTAL_RESET_COMPATIBILITY_CLASSIFICATION.json",
    "artifacts/BHSM_multi_harmonic_Hopf_bridge_selection_rules_v14_34.json",
    "artifacts/BHSM_three_harmonic_observability_v14_55.json",
    "artifacts/BHSM_harmonic_linear_no_selection_theorem_v6_0_4.json",
    "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json",
    "theory/n12_forward_graded_phase_independence_no_go.md",
    "theory/bhsm_active_encapsulation_boundary_generator_adjudication.md",
)


def _sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def build_payload() -> dict[str, Any]:
    payload = representation_theorem_payload()
    source_paths = list(SOURCES) + [
        MODULE.relative_to(ROOT).as_posix(),
        SCRIPT.relative_to(ROOT).as_posix(),
        THEORY.relative_to(ROOT).as_posix(),
        TEST.relative_to(ROOT).as_posix(),
    ]
    missing = [source for source in source_paths if not (ROOT / source).is_file()]
    if missing:
        raise FileNotFoundError("missing representation-theorem provenance: " + ", ".join(missing))
    payload["source_sha256"] = {
        source: _sha256(ROOT / source) for source in sorted(source_paths)
    }

    finite = payload["recovered_finite_subspaces"]
    freedom = payload["response_freedom"]
    rank = payload["N12_rank_forecast"]
    claims = payload["claim_boundary"]
    validation = {
        "provenance_categories_separated": set(payload["provenance"])
        == {"RECOVERED_PRIOR_BHSM", "OWNER_SUPPLIED_PHYSICS", "NEWLY_DERIVED"},
        "input_not_falsely_promoted_to_one_vector_space": (
            payload["input_space"]["global_event_irreducible_decomposition_owned"] is False
        ),
        "output_is_full_field_boundary_phase_type": (
            payload["output_space"]["dimension_class"].startswith("INFINITE_DIMENSIONAL")
        ),
        "six_sector_isotypic_classes_only": len(payload["event_sector_decomposition"]) == 6,
        "round_commutants_reproduced": (
            finite["round_shape_H2_full_Spin4"]["commutant_real_dimension"] == 1
            and finite["round_shape_H2_diagonal_SU2"]["commutant_real_dimension"] == 3
        ),
        "Clifford_commutants_reproduced": (
            finite["Clifford_spin_factor"]["full_irreducible_commutant_complex_dimension"] == 1
            and finite["Clifford_spin_factor"]["normal_symbol_only_commutant_complex_dimension"] == 8
        ),
        "canonical_test_witness_is_isotropic": canonical_pullback_residual(
            np_identity(2), np_diagonal((2.0, 3.0))
        ) < 1.0e-13,
        "RSP5_fail_closed": (
            RSP_CLASS == "RSP5"
            and freedom["class"] == "RSP5"
            and freedom["physical_irreducible_channel_count"] is None
        ),
        "N12_rank_not_promoted": (
            rank["current_certified_rank"] == 31
            and rank["current_residual"] == 67
            and rank["time_quotient_residual"] == 66
            and rank["actual_additional_rank_this_sprint"] == 0
        ),
        "no_owner_function_requested_under_RSP5": payload["ONE_OWNER_QUESTION"] is None,
        "claim_firewall": not any(claims.values()),
    }
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    return payload


def np_identity(size: int):
    """Avoid exposing NumPy objects in the serialized payload."""

    import numpy as np

    return np.eye(size)


def np_diagonal(values: tuple[float, ...]):
    import numpy as np

    return np.diag(values)


def main() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(build_payload()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(main())
