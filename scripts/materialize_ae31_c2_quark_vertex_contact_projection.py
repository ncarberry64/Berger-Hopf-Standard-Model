"""Materialize the current-C2 quark vertex/contact projection theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_vertex_contact_projection import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    descriptor_channel_incidence,
    exact_missing_incidence_map,
    projection_nonidentifiability_theorem,
    unit_probe_scaling_theorem,
)


A = ROOT / "artifacts/action_extension"
NPZ = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
TARGET = A / "BHSM_AE31_C2_QUARK_VERTEX_CONTACT_PROJECTION.json"
INPUTS = (
    A / "BHSM_AE31_C2_QUARK_CHANNEL_SELECTOR_DOMAIN.json",
    A / "BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json",
    A / "BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json",
    NPZ,
    ROOT / "docs/bhsm_sector_projector_ledger_theorem.md",
    ROOT / "src/bhsm/interface/ae31_c2_quark_vertex_contact_projection.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    selector, hs, puzzle = map(_load, INPUTS[:3])
    with np.load(NPZ) as descriptor:
        incidence = descriptor_channel_incidence(descriptor.files)
    scaling = unit_probe_scaling_theorem()
    projection = projection_nonidentifiability_theorem()
    missing_map = exact_missing_incidence_map()
    boundary = claim_boundary()
    validation = {
        "selector_domain_first_missing_vertices_reused": selector[
            "exact_dependency_order"
        ]["first_missing_object"].endswith("V_u_V_d_Q_fg"),
        "unit_probe_scaling_exact": (
            scaling["scaling_verified"]
            and scaling["vertex_scaling_residual"] < 1.0e-14
            and scaling["contact_scaling_residual"] < 1.0e-14
        ),
        "descriptor_has_chirality_but_no_up_down_axis": (
            incidence["chirality_plus_present"]
            and incidence["chirality_minus_present"]
            and not incidence["explicit_up_down_sector_axis_present"]
            and not incidence["descriptor_can_distinguish_up_from_down"]
        ),
        "existing_HS_piece_is_unit_family_central_probe": (
            hs["claim_boundary"]["current_C2_third_LR_HS_vertex_retained"]
            and all(
                row["family_factor"] == "I3"
                for row in hs["reduced_variations"].values()
            )
            and puzzle["operator_piece"]["family_factor"] == "I3"
            and puzzle["operator_piece"]["source_probe"]
            == "UNIT_COMMUTING_REDUCED_LR_HS_PROBE"
        ),
        "projectors_split_support_not_coefficients": (
            projection["both_obey_same_projector_algebra"]
            and projection["same_structural_projection_different_residue_ratio"]
            and projection["representation_projectors_select_block_support"]
            and not projection["representation_projectors_select_block_coefficients"]
        ),
        "missing_map_reuses_assets_without_free_coefficients": (
            missing_map["existing_projectors_and_family_operators_reused"]
            and not missing_map["unit_probe_may_be_declared_both_sector_coefficients"]
            and not missing_map["independent_q_up_q_down_allowed"]
            and not missing_map["quark_mass_fit_allowed"]
        ),
        "no_vertex_coefficient_selector_pole_or_completion_overclaim": (
            not boundary["CURRENT_C2_QUARK_VERTEX_CONTACT_COEFFICIENTS_ACTION_DERIVED"]
            and not boundary["CURRENT_C2_QUARK_CHANNEL_DIRECTION_SELECTED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_VERTEX_CONTACT_PROJECTION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "unit_probe_scaling_theorem": scaling,
        "descriptor_channel_incidence": incidence,
        "projection_nonidentifiability_theorem": projection,
        "exact_missing_incidence_map": missing_map,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 quark vertex/contact projection theorem failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
