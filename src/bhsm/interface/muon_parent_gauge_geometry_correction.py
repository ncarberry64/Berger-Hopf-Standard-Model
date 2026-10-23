"""Finite common-vector correction of the retained cap/Maxwell action.

The local time interval and Galerkin orders are numerical representation
parameters.  The affine reference reproduces the saved E1 value and first
jet; it is an initial iterate, not a recovered history or acceleration.
Compact temporal/radial corrections preserve reference traces.  Natural
event cotangents are exported separately; no event generating term is made
up.  All five gauge components and all retained geometry multipliers enter.

Independent gauge fields contribute S_Maxwell(Abar+a)-S_Maxwell(Abar): the
mechanical curvature is already in the parent R8.  This is an evaluated
classical sector correction, not the interacting/native stationary base.
The reached intrinsic-H vacuum and surface cotangents remain explicit
parameter sensitivities; a physical common energy scale is not assigned.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

from .muon_birth_candidate_geometry_action import ROOT, RESET_RECEIPT, STATE_SOURCE
from .muon_moving_geometric_action import retained_state, moving_cap_action_jet
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_intrinsic_higgs_gauge_action import intrinsic_higgs_gauge_action_jet,higgs_u2_real_representation
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import (
    FIELD_ORDER, background_subtracted_maxwell_action_jet,
    full_maxwell_weak_geometric_jets, full_maxwell_gauge_hessian_matrix,
    M, _bracket,
)
from .muon_parent_retarded_hypercharge import SOURCE, WALL, regular_radial_basis, _deterministic_npz
from .muon_parent_maxwell_background_euler import angular_ward_probe


ORBIT_VOLUME_SQUARED=(2*np.pi**2)**2
MECHANICAL_EMBEDDING_INDEX=8.
MAXWELL_TO_CAP=1/(MECHANICAL_EMBEDDING_INDEX*ORBIT_VOLUME_SQUARED)
SCALAR_MATCHING_INPUT='artifacts/muon_calibrated_pauli_20261009/inputs.json'
CURRENT_DECAY_MATCHING='artifacts/muon_calibrated_weak_decay_20261010/run_1/weak_decay.json'
SOURCE_RECEIPTS=(STATE_SOURCE,RESET_RECEIPT,SOURCE,
    'src/bhsm/interface/muon_parent_gauge_geometry_correction.py',
    'src/bhsm/interface/muon_parent_maxwell_full_weak.py',
    'src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',
    'src/bhsm/interface/muon_parent_maxwell_background_euler.py',
    'src/bhsm/interface/muon_parent_retarded_hypercharge.py',
    'src/bhsm/interface/muon_moving_geometric_action.py',
    'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
    'src/bhsm/interface/muon_intrinsic_higgs_gauge_action.py',
    SCALAR_MATCHING_INPUT,CURRENT_DECAY_MATCHING,
    'src/bhsm/interface/aether_lorentzian_child_galerkin_v15_44.py',
    'src/bhsm/interface/aether_diagonal_sp1_m4_attachment_v15_50.py')


def retained_scalar_matching_coefficients(repository=ROOT):
    """Current tree coefficient matching; the common action unit is unknown."""
    root=Path(repository)
    config=json.loads((root/SCALAR_MATCHING_INPUT).read_text(encoding='utf8'))
    decay=json.loads((root/CURRENT_DECAY_MATCHING).read_text(encoding='utf8'))
    gf=float(decay['decay_rematching']['G_F_GeV_minus2'])
    mh=float(config['selected_consumer_values']['m_h_GeV']['value'])
    return dict(lambda_H=gf*mh*mh/np.sqrt(2),nu_squared_GeV_squared=1/(2*np.sqrt(2)*gf),
        G_F_GeV_minus2=gf,E_kappa_GeV=None,
        matching_scope='calibrated tree coefficient approximation; not native matching or an E1 condition')


def compact_temporal_basis(time,length):
    """A real trial with value and first derivative zero at both endpoints."""
    u=(np.asarray(time,float)+float(length))/float(length)
    if length<=0 or np.any(u<0) or np.any(u>1):
        raise ValueError('positive explicit local representation interval required')
    return 16*u*u*(1-u)**2,32*u*(1-u)*(1-2*u)/length


def correction_representation(*,length=1e-3,time_points=4,radial_points=24,
                              radial_order=2,cap_points=24,include_wall_lift=False,
                              include_scalar_mean=False,repository=ROOT):
    """Interior coefficient space, not a physical endpoint condition."""
    if length<=0 or any(type(x) is not int or x<1 for x in
                       (time_points,radial_points,radial_order,cap_points)):
        raise ValueError('finite positive numerical representation parameters required')
    tx,tw=leggauss(time_points);t=(tx-1)*length/2;tw=tw*length/2
    rx,rw=leggauss(radial_points);rho=(rx+1)*WALL/2;rw=rw*WALL/2
    b,bt=compact_temporal_basis(t,length)
    if type(include_wall_lift) is not bool or type(include_scalar_mean) is not bool:
        raise ValueError('explicit wall-lift and scalar-mean representation flags required')
    # A wall lift contributes the parent action row, never an invented
    # Neumann condition.  Child and interface rows still enter the join.
    h,hr=regular_radial_basis(rho,radial_order)
    radial_count=radial_order+int(include_wall_lift)
    h,hr=h[:,:radial_count],hr[:,:radial_count]
    gauge_count=20*radial_count;gb=np.zeros((radial_points,gauge_count,1,5,4))
    gr=np.zeros_like(gb);labels=[]
    for j in range(radial_count):
        for field in range(5):
            for internal in range(4):
                i=len(labels);gb[:,i,0,field,internal]=h[:,j]
                gr[:,i,0,field,internal]=hr[:,j]
                labels.append(dict(radial=j,field=FIELD_ORDER[field],internal=internal,
                    wall_lift=bool(j==radial_order)))
    return dict(time=t,time_quadrature=tw,time_basis=b,time_basis_derivative=bt,
        rho=rho,radial_quadrature=rw,gauge_basis=gb,gauge_radial_basis=gr,
        gauge_labels=labels,geometry_count=62,gauge_count=gauge_count,
        scalar_count=4+4*int(include_scalar_mean),scalar_start=62+gauge_count,
        count=66+gauge_count+4*int(include_scalar_mean),include_scalar_mean=include_scalar_mean,
        scalar_coefficient_order=('compact ReH1,ReH2,ImH1,ImH2; optional mean in same realification'),
        scalar_matching=retained_scalar_matching_coefficients(repository),
        length=float(length),time_points=time_points,
        radial_points=radial_points,radial_order=radial_order,cap_points=cap_points,
        include_wall_lift=include_wall_lift,radial_count=radial_count,
        endpoint_policy=('compact temporal corrections; independent wall trace coefficients; parent wall rows only'
             if include_wall_lift else 'compact corrections; fixed reference traces only within this finite application'),
        E0_policy='the local numerical interval is not identified with E0; external birth-source domain retains M_f=M11',
        physical_branch_duration=False)


def _geometry_map(b,bt):
    P=np.zeros((100,62));P[:37,:37]=b*np.eye(37);P[37:74,:37]=bt*np.eye(37)
    P[74:98,37:61]=b*np.eye(24);P[98,61]=b;P[99,61]=bt
    return P


def _reference_fields(coefficients,representation,reference,index):
    c=np.asarray(coefficients,float);q,v,m=reference
    b,bt=representation['time_basis'][index],representation['time_basis_derivative'][index]
    time=representation['time'][index]
    qq=q+time*v+b*c[:37];vv=v+bt*c[:37];mm=m+b*c[37:61]
    s,sr=b*c[61],bt*c[61]
    gb,gr=representation['gauge_basis'],representation['gauge_radial_basis']
    gc=c[62:62+representation['gauge_count']]
    a=np.einsum('rjpic,j->rpic',gb,gc)
    ar=np.einsum('rjpic,j->rpic',gr,gc)
    fields=dict(gauge=b*a,gauge_tau=bt*a,gauge_rho=b*ar,
                gauge_angular=np.zeros((len(a),1,3,5,4)))
    tests=dict(tests=b*gb,tests_tau=bt*gb,tests_rho=b*gr,
        tests_angular=np.zeros((len(a),representation['gauge_count'],1,3,5,4)))
    return qq,vv,mm,s,sr,fields,tests,_geometry_map(b,bt)


def finite_common_iterate_at_time(time,coefficients,representation,reference,*,rho=None):
    """Evaluate geometry and every independent gauge field of one iterate.

    The common time derivative is analytic.  There is no independently
    chosen acceleration, lambda path, angular mode or field profile.
    """
    rep=dict(representation);b,bt=compact_temporal_basis(np.array([time]),rep['length'])
    rep.update(time=np.array([float(time)]),time_basis=b,time_basis_derivative=bt)
    if rho is not None:
        grid=np.asarray(rho,float);h,hr=regular_radial_basis(grid,rep['radial_order'])
        gb=np.zeros((len(grid),rep['gauge_count'],1,5,4));gr=np.zeros_like(gb)
        for j,label in enumerate(rep['gauge_labels']):
            field=FIELD_ORDER.index(label['field']);internal=label['internal'];radial=label['radial']
            gb[:,j,0,field,internal]=h[:,radial];gr[:,j,0,field,internal]=hr[:,radial]
        rep.update(rho=grid,gauge_basis=gb,gauge_radial_basis=gr)
    q,v,m,s,sdot,fields,tests,P=_reference_fields(coefficients,rep,reference,0)
    return dict(q=q,qdot=v,m=m,normal=s,normal_rate=sdot,fields=fields,tests=tests,
        geometry_coefficient_map=P,scope='finite local common iterate; not a physical branch reconstruction')


def prolong_finite_coefficients(coefficients,old_representation,new_representation):
    """Exact inclusion of the old trial functions into an enriched basis."""
    old=np.asarray(coefficients,float)
    if old.shape!=(old_representation['count'],):raise ValueError('old common vector disagrees with representation')
    result=np.zeros(new_representation['count']);result[:62]=old[:62]
    key=lambda label:(label['field'],label['internal'],'wall' if label.get('wall_lift',False) else label['radial'])
    indices={key(label):j for j,label in enumerate(new_representation['gauge_labels'])}
    for j,label in enumerate(old_representation['gauge_labels']):
        if key(label) not in indices:raise ValueError('new representation must contain every old gauge trial')
        result[62+indices[key(label)]]=old[62+j]
    os,ns=old_representation['scalar_start'],new_representation['scalar_start']
    result[ns:ns+4]=old[os:os+4]
    if old_representation.get('include_scalar_mean',False):
        if not new_representation['include_scalar_mean']:raise ValueError('new representation removed scalar mean trial')
        result[ns+4:ns+8]=old[os+4:os+8]
    return result


def finite_action_contacts(coefficients,representation,reference):
    """Evaluate oriented temporal and wall conormals, without appending them.

    The original derivative-form rows already are full action variations.
    These are actual face evaluations, distinct from integrated radial
    momentum tests.  An independent wall lift yields only the parent arm;
    its physical interface equation also includes the child and join terms.
    """
    temporal=[];wall=[]
    for time in (-representation['length'],0.):
        data=finite_common_iterate_at_time(time,coefficients,representation,reference)
        q,v,m,s,sr=(data[key] for key in ('q','qdot','m','normal','normal_rate'))
        cap=moving_cap_action_jet(12,q,v,m,points=representation['cap_points'],source_value=s,source_rate=sr)
        geometry=geometric_connection_coefficient_jets(12,q,v,m,representation['rho'],source_value=s,source_rate=sr)
        tests=dict(tests=representation['gauge_basis'],tests_tau=np.zeros_like(representation['gauge_basis']),
            tests_rho=representation['gauge_radial_basis'],
            tests_angular=np.zeros((len(representation['rho']),representation['gauge_count'],1,3,5,4)))
        momentum=full_maxwell_weak_geometric_jets(geometry,representation['radial_quadrature'],np.ones(1),
            **data['fields'],**tests)['temporal_momentum_test']['values']
        at_wall=finite_common_iterate_at_time(time,coefficients,representation,reference,rho=np.array([WALL]))
        Hcoef=np.asarray(coefficients)[representation['scalar_start']:]
        b,bt=compact_temporal_basis(np.array([time]),representation['length'])
        H=b[0]*Hcoef[:4]+(Hcoef[4:8] if representation['include_scalar_mean'] else 0.)
        Ht=bt[0]*Hcoef[:4]
        metric=intrinsic_m4_weight_jet(12,q,v,m,source_value=s,source_rate=sr)
        trace=at_wall['fields']['gauge'][0,0]
        connection=trace[0]+2*metric['wall_rate'].value*trace[1]
        covariant_t=Ht+np.einsum('a,aij,j->i',connection,higgs_u2_real_representation()['real_generators'],H)
        scalar_momentum=2*metric['wT'].value*covariant_t/(2*np.pi**2)
        temporal.append(dict(time=float(time),orientation=-1 if time<0 else 1,
            geometry_momentum=cap['total'].gradient[37:74],
            gauge_momentum_test=MAXWELL_TO_CAP*momentum,H_real_trace=H,
            scalar_real_canonical_dual=scalar_momentum))
    for time,weight in zip(representation['time'],representation['time_quadrature']):
        data=finite_common_iterate_at_time(time,coefficients,representation,reference,rho=np.array([WALL]))
        q,v,m,s,sr=(data[key] for key in ('q','qdot','m','normal','normal_rate'))
        geometry=geometric_connection_coefficient_jets(12,q,v,m,np.array([WALL]),source_value=s,source_rate=sr)
        # Unit field-component trace tests directly identify the face
        # cotangent.  Their derivatives do not affect this momentum output.
        unit=np.eye(20).reshape(1,20,1,5,4)
        weak=full_maxwell_weak_geometric_jets(geometry,np.ones(1),np.ones(1),**data['fields'],
            tests=unit,tests_tau=np.zeros_like(unit),tests_rho=np.zeros_like(unit),
            tests_angular=np.zeros((1,20,1,3,5,4)))
        wall.append(MAXWELL_TO_CAP*weak['radial_momentum_test']['values'])
    return dict(temporal=temporal,wall_conormal=np.array(wall),
        wall_outward_orientation=1,pole_outward_orientation=-1,
        pole_contact='regular finite-energy trial density limit zero; not an additional imposed boundary equation',
        endpoint_contact_role='displayed IBP contact only; not appended to derivative-form action rows',
        scalar_contact_pairing='real dual=2*Wt*D_tH; equivalent to2Re complex pairing, cap orbit normalization applied once',
        wall_contact_role='partial parent outward cotangent; physical join also requires child and interface action',
        physical_boundary_selected=False)


def coupled_sector_application(coefficients,representation,reference,*,nu_squared_action=None,surface_gamma=None):
    """Assemble residual/Hessian from one scalar action, without supplied rows.

    Geometry qdot and all five gauge derivative applications are derivatives
    of the same coefficient vector.  Lapse/shift rows are the retained
    multiplier constraints; no Gauss row is dropped or set to zero.
    The correction's action excludes the unsolved interacting scalar/native
    load.  Its exact first reached cotangents are returned as sensitivities.
    """
    coefficients=np.asarray(coefficients,float);n=representation['count']
    if coefficients.shape!=(n,) or not np.isfinite(coefficients).all():
        raise ValueError('finite one common coefficient vector required')
    r=np.zeros(n);K=np.zeros((n,n));value=0.
    sectors={name:dict(value=0.,residual=np.zeros(n),hessian=np.zeros((n,n)))
             for name in ('cap','independent_Maxwell','intrinsic_H_kinetic_quartic',
                          'intrinsic_H_potential_per_nu2','surface_per_gamma','H_zero_potential_per_lambda_nu4')}
    moments=[]
    for index,wt in enumerate(representation['time_quadrature']):
        q,v,m,s,sr,fields,tests,P=_reference_fields(coefficients,representation,reference,index)
        cap=moving_cap_action_jet(12,q,v,m,points=representation['cap_points'],
                                source_value=s,source_rate=sr)
        geometry=geometric_connection_coefficient_jets(12,q,v,m,representation['rho'],
                                source_value=s,source_rate=sr,clock='coordinate_time')
        gw=representation['radial_quadrature'];hw=np.ones(1)
        delta=background_subtracted_maxwell_action_jet(geometry,gw,hw,**fields)
        weak=full_maxwell_weak_geometric_jets(geometry,gw,hw,**fields,**tests)
        HH=full_maxwell_gauge_hessian_matrix(geometry,gw,hw,**fields,**tests)
        base=cap['total'];geom=sectors['cap']
        geom['value']+=wt*base.value
        geom['residual'][:62]+=wt*(P.T@base.gradient)
        geom['hessian'][:62,:62]+=wt*(P.T@base.hessian@P)
        gauge=sectors['independent_Maxwell'];scale=wt*MAXWELL_TO_CAP
        gauge['value']+=scale*delta['value']
        gauge['residual'][:62]+=scale*(P.T@delta['gradient'])
        gs=slice(62,62+representation['gauge_count'])
        gauge['residual'][gs]+=scale*weak['weak']['values']
        gauge['hessian'][:62,:62]+=scale*(P.T@delta['hessian']@P)
        B=scale*(weak['weak']['geometric_jacobian']@P)
        gauge['hessian'][gs,:62]+=B;gauge['hessian'][:62,gs]+=B.T
        gauge['hessian'][gs,gs]+=scale*HH['matrix']
        # These are the actual reached weak-action coefficient maps, not
        # numerical choices of gamma, H or the physical common energy scale.
        metric=intrinsic_m4_weight_jet(12,q,v,m,source_value=s,source_rate=sr)
        for name,jet in (('surface_per_gamma',cap['surface_per_gamma']),):
            target=sectors[name];target['value']+=wt*jet.value
            target['residual'][:62]+=wt*(P.T@jet.gradient)
            target['hessian'][:62,:62]+=wt*(P.T@jet.hessian@P)
        # The intrinsic scalar is an unknown in the same coefficient
        # vector.  nu^2 remains one common calibration parameter; the
        # exact polynomial coefficients require no physical value of it.
        b,bt=representation['time_basis'][index],representation['time_basis_derivative'][index]
        scalar_count=representation['scalar_count']
        V=np.zeros((1,4,scalar_count));V[0,:,:4]=b*np.eye(4)
        D=np.zeros((1,4,4,scalar_count));D[0,0,:,:4]=bt*np.eye(4)
        if representation['include_scalar_mean']:V[0,:,4:8]=np.eye(4)
        wall_h,_=regular_radial_basis(np.array([WALL]),representation['radial_order'])
        trace=np.zeros((1,5,4,representation['gauge_count']))
        for j,label in enumerate(representation['gauge_labels']):
            field=FIELD_ORDER.index(label['field'])
            trace[0,field,label['internal'],j]=b*wall_h[0,label['radial']]
        scalar_start=representation['scalar_start'];lam=representation['scalar_matching']['lambda_H']
        scalar=intrinsic_higgs_gauge_action_jet(metric,
            scalar_coefficients=coefficients[scalar_start:],scalar_value_map=V,scalar_derivative_map=D,
            gauge_coefficients=coefficients[gs],gauge_trace_map=trace,
            angular_quadrature=np.ones(1),lambda_H=lam,nu_squared_action=0.)
        local_size=100+scalar_count+representation['gauge_count'];lift=np.zeros((local_size,n))
        lift[:100,:62]=P;lift[100:100+scalar_count,scalar_start:]=np.eye(scalar_count)
        lift[100+scalar_count:,gs]=np.eye(representation['gauge_count'])
        for name,jet,factor in zip(
                ('intrinsic_H_kinetic_quartic','intrinsic_H_potential_per_nu2','H_zero_potential_per_lambda_nu4'),
                scalar['nu_squared_polynomial_coefficients'],(1.,1.,1/lam)):
            target=sectors[name];scale_H=wt*factor/ORBIT_VOLUME_SQUARED
            target['value']+=scale_H*jet.value
            target['residual']+=scale_H*(lift.T@jet.gradient)
            target['hessian']+=scale_H*(lift.T@jet.hessian@lift)
        moments.append(dict(time=float(representation['time'][index]),
            temporal_gauge_momentum_test_integral=MAXWELL_TO_CAP*weak['temporal_momentum_test']['values'],
            radial_gauge_momentum_test_integral=MAXWELL_TO_CAP*weak['radial_momentum_test']['values'],
            geometric_canonical_momentum=base.gradient[37:74],
            multiplier_constraint_density=base.gradient[74:98],
            mechanical_connection=np.array([row['connection_lambda'].value for row in geometry['rows']])))
    terms=[('cap',1.),('independent_Maxwell',1.),('intrinsic_H_kinetic_quartic',1.)]
    if nu_squared_action is not None:
        if not np.isfinite(nu_squared_action) or nu_squared_action<0:
            raise ValueError('finite nonnegative explicit shared action-unit nu squared required')
        terms.extend((('intrinsic_H_potential_per_nu2',nu_squared_action),
          ('H_zero_potential_per_lambda_nu4',representation['scalar_matching']['lambda_H']*nu_squared_action**2)))
    if surface_gamma is not None:
        if not np.isfinite(surface_gamma):raise ValueError('finite explicit surface coefficient required')
        terms.append(('surface_per_gamma',surface_gamma))
    for name,factor in terms:
        value+=factor*sectors[name]['value'];r+=factor*sectors[name]['residual'];K+=factor*sectors[name]['hessian']
    return dict(value=float(value),residual=r,hessian=K,sectors=sectors,moments=moments,
        hessian_symmetry_defect=float(np.max(abs(K-K.T))),
        multiplier_rows=r[37:61],Gauss_rows=r[62:representation['scalar_start']].reshape(-1,5,4)[:,:2],
        scalar_rows=r[representation['scalar_start']:],
        parent_wall_rows=(r[62+20*representation['radial_order']:representation['scalar_start']]
                          if representation['include_wall_lift'] else np.empty(0)),
        parent_wall_rows_scope='partial parent action; child and interface generating action must be included in physical join',
        scalar_gauge_block=sectors['intrinsic_H_kinetic_quartic']['hessian'][representation['scalar_start']:,62:representation['scalar_start']],
        field_order=FIELD_ORDER,geometry_unknown_count=62,gauge_unknown_count=representation['gauge_count'],scalar_unknown_count=representation['scalar_count'],
        normalization=dict(cap='orbit-volume normalized retained local action',
            Maxwell_to_cap=MAXWELL_TO_CAP,embedding_index=MECHANICAL_EMBEDDING_INDEX,
            orbit_volume_squared=ORBIT_VOLUME_SQUARED),
        background_Maxwell_added_again=False,Gauss_rows_eliminated=False,
        action_parameters=dict(nu_squared_action=nu_squared_action,surface_gamma=surface_gamma),
        stationary_E1_claim=False,physical_Pauli_contraction=False,
        scalar_scale_sensitivity='R_Hzero=(lambda_H*nu_GeV^4)*exp(-4 log E_kappa)*R_Hzero_per_lambda_nu4; d_logE=-4 R_Hzero',
        interacting_scalar_native_load_included=False)


def finite_newton_correction(coefficients,representation,reference,*,rank_tolerance=1e-11,max_halvings=14,
                             action_parameters=None):
    """Compute and actually apply a damped finite residual-driven correction.

    A rank-revealing symmetric solve retains the discarded residual and
    reports nullity.  It is a numerical minimum-norm update in this finite
    representation, not a physical gauge fixing or a quotient projection.
    """
    action_parameters={} if action_parameters is None else dict(action_parameters)
    before=coupled_sector_application(coefficients,representation,reference,**action_parameters)
    K=before['hessian'];r=before['residual']
    norm=np.sqrt(np.maximum(np.max(abs(K),axis=1),np.finfo(float).tiny))
    scaling=1/norm;scaled=scaling[:,None]*K*scaling[None,:]
    eig,U=np.linalg.eigh((scaled+scaled.T)/2)
    active=abs(eig)>rank_tolerance*max(1.,np.max(abs(eig)))
    rr=scaling*r;projected=U[:,active].T@rr
    correction=-scaling*(U[:,active]@(projected/eig[active]))
    linear=K@correction+r
    initial=float(np.linalg.norm(rr));history=[];updated=None
    for j in range(max_halvings+1):
        step=2.**(-j)
        try:
            application=coupled_sector_application(np.asarray(coefficients)+step*correction,representation,reference,**action_parameters)
            after=float(np.linalg.norm(scaling*application['residual']))
            history.append(dict(step=step,scaled_residual=after,admissible=True))
        except ValueError as err:
            history.append(dict(step=step,scaled_residual=None,admissible=False,reason=str(err)))
            continue
        if after<initial:
            updated=application;break
    if updated is None:
        return dict(before=before,after=None,correction=correction,accepted=False,
            rank=int(active.sum()),nullity=int((~active).sum()),damping_history=history,
            linearized_residual=linear,scaled_initial_residual=initial,eigenvalues=eig)
    # Exact first-order response to the unsolved scalar coefficient is a
    # consumed finite solve against its actual metric-volume cotangent.
    load=before['sectors']['H_zero_potential_per_lambda_nu4']['residual']
    sensitivity=-scaling*(U[:,active]@((U[:,active].T@(scaling*load))/eig[active]))
    surface_load=before['sectors']['surface_per_gamma']['residual']
    surface_sensitivity=-scaling*(U[:,active]@((U[:,active].T@(scaling*surface_load))/eig[active]))
    nu2=action_parameters.get('nu_squared_action')
    nu_load=before['sectors']['intrinsic_H_potential_per_nu2']['residual'].copy()
    if nu2 is not None:
        nu_load+=2*representation['scalar_matching']['lambda_H']*nu2*load
    nu_sensitivity=-scaling*(U[:,active]@((U[:,active].T@(scaling*nu_load))/eig[active]))
    return dict(before=before,after=updated,correction=correction,accepted=True,
        updated_coefficients=np.asarray(coefficients)+step*correction,step=step,
        rank=int(active.sum()),nullity=int((~active).sum()),eigenvalues=eig,
        damping_history=history,linearized_residual=linear,
        scaled_initial_residual=initial,scaled_updated_residual=after,
        scalar_vacuum_coefficient_correction_sensitivity=sensitivity,
        scalar_sensitivity_linear_residual=K@sensitivity+load,
        surface_gamma_correction_sensitivity=surface_sensitivity,
        surface_sensitivity_linear_residual=K@surface_sensitivity+surface_load,
        nu_squared_correction_sensitivity=nu_sensitivity,
        nu_squared_sensitivity_linear_residual=K@nu_sensitivity+nu_load,
        physical_gauge_fixing_selected=False,complete_interacting_correction=False)


def iterate_finite_newton(coefficients,representation,reference,*,max_iterations=8,
                          relative_tolerance=1e-9,absolute_tolerance=1e-13,action_parameters=None):
    """Actually iterate the finite action, with one fixed convergence norm.

    Parameter values supplied here are conditional family applications, not
    determinations of physical gamma or E_kappa.  The returned tolerance is
    a finite residual tolerance; continuum and event closure are separate.
    """
    if type(max_iterations) is not int or max_iterations<1:
        raise ValueError('positive finite iteration budget required')
    initial=np.asarray(coefficients,float).copy();current=initial.copy();history=[];steps=[]
    first=coupled_sector_application(current,representation,reference,**({} if action_parameters is None else action_parameters))
    scaling=1/np.sqrt(np.maximum(np.max(abs(first['hessian']),axis=1),np.finfo(float).tiny))
    original=float(np.linalg.norm(scaling*first['residual']));target=max(absolute_tolerance,relative_tolerance*original)
    final=first;status='ITERATION_LIMIT'
    for i in range(max_iterations):
        residual=float(np.linalg.norm(scaling*final['residual']))
        if residual<=target:status='FINITE_RESIDUAL_TOLERANCE';break
        result=finite_newton_correction(current,representation,reference,action_parameters=action_parameters)
        steps.append(result)
        history.append(dict(iteration=i,initial_residual_norm=float(np.linalg.norm(result['before']['residual'])),
            fixed_scaled_initial_residual=residual,rank=result['rank'],nullity=result['nullity'],
            accepted=result['accepted'],damping_history=result['damping_history'],
            linearized_residual_norm=float(np.linalg.norm(result['linearized_residual']))))
        if not result['accepted']:status='DAMPING_STALL';break
        current=result['updated_coefficients'];final=result['after']
    fixed_final=float(np.linalg.norm(scaling*final['residual']))
    if fixed_final<=target:status='FINITE_RESIDUAL_TOLERANCE'
    end_scale=1/np.sqrt(np.maximum(np.max(abs(final['hessian']),axis=1),np.finfo(float).tiny))
    end_eigenvalues=np.linalg.eigvalsh(end_scale[:,None]*final['hessian']*end_scale[None,:])
    end_active=abs(end_eigenvalues)>1e-11*max(1.,np.max(abs(end_eigenvalues)))
    return dict(initial_coefficients=initial,coefficients=current,initial=first,final=final,
        history=history,steps=steps,status=status,fixed_scaling=scaling,
        fixed_scaled_initial_residual=original,fixed_scaled_final_residual=fixed_final,
        final_scaled_eigenvalues=end_eigenvalues,final_numeric_rank=int(end_active.sum()),
        final_numeric_nullity=int((~end_active).sum()),numeric_rank_cutoff=1e-11,
        finite_residual_target=target,physical_stationarity=False,complete_interacting_correction=False)


def corrected_Q_hessian_and_Ward(coefficients,representation,reference,repository=ROOT):
    """Apply the full gauge Hessian to the eight retained n1 Q lifts.

    This is a primitive action pairing on the evaluated finite iterate,
    not its native heat, retarded inverse or physical Pauli contraction.
    The radial/time test profile is a numerical representation.  An
    angular gauge variation need not preserve the fixed trace trial space:
    the off-shell Ward identity is checked in the full action application,
    with its nonzero Euler commutator and curvature contact retained.
    """
    probe=angular_ward_probe();hw=probe['Haar_weights']
    with np.load(Path(repository)/SOURCE,allow_pickle=False) as data:
        saved=np.array(data['original_n1'])
    val=probe['evaluate'](saved).transpose(0,3,1,2)
    ev=np.array([probe['evaluate'](probe['derivative'](saved,i)).transpose(0,3,1,2)
                 for i in range(3)]).transpose(1,2,0,3,4)
    gram=np.einsum('Apic,Bpic,p->AB',val,val,hw)
    defect=float(np.linalg.norm(gram-(16/3)*np.eye(8)))
    if defect>2e-11:raise ValueError('retained real n1 source/Haar normalization changed')
    nr=len(representation['rho'])
    h,hr=regular_radial_basis(representation['rho'],representation['radial_order'])
    matrix=np.zeros((8,8));contact=np.zeros((8,8));hessian=np.zeros(8);Euler=np.zeros(8);Ward_contact=np.zeros(8)
    time_Ward=[]
    for index,wt in enumerate(representation['time_quadrature']):
        q,v,m,s,sr,fields,_,_=_reference_fields(coefficients,representation,reference,index)
        geometry=geometric_connection_coefficient_jets(12,q,v,m,representation['rho'],
                       source_value=s,source_rate=sr,clock='coordinate_time')
        # Only the existing finite iterate is angular constant.  The Q
        # tests and the gauge variation are the full owned n1 sections.
        fields={key:np.repeat(value,len(hw),axis=1) for key,value in fields.items()}
        b,bt=representation['time_basis'][index],representation['time_basis_derivative'][index]
        source=np.zeros((nr,8,len(hw),5,4));source_tau=np.zeros_like(source);source_rho=np.zeros_like(source)
        source_angular=np.zeros((nr,8,len(hw),3,5,4))
        source[...,2:,:]=b*h[:,0,None,None,None,None]*val[None]
        source_tau[...,2:,:]=bt*h[:,0,None,None,None,None]*val[None]
        source_rho[...,2:,:]=b*hr[:,0,None,None,None,None]*val[None]
        source_angular[...,2:,:]=b*h[:,0,None,None,None,None,None]*ev[None]
        total=fields['gauge'].copy();total_tau=fields['gauge_tau'].copy();total_rho=fields['gauge_rho'].copy()
        for i,row in enumerate(geometry['rows']):
            total[i,:,2:]+=M*(row['connection_lambda'].value-1)
            total_tau[i,:,2:]+=M*row['lambda_tau'].value
            total_rho[i,:,2:]+=M*row['lambda_rho'].value
        eta=probe['eta'][None,:,None,:];eta_e=probe['eta_angular'][None,:,:,None,:]
        z=_bracket(total,eta);z[...,2:,:]+=probe['eta_angular'][None]
        zt,zr=_bracket(total_tau,eta),_bracket(total_rho,eta)
        ez=_bracket(total[:,:,None],eta_e)
        # eta_second uses the retained coefficient-action ordering.  Its
        # curl with 2*E eta vanishes exactly in the owned right coframe.
        ez[...,2:,:]+=probe['eta_second'][None]
        tests=dict(tests=np.concatenate((source,z[:,None]),axis=1),
            tests_tau=np.concatenate((source_tau,zt[:,None]),axis=1),
            tests_rho=np.concatenate((source_rho,zr[:,None]),axis=1),
            tests_angular=np.concatenate((source_angular,ez[:,None]),axis=1))
        hh=full_maxwell_gauge_hessian_matrix(geometry,representation['radial_quadrature'],hw,**fields,**tests)
        eta_test=eta[:,None];eta_derivative=eta_e[:,None]
        comm=_bracket(source,eta_test)
        comm_t,comm_r=_bracket(source_tau,eta_test),_bracket(source_rho,eta_test)
        comm_e=(_bracket(source_angular,eta_test[:,:,:,None])
                +_bracket(source[:,:,:,None],eta_derivative))
        ew=full_maxwell_weak_geometric_jets(geometry,representation['radial_quadrature'],hw,**fields,
            tests=comm,tests_tau=comm_t,tests_rho=comm_r,tests_angular=comm_e)['weak']['values']
        scale=wt*MAXWELL_TO_CAP
        matrix+=scale*hh['matrix'][:8,:8];contact+=scale*hh['curvature_contact_matrix'][:8,:8]
        hessian+=scale*hh['matrix'][:8,8];Euler+=scale*ew
        Ward_contact+=scale*hh['curvature_contact_matrix'][:8,8]
        time_Ward.append(hh['matrix'][:8,8]+ew)
    ward=hessian+Euler
    return dict(Q_hessian=matrix,Q_curvature_contact=contact,
        Hessian_on_gauge_tangent=hessian,Euler_commutator=Euler,Ward_pairing=ward,
        Ward_curvature_contact=Ward_contact,
        source_Haar_Gram=gram,source_Haar_Gram_defect=defect,
        Ward_max_time_slice_defect=float(np.max(abs(np.array(time_Ward)))),
        Ward_relative_defect=float(np.max(abs(ward))/(1+np.max(abs(hessian))+np.max(abs(Euler)))),
        scope='EVALUATED_PRIMITIVE_FULL5_ACTION_PAIRING_ON_FINITE_COMMON_ITERATE',
        profile_scope='CONTROL_ONLY compact temporal times first regular radial interior test',
        gauge_probe_scope=probe['gauge_probe_scope'],stationary_E1_claim=False,
        native_heat_evaluated=False,retarded_inverse_evaluated=False,physical_Pauli_contraction=False,
        normalization=MAXWELL_TO_CAP,curvature_contacts_retained=True,Gauss_columns_eliminated=False)


def materialize(output,repository=ROOT,*,representation_parameters=None,
                action_parameters=None,initial_scalar_coefficients=None,initial_application=None):
    repository=Path(repository);output=Path(output)
    if output.exists():raise FileExistsError('preserve prior evidence; use a new output directory')
    reference=retained_state(repository)
    rep=correction_representation(repository=repository,**({} if representation_parameters is None else representation_parameters))
    initial=np.zeros(rep['count'])
    replay_refs=[]
    if initial_application is not None:
        previous=Path(initial_application)
        if not previous.is_absolute():previous=repository/previous
        metadata=json.loads((previous/'result.json').read_text(encoding='utf8'))
        old_rep=correction_representation(repository=repository,
            length=metadata['numerical_local_interval_length'],time_points=metadata['temporal_quadrature_order'],
            radial_points=metadata['radial_quadrature_order'],radial_order=metadata['gauge_unknowns']//20-int(metadata.get('include_wall_lift',False)),
            cap_points=metadata['cap_quadrature_order'],include_wall_lift=metadata.get('include_wall_lift',False),
            include_scalar_mean=metadata.get('include_scalar_mean',False))
        with np.load(previous/'application.npz',allow_pickle=False) as data:
            initial=prolong_finite_coefficients(data['updated_coefficients'],old_rep,rep)
        replay_refs=[(previous/name).relative_to(repository).as_posix() for name in ('result.json','application.npz')]
    if initial_scalar_coefficients is not None:
        scalar_initial=np.asarray(initial_scalar_coefficients,float)
        if scalar_initial.shape==(4,) and rep['include_scalar_mean']:
            initial[-4:]=scalar_initial
        elif scalar_initial.shape==(rep['scalar_count'],):initial[rep['scalar_start']:]=scalar_initial
        else:raise ValueError('four real mean components or the complete finite scalar vector required')
        if not np.isfinite(scalar_initial).all():raise ValueError('finite numerical scalar starting iterate required')
    refs=list(SOURCE_RECEIPTS)+replay_refs
    input_hashes={p:sha256((repository/p).read_bytes()).hexdigest() for p in refs}
    iteration=iterate_finite_newton(initial,rep,reference,action_parameters=action_parameters)
    result=(dict(iteration['steps'][0]) if iteration['steps'] else
        finite_newton_correction(initial,rep,reference,action_parameters=action_parameters))
    if result['accepted']:
        result.update(after=iteration['final'],updated_coefficients=iteration['coefficients'])
    primitive_before=corrected_Q_hessian_and_Ward(initial,rep,reference,repository)
    primitive_after=(corrected_Q_hessian_and_Ward(result['updated_coefficients'],rep,reference,repository)
                     if result['accepted'] else None)
    contacts=finite_action_contacts(iteration['coefficients'],rep,reference)
    arrays=dict(initial_coefficients=initial,first_Newton_correction=result['correction'],
        total_coefficient_update=iteration['coefficients']-initial,
        initial_residual=result['before']['residual'],initial_hessian=result['before']['hessian'],
        scaled_eigenvalues=result['eigenvalues'],linearized_residual=result['linearized_residual'],
        temporal_points=rep['time'],radial_points=rep['rho'])
    arrays['final_scaled_eigenvalues']=iteration['final_scaled_eigenvalues']
    if iteration['steps']:
        arrays['iteration_Newton_corrections']=np.array([step['correction'] for step in iteration['steps']])
        arrays['iteration_initial_residuals']=np.array([step['before']['residual'] for step in iteration['steps']])
        arrays['iteration_hessians']=np.array([step['before']['hessian'] for step in iteration['steps']])
        arrays['iteration_linearized_residuals']=np.array([step['linearized_residual'] for step in iteration['steps']])
    for name,value in result['before']['sectors'].items():
        arrays[name+'_residual']=value['residual'];arrays[name+'_hessian']=value['hessian']
    if result['accepted']:
        arrays.update(updated_coefficients=result['updated_coefficients'],updated_residual=result['after']['residual'],
            updated_hessian=result['after']['hessian'],
            scalar_vacuum_coefficient_correction_sensitivity=result['scalar_vacuum_coefficient_correction_sensitivity'],
            nu_squared_correction_sensitivity=result['nu_squared_correction_sensitivity'],
            surface_gamma_correction_sensitivity=result['surface_gamma_correction_sensitivity'])
    for name,application in (('primitive_before',primitive_before),('primitive_after',primitive_after)):
        if application is not None:
            arrays.update({name+'_'+key:value for key,value in application.items() if isinstance(value,np.ndarray)})
    arrays.update(temporal_endpoint_geometry_momenta=np.array([x['geometry_momentum'] for x in contacts['temporal']]),
        temporal_endpoint_gauge_momenta=np.array([x['gauge_momentum_test'] for x in contacts['temporal']]),
        temporal_endpoint_H_real_traces=np.array([x['H_real_trace'] for x in contacts['temporal']]),
        temporal_endpoint_scalar_real_canonical_duals=np.array([x['scalar_real_canonical_dual'] for x in contacts['temporal']]),
        wall_outward_conormal=contacts['wall_conormal'],
        integrated_radial_momentum_tests=np.array([x['radial_gauge_momentum_test_integral'] for x in iteration['final']['moments']]),
        integrated_temporal_momentum_tests=np.array([x['temporal_gauge_momentum_test_integral'] for x in iteration['final']['moments']]))
    arrays['final_multiplier_constraint_density_at_time_nodes']=np.array([x['multiplier_constraint_density']
                                                              for x in iteration['final']['moments']])
    if input_hashes!={p:sha256((repository/p).read_bytes()).hexdigest() for p in refs}:
        raise RuntimeError('an audited input/source changed during application; preserve evidence and replay under stable owners')
    output.mkdir(parents=True);_deterministic_npz(output/'application.npz',arrays)
    receipt=dict(scope='EVALUATED_FINITE_COMMON_CAP_MAXWELL_INTRINSIC_HIGGS_SECTOR_CORRECTION',
        accepted=result['accepted'],rank=result['rank'],nullity=result['nullity'],
        action_parameters=result['before']['action_parameters'],
        initial_scalar_coefficients=initial[rep['scalar_start']:].tolist(),
        scalar_start_scope='numerical initial coefficient iterate; not selected physical H or E0 scalar trace',
        iteration_status=iteration['status'],iteration_history=iteration['history'],
        fixed_scaled_initial_residual=iteration['fixed_scaled_initial_residual'],
        fixed_scaled_final_residual=iteration['fixed_scaled_final_residual'],
        finite_residual_target=iteration['finite_residual_target'],
        final_numeric_rank=iteration['final_numeric_rank'],final_numeric_nullity=iteration['final_numeric_nullity'],
        numeric_rank_cutoff=iteration['numeric_rank_cutoff'],
        numeric_nullity_is_physical_gauge_orbit_count=False,
        damping_history=result['damping_history'],
        initial_residual_norm=float(np.linalg.norm(result['before']['residual'])),
        scaled_initial_residual=result['scaled_initial_residual'],
        scaled_updated_residual=result.get('scaled_updated_residual'),
        linearized_residual_norm=float(np.linalg.norm(result['linearized_residual'])),
        hessian_symmetry_defect=result['before']['hessian_symmetry_defect'],
        primitive_Q_application_before={k:v for k,v in primitive_before.items() if not isinstance(v,np.ndarray)},
        primitive_Q_application_after=({k:v for k,v in primitive_after.items() if not isinstance(v,np.ndarray)}
                                      if primitive_after is not None else None),
        primitive_Q_Hessian_change_norm=(float(np.linalg.norm(primitive_after['Q_hessian']-primitive_before['Q_hessian']))
                                         if primitive_after is not None else None),
        sector_initial_residual_norms={k:float(np.linalg.norm(v['residual'])) for k,v in result['before']['sectors'].items()},
        normalization=result['before']['normalization'],gauge_labels=rep['gauge_labels'],
        geometry_order=12,geometry_unknowns=62,gauge_unknowns=rep['gauge_count'],scalar_unknowns=rep['scalar_count'],
        include_wall_lift=rep['include_wall_lift'],
        include_scalar_mean=rep['include_scalar_mean'],
        scalar_order=rep['scalar_coefficient_order'],
        updated_scalar_coefficients=iteration['coefficients'][rep['scalar_start']:].tolist(),
        scalar_gauge_cross_norm=float(np.linalg.norm(iteration['final']['scalar_gauge_block'])),
        scalar_gauge_cross_scope=('actual wall-trace restriction; zero interiors do not imply physical decoupling'
            if not rep['include_wall_lift'] else 'actual parent wall-lift/Higgs action block; child/interface arm not included'),
        parent_wall_row_norm=float(np.linalg.norm(iteration['final']['parent_wall_rows'])),
        face_contacts={k:v for k,v in contacts.items() if k not in ('temporal','wall_conormal')},
        scalar_matching=rep['scalar_matching'],
        numerical_local_interval_length=rep['length'],physical_branch_duration=False,
        temporal_quadrature_order=rep['time_points'],radial_quadrature_order=rep['radial_points'],cap_quadrature_order=rep['cap_points'],
        reference='outgoing branch24 E1+ affine germ plus recorded initial_coefficients; not incoming C1 history or a physical branch duration',
        reference_trace=rep['endpoint_policy'],E0_policy=rep['E0_policy'],
        endpoint_terms_invented=False,background_Maxwell_added_again=False,
        Gauss_rows_eliminated=False,physical_gauge_fixing_selected=False,
        scalar_scale_sensitivity=result['before']['scalar_scale_sensitivity'],
        scalar_vacuum_sensitivity_norm=None if not result['accepted'] else float(np.linalg.norm(result['scalar_vacuum_coefficient_correction_sensitivity'])),
        scalar_vacuum_sensitivity_linear_residual_norm=None if not result['accepted'] else float(np.linalg.norm(result['scalar_sensitivity_linear_residual'])),
        surface_gamma_sensitivity_norm=None if not result['accepted'] else float(np.linalg.norm(result['surface_gamma_correction_sensitivity'])),
        surface_gamma_sensitivity_linear_residual_norm=None if not result['accepted'] else float(np.linalg.norm(result['surface_sensitivity_linear_residual'])),
        nu_squared_sensitivity_norm=None if not result['accepted'] else float(np.linalg.norm(result['nu_squared_correction_sensitivity'])),
        nu_squared_sensitivity_linear_residual_norm=None if not result['accepted'] else float(np.linalg.norm(result['nu_squared_sensitivity_linear_residual'])),
        final_unscaled_residual_norm=float(np.linalg.norm(iteration['final']['residual'])),
        final_unprojected_constraint_density_max=float(np.max(abs(arrays['final_multiplier_constraint_density_at_time_nodes']))),
        finite_residual_is_pointwise_action_solution=False,
        unassigned_physical_parameter_terms=['gamma(c)*surface_per_gamma with gamma=alpha_FSC*ell_current^(-m)',
            'nu_GeV^2*exp(-2logE_kappa)*intrinsic_H_potential_per_nu2',
            'lambda_H*nu_GeV^4*exp(-4logE_kappa)*H_zero_potential_per_lambda_nu4'],
        common_scale_unknown=True,scale_matching_equation='G_F_measured=c_F[common action charged-current contraction]/E_kappa^2; E_kappa is a shared calibration unknown',
        scale_matching_owner='universal_gf_scale.UniversalGFScaleMap; action coefficient still must be computed on corrected coupled domain',
        complete_interacting_correction=False,stationary_E1_claim=False,
        physical_Pauli_contraction=False,physical_unit_assigned=False,
        numerical_sha256=sha256((output/'application.npz').read_bytes()).hexdigest(),
        input_hashes=input_hashes,
        error_scope='finite Galerkin residual correction; no continuum convergence, native completion or physical branch selection')
    (output/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return receipt


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--time-points',type=int,default=4);parser.add_argument('--radial-points',type=int,default=24)
    parser.add_argument('--radial-order',type=int,default=2);parser.add_argument('--cap-points',type=int,default=24)
    parser.add_argument('--include-wall-lift',action='store_true')
    parser.add_argument('--include-scalar-mean',action='store_true');parser.add_argument('--initial-application',type=Path)
    parser.add_argument('--nu-squared-action',type=float);parser.add_argument('--surface-gamma',type=float)
    parser.add_argument('--initial-scalar-coefficients',nargs='+',type=float)
    args=parser.parse_args();print(json.dumps(materialize(args.output,
        representation_parameters=dict(time_points=args.time_points,radial_points=args.radial_points,
           radial_order=args.radial_order,cap_points=args.cap_points,include_wall_lift=args.include_wall_lift,
           include_scalar_mean=args.include_scalar_mean),
        action_parameters=dict(nu_squared_action=args.nu_squared_action,surface_gamma=args.surface_gamma),
        initial_scalar_coefficients=args.initial_scalar_coefficients,initial_application=args.initial_application),sort_keys=True))
