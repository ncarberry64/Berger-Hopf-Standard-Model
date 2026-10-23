"""Bind independently evaluated finite controls without changing their bytes."""
from hashlib import sha256
import json
from pathlib import Path
import shutil

REPO = Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
WORK = Path(r'C:/Users/carbe/OneDrive/Documents/CODEX')
OUT = REPO/'artifacts/muon_physical_outgoing_energy_20261015'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def copy_file(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() != source.read_bytes():
        raise RuntimeError('Refusing to replace different retained bytes: '+str(destination))
    shutil.copyfile(source, destination)
    assert digest(source) == digest(destination)


def main():
    pairs = [
        ('bhsm_finite_d5_split_spin_poles_20261015', 'split_poles', 'run_1', 'run_2'),
        ('bhsm_outgoing_tail_domain_20261015', 'outgoing_domain', 'run_1', 'run_2'),
        ('bhsm_split_pole_em_observable_20261015', 'em_readout', 'run_2', 'run_3'),
    ]
    repeated = []
    for source, destination, left, right in pairs:
        a, b = [WORK/'outputs'/source/r for r in (left, right)]
        names = sorted(p.name for p in a.iterdir() if p.is_file())
        assert names == sorted(p.name for p in b.iterdir() if p.is_file())
        for name in names:
            assert (a/name).read_bytes() == (b/name).read_bytes(), name
            for run in (left, right):
                copy_file(WORK/'outputs'/source/run/name, OUT/destination/run/name)
        repeated.append(dict(component=destination, independently_evaluated_runs=[left, right],
                             byte_identical_files={name: digest(a/name) for name in names}))
    for name in ('bhsm_muon_finite_d5_split_spin_poles_20261015.py',
                 'bhsm_baton_zoo_outgoing_tail_domain_20261015.py',
                 'bhsm_muon_split_pole_em_observable_20261015.py'):
        copy_file(WORK/name, REPO/'audits'/name)
    copy_file(WORK/'outputs/bhsm_split_pole_em_observable_20261015/actual_four_finite_poles_manifest.json',
              OUT/'em_readout/actual_four_finite_poles_manifest.json')
    for source, destination in (
        ('test_bhsm_outgoing_tail_domain_20261015.py', 'test_bhsm_outgoing_tail_domain_20261015.py'),
        ('test_bhsm_muon_split_pole_em_observable_20261015.py', 'test_bhsm_split_pole_em_observable_20261015.py'),
    ):
        prefix = ('from pathlib import Path\nimport sys\n'
                  'sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"audits"))\n')
        body = (WORK/source).read_text(encoding='utf8')
        if source == 'test_bhsm_muon_split_pole_em_observable_20261015.py':
            body = body.replace("Path(__file__).with_name('bhsm_muon_split_pole_em_observable_20261015.py')",
                                'Path(__file__).resolve().parents[1]/"audits"/"bhsm_muon_split_pole_em_observable_20261015.py"')
        (REPO/'tests'/destination).write_text(prefix+body,
                                            encoding='utf8', newline='\n')
    (OUT/'packaging_script.py').write_bytes(Path(__file__).read_bytes())

    # Archive the consumed finite-control coefficients, not a new action solve.
    inputs = {}
    for component, run in [('split_poles','run_1'), ('outgoing_domain','run_1'), ('em_readout','run_3')]:
        result = json.loads((OUT/component/run/'result.json').read_text(encoding='utf8'))
        for path, expected in result.get('input_hashes', {}).items():
            p = Path(path)
            if not p.is_absolute():
                p = REPO/p
            if p.is_relative_to(REPO/'artifacts'):
                assert digest(p) == expected
                relative = p.relative_to(REPO)
                group = ('d5_coefficients' if 'muon_trial_d5_trace_action_20261012' in p.parts else
                         'old_pole_center' if 'muon_d5_finite_trace_pole_match_20261012' in p.parts else
                         'causal_prefix' if 'muon_joined_d5_causal_tail_action_20261013' in p.parts else
                         'normal_prefix')
                destination = OUT/'retained_inputs'/group/p.name
                copy_file(p, destination)
                inputs[relative.as_posix()] = dict(sha256=expected,
                                                  archived_at=destination.relative_to(OUT).as_posix())
    return dict(actual_scientific_repeat_pairs=repeated, retained_input_snapshots=inputs,
                input_snapshots_are_not_new_action_evaluations=True)


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, indent=2))
