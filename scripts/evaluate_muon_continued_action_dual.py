"""Apply the doubled analytic action and current on the actual joined contour."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_continued_action_dual import (
    analytic_midpoint_action,analytic_action_current,directed_action_contact,
    analytic_magnetic_current,principal_heat_contour_condition)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def _sparse_export(arrays,prefix,matrix):
    a=matrix.tocsr()
    arrays[prefix+'_data']=a.data;arrays[prefix+'_indices']=a.indices
    arrays[prefix+'_indptr']=a.indptr;arrays[prefix+'_shape']=np.array(a.shape)


def materialize(output, *, refinements=(16,32),cutoff_probe=1.0329133712274834e-11):
    out=ROOT/output;folder=ROOT/'artifacts/muon_continued_current_factor_20261011/run_1'
    if out.exists():raise FileExistsError('preserve earlier analytic action application')
    md=json.loads((folder/'result.json').read_bytes());refs=dict(md['input_hashes'])
    refs[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256((folder/'result.json').read_bytes()).hexdigest()
    records=[];pending=[];previous=None
    for steps in refinements:
        inp=[]
        for side in('incoming','outgoing'):
            path=folder/f'{side}_{steps}.npz';h=md['array_archives'][path.name]['sha256']
            if sha256(path.read_bytes()).hexdigest()!=h:raise ValueError('same corrected-profile source changed')
            refs[path.relative_to(ROOT).as_posix()]=h
            with np.load(path,allow_pickle=False)as a:inp.append({k:a[k].copy()for k in a.files})
        for key in('family_Y','family_indices','alpha6','n1_right_body_derivatives'):
            if not np.array_equal(inp[0][key],inp[1][key]):raise ValueError('one common representation required')
        names=('proper_cell_weights','common_Hcan0','common_Hcan1','R4','source_right_map',
            'target_left_map','magnetic_right_Y0','magnetic_right_Y1','magnetic_left_Y0',
            'magnetic_left_Y1','magnetic_continued_source_tau_first')
        d={k:np.concatenate((inp[0][k],inp[1][k]))for k in names}
        Y=float(inp[0]['family_Y'][1]);body=d['common_Hcan0']+Y*d['common_Hcan1']
        alpha,E=inp[0]['alpha6'],inp[0]['n1_right_body_derivatives']
        body1=np.array([np.kron(H,np.eye(4))-1j*sum(np.kron(a,e)for a,e in zip(alpha,E))/R
            for H,R in zip(body,d['R4'])])
        a=analytic_midpoint_action(d['proper_cell_weights'],body)
        b=analytic_midpoint_action(d['proper_cell_weights'],body1)
        R0,L0=d['source_right_map'],d['target_left_map']
        R1=np.array([np.kron(r,np.eye(4))for r in R0]);L1=np.array([np.kron(l,np.eye(4))for l in L0])
        c0=analytic_action_current(a,R0,L0);c1=analytic_action_current(b,R1,L1)
        arrays=dict(body_n0=body,body_n1=body1,proper_cell_weights=d['proper_cell_weights'],
            family_Y=inp[0]['family_Y'],family_indices=inp[0]['family_indices'],
            source_R_n0=R0,target_L_n0=L0,source_R_n1=R1,target_L_n1=L1,
            canonical_Xi_tau_first=d['magnetic_continued_source_tau_first'],
            midpoint_birth_index=np.array(steps),contour_rotation=np.array(1j))
        checks=[]
        for label,action,current in(('n0',a,c0),('n1',b,c1)):
            for key in('A_full','left_Euler_full','midpoint_full','contour_source_Gram',
                'action','doubled_Grassmann_action','oriented_endpoint_contact','original_Green_rows'):
                _sparse_export(arrays,label+'_'+key,action[key])
            arrays.update({label+'_'+k:v for k,v in current.items()if isinstance(v,np.ndarray)})
            arrays[label+'_right_final_trace']=current['right_solution'][-action['dimension']:]
            checks.append(dict(sector=label,Green_identity_max=action['Green_identity_max'],
                doubled_skew_max=action['doubled_skew_max'],signed_action_identity_max=action['lorentz_contour_action_identity_max'],
                current_pairing_max=current['current_pairing_max'],inverse_action_identity_max=current['inverse_action_identity_max'],
                original_right_Euler_max=float(np.max(abs(current['original_right_Euler_rows']))),
                original_action_max=float(np.max(abs(current['original_action_rows']))),
                analytic_versus_Hermitian_dual_difference_norm=current['action_Hermitian_dual_mismatch_norm']))
        magnetic=[]
        for axis in range(3):
            forward=d['magnetic_right_Y0'][:,axis]+Y*d['magnetic_right_Y1'][:,axis]
            reverse=d['magnetic_left_Y0'][:,axis]+Y*d['magnetic_left_Y1'][:,axis]
            for label,s,t,sc,L,V in(('10',a,b,c0,L1,forward),('01',b,a,c1,L0,reverse)):
                contact=directed_action_contact(s,t,V);mag=analytic_magnetic_current(s,t,sc,L,contact)
                arrays[f'Xi_{label}_{axis}']=V
                for k in('delta_right_operator','delta_action','delta_left_Euler_action','delta_doubled_Grassmann_action'):
                    _sparse_export(arrays,f'{label}_{axis}_'+k,contact[k])
                arrays.update({f'{label}_{axis}_'+k:v for k,v in mag.items()if isinstance(v,np.ndarray)})
                magnetic.append(dict(source_axis=axis,directed_block=label,
                    physical_coordinate_current_norm=float(np.linalg.norm(mag['physical_coordinate_current'])),
                    original_right_Euler_max=float(np.max(abs(mag['original_right_Euler_rows']))),
                    original_action_max=float(np.max(abs(mag['original_action_rows']))),
                    current_pairing_max=mag['current_pairing_max'],
                    inverse_operator_contact_identity_max=mag['inverse_operator_contact_identity_max']))
        curr=c0['physical_coordinate_current']
        row=dict(steps_per_arm=steps,actual_fixed_middle_Y=Y,analytic_action_checks=checks,
            physical_coordinate_current_norm=float(np.linalg.norm(curr)),
            contour_current_norm=float(np.linalg.norm(c0['contour_current'])),
            current_refinement_difference=None if previous is None else float(np.linalg.norm(curr-previous)),
            right_birth_trace_norm=float(np.linalg.norm(c0['right_solution'][(steps-1)*6:steps*6])),
            free_final_trace_norm=float(np.linalg.norm(c0['right_solution'][-6:])),magnetic_contacts=magnetic)
        previous=curr;records.append(row);pending.append((f'joined_{steps}.npz',arrays))
        print(json.dumps(dict(stage='doubled_analytic_action_current',**row),sort_keys=True),flush=True)
    for path in('src/bhsm/interface/muon_continued_action_dual.py',
        'tests/test_muon_continued_action_dual.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[path]=sha256((ROOT/path).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    condition=principal_heat_contour_condition(1j,cutoff_probe)
    condition['principal_cutoff_phase']=[condition['principal_cutoff_phase'].real,condition['principal_cutoff_phase'].imag]
    out.mkdir(parents=True);files={}
    for name,arrays in pending:
        p=out/name;_compressed_npz(p,arrays);files[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    result=dict(classification='EVALUATED_DOUBLED_ANALYTIC_ACTION_CURRENT_DUAL_AND_GREEN_CONTACT_ON_ACTUAL_JOINED_CONTOUR',
        input_hashes=refs,array_archives=files,records=records,
        contour='tau=i*(t-t0); actual corrected-profile Hcan at retained real-time anchors',
        signed_action='S_L=i S_contour; C_contour=i C_coordinate',
        analytic_left_action='independent Grassmann left Euler uses -d_tau+Hcan^T; no imposed complex conjugation',
        Green_identity='bar_chi^T chi at final minus initial; right initial zero and left final zero applied after full identity',
        chronological_birth='one common T=I trace, incoming then outgoing with no duplicated birth coordinate',
        numerical_far_domain='right trace initially zero for this inverse; outer face is not identified with E0 or an asymptotic vacuum',
        magnetic_contact='both directed canonical deltaH, with both midpoint halves and analytic transpose dual; all source/current pairing retained',
        source_rate_scope='actual canonical Xi tau first germs exported; no continuous complex-contour interpolation invented',
        source_norm='unit canonical current and unit-coupling -Q; no electric charge, density or Yukawa fit inserted',
        angular_scope='exact reached C6 n0 and four-mode n1 directed source images; not full exterior continuum',
        principal_heat_rotation=condition,
        necessary_next_heat_application='continue the formal Euclidean adjoint/reality, proper measure, relative domain and heat contour together; the conjugated positive square on the imaginary anchor is a different Riesz construction',
        real_Euclidean_relative_contour_deformation_proved=False,
        physical_L2_L3_quantum_loop_or_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 original Euler/Green/action/current identities and temporal refinement; no continuum, contour-deformation, relative-exterior, or physical uncertainty certificate')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--refinements',type=int,nargs='+',default=[16,32]);a=p.parse_args()
    print(json.dumps(materialize(a.output,refinements=tuple(a.refinements)),sort_keys=True))
