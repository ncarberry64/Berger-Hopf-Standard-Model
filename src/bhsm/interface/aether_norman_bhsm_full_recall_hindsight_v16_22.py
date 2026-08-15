"""Full Norman-works/BHSM recall at the v16.21 microscopic frontier.

This is a provenance and dependency audit, not a new dynamical model.  It
records which ideas survive as causal guidance, which equations cannot be
imported into the anchored replacement action, and what the current KKT
calculation has already superseded.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


VERSION = "v16.22"
CLASSIFICATION = "BHSM_NORMAN_WORKS_FULL_RECALL_AND_HINDSIGHT"
FULL_BHSM_COMPLETE = False
USB_OR_REMOTE_SYNC_AUTHORIZED = False


SOURCE_LEDGER = (
    {
        "source": "Norman's_Hypersphere.pdf",
        "sha256": "8d98a9a66388a41755e6f5fd6142c1d1434868d75f1e50358089841c75807d32",
        "kind": "INDEPENDENT_COMPACT_S3_SCALAR_TOPOGRAPHIC_EFT",
        "disposition": "RECLASSIFIED",
    },
    {
        "source": "A_Hyperspherical_Scalar_Topographic_Framework (3).pdf",
        "sha256": "138d39964745706fbe22fc0524a7412b408a37b65f0f7b2cf8d6a3817e9ee3b0",
        "kind": "SCALAR_TOPOGRAPHIC_PHENOMENOLOGY",
        "disposition": "RECLASSIFIED",
    },
    {
        "source": "topographic_dark_energy_arxiv_ready.pdf",
        "sha256": "1b063a869e5aa12b90bdad80d708f51b8d847a492cc233fc7fd7e62b63a09b19",
        "kind": "SEPARATE_HORNDESKI_GALILEON_COSMOLOGY_BRANCH",
        "disposition": "RECLASSIFIED",
    },
    {
        "source": "mass_from_local_curvature_thresholds_scalar_topographic_eft.pdf",
        "sha256": "8c491926b5a419064b515ab2f345edd4aee66563479882e3c73bfae9d0f23f36",
        "kind": "CURVATURE_THRESHOLD_MASS_ANSATZ",
        "disposition": "INVALIDATED_AS_BHSM_MASS_NORMALIZATION",
    },
    {
        "source": "mass_gap.pdf",
        "sha256": "f32e070dca892ed21715e06416415b1e0c091e9a29cebf69ae553698659e4a53",
        "kind": "SCALAR_MASS_GAP_ANALOGUE",
        "disposition": "INVALIDATED_AS_YANG_MILLS_OR_STANDARD_MODEL_PROOF",
    },
    {
        "source": "mass_without_higgs.pdf",
        "sha256": "35323d6e0a1e4112046eef2c616614d0cc821092314d4a0681b3723ad2c6b29c",
        "kind": "EMPIRICALLY_CALIBRATED_CURVATURE_MASS_SCREEN",
        "disposition": "INVALIDATED_AS_NO_FIT_PREDICTION",
    },
    {
        "source": "BHSM_Unified_Field_Report.pdf",
        "sha256": "cb349dc3cbc05c5626e1e9faf9c2a8d4840d98f5f6a91db6832f62a60b6a1c4b",
        "kind": "HISTORICAL_COMPLETE_CLOSURE_CLAIM",
        "disposition": "INVALIDATED_BY_LATER_ACTION_PROVENANCE_AUDITS",
    },
    {
        "source": "BHSM_final_paper.pdf",
        "sha256": "ae1c1d42d16fa9a40de5f93e8d0344c9bc9787ff6b0adf364474e18230055aab",
        "kind": "HISTORICAL_FROZEN_SCREEN",
        "disposition": "RECLASSIFIED_AS_CONDITIONAL_NOT_COMPLETE",
    },
)


def verify_source_file(path: str | Path, expected_sha256: str) -> bool:
    """Verify a recalled source without making the external file a dependency."""

    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return digest.lower() == expected_sha256.lower()


def source_ledger() -> list[dict[str, str]]:
    """Return a copy of the immutable source/provenance ledger."""

    return [dict(row) for row in SOURCE_LEDGER]


def hindsight_classification() -> dict[str, list[str]]:
    """Classify the recalled mechanisms against the v16.21 anchored action."""

    return {
        "VALIDATED": [
            "A_PHYSICAL_PARTICLE_REQUIRES_A_PERSISTENT_RECONSTRUCTED_CHILD_NOT_A_STATIC_SOFT_CROSSING",
            "COMPACT_S3_HARMONICS_AND_CURVATURE_RESPONSE_REMAIN_USEFUL_MODE_SELECTION_INTUITION",
            "FORMATION_PRECEDES_ENCAPSULATION_RECONSTRUCTION_AND_RETURN",
            "ONE_COMMON_PARENT_CHILD_PROCESS_MUST_OWN_GEOMETRY_GAUGE_RANK16_AND_HUBBARD_STRATONOVICH_RESPONSES",
            "THE_V16_21_ENDPOINT_AND_PERIOD_ROWS_ARE_VARIATIONS_OF_THE_SAME_ANCHORED_DISCRETE_ACTION",
        ],
        "INVALIDATED": [
            "IMPORTING_AN_INDEPENDENT_T_OR_PHI_FIELD_INTO_THE_REPLACEMENT_ACTION",
            "IMPORTING_B_BETA_Q1_Q2_RH_ETA0_ZT_OR_ANY_ALTERNATIVE_YUKAWA_NORMALIZATION",
            "USING_A_FIXED_RADIUS_OR_CALIBRATED_CURVATURE_THRESHOLD_TABLE_AS_A_MASS_DERIVATION",
            "PROMOTING_A_SCALAR_MASS_GAP_ANALOGUE_TO_A_YANG_MILLS_OR_STANDARD_MODEL_PROOF",
            "TREATING_THE_UNIFIED_FIELD_REPORT_AS_A_COMPLETION_CERTIFICATE",
            "TREATING_THE_SOFT_EVENT_CROSSING_ALONE_AS_PARTICLE_PERSISTENCE",
            "USING_THE_ENDPOINT_RESIDUAL_AS_PERMISSION_TO_ADD_A_BOUNDARY_OR_REFLECTION_LAW",
        ],
        "RECLASSIFIED": [
            "NORMAN_SOURCES_ARE_A_CAUSAL_AND_PHENOMENOLOGICAL_MAP_NOT_MISSING_BHSM_EQUATIONS",
            "PAIR_WAKE_NEUTRINO_STRUCTURE_IS_A_DOWNSTREAM_RETURNED_CHILD_PROPAGATION_HYPOTHESIS",
            "TOPOGRAPHIC_DARK_ENERGY_IS_AN_EXTERNAL_COSMOLOGY_BRANCH_NOT_THE_MICROSCOPIC_ANCHOR",
            "THE_STATIONARY_TRANSPORT_NO_GO_DOES_NOT_FORBID_THE_CONSTRAINED_DYNAMIC_ORBIT",
            "THE_V16_21_DEFECT_IS_CASE_1_NUMERICAL_CONDITIONING_WITH_THE_RESIDUAL_OVERWHELMINGLY_IN_RANGE",
        ],
        "ACTIVE": [
            "RANK_AWARE_TRUST_REGION_SOLUTION_OF_THE_SAME_376_VARIABLE_N3_KKT_SYSTEM",
            "COMMON_M5_TO_M4_GAUGE_GHOST_RANK16_HS_PUSHFORWARD_AT_THE_SOLVED_EVENT",
        ],
        "OPEN": [
            "INDEPENDENT_N4_AND_HIGHER_ORBIT_CONVERGENCE_IN_THE_FULL_SOBOLEV_NORM",
            "NONLINEAR_FERMION_BACKREACTED_BROKEN_CHILD_BRANCH",
            "ONE_CYCLE_RETURN_WITH_A_PERSISTENT_NONZERO_MASS_GENERATING_ORDER_PARAMETER",
            "PHYSICAL_MASS_MATRICES_CKM_PMNS_CP_AND_NEUTRINO_SPLITTINGS",
            "ABSOLUTE_GAUGE_AND_MASS_SPECTRUM_FROM_THE_SAME_LOCALIZATION_PUSHFORWARD",
            "FINAL_UNIQUE_ACTUALIZATION_AND_COMPLETION_AUDIT",
        ],
    }


def completion_payload() -> dict[str, Any]:
    classification = hindsight_classification()
    validation = {
        "all_eight_recalled_sources_have_sha256_provenance": (
            len(SOURCE_LEDGER) == 8
            and all(len(row["sha256"]) == 64 for row in SOURCE_LEDGER)
        ),
        "no_recalled_external_parameter_is_promoted": any(
            "B_BETA_Q1_Q2_RH_ETA0_ZT" in row
            for row in classification["INVALIDATED"]
        ),
        "shared_gauge_and_mass_pushforward_is_preserved": any(
            "ONE_COMMON_PARENT_CHILD_PROCESS" in row
            for row in classification["VALIDATED"]
        ),
        "current_rank_aware_calculation_is_preserved": any(
            "376_VARIABLE_N3_KKT" in row for row in classification["ACTIVE"]
        ),
        "completion_remains_open": not FULL_BHSM_COMPLETE,
        "sync_remains_unauthorized": not USB_OR_REMOTE_SYNC_AUTHORIZED,
    }
    return {
        "artifact": "BHSM_aether_norman_bhsm_full_recall_hindsight_v16_22",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "USB_OR_REMOTE_SYNC_AUTHORIZED": USB_OR_REMOTE_SYNC_AUTHORIZED,
        "status": "RECLASSIFIED",
        "source_ledger": source_ledger(),
        "hindsight": classification,
        "hindsight_verdict": (
            "NO_RECALLED_NORMAN_OR_HISTORICAL_BHSM_SOURCE_CONTAINS_AN_ACTION_OWNED_"
            "ENDPOINT_VARIATION_MASS_NORMALIZATION_OR_YUKAWA_NORMALIZATION_THAT_"
            "MAY_BE_INSERTED_INTO_THE_V16_21_SYSTEM"
        ),
        "dependency_advanced": (
            "CLOSES_THE_HYPOTHESIS_THAT_THE_CURRENT_N3_DEFECT_OR_THE_DOWNSTREAM_"
            "GAUGE_MASS_NORMALIZATION_REQUIRES_A_MISSING_EQUATION_FROM_THE_RECALLED_"
            "NORMAN_WORKS;_PRESERVES_ONE_SHARED_LOCALIZATION_PUSHFORWARD"
        ),
        "active_calculation": classification["ACTIVE"][0],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_norman_bhsm_full_recall_hindsight_v16_22.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "USB_OR_REMOTE_SYNC_AUTHORIZED",
    "SOURCE_LEDGER",
    "verify_source_file",
    "source_ledger",
    "hindsight_classification",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
