"""Evaluate only the new parent tangential source/contact on saved data."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    p.write_bytes((json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode())


def run(root, output):
    if output.exists():
        raise FileExistsError('Use a new output directory; saved evidence is immutable')
    sys.path.insert(0, str(root/'src'))
    from bhsm.interface.muon_parent_source_contact import evaluate_cut
    sources = root/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz'
    geometry = root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz'
    with np.load(sources) as src, np.load(geometry) as geo:
        arrays, scalars, checks = evaluate_cut(src, geo)
    output.mkdir(parents=True)
    np.savez_compressed(output/'parent_source_contact.npz', **arrays)
    inputs = [sources, geometry,
        root/'src/bhsm/interface/muon_parent_source_contact.py',
        root/'scripts/replay_muon_parent_source_contact.py',
        root/'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        root/'src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py',
        root/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py']
    save(output/'input_hashes.json', [dict(path=p.relative_to(root).as_posix(), sha256=sha(p)) for p in inputs])
    head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=root, text=True).strip()
    branch = subprocess.check_output(['git','branch','--show-current'], cwd=root, text=True).strip()
    diff = subprocess.check_output(['git','diff','--binary'], cwd=root)
    (output/'working_tree_tracked.diff').write_bytes(diff)
    (output/'working_tree_status.txt').write_bytes(subprocess.check_output(['git','status','--short'],cwd=root))
    result = dict(checkpoint='BHSM_MUON_PARENT_TANGENTIAL_SOURCE_CONTACT_20261003',
        branch=branch, calculation_HEAD=head,
        reference_checkpoint='0ec64ea11cd52661b567c2efaf96ebedefc41e4f',
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',
        differentiation_coordinate='b; beta=T_b b; saved source is (-iQ) times beta, no additional sqrt2 or 2/3',
        action_owner='AE4 canonical geometric L2; adopted common-A effective Dirac action',
        realization='M5 plus, sigma1 carrier, saved right spatial coframe, C2 step1222 past cut',
        domain_scope='Central hypercharge coexact H1 test, compact radial support, zero material trace; temporal/prefix extension and full quotient not evaluated',
        state_scope='64 Spin4 x SM16 coordinate probes per fixed family; no physical muon state, child16 basis, pole or LSZ substituted',
        equations=dict(Xi_A='(T_b L/r) i gamma_LR^a S_A,a^sigma1',
            Xi_Z='(T_b z/r) i gamma_LR^a Y_B,a (-iY)',
            local_Xi_ZA='0 only at fixed metric/section for the affine local minimal coupling',
            K_ZA_contact='Xi_Z^dagger Xi_A + Xi_A^dagger Xi_Z',
            cut_density='2*pi^2 integral d_rho nu C r^3 chi^2 K_ZA_contact',
            M_probe_cut_density='2*pi^2 integral d_rho nu C r^3 chi^2 I64',
            full_A_ZA='solve(M, K_ZA-M_ZA A-M_Z A_A-M_A A_Z)',
            target='c_D,ZA_contact=-Tr(Q(A_strat) A_ZA)',
            native_length='ell_star=1/E_impedance[Phi_star;Sigma_star], retained unevaluated'),
        evaluated=scalars, checks=checks,
        complement_scope='All n1/n3 outputs of source acting on n0 probes retained. No tail theorem for Q, repeated actions or resolvent.',
        error_scope='256-bit Arb scalar enclosure for exact binary64 piecewise-affine nodal model. Matrix contractions binary64, unvalidated roundoff. History/interpolation, temporal integration, domain, spectral tails and native uncertainties unevaluated.',
        execution=dict(old_production_runs=0, old_symbolic_replays=0, native_heat_evaluations=0,
            parent_local_source_actions=True, parent_test_source_labels=8,
            spin_carrier_probe_columns=64, radial_nodes=65, physical_transfer_directions=0),
        contribution_ledger=dict(native_bulk_heat=None, state_variation=None, contact=dict(
            local_parent_K_ZA_cut_density='parent_source_contact.npz',
            native_heat_weighted_trace=None, paired_DQ_term=None),
            domain_boundary=None, completion_counterterm=None, strong_within_native=None),
        frozen_local=json.loads((root/'artifacts/muon_connection_attachment_20261002/frozen_local.json').read_text()),
        physical_a_mu=None, physical_g_mu=None)
    save(output/'result.json', result)
    save(output/'receipt.json', dict(script_sha256=sha(Path(__file__)),
        old_producers_imported=False, earlier_hash_audit_repeated=False,
        files=[dict(path=p.name,sha256=sha(p)) for p in sorted(output.iterdir())]))
    print(json.dumps(dict(output=str(output),evaluated=scalars,checks=checks,native_heat_evaluations=0)))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repository', type=Path, default=HERE.parent)
    p.add_argument('--output', type=Path, required=True)
    a=p.parse_args()
    run(a.repository.resolve(), a.output.resolve())
