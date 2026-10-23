"""Archive evaluated finite operands and the user's resolved preparation."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import shutil

REPO = Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
WORK = Path(r'C:/Users/carbe/OneDrive/Documents/CODEX')
OUT = REPO/'artifacts/muon_formed_weak_field_20261015'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def encoded(data):
    return (json.dumps(data, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != source.read_bytes():
        raise RuntimeError('Preserve existing different bytes: '+str(target))
    shutil.copyfile(source, target)
    assert digest(source) == digest(target)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--probe-base', required=True, type=Path)
    p.add_argument('--probe-producer', required=True, type=Path)
    p.add_argument('--probe-runs', nargs=2, default=['run_2','run_3'])
    args = p.parse_args()
    sources = [('point_spin', WORK/'outputs/bhsm_finite_pole_point_spin_diagnostic_20261015', ['run_1','run_2']),
               ('same_epoch_probe', args.probe_base, args.probe_runs)]
    repeated = []
    for name, base, runs in sources:
        left, right = [base/run for run in runs]
        names = sorted(x.name for x in left.iterdir() if x.is_file())
        assert names == sorted(x.name for x in right.iterdir() if x.is_file())
        for file in names:
            assert (left/file).read_bytes() == (right/file).read_bytes()
            for run in runs:
                copy(base/run/file, OUT/name/run/file)
        repeated.append(dict(component=name, independent_evaluations=runs,
                             byte_identical_files={f:digest(left/f) for f in names}))
    producers = [WORK/'bhsm_muon_finite_pole_point_spin_diagnostic_20261015.py', args.probe_producer]
    for producer in producers:
        copy(producer, REPO/'audits'/producer.name)
    failed = args.probe_base/'run_1'
    if (failed/'failed_attempt.json').is_file():
        for source in sorted(failed.iterdir()):
            if source.is_file():
                copy(source, OUT/'same_epoch_probe'/'run_1'/source.name)
    copy(Path(__file__), OUT/'binding_script.py')
    pins = {}
    for component, base, runs in sources:
        result = json.loads((base/runs[0]/'result.json').read_text(encoding='utf8'))
        for name, expected in result.get('input_hashes', {}).items():
            source = Path(name)
            if not source.is_absolute():
                source = REPO/source
            if isinstance(expected, dict):
                expected = expected['sha256']
            assert digest(source) == expected, source
            pins[str(source)] = expected
            # A compact content-addressed copy preserves any new exact stage inputs.
            if source.is_relative_to(REPO/'artifacts'):
                old_packet = REPO/'artifacts/muon_physical_outgoing_energy_20261015'
                old_files = list(old_packet.rglob(source.name))
                prior = next((x for x in old_files if x.is_file() and digest(x)==expected), None)
                if prior:
                    continue
                copy(source, OUT/'retained_inputs'/(expected[:12]+'_'+source.name))
    selection = dict(
        source='Explicit human reply to the magnetic-moment benchmark question in this chat.',
        selected_answer='Formed muon in a weak measuring field (Recommended)',
        question='For the magnetic-moment benchmark, should we study the formed muon after it has left the collision and entered a weak measuring magnetic field, or its response while still inside the collision fields?',
        selection_status='CONFIRMED_BY_USER',
        replaces_pending_assumption_in='artifacts/muon_physical_outgoing_energy_20261015/checkpoint.txt',
        background='formed muon, with its full self-field; the earlier finite trial is not promoted to this state',
        expansion='infinitesimal applied B at B_applied=0; self-fields and induced responses retained',
        selected_incoming_collision_beams_for_measurement=False,
        physical_outgoing_rule='existing future-retarded regularity/outgoing support, including realized decay/daughter channels',
        muon_assumed_eternally_stable=False,
        source_axes='all three canonical local spatial magnetic directions; body-to-measuring/rest-frame map remains to be supplied',
        finite_turn_on_plateau_identified_with_global_uniform_or_adiabatic_field=False)
    (OUT/'selection.json').write_bytes(encoded(selection))
    physical = dict(
        physical_formed_muon_background=None, physical_outgoing_boundary_energy_jet=None,
        physical_two_spin_muon_state=None, full_same_domain_Gamma_B=None,
        physical_magnetic_moment=None, physical_g_mu=None, physical_a_mu=None,
        physical_coupled_matching_corrections_applied=0,
        fresh_physical_Maxwell_all226_after_pass=False,
        nonzero_finite_spin_impurity_commutators_and_splitting_retained=True,
        point_spin_purity_or_bare_spin_commutator_used_as_new_physical_gate=False,
        angular_constant_projection_of_probe_used_as_zero_moment=False,
        completed_source_D5_history_profile_canonical_pairing_campaigns_restarted=False)
    source_laws = ['src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py',
                   'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
                   'src/bhsm/interface/ae4_branch_relative_support_transition.py',
                   'src/bhsm/interface/muon_native_dirac_hamiltonian.py',
                   'src/bhsm/interface/muon_holomorphic_n1_magnetic_action.py',
                   'scripts/evaluate_muon_trial_d5_trace_action.py']
    result = dict(classification='USER_CONFIRMED_FORMED_WEAK_FIELD_PREPARATION_WITH_EVALUATED_FINITE_POINT_SPIN_AND_LOCAL_PROBE',
                  selection=selection, physical_status=physical,
                  actual_scientific_repeat_pairs=repeated, input_hashes=pins,
                  existing_source_law_sha256={s:digest(REPO/s) for s in source_laws},
                  producer_sha256={p.name:digest(p) for p in producers},
                  failed_optional_source_difference_control_preserved='same_epoch_probe/run_1/failed_attempt.json',
                  source_probe_scope='New local source and direct angular operator operands on the saved finite stages; not a formed-muon saddle, complete retarded magnetic response or interacting Pauli coefficient.',
                  spin_scope='Unit point-coefficient current Gram and separate analytic pole normalization. Nonzero point-spin admixture is retained; it is neither rounded away nor classified as an upstream numerical error or a new physical admission gate. Full angular/field state and measuring-frame spin remain unevaluated.',
                  binding_repeat_scope='Two serializations bind the independent evaluations above; this binding does not repeat a physics solve.')
    payload = encoded(result)
    for run in (1, 2):
        folder = OUT/f'binding_run_{run}'
        folder.mkdir(exist_ok=True)
        (folder/'result.json').write_bytes(payload)
    print(json.dumps(dict(output=str(OUT), binding_sha256=sha256(payload).hexdigest(),
                          actual_components=[x[0] for x in sources])))


if __name__ == '__main__':
    main()
