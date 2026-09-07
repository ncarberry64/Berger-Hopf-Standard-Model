from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface.encapsulation_response_representation_theorem import (
    EXACT_NEXT_OBJECT,
    RSP_CLASS,
    canonical_pullback_residual,
    canonical_structure_ledger,
    coefficient_length_exponent,
    coupling_allowed,
    event_channel_decomposition,
    equivariance_residual,
    first_order_response_theorem,
    input_space_contract,
    intertwiner_space_ledger,
    mode_coupling_graph,
    n12_rank_forecast,
    nonlinear_response_theorem,
    output_space_contract,
    recovered_finite_subspaces,
    representation_theorem_payload,
    response_freedom_classification,
    scale_and_control_ledger,
)
from scripts.materialize_encapsulation_response_representation_theorem import (
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_encapsulation_response_representation_theorem.py"
TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_ENCAPSULATION_RESPONSE_REPRESENTATION_THEOREM.json"
)


def test_input_and_output_spaces_fail_closed_at_full_field_level() -> None:
    inputs = input_space_contract()
    outputs = output_space_contract()
    assert inputs["global_event_irreducible_decomposition_owned"] is False
    assert inputs["N12_owned_event_subspace"]["dimension"] == 1
    assert "NOT_A_CHILD_BOUNDARY_HARMONIC" in inputs["N12_owned_event_subspace"]["meaning"]
    assert outputs["finite_dimension"] is None
    assert outputs["dimension_class"].startswith("INFINITE_DIMENSIONAL")
    assert "ACTION_UNITS" in outputs["pairing"]


def test_sector_decomposition_is_not_mislabeled_as_irreducible() -> None:
    channels = event_channel_decomposition()
    assert {row.key for row in channels} == {
        "geometry",
        "scalar_topographic",
        "gauge",
        "fermion",
        "ghost_antighost",
        "higher_spin",
    }
    assert all("INFINITE_SECTION_SPACE" in row.dimension for row in channels)
    assert input_space_contract()["global_event_irreducible_decomposition_owned"] is False
    hs = next(row for row in channels if row.key == "higher_spin")
    assert "ZERO_IMAGE" in hs.canonical_partner


def test_exact_recovered_commutant_dimensions_are_preserved() -> None:
    result = recovered_finite_subspaces()
    assert result["round_shape_H2_full_Spin4"]["real_dimension"] == 9
    assert result["round_shape_H2_full_Spin4"]["commutant_real_dimension"] == 1
    assert result["round_shape_H2_diagonal_SU2"]["dimensions"] == [1, 3, 5]
    assert result["round_shape_H2_diagonal_SU2"]["commutant_real_dimension"] == 3
    assert result["Clifford_spin_factor"]["full_irreducible_commutant_complex_dimension"] == 1
    assert result["Clifford_spin_factor"]["normal_symbol_only_commutant_complex_dimension"] == 8
    assert result["N12_event_stop_line"]["child_boundary_identification"] is False


def test_intertwiner_theorem_and_forbidden_blocks() -> None:
    ledger = intertwiner_space_ledger()
    theorem = first_order_response_theorem()
    graph = mode_coupling_graph()
    assert ledger["actual_group_instantiated"] is False
    assert "Hom_G" in ledger["isotypic_theorem"]
    assert theorem["does_not_supply_values"] is True
    assert any(row.status == "REQUIRED_ZERO" for row in graph)
    assert coupling_allowed("scalar", "scalar", same_irrep=True)
    assert not coupling_allowed(
        "boson", "fermion", same_irrep=False, grading_compatible=False
    )
    assert coupling_allowed(
        "mode_r", "mode_s", same_irrep=False, owned_coupling_mechanism=True
    )


def test_finite_equivariance_witness() -> None:
    theta = 0.41
    rotation = np.asarray(
        ((np.cos(theta), -np.sin(theta)), (np.sin(theta), np.cos(theta)))
    )
    assert equivariance_residual(np.eye(2), rotation, rotation) < 1.0e-13
    assert equivariance_residual(np.diag((1.0, 2.0)), rotation, rotation) > 1.0e-3
    with pytest.raises(ValueError):
        equivariance_residual(np.eye(2), np.ones((2, 3)), np.eye(2))


def test_nonlinear_jets_are_classified_but_not_selected() -> None:
    result = nonlinear_response_theorem()
    assert "Sym_gr" in result["kth_jet"]
    assert "10_4_4" in result["cubic"]
    assert result["full_nonlinear_map_determined"] is False
    assert result["high_order_campaign_launched"] is False


def test_scale_dimensions_and_minimal_controls() -> None:
    result = scale_and_control_ledger()
    assert result["rho_E/ST"]["recovered_unique_definition"] is False
    assert result["rho_E/ST"]["dimension"] is None
    assert result["Lambda_s"]["ell_kappa_units"] == "L"
    assert coefficient_length_exponent(3.0, -2.0) == 5.0
    with pytest.raises(ValueError):
        coefficient_length_exponent(np.inf, 1.0)
    assert result["no_function_selected"] is True


def test_canonical_pullback_isotropy_links_response_derivatives() -> None:
    jq = np.eye(2)
    symmetric_jp = np.diag((2.0, 3.0))
    nonsymmetric_jp = np.asarray(((0.0, 1.0), (0.0, 0.0)))
    assert canonical_pullback_residual(jq, symmetric_jp) < 1.0e-13
    assert canonical_pullback_residual(jq, nonsymmetric_jp) > 0.1
    with pytest.raises(ValueError):
        canonical_pullback_residual(np.eye(2), np.eye(3))
    ledger = canonical_structure_ledger()
    assert ledger["complete_global_reduced_symplectic_form_owned"] is False
    assert any("b_r=a_r" in item for item in ledger["does_not_force"])


def test_rsp5_and_n12_forecast_do_not_claim_rank() -> None:
    freedom = response_freedom_classification()
    rank = n12_rank_forecast()
    payload = representation_theorem_payload()
    assert RSP_CLASS == "RSP5"
    assert freedom["class"] == "RSP5"
    assert freedom["physical_irreducible_channel_count"] is None
    assert freedom["operator_valued_freedom"] == "INFINITE_DIMENSIONAL"
    assert rank["current_certified_rank"] == 31
    assert rank["current_residual"] == 67
    assert rank["time_quotient_residual"] == 66
    assert rank["maximum_potential_additional_rank"] == 67
    assert rank["actual_additional_rank_this_sprint"] == 0
    assert payload["ONE_OWNER_QUESTION"] is None
    assert payload["EXACT_NEXT_OBJECT"] == EXACT_NEXT_OBJECT
    assert not any(payload["claim_boundary"].values())


def test_deterministic_materialization() -> None:
    assert build_payload()["validation_passed"] is True
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert stored["validation_passed"] is True
    assert stored["response_freedom"]["class"] == "RSP5"
