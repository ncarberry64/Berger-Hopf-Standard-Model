"""Materialize the current-C2 Hopf-semigroup transport theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_c2_hopf_semigroup_transport import (
    ACTION_VERSION,
    CLASSIFICATION,
    action_transport_ledger,
    claim_boundary,
    current_c2_birth_overlap_operator,
    frozen_internal_semigroup_attachment,
    symmetric_slice_mass_test,
)


A = ROOT / "artifacts"
HARMONIC = A / "action_extension/BHSM_AE3_FAMILY_HARMONIC_ENERGY_PULLBACK_AUDIT.json"
RECOVERY = A / "action_extension/BHSM_AE3_FAMILY_MASS_ONTOLOGY_RECOVERY_AUDIT.json"
HS = A / "action_extension/BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json"
PUZZLE = A / "action_extension/BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json"
FROZEN = ROOT / "theory/bhsm_v1_frozen_prediction_set.json"
FIELDS = ROOT / "src/bhsm/interface/master_action/fields.py"
PACKET = ROOT / (
    "docs/research_packets/2026-08-03/"
    "BHSM_FINAL_PARENT_ACTION_LEPTON_MASS_COMPLETION_2026-08-03.md"
)
TARGET = A / "action_extension/BHSM_AE3_C2_HOPF_SEMIGROUP_TRANSPORT.json"
INPUTS = (
    HARMONIC,
    RECOVERY,
    HS,
    PUZZLE,
    FROZEN,
    FIELDS,
    PACKET,
    ROOT / "src/bhsm/interface/ae3_c2_hopf_semigroup_transport.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    harmonic, recovery, hs, puzzle, frozen = map(_load, INPUTS[:5])
    fields_text = FIELDS.read_text(encoding="utf-8")
    packet_text = PACKET.read_text(encoding="utf-8")
    birth = current_c2_birth_overlap_operator()
    internal = frozen_internal_semigroup_attachment()
    transport = action_transport_ledger()
    zero_slice = symmetric_slice_mass_test()
    boundary = claim_boundary()
    validation = {
        "current_round_costs_reused": (
            birth["sectors"]["charged_lepton"][
                "round_reset_dimensionless_generator_costs"
            ]
            == [0.0, 35.0, 99.0]
            and harmonic["harmonic_spectral_pullback"]["sectors"]["up"][
                "dimensionless_R_F_squared_eigenvalues"
            ]
            == [0.0, 48.0, 120.0]
        ),
        "all_three_sector_response_shapes_noncentral": birth[
            "all_sector_shapes_noncentral"
        ],
        "all_three_sector_role_orders_recovered": birth[
            "all_frozen_role_orders_recovered"
        ],
        "frozen_internal_operator_attached_to_current_C2": (
            internal["all_attachment_commutators_zero"]
            and internal["all_frozen_ratios_attached_unchanged"]
        ),
        "internal_Berger_shape_is_separate_fixed_datum": (
            '"berger_shape", "a", "internal Berger S3 datum"' in fields_text
            and '"INDEPENDENT_THEORY_INPUT"' in fields_text
        ),
        "frozen_charged_ratios_reproduced": (
            internal["sectors"]["charged_lepton"]["frozen_mass_ratio_screen"]
            == [
                frozen["prediction_sets"][0]["outputs"]["charged_lepton_ratios"][
                    role
                ]
                for role in ("heavy", "middle", "light")
            ]
        ),
        "frozen_up_ratios_reproduced": (
            internal["sectors"]["up"]["frozen_mass_ratio_screen"]
            == [
                frozen["prediction_sets"][0]["outputs"]["up_quark_ratios"][role]
                for role in ("heavy", "middle", "light")
            ]
        ),
        "frozen_down_ratios_reproduced": (
            internal["sectors"]["down"]["frozen_mass_ratio_screen"]
            == [
                frozen["prediction_sets"][0]["outputs"]["down_quark_ratios"][
                    role
                ]
                for role in ("heavy", "middle", "light")
            ]
        ),
        "semigroup_law_verified": all(
            row["composition_holds"] for row in birth["semigroup_checks"].values()
        ),
        "historical_candidate_was_not_current_AE3": not recovery[
            "lineage_ledger"
        ]["historical_semigroup_candidate_present_in_active_AE3_dependency_graph"],
        "historical_action_packet_is_v11_3": "Repository baseline:** BHSM v11.3"
        in packet_text,
        "current_HS_kernel_and_broken_saddle_absent": (
            hs["claim_boundary"]["current_C2_dynamical_HS_kernel_derived"] is False
            and hs["claim_boundary"]["current_C2_broken_LR_saddle_derived"] is False
        ),
        "current_full_field_action_still_open": puzzle[
            "CURRENT_FULL_FIELD_ACTION_COMPLETE"
        ]
        is False,
        "first_failure_is_variational_coupling": transport[
            "first_missing_variational_owner"
        ]
        == "CURRENT_AE3_INTRINSIC_M4_LR_HIGGS_COUPLING_WITH_T_C2",
        "zero_slice_does_not_fake_a_pole": (
            zero_slice["all_formal_mass_operators_zero"]
            and not zero_slice["zero_formal_mass_is_a_physical_pole_theorem"]
        ),
        "no_dimensionful_number_or_spectrum_promoted": (
            not boundary["historical_dimensionful_numbers_promoted"]
            and not boundary["particle_spectrum_rebuilt"]
        ),
    }
    return {
        "artifact": "BHSM_AE3_C2_HOPF_SEMIGROUP_TRANSPORT",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "current_C2_birth_overlap_operator": birth,
        "frozen_internal_semigroup_attachment": internal,
        "action_transport_ledger": transport,
        "symmetric_slice_mass_test": zero_slice,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3 current-C2 Hopf-semigroup transport theorem failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
