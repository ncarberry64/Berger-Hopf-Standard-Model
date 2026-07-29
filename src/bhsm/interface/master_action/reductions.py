"""Historical reconciliation and low-energy reduction audit."""

from __future__ import annotations

from .common import MISSING_OBJECT, envelope


def historical_rows() -> list[dict]:
    return [
        {
            "architecture": "v5.4 unified boundary action",
            "domain": "unspecified Sigma/collar effective boundary",
            "status": "EFFECTIVE_ONLY",
            "retained": "term taxonomy and levelwise variational templates",
            "retired": "claim that symbolic coefficients form a unified parent action",
            "evidence": ["artifacts/BHSM_unified_dynamical_action_candidate_v5_4.json"],
            "map_to_master_complex": "S4_effective template",
        },
        {
            "architecture": "v6.0.5 minimal M8 parent",
            "domain": "M8=R_t x S7",
            "status": "PROVISIONAL_PARENT_KILL_TEST",
            "retained": "finite local P1+chi+sigma action family",
            "retired": "physicality trigger and selected physical parent status",
            "evidence": ["artifacts/BHSM_minimal_parent_theory_freeze_v6_0_5.json"],
            "map_to_master_complex": "S8 node",
        },
        {
            "architecture": "v6.1.3-v6.30 two-cap constrained gravity",
            "domain": "M5_+ disjoint_union M5_- with common intrinsic B1",
            "status": "VALID_RELATIVE_ACTION_ON_DECLARED_DOMAIN",
            "retained": "P1 caps, GHY, B1, exact matcher, D0 reduction and scalar potential",
            "retired": "interpretation as reduction of M8 without a map",
            "evidence": [
                "artifacts/BHSM_frozen_bulk_boundary_total_action_v6_1_4.json",
                "artifacts/BHSM_fixed_h_canonical_interaction_v6_30_5.json",
            ],
            "map_to_master_complex": "S5|4 node",
        },
        {
            "architecture": "v6.7 boundary matter action",
            "domain": "intrinsic M4/B1",
            "status": "CONDITIONAL_EFFECTIVE_ACTION",
            "retained": "levelwise matter variation, representation and Green pairing",
            "retired": "parent-derived Dirac or unique self-adjoint domain claim",
            "evidence": ["artifacts/BHSM_complete_boundary_action_v6_7_0.json"],
            "map_to_master_complex": "conditional subset of S4_effective",
        },
    ]


def historical_payload() -> dict:
    return envelope(
        "BHSM_historical_action_reconciliation_v7_0",
        architectures=historical_rows(),
        coequal_authoritative_parent_actions=False,
        authoritative_object="maximal three-node action complex with explicitly missing arrows",
        equivalence_or_reduction_theorem_exists=False,
        missing_object=MISSING_OBJECT,
    )


def sector_rows() -> list[dict]:
    return [
        {"sector": "geometry/gravity", "S8_source": "P1 Einstein-Hilbert", "S5_source": "two P1 caps plus GHY", "S4_source": "C_partial R4", "reduction": "MISSING", "coefficient_outcome": "finite independent inputs", "final_status": "LEVELWISE_CLOSED_CROSS_LEVEL_BLOCKED"},
        {"sector": "gauge", "S8_source": None, "S5_source": "conditional B1 connection only", "S4_source": "Yang-Mills action", "reduction": "MISSING", "coefficient_outcome": "g1,g2,g3 independent; 1:2:7 rejected as action weights", "final_status": "EFT_CLOSED_PARENT_ATTACHMENT_BLOCKED"},
        {"sector": "fermion", "S8_source": None, "S5_source": "adopted B1 Clifford pairing", "S4_source": "Dirac plus Yukawa EFT", "reduction": "MISSING", "coefficient_outcome": "Yukawa matrices independent; kinetic normalization redundant", "final_status": "EFT_CLOSED_PARENT_ATTACHMENT_BLOCKED"},
        {"sector": "scalar/topographic", "S8_source": "sigma kinetic and polynomial potential", "S5_source": "cap scalar plus B1 reduction", "S4_source": "Higgs-like scalar EFT", "reduction": "MISSING", "coefficient_outcome": "lambda5 independent", "final_status": "D0_RECOVERED_CROSS_LEVEL_BLOCKED"},
        {"sector": "charged current", "S8_source": None, "S5_source": "no independent normalized term", "S4_source": "contained in SU2 covariant derivative", "reduction": "MISSING", "coefficient_outcome": "g_ch removed as redundant; CKM from independent Yukawas", "final_status": "EFT_EXACT_SCREEN_LAW_NOT_DERIVED"},
        {"sector": "neutral/neutrino", "S8_source": None, "S5_source": "conditional response candidates", "S4_source": "SM neutral current plus DeltaS neutral auxiliary EFT", "reduction": "MISSING", "coefficient_outcome": "neutral response coefficients independent", "final_status": "EFT_PARAMETERIZED_CONE_CONDITIONAL"},
        {"sector": "projectors/generations", "S8_source": None, "S5_source": "triality/sector boundary data", "S4_source": "representation and finite projector inputs", "reduction": "MISSING", "coefficient_outcome": "triality representation-derived; sector/mode projectors independent", "final_status": "FINITE_TYPED_NOT_PARENT_DERIVED"},
        {"sector": "scale/normalization", "S8_source": "dimensionful primitives without selected unit", "S5_source": "dimensionless representative", "S4_source": "unit-free EFT coefficients", "reduction": "MISSING", "coefficient_outcome": "no calibration exercised", "final_status": "TIER_B_SCALE_OPEN"},
    ]


def sector_payload() -> dict:
    return envelope(
        "BHSM_master_sector_reduction_map_v7_0",
        sectors=sector_rows(),
        every_sector_examined=True,
        every_sector_levelwise_action_or_retirement_recorded=True,
        common_failure=MISSING_OBJECT,
    )


def sm_rows() -> list[dict]:
    return [
        {"SM_term": "SU3xSU2xU1 gauge kinetic", "status": "PRESENT_AS_INDEPENDENT_INPUT", "source": "S4eff", "missing_for_parent_recovery": "gauge bundle/measure pushforward"},
        {"SM_term": "fermion kinetic and spin connection", "status": "RECOVERED_CONDITIONALLY", "source": "S4eff", "missing_for_parent_recovery": "bulk spinor branching and unique Dirac domain"},
        {"SM_term": "chirality and representations", "status": "RECOVERED_CONDITIONALLY", "source": "retained representation ledger", "missing_for_parent_recovery": "polarization from parent bundle"},
        {"SM_term": "charges and anomaly cancellation", "status": "RECOVERED_EXACTLY_CONDITIONAL_ON_REPRESENTATION", "source": "v6.3 ledger", "missing_for_parent_recovery": "representation selection"},
        {"SM_term": "scalar kinetic/potential", "status": "PRESENT_AS_INDEPENDENT_INPUT", "source": "S4eff and D0 map", "missing_for_parent_recovery": "cross-level scalar normalization"},
        {"SM_term": "charged currents", "status": "RECOVERED_EXACTLY_AT_EFT_LEVEL", "source": "SU2 covariant derivative", "missing_for_parent_recovery": "bulk gauge-spinor reduction"},
        {"SM_term": "neutral currents", "status": "RECOVERED_EXACTLY_AT_EFT_LEVEL", "source": "SU2xU1 covariant derivative", "missing_for_parent_recovery": "bulk gauge-spinor reduction"},
        {"SM_term": "Yukawa and mass operators", "status": "PRESENT_AS_INDEPENDENT_INPUT", "source": "Y_u,Y_d,Y_e", "missing_for_parent_recovery": "overlap/projector pushforward"},
        {"SM_term": "CKM", "status": "ACTION_DERIVED_FROM_INDEPENDENT_YUKAWAS", "source": "U_u^dagger U_d", "missing_for_parent_recovery": "BHSM screen law not derived"},
        {"SM_term": "PMNS/neutrino masses", "status": "MISSING_FROM_MINIMAL_RETAINED_SM_ACTION", "source": None, "missing_for_parent_recovery": "licensed neutrino mass operator and scale"},
        {"SM_term": "higher-dimensional BHSM corrections", "status": "PARAMETERIZED_DELTA_S", "source": "neutral/scalar response EFT", "missing_for_parent_recovery": "cutoff and reduction coefficients"},
    ]


def sm_payload() -> dict:
    return envelope(
        "BHSM_SM_low_energy_reduction_v7_0",
        formal_relation="S4eff = S_SM,retained(inputs) + DeltaS_BHSM",
        relation_status="VALID_EFT_DECOMPOSITION_NOT_DERIVED_FROM_S8_OR_S5",
        terms=sm_rows(),
        full_Standard_Model_recovered=False,
        exact_missing_terms=["licensed neutrino mass operator", "parent-derived Yukawa/projector map"],
        physical_observable_map_closed=False,
    )


def recovery_rows() -> list[dict]:
    return [
        {"result": "charge and anomaly algebra", "master_term": "S4 fermion covariant derivative", "operation": "representation trace", "status": "RECOVERED_CONDITIONALLY", "agreement": "exact"},
        {"result": "Berger spectral results", "master_term": "internal geometry datum", "operation": "spectral decomposition", "status": "EFFECTIVE_INPUT_GEOMETRY", "agreement": "exact at declared a"},
        {"result": "three-generation triality projectors", "master_term": "finite family bundle", "operation": "Z3 spectral projection", "status": "RECOVERED_CONDITIONALLY", "agreement": "exact algebra"},
        {"result": "charged overlap formulas", "master_term": "screen-only projector geometry", "operation": "mode overlap", "status": "EFFECTIVE_ONLY", "agreement": "formula unchanged"},
        {"result": "frozen charged-ratio screens", "master_term": None, "operation": "screen computation", "status": "RETAINED_SCREEN_NOT_ACTION_RECOVERED", "agreement": "hash unchanged"},
        {"result": "CKM structural screens", "master_term": None, "operation": "internal screen rule", "status": "RETAINED_SCREEN_NOT_ACTION_RECOVERED", "agreement": "hash unchanged"},
        {"result": "gauge screens", "master_term": None, "operation": "candidate weights", "status": "RETAINED_SCREEN_NOT_ACTION_RECOVERED", "agreement": "hash unchanged"},
        {"result": "fixed-h D0 operator", "master_term": "S5 caps+GHY+B1+matcher", "operation": "second variation and D0 restriction", "status": "RECOVERED_EXACTLY", "agreement": "historical tests"},
        {"result": "second-order solvability", "master_term": "S5 relative action", "operation": "KKT range projection", "status": "RECOVERED_EXACTLY", "agreement": "Omega2=0"},
        {"result": "third-order exact-branch obstruction", "master_term": "S5 relative action", "operation": "kernel projection", "status": "RECOVERED_EXACTLY", "agreement": "historical coefficient"},
        {"result": "fourth-order reduced potential", "master_term": "S5 relative action", "operation": "Lyapunov-Schmidt reduction", "status": "RECOVERED_EXACTLY", "agreement": "historical artifact"},
        {"result": "canonical scalar quartic", "master_term": "S5 scalar potential", "operation": "canonical field normalization", "status": "RECOVERED_PARAMETERIZED", "agreement": "function of lambda5 unchanged"},
        {"result": "conditional scalar stability", "master_term": "reduced quartic", "operation": "quartic sign inequality", "status": "RECOVERED_CONDITIONALLY", "agreement": "threshold unchanged"},
        {"result": "PMNS effective screen", "master_term": None, "operation": "alpha rule", "status": "CANDIDATE_EFFECTIVE_ONLY", "agreement": "hash unchanged"},
        {"result": "Higgs scale screen", "master_term": None, "operation": "external scale formula", "status": "INVALIDATED_AS_ACTION_PREDICTION", "agreement": "retained comparison screen only"},
    ]


def recovery_payload() -> dict:
    return envelope(
        "BHSM_existing_result_recovery_matrix_v7_0",
        results=recovery_rows(),
        all_historical_results_classified=True,
        silently_preserved_results=[],
    )
