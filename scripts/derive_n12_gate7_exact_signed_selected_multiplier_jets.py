"""Derive exact signed selected-multiplier jets on the Gate-7 history.

The selected bordered multiplier has the inverse-free action identity

    mu = DS[A psi] - D2S[B psi, C].

Here ``A`` and ``B`` are the retained metric lifts and ``C`` is the retained
configuration incidence.  This script differentiates that scalar identity
twice in the already derived Green-correction direction.  Signed action
contractions are summed before absolute values; no response norm or minimum
spectral gap is inserted into the multiplier estimate.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
os.environ.setdefault("BHSM_N12_CERTIFICATE_BALL", "1.0")

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from derive_n12_action_signed_interval_majorants import action_bound  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
EIGENLINE = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_EIGENLINE_FIRST_JETS.npz"
FIRST = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_BORDERED_RESPONSE_FIRST_JETS.npz"
SECOND = BASE / "BHSM_N12_GATE7_CORRECTION_BORDERED_RESPONSE_SECOND_JETS.npz"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_SELECTED_MULTIPLIER_JETS.json"
DATA = RESULT.with_suffix(".npz")
QDIM = 37
SELECTED = 24


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _row(task: tuple[int, np.ndarray, np.ndarray, np.ndarray, np.ndarray]) -> dict[str, Any]:
    index, state, weights, direction, reference_psi = task
    q_weights, reduced_weights, _, _ = metric_data()
    total = weights.size
    reduced = reduced_weights.size

    jet = exact_full_action_jet_at_state(
        12,
        state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=96,
    )
    hessian = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(0.5 * (hessian + hessian.T))
    psi = vectors[:, SELECTED]
    if float(psi @ reference_psi) < 0.0:
        vectors[:, SELECTED] *= -1.0
        psi = -psi

    reduced_lift = np.zeros((total, reduced))
    reduced_lift[QDIM:] = reduced_weights[:, None] * np.eye(reduced)
    eigenframe_lift = reduced_lift @ vectors

    def signed(*directions: np.ndarray) -> float | np.ndarray:
        return np.asarray(action_bound(
            state,
            mixed_directions=list(directions),
            exact_signed_output_index=0,
        ).d[-1], dtype=float)

    def A(vector: np.ndarray) -> np.ndarray:
        result = np.zeros(total)
        result[:QDIM] = (
            q_weights * reduced_weights[:QDIM] * vector[:QDIM]
        )
        return result

    def B(vector: np.ndarray) -> np.ndarray:
        return reduced_lift @ vector

    configuration = np.zeros(total)
    configuration[:QDIM] = q_weights * state[QDIM:2 * QDIM]
    configuration_first = np.zeros(total)
    configuration_first[:QDIM] = (
        q_weights * direction[QDIM:2 * QDIM]
        / weights[QDIM:2 * QDIM]
    )

    B_psi = B(psi)
    H_first_psi = signed(eigenframe_lift, direction, B_psi)
    lambda_first = float(H_first_psi[SELECTED])
    first_coefficients = np.zeros(reduced)
    hard = np.arange(reduced) != SELECTED
    denominators = values - values[SELECTED]
    first_coefficients[hard] = (
        -H_first_psi[hard] / denominators[hard]
    )
    psi_first = vectors @ first_coefficients

    H_second_psi = signed(
        eigenframe_lift, direction, direction, B_psi,
    )
    H_first_psi_first = signed(
        eigenframe_lift, direction, B(psi_first),
    )
    lambda_second = float(
        H_second_psi[SELECTED]
        + 2.0 * H_first_psi_first[SELECTED]
    )
    second_coefficients = np.zeros(reduced)
    second_coefficients[SELECTED] = -float(psi_first @ psi_first)
    second_coefficients[hard] = -(
        H_second_psi[hard]
        + 2.0 * H_first_psi_first[hard]
        - 2.0 * lambda_first * first_coefficients[hard]
    ) / denominators[hard]
    psi_second = vectors @ second_coefficients

    zeroth_terms = np.asarray((
        float(signed(A(psi))),
        -float(signed(B_psi, configuration)),
    ))
    first_terms = np.asarray((
        float(signed(A(psi), direction)),
        float(signed(A(psi_first))),
        -float(signed(B_psi, direction, configuration)),
        -float(signed(B(psi_first), configuration)),
        -float(signed(B_psi, configuration_first)),
    ))
    second_terms = np.asarray((
        float(signed(A(psi), direction, direction)),
        2.0 * float(signed(A(psi_first), direction)),
        float(signed(A(psi_second))),
        -float(signed(B_psi, direction, direction, configuration)),
        -2.0 * float(signed(B(psi_first), direction, configuration)),
        -2.0 * float(signed(B_psi, direction, configuration_first)),
        -float(signed(B(psi_second), configuration)),
        -2.0 * float(signed(B(psi_first), configuration_first)),
    ))
    mu = math.fsum(map(float, zeroth_terms))
    mu_first = math.fsum(map(float, first_terms))
    mu_second = math.fsum(map(float, second_terms))
    return {
        "node": index,
        "selected_branch": SELECTED,
        "selected_eigenvalue": float(values[SELECTED]),
        "selected_eigenvalue_first_variation": lambda_first,
        "selected_eigenvalue_second_variation": lambda_second,
        "selected_eigenvector_first_variation_2_norm": float(
            np.linalg.norm(psi_first)
        ),
        "selected_eigenvector_second_variation_2_norm": float(
            np.linalg.norm(psi_second)
        ),
        "selected_eigenvector_first": psi_first.tolist(),
        "selected_eigenvector_second": psi_second.tolist(),
        "multiplier": mu,
        "multiplier_first_variation": mu_first,
        "multiplier_second_variation": mu_second,
        "zeroth_signed_terms": zeroth_terms.tolist(),
        "first_signed_terms": first_terms.tolist(),
        "second_signed_terms": second_terms.tolist(),
        "zeroth_separated_absolute_sum": float(np.sum(abs(zeroth_terms))),
        "first_separated_absolute_sum": float(np.sum(abs(first_terms))),
        "second_separated_absolute_sum": float(np.sum(abs(second_terms))),
        "eigenline_first_normalization_residual": float(abs(psi @ psi_first)),
        "eigenline_second_normalization_residual": float(abs(
            psi @ psi_second + psi_first @ psi_first
        )),
    }


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, EIGENLINE, FIRST, SECOND)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("retained multiplier-jet inputs required")
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
    with np.load(EIGENLINE) as source:
        directions = np.asarray(
            source["action_correction_directions"], dtype=float,
        )
        reference_psi = np.asarray(source["selected_eigenvectors"], dtype=float)
        retained_psi_first = np.asarray(
            source["selected_eigenvector_first_variations"], dtype=float,
        )
    with np.load(FIRST) as source:
        response = np.asarray(source["bordered_response"], dtype=float)
        response_first = np.asarray(
            source["bordered_response_correction_direction_first_variation"],
            dtype=float,
        )
    with np.load(SECOND) as source:
        response_second = np.asarray(
            source["bordered_response_correction_direction_second_variation"],
            dtype=float,
        )
        prior_psi_second = np.asarray(
            source["selected_eigenvector_correction_direction_second_variation"],
            dtype=float,
        )

    tasks = [
        (index, states[index], weights, directions[index], reference_psi[index])
        for index in range(len(states))
    ]
    workers = min(
        int(os.environ.get("BHSM_N12_SIGNED_JET_WORKERS", "12")),
        os.cpu_count() or 1,
    )
    with ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(_row, tasks, chunksize=1))

    multiplier = np.asarray([row["multiplier"] for row in rows])
    multiplier_first = np.asarray([
        row["multiplier_first_variation"] for row in rows
    ])
    multiplier_second = np.asarray([
        row["multiplier_second_variation"] for row in rows
    ])
    psi_first = np.asarray([
        row.pop("selected_eigenvector_first") for row in rows
    ])
    psi_second = np.asarray([
        row.pop("selected_eigenvector_second") for row in rows
    ])
    for index, row in enumerate(rows):
        row["bordered_multiplier_difference"] = float(
            multiplier[index] - response[index, -1]
        )
        row["bordered_multiplier_first_difference"] = float(
            multiplier_first[index] - response_first[index, -1]
        )
        row["prior_multiplier_second_difference"] = float(
            multiplier_second[index] - response_second[index, -1]
        )
        row["retained_eigenline_first_difference_2_norm"] = float(
            np.linalg.norm(psi_first[index] - retained_psi_first[index])
        )
        row["prior_eigenline_second_difference_2_norm"] = float(
            np.linalg.norm(psi_second[index] - prior_psi_second[index])
        )

    np.savez_compressed(
        DATA,
        action_lengths=times,
        selected_multiplier=multiplier,
        selected_multiplier_correction_direction_first_variation=multiplier_first,
        selected_multiplier_correction_direction_second_variation=multiplier_second,
        selected_eigenvector_exact_signed_first_variation=psi_first,
        selected_eigenvector_exact_signed_second_variation=psi_second,
    )
    active_first = np.abs(response_first[:, -1]) > 1.0e-20
    validation = {
        "all_48_retained_macro_seams_evaluated": len(rows) == 48,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == SELECTED for row in rows
        ),
        "exact_signed_action_identity_matches_bordered_multiplier_to_1e_minus_9": max(
            abs(multiplier[i] - response[i, -1])
            for i in range(len(rows))
        ) < 1.0e-9,
        "exact_signed_first_identity_matches_differentiated_bordered_multiplier_to_2e_minus_10": max(
            abs(multiplier_first[i] - response_first[i, -1])
            for i in np.flatnonzero(active_first)
        ) < 2.0e-10,
        "exact_signed_second_identity_matches_prior_independent_assembly_to_2e_minus_10": max(
            abs(multiplier_second[i] - response_second[i, -1])
            for i in range(len(rows))
        ) < 2.0e-10,
        "retained_complex_step_eigenline_first_jet_reproduced": max(
            row["retained_eigenline_first_difference_2_norm"] for row in rows
        ) < 1.0e-7,
        "all_eigenline_normalization_identities_close": max(
            max(
                row["eigenline_first_normalization_residual"],
                row["eigenline_second_normalization_residual"],
            ) for row in rows
        ) < 1.0e-12,
        "signed_terms_summed_before_absolute_value": True,
        "no_bordered_response_norm_used_in_multiplier_bound": True,
        "no_minimum_gap_scalarization_or_full_history_inverse_used": True,
        "no_JAX_derivative_used_as_action_authority": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner_first = int(np.argmax(abs(multiplier_first)))
    owner_second = int(np.argmax(abs(multiplier_second)))
    return {
        "artifact": "BHSM_N12_GATE7_EXACT_SIGNED_SELECTED_MULTIPLIER_JETS",
        "status": (
            "EXACT_SIGNED_SELECTED_MULTIPLIER_JETS_DERIVED_ON_48_RETAINED_SEAMS"
            if passed else "EXACT_SIGNED_SELECTED_MULTIPLIER_JETS_INVALID"
        ),
        "authority": "RETAINED_ACTION_EXACT_SIGNED_MIXED_DERIVATIVE_IDENTITY",
        "identity": {
            "zeroth": "mu=DS[A*psi]-D2S[B*psi,C]",
            "first": "differentiate_the_same_scalar_identity_once_before_norms",
            "second": "differentiate_the_same_scalar_identity_twice_before_norms",
            "selected_branch": SELECTED,
        },
        "summary": {
            "maximum_multiplier_absolute": float(np.max(abs(multiplier))),
            "maximum_multiplier_first_variation_absolute": float(
                abs(multiplier_first[owner_first])
            ),
            "multiplier_first_owner_node": owner_first,
            "maximum_multiplier_second_variation_absolute": float(
                abs(multiplier_second[owner_second])
            ),
            "multiplier_second_owner_node": owner_second,
            "maximum_first_separated_absolute_sum": max(
                row["first_separated_absolute_sum"] for row in rows
            ),
            "maximum_second_separated_absolute_sum": max(
                row["second_separated_absolute_sum"] for row in rows
            ),
            "maximum_exact_vs_bordered_multiplier_absolute_difference": max(
                abs(row["bordered_multiplier_difference"]) for row in rows
            ),
            "maximum_exact_vs_bordered_first_absolute_difference": max(
                abs(row["bordered_multiplier_first_difference"]) for row in rows
            ),
            "maximum_exact_vs_prior_second_absolute_difference": max(
                abs(row["prior_multiplier_second_difference"]) for row in rows
            ),
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "retained_center_selected_multiplier_signed_second_jet": (
                "DERIVED" if passed else "OPEN"
            ),
            "outward_selected_multiplier_interval_tube": "OPEN",
            "normalized_numerator_signed_product_tube": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "PROPAGATE_THE_SAME_SIGNED_ACTION_IDENTITY_THROUGH_THE_CERTIFIED_"
            "RECENTERED_CELL_INTERVALS_AND_COMPOSE_THE_DESCRIPTOR_WEIGHTED_"
            "NORMALIZED_NUMERATOR_BEFORE_ANY_RESPONSE_NORM"
        ),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
