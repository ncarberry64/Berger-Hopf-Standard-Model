"""Execute the reached literal continued H Green and fixed-Y open current."""
from pathlib import Path
from hashlib import sha256
import argparse, json, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_literal_euclidean_higgs_green import (
    continued_action_polynomial, literal_higgs_weak_form, intrinsic_higgs_open_current_application)
from bhsm.interface.muon_euclidean_angular_weak_action import (
    angular_action_coefficients, angular_weak_square, euclidean_open_action_vertices)
from bhsm.interface.muon_continued_action_reality import action_reality_coefficient
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_corrected_profile_magnetic_response import corrected_profile_reached_sample
from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def _read(path, refs, expected=None):
    raw = path.read_bytes()
    h = sha256(raw).hexdigest()
    if expected is not None and h != expected:
        raise ValueError('consumed action/source changed: '+str(path))
    refs[path.relative_to(ROOT).as_posix()] = h
    with np.load(path,allow_pickle=False) as a:
        return {k:a[k].copy() for k in a.files}


def materialize(output, *, temporal_cells=(2,4), fresh_checks=True):
    out = ROOT/output
    if out.exists():
        raise FileExistsError('preserve completed action applications')
    refs, rows, pending = {}, [], []
    original = ROOT/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'
    p = original/'result.json'
    original_receipt = json.loads(p.read_bytes())
    refs[p.relative_to(ROOT).as_posix()] = sha256(p.read_bytes()).hexdigest()
    euclidean = ROOT/'artifacts/muon_piecewise_euclidean_action_20261011/run_2'
    p = euclidean/'result.json'
    ereceipt = json.loads(p.read_bytes())
    refs[p.relative_to(ROOT).as_posix()] = sha256(p.read_bytes()).hexdigest()
    angular = retained_full_q_angular_space(ROOT)
    E = angular['derivative_matrices'][:,:4,:4]
    Y = np.diag(lepton_current_hilbert_representation()['family_Y'])
    for side in ('incoming','outgoing'):
        phase, _ = retained_input(side,refs)
        L = abs(float(phase['receipt']['span']))
        values = []
        for name in ('M','B','K'):
            path = original/f'{side}_operator_{name}.npz'
            data = _read(path,refs,original_receipt['array_archives'][path.name]['sha256'])
            values.append(data['raw_'+name])
            if name == 'M': times = data['times']
            elif not np.array_equal(times,data['times']): raise ValueError('same original action nodes required')
        interpolation = continued_action_polynomial(times,values)
        fresh = []
        if fresh_checks:
            for u in (.125*L,.375*L,.625*L,.875*L):
                t = u-L if side == 'incoming' else u
                sample = profile_preserving_raw_sample(phase,t)
                kw = {} if side == 'incoming' else dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
                actual = corrected_profile_reached_sample(sample['raw_fields'],phase['representation'],angular,
                    np.zeros((400,8)),np.zeros((400,8)),coordinate_time=t,
                    nu_squared_action=phase['receipt']['action_parameters']['nu_squared_action'],**kw)
                interpolated = interpolation(u)
                checks = []
                for name, a, b in zip(('M','B','K'),actual['raw_forms'],interpolated):
                    delta = a[:480,:480]-b[:480,:480]
                    checks.append(dict(name=name,maximum_absolute_difference=float(np.max(abs(delta))),
                        relative_Frobenius_difference=float(np.linalg.norm(delta)/max(np.linalg.norm(a[:480,:480]),np.finfo(float).tiny)),
                        intrinsic_H_maximum_absolute_difference=float(np.max(abs(delta[400:480,400:480])))))
                fresh.append(dict(coordinate_time=t,source_time=u,forms=checks))
                print(json.dumps(dict(stage='fresh_actual_action_interpolation_check',side=side,**fresh[-1]),sort_keys=True),flush=True)
        nodes = _read(euclidean/f'{side}_nodes.npz',refs,ereceipt['archives'][side+'_nodes.npz']['sha256'])
        nodes['total_proper_clock'] = next(r['total_proper_clock'] for r in ereceipt['records'] if r['side']==side)
        # Action-polynomial clocks are chronological u; the saved node
        # anchor is physical t.  Their derivatives have the same +1 clock.
        original_polynomial = interpolation
        def action(anchor, offset=0j):
            return original_polynomial(float(anchor)+L if side=='incoming' else float(anchor),offset)
        nodes_by_family = {}
        for family in (1,2):
            fi = FAMILY_INDICES[family]
            fn = dict(nodes)
            fn['lepton_indices'] = fi
            fn['H'] = np.array([action_reality_coefficient(phase,float(t),z)['Hcan'][np.ix_(fi,fi)]
                for t,z in zip(nodes['coordinate_anchor'],nodes['coordinate_offset'])])
            fn['Hsharp'] = np.array([action_reality_coefficient(phase,float(t),z)['Hcan'][np.ix_(fi,fi)]
                for t,z in zip(nodes['coordinate_anchor'],nodes['reflected_coordinate_offset'])])
            nodes_by_family[family] = fn
        for n in temporal_cells:
            h = literal_higgs_weak_form(nodes,action,temporal_cells=int(n),harmonics=np.arange(4))
            arrays = {k:v for k,v in h.items() if isinstance(v,np.ndarray)}
            row = dict(side=side,temporal_cells=int(n),original_action_operator_nodes=len(times),
                proper_source_cells=len(np.unique(nodes['source_cell'])),proper_clock=nodes['total_proper_clock'],
                fresh_actual_action_interpolation_checks=fresh,
                intrinsic_H_current_domain='full n1 H16, full n1 At/Ar/Ai80 retained in point matrices; internal gauge wall trace zero',
                normalized_Hermitian_part_minimum=float(h['normalized_Hermitian_part_eigenvalues'][0]),
                operator_Hermiticity_defect=h['operator_Hermiticity_defect'],
                original_action_inverse_residual_max=h['original_action_inverse_residual_max'],
                original_Gauss_smallest_singular_value_min=h['original_Gauss_smallest_singular_value_min'],
                independent_branch_reflection_max=h['independent_branch_reflection_max'],
                gauge_H_cross_max=float(np.max(h['gauge_H_cross_max'])),families=[])
            for family, fn in nodes_by_family.items():
                fc = angular_action_coefficients(fn,E,family=family)
                ff = angular_weak_square(fn,fc,temporal_cells=int(n))
                # The four scalar vertices do not depend on R,N; derive
                # them from the same fixed-Y action, without refitting Y.
                v = euclidean_open_action_vertices(fn['R'][0],fn['N'][0],family=family)['scalar']
                a = intrinsic_higgs_open_current_application(fn,fc,ff,h,v,temporal_cells=int(n))
                for key,value in a.items():
                    if isinstance(value,np.ndarray):arrays[f'family_{family}_'+key]=value
                arrays[f'family_{family}_fermion_original_K'] = ff['K']
                arrays[f'family_{family}_fermion_Gram'] = ff['M']
                arrays[f'family_{family}_unit_Y_current'] = a['open_Gaussian_current']/Y[family]**2
                row['families'].append(dict(family=family,indices=FAMILY_INDICES[family].tolist(),fixed_Y=float(Y[family]),
                    current_norm=float(np.linalg.norm(a['open_Gaussian_current'])),
                    current_complex_trace=[float(np.trace(a['open_Gaussian_current']).real),float(np.trace(a['open_Gaussian_current']).imag)],
                    fermion_original_source_rows_max=a['original_fermion_source_rows_max']))
            row['middle_light_paired_current_norm'] = float(np.linalg.norm(arrays['family_1_open_Gaussian_current']-arrays['family_2_open_Gaussian_current']))
            pending.append((f'{side}_cells_{n}.npz',arrays))
            rows.append(row)
            print(json.dumps(dict(stage='literal_continued_H_action_open_current',**row),sort_keys=True),flush=True)
    for name in ('muon_literal_euclidean_higgs_green','muon_euclidean_angular_weak_action','muon_piecewise_euclidean_action',
                 'muon_continued_action_reality','muon_corrected_profile_magnetic_response'):
        p = 'src/bhsm/interface/'+name+'.py';refs[p] = sha256((ROOT/p).read_bytes()).hexdigest()
    for p in ('tests/test_muon_literal_euclidean_higgs_green.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p] = sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):
        raise RuntimeError('consumed frozen action changed')
    out.mkdir(parents=True)
    archives = {}
    for name, data in pending:
        p = out/name;_compressed_npz(p,data)
        if p.stat().st_size > 10*1024*1024:raise ArithmeticError('split packaging required; do not prune arrays')
        archives[name] = dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    receipt = dict(classification='EVALUATED_LITERAL_CONTINUED_INTRINSIC_H_ACTION_GAUSSIAN_CURRENT',
        input_hashes=refs,archives=archives,records=rows,
        action='L_E=-L_L/N, material At_E=-iAt_L/N; original analytic temporal/radial cross preserved',
        scalar_Maxwell_common_cap_normalization='raw full488 action divided by8V²; intrinsic scalar relative8 already present in the raw action',
        exact_domain_reduction='internal gauge radial trial has zero wall trace; all gauge400/H80 raw cross blocks zero; external drive8 not relabeled as internal gauge wall fluctuations',
        fermion_factor='Clifford-derived A_E; its independent reflected branch supplies A_Edagger in the actual proper-clock weak form',
        Gaussian_current='-V (A_Edagger A_E)^-1 A_Edagger V K_H^-1 at c=0; all C6 fibers before charged projection',
        field_pairing='literal continued scalar action Hessian, with analytic transpose; reflected absolute square or old positive ADM Green not substituted',
        computational_temporal_domain='initial H trace zero, final natural weak cotangent; coefficient cell/source corners inherited; represented free-final Clifford factor on the same arm',
        uncertainty_scope='binary action interpolation/fresh-node differences, FE and inverse residuals; no contour/assembly/continuum/starting-shell/LSZ error enclosure',
        regulated_P_cycle_or_full_native_or_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None)
    (out/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return receipt


if __name__=='__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--temporal-cells',type=int,nargs='+',default=[2,4])
    args = p.parse_args()
    materialize(args.output,temporal_cells=tuple(args.temporal_cells))
