"""Materialize the affine-72 product-Dirac carrier on preserved fibers."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_current_c2_affine72_particle_fiber_calderon import (
    ACTION_VERSION,
    CLASSIFICATION,
    attach_preserved_particle_fibers,
    claim_boundary,
)
from scripts.materialize_ae4_current_c2_affine72_gauge_calderon_first_jet import (
    AFFINE,
    AFFINE_DATA,
    CENTER,
    CENTER_DATA,
    FIRST_HIT,
    MOVING,
    TRANSFER,
    build_affine72_proper_time_carrier,
)


A = ROOT / "artifacts/action_extension"
FIBERS = A / "BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json"
GAUGE_JET = A / "BHSM_AE4_CURRENT_C2_AFFINE72_GAUGE_CALDERON_FIRST_JET.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_AFFINE72_PARTICLE_FIBER_CALDERON.json"
INPUTS = (
    AFFINE,
    AFFINE_DATA,
    TRANSFER,
    MOVING,
    CENTER,
    CENTER_DATA,
    FIRST_HIT,
    FIBERS,
    GAUGE_JET,
    ROOT / "src/bhsm/interface/action_extension_ae2_angular_dini_uniformity.py",
    ROOT / "src/bhsm/interface/ae3_reciprocal_join_localization.py",
    ROOT / "src/bhsm/interface/ae4_current_c2_affine72_particle_fiber_calderon.py",
    ROOT / "src/bhsm/interface/aether_forward_c2_weyl_riccati.py",
    ROOT / "scripts/materialize_ae4_current_c2_affine72_gauge_calderon_first_jet.py",
    ROOT / "scripts/materialize_ae4_current_c2_affine72_particle_fiber_calderon.py",
    ROOT / "theory/ae4_current_c2_affine72_particle_fiber_calderon.md",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    transfer, moving, fibers, gauge = (
        _load(path) for path in (TRANSFER, MOVING, FIBERS, GAUGE_JET)
    )
    if not all(
        row.get("validation_passed") is True
        for row in (transfer, moving, fibers, gauge)
    ):
        raise RuntimeError("validated affine carrier, fiber, and moving-stop inputs required")

    carrier = build_affine72_proper_time_carrier()
    pulled = carrier["pulled"]
    frozen_rows = fibers["family_mode_C2_instantiation"]["rows"]
    result = attach_preserved_particle_fibers(
        log_radii=np.asarray(pulled["log_radius"], dtype=float),
        normalized_proper_times=np.asarray(
            pulled["normalized_proper_times"], dtype=float
        ),
        proper_duration=float(pulled["proper_duration"]),
        log_radius_first_jet=np.asarray(
            pulled["log_radius_normalized_proper_time_first_jet"], dtype=float
        ),
        proper_duration_first_jet=np.asarray(
            pulled["proper_duration_first_jet"], dtype=float
        ),
        frozen_fiber_rows=frozen_rows,
        spatial_dirac_level=0,
        spectral_parameter=-1.0,
    )
    plus = result["chiral_carrier_responses"]["plus"]
    minus = result["chiral_carrier_responses"]["minus"]
    plus_jet = np.asarray(plus["D_parameter_Weyl"], dtype=float)
    minus_jet = np.asarray(minus["D_parameter_Weyl"], dtype=float)
    plus_radius = np.asarray(plus["D_parameter_Weyl_radius_part"], dtype=float)
    plus_duration = np.asarray(plus["D_parameter_Weyl_duration_part"], dtype=float)
    boundary = claim_boundary()
    upstream_identities = [
        (row["sector"], int(row["slot"]), tuple(row["mode_label"]))
        for row in frozen_rows
    ]
    attached_identities = [
        (
            row["sector"],
            int(row["slot"]),
            tuple(row["internal_Berger_mode_label_k_j"]),
        )
        for row in result["attached_particle_fibers"]
    ]
    duration_norm = float(np.linalg.norm(plus_duration))
    radius_norm = float(np.linalg.norm(plus_radius))
    validation = {
        "existing_nine_fibers_reused_exactly": (
            upstream_identities == attached_identities
        ),
        "all_projectors_are_existing_rank_one_projectors": all(
            row["existing_projector_rank"] == 1
            and row["family_projector_reused"]
            for row in result["attached_particle_fibers"]
        ),
        "internal_and_spatial_mode_indices_not_conflated": (
            not result["index_separation"]["indices_identified_with_each_other"]
            and all(
                not row["internal_mode_relabelled_as_spatial_mode"]
                for row in result["attached_particle_fibers"]
            )
        ),
        "lowest_round_S3_product_Dirac_channel_reused": (
            plus["spatial_dirac_level_n"] == 0
            and plus["unit_radius_dirac_eigenvalue_mu_n"] == 1.5
            and minus["unit_radius_dirac_eigenvalue_mu_n"] == 1.5
        ),
        "both_chiral_carrier_first_jets_finite": bool(
            plus_jet.shape == (72,)
            and minus_jet.shape == (72,)
            and np.all(np.isfinite(plus_jet))
            and np.all(np.isfinite(minus_jet))
        ),
        "shared_affine72_proper_time_carrier_matches_gauge_unit": (
            pulled["parameter_count"] == 72
            and len(pulled["log_radius"])
            == gauge["proper_time_pullback"]["node_count"]
            and abs(
                pulled["proper_duration"]
                - gauge["proper_time_pullback"]["proper_duration"]
            )
            < 1.0e-18
        ),
        "moving_stop_duration_contribution_retained": (
            duration_norm > 1.0e6 * radius_norm
        ),
        "moving_endpoint_chain_rule_reused": moving["claim_boundary"][
            "moving_endpoint_two_jet_chain_rule"
        ]
        == "DERIVED",
        "rejected_affine_to_nonlinear_transfer_not_promoted": (
            transfer["adjudication"][
                "affine_jet_may_be_used_as_complete_operator_authority"
            ]
            is False
            and not boundary[
                "AE4_CURRENT_C2_NONLINEAR72_PARTICLE_FIBER_CALDERON_DERIVED"
            ]
        ),
        "no_spectrum_or_mass_rebuild": (
            not result["particle_spectrum_rebuilt"]
            and not result["physical_mass_operator_derived"]
            and not plus["raw_Dirac_level_identified_as_physical_mass"]
            and not boundary["PARTICLE_SPECTRUM_REBUILT"]
        ),
    }
    return _canonical(
        {
            "artifact": "BHSM_AE4_CURRENT_C2_AFFINE72_PARTICLE_FIBER_CALDERON",
            "action_version": ACTION_VERSION,
            "classification": CLASSIFICATION,
            "carrier": {
                "base_path": "ACCEPTED_CANONICAL_STOP_CENTER_PROPER_TIME_PATH",
                "first_jet": "EXISTING_72D_EXACT_AFFINE_CARRIER",
                "spatial_channel": "LOWEST_ROUND_S3_PRODUCT_DIRAC_n=0_mu=3/2",
                "nonlinear_exact_family_authority": False,
            },
            "particle_fiber_Calderon_attachment": result,
            "scientific_result": {
                "attached_existing_fiber_count": result["attached_fiber_count"],
                "plus_chirality_Weyl_birth_value": plus["Weyl_birth_value"],
                "minus_chirality_Weyl_birth_value": minus["Weyl_birth_value"],
                "plus_chirality_first_jet_2_norm": plus["D_parameter_Weyl_2_norm"],
                "minus_chirality_first_jet_2_norm": minus["D_parameter_Weyl_2_norm"],
                "plus_moving_duration_to_log_radius_norm_ratio": duration_norm
                / radius_norm,
                "family_result": (
                    "THE_CURRENT_LOWEST_SPATIAL_PRODUCT_DIRAC_CARRIER_IS_"
                    "FAMILY_CENTRAL;_THE_ALREADY_DERIVED_INTERNAL_PROJECTORS_"
                    "PRESERVE_PARTICLE_IDENTITY_WITHOUT_GENERATING_MASS"
                ),
                "interpretation": (
                    "AFFINE_CARRIER_PARTICLE_FIBER_OPERATOR_JET_CANDIDATE__"
                    "NOT_NONLINEAR_AUTHORITY_OR_PHYSICAL_POLE"
                ),
            },
            "claim_boundary": boundary,
            "exact_next_calculation": (
                "REPEAT_THE_SAME_PRODUCT_DIRAC_COTANGENT_CONTRACTION_ON_THE_"
                "CLOSED_NONLINEAR_STOP_FAMILY_AND_COMPOSE_THE_EXISTING_"
                "FAMILY_NONCENTRAL_HS_MIXED_OPERATOR_BEFORE_EXTRACTING_POLES"
            ),
            "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
            "validation": validation,
            "validation_passed": all(validation.values()),
            "FULL_BHSM_COMPLETE": False,
        }
    )


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("affine72 particle-fiber Calderon validation failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
