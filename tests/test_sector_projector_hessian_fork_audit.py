import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import sector_projector_hessian_fork as fork  # noqa: E402


AUDIT_JSON = ROOT / "data" / "bhsm_sector_projector_hessian_fork_audit.json"
CLOSURE_MAP = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
DOCS = [
    ROOT / "docs" / "bhsm_sector_projector_ledger_theorem.md",
    ROOT / "docs" / "bhsm_charged_hessian_fork_audit.md",
    ROOT / "docs" / "bhsm_eta_projection_no_overfit.md",
    ROOT / "docs" / "bhsm_validation_invalidation_ledger.md",
]
STATUS_PATH = ROOT / "docs" / "current_bhsm_status.md"
CLAIM_TABLE = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_unified_omega_formula_reproduces_four_sector_operators():
    expected = {
        "lepton": "-q + 2j",
        "neutrino": "-q - 2j",
        "up": "q - 2j",
        "down": "q + 4j",
    }
    for sector, expression in expected.items():
        C, sigma = fork.SECTORS[sector]
        assert fork.omega_expression(C, sigma) == expression
    assert fork.audit_statuses()["unified_Omega_projector_formula"] == (
        "STRUCTURALLY_MOTIVATED_DERIVATION_CANDIDATE"
    )


def test_sector_projectors_and_down_incidence_are_deterministic():
    for sector, C, sigma in fork.sector_rows():
        projectors = fork.sector_projectors(C, sigma, sector=sector)
        active = {
            "neutrino": projectors.P_nu,
            "lepton": projectors.P_l,
            "up": projectors.P_u,
            "down": projectors.P_d,
        }
        assert active[sector] == 1
        assert sum(active.values()) == 1

    assert fork.down_sector_incidence(1, -1) == 2
    assert fork.down_sector_incidence(1, +1) == 1
    assert fork.down_sector_incidence(0, -1) == 1
    assert fork.audit_statuses()["down_extra_boundary_incidence"] == (
        "STRONGLY_SUPPORTED_CANDIDATE"
    )


def test_target_amplitude_formula_reproduces_3_3_6_12():
    expected = {
        "neutrino": 3,
        "lepton": 3,
        "up": 6,
        "down": 12,
    }
    for sector, target in expected.items():
        C, sigma = fork.SECTORS[sector]
        assert fork.target_amplitude(C, sigma) == target
    statuses = fork.audit_statuses()
    assert statuses["sector_target_amplitude_A"] == "STRUCTURALLY_MOTIVATED_CANDIDATE"
    assert statuses["base_cyclic_factor_3"] != "ACTION_DERIVED"


def test_ledgers_and_old_costs_match_only_rho_1():
    assert fork.all_charged_ledgers_preserved(1)
    assert {sector: fork.ledger_costs(sector, 1) for sector in fork.CHARGED_LEDGER} == {
        "lepton": [0, 5, 18],
        "up": [0, 36, 65],
        "down": [0, 9, 20],
    }
    assert fork.ISOTROPIC_COSTS == {
        "lepton": [0, 5, 18],
        "up": [0, 36, 65],
        "down": [0, 9, 20],
    }
    assert fork.ledger_costs("lepton", 3) != fork.ISOTROPIC_COSTS["lepton"]
    assert fork.audit_statuses()["exact_old_costs_0_5_18_etc"] == (
        "CONDITIONAL_ON_RHO_CH_EQUALS_1"
    )


def test_cyclic_anisotropy_costs_match_rho_3():
    assert fork.all_charged_ledgers_preserved(3)
    assert {sector: fork.ledger_costs(sector, 3) for sector in fork.CHARGED_LEDGER} == {
        "lepton": [0, 13, 36],
        "up": [0, 36, 67],
        "down": [0, 27, 28],
    }
    assert fork.CYCLIC_ANISOTROPY_COSTS == {
        "lepton": [0, 13, 36],
        "up": [0, 36, 67],
        "down": [0, 27, 28],
    }
    assert fork.audit_statuses()["cyclic_candidate_costs_0_13_36_etc"] == (
        "CONDITIONAL_ON_RHO_CH_EQUALS_3"
    )


def test_down_ordering_constraint_and_membership_constraint():
    assert fork.down_ordering_constraint_holds(Fraction(3, 1))
    assert not fork.down_ordering_constraint_holds(Fraction(16, 5))
    assert not fork.down_ordering_constraint_holds(Fraction(4, 1))
    assert fork.membership_constraint_holds(Fraction(7, 1))
    assert not fork.membership_constraint_holds(Fraction(8, 1))


def test_charged_neutral_hessian_fork_statuses():
    statuses = fork.audit_statuses()
    assert statuses["charged_cross_term_s_ch"] == "FORBIDDEN_CONDITIONAL"
    assert statuses["neutral_cross_term_s_neutral"] == "OPEN_ALLOWED"
    assert statuses["neutral_topographic_metric_mixing"] == "OPEN_LOCALIZABLE"
    assert statuses["charged_Hessian_anisotropy_rho_ch"] == "OPEN_LOCALIZABLE"
    assert statuses["isotropic_metric_rho_1"] == "MINIMAL_ISOTROPIC_CANDIDATE"
    assert statuses["cyclic_anisotropy_rho_3"] == "CYCLIC_ANISOTROPY_CANDIDATE"


def test_eta_l_8_over_9_route_is_not_primary_or_derived():
    audit = load_json(AUDIT_JSON)
    statuses = fork.audit_statuses()
    assert audit["eta_l_8_over_9_trace_route"] == "DOWNGRADED_NUMERICAL_COINCIDENCE"
    assert audit["eta_l_8_over_9_primary"] is False
    assert statuses["eta_l_projection_structure"] == "VALIDATED_CANDIDATE"
    assert statuses["Pi_l_value"] == "OPEN_LOCALIZABLE"
    assert statuses["alpha_geom_internal_derivation"] == "OPEN_LOCALIZABLE"
    assert statuses["eta_l_fit"] == "FORBIDDEN_AS_DERIVATION"
    assert statuses["eta_l_8_over_9_trace_route"] != "DERIVED"


def test_z_virt_dimension_ratio_strengthened_but_not_fully_derived():
    statuses = fork.audit_statuses()
    assert statuses["Z_virt_u2_dimension_ratio"] == "STRONG_DERIVATION_CANDIDATE"
    text = (ROOT / "docs" / "bhsm_eta_projection_no_overfit.md").read_text(encoding="utf-8")
    assert "dim(admissible virtual channel) / dim(two-channel virtual pair)" in text
    assert "It is not called fully" in text


def test_machine_readable_ledger_and_closure_map_include_required_statuses():
    audit = load_json(AUDIT_JSON)
    closure = load_json(CLOSURE_MAP)
    for key, status in fork.audit_statuses().items():
        assert audit[key] == status
        assert closure[key]["status"] == status
    assert audit["public_status"] == "structural architecture integrated conditional; numerical closure open"
    assert audit["frozen_predictions_changed"] is False
    assert audit["official_predictions_changed"] is False


def test_docs_include_validation_invalidation_and_public_status():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DOCS)
    combined += "\n" + STATUS_PATH.read_text(encoding="utf-8")
    combined += "\n" + CLAIM_TABLE.read_text(encoding="utf-8")
    combined += "\n" + BACKLOG.read_text(encoding="utf-8")
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "sector projector compression survives" in combined
    assert "H=I as a locked claim" in combined
    assert "exact `q^2+j^2` costs as unconditional" in combined
    assert "rho_ch" in combined
    assert "Pi_l" in combined
    assert "alpha_geom" in combined


def test_no_empirical_inputs_choose_open_parameters():
    audit = load_json(AUDIT_JSON)
    forbidden = set(audit["forbidden_inputs"])
    for item in (
        "observed masses",
        "charged lepton masses",
        "quark masses",
        "CKM values",
        "PMNS values",
        "neutrino data",
        "measured alpha",
        "CODATA alpha",
        "observed generation data",
    ):
        assert item in forbidden

    source = (ROOT / "src" / "sector_projector_hessian_fork.py").read_text(encoding="utf-8")
    forbidden_imports = ["mass_scheme", "prediction_ledger", "residual_audit", "ckm", "pmns"]
    for name in forbidden_imports:
        assert f"import {name}" not in source
        assert f"from {name}" not in source


def test_no_forbidden_claims_or_prediction_file_changes():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DOCS)
    forbidden = [
        "BHSM is proven",
        "BHSM is complete",
        "empirically validated",
        "numerically closed",
        "Standard Model replacement",
        "mass-ratio outputs changed",
        "CKM outputs changed",
        "PMNS outputs changed",
        "neutrino outputs changed",
    ]
    for phrase in forbidden:
        assert phrase not in combined
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()
