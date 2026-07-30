from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from anomalies import anomalies_cancel
from bhsm.interface import master_action
from bhsm.interface.master_action import (
    coefficients,
    fields,
    hessians,
    measures,
    reductions,
    symmetries,
    terms,
    validation,
    variations,
)
from bhsm.interface import scalar_wall_quartic_source as quartic


def test_version_source_and_decisive_verdict_are_pinned():
    assert master_action.VERSION == "v7.0"
    assert master_action.MISSING_OBJECT == "COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR"
    assert master_action.VERDICT == (
        "BHSM_UNIFIED_PARENT_ACTION_BLOCKED_BY_MISSING_"
        "COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR_SOURCE"
    )


def test_maximal_action_is_a_three_level_complex_not_a_false_sum():
    payload = terms.payload()
    assert set(payload["levels"]) == {"S8", "S5_relative", "S4_effective"}
    assert payload["maps"] == {"R_8to5": None, "R_5to4": None}
    assert payload["master_action_closed"] is False
    assert "S8 --R_8to5--> S5|4" in payload["action_complex"]


def test_action_reality_dimensions_and_levelwise_gauge_invariance():
    rows = terms.term_rows()
    assert len(rows) == 13
    assert all(row["real"] for row in rows)
    assert all(row["mass_dimension_closed"] for row in rows)
    assert all(row["gauge_invariant"] for row in rows)
    assert len({row["term_id"] for row in rows}) == len(rows)


def test_complete_configuration_space_fields_have_required_metadata():
    required = {
        "manifold",
        "bundle",
        "representation",
        "reality_condition",
        "chirality",
        "mass_dimension",
        "boundary_regularity",
        "activity",
        "gauge_transformation",
        "diffeomorphism_transformation",
        "variation_domain",
    }
    rows = fields.field_rows()
    assert len(rows) >= 17
    assert all(required <= set(row) for row in rows)
    assert fields.configuration_space_payload()["single_configuration_space_exists"] is False


def test_representation_and_anomaly_identities_remain_exact():
    assert anomalies_cancel()
    ledger = symmetries.payload()
    anomaly = next(row for row in ledger["symmetries"] if row["symmetry"] == "anomaly_cancellation")
    assert anomaly["S4_effective"] == "EXACT_FOR_RETAINED_LEDGER"


def test_cap_orientation_GHY_and_matcher_variations_are_consistent():
    measure = measures.payload()
    boundary = variations.boundary_payload()
    assert measure["cap_orientation_check"] is True
    assert measure["GHY_sign_check"] is True
    assert boundary["GHY_cancellation"] is True
    assert boundary["matcher_variation_exact"] is True
    matcher = next(row for row in variations.equation_rows() if row["variation"] == "delta Lambda_eps")
    assert matcher["equation"] == "h_ab-gamma_eps,ab=0"


def test_scalar_field_redefinition_invariant_and_quartic_are_recovered():
    transformed = quartic.scalar_redefinition(
        2.5, z5=3.0, a5=7.0, g5=11.0, kappa1=13.0
    )
    assert transformed["lambda5_hat"] == transformed["lambda5"]
    recovered = {row["result"]: row for row in reductions.recovery_rows()}
    assert recovered["canonical scalar quartic"]["status"] == "RECOVERED_PARAMETERIZED"
    assert recovered["conditional scalar stability"]["status"] == "RECOVERED_CONDITIONALLY"


def test_every_coefficient_has_exactly_one_allowed_type():
    rows = coefficients.rows()
    assert rows
    assert all(row["classification"] in coefficients.COEFFICIENT_TYPES for row in rows)
    assert len({row["coefficient_id"] for row in rows}) == len(rows)
    assert coefficients.payload()["every_coefficient_typed"] is True


def test_no_comparison_data_or_fit_enters_action_inputs():
    for row in coefficients.rows():
        assert row["fitted"] is False
        if row["comparison_input"]:
            assert row["action_level"] == "ACTION_EXCLUDED"
            assert row["classification"] == "REJECTED_AS_INCOMPATIBLE"
    assert coefficients.payload()["comparison_inputs_in_action"] == []


def test_gauge_and_charged_double_counting_is_removed():
    rows = validation.no_double_counting_rows()
    assert not any(row["duplicate"] for row in rows)
    charged = next(row for row in rows if row["pair"].startswith("explicit charged"))
    assert charged["decision"] == "EXPLICIT_G_CH_TERM_REMOVED_AS_REDUNDANT"
    assert validation.no_double_counting_payload()["passed"] is True


def test_fermion_hermiticity_and_charged_adjoint_pair():
    fermion = next(row for row in terms.term_rows() if row["term_id"] == "T4_fermion")
    yukawa = next(row for row in terms.term_rows() if row["term_id"] == "T4_Yukawa")
    charged = next(row for row in hessians.rows() if row["block"] == "charged")
    assert fermion["real"] is True
    assert "h.c." in yukawa["expression"]
    assert charged["adjoint_domain"] == "Hermitian adjoint pair"


def test_neutral_response_reality_and_domain_are_explicitly_conditional():
    term = next(row for row in terms.term_rows() if row["term_id"] == "T4_neutral_aux")
    block = next(row for row in hessians.rows() if row["block"] == "neutral_response")
    assert term["real"] is True
    assert "response cone" in block["domain"]
    assert block["status"] == "EFFECTIVE_CONDITIONAL"


def test_fixed_h_D0_operator_and_kkt_domain_are_recovered():
    block = next(row for row in hessians.rows() if row["block"] == "D0_fixed_h")
    assert block["status"] == "RECOVERED_EXACTLY"
    assert "matcher KKT" in block["operator"]
    assert hessians.payload()["fixed_h_D0_recovered"] is True


def test_every_sector_was_examined_and_has_a_decision():
    rows = reductions.sector_rows()
    assert {row["sector"] for row in rows} == {
        "geometry/gravity",
        "gauge",
        "fermion",
        "scalar/topographic",
        "charged current",
        "neutral/neutrino",
        "projectors/generations",
        "scale/normalization",
    }
    assert all(row["final_status"] and row["coefficient_outcome"] for row in rows)


def test_low_energy_SM_map_is_complete_and_honest():
    payload = reductions.sm_payload()
    assert payload["formal_relation"] == "S4eff = S_SM,retained(inputs) + DeltaS_BHSM"
    assert payload["full_Standard_Model_recovered"] is False
    assert len(payload["terms"]) >= 10
    assert "licensed neutrino mass operator" in payload["exact_missing_terms"]


def test_all_historical_results_are_recovered_retired_or_reclassified():
    payload = reductions.recovery_payload()
    assert payload["all_historical_results_classified"] is True
    assert payload["silently_preserved_results"] == []
    assert len(payload["results"]) >= 15


def test_obstruction_is_singular_exact_and_not_overstated():
    payload = validation.obstruction_payload()
    assert payload["every_independent_sector_examined"] is True
    assert payload["exact_missing_object"] == master_action.MISSING_OBJECT
    assert payload["why_not_inequivalence_theorem"]
    assert payload["why_not_scale_only"]
    assert validation.verdict_payload()["outcome"] == "C_MAXIMAL_ACTION_WITH_EXACT_MISSING_SOURCE"


def test_completion_gate_remains_open_and_localizes_RB01():
    payload = validation.canonical_completion_gate_payload()
    assert payload["BHSM_1_0_release_complete"] is False
    assert payload["RB01"]["status"] == "BLOCKED_EXACT_OBJECT_LOCALIZED"
    assert payload["current_tier_status"]["Tier_A"] == "BLOCKED"
    assert payload["parameter_free_extension_blocker"] == "RB-02"


def test_model_validation_contract_passes():
    checks = master_action.validate_model()
    assert checks
    assert all(checks.values()), checks


def test_nineteen_required_artifacts_are_deterministic_and_current():
    assert len(master_action.ARTIFACT_FILES) == 19
    first = master_action.artifact_bytes()
    second = master_action.artifact_bytes()
    assert first == second
    for filename, content in first.items():
        assert (ROOT / "artifacts" / filename).read_bytes() == content
        if filename.endswith(".json"):
            json.loads(content)


def test_materializer_is_idempotent_and_canonical_gate_is_current():
    script = ROOT / "scripts" / "materialize_complete_unified_parent_action_v7_0.py"
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = master_action.artifact_bytes()
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    assert first == master_action.artifact_bytes()
    canonical = json.loads((ROOT / "artifacts" / "BHSM_1_0_completion_gate.json").read_text(encoding="utf-8"))
    assert canonical["version"] == "v8.1"


def test_cli_reports_action_terms_inputs_reduction_and_verdict():
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(SRC)
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "master-action-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["validation_passed"] is True
    assert payload["RB01_result"] == (
        "RB_01_UNIFIED_PARENT_ACTION_PROVENANCE_CLOSED"
    )
    assert payload["core_result"] == "BHSM_CORE_COMPLETE"
    assert payload["remaining_exact_object"] == (
        "COMMON_SCHEME_OBSERVABLE_TRANSPORT_FUNCTOR"
    )


def test_frozen_prediction_integrity_is_exact():
    assert master_action.frozen_hashes_match(ROOT)
    for path, expected in {
        "docs/frozen_predictions.md": "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
        "docs/frozen_predictions.json": "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
    }.items():
        assert master_action.frozen_file_sha256(ROOT / path) == expected
