"""Materialize the executed E1 compatibility/formation and trace application."""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups,owners,pin
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_event_bundle_incidence import original_event_coefficients,wall_event_incidence
from bhsm.interface.muon_d5_event_formation_constraints import corrected_original_event_source_directions
from bhsm.interface.muon_d5_affine_event_trace_application import parent_trace_coordinates
from bhsm.interface.muon_d5_event_normal_source_application import evaluate_event_normal_source
from bhsm.interface.muon_d5_event_consumed_source_refinement import evaluate_consumed_source_refinement
from bhsm.interface.muon_d5_event_represented_radial_source import evaluate_represented_radial_source
from bhsm.interface.muon_d5_temporal_bulk_refinement import evaluate_refined_field,time_evaluation_matrix
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.retained_response.finite_time_response import write_npz

BASE=ROOT/'artifacts/muon_d5_event_matching_20261019'

def dump(path,value):path.write_bytes((json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())

def verified_pins(pins):
    """Only prove exact text normalization/additional returned frame metadata."""
    compatibility={}
    for rel,expected in pins.items():
        p=ROOT/rel;b=p.read_bytes()
        if sha256(b).hexdigest()==expected:continue
        if p.suffix not in ('.py','.json','.txt','.md'):
            raise ValueError('binary application input changed: '+rel)
        lf=b.replace(b'\r\n',b'\n');versions=[lf,lf.replace(b'\n',b'\r\n')]
        reason='LF/CRLF normalization only'
        if rel=='src/bhsm/interface/muon_d5_event_bundle_incidence.py':
            old=lf.replace(b"        parent_spin_boost_first128=bp['spin_boost_first128'],\n",b'')
            old=old.replace(b"        child_spin_boost_first128=bc['spin_boost_first128'],\n",b'')
            versions.extend([old,old.replace(b'\n',b'\r\n')])
            reason='only returned existing material-frame first arrays added; numerical equations unchanged; exact previous bytes reconstructed'
        if not any(sha256(v).hexdigest()==expected for v in versions):
            raise ValueError('saved application owner changed: '+rel)
        compatibility[rel]=dict(saved_sha256=expected,current_sha256=pin(p),verified_change=reason)
    return compatibility

def cached(folder):
    folder=Path(folder);r=json.loads((folder/'result.json').read_bytes())
    p=folder/'application.npz'
    expected=r.get('numerical_sha256',r.get('arrays',{}).get('sha256'))
    if pin(p)!=expected:raise ValueError('saved numerical application changed '+str(folder))
    with np.load(p,allow_pickle=False) as z:a={k:z[k].copy(order='K') for k in z.files}
    return a,r,{q.relative_to(ROOT).as_posix():pin(q) for q in (p,folder/'result.json')},verified_pins(r['input_sha256'])

def run(output):
    output=Path(output).resolve()
    if output.exists():raise FileExistsError('preserve prior checkpoints')
    output.mkdir(parents=True)
    formation,fr,fp,compat=cached(BASE/'formation_core')
    affine,ar,ap,c=cached(BASE/'affine_core');compat.update(c)
    coarse_affine,car,cap,c=cached(BASE/'affine6_core');compat.update(c)
    new,nr,npins,c=cached(BASE/'source_core');compat.update(c)
    new6,n6r,n6pins,c=cached(BASE/'source6_core');compat.update(c)
    literal2,l2r,l2pins,c=cached(BASE/'consistent_source2_core');compat.update(c)
    literal4,l4r,l4pins,c=cached(BASE/'consistent_source4_core');compat.update(c)
    represented,rr,rrpins,c=cached(BASE/'represented_source_core');compat.update(c)
    prior=ROOT/'artifacts/muon_d5_valid_domain_application_20261019'
    pc=json.loads((prior/'run_3/core_result.json').read_bytes());saved=load_groups(prior/'run_3',pc['archives'])
    c6=json.loads((prior/'temporal6_run_1/core_result.json').read_bytes());saved6=load_groups(prior/'temporal6_run_1',c6['archives'])
    _,hist,ip=inputs();hp,pr=recovered_export_history(ROOT,'incoming',*hist['incoming'])
    hc,cr=recovered_export_history(ROOT,'outgoing',*hist['outgoing'])
    for value_cache in (saved,saved6):
        original=np.array([hp.value(t)[0] for t in value_cache['times']])
        if not np.array_equal(original,value_cache['raw268_nodes']):
            raise ValueError('original value history identity changed')
    for source_cache in (literal2,literal4,represented):
        if not np.array_equal(source_cache['times'],saved['times']):
            raise ValueError('consumed source/value time identities changed')
        if not np.array_equal(source_cache['source_Xi268_nodes'],new['source_Xi268_nodes']):
            raise ValueError('source direction identity changed')
    delta=formation['provisional_raw_normal_source_correction']
    p=original_event_coefficients(hp,0.,[WALL],side='parent',
        directions=corrected_original_event_source_directions(hp,delta[0],side='parent'))
    cc=original_event_coefficients(hc,0.,[WALL],side='child',
        directions=corrected_original_event_source_directions(hc,delta[1],side='child'))
    wall,wr=wall_event_incidence(p,cc)
    S=np.kron(np.eye(3),wall['parent_spin_boost128'])
    Sx=np.kron(np.eye(3),wall['parent_spin_boost_first128'])
    St=affine['parent_material_spin_time384']
    output_arrays={};reports={};comparison={}
    maxabs=lambda a:float(np.max(abs(a)))
    for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
        raw=evaluate_refined_field(saved,label,[0.],[WALL])
        raw.update(evaluate_represented_radial_source(represented,label,[0.],[WALL]))
        q=parent_trace_coordinates({k:v[0,0] for k,v in raw.items()},S,Sx,St)
        legacy=dict(raw)
        legacy.update(evaluate_event_normal_source(new,label,[0.],[WALL]))
        qlegacy=parent_trace_coordinates({k:v[0,0] for k,v in legacy.items()},S,Sx,St)
        raw6=evaluate_refined_field(saved6,label,[0.],[WALL])
        raw6.update(evaluate_event_normal_source(new6,label,[0.],[WALL]))
        q6=parent_trace_coordinates({k:v[0,0] for k,v in raw6.items()},S,Sx,St)
        for k in ('value','source','time','radial_fixed_frame',
            'ambient_time_source_in_frame','ambient_radial_source_in_frame'):
            output_arrays[label+'_new_partial_Xi_'+k]=q[k]
            output_arrays[label+'_same_legacy_source_temporal6_minus10_'+k]=q6[k]-qlegacy[k]
            output_arrays[label+'_represented_source_minus_legacy10_'+k]=q[k]-qlegacy[k]
        reports[label]=dict(partial_event_source_rhs_norm=float(np.linalg.norm(q['source'])),
            original_Xi_source_rhs_norm=float(np.linalg.norm(affine[label+'_source'])),
            normal_source_change_norm=float(np.linalg.norm(q['source']-affine[label+'_source'])),
            parent_reconstruction_max=maxabs(q['parent_reconstruction_rows']),
            after_transported_child_coordinate_row_max=maxabs(q['value']-q['value']),
            after_transported_child_partial_source_row_max=maxabs(q['source']-q['source']),
            physical_child_or_event_residual=None)
        comparison[label+'_legacy_temporal6_minus10']={k:maxabs(q6[k]-qlegacy[k]) for k in ('value','source','time','radial_fixed_frame',
            'ambient_time_source_in_frame','ambient_radial_source_in_frame')}
        comparison[label+'_represented_source_minus_legacy10']={k:maxabs(q[k]-qlegacy[k]) for k in (
            'source','ambient_time_source_in_frame','ambient_radial_source_in_frame')}
        literal_coordinates=[]
        for source_arrays in (literal2,literal4):
            literal_raw=dict(raw)
            literal_raw.update(evaluate_consumed_source_refinement(source_arrays,label,[0.],[WALL]))
            literal_coordinates.append(parent_trace_coordinates({k:v[0,0] for k,v in literal_raw.items()},S,Sx,St))
        comparison[label+'_ideal_source_radial4_minus2']={}
        for key in ('source','ambient_time_source_in_frame','ambient_radial_source_in_frame'):
            difference=literal_coordinates[1][key]-literal_coordinates[0][key]
            output_arrays[label+'_ideal_source_radial4_minus2_'+key]=difference
            comparison[label+'_ideal_source_radial4_minus2'][key]=maxabs(difference)
    # Every coarse homogeneous coefficient is embedded in the fine time
    # representation. New high-time coordinates stay separate and free.
    embed=time_evaluation_matrix(saved6['times'],saved['times'])
    for side in ('plus','minus'):
        for key in ('value','source','time','radial_fixed_frame'):
            fine=affine[side+'_homogeneous_'+key].reshape(384,len(saved['times']),366)
            embedded=np.einsum('dnj,nm->dmj',fine,embed).reshape(384,-1)
            difference=coarse_affine[side+'_homogeneous_'+key]-embedded
            output_arrays[side+'_old_Xi_common6_h_difference_'+key]=difference
            comparison[side+'_homogeneous_old_Xi_'+key]=maxabs(difference)
        # At the wall the value fundamental is I for every background. Its
        # parameter derivative is zero; Q_source is an evaluated vertex.
        # This supplies the wall source coefficient, not a bulk h source.
        Qx=represented['wall_'+side+'_complement_basis_source'][-1]
        direct=np.zeros((384,len(saved['times'])*366),complex)
        direct[:,-366:]=np.linalg.solve(S,Qx)
        qvalue=affine[side+'_homogeneous_value']
        direct-=np.linalg.solve(S,Sx)@qvalue
        output_arrays[side+'_new_partial_Xi_h_wall_source']=direct
        reports[side+'_homogeneous']=dict(h_coordinates=366*len(saved['times']),
            wall_source_coefficient_norm=float(np.linalg.norm(direct)),
            new_bulk_source_response=None,new_mixed_gradient_response=None,
            h_values_assigned=False,h_source_values_assigned=False)
    output_arrays.update({'corrected_wall_'+k:v for k,v in wall.items()})
    write_npz(output/'application.npz',output_arrays)
    used={**fp,**ap,**cap,**npins,**n6pins,**l2pins,**l4pins,**rrpins,**ip,**pr['input_sha256'],**cr['input_sha256'],**owners(),
        Path(__file__).relative_to(ROOT).as_posix():pin(Path(__file__))}
    for folder,core in ((prior/'run_3',pc),(prior/'temporal6_run_1',c6)):
        used[(folder/'core_result.json').relative_to(ROOT).as_posix()]=pin(folder/'core_result.json')
        used.update({(folder/name).relative_to(ROOT).as_posix():md['sha256'] for name,md in core['archives'].items()})
    result=dict(schema='bhsm.d5-event-matching-application.v1',parent_head='bdd993d9afe33f8cbe3181ba452ffac5e5d85976',
        input_sha256=used,saved_source_compatibility=compat,
        arrays=dict(sha256=pin(output/'application.npz'),keys=sorted(output_arrays)),
        formation_tangency=fr,
        formation_tangency_norm_scope='max absolute unscaled seven audit components: radius squared and Higgs2/SM16 trG,trG2,detG; mixed invariant powers and representation duplicates; not the original physical admission norm',
        original_physical_admission_norm_residual=None,
        affine_event=ar['report'],new_source_application=nr,new_source6_application=n6r,
        consistent_source2_application=l2r,consistent_source4_application=l4r,
        represented_source_application=rr,
        corrected_wall_equations=wr,actual_partial_event_source_consumption=reports,
        finite_representation_comparison=comparison,
        error_propagation='deltaE=deltaGamma_child-deltaU*Gamma_parent-U*(deltaGamma_parent+dGamma_parent*totaldeltaF_B); finite value/source/gradient differences saved as coefficients, not continuum bounds',
        old_full_family_nonpasses_preserved=dict(unit_bulk=.0002923620989305011,unit_source=.01024044836655653,
            old_time_LR_bulk=5.240843503598206e-10,old_time_LR_source=4.4019543566802504e-10),
        physical_event_residual=None,remaining_parent_homogeneous_coordinates=3660,
        normalized_physical_child_reconstructed=False,base_map_selected=False,middle_lift_selected=False,
        physical_outer_residual=None,normal_profile_normalization=None,full_formation_residual=None,
        complete_physical_derivative=False,physical_guard=2e-10,physical_admission=False,
        original_value_history_bitwise_identical=True,source_direction_bitwise_identical=True,
        local_native_accounting_changed=False,background_or_value_response_recomputed=False,
        NEXT_OPERAND='use the retained event compatibility/source rows with the full worldvolume, initial angular/bundle, outer and independent normal equations; resolve the corrected child-domain, field/born-reference variations and multiplier curvature; use consumed coefficients and original-rho source residuals to control further discretization before physical formation admission')
    dump(output/'result.json',result)
    print(json.dumps(dict(stage='EVENT_MATCHING_SAVED',sha256=pin(output/'result.json'),partial_event=reports,
        physical_admission=False,formation_before=fr['supplied_Xi_constraint_before_max'],formation_after=fr['original_callback_corrected_Xi_constraint_max'])),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.output)
