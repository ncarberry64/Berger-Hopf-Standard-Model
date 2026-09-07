"""Materialize the full-core transport law for terminal HS response jets."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_current_c2_factorized_hs_calderon import (
    ACTION_VERSION,
    terminal_hs_jet_transport_coefficients,
)


A = ROOT / "artifacts/action_extension"
F = ROOT / "artifacts/flagship_integration"
DESCRIPTOR = F / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DESCRIPTOR_DATA = F / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
SEAM = F / "BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"
ENDPOINT_OWNER = F / "BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json"
FACTORIZED = A / "BHSM_AE4_CURRENT_C2_FACTORIZED_HS_CALDERON.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT.json"
INPUTS = (
    DESCRIPTOR,
    DESCRIPTOR_DATA,
    SEAM,
    ENDPOINT_OWNER,
    FACTORIZED,
    ROOT / "src/bhsm/interface/ae4_current_c2_factorized_hs_calderon.py",
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    descriptor = _load(DESCRIPTOR)
    seam = _load(SEAM)
    endpoint_owner = _load(ENDPOINT_OWNER)
    factorized = _load(FACTORIZED)
    if not all(
        row["validation_passed"]
        for row in (descriptor, seam, endpoint_owner, factorized)
    ):
        raise RuntimeError("validated current-C2 and endpoint-owner inputs required")

    broad_upper = float(
        seam["fermion_AE2_W_zero_load_enclosures"][0][
            "child_Calderon_interval"
        ][1]
    )
    with np.load(DESCRIPTOR_DATA) as data:
        x = np.asarray(data["node_log_R4_center"], dtype=float)
        h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)
        profile = np.ones_like(h)
        rows: dict[str, Any] = {}
        for chirality, label in ((1, "chirality_plus"), (-1, "chirality_minus")):
            rows[label] = {}
            for load_label, load in (
                ("zero_reference_load", 0.0),
                ("broad_AE2_child_load_upper_reference", broad_upper),
            ):
                rows[label][load_label] = terminal_hs_jet_transport_coefficients(
                    log_radii=x,
                    proper_durations=h,
                    dirac_eigenvalue_at_unit_radius=1.5,
                    chirality=chirality,
                    source_profile=profile,
                    spectral_parameter=-1.0,
                    terminal_load=load,
                    decimal_precision=60,
                )

    all_rows = [entry for channel in rows.values() for entry in channel.values()]
    boundary = {
        "AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT_LAW_DERIVED": True,
        "AE4_CURRENT_C2_TERMINAL_HS_JETS_DERIVED": False,
        "AE4_CURRENT_C2_MAXIMAL_TAIL_LOAD_AND_HS_JETS_DERIVED": False,
        "AE4_CURRENT_C2_MAXIMAL_HISTORY_RETARDED_HS_CALDERON_BLOCK_DERIVED": False,
        "AE4_E1_FULL_CORE_HS_HESSIAN_DERIVED": False,
        "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    validation = {
        "full_1222_segment_current_C2_core_consumed": all(
            row["segment_count"] == 1222 for row in all_rows
        ),
        "negative_axis_native_probe_used": all(
            row["spectral_parameter"] == -1.0 for row in all_rows
        ),
        "transport_coefficients_finite": all(
            np.isfinite(row[key])
            for row in all_rows
            for key in (
                "first_local_coefficient_a",
                "second_local_coefficient_b",
                "terminal_first_jet_sensitivity_s",
                "mixed_terminal_first_coefficient_c",
                "terminal_first_jet_quadratic_coefficient_q",
            )
        ),
        "first_and_second_terminal_sensitivities_identical": all(
            row["terminal_first_jet_sensitivity_s"]
            == row["terminal_second_jet_sensitivity"]
            for row in all_rows
        ),
        "terminal_second_jet_chain_rule_identity_certified": all(
            abs(row["terminal_second_jet_identity_residual"]) < 1.0e-50
            for row in all_rows
        ),
        "terminal_HS_jets_are_not_suppressed_by_finite_core": all(
            abs(row["terminal_first_jet_sensitivity_s"]) > 0.99
            for row in all_rows
        ),
        "no_physical_terminal_HS_jet_selected": all(
            not row["physical_terminal_HS_jets_selected"] for row in all_rows
        ),
        "maximal_history_not_overclaimed": not boundary[
            "AE4_CURRENT_C2_MAXIMAL_HISTORY_RETARDED_HS_CALDERON_BLOCK_DERIVED"
        ],
    }
    return {
        "artifact": "BHSM_AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT",
        "action_version": ACTION_VERSION,
        "classification": (
            "THE_FULL_CURRENT_C2_FACTORIZED_CORE_TRANSPORTS_AN_ACTION_OWNED_"
            "TERMINAL_LOAD_HS_JET_BY_AN_EXACT_AFFINE_QUADRATIC_CHAIN_RULE;_AT_"
            "THE_NATIVE_z_MINUS_1_PROBE_THE_TERMINAL_FIRST_AND_SECOND_JETS_"
            "ENTER_THE_BIRTH_RESPONSE_WITH_NEAR_UNIT_SENSITIVITY,_SO_THE_"
            "UNKNOWN_MAXIMAL_CHILD_HS_JETS_CANNOT_BE_DROPPED_OR_RELABELED_AS_"
            "LOCAL_CORE_DATA"
        ),
        "operator_domain": {
            "background": "RESET_GENERATED_CURRENT_C2_PROOF_CENTER_FAMILY",
            "segment_count": 1222,
            "spectral_parameter": -1.0,
            "source": "UNIT_COMMUTING_LR_HS_SUPERPOTENTIAL_SHIFT",
            "terminal_load_references": {
                "zero": 0.0,
                "broad_AE2_child_load_upper": broad_upper,
            },
            "broad_AE2_upper_is_physical_endpoint_selection": False,
            "physical_terminal_HS_jets_selected": False,
        },
        "transport_law": {
            "first": "D_H_M_birth=a+s*u",
            "second": "D2_H_M_birth=b+2*c*u+q*u^2+s*v",
            "u": "D_H_L_terminal",
            "v": "D2_H_L_terminal",
            "derivation": "EXACT_COMPOSED_MOBIUS_TANGENT_JETS_NOT_FINITE_DIFFERENCE",
        },
        "negative_axis_terminal_HS_jet_transport_rows": rows,
        "scientific_result": {
            "terminal_HS_jets_reduce_to_two_missing_scalars_per_channel_at_fixed_z": [
                "D_H_L_terminal",
                "D2_H_L_terminal",
            ],
            "finite_core_can_erase_unknown_terminal_HS_jets": False,
            "existing_covariant_geometry_jet_bounds_reclassified_as_HS_jets": False,
            "required_owner": (
                "ACTION_OWNED_N12_MAXIMAL_CHILD_OR_FIRST_PHYSICAL_DOMAIN_EXIT_"
                "TERMINAL_LOAD_WITH_ITS_HS_VARIATIONS"
            ),
        },
        "claim_boundary": boundary,
        "exact_next_calculation": (
            "DERIVE_D_H_L_terminal_AND_D2_H_L_terminal_FROM_THE_ACTION_OWNED_"
            "N12_MAXIMAL_CHILD_OR_FIRST_PHYSICAL_DOMAIN_EXIT,_THEN_SUBSTITUTE_"
            "THEM_IN_THE_CERTIFIED_TRANSPORT_LAW_BEFORE_THE_AE4_E1_SPECTRAL_"
            "INTEGRATION"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("terminal HS-jet transport validation failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
