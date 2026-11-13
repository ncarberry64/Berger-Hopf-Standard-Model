"""Execute the Clifford-derived piecewise proper-clock current action."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_continued_action_reality import actual_source_curve_coefficients
from bhsm.interface.muon_piecewise_euclidean_action import (
    FAMILY_INDICES,proper_euclidean_source_nodes,family_piecewise_weak_forms,
    positive_weak_form_factor,weak_form_heat_action,weak_form_heat_source_contact)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def read(path):
    with np.load(path,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}


def materialize(output,*,temporal_cells=(4,8),cutoff=1.0329133712274834e-11):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous piecewise action')
    refs={};records=[];pending=[];fi=FAMILY_INDICES[1]
    for side in('incoming','outgoing'):
        phase,_=retained_input(side,refs);data=[]
        folder=ROOT/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'
        for name in('phase','velocity','contacts'):
            path=folder/f'{side}_{name}.npz'
            refs[path.relative_to(ROOT).as_posix()]=sha256(path.read_bytes()).hexdigest();data.append(read(path))
        curves=actual_source_curve_coefficients(*data)
        nodes=proper_euclidean_source_nodes(phase,curves,family_indices=fi)
        pending.append((side+'_nodes.npz',{k:v for k,v in nodes.items()if isinstance(v,np.ndarray)}))
        print(json.dumps(dict(stage='proper_Euclidean_action_nodes',side=side,
            total_proper_clock=nodes['total_proper_clock'],source_cells=nodes['source_cells'],
            reflected_body_identity_max=nodes['reflected_body_identity_max'],
            reflected_source_identity_max=nodes['reflected_source_identity_max']),sort_keys=True),flush=True)
        previous=None
        for n in temporal_cells:
            forms=family_piecewise_weak_forms(nodes,temporal_cells=n,family=1)
            s=positive_weak_form_factor(forms['source_K'],forms['source_M'])
            t=positive_weak_form_factor(forms['target_K'],forms['target_M'])
            B=forms['source_numerator'];response=weak_form_heat_action(s,B,cutoff)
            c0=weak_form_heat_action(s,B,0.)
            # SAME-form final Dirichlet comparison: both K and M restricted.
            si=np.arange((n-1)*6);ti=np.arange((n-1)*120)
            sd=positive_weak_form_factor(forms['source_K'][np.ix_(si,si)],forms['source_M'][np.ix_(si,si)])
            td=positive_weak_form_factor(forms['target_K'][np.ix_(ti,ti)],forms['target_M'][np.ix_(ti,ti)])
            restricted=np.zeros_like(response);restricted[si]=weak_form_heat_action(sd,B[si],cutoff)
            arrays={k:v for k,v in forms.items()if isinstance(v,np.ndarray)}
            arrays.update(source_heat_response=response,source_c0_response=c0,
                source_final_Dirichlet_response=restricted,source_relative_boundary_response=response-restricted,
                source_eigenvalues=s['eigenvalues'],target_eigenvalues=t['eigenvalues'],
                source_eigenvectors=s['eigenvectors'],target_eigenvectors=t['eigenvectors'],
                cutoff=np.array(cutoff))
            contacts=[]
            for a in range(3):
                dK=forms['magnetic_delta_K'][a];dB=forms['magnetic_delta_numerator'][a]
                mag=weak_form_heat_source_contact(s,t,B,dK,dB,cutoff)
                mag0=weak_form_heat_source_contact(s,t,B,dK,dB,0.)
                inner=weak_form_heat_source_contact(sd,td,B[si],dK[np.ix_(ti,si)],dB[ti],cutoff)
                inner_response=np.zeros_like(mag['response']);inner_response[ti]=inner['response']
                for k,v in mag.items():arrays[f'magnetic_{a}_{k}']=v
                arrays[f'magnetic_{a}_final_Dirichlet_response']=inner_response
                arrays[f'magnetic_{a}_relative_boundary_response']=mag['response']-inner_response
                original0=np.linalg.solve(forms['target_K'],dB-dK@c0)
                contacts.append(dict(axis=a,delta_K_norm=float(np.linalg.norm(dK)),
                    delta_numerator_norm=float(np.linalg.norm(dB)),response_norm=float(np.linalg.norm(mag['response'])),
                    square_contact_norm=float(np.linalg.norm(mag['square_contact'])),
                    numerator_contact_norm=float(np.linalg.norm(mag['numerator_contact'])),
                    boundary_return_norm=float(np.linalg.norm(mag['response']-inner_response)),
                    c0_original_action_contact_residual_max=float(np.max(abs(forms['target_K']@mag0['response']+dK@c0-dB))),
                    c0_direct_inverse_difference_max=float(np.max(abs(mag0['response']-original0)))))
            current=forms['current_target']@response
            row=dict(side=side,temporal_cells=n,total_proper_clock=nodes['total_proper_clock'],
                represented_source_cells=nodes['source_cells'],source_P_minimum=float(s['eigenvalues'][0]),
                target_P_minimum=float(t['eigenvalues'][0]),source_current_norm=float(np.linalg.norm(current)),
                source_boundary_return_norm=float(np.linalg.norm(response-restricted)),
                c0_original_action_residual_max=float(np.max(abs(forms['source_K']@c0-B))),
                source_Hermiticity_rounding_max=forms['source_Hermiticity_rounding_max'],
                target_Hermiticity_rounding_max=forms['target_Hermiticity_rounding_max'],
                current_previous_resolution_difference_norm=None if previous is None else float(np.linalg.norm(current-previous)),
                contacts=contacts)
            previous=current;records.append(row)
            # Keep every array unchanged, splitting only dense eigenvector
            # packaging so each published archive stays below10MiB.
            vectors=arrays.pop('target_eigenvectors');parts=[]
            for start in range(0,vectors.shape[1],240):
                stop=min(start+240,vectors.shape[1]);name=f'{side}_cells_{n}_target_vectors_{start}_{stop}.npz'
                pending.append((name,dict(target_eigenvectors=vectors[:,start:stop],
                    column_start=np.array(start),column_stop=np.array(stop),full_shape=np.array(vectors.shape))))
                parts.append(dict(archive=name,column_start=start,column_stop=stop))
            row['target_eigenvector_parts']=parts;pending.append((f'{side}_cells_{n}.npz',arrays))
            print(json.dumps(dict(stage='piecewise_positive_Euclidean_weak_current',**row),sort_keys=True),flush=True)
    for path in('src/bhsm/interface/muon_piecewise_euclidean_action.py','tests/test_muon_piecewise_euclidean_action.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[path]=sha256((ROOT/path).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    out.mkdir(parents=True);archives={}
    for name,arrays in pending:
        path=out/name;_compressed_npz(path,arrays)
        archives[name]=dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest())
    report=dict(classification='EVALUATED_PIECEWISE_CLIFFORD_EUCLIDEAN_ACTION_AND_SAME_FORM_BOUNDARY_RETURN',
        input_hashes=refs,archives=archives,records=records,cutoff=cutoff,
        actual_action='A_E=partial_tau_E+Hcan(t(tau_E)); dt/dtau_E=-i/N; independent reflected branch dt_sharp/dtau_E=+i/N',
        positive_pairing='real positive proper-clock quadrature; A_Edagger from the independently evaluated reflected real-action coefficients',
        temporal_domain='continuous piecewise linear trace with initial value zero and final natural cotangent; shared corner value/weak flux rows, no imposed final Dirichlet in the primary form',
        boundary_comparison='full minus SAME K/M final-Dirichlet heat action, including dK and dB; this is an actual finite-domain return, not a zero-frequency Schur heat replacement',
        source_image='middle fixed-Y family C6 source and all20 n1+n3 angular target images, axes0:3; no source-compressed square',
        quantum_loop_or_stratified_relative_completion=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 ODE/quadrature/FE/spectral action diagnostics and 4/8 FE comparison; no physical temporal/exterior/tail/overlap uncertainty certificate')
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=report['classification'],archives=archives),sort_keys=True));return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    materialize(parser.parse_args().output)
