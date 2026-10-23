"""Actual retained-real Maxwell seed/complement application, not collider admission.

Consumes saved incoming/outgoing one-cell histories and their complete original
radial representation. No initial data, inherited quantum reference, cap force
or outgoing boundary condition is selected by this calculation.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

REPO=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(REPO/'src'),str(REPO/'scripts')]
from bhsm_real_full_d5_combined_eta_open_form_20261016 import PHASES,radial_representation,sample_coefficients
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_radial_basis
from bhsm.interface.muon_holomorphic_normal_geometry import holomorphic_geometry_rows
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_parent_maxwell_full_weak import M,full_maxwell_hessian_pairing
from bhsm.interface.muon_primal_electromagnetic_source import higgs_aligned_charge
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.electromagnetic_carrier_original_maxwell import (
    even_angular_space,original_maxwell_covectors,electromagnetic_inclusion,geometric_dual_split,
)


def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_bytes((json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n').encode());temp.replace(path)


def real(value):
    a=np.asarray(value)
    if not np.isfinite(a).all() or np.any(a.imag!=0):raise ValueError('actual real operands required; no imaginary projection')
    return a.real.copy()


def snapshot(phase,t,order,space):
    nodes,weights=np.polynomial.legendre.leggauss(order)
    rho,wr=(nodes+1)*WALL/2,weights*WALL/2
    rep=radial_representation(phase['representation'],rho)
    c,sample=sample_coefficients(phase,t,rep)
    raw=sample['raw_fields']
    geo=holomorphic_geometry_rows(raw[:100],rho,differentiate=False)
    keys=('electric','radial','angular','electric_radial','shift')
    densities=real([[row[k].value for k in keys] for row in geo['rows']])
    a=real(c['gauge_connection_material']);at=real(c['gauge_connection_material_first'][0])
    ar=np.einsum('rjfac,j->rac',rep['gauge_radial_basis'],raw[100:180])
    ar[:,2:]+=M*real(c['mechanical_profile'])[:,2,None,None]
    nh=len(space['weights']);base=lambda x:np.broadcast_to(x[:,None],(order,nh)+x.shape[1:]).copy()
    fields=[base(v) for v in (a,at,ar)]+[np.zeros((order,nh,3,5,4))]
    b,br=trace_enriched_radial_basis(phase['representation'],rho)
    hr,hdr=real(c['intrinsic_H_realified']),real(c['intrinsic_H_realified_first'][0])
    alignment=higgs_aligned_charge(hr[:2]+1j*hr[2:],hdr[:2]+1j*hdr[2:])
    charge=alignment['unit_Tr16_coefficients'];charge_rate=alignment['unit_Tr16_coefficient_rate']
    s=electromagnetic_inclusion(space['mode_coefficients'],charge)
    sd=electromagnetic_inclusion(space['mode_coefficients'],charge_rate)
    e,r,d,_,beta=densities.T;radius=real(c['radius'])
    gt,gr,gs=e*radius**2,r*radius**2,d*radius**2
    g=np.zeros((order,5,5));g[:,0,0]=gt;g[:,1,1]=gr+beta**2*gt
    g[:,0,1]=g[:,1,0]=-beta*gt
    for i in (2,3,4):g[:,i,i]=gs
    # Same positive ADM one-form reference as one_form_point_row, not a
    # Wick identification with physical P_strat and not the velocity Hessian.
    gram=np.einsum('r,ra,rb,rfg->afbg',MAXWELL_TO_CAP*wr,b,b,g).reshape(20,20)
    kinetic=np.kron(np.einsum('r,ra,rb->ab',MAXWELL_TO_CAP*wr*e,b,b),np.eye(4))*np.dot(charge,charge)
    return dict(rho=rho,wr=wr,b=b,br=br,c=c,geo=geo,fields=fields,densities=base(densities),
                s=s,sd=sd,charge=charge,charge_rate=charge_rate,alignment=alignment,gram=gram,kinetic=kinetic,
                time=t,order=order,space=space)


def rows(snap,fields=None):
    return original_maxwell_covectors(*(snap['fields'] if fields is None else fields),snap['densities'],
        snap['wr'],snap['b'],snap['br'],snap['space'],normalization=MAXWELL_TO_CAP)


def direction(snap,radial,mode,*,rate=False):
    a=snap['space'];b,br=snap['b'][:,radial],snap['br'][:,radial]
    charge=snap['charge'];qd=snap['charge_rate']
    v=np.zeros_like(snap['fields'][0]);vt=v.copy();vr=v.copy();ev=np.zeros_like(snap['fields'][3])
    spatial=np.einsum('r,pi,c->rpic',b,a['modes'][:,mode],charge)
    if rate:
        vt[:,:,2:]=spatial
    else:
        v[:,:,2:]=spatial
        vt[:,:,2:]=np.einsum('r,pi,c->rpic',b,a['modes'][:,mode],qd)
        vr[:,:,2:]=np.einsum('r,pi,c->rpic',br,a['modes'][:,mode],charge)
        ev[:,:,:,2:]=np.einsum('r,pji,c->rpjic',b,a['mode_derivatives'][:,:,mode],charge)
    return [v,vt,vr,ev]


def independent_hessian_check(snap,column,left_index,right_direction):
    """Original-row complex derivative versus independent action Hessian."""
    r,f,c,h=np.unravel_index(left_index,(4,5,4,10))
    a=snap['space'];b,br=snap['b'][:,r],snap['br'][:,r]
    left=np.zeros_like(snap['fields'][0]);lt=left.copy();lr=left.copy();le=np.zeros_like(snap['fields'][3])
    left[:,:,f,c]=b[:,None]*a['values'][None,:,h]
    lr[:,:,f,c]=br[:,None]*a['values'][None,:,h]
    le[:,:,:,f,c]=b[:,None,None]*a['derivatives'][None,:,:,h]
    # Recenter independent fields before the analytic owner adds its own
    # mechanical connection. The TOTAL inherited connection appears once.
    keys=('electric','radial','angular','electric_radial','shift','connection_lambda','lambda_tau','lambda_rho')
    coeff={'coordinate_count':1,'rows':[{k:Jet.constant(float(real(row[k].value)),1) for k in keys} for row in snap['geo']['rows']]}
    independent=[v.copy() for v in snap['fields']]
    for index,key,offset in ((0,'connection_lambda',1),(1,'lambda_tau',0),(2,'lambda_rho',0)):
        independent[index][:,:,2:]-=M[None,None]*(np.array([row[key].value.real for row in snap['geo']['rows']])-offset)[:,None,None,None]
    result=full_maxwell_hessian_pairing(coeff,MAXWELL_TO_CAP*snap['wr'],a['weights'],
        **dict(zip(('gauge','gauge_tau','gauge_rho','gauge_angular'),independent)),
        **dict(zip(('left','left_tau','left_rho','left_angular'),(left,lt,lr,le))),
        **dict(zip(('right','right_tau','right_rho','right_angular'),right_direction)),geometric_derivatives=False)
    actual=float(column[left_index]);predicted=result['value']
    return dict(left_index=int(left_index),original_row_derivative=actual,action_hessian=predicted,
        absolute_error=abs(actual-predicted),relative_error=abs(actual-predicted)/max(abs(actual),abs(predicted),1e-300),
        curvature_contact=result['curvature_contact'],fixed_geometry=True,full_outgoing_derivative=False)


def execute(output,orders):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError('preserve evaluated evidence; choose a new run')
    out.mkdir(parents=True)
    space=even_angular_space();haar=even_angular_space(haar_degree=8)
    arrays={};records=[];pins={}
    for side,path in PHASES.items():
        phase=load_profile_preserving_phase(path,repository=REPO);pins.update(phase['input_hashes'])
        midpoint=phase['receipt']['span']/2;table=[];previous=None
        for order in orders:
            snap=snapshot(phase,midpoint,order,space);baseline=rows(snap)
            value=real(baseline['value_rows']).ravel();momentum=real(baseline['rate_rows']).ravel()
            split=geometric_dual_split(value,snap['gram'],snap['s'])
            row=dict(order=order,original_value_max=float(np.max(abs(value))),original_rate_max=float(np.max(abs(momentum))),
                original_Gauss_max=float(np.max(abs(value.reshape(4,5,4,10)[:,0]))),
                seed_value_max=float(np.max(abs(snap['s'].T@value+snap['sd'].T@momentum))),
                complement_value_max=float(np.max(abs(split['complement_covector']))),
                kinetic_eigenvalue_min=float(np.linalg.eigvalsh(snap['kinetic'])[0]))
            if previous is not None:
                row.update(value_difference_to_previous_max=float(np.max(abs(value-previous[0]))),
                    rate_difference_to_previous_max=float(np.max(abs(momentum-previous[1]))),
                    kinetic_difference_to_previous_max=float(np.max(abs(snap['kinetic']-previous[2]))))
            previous=value,momentum,snap['kinetic'];table.append(row)
            print(side,'radial',order,row['original_value_max'],flush=True)
        columns=[];directions=[];checks=[]
        for is_rate in (False,True):
            for radial in range(4):
                for mode in range(4):
                    delta=direction(snap,radial,mode,rate=is_rate)
                    changed=[v.astype(complex)+1e-20j*d for v,d in zip(snap['fields'],delta)]
                    applied=rows(snap,changed)
                    columns.append(np.r_[applied['value_rows'].imag.ravel(),applied['rate_rows'].imag.ravel()]/1e-20)
                    directions.append(delta)
        operator=np.column_stack(columns)
        complement=geometric_dual_split(operator[:800],snap['gram'],snap['s'])['complement_covector']
        for j in (0,2,8,10,16,18,24,26):
            left_index=int(np.argmax(abs(operator[:800,j])))
            checks.append(independent_hessian_check(snap,operator[:800,j],left_index,directions[j]))
        # Independent larger Haar quadrature, same fields and normalization.
        hs=snapshot(phase,midpoint,orders[-1],haar);hb=rows(hs)
        hr=direction(hs,2,2);hp=rows(hs,[v.astype(complex)+1e-20j*d for v,d in zip(hs['fields'],hr)])
        angular_error=max(float(np.max(abs(real(hb['value_rows']).ravel()-value))),
            float(np.max(abs(hp['value_rows'].imag.ravel()/1e-20-operator[:800,10]))))
        # Chronological ORIGINAL residual for the constant complete800 tests.
        lo,hi=sorted((0.,phase['receipt']['span']));qt,wt=np.polynomial.legendre.leggauss(3)
        integrated=np.zeros(800);seed_integrated=np.zeros(16)
        for t,w in zip(lo+(qt+1)*(hi-lo)/2,wt*(hi-lo)/2):
            ts=snapshot(phase,float(t),orders[-1],space);tr=rows(ts)
            v,m=real(tr['value_rows']).ravel(),real(tr['rate_rows']).ravel()
            integrated+=w*v;seed_integrated+=w*(ts['s'].T@v+ts['sd'].T@m)
        faces=[];seed_faces=[]
        for t in (lo,hi):
            fs=snapshot(phase,t,orders[-1],space);fr=rows(fs)
            p=real(fr['rate_rows']).ravel();faces.append(p);seed_faces.append(fs['s'].T@p)
        euler=integrated-faces[1]+faces[0]
        seed_euler=seed_integrated-seed_faces[1]+seed_faces[0]
        arrays.update({side+'_original_value':value,side+'_original_rate':momentum,
            side+'_full1600_by32_local_field_operator':operator,side+'_value_complement_operator':complement,
            side+'_kinetic_gram':snap['kinetic'],side+'_geometric_gram20':snap['gram'],side+'_EM_inclusion':snap['s'],
            side+'_EM_inclusion_rate':snap['sd'],side+'_original_integrated_Euler800':euler,
            side+'_moving_EM_integrated_Euler16':seed_euler,side+'_temporal_face_momenta':np.array(faces)})
        record=dict(side=side,signed_span=phase['receipt']['span'],time=midpoint,radial_refinement=table,
            original_rows=800,independent_local_rate_rows=800,independent_EM_amplitude_rate_directions=32,
            source_profile_count=4,angular_levels=[0,2],angular_points=24,larger_Haar_points=len(haar['weights']),
            angular_original_value_and_column_absolute_difference=angular_error,
            action_Hessian_checks=checks,local_complement_operator_max=float(np.max(abs(complement))),
            integrated_original_Euler_max=float(np.max(abs(euler))),integrated_moving_EM_Euler_max=float(np.max(abs(seed_euler))),
            original_Gauss_integrated_max=float(np.max(abs(euler.reshape(4,5,4,10)[:,0]))),
            H_alignment_residual=snap['alignment']['generator_reconstruction_defect'],
            charge_coefficients=snap['charge'].tolist(),charge_rate_coefficients=snap['charge_rate'].tolist(),
            phase_is_adopted_collider_history=False,full_outgoing_derivative_admitted=False)
        records.append(record)
        _compressed_npz(out/'application.npz',arrays)
        atomic(out/'partial_result.json',{'completed_sides':records,'next_side':None if side=='outgoing' else 'outgoing'})
        print(side,'saved original-action application',flush=True)
    for name,module in list(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and path and Path(path).is_relative_to(REPO):
            pins[Path(path).relative_to(REPO).as_posix()]=sha256(Path(path).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(REPO).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    prep='artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'
    pins[prep]=sha256((REPO/prep).read_bytes()).hexdigest()
    result=dict(classification='EVALUATED_ORIGINAL_MAXWELL_SECTOR_ON_RETAINED_REAL_HISTORY',records=records,
        action='same Lorentzian full-five-component Maxwell; mechanical inherited profile once; MAXWELL_TO_CAP once',
        domain='actual saved one-cell material cap, all four frozen regular/source/wall profiles; full even n0,n2 finite band',
        nonlinear_surface_restrictions_imposed=False,amplitude_and_relative_phase_released_as_original_fields=True,
        fixed_geometry_Higgs_for_field_derivative=True,moving_Higgs_clock_contact_retained=True,
        angular_rule_scope='homogeneous background degree<=2 weak, degree<=4 first derivative; no nonlinear closure claim',
        projection_pairing='owned unreduced positive ADM geometric L2; not Maxwell kinetic inverse or BRST quotient',
        kinetic_pairing='actual spatial EM Gram from electric density; full velocity Hessian diag(0,k,e,e,e)',
        temporal_Euler_identity='integral W(V,Vdot)-[Pi.V]_lo^hi; actual moving EM Vdot retained once',
        supplied_normal_force_added=False,source_and_interface_scope='bulk Maxwell only; scalar/Higgs/matter/native/interface and moving-domain coupled residuals NOT composed',
        physical_radial_convergence_admitted=False,full_physical_outgoing_derivative_at_guard=False,
        matching_guard=2e-10,coupled_corrections=0,fresh_adopted_preparation_Maxwell=None,fresh_adopted_preparation_226_rows=None,
        inherited_quantum_reference_selected=False,physical_packets=None,physical_pole=None,a_mu=None,g_mu=None,total_uncertainty=None,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),input_and_source_sha256=dict(sorted(pins.items())),
        NEXT_OPERAND='Compose the evaluated released-field Maxwell columns with original intrinsic Higgs/matter currents and moving geometry/interface/contact rows on the adopted preparation; solve the inherited retarded initial-boundary problem before a terminal derivative or coupled correction.')
    atomic(out/'result.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--radial-orders',type=int,nargs='+',default=[12,24,48,96])
    args=parser.parse_args();execute(args.output,args.radial_orders)
