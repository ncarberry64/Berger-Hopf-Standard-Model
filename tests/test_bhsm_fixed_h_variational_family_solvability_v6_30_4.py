from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import fixed_h_variational_family_solvability as solve


def test_starting_main_and_parent_scientific_shas_are_pinned():
    assert solve.SOURCE_MAIN_SHA == (
        "24b6be33871911dcd7932503ed56553867462ff8"
    )
    assert solve.PARENT_SCIENTIFIC_SHAS["v6.30.2"].startswith("0d72d9a")
    assert solve.PARENT_SCIENTIFIC_SHAS["v6.30.3"].startswith("394c59b")


def test_clean_reproduction_of_pure_scalar_Phi1_and_F1_zero():
    assert solve.v6303.fixed_action_phi1() == ("0", "0", "u1", "0")
    assert solve.v6303.fixed_action_frame_F1() == 0


def test_D0_D1_D2_D3_are_explicitly_separated():
    rows = {row["domain"]: row for row in solve.domain_rows()}
    assert set(rows) == {"D0", "D1", "D2", "D3"}
    assert rows["D0"]["selected"] is True
    assert all(rows[key]["selected"] is False for key in ("D1", "D2", "D3"))
    assert rows["D0"]["r2_allowed"] is False
    assert rows["D2"]["r1"] == "tau chi_1"
    assert "no existing" in rows["D3"]["action_provenance"]


def test_D0_fixes_curvature_at_every_order_not_only_r1():
    row = solve.domain_rows()[0]
    assert "r(q)=r0 at every order" in row["fixed_data"]
    assert row["r1"] == 0


def test_tau_is_not_sign_q_and_reflection_keeps_tau_fixed():
    payload = solve.artifact_payloads()["parity"]
    assert payload["reflection"] == "(q,tau)->(-q,tau)"
    assert payload["tau_not_sign_q"] is True


def test_reflection_parity_assigns_all_components():
    rows = {row["component"]: row for row in solve.parity_rows()}
    assert "odd" in rows["delta_sigma"]["D0"]
    assert "even" in rows["A,psi"]["D0"]
    assert "even" in rows["eta_tr"]["D0"]
    assert rows["r"]["D0"] == "constant r0"
    assert rows["F,V_J"]["D0"] == "even"
    assert "fixed" in rows["tau"]["D0"]


def test_exact_complete_second_order_source_generation():
    ledger = solve.second_order_source_ledger()
    assert ledger["S2"]["scalar"] == "0"
    assert "u1'^2+mu_c u1^2" in ledger["S2"]["lapse_constraint"]
    assert "-u1'^2+mu_c u1^2" in ledger["S2"]["tangential_metric"]
    assert ledger["S2"]["matcher_trace"] == "0"


def test_hamiltonian_response_solves_constraint_exactly():
    assert solve.hamiltonian_order_two_residual() == 0


def test_tangential_equation_follows_exactly_from_Jacobi_equation():
    assert solve.tangential_order_two_residual() == 0


def test_scalar_second_order_source_is_zero_by_reflection():
    assert solve.scalar_source_order_two() == 0


def test_KKT_pairing_uses_weight_and_extended_endpoint_pairing():
    ledger = solve.projection_ledger()
    assert "4 sin(rho)^4" in ledger["KKT_pairing"]
    assert "extended endpoint saddle pairing" in ledger["KKT_pairing"]
    assert ledger["boundary_contribution"] == 0


def test_adjoint_projection_is_exactly_zero_and_source_is_in_range():
    assert solve.fredholm_projection_exact() == 0
    ledger = solve.projection_ledger()
    assert ledger["Omega2_exact"] == 0
    assert ledger["range_condition_holds"] is True
    assert ledger["result"] == solve.PRIMARY_RESULT


def test_control_provenance_has_no_selected_or_free_coefficient():
    rows = solve.control_projection_rows()
    assert all(row["D_a_at_order_two"] == 0 for row in rows)
    assert all(row["coefficient_selected"] is None for row in rows)
    permission = solve.permission_ledger()
    assert permission["control_unfolding_required"] is False
    assert permission["free_control_coefficient"] is False


def test_no_historical_F1_tau_is_used_in_D0_or_D1():
    payload = json.dumps(solve.artifact_payloads())
    assert '"historical_F1_tau_imported": false' in payload
    assert "D2 F1_tau" in payload


def test_noether_identity_and_order_two_compatibility_are_exact():
    ledger = solve.noether_order_two_ledger()
    assert ledger["off_shell_symbolic_residual"] == "0"
    assert ledger["order_two_hamiltonian_residual"] == "0"
    assert ledger["order_two_tangential_residual_after_Jacobi_equation"] == "0"
    assert ledger["differential_compatibility"] is True


def test_matcher_recurrence_gives_zero_trace_and_generated_reaction():
    assert solve.matcher_trace_order_two() == 0
    trial = sp.symbols("A2")
    assert solve.matcher_reaction_order_two(trial) == (
        -24 * solve.KAPPA_1 * trial
    )


def test_Phi2_is_regular_complement_solution():
    ledger = solve.second_order_source_ledger()["Phi2"]
    assert "tan(rho)**2" in ledger["A2"]
    assert ledger["psi2"].startswith("0")
    assert ledger["sigma2"].startswith("0")
    assert "2 Z5 u1'" in ledger["eta2"]


def test_two_method_precision_and_profile_agreement():
    diagnostics = solve.second_order_numerical_diagnostics()
    assert len(diagnostics["methods"]) == 2
    assert diagnostics["hypergeometric"]["dps"] == 60
    assert diagnostics["agreement"]["mu_difference"] < 1.0e-12
    assert diagnostics["agreement"]["A2_endpoint_difference"] < 1.0e-11
    assert (
        diagnostics["agreement"]["A2_profile_max_difference_33_nodes"]
        < 2.0e-12
    )
    assert diagnostics["complement_gap"] > 64


def test_endpoint_reaction_numerics_agree():
    diagnostics = solve.second_order_numerical_diagnostics()
    assert diagnostics["agreement"]["eta2_endpoint_difference"] < 2.0e-10
    assert diagnostics["hypergeometric"]["eta2_endpoint"] > 166


def test_permission_is_only_for_v6305_not_scale():
    ledger = solve.permission_ledger()
    assert ledger["v6_30_5_permitted"] is True
    assert ledger["v6_30_5_permission"] == solve.PERMISSION_RESULT
    assert ledger["v6_31_permitted"] is False
    assert ledger["v6_31_permission"] == solve.SCALE_RESULT


def test_no_Robin_pseudoinverse_measurement_scale_or_frozen_change():
    for key, value in solve.GUARDS.items():
        assert value is False, key


def test_artifact_count_and_names():
    assert len(solve.ARTIFACT_FILES) == 7
    assert set(solve.artifact_payloads()) == set(solve.ARTIFACT_FILES)


def test_deterministic_artifact_bytes():
    first = solve.artifact_bytes()
    second = solve.artifact_bytes()
    assert first == second
    assert {
        name: hashlib.sha256(content).hexdigest()
        for name, content in first.items()
    } == {
        name: hashlib.sha256(content).hexdigest()
        for name, content in second.items()
    }


def test_checked_in_artifacts_are_current():
    for name, content in solve.artifact_bytes().items():
        assert (ROOT / "artifacts" / name).read_bytes() == content


def test_materializer_is_idempotent():
    script = (
        ROOT
        / "scripts"
        / "materialize_fixed_h_variational_family_solvability_v6_30_4.py"
    )
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in solve.ARTIFACT_FILES.values()
    }
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in solve.ARTIFACT_FILES.values()
    }
    assert first == second == solve.artifact_bytes()
