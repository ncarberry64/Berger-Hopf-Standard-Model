import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from scalar_action import (
    CURVATURE_SCREENED,
    DERIVATIVE_SCREENED,
    FORBIDDEN_UNSCREENED_LIGHT_SCALAR,
    HIGGS_PROJECTED_LIGHT_MODE,
    HOPF_GAP_LIFTED,
    HT_COMPLEMENT_LIFTED,
    VIRTUAL_ONLY,
    action_level_scalar_modes,
    scalar_action_terms,
)
from scalar_decoupling_proof import (
    FULL_ACTION_PROVEN,
    SCALAR_ACTION_SCAFFOLD_PASSES,
    build_scalar_action_proof_report,
    classify_action_scalar_mode,
    explicit_unscreened_scalar_risk_example,
    export_fifth_force_report_json,
    export_fifth_force_report_markdown,
    export_scalar_action_proof_json,
    export_scalar_action_proof_markdown,
)
from state_ontology import BHSMState, StateCategory, classify_state


def test_action_scaffold_allows_exactly_one_higgs_projection():
    modes = action_level_scalar_modes()
    higgs_modes = [mode for mode in modes if mode.channel == HIGGS_PROJECTED_LIGHT_MODE]

    assert len(higgs_modes) == 1
    assert higgs_modes[0].on_shell_light_particle is True
    assert classify_action_scalar_mode(higgs_modes[0]) == "ALLOWED_SM_HIGGS"


def test_heavy_lifted_modes_are_not_forbidden():
    modes = action_level_scalar_modes()
    heavy_modes = [mode for mode in modes if mode.channel in {HOPF_GAP_LIFTED, HT_COMPLEMENT_LIFTED}]

    assert heavy_modes
    for mode in heavy_modes:
        assert mode.on_shell_light_particle is False
        assert classify_action_scalar_mode(mode) == "LIFTED_NOT_LIGHT_PARTICLE"
        assert mode.status != FORBIDDEN_UNSCREENED_LIGHT_SCALAR


def test_screened_and_virtual_topographic_modes_are_not_on_shell_light_particles():
    modes = action_level_scalar_modes()
    screened_channels = {DERIVATIVE_SCREENED, CURVATURE_SCREENED, VIRTUAL_ONLY}
    screened_modes = [mode for mode in modes if mode.channel in screened_channels]

    assert {mode.channel for mode in screened_modes} == screened_channels
    for mode in screened_modes:
        assert mode.on_shell_light_particle is False
        assert classify_action_scalar_mode(mode) == "SCREENED_OR_VIRTUAL_CONDITIONAL"


def test_unscreened_light_scalar_risk_is_reported_explicitly():
    terms = scalar_action_terms()
    risk_terms = [term for term in terms if term.channel == FORBIDDEN_UNSCREENED_LIGHT_SCALAR]
    example = explicit_unscreened_scalar_risk_example()

    assert len(risk_terms) == 1
    assert risk_terms[0].forbids_unscreened_light_scalar is True
    assert example["classification"] == FORBIDDEN_UNSCREENED_LIGHT_SCALAR
    assert example["violates_low_energy_ontology"] is True
    assert example["reported_not_hidden"] is True


def test_fifth_force_ranges_are_generated_where_masses_exist():
    report = build_scalar_action_proof_report()
    massive_rows = [row for row in report.fifth_force_bounds if row.effective_mass_gev is not None]

    assert massive_rows
    assert all(row.compton_range_m is not None for row in massive_rows)
    assert all(row.limitations for row in report.fifth_force_bounds)


def test_scalar_action_ontology_is_consistent_with_state_ontology():
    screened = BHSMState(
        id="v1_5_screened_topographic",
        name="v1.5 screened topographic scaffold mode",
        sector="scalar_topographic",
        description="Screened scalar/topographic mode from v1.5 action scaffold.",
        internal_mode=True,
        screened=True,
        light=True,
    )
    forbidden = BHSMState(
        id="v1_5_unscreened_light_scalar",
        name="v1.5 unscreened scalar risk",
        sector="scalar_topographic",
        description="Diagnostic unscreened direct-coupled light scalar risk.",
        internal_mode=True,
        on_shell=True,
        light=True,
        couples_as_observable=True,
    )

    assert classify_state(screened).category == StateCategory.SCREENED_TOPOGRAPHIC_STATE
    assert classify_state(screened).observable_particle is False
    assert classify_state(forbidden).category == StateCategory.FORBIDDEN_EXTRA_LIGHT_STATE


def test_scalar_action_proof_report_is_conservative_and_uses_formal_kernel():
    report = build_scalar_action_proof_report()

    assert report.status == SCALAR_ACTION_SCAFFOLD_PASSES
    assert report.theorem_complete is False
    assert report.status != FULL_ACTION_PROVEN
    assert report.open_scalar_risks == ()
    assert report.dangerous_proxy_modes == ()
    assert report.corrected_ht_dependency["model_level"] == "DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL"
    assert report.corrected_ht_dependency["old_coordinate_first_superseded"] is True
    assert report.corrected_ht_dependency["theorem_complete"] is False


def test_scalar_action_scaffold_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_scalar_action_proof_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert bare_after.outputs["up_quark_ratios"]["light"] == dressed_after.outputs["up_quark_ratios"]["light"]
    assert bare_after.outputs["ckm"]["angles"]["sin_theta_13"] == dressed_after.outputs["ckm"]["angles"]["sin_theta_13"]
    assert [row for row in comparison["rows"] if row["changed"]] == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_scalar_action_theorem_modules_do_not_import_empirical_or_residual_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "scalar_action.py",
            "topographic_action.py",
            "scalar_decoupling_proof.py",
            "fifth_force_bounds.py",
        )
    )
    forbidden_tokens = (
        "EMPIRICAL_MASS_RATIOS",
        "from ckm",
        "compute_ckm",
        "from pmns",
        "compute_pmns",
        "build_prediction_ledger",
        "build_residual_audit",
        "precision_rg_matching",
        "QuarkRatioComparison",
    )

    assert all(token not in sources for token in forbidden_tokens)


def test_scalar_action_exports_generate_cleanly(tmp_path):
    md = tmp_path / "scalar_action.md"
    data_path = tmp_path / "scalar_action.json"
    force_md = tmp_path / "fifth_force.md"
    force_json = tmp_path / "fifth_force.json"

    export_scalar_action_proof_markdown(md)
    export_scalar_action_proof_json(data_path)
    export_fifth_force_report_markdown(force_md)
    export_fifth_force_report_json(force_json)

    data = json.loads(data_path.read_text())
    force = json.loads(force_json.read_text())
    assert data["report"]["status"] == SCALAR_ACTION_SCAFFOLD_PASSES
    assert data["report"]["theorem_complete"] is False
    assert data["unscreened_scalar_risk_example"]["classification"] == FORBIDDEN_UNSCREENED_LIGHT_SCALAR
    assert force["theorem_complete"] is False
    assert "fully proven" not in md.read_text().lower()


def test_generated_v1_5_scalar_action_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "bhsm_v1_5_scalar_action_decoupling.md",
        root / "theory" / "bhsm_v1_5_scalar_action_decoupling.json",
        root / "theory" / "scalar_fifth_force_bound_report.md",
        root / "theory" / "scalar_fifth_force_bound_report.json",
        root / "manuscript" / "BHSM_v1_5_scalar_action_decoupling_note.md",
        root / "notebooks" / "41_scalar_action_decoupling.ipynb",
    )

    for path in paths:
        assert path.exists(), path

    data = json.loads(paths[1].read_text())
    text = paths[0].read_text()
    note = paths[4].read_text()

    assert data["report"]["status"] == SCALAR_ACTION_SCAFFOLD_PASSES
    assert data["report"]["theorem_complete"] is False
    assert "DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL" in text
    assert "not claim full scalar decoupling" in note
    assert "fully proven" not in (text + note).lower()
