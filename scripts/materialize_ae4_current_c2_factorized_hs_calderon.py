"""Materialize the full finite-core factorized HS Calderon jets."""

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
    CLASSIFICATION,
    claim_boundary,
    factorized_product_dirac_hs_weyl_jet,
)


A = ROOT / "artifacts/action_extension"
F = ROOT / "artifacts/flagship_integration"
DESCRIPTOR = F / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DESCRIPTOR_DATA = F / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
NEGATIVE_AXIS = F / "BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_FACTORIZED_HS_CALDERON.json"
INPUTS = (
    A / "BHSM_AE4_STRATIFIED_DIRAC_ZETA_INDUCED_OWNER.json",
    A / "BHSM_AE4_C2_STRATIFIED_EVENT_FLUX_ASSEMBLY.json",
    A / "BHSM_AE4_CURRENT_C2_HS_FRECHET_HESSIAN.json",
    DESCRIPTOR,
    DESCRIPTOR_DATA,
    NEGATIVE_AXIS,
    ROOT / "src/bhsm/interface/aether_forward_c2_weyl_riccati.py",
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
    owner, assembly, local_hs, descriptor, negative_axis = (
        _load(INPUTS[index]) for index in (0, 1, 2, 3, 5)
    )
    if not all(
        row["validation_passed"]
        for row in (owner, assembly, local_hs, descriptor, negative_axis)
    ):
        raise RuntimeError("validated AE4 and current-C2 inputs required")

    with np.load(DESCRIPTOR_DATA) as data:
        x = np.asarray(data["node_log_R4_center"], dtype=float)
        h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)
        profile = np.ones_like(h)
        rows: list[dict[str, Any]] = []
        for normalized_magnitude in (0.1, 1.0, 10.0):
            channels: dict[str, Any] = {}
            for chirality, suffix in (
                (1, "product_Dirac_lambda1_5_chirality_plus"),
                (-1, "product_Dirac_lambda1_5_chirality_minus"),
            ):
                gap = float(
                    descriptor["descriptor_pencils"][suffix][
                        "generalized_gap_lower"
                    ]
                )
                endpoint_rows: dict[str, Any] = {}
                loads = (("zero_tail_load", 0.0), ("Dirichlet_limit", None))
                for endpoint, load in loads:
                    endpoint_rows[endpoint] = factorized_product_dirac_hs_weyl_jet(
                        log_radii=x,
                        proper_durations=h,
                        dirac_eigenvalue_at_unit_radius=1.5,
                        chirality=chirality,
                        source_profile=profile,
                        spectral_parameter=-normalized_magnitude * gap,
                        terminal_load=load,
                        decimal_precision=60,
                    )
                channels[suffix] = {
                    "analytic_generalized_gap_lower": gap,
                    "endpoint_domain_rows": endpoint_rows,
                }
            rows.append(
                {
                    "negative_axis_magnitude_over_analytic_gap": normalized_magnitude,
                    "channels": channels,
                }
            )

    central = rows[1]["channels"]
    plus = central["product_Dirac_lambda1_5_chirality_plus"][
        "endpoint_domain_rows"
    ]
    minus = central["product_Dirac_lambda1_5_chirality_minus"][
        "endpoint_domain_rows"
    ]
    all_endpoint_rows = [
        endpoint
        for row in rows
        for channel in row["channels"].values()
        for endpoint in channel["endpoint_domain_rows"].values()
    ]
    boundary = claim_boundary()
    validation = {
        "full_1222_segment_current_C2_core_consumed": all(
            endpoint["segment_count"] == 1222 for endpoint in all_endpoint_rows
        ),
        "all_negative_axis_graphs_regular": all(
            endpoint["negative_axis_regular_margin"] > 0.0
            for endpoint in all_endpoint_rows
        ),
        "all_first_and_second_HS_jets_finite": all(
            np.isfinite(endpoint["D_H_Weyl_birth"])
            and np.isfinite(endpoint["D2_H_Weyl_birth"])
            for endpoint in all_endpoint_rows
        ),
        "factorization_preserved_without_dense_spectrum_or_inverse": all(
            endpoint["first_order_product_Dirac_factorization_preserved"]
            and not endpoint["dense_generalized_eigensolve_formed"]
            and not endpoint["explicit_matrix_inverse_formed"]
            for endpoint in all_endpoint_rows
        ),
        "central_chiral_Dirichlet_second_jets_agree": abs(
            plus["Dirichlet_limit"]["D2_H_Weyl_birth"]
            - minus["Dirichlet_limit"]["D2_H_Weyl_birth"]
        )
        < 1.0e-40,
        "central_endpoint_domain_dependence_resolved_not_erased": abs(
            plus["Dirichlet_limit"]["D_H_Weyl_birth"]
            - plus["zero_tail_load"]["D_H_Weyl_birth"]
        )
        > 0.1,
        "maximal_tail_not_overclaimed": not boundary[
            "AE4_CURRENT_C2_MAXIMAL_TAIL_LOAD_AND_HS_JETS_DERIVED"
        ],
        "maximal_history_not_overclaimed": not boundary[
            "AE4_CURRENT_C2_MAXIMAL_HISTORY_RETARDED_HS_CALDERON_BLOCK_DERIVED"
        ],
    }
    return {
        "artifact": "BHSM_AE4_CURRENT_C2_FACTORIZED_HS_CALDERON",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "operator_domain": {
            "background": "RESET_GENERATED_CURRENT_C2_PROOF_CENTER_FAMILY",
            "segment_count": 1222,
            "source": "UNIT_COMMUTING_LR_HS_SUPERPOTENTIAL_SHIFT",
            "spectral_domain": "REAL_NEGATIVE_AXIS",
            "terminal_domains_evaluated": [
                "ZERO_NONNEGATIVE_TAIL_LOAD",
                "FINITE_CORE_DIRICHLET_LIMIT",
            ],
            "physical_maximal_tail_load_selected": False,
        },
        "negative_axis_HS_Calderon_rows": rows,
        "central_gap_probe_result": {
            "plus_zero_load_D_H": plus["zero_tail_load"]["D_H_Weyl_birth"],
            "plus_Dirichlet_D_H": plus["Dirichlet_limit"]["D_H_Weyl_birth"],
            "plus_zero_load_D2_H": plus["zero_tail_load"]["D2_H_Weyl_birth"],
            "plus_Dirichlet_D2_H": plus["Dirichlet_limit"]["D2_H_Weyl_birth"],
            "minus_Dirichlet_D2_H": minus["Dirichlet_limit"]["D2_H_Weyl_birth"],
            "tail_domain_changes_the_HS_Calderon_jet": True,
        },
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("factorized current-C2 HS Calderon validation failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
