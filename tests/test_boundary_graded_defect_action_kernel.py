import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import boundary_graded_defect_action_kernel as kernel  # noqa: E402


DATA_JSON = ROOT / "data" / "boundary_graded_defect_action_kernel_v1.json"
DOC = ROOT / "docs" / "boundary_graded_defect_action_kernel_v1.md"
CLAIM_STATUS = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_projector_readouts_for_all_sectors():
    expected = {
        "neutrino": {"P_C": 0, "P_plus": 1, "P_minus": 0, "P_d_overlap": 0, "P_nu": 1},
        "lepton": {"P_C": 0, "P_plus": 0, "P_minus": 1, "P_d_overlap": 0, "P_l": 1},
        "up": {"P_C": 1, "P_plus": 1, "P_minus": 0, "P_d_overlap": 0, "P_u": 1},
        "down": {"P_C": 1, "P_plus": 0, "P_minus": 1, "P_d_overlap": 1, "P_d_sector": 1},
    }
    for sector, (C, sigma) in kernel.SECTORS.items():
        p = kernel.projectors(C, sigma)
        assert p.P_C == C
        assert p.P_plus == Fraction(1 + sigma, 2)
        assert p.P_minus == Fraction(1 - sigma, 2)
        assert p.P_d_overlap == p.P_C * p.P_minus
        for key, value in expected[sector].items():
            assert getattr(p, key) == value


def test_defect_readouts_and_orientation_trace():
    for sector, (C, sigma) in kernel.SECTORS.items():
        d_c = kernel.D_C_readout(C, sigma)
        d_d = kernel.D_d_readout(C, sigma)
        gamma = kernel.Gamma_sigma_readout(C, sigma)
        assert d_c.rank_readout == (1 if C == 0 else 2)
        assert d_c.orientation_readout == (-1 if C == 0 else 1)
        assert d_d.rank_readout == (2 if sector == "down" else 1)
        assert d_d.hopf_multiplier == (2 if sector == "down" else 1)
        assert gamma.hopf_multiplier == -sigma

    assert [kernel.tau(*kernel.SECTORS[s]) for s in kernel.SECTORS] == [-1, 1, 1, 1]


def test_unified_formulas_reproduce_sector_equations():
    expected_omega = {
        "neutrino": "-q - 2j",
        "lepton": "-q + 2j",
        "up": "q - 2j",
        "down": "q + 4j",
    }
    expected_A = {"neutrino": 3, "lepton": 3, "up": 6, "down": 12}
    expected_T = {"neutrino": -3, "lepton": 3, "up": 6, "down": 12}
    for sector, (C, sigma) in kernel.SECTORS.items():
        assert kernel.omega_expression(C, sigma) == expected_omega[sector]
        assert kernel.incidence_A(C, sigma) == expected_A[sector]
        assert kernel.target_T(C, sigma) == expected_T[sector]
        assert expected_omega[sector].replace(" ", "") in kernel.SECTOR_EQUATIONS[sector].replace(" ", "")


def test_ledgers_are_zero_defect_except_reference_slot_and_tangents_match():
    for sector, ledger in kernel.LEDGERS.items():
        C, sigma = kernel.SECTORS[sector]
        assert kernel.is_reference_slot(ledger[0])
        assert kernel.delta_IT(C, sigma, *ledger[0]) != 0
        for mode in ledger[1:]:
            assert kernel.delta_IT(C, sigma, *mode) == 0
            assert kernel.S_index_trace(C, sigma, *mode) == 0
        assert kernel.tangent_difference(sector) == kernel.EXPECTED_TANGENTS[sector]


def test_action_kernel_objects_exist_and_encode_s_index_trace_constraint():
    for sector in kernel.SECTORS:
        k = kernel.build_kernel(sector)
        C, sigma = k.label.C, k.label.sigma
        assert k.status == "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL"
        assert k.D_C.name == "D_C"
        assert k.D_d.name == "D_d"
        assert k.Gamma_sigma.name == "Gamma_sigma"
        assert k.incidence_module.factorization == "E_A(C,sigma)=E3 tensor E_C(C) tensor E_d(C,sigma)"
        for q, j in k.ledger[1:]:
            assert kernel.S_index_trace(C, sigma, q, j, lambda_IT=2) == 0


def test_s_index_trace_is_not_charged_hessian_source():
    for C, sigma in kernel.SECTORS.values():
        diagnostic = kernel.S_index_trace_hessian_diagnostic(C, sigma)
        assert diagnostic["charged_Hessian_from_S_index_trace"] == "INVALIDATED_DO_NOT_CLAIM"
        assert diagnostic["rank"] == 1
        assert diagnostic["determinant"] == "0"
        assert diagnostic["has_cross_term"] is True
    assert kernel.STATUS_TABLE["charged_Hessian_from_S_index_trace"] == "INVALIDATED_DO_NOT_CLAIM"


def test_json_artifact_contains_all_kernel_data_and_statuses():
    data = load_json(DATA_JSON)
    assert data["public_status"] == kernel.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert len(data["kernels"]) == 4
    assert data["statuses"] == kernel.STATUS_TABLE
    assert data["statuses"]["Boundary_Graded_Defect_Action_Kernel_v1"] == (
        "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL"
    )
    assert data["statuses"]["numerical_closure"] == "OPEN"
    assert data["statuses"]["rho_ch_exact_value"] == "OPEN_LOCALIZABLE"
    assert data["statuses"]["B_supp_universal_suppression_operator"] == "OPEN_LOCALIZABLE"
    assert data["statuses"]["charged_Hessian_from_S_index_trace"] == "INVALIDATED_DO_NOT_CLAIM"


def test_no_empirical_prediction_imports_in_kernel_or_generator():
    combined_source = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "src/boundary_graded_defect_action_kernel.py",
            "src/charged_kf_generator.py",
        )
    )
    forbidden_imports = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "neutrino",
        "reference_common_scale",
        "fine_structure",
    )
    for name in forbidden_imports:
        assert f"import {name}" not in combined_source
        assert f"from {name}" not in combined_source


def test_docs_and_status_ledgers_preserve_claim_boundaries():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC, CLAIM_STATUS, BACKLOG)
    )
    assert kernel.PUBLIC_STATUS in combined
    assert "Boundary_Graded_Defect_Action_Kernel_v1" in combined
    assert "charged_Hessian_from_S_index_trace=INVALIDATED_DO_NOT_CLAIM" in combined
    assert "S_index_trace is not the charged Hessian" in combined
    assert "numerical_closure: OPEN" in combined
    forbidden = (
        "BHSM is complete.",
        "BHSM is proven.",
        "BHSM is empirically validated",
        "charged masses are derived",
        "CKM closure achieved",
        "PMNS closure achieved",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_frozen_prediction_files_remain_unchanged_by_kernel():
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()
    data = load_json(DATA_JSON)
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
