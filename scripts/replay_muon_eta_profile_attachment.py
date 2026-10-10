"""Replay daughter identities and one local curve; never historical production."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
import numpy as np


START = "1eb713fa12e26858c78913951b600643027714d5"
REFERENCE = "524ed90689bd5923c249bba2e699abf627e703cd"
CHECKPOINT = "BHSM_MUON_CURRENT_ETA_ATTACHMENT_COTANGENT_20261003"
PRODUCERS = {
    "src/bhsm/interface/completion/eta_static_texture_v13_1.py": ["log_profile_ode", "solve_profile"],
    "src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py": ["foundational_action_payload", "zero_mode_pullback_payload"],
    "src/bhsm/interface/completion/geometry_first_nonlocal_v14_51.py": ["berger_scale_stationarity_contract"],
    "src/bhsm/interface/aether_eta_wall_material_response_v15_26.py": ["normalized_eta_probability_response", "retained_eta_profile_response", "completed_sigma_action"],
    "src/bhsm/interface/aether_join_skin_nonlinear_constraint_v15_32.py": ["join_trace_domain_and_jet"],
    "src/bhsm/interface/bhsm_complete_child_mathematical_system_v15_39.py": ["child_configuration_space", "complete_child_functional", "variational_problem"],
    "src/bhsm/interface/aether_eta_sigma_response_constraint_v15_40.py": ["response_constraint_action"],
    "src/bhsm/interface/aether_post_cut_nonround_lorentzian_cap_v15_48.py": ["cap_fields"],
    "src/bhsm/interface/aether_post_cut_child_cap_reconstruction_v15_46.py": ["post_cut_variational_contract", "round_cap_constraint_fields"],
    "src/bhsm/interface/aether_m4_standard_model_zeta_backreaction_v15_51.py": ["solve_attached_constraint_projection"],
    "src/bhsm/interface/aether_full_sobolev_hybrid_actualization_v15_57.py": ["full_reconstruction_operator"],
    "src/bhsm/interface/aether_full_reset_action_jacobian.py": ["full_reset_residual"],
    "src/bhsm/interface/aether_c2_reset_generated_launch_chart.py": ["reset_generated_launch_decomposition"],
    "src/bhsm/interface/action_extension_global_spin_reset_ae2.py": ["action_definition"],
    "src/bhsm/interface/muon_parent_maxwell_velocity.py": ["current_parent_fields"],
    "src/bhsm/interface/aether_hybrid_yukawa_mass_semantics_v15_56.py": ["wall_normal_overlap_contract"],
    "src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py": ["unified_parent_boundary_functional"],
    "src/bhsm/interface/aether_einstein_cartan_joint_pushforward_v15_75.py": ["first_order_parent_action", "wall_projected_kernel"],
    "src/bhsm/interface/aether_cartan_shell_crossing_v15_76.py": ["shell_geometry"],
    "src/bhsm/interface/aether_sobolev_galerkin_pencil_lift_v15_81.py": ["generalized_lagrangian"],
    "src/bhsm/interface/aether_invariant_sobolev_schur_pushforward_v15_82.py": ["regular_einstein_cartan_kernel"],
    "src/bhsm/interface/aether_reset_hessian_matter_cones_v15_93.py": ["proper_fermion_cone"],
    "src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py": ["microscopic_owner_contract"],
}
PRESERVED = [
    "artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz",
    "artifacts/muon_wall_source_pairing_20261003/replay_reference/result.json",
    "artifacts/muon_wall_source_pairing_20261003/replay_reference/radial_slice_causal_certificate.json",
    "artifacts/muon_wall_source_pairing_20261003/exterior_KM_partial.json",
    "artifacts/muon_wall_source_pairing_20261003/native_ledger.json",
    "artifacts/muon_wall_source_pairing_20261003/frozen_local.json",
    "artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz",
    "artifacts/muon_parent_source_rate_20261003/replay_reference/cut_rate_record.json",
    "artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode())


def git(root, *args):
    archive = root / 'reproduction_revision.json'
    if archive.exists() and not (root/'.git').exists():
        record = json.loads(archive.read_text())
        if args == ('rev-parse', 'HEAD'):return record['published_source_commit']
        if args == ('branch', '--show-current'):return record['branch']
        if args == ('status', '--short'):return 'portable source archive; no Git working tree'
        raise ValueError('unsupported Git operation for portable source archive')
    return subprocess.check_output(
        ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false", *args],
        cwd=root, text=True,
    ).strip()


def extract(root):
    records = []
    for name, functions in PRODUCERS.items():
        path = root / name
        source = path.read_text(encoding="utf-8-sig")
        lines = source.splitlines()
        nodes = {n.name: n for n in ast.parse(source).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for function in functions:
            n = nodes[function]
            records.append(dict(path=name, sha256=sha(path), function=function,
                line=n.lineno, end_line=n.end_lineno,
                source="\n".join(lines[n.lineno-1:n.end_lineno]), execution="AST read only; not imported or executed"))
    return records


def run(root, output):
    if output.exists():
        raise FileExistsError("fresh dedicated output required")
    sys.path.insert(0, str(root / "src"))
    import sympy
    from bhsm.interface.muon_eta_profile_attachment import (
        attachment_equations, exact_profile_residuals, probability_pullback_residuals, daughter_collar_profile,
    )
    retained = extract(root)
    residuals = {**exact_profile_residuals(), **probability_pullback_residuals()}
    identities = {name: dict(exact_residual=str(value), passed=value == 0) for name, value in residuals.items()}
    if not all(record["passed"] for record in identities.values()):
        raise ArithmeticError(str(identities))
    with np.load(root/PRESERVED[-1]) as geometry:
        curve, curve_result = daughter_collar_profile(geometry)
        cache_time_range = [float(geometry['proper_times'][0]), float(geometry['proper_times'][-1])]
    output.mkdir(parents=True)
    np.savez_compressed(output/'daughter_collar_profile.npz', **curve)
    head = git(root, "rev-parse", "HEAD")
    branch = git(root, "branch", "--show-current")
    status = git(root, "status", "--short")
    archive_only = (root/'reproduction_revision.json').exists() and not (root/'.git').exists()
    diff = b'' if archive_only else subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=root)
    (output / "tracked_working_diff.patch").write_bytes(diff)
    save(output / "retained_equations.json", retained)
    save(output / "exact_identities.json", identities)
    equations = attachment_equations()
    missing = dict(
        classification="uncomputed same-domain geometric/pairing/transport pullback on source support; daughter eta field identity resolved",
        resolved_field_equation=equations["restriction"], action_equality=equations["normal_action"],
        inputs="current C2 join eta/metric, adopted M5/M4 inclusion and collar domain in the resolved common-A section",
        output="X/J/Spin x SM transport on source support and normalization integration domain, or the equivalent contracted W actions, with SAME-source first jet",
        defining_equations="X_ss+Gamma[X_s,X_s]=0; transverse Jacobi evolution with wall base data; nabla_Xs U54=0; J from owned pairing pullback, patched with actual interface equations where needed",
        sufficient_contraction=equations["overlap"], consumer=equations["overlap_consumer"],
        source_tangent=equations["same_source_jet"],
        concrete_predecessor="v15.76/v15.82 establish the adopted same-eta field identity; their slice ds=C dchi and J=(r/R_b)^3 are not reused as a full current collar",
        no_full_precursor_or_new_framework_required=True,
        inherited_data="past physical prefix at the artificial cut and canonical future stop retained; no new boundary law or profile required",
    )
    save(output / "missing_matching_equation.json", missing)
    execution = dict(exact_identity_checks=len(identities), historical_producer_executions=0,
        static_BVP_solves=0, old_replays=0, new_source_or_pairing_arrays=0,
        finite_collar_curve_integrations=1, daughter_normal_mass_evaluations=len(curve['s']),
        current_wall_overlap_evaluations=0, exterior_shifted_solves=0,
        native_heat_evaluations=0, physical_transfer_directions=0)
    result = dict(checkpoint_id=CHECKPOINT, classification="resolved outgoing eta field identity and evaluated finite nodal collar mass coefficient; full source-support wall projection not yet realized",
        start_HEAD=START, scientific_reference=REFERENCE, evaluated_code_base_HEAD=head, branch=branch,
        equations=equations, checks=identities, execution=execution,
        theorem_scope="fixed compatible chart/pairing/transport; smooth compactly supported profile variations; no alternate full BHSM saddles asserted",
        invariance_criterion="delta T vanishes on every allowed k iff J u^* phi-|v|^2 T vanishes as a distribution on that tangent support",
        bound="abs(delta T)<=norm((I-|u><u|)phi)_J sqrt(Var_|v|^2(k)); symbolic derivative bound only",
        action_scope="adopted v14.45 common-A Dirac sector within one AE4 owner, no second determinant or new normalization",
        current_profile_selected=True, current_m_eta="daughter_collar_profile.npz: m_eta_current on saved local curve",
        finite_collar=curve_result, cached_metric_time_range=cache_time_range,
        saved_source_support_rho_cell_envelope=[float(24*np.pi/128),float(40*np.pi/128)],
        full_source_support_curve_computed=False, actual_overlap_T=None, B54_required=None,
        error_scope="exact algebra plus binary64 ODE in cached bilinear nodal metric; tolerances/norm residual do not certify absolute ODE or continuum error; normalization/chart/transport/domain/tail/soft errors unevaluated",
        physical_a_mu=None, physical_g_mu=None)
    save(output / "result.json", result)
    ledger = json.loads((root / PRESERVED[4]).read_text())
    ledger["domain_boundary"]["current_eta_attachment_result"] = "same outgoing eta field resolved at adopted effective-action scope; finite local m_eta_current curve evaluated"
    ledger["domain_boundary"]["finite_local_m_eta"] = "daughter_collar_profile.npz; full source support, J, normalization, transport still unevaluated"
    ledger["domain_boundary"]["profile_overlap_cotangent"] = equations["overlap_kernel"]
    save(output / "native_ledger.json", ledger)
    # Byte-copy the frozen convention; do not reinterpret its uncertainty.
    (output / "frozen_local.json").write_bytes((root / PRESERVED[5]).read_bytes())
    save(output / "preserved_operands.json", [dict(path=name, sha256=sha(root/name), replayed=False) for name in PRESERVED])
    sources = [*PRODUCERS,
        "src/bhsm/interface/muon_eta_profile_attachment.py", "tests/test_muon_eta_profile_attachment.py",
        "scripts/replay_muon_eta_profile_attachment.py", "theory/muon_current_eta_profile_attachment_20261003.md"]
    hashes = [dict(path=name, sha256=sha(root/name), role="source" if name in sources else "preserved input") for name in [*sources, *PRESERVED]]
    save(output / "input_hashes.json", hashes)
    save(output / "workspace.json", dict(path=str(root), HEAD=head, branch=branch,
        status=status, source_identity='archived published revision and source hashes' if archive_only else 'actual Git HEAD and working tree',
        start_commit_ancestor=None if archive_only else subprocess.run(["git", "merge-base", "--is-ancestor", START, "HEAD"], cwd=root).returncode == 0,
        tracked_diff="tracked_working_diff.patch", untracked_files_recorded_in_status=True,
        intentional_scientific_source_changes="new daughter collar-profile module and replay; historical producer identity recovered; no historical producer modified",
        primary_workspace_modified=False))
    save(output / "runtime.json", dict(python=sys.version, platform=platform.platform(), sympy=sympy.__version__))
    save(output / "checkpoint.json", dict(checkpoint_id=CHECKPOINT, code_base_HEAD=head, branch=branch,
        start_HEAD=START, scientific_reference=REFERENCE, action="BHSM-AE-4.0.0 with adopted v14.45 effective Dirac/common-A action",
        history="C2 step1222 artificial past cut with inherited physical prefix; canonical future stop; true material wall rho=pi/2",
        domain="inherited reset graph; compatible collar assumed only for functional theorem, not numerically materialized",
        state="canonical source trial inputs preserved; no physical state selected",
        source_coordinate="b, beta=T_b b, A_Q=sqrt(2) beta; no action-index vertex factor",
        result="result.json", missing_operand="missing_matching_equation.json", ledger="native_ledger.json",
        exact_checks=len(identities), physical_a_mu=None, physical_g_mu=None,
        reproduction="python scripts/replay_muon_eta_profile_attachment.py --output <fresh-directory>",
        targeted_tests="python -m pytest -q tests/test_muon_eta_profile_attachment.py",
        next="Continue same-domain collar X/J/transport onto saved source support using inherited prefix/patches, then contract fixed outgoing eta mode to T/B54 and consume coupled exterior K/M solve"))
    (output / "report.md").write_bytes((root / "theory/muon_current_eta_profile_attachment_20261003.md").read_bytes())
    save(output / "receipt.json", dict(files=[dict(path=p.name, sha256=sha(p)) for p in sorted(output.iterdir()) if p.is_file()]))
    print(json.dumps(dict(output=str(output), exact_checks=len(identities), passed=True,
        current_profile_selected=True, finite_collar=curve_result, execution=execution)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.repository.resolve(), args.output.resolve())
