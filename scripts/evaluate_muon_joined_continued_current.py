"""Apply the actual finite two-arm canonical current boundary return."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_joined_continued_current import join_current_coefficients,joined_squared_current_application
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output,*,input_folder=Path('artifacts/muon_continued_current_factor_20261011/run_1'),refinements=(16,32,64)):
    out=ROOT/output;folder=ROOT/input_folder
    if out.exists():raise FileExistsError('preserve prior boundary-return applications')
    md=json.loads((folder/'result.json').read_bytes());refs=dict(md['input_hashes'])
    refs[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256((folder/'result.json').read_bytes()).hexdigest()
    pending=[];records=[];previous=None
    for steps in refinements:
        inputs=[]
        for side in('incoming','outgoing'):
            p=folder/f'{side}_{steps}.npz';h=md['array_archives'][p.name]['sha256']
            if sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('actual coefficient export changed')
            refs[p.relative_to(ROOT).as_posix()]=h
            with np.load(p,allow_pickle=False)as a:inputs.append({k:a[k].copy()for k in a.files})
        # This is the already-represented homogeneous common canonical
        # Cauchy frame, not a newly chosen full worldvolume F_B/U transport.
        c=join_current_coefficients(*inputs,np.eye(6));a=joined_squared_current_application(c)
        arrays={k:v for k,v in c.items()if isinstance(v,np.ndarray)}
        arrays.update({k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        pending.append((f'joined_{steps}.npz',arrays))
        row=dict(steps_per_arm=steps,first_order_identity_max=a['first_order_identity_max'],
            boundary_reconstruction_identity_max=a['boundary_reconstruction_identity_max'],
            current_source_adjoint_max=a['current_source_adjoint_max'],
            current_boundary_decomposition_max=a['current_boundary_decomposition_max'],
            original_first_order_max=float(np.max(abs(a['original_first_order_rows']))),
            original_squared_birth_dual_max=float(np.max(abs(a['squared_birth_dual_row']))),
            natural_final_face_max=float(np.max(abs(a['squared_natural_final_face_row']))),
            actual_birth_trace_norm=float(np.linalg.norm(a['actual_birth_canonical_trace'])),
            actual_free_final_trace_norm=float(np.linalg.norm(a['boundary_final_trace'])),
            total_current_norm=float(np.linalg.norm(a['current_total'])),
            Dirichlet_interior_current_norm=float(np.linalg.norm(a['current_Dirichlet_interior'])),
            boundary_return_current_norm=float(np.linalg.norm(a['current_boundary_return'])),
            refinement_difference=None if previous is None else float(np.linalg.norm(a['current_total']-previous)))
        previous=a['current_total'];records.append(row)
        print(json.dumps(dict(stage='actual_joined_current_boundary_return',**row),sort_keys=True),flush=True)
    for p in('src/bhsm/interface/muon_joined_continued_current.py','tests/test_muon_joined_continued_current.py',Path(__file__).relative_to(ROOT).as_posix()):refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed source changed')
    out.mkdir(parents=True);files={}
    for name,arrays in pending:
        p=out/name;_compressed_npz(p,arrays);files[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    r=dict(classification='EVALUATED_JOINED_CANONICAL_CURRENT_WITH_EXACT_FINITE_BOUNDARY_RETURN',
        input_hashes=refs,array_archives=files,records=records,
        common_birth_frame='conditional represented homogeneous canonical C6 frame T=I; all body coefficients/connection images retained',
        trace_rule='one birth coordinate; chi_child_initial=T chi_parent_final, canonical current Gram preserved',
        squared_domain='initial-zero incoming inverse and free outgoing final face; action-generated adjoint birth/final rows retained',
        boundary_return='K_II inverse plus rank6 Poisson/Schur correction from SAME K=A†G_source A',
        numerical_far_faces_identified_with_E0_or_infinity=False,full_worldvolume_transport_or_exterior_completion_claimed=False,
        Y0_is_operator_Taylor_coefficient_not_physical_H0=True,
        finite_c_regulator_or_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 same-domain source/dual and boundary Schur identities; temporal refinements are diagnostics, not continuum/exterior/finite-c or physical Pauli enclosures')
    (out/'result.json').write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--input-folder',type=Path,default=Path('artifacts/muon_continued_current_factor_20261011/run_1'))
    a=p.parse_args();print(json.dumps(materialize(a.output,input_folder=a.input_folder),sort_keys=True))
