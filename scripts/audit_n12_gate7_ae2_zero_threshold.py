"""Audit the AE2 zero-threshold consequence of product-Dirac factorization."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_zero_threshold import (  # noqa: E402
    constant_channel_zero_transport,
    piecewise_constant_zero_transport,
    two_sided_ae2_zero_transport,
)


TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_ZERO_THRESHOLD_NO_SHORTCUT.json"
)
AE2_ACTION = ROOT / (
    "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
)
AE2_GATE7 = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
)
PRODUCT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
)
THRESHOLD = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_BIRTH_THRESHOLD_MARGIN_AUDIT.json"
)
PROPER_TIME = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json"
)
MODULE = ROOT / "src/bhsm/interface/action_extension_ae2_zero_threshold.py"
INPUTS = (AE2_ACTION, AE2_GATE7, PRODUCT, THRESHOLD, PROPER_TIME, MODULE)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite AE2 threshold audit value")
        rounded = round(value, 15)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, complex):
        return {"real": _canonical(value.real), "imag": _canonical(value.imag)}
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all AE2 zero-threshold inputs are required")
    action, gate7, product, threshold, proper_time = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(
        record.get("validation_passed") is True
        for record in (action, gate7, product, threshold, proper_time)
    ):
        raise RuntimeError("validated AE2 zero-threshold lineage is required")
    if action.get("action_version") != "BHSM-AE-2.0.0":
        raise RuntimeError("BHSM-AE-2.0.0 action input required")

    duration = float(product["certified_core"]["proper_duration_lower"])
    representative_s = float(
        product["representative_retained_low_levels"]["rows"][0][
            "superpotential_absolute_upper_on_certified_core"
        ]
    )
    constant = constant_channel_zero_transport(representative_s, duration, 1.0)
    piecewise = piecewise_constant_zero_transport(
        [representative_s, -0.7 * representative_s, 0.2 * representative_s],
        [duration / 3.0] * 3,
        1.0 + 0.25j,
    )
    lift = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    two_sided = two_sided_ae2_zero_transport(
        representative_s,
        -representative_s,
        duration,
        duration,
        lift,
        [1.0 + 0.5j, -0.25j],
    )

    validation = {
        "all_inputs_validated": True,
        "AE2_relative_Cayley_family_absent": (
            gate7["source_domain"]["Cayley_phase_family"] is None
        ),
        "AE2_independent_fermion_surface_block_is_zero": (
            gate7["source_domain"]["fermion_W_phys_local_surface_block"] == 0
        ),
        "retained_product_form_is_factorized": (
            product["factorized_comparison_theorem"]["factor"]
            == "A_lambda=d_tau+s_lambda,_s_lambda=chirality*lambda/R4"
        ),
        "constant_transport_has_zero_form_energy": (
            constant["factorized_form_energy"] == 0.0
        ),
        "piecewise_transport_is_exact": (
            piecewise["maximum_transport_residual"] == 0.0
        ),
        "two_sided_AE2_trace_graph_is_satisfied": (
            two_sided["trace_graph_residual"] < 1.0e-12
        ),
        "two_sided_local_wronskian_can_equal_zero": (
            two_sided["two_sided_zero_energy_wronskian"] == 0.0
        ),
        "positive_duration_does_not_create_zero_margin": (
            duration > 0.0
            and not two_sided["strict_positive_margin_from_local_collars"]
        ),
        "negative_probe_not_relabelled_zero_energy": (
            product["spectral_probe"]["z"] < 0.0
        ),
        "realized_maximal_exterior_zero_mode_not_claimed": True,
        "Gate7_not_overclaimed": True,
        "FULL_BHSM_COMPLETE_false": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_AE2_ZERO_THRESHOLD_NO_SHORTCUT",
        "action_version": "BHSM-AE-2.0.0",
        "status": "AE2_DOMAIN_FIXED_BUT_LOCAL_ZERO_THRESHOLD_MARGIN_NOT_FORCED",
        "classification": (
            "AE2_REMOVES_THE_RELATIVE_CAYLEY_DOMAIN_AMBIGUITY_BUT_THE_"
            "RETAINED_PRODUCT_DIRAC_FORM_REMAINS_A_lambda_STAR_A_lambda;_"
            "ON_EVERY_POSITIVE_DURATION_COLLAR_THE_EXACT_TRANSPORT_"
            "A_lambda_u_EQUALS_ZERO_HAS_ARBITRARY_NONZERO_BIRTH_TRACE_AND_"
            "ZERO_FACTORIZED_CONORMAL,_SO_SPATIAL_EIGENVALUE_POSITIVITY_AND_"
            "TWO_CHORD_DURATION_ALONE_CANNOT_PROVE_A_STRICT_ZERO_ENERGY_"
            "TWO_SIDED_WRONSKIAN_MARGIN"
        ),
        "theorem": {
            "channel_factor": "A_s=d_tau+s(tau)",
            "zero_transport": "u(tau)=exp(-integral_0^tau_s(r)dr)*g",
            "identity": "A_s*u=0_AND_q_0[u]=norm(A_s*u)^2=0",
            "birth_conormal": "M_local(0)=-A_s*u(0)/u(0)=0",
            "terminal_inward_graph": "-A_s*u(T)/u(T)=0_IS_NONNEGATIVE",
            "two_sided_AE2_graph": (
                "g_child=U_R*g_event_AND_M_event_local(0)+"
                "U_R_DAGGER*M_child_local(0)*U_R=0"
            ),
            "consequence": (
                "NO_STRICT_POSITIVE_FUTURE_INDEPENDENT_ZERO_THRESHOLD_"
                "BOUND_FOLLOWS_FROM_THE_CERTIFIED_COLLARS"
            ),
            "negative_resolvent_distinction": (
                "AT_z=-kappa_squared<0_THE_FORM_ADDS_kappa_squared*norm(u)^2_"
                "AND_COERCIVITY_RETURNS;_THAT_CERTIFICATE_CANNOT_BE_SET_TO_"
                "z=0"
            ),
        },
        "N12_two_chord_application": {
            "proper_duration_lower": duration,
            "representative_absolute_superpotential_upper": representative_s,
            "constant_channel_witness": constant,
            "piecewise_channel_witness": piecewise,
            "two_sided_AE2_witness": two_sided,
        },
        "provenance_adjudication": {
            "well_defined_AE2_reset_and_matter_domain": "ACTION_VERSION_OWNED",
            "relative_terminal_phase_eliminated": "ACTION_VERSION_OWNED",
            "positive_two_chord_duration": "CERTIFIED",
            "negative_resolvent_product_Weyl_bounds": "CERTIFIED_BROAD",
            "strict_zero_energy_two_sided_margin": "NOT_DERIVED",
            "maximal_exterior_Calderon_value_and_geometry_jets": "OPEN",
        },
        "claim_boundary": {
            "AE2_action_invalidated": False,
            "physical_maximal_exterior_has_zero_mode": "NOT_CLAIMED",
            "strict_margin_impossible_for_all_realizations": "NOT_CLAIMED",
            "local_collars_suffice_for_strict_margin": False,
            "zero_source_force_evaluated": False,
            "frozen_predictions_changed": False,
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "REALIZE_OR_RIGOROUSLY_ENCLOSE_THE_AE2_ACTION_OWNED_MAXIMAL_"
            "EVENT_AND_CHILD_CALDERON_MAPS_M_event(z)_AND_M_child(z)_WITH_"
            "THEIR_FIRST_AND_SECOND_GEOMETRY_VARIATIONS_ON_A_NONEMPTY_"
            "NATIVE_RESOLVENT_REGION;_AT_ZERO_ENERGY_PROVE_THE_STRICT_"
            "TWO_SIDED_WRONSKIAN_MARGIN_FROM_THAT_GLOBAL_EXTERIOR_DATA,_NOT_"
            "FROM_THE_LOCAL_COLLARS,_BEFORE_CLAIMING_THE_CONTINUOUS_LOW_"
            "ENERGY_SOURCE_MEASURE_OR_ZERO_SOURCE_FORCE"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def materialize() -> Path:
    payload = build_payload()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
