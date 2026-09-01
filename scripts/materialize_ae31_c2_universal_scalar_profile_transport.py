"""Materialize the current-C2 universal scalar-profile transport theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_universal_scalar_profile_transport import (
    ACTION_VERSION,
    CLASSIFICATION,
    canonical_discrete_normalization,
    claim_boundary,
    conjugate_channel_universality,
    current_c2_tensor_domain_transport,
    exact_remaining_owner,
    finite_projector_response_bound,
    provenance_and_action_gate,
    universal_profile_operator,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_UNIVERSAL_SCALAR_PROFILE_TRANSPORT.json"
INPUTS = (
    A / "BHSM_AE31_C2_QUARK_PROJECTOR_OVERLAP_BRIDGE.json",
    A / "BHSM_AE31_C2_QUARK_HIGGS_INCIDENCE_TRANSPORT.json",
    ROOT / "theory/theorem_discharge_legacy_geometric_overlap_results.json",
    ROOT / "theory/derived_universal_higgs_topographic_profile.md",
    ROOT / "src/profile_normalization_hessian_closure.py",
    ROOT / "src/bhsm/interface/ae31_c2_universal_scalar_profile_transport.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    projector_bridge, incidence, historical = map(_load, INPUTS[:3])
    profile = universal_profile_operator(distances=(0.0, 0.5, 1.0), sigma=1.25, phi0=2.0)
    normalization = canonical_discrete_normalization(
        distances=(0.0, 0.5, 1.0), measure_weights=(0.2, 0.5, 0.3), sigma=1.25
    )
    domain = current_c2_tensor_domain_transport(profile_values=profile["values"])
    response_bound = finite_projector_response_bound(
        active_projector=((1, 0, 0), (0, 1, 0), (0, 0, 0)),
        scalar_map=profile["multiplication_operator"],
        singlet_projector=((0, 0, 0), (0, 1, 0), (0, 0, 1)),
    )
    channels = conjugate_channel_universality()
    provenance = provenance_and_action_gate()
    remaining = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "historical_universal_profile_reused": (
            historical["kernel"]["universal_profile"]
            == "Phi(y)=Phi0 exp[-sigma d_I(y,y0)^2]"
            and provenance["historical_profile_status"]
            == "UNIVERSAL_HIGGS_TOPOGRAPHIC_PROFILE_DERIVED_CONDITIONAL"
        ),
        "profile_multiplier_is_bounded": (
            profile["bound_residual"] == 0.0
            and profile["bounded_for_every_finite_phi0_and_sigma_nonnegative"]
        ),
        "canonical_amplitude_formula_normalizes_sample": (
            normalization["unit_norm_residual"] < 1e-12
            and not normalization["independent_amplitude_after_canonical_normalization"]
            and not normalization["BHSM_profile_measure_numerically_evaluated"]
        ),
        "current_C2_domain_and_birth_trace_preserved": (
            domain["sample_commutator_residual"] == 0.0
            and domain["bounded_internal_multiplier_preserves_Domain_D_C2_tensor_I"]
            and domain["retained_birth_trace_unchanged"]
            and incidence["current_C2_domain_tensor_theorem"]["retained_birth_trace_unchanged"]
        ),
        "finite_projector_trace_requires_no_global_trace_class_claim": (
            response_bound["bound_residual"] < 1e-12
            and response_bound["compressed_operator_is_hilbert_schmidt"]
            and not response_bound["global_uncompressed_trace_class_assumed"]
            and projector_bridge["claim_boundary"]["CURRENT_C2_QUARK_PROJECTOR_OVERLAP_FUNCTIONAL_DERIVED"]
        ),
        "one_profile_does_not_force_equal_sector_response": (
            channels["one_universal_profile"]
            and not channels["flavor_or_generation_dependent_sigma_allowed"]
            and not channels["equal_up_down_projector_responses_forced"]
        ),
        "action_ownership_and_residues_not_overclaimed": (
            not provenance["intrinsic_M4_H_to_internal_profile_attachment_action_derived"]
            and not boundary["CURRENT_C2_INTRINSIC_HIGGS_INTERNAL_PROFILE_ATTACHMENT_ACTION_DERIVED"]
            and not boundary["CURRENT_C2_PROFILE_SIGMA_AND_AMPLITUDE_ACTION_DERIVED"]
            and not boundary["CURRENT_C2_UP_DOWN_YUKAWA_VERTEX_RESIDUES_ACTION_DERIVED"]
            and not provenance["old_boundary_no_fit_values_used_as_quark_yukawa_inputs"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_UNIVERSAL_SCALAR_PROFILE_TRANSPORT",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "universal_profile_operator_witness": profile,
        "canonical_normalization_witness": normalization,
        "current_c2_tensor_domain_transport": domain,
        "finite_projector_response_bound": response_bound,
        "conjugate_channel_universality": channels,
        "provenance_and_action_gate": provenance,
        "exact_remaining_owner": remaining,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 universal scalar-profile transport failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
