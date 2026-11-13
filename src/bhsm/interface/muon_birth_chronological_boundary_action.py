"""Chronological boundary action of the retained full-field phase cells.

The saved midpoint Jacobian determines every x/v/y second derivative of
the same action.  This module applies that action to both temporal faces,
eliminates the literal algebraic multiplier/Gauss block when invertible,
and retains the full two-face relation.  Holding a numerical far face
fixed is an application argument, not a selection of physical E0 data.
The lateral material-normal trial is distinct from the temporal normal.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_attached_phase import load_attached_endpoint
from .muon_birth_phase_continuation import _compressed_npz


def action_hessian_from_midpoint_jacobian(jacobian, dynamic_count, oriented_step):
    """Recover the literal L Hessian; no spectral direction is removed."""
    J = np.asarray(jacobian, float); n = int(dynamic_count); h = float(oriented_step)
    m = len(J)-3*n
    if n < 1 or m < 1 or J.shape != (3*n+m,)*2 or not np.isfinite(J).all() or not np.isfinite(h) or h == 0:
        raise ValueError('complete saved midpoint Jacobian and oriented step required')
    if (np.max(abs(J[:n,:n]-np.eye(n))) != 0 or
        np.max(abs(J[:n,2*n:3*n]+h*np.eye(n))) != 0 or
        np.max(abs(J[n:2*n,n:2*n]-np.eye(n))) != 0 or
        np.max(abs(J[2*n:3*n,n:2*n]+np.eye(n)/2)) != 0):
        raise ValueError('unchanged action-generated midpoint row convention required')
    return np.block([
        [-2*J[n:2*n,:n]/h, -J[n:2*n,2*n:]/h],
        [2*J[2*n:,:n], J[2*n:,2*n:]],
    ])


def discrete_boundary_two_jet(hessian, gradient, step, dynamic_count):
    """Differentiate S_h=h L((x0+x1)/2,(x1-x0)/h,y).

    The order is (x_initial,x_final,y), and h is positive chronological
    coordinate time.  Both outward temporal contacts are present once.
    """
    H = np.asarray(hessian, float); g = np.asarray(gradient, float)
    n = int(dynamic_count); h = float(step); m = len(g)-2*n
    if n < 1 or m < 1 or H.shape != (len(g),)*2 or not np.isfinite(H).all() or not np.isfinite(g).all() or h <= 0:
        raise ValueError('same finite action two-jet and positive time step required')
    T = np.zeros_like(H)
    T[:n,:n] = np.eye(n)/2; T[:n,n:2*n] = np.eye(n)/2
    T[n:2*n,:n] = -np.eye(n)/h; T[n:2*n,n:2*n] = np.eye(n)/h
    T[2*n:,2*n:] = np.eye(m)
    return dict(coordinate_map=T, gradient=h*T.T@g, hessian=h*T.T@H@T,
        temporal_orientation='initial face -Pi+h L_x/2; final face +Pi+h L_x/2',
        all_algebraic_rows_retained=True)


def algebraic_boundary_response(boundary_hessian, dynamic_count, boundary_directions=None):
    """Apply all algebraic rows, retaining the two-face boundary graph.

    dy=-K_yy^{-1} K_yE dx_E is solved, not formed as an explicit inverse.
    No far-face condition is introduced by the Schur complement itself.
    """
    K = np.asarray(boundary_hessian, float); n = int(dynamic_count); e = 2*n
    if n < 1 or K.ndim != 2 or K.shape[0] != K.shape[1] or len(K) <= e or not np.isfinite(K).all():
        raise ValueError('complete two-face/algebraic action Hessian required')
    A, B = K[e:,e:], K[e:,:e]
    row = np.max(abs(A), axis=1)
    if np.any(row == 0): raise np.linalg.LinAlgError('literal algebraic row has no coefficient')
    s = 1/np.sqrt(row); balanced = s[:,None]*A*s[None,:]
    X = s[:,None]*np.linalg.solve(balanced, s[:,None]*B)
    D = K[:e,:e]-K[:e,e:]@X
    directions = np.eye(e) if boundary_directions is None else np.asarray(boundary_directions, float)
    if directions.ndim != 2 or directions.shape[0] != e or not np.isfinite(directions).all():
        raise ValueError('explicit same two-face trace directions required')
    Y = -X@directions
    residual = A@Y+B@directions
    return dict(DtN=D, algebraic_response_map=-X, boundary_directions=directions,
        algebraic_response=Y, boundary_cotangent_response=D@directions,
        algebraic_residual=residual, Schur_symmetry_defect=D-D.T,
        balanced_condition_number=float(np.linalg.cond(balanced)),
        full_algebraic_dimension=len(A), regularizing_shift=0.,
        spectral_directions_removed=0, far_face_fixed_by_this_operation=False)


def assemble_chronological_chain(cell_hessians, cell_gradients, dynamic_count):
    """Assemble interior node cotangents and all y rows without a quotient."""
    cells = np.asarray(cell_hessians, float); gradients = np.asarray(cell_gradients, float)
    n = int(dynamic_count); steps = len(cells); m = cells.shape[1]-2*n
    if steps < 1 or m < 1 or cells.shape != (steps,2*n+m,2*n+m) or gradients.shape != (steps,2*n+m):
        raise ValueError('complete chronological cell two-jets required')
    dim = (steps+1)*n+steps*m; K = np.zeros((dim,dim)); g = np.zeros(dim)
    for k, (a,b) in enumerate(zip(cells,gradients)):
        indices = np.r_[np.arange(k*n,(k+2)*n), (steps+1)*n+k*m+np.arange(m)]
        K[np.ix_(indices,indices)] += a; g[indices] += b
    E = np.r_[np.arange(n),steps*n+np.arange(n)]
    I = np.r_[np.arange(n,steps*n),np.arange((steps+1)*n,dim)]
    A = K[np.ix_(I,I)]; row = np.max(abs(A),axis=1)
    s = 1/np.sqrt(np.maximum(row,np.finfo(float).tiny))
    sv = np.linalg.svd(s[:,None]*A*s[None,:],compute_uv=False)
    return dict(hessian=K, gradient=g, endpoint_indices=E, interior_indices=I,
        interior_singular_values=sv, interior_row_scale=s,
        balanced_condition_number=float(sv[0]/sv[-1]),
        literal_interior_residual=g[I], all_cell_Gauss_and_multiplier_rows_retained=True,
        no_interior_eigenvector_deleted=True)


def _npy_hash(value):
    stream=BytesIO(); np.lib.format.write_array(stream,np.asarray(value),allow_pickle=False)
    return sha256(stream.getvalue()).hexdigest()


def _read_phase(directory):
    """Read either the original archive or its bit-identical stage package."""
    p=Path(directory); rb=(p/'result.json').read_bytes(); outer=json.loads(rb)
    refs={p/'result.json':sha256(rb).hexdigest()}
    if 'array_inventory' in outer:
        receipt=outer['original_receipt']; pieces={}
        for name,rec in outer['pieces'].items():
            target=p/name; data=target.read_bytes()
            if sha256(data).hexdigest()!=rec['sha256']: raise ValueError('stage package changed: '+name)
            refs[target]=rec['sha256']
            with np.load(target,allow_pickle=False) as f:pieces[name]={k:f[k] for k in f.files}
        arrays={}
        for name,row in outer['array_inventory'].items():
            array=(np.stack([pieces[file][name] for file in row['storage']]) if row['operation']=='stack'
                   else pieces[row['storage'][0]][name])
            if _npy_hash(array)!=row['npy_sha256']: raise ValueError('packaged array changed: '+name)
            arrays[name]=array
        receipt_hash=outer['original_receipt_sha256']
    else:
        receipt=outer; data=(p/'application.npz').read_bytes()
        if sha256(data).hexdigest()!=receipt['numerical_sha256']: raise ValueError('phase archive changed')
        refs[p/'application.npz']=receipt['numerical_sha256']
        with np.load(p/'application.npz',allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
        receipt_hash=sha256(rb).hexdigest()
    return receipt, arrays, refs, receipt_hash


def retained_chronological_boundary_application(phase_directory, *, repository=ROOT):
    root=Path(repository); path=Path(phase_directory); path=path if path.is_absolute() else root/path
    receipt, arrays, refs, receipt_hash=_read_phase(path)
    steps=receipt['steps']; n=receipt['dynamic_count']; m=receipt['algebraic_count']; stored_h=receipt['span']/steps
    if receipt['completed_steps']!=steps or any(s['status']!='REPRESENTED_PHASE_TOLERANCE' for s in receipt['stages']):
        raise ValueError('complete converged phase cells required')
    for name,digest in receipt['input_hashes'].items():
        if sha256((root/name).read_bytes()).hexdigest()!=digest: raise ValueError('consumed action owner changed: '+name)
    loaded=load_attached_endpoint(receipt['consumed_paired_endpoint_path'],side=receipt['side'],repository=root,
        radial_points=receipt['radial_points'],cap_points=receipt['cap_points'])
    order=list(range(steps)) if stored_h>0 else list(range(steps-1,-1,-1))
    h=abs(stored_h); LH=[]; Lg=[]; cellH=[]; cellg=[]; responses=[]; contacts=[]
    for k in order:
        J=arrays['stage_jacobian'][k]
        H=action_hessian_from_midpoint_jacobian(J,n,stored_h)
        initial,final=arrays['stage_initial_face'][k],arrays['stage_final_face'][k]
        g=np.r_[(initial+final)/stored_h,(final-initial)/2,arrays['stage_residual'][k,3*n:]]
        boundary=discrete_boundary_two_jet(H,g,h,n)
        response=algebraic_boundary_response(boundary['hessian'],n)
        expected=np.r_[initial,final] if stored_h>0 else np.r_[-final,-initial]
        contacts.append(boundary['gradient'][:2*n]-expected)
        LH.append(H); Lg.append(g); cellH.append(boundary['hessian']); cellg.append(boundary['gradient']); responses.append(response)
    chain=assemble_chronological_chain(cellH,cellg,n)
    birth_is_final=receipt['side']=='incoming'; adjacent=steps-1 if birth_is_final else 0
    # n=0 retained birth endpoints: dn is one proper lateral wall displacement
    # at fixed q.  No temporal-normal or physical mode identification follows.
    birth_face=1 if birth_is_final else 0; d=np.zeros((2*n,1)); d[birth_face*n+37]=1.
    r=responses[adjacent]; normal=algebraic_boundary_response(cellH[adjacent],n,d)
    chain_birth=chain['endpoint_indices'][n:] if birth_is_final else chain['endpoint_indices'][:n]
    p=chain['gradient'][chain_birth]
    return dict(receipt=receipt,receipt_sha256=receipt_hash,representation=loaded['representation'],input_refs=refs,
        chronological_cell_order=np.array(order),action_hessians=np.array(LH),action_gradients=np.array(Lg),
        cell_hessians=np.array(cellH),cell_gradients=np.array(cellg),
        cell_DtN=np.array([a['DtN'] for a in responses]),
        cell_algebraic_response_map=np.array([a['algebraic_response_map'] for a in responses]),
        cell_algebraic_residual=np.array([a['algebraic_residual'] for a in responses]),
        cell_algebraic_conditions=np.array([a['balanced_condition_number'] for a in responses]),
        temporal_contact_reconstruction=np.array(contacts), chain=chain,
        birth_normal_direction=d[:,0], birth_normal_response=normal,
        birth_cotangent=p, birth_normal_cotangent=float(p[37]),
        birth_normal_fixed_far_face_contraction=float(d[:,0]@r['DtN']@d[:,0]),
        far_face_response_for_unit_birth_normal=(r['DtN']@d[:,0])[:n] if birth_is_final else (r['DtN']@d[:,0])[n:],
        raw_chronological_midpoints=arrays['stage_midpoint_raw'][order],
        lateral_wall_conormals=arrays['material_wall_conormals'][order],
        signed_step=h, stored_oriented_step=stored_h,
        normal_scope='unit proper lateral wall trial at retained n=0 birth and fixed geometry; not temporal normal, selected psi or full formation',
        far_face_scope='complete two-face graph exported; fixing a far trace is a numerical argument, not physical E0/finalchild data',
        event_drive_scope='incoming-final boundary action contribution; no eventdrive equated to resistance; global constrained domain reduction remains explicit')


def materialize_chronological_boundary_action(phase_directory, output, *, repository=ROOT):
    root=Path(repository); out=Path(output); out=out if out.is_absolute() else root/out
    if out.exists(): raise FileExistsError('preserve earlier applications')
    a=retained_chronological_boundary_application(phase_directory,repository=root); chain=a['chain']; normal=a['birth_normal_response']
    arrays={k:a[k] for k in ('chronological_cell_order','action_hessians','action_gradients','cell_hessians','cell_gradients',
        'cell_DtN','cell_algebraic_response_map','cell_algebraic_residual','cell_algebraic_conditions',
        'temporal_contact_reconstruction','birth_normal_direction','birth_cotangent','raw_chronological_midpoints','lateral_wall_conormals')}
    arrays.update(chain_hessian=chain['hessian'],chain_gradient=chain['gradient'],chain_endpoint_indices=chain['endpoint_indices'],
        chain_interior_indices=chain['interior_indices'],chain_interior_singular_values=chain['interior_singular_values'],
        chain_interior_row_scale=chain['interior_row_scale'],chain_literal_interior_residual=chain['literal_interior_residual'],
        birth_normal_algebraic_response=normal['algebraic_response'],birth_normal_boundary_response=normal['boundary_cotangent_response'])
    out.mkdir(parents=True); _compressed_npz(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>10*1024**2: raise ValueError('split complete arrays before publication')
    refs=dict(a['receipt']['input_hashes']); refs.update({p.relative_to(root).as_posix():h for p,h in a['input_refs'].items()})
    for name in ('src/bhsm/interface/muon_birth_chronological_boundary_action.py','src/bhsm/interface/muon_birth_attached_phase.py',
                 'src/bhsm/interface/muon_birth_phase_continuation.py','src/bhsm/interface/muon_birth_coupled_primal_midpoint.py'):
        refs[name]=sha256((root/name).read_bytes()).hexdigest()
    r=a['receipt']; md=dict(scope='EVALUATED_CHRONOLOGICAL_FULL_FIELD_BOUNDARY_ACTION',side=r['side'],steps=r['steps'],
        dynamic_count=r['dynamic_count'],algebraic_count=r['algebraic_count'],signed_step=a['signed_step'],stored_oriented_step=a['stored_oriented_step'],
        chronological_cell_order=a['chronological_cell_order'].tolist(),input_hashes=refs,consumed_phase_receipt_sha256=a['receipt_sha256'],
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),action_parameters=r['action_parameters'],
        algebraic_condition_numbers=a['cell_algebraic_conditions'].tolist(),
        algebraic_response_residual_max=float(np.max(abs(a['cell_algebraic_residual']))),
        temporal_contact_reconstruction_max=float(np.max(abs(a['temporal_contact_reconstruction']))),
        birth_normal_cotangent=a['birth_normal_cotangent'],birth_normal_fixed_far_face_contraction=a['birth_normal_fixed_far_face_contraction'],
        birth_normal_all_field_response_norm=float(np.linalg.norm(normal['boundary_cotangent_response'])),
        birth_normal_algebraic_response_norm=float(np.linalg.norm(normal['algebraic_response'])),
        chain_interior_condition_number=chain['balanced_condition_number'],
        chain_interior_source_norm=float(np.linalg.norm(chain['literal_interior_residual'])),
        full_chain_interior_inverse_claimed=False,all_y_Gauss_multiplier_contacts_retained=True,
        true_Lyy_retained=True,regularizing_shift=0.,spectral_directions_removed=0,
        normal_scope=a['normal_scope'],far_face_scope=a['far_face_scope'],event_drive_scope=a['event_drive_scope'],
        temporal_and_lateral_normals_distinguished=True,physical_event_drive_selected=False,physical_inertia_or_cutoff_selected=False,
        physical_formation_closed=False,physical_native_Pauli_value=False,
        error_scope='binary64 exact-saved variational Jacobian reconstruction and direct algebraic solves; no action-rounding/continuum/physical-domain enclosure')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(); print(json.dumps(materialize_chronological_boundary_action(args.phase_directory,args.output),sort_keys=True))
