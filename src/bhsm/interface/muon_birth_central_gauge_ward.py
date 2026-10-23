"""Literal central gauge germ and its off-shell full-action Ward contact.

For eta(t,rho)=t*g(rho)*H_Y at t=0, delta A_t=-g H_Y,
delta dot A_r=-g_rho H_Y and delta dot H=g(wall)H_Y H.
Both F_tr and D_t H are unchanged.  The vector depends on H, so its
correct Hessian identity is L'' delta+(D delta)^T L'=0.  This does not
identify a physical gauge quotient of a finite temporal discretization.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT,SOURCE_RECEIPTS,correction_representation,_deterministic_npz
from .muon_parent_retarded_hypercharge import WALL,ALPHA,regular_radial_basis
from .muon_parent_maxwell_full_weak import FIELD_ORDER
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_pointwise_full_field_action import pointwise_full_field_action


def represented_central_gauge_germ(raw,representation,power):
    """Two exact radial polynomial intersections, with no chosen field state."""
    if power not in (1,2) or representation['radial_order']!=2 or not representation['include_wall_lift']:
        raise ValueError('this exact application owns the radial2 plus wall-lift representation')
    raw=np.asarray(raw,float)
    if raw.shape!=(228,) or not np.isfinite(raw).all():raise ValueError('same finite raw228 required')
    points=WALL*np.array([.25,.55,.85]);x=points/WALL
    B,_=regular_radial_basis(points,2)
    coefficients=np.linalg.solve(B,x**(ALPHA+power))
    derivative_coefficients=np.linalg.solve(B,(ALPHA+power)/WALL*x**(ALPHA+power-1))
    delta=np.zeros(228);T=np.zeros((228,228))
    for k,label in enumerate(representation['gauge_labels']):
        if label['internal']==3 and label['field']==FIELD_ORDER[0]:delta[100+k]=-coefficients[label['radial']]
        if label['internal']==3 and label['field']==FIELD_ORDER[1]:delta[160+k]=-derivative_coefficients[label['radial']]
    HY=higgs_u2_real_representation()['real_generators'][3]
    delta[224:228]=HY@raw[220:224];T[224:228,220:224]=HY
    grid=representation['rho'];B,D=regular_radial_basis(grid,2);xx=grid/WALL
    return dict(direction=delta,direction_derivative=T,parameter_coefficients=coefficients,
        parameter_radial_derivative_coefficients=derivative_coefficients,
        parameter_value_reconstruction_defect=B@coefficients-xx**(ALPHA+power),
        parameter_derivative_reconstruction_defect=D@coefficients-(ALPHA+power)/WALL*xx**(ALPHA+power-1),
        derivative_in_field_space_defect=B@derivative_coefficients-D@coefficients,
        Higgs_generator=HY,power=power,
        convention='D=partial+A, H transforms gH, A transforms gAg^-1-(dg)g^-1; eta(t0)=0',
        physical_midpoint_null_quotient_claimed=False)


def central_ward_application(raw,representation,action_parameters,*,power,finite_parameter=1e-3):
    """Execute actual nonlinear action, gradient, Hessian and finite gauge ray."""
    germ=represented_central_gauge_germ(raw,representation,power)
    base=pointwise_full_field_action(raw,representation,**action_parameters)
    d,T=germ['direction'],germ['direction_derivative'];G,H=base['raw_gradient'],base['raw_hessian']
    hessian_source=H@d;contact=T.T@G;ward=hessian_source+contact
    values=[pointwise_full_field_action(raw+t*d,representation,**action_parameters)['value'] for t in (-finite_parameter,finite_parameter)]
    return dict(**germ,raw_coefficients=np.asarray(raw),gradient=G,hessian=H,
        action_value=base['value'],finite_parameter=finite_parameter,finite_ray_values=np.asarray(values),
        finite_ray_action_difference=np.asarray(values)-base['value'],first_ward_pairing=float(G@d),
        hessian_gauge_source=hessian_source,gauge_vector_contact=contact,ward_covector=ward,
        hessian_self_pairing=float(d@hessian_source),
        first_ward_relative_defect=float(abs(G@d)/max(np.linalg.norm(G)*np.linalg.norm(d),np.finfo(float).tiny)),
        second_ward_relative_defect=float(np.linalg.norm(ward)/max(np.linalg.norm(hessian_source)+np.linalg.norm(contact),1.)),
        finite_ray_relative_defect=float(np.max(abs(np.asarray(values)-base['value']))/max(abs(base['value']),1.)))


def materialize_central_ward(phase_application,output,*,repository=ROOT):
    root=Path(repository);source=Path(phase_application);source=source if source.is_absolute() else root/source
    out=Path(output)
    if out.exists():raise FileExistsError('preserve original applications')
    b=(source/'result.json').read_bytes();receipt=json.loads(b)
    if sha256((source/'application.npz').read_bytes()).hexdigest()!=receipt['numerical_sha256']:raise ValueError('phase archive hash mismatch')
    rep=correction_representation(radial_points=receipt['radial_points'],radial_order=2,
        cap_points=receipt['cap_points'],include_wall_lift=True,include_scalar_mean=True)
    with np.load(source/'application.npz',allow_pickle=False) as f:
        raw=np.array(f['stage_midpoint_raw'][-1])
    refs=list(SOURCE_RECEIPTS)+['src/bhsm/interface/muon_pointwise_full_field_action.py',
        'src/bhsm/interface/muon_parent_mean_causal_action.py','src/bhsm/interface/muon_material_higgs_gauge_action.py',
        'src/bhsm/interface/muon_intrinsic_higgs_gauge_action.py','src/bhsm/interface/muon_birth_central_gauge_ward.py']
    hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}
    apps=[central_ward_application(raw,rep,receipt['action_parameters'],power=k) for k in (1,2)]
    if hashes!={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:raise RuntimeError('owner changed during application')
    out.mkdir(parents=True);arrays={}
    for k,a in enumerate(apps):
        for key,value in a.items():
            if isinstance(value,np.ndarray):arrays[f'power_{k+1}_{key}']=value
    _deterministic_npz(out/'application.npz',arrays)
    rows=[]
    for a in apps:
        rows.append(dict(power=a['power'],first_pairing=a['first_ward_pairing'],first_relative_defect=a['first_ward_relative_defect'],
            second_covector_norm=float(np.linalg.norm(a['ward_covector'])),second_relative_defect=a['second_ward_relative_defect'],
            hessian_source_norm=float(np.linalg.norm(a['hessian_gauge_source'])),contact_norm=float(np.linalg.norm(a['gauge_vector_contact'])),
            hessian_self_pairing=a['hessian_self_pairing'],finite_ray_relative_defect=a['finite_ray_relative_defect'],
            radial_reconstruction_max=max(float(np.max(abs(a[k]))) for k in (
                'parameter_value_reconstruction_defect','parameter_derivative_reconstruction_defect','derivative_in_field_space_defect'))))
    md=dict(scope='EVALUATED_LITERAL_FULL_ACTION_CENTRAL_GAUGE_WARD_GERM',
        identity='Lprime.delta=0; Lsecond.delta+(Ddelta)^T.Lprime=0; finite gauge ray preserves Ftr and DtH',
        rows=rows,consumed_receipt_sha256=sha256(b).hexdigest(),consumed_coefficients_sha256=receipt['numerical_sha256'],
        input_hashes=hashes,action_parameters=receipt['action_parameters'],
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        domain='retained radial2 plus wall-lift finite action; eta(t0)=0; no gauge quotient of temporal midpoint inferred',
        physical_gauge_quotient_closed=False,physical_formation_closed=False,physical_Pauli_value=False,
        error_scope='binary64 nonlinear action and exact analytic finite action jets; no continuum or physical event claim')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase-application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize_central_ward(a.phase_application,a.output),sort_keys=True))
