import json
from fractions import Fraction
from math import isclose, pi
from pathlib import Path

from anomalies import anomalies_cancel
from bhsm_config import canonical_geometry_config
from bhsm_model import (
    build_bhsm_model,
    compute_geometric_couplings,
    compute_higgs_sector,
    compute_ht_gap_status,
    compute_scalar_decoupling_status,
    compute_yukawa_ratios,
    export_model_card_json,
    export_model_card_markdown,
    generation_mode_ledger,
    model_summary,
    standard_model_field_ledger,
)
from boundary_derivation import DerivationStatus
from lagrangian import (
    effective_neutrino_extension,
    fermion_kinetic_terms,
    gauge_kinetic_terms,
    higgs_kinetic_and_potential,
    topographic_internal_correction,
    yukawa_terms,
)
from mode_selection import EXPECTED_LEDGER
from yukawa_overlap import mass_ratio


def test_build_bhsm_model_returns_complete_model():
    model = build_bhsm_model()
    summary = model_summary(model)
    canonical = canonical_geometry_config()

    assert model.gauge_group.display
    assert len(model.fermion_fields) == 5
    assert model.higgs.expression == "H(x,y)=H(x)Phi(y)"
    assert model.geometry_config.name == canonical.name
    assert model.geometry_config.a == canonical.a
    assert summary["anomalies_cancel"] is True
    assert summary["theorem_complete"] is False


def test_gauge_group_is_standard_model_group():
    model = build_bhsm_model()

    assert model.gauge_group.display == "SU(3)_c x SU(2)_L x U(1)_Y"
    assert model.gauge_group.factors == ("SU(3)_c", "SU(2)_L", "U(1)_Y")


def test_physical_hypercharges_match_standard_model_ledger():
    fields = {field.name: field.representation.hypercharge for field in standard_model_field_ledger()}

    assert fields == {
        "Q_L": Fraction(1, 6),
        "u_R": Fraction(2, 3),
        "d_R": Fraction(-1, 3),
        "L_L": Fraction(-1, 2),
        "e_R": Fraction(-1, 1),
    }


def test_anomalies_cancel_in_model_summary():
    summary = model_summary(build_bhsm_model())

    assert anomalies_cancel() is True
    assert summary["anomalies_cancel"] is True
    assert all(value == 0 for value in summary["anomaly_residuals"].values())


def test_three_generations_and_mode_ledger_match_current_tests():
    model = build_bhsm_model()
    ledger = generation_mode_ledger()

    assert all(field.generations == 3 for field in model.fermion_fields)
    assert all(len(modes) == 3 for modes in ledger.values())
    assert [(mode.k, mode.j) for mode in ledger["charged_leptons"][1:]] == EXPECTED_LEDGER["lepton"]
    assert [(mode.k, mode.j) for mode in ledger["up_quarks"][1:]] == EXPECTED_LEDGER["up"]
    assert [(mode.k, mode.j) for mode in ledger["down_quarks"][1:]] == EXPECTED_LEDGER["down"]


def test_boundary_operators_remain_action_linked_not_action_derived():
    model = build_bhsm_model()

    assert set(model.boundary_derivation_status.values()) == {DerivationStatus.ACTION_LINKED.value}
    assert DerivationStatus.ACTION_DERIVED.value not in model.boundary_derivation_status.values()


def test_yukawa_ratios_are_computed_from_mode_overlaps():
    model = build_bhsm_model()
    ratios = compute_yukawa_ratios(model)

    for sector, modes in model.generation_modes.items():
        for mode in modes:
            assert ratios[sector][mode.generation_rank] == mass_ratio(
                mode.k,
                mode.j,
                a=model.geometry_config.a,
            )


def test_geometric_couplings_match_supplied_values():
    couplings = compute_geometric_couplings(build_bhsm_model())["values"]

    assert isclose(couplings["alpha_1"], 1 / (6 * pi**2))
    assert isclose(couplings["alpha_2"], 1 / (3 * pi**2))
    assert isclose(couplings["alpha_3"], 7 / (6 * pi**2))


def test_higgs_scale_calculation_runs():
    higgs = compute_higgs_sector(build_bhsm_model())

    assert higgs["status"] == "screened"
    assert higgs["outputs"]["v_gev"] > 0
    assert higgs["outputs"]["m_lift_gev"] > 0


def test_ht_gap_status_is_proxy_level():
    ht = compute_ht_gap_status(build_bhsm_model())

    assert ht["status"] == "PROXY_AUDIT"
    assert ht["model_level"] == "DIRAC_PROXY_LEVEL_2"
    assert ht["passes"] is True
    assert ht["theorem_complete"] is False


def test_scalar_decoupling_status_is_finite_basis_scaffold():
    scalar = compute_scalar_decoupling_status(build_bhsm_model())

    assert scalar["status"] == "FINITE_BASIS_SCAFFOLD"
    assert scalar["passes"] is True
    assert scalar["theorem_complete"] is False


def test_symbolic_lagrangian_blocks_are_present():
    assert "G_" in gauge_kinetic_terms()
    assert "Q_L" in fermion_kinetic_terms()
    assert "H^\\dagger H" in higgs_kinetic_and_potential()
    assert "Y_u" in yukawa_terms()
    assert "c_{ij}" in effective_neutrino_extension()
    assert "topo/int" in topographic_internal_correction()


def test_model_card_exports_to_markdown_and_json(tmp_path):
    model = build_bhsm_model()
    md_path = tmp_path / "model.md"
    json_path = tmp_path / "model.json"

    export_model_card_markdown(model, md_path)
    export_model_card_json(model, json_path)

    markdown = md_path.read_text()
    data = json.loads(json_path.read_text())
    assert "Field and Representation Ledger" in markdown
    assert "ALPHA_ANCHORED" in markdown
    assert "alpha^{-1}/(12*pi^2)" in markdown
    assert data["gauge_group"] == "SU(3)_c x SU(2)_L x U(1)_Y"
    assert data["geometry_config"]["name"] == "ALPHA_ANCHORED"
    assert data["ht_gap"]["status"] == "PROXY_AUDIT"


def test_generated_model_card_avoids_forbidden_completion_phrases(tmp_path):
    model = build_bhsm_model()
    md_path = tmp_path / "model.md"
    json_path = tmp_path / "model.json"
    export_model_card_markdown(model, md_path)
    export_model_card_json(model, json_path)

    text = md_path.read_text().lower() + "\n" + json_path.read_text().lower()
    assert "fully proven" not in text
    assert "completed first-principles derivation" not in text
