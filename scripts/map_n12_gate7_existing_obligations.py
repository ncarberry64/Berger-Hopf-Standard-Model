"""Read-only crosswalk of current calculations to existing Gate-7 obligations.

This is bookkeeping, not a completion gate or a scientific producer. It never
changes authoritative criteria, numerical packets, status or tolerances.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'artifacts/flagship_integration'

# Short labels are cross-references, not new numbered gates.
OBLIGATIONS = {
    'operator': ('Existing joint operator and variational-domain realization', [
        ('docs/BHSM_1_0_DEFINITION_OF_DONE.md', '## Authoritative current completion state'),
        ('theory/n12_joint_finite_history_operator_data_gate.md', 'or directly derive')]),
    'force': ('Existing projected same-action force', [
        ('theory/n12_finite_endpoint_zero_source_force_functional.md', 'D Gamma_heat(P)[delta P]'),
        ('theory/n12_c2_projected_adjoint_cauchy_criterion.md', 'This is the exact weakest convergence requirement')]),
    'root': ('Existing nonlinear same-action KKT root', [
        ('theory/n12_finite_endpoint_forward_adjoint_kkt.md', 'There are two equivalent implementations'),
        ('theory/n12_forward_adjoint_kkt_existence_gate.md', 'Gate 7 can advance by any one of three')]),
    'geometry_hessian': ('Existing constrained geometry Hessian and stationary first response', [
        ('src/bhsm/interface/formation_stationarity_kkt.py', 'def assemble_stationarity'),
        ('src/bhsm/interface/formation_stationarity_kkt.py', 'def reset_tangent_blocks')]),
    'source_hessian': ('Existing physical pair-plus-contact source Hessian', [
        ('theory/n12_finite_endpoint_forward_adjoint_kkt.md', 'is still distinct from the later pair-plus-contact source Hessian'),
        ('src/bhsm/interface/heat_zeta_mixed_boundary_launch.py', 'def element_mixed')]),
    'interface': ('Existing fixed-environment interface and physical tangent', [
        ('theory/n12_gate7_comoving_slaved_interface.md', 'For complete equations F(x,b,p;e0)=0'),
        ('src/bhsm/interface/geometric_material_port.py', 'def required_material_jet')]),
    'persistence': ('Existing nonlinear physical-history and persistence bounds', [
        ('docs/GATE7_CURRENT_REPRODUCTION.md', 'Layer B still requires uniform'),
        ('theory/n12_gate7_uniform_remainder_formulation.md', 'The formula refers to the exact frozen operators'),
        ('artifacts/mission_state/BHSM_GATE7_CRITICAL_PATH_RECONCILIATION_20260923.json', '"active_ledger"')]),
    'downstream': ('Existing continuum and declared physical readouts', [
        ('docs/BHSM_1_0_DEFINITION_OF_DONE.md', '## Current N12 continuum evaluation'),
        ('docs/BHSM_1_0_DEFINITION_OF_DONE.md', '## Internal finish line')]),
    'reproduction': ('Existing reproducibility of headline results', [
        ('docs/BHSM_1_0_DEFINITION_OF_DONE.md', '## Release-relevance firewall'),
        ('AGENTS.md', 'Deterministic artifacts must be materialized twice')]),
}

# Each dated package is accounted for, including failed/superseded diagnostic
# routes. Their existence does not authorize a rerun or imply active blockers.
PACKAGES = {
    'current_incoming_response_20260928': ('operator force geometry_hessian interface', 'reuse_local_subsystem', 'Local internal/clock first contractions; not a mandatory 124-variable completion item'),
    'formation_op_current_20260928': ('force geometry_hessian', 'reuse_frozen', 'Local ten-sector accounting and endpoint simplifications; not integrated action derivatives'),
    'gate7_66d_checkpoint_20260926': ('interface persistence', 'reuse_scoped', 'Coordinate/frame and Newton-center binding; retain reprojection allowances'),
    'gate7_8reaction_center_20260926': ('root interface', 'diagnostic_only', 'Failed point/border diagnosis; no independent eight-reaction gate'),
    'gate7_appended_fiber_center_20260926': ('root interface', 'diagnostic_only', 'Augmented-center attempt; current coupled equations supersede a chart-only solve'),
    'gate7_comoving_interface_20260927': ('interface persistence', 'reuse_scoped', 'Canonical outputs and conditional feedback; triangular output graph is not full slaving'),
    'gate7_coupled_fiber_center_20260927': ('root interface persistence', 'reuse_scoped', 'Local coupled center, neighborhood and jets; not complete incoming/joint stationarity'),
    'gate7_current_formation_stationarity_20260927': ('root geometry_hessian interface', 'reuse_frozen', 'Current reset residuals and stationarity assembly; no separate exact-event pre-gate'),
    'gate7_current_history_20260927': ('operator force geometry_hessian', 'reuse_prefix', 'Current finite C2 proof core and pullbacks; prefix cannot define a physical endpoint'),
    'gate7_current_reset_connection_20260927': ('operator root interface', 'reuse_candidate', 'Existing current connection and reset guess; its residual is part of the coupled problem'),
    'gate7_current_spectral_20260927': ('operator force geometry_hessian', 'reuse_scoped', 'Current downstream coefficient first maps; do not relabel them incoming launch jets'),
    'gate7_descriptor_fiber_owner_20260926': ('root persistence', 'diagnostic_only', 'Descriptor ownership/defect diagnosis; consistency is an existing equation'),
    'gate7_environment_ownership_20260927': ('operator force interface', 'reuse_accounting', 'Internal/external source accounting; current one-seam supersession controls old terminology'),
    'gate7_environment_seam_20260927': ('operator force interface', 'reuse_accounting', 'Existing seam composition; no new environment constitutive law'),
    'gate7_event_conormal_20260927': ('interface persistence', 'reuse_scoped', 'Local canonical conormal and dynamic-flux response'),
    'gate7_fiber_covector_20260927': ('root interface persistence', 'reuse_scoped', 'Local fiber derivative; no new physical input'),
    'gate7_fiber_domain_exclusion_20260927': ('root persistence', 'diagnostic_only', 'Old-domain exclusion diagnosis; do not demand repair of every historical box'),
    'gate7_formation_action_basis_20260928': ('force geometry_hessian root', 'reuse_frozen', 'Q66 is the complete current pointwise reset tangent, not a nonlinear history parameterization'),
    'gate7_full_shooting_owner_20260926': ('root persistence', 'reuse_scoped', 'Existing shooting equation ownership and allowance replay'),
    'gate7_geometric_material_port_20260927': ('interface geometry_hessian persistence', 'reuse_frozen', 'Canonical three geometric plus four material split and flux operator'),
    'gate7_history_jet_prerequisites_20260927': ('interface persistence', 'reuse_accounting', 'Checks inputs for a history-response implementation, not extra completion gates'),
    'gate7_joint_port_20260927': ('force interface geometry_hessian', 'reuse_scoped', 'Joint implicit adjoint identity; local zero correction is not global cancellation'),
    'gate7_launch_response_20260927': ('geometry_hessian interface persistence', 'reuse_frozen', 'Current downstream 73-chart and native response; total incoming mixed contractions still need correct incidence'),
    'gate7_local_child_flow_dimension_20260926': ('root interface', 'diagnostic_only', 'Nonsquare local subsystem diagnosis; does not add physical degrees of freedom'),
    'gate7_local_null_classification_20260926': ('root interface', 'diagnostic_only', 'Unresolved local kernel ownership; no arbitrary gauge/pseudoinverse selector'),
    'gate7_material_seeds_20260927': ('interface source_hessian', 'reuse_with_supersession', 'Four canonical action directions retained; demand for seven action seeds superseded by 3+4 split'),
    'gate7_mixed_boundary_launch_20260927': ('geometry_hessian source_hessian interface', 'reuse_with_supersession', 'Pair, genuine mixed and adjoint identities; no padded seven-action-seed campaign'),
    'gate7_nonlinear_lift_gap_20260926': ('root interface persistence', 'reuse_accounting', 'Need correct nonlinear/implicit response, not a separately stored full-history lift'),
    'gate7_parent_sectors_20260927': ('force geometry_hessian interface', 'historical_base_algorithms_only', 'Retain sector laws; current endpoint values are already frozen in formation_op_current'),
    'gate7_reduced_fiber_tangents_20260926': ('interface persistence', 'reuse_scoped', 'Tangent comparison diagnosis; action-derived tangent remains authority'),
    'gate7_seven_outputs_20260927': ('interface persistence', 'reuse_accounting', 'Complete output-jet target; latest 3+4 split controls implementation'),
    'gate7_two_sided_null_owner_20260926': ('root force interface', 'diagnostic_only', 'Two-sided residual ownership; unresolved scalar is not an extra completion gate'),
}

INHERITED = [
    ('Branch atlas / Layers A and B', 'persistence', 'docs/GATE7_CURRENT_REPRODUCTION.md'),
    ('Physical rate, HS incidence, signed causal remainder / Layer C', 'persistence', 'theory/n12_gate7_uniform_remainder_formulation.md'),
    ('Same-map self-map and contraction / Layer D', 'persistence', 'artifacts/flagship_integration/gate7_global_checkpoint_20260923/current_history_budget.json'),
    ('Existing finite event/canonical-stop route; not universal reachability', 'operator root', 'theory/n12_finite_endpoint_forward_adjoint_kkt.md'),
    ('Projected tail, only if the chosen route requires it', 'force geometry_hessian', 'theory/n12_c2_projected_adjoint_cauchy_criterion.md'),
    ('Existing source-Hessian readouts', 'source_hessian', 'src/bhsm/interface/heat_zeta_mixed_boundary_launch.py'),
    ('Existing continuum and declared observable obligations', 'downstream', 'docs/BHSM_1_0_DEFINITION_OF_DONE.md'),
    ('Retention/reproduction; not a formation equation', 'reproduction', 'AGENTS.md'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def reference(relative, needle):
    path = ROOT/relative
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    number = next(i+1 for i, line in enumerate(lines) if needle in line)
    return dict(path=relative, line=number, exact_line=lines[number-1], SHA256=digest(path))


def producer_names(value):
    """Read source-listed producer paths without executing any producer."""
    found = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and key.replace('\\', '/').startswith('scripts/') and key.endswith('.py'):
                found.add(key.replace('\\', '/'))
            found.update(producer_names(item))
    elif isinstance(value, list):
        for item in value:
            found.update(producer_names(item))
    return found


def calculate(out):
    if out.exists():
        raise ValueError('new crosswalk output directory required')
    # Inventory the active dated packages independently of the mapping table.
    discovered = {p.name for p in BASE.iterdir() if p.is_dir()
        and p.name.startswith(('gate7_', 'formation_op_', 'current_incoming_'))
        and any(day in p.name for day in ('20260926', '20260927', '20260928'))}
    if discovered != set(PACKAGES):
        raise ValueError('calculation inventory needs scope review; this is not a completion gate: '
                         +repr(sorted(discovered.symmetric_difference(PACKAGES))))
    obligations = {key: dict(existing_name=name, references=[reference(*r) for r in refs])
                   for key, (name, refs) in OBLIGATIONS.items()}
    packages = []
    for package, (labels, disposition, reason) in sorted(PACKAGES.items()):
        refs = labels.split()
        assert set(refs) <= set(OBLIGATIONS)
        prefix = 'artifacts/flagship_integration/'+package
        files = subprocess.run(['git', 'ls-files', '--', prefix], cwd=ROOT,
                               capture_output=True, text=True, check=True).stdout.splitlines()
        reports = []
        for relative in sorted(f for f in files if f.endswith('/report.json')):
            path = ROOT/relative
            report = json.loads(path.read_bytes())
            reports.append(dict(path=relative, SHA256=digest(path),
                saved_status=report.get('status'), existing_obligations=refs,
                source_listed_producers=sorted(producer_names(report))))
        if not reports:
            raise ValueError('no tracked reports found for '+package)
        packages.append(dict(package=prefix, existing_obligations=refs,
                             disposition=disposition, necessity_or_scope=reason, reports=reports))
    inherited = [dict(calculation=name, existing_obligations=labels.split(),
                      owner=path, owner_SHA256=digest(ROOT/path)) for name, labels, path in INHERITED]
    authorities = ['AGENTS.md', 'docs/BHSM_1_0_DEFINITION_OF_DONE.md', 'theory/gate_ledger.md',
        'artifacts/mission_state/BHSM_GATE7_CRITICAL_PATH_RECONCILIATION_20260923.json']
    result = dict(
        record_type='CALCULATION_TO_EXISTING_OBLIGATION_CROSSWALK_NOT_A_COMPLETION_GATE',
        checkpoint_reviewed='8dc85376', new_completion_gates=[],
        authoritative_criteria_modified=False, completion_status_changed=False,
        scientific_producers_run=[], globally_minimal_dimension_claimed=False,
        independent_history_input_count=None,
        scope='All tracked reports in the 32 active dated 26-28 September continuation packages, plus inherited completion-facing workstreams; no demand to rerun historical experiments',
        package_count=len(packages), tracked_report_count=sum(len(p['reports']) for p in packages),
        obligations=obligations, calculations=packages, inherited_workstreams=inherited,
        completion_facing_representation=dict(
            force_root=['q66 evaluator', 'H66 actions', 'B66x73 actions', 'existing constraint/domain residuals and certified evaluation/root error bounds'],
            interface=['existing three geometric traces', 'existing four material values and required first/mixed contractions', 'owned slaving response'],
            persistence=['existing physical admissibility and neighborhood self-map/contraction bounds'],
            source_hessian='Retain only the existing declared source-Hessian blocks; H66 is not their substitute',
            absolute_action_value='Only where an existing residual or chosen proof consumes it',
            realization='Signed reduced action/response contractions; equivalent operator, adjoint, Schur, or coupled KKT implementation',
            exact_full_history_required=False, stored_full_internal_73_column_history_required=False,
            generic_ambient_second_jet_required=False,
            full_internal_solution_eliminated_without_proof=False),
        necessity_policy='Before pursuing a new dependency, name its existing obligation and non-eliminated term; show why an existing contraction, identity or bound is insufficient. An uncomputed operand alone does not establish necessity.',
        superseded_implementation_prerequisites=[
            'Exact stored incoming trajectory before force evaluation',
            'Separately selected complete duration family before the equivalent coupled KKT solve',
            'Complete stored incoming 73-column history Jacobian',
            'Generic ambient second jets or full internal spectral decomposition',
            'Separate zero-force tests for internal sectors',
            'Standalone exact-event pre-gate at the saved binary candidate',
        ],
        preserved_information=[
            'All retained signed action, moving-duration/reset, internal, pair/contact and dynamic-flux contributions',
            'Interior graded spectral contribution when using a boundary Schur representation, unless its irrelevance is proved',
            'Action-owned domain, branch, external-source convention and reference normalization',
            'Existing numerical errors, proof budgets, physical directions and completion obligations',
        ],
        current_checkpoint_interpretation=dict(
            local_124_response='Reusable local derivative evidence, not an additional completion deliverable',
            formal_clock_witness='Refutes an endpoint-only kinematic shortcut; does not prove a nonzero total action term',
            descriptor_defect='Existing coupled event-constraint residual; not a new gate',
            q66_H66_B66x73_numerically_completed=False),
        authority_SHA256={p: digest(ROOT/p) for p in authorities},
        source_SHA256={p.relative_to(ROOT).as_posix(): digest(p) for p in (
            Path(__file__), ROOT/'docs/GATE7_CURRENT_CALCULATION_SCOPE.md',
            ROOT/'theory/n12_gate7_external_birth_source_role_supersession.md',
            ROOT/'src/bhsm/interface/heat_zeta_mixed_boundary_launch.py',
            ROOT/'src/bhsm/interface/joint_boundary_port_reduction.py',
        )})
    out.mkdir(parents=True)
    (out/'report.json').write_bytes((json.dumps(result, sort_keys=True, indent=2)+'\n').encode())
    print(json.dumps(dict(package_count=result['package_count'], tracked_report_count=result['tracked_report_count'],
                          new_completion_gates=[], report_SHA256=digest(out/'report.json'))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    calculate(parser.parse_args().out.resolve())
