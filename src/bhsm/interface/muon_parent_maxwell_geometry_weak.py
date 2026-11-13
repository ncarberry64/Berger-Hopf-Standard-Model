"""Same-action geometric derivatives of spatial parent Maxwell weak rows.

The material chart is the retained anchored sigma chart.  Geometry, measure,
shift and the induced mechanical connection are differentiated together.
Independent gauge coefficient fields are held fixed in that chart; their
additional variations belong to their own coupled columns.  This restricted
spatial block does not replace the temporal/radial Gauss equations.
"""
from __future__ import annotations

import math
import json
from hashlib import sha256
from pathlib import Path
import numpy as np

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .aether_n3_exact_full_local_action_jet_v17_60 import _linear, _variables
from .muon_moving_geometric_action import (
    _fields, _sqrt, response_two_jet, retained_state,
)
from .muon_parent_retarded_hypercharge import WALL
from .muon_parent_maxwell_background_euler import _bracket
from .muon_matched_mechanical_source import epsilon


def geometric_connection_coefficient_jets(order, q, velocity, multipliers, rho,
                                        *, source_value=0., source_rate=0.,
                                        trial_normal=1., clock='coordinate_time'):
    """Evaluate the common (q,qdot,m,s,sdot) coefficient two-jet.

    rho is a reference cap coordinate.  Its physical value is
    rho_phys=2*rho*chi_wall/(pi/2).  Density pullback gives e_ref=J*e,
    r_ref=r/J, d_ref=J*d and shift_ref=(shift+rho_phys_dot)/J.
    The temporal-radial two-form coefficient is
    electric_radial=common*r_orbit**3/(lapse*C_rho*J).
    lambda_tau_ref=lambda_tau+rho_phys_dot*lambda_rho and
    lambda_rho_ref=J*lambda_rho; hence normal advection is included once.

    Coordinate time includes the lapse-clock Jacobian explicitly.  Boundary
    proper time is also available, with its conversion in the returned jet.
    No time acceleration or inverse singular birth Hessian is used.
    """
    if clock not in ('coordinate_time','boundary_proper_time'):
        raise ValueError('explicit common time coordinate required')
    qq,vv,mm=(np.asarray(x,float) for x in (q,velocity,multipliers))
    qdim=1+3*order;total=2*qdim+2*order+2
    if qq.shape!=(qdim,) or vv.shape!=(qdim,) or mm.shape!=(2*order,):
        raise ValueError('same retained geometric state layout required')
    rho=np.asarray(rho,float)
    if rho.ndim!=1 or np.any(rho<=0) or np.any(rho>WALL):
        raise ValueError('regular reference cap quadrature required')
    qj=_variables(qq,0,total);vj=_variables(vv,qdim,total);mj=_variables(mm,2*qdim,total)
    s,sdot=_variables(np.array([source_value,source_rate]),total-2,total)
    sk=(-1.)**np.arange(1,order+1);sj=(-1.)**np.arange(order)
    from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
    Cstar=RADIUS0*(qj[0]+_linear(qj[1:1+order],sk)+_linear(qj[1+order:1+2*order],sj)).exp()
    logCdot=vj[0]+_linear(vj[1:1+order],sk)+_linear(vj[1+order:1+2*order],sj)
    k=-float(trial_normal)/(16*Cstar);kdot=-k*logCdot
    wall=math.pi/4-16*k*s;wall_dot=-16*(k*sdot+kdot*s)
    if wall.value<=0 or wall.value>=math.pi/2:
        raise ValueError('material chart remains inside the owned two-pole interval')
    jac=2*wall/WALL
    Nb=_linear(mj[:order],sk).exp()
    clock_lapse=Jet.constant(1.,total) if clock=='coordinate_time' else Nb
    rows=[]
    for rr in rho:
        chi=(float(rr)/WALL)*wall
        f=_fields(order,qj,vj,mj,chi)
        LF=_sqrt(f['A']**2+f['B']**2)
        radius=f['A']*f['B']/LF;Crho=f['C']/2
        _,sigma=response_two_jet(chi,s,k)
        weight=1-4*sigma**2
        common=2*math.pi**4*LF**5*weight
        lapse=f['N']/clock_lapse
        shift=2*f['beta']/clock_lapse
        adv=(2*float(rr)/WALL)*wall_dot/clock_lapse
        lam=f['A']**2/LF**2
        lr=lam*(1-lam)*(f['ap']-f['bp'])
        lt=2*lam*(1-lam)*(f['la']-f['lb'])/clock_lapse
        rows.append(dict(electric=jac*common*Crho*radius/lapse,
            electric_radial=common*radius**3/(lapse*Crho*jac),
            radial=common*lapse*radius/(Crho*jac),
            angular=jac*common*lapse*Crho/radius,
            shift=(shift+adv)/jac, connection_lambda=lam,
            lambda_tau=lt+adv*lr, lambda_rho=jac*lr,
            induced_lambda_tau_unadvected=lt, induced_lambda_rho_unadvected=lr,
            material_jacobian=jac, material_velocity=adv,
            boundary_lapse=Nb, sigma=sigma))
    return dict(rows=rows, clock=clock, coordinate_count=total,
                chart='(q,qdot,lapse_shift,s,sdot); anchored material sigma and wall',
                gauge_field_policy='independent gauge coefficients fixed in reference material chart',
                induced_connection_motion_count=1)


def _curl_without_background(value, angular_derivative):
    out=2*value.copy();eps=epsilon()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                out[...,i,:] += eps[i,j,k]*angular_derivative[...,j,k,:]
    return out


def _curl_bracket(a,b):
    out=np.zeros(np.broadcast_shapes(a.shape,b.shape),float);eps=epsilon()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                out[...,i,:] += eps[i,j,k]*_bracket(a[...,j,:],b[...,k,:]).real
    return out


def spatial_maxwell_weak_geometric_jets(coefficient_jets, quadrature, Haar_weights,
        *, gauge, gauge_tau, gauge_rho, gauge_angular,
        tests, tests_tau, tests_rho, tests_angular):
    """Return spatial gauge Euler rows and their full geometric derivatives.

    Gauge arrays have (radial,Haar_point,spatial,internal) axes.  Test arrays
    insert a test index after radial.  Angular derivatives insert their
    derivative index before spatial.  All inputs are real components in
    the owned anti-Hermitian unit-Tr16 basis, evaluated from the caller's
    coefficient vector.  Their values are solver unknowns, not new data.

    A_i=jmath_i(lambda-1)+a_i, jmath_i=sqrt(8)H_i.  The full spatial
    magnetic polynomial and its background and a-a curvature contacts are
    retained.  This block holds temporal/radial one-forms at zero; it does
    not impose their Gauss equations or certify a physical gauge background.
    """
    supplied=(quadrature,Haar_weights,gauge,gauge_tau,gauge_rho,gauge_angular,
              tests,tests_tau,tests_rho,tests_angular)
    if any(not np.isrealobj(x) for x in supplied):
        raise ValueError('real anti-Hermitian component applications required; no silent complex projection')
    w,hw=np.asarray(quadrature,float),np.asarray(Haar_weights,float)
    a,at,ar,ea=(np.asarray(x,float) for x in (gauge,gauge_tau,gauge_rho,gauge_angular))
    v,vt,vr,ev=(np.asarray(x,float) for x in (tests,tests_tau,tests_rho,tests_angular))
    if w.ndim!=1 or hw.ndim!=1 or len(coefficient_jets['rows'])!=len(w):
        raise ValueError('same reference radial and Haar quadrature required')
    if any(not np.all(np.isfinite(x)) for x in (w,hw,a,at,ar,ea,v,vt,vr,ev)):
        raise ValueError('finite coefficient applications required')
    if a.shape != (len(w),len(hw),3,4) or at.shape!=a.shape or ar.shape!=a.shape:
        raise ValueError('same material gauge coefficient applications required')
    if v.ndim!=5 or v.shape[0]!=len(w) or v.shape[2:]!=(len(hw),3,4) or vt.shape!=v.shape or vr.shape!=v.shape:
        raise ValueError('same indexed real spatial gauge test applications required')
    if ea.shape!=a.shape[:-2]+(3,3,4) or ev.shape!=v.shape[:-2]+(3,3,4):
        raise ValueError('actual angular derivative applications required')
    M=np.sqrt(8)*np.column_stack((np.eye(3),np.zeros(3)))
    a,at,ar,ea=(x[:,None] for x in (a,at,ar,ea))
    Ta,Tv=_curl_bracket(M,a),_curl_bracket(M,v)
    b0=_curl_without_background(a,ea)-Ta+.5*_curl_bracket(a,a)
    b1=Ta-2*M;b2=2*M
    v0=_curl_without_background(v,ev)-Tv+_curl_bracket(a,v);v1=Tv
    inner=lambda x,y:np.einsum('p,...p->...',hw,np.sum(x*y,axis=(-1,-2)))
    polynomial=[inner(b0,v0),inner(b1,v0)+inner(b0,v1),
                inner(b2,v0)+inner(b1,v1),inner(b2,v1)]
    mt,mr,mv=(inner(M,x) for x in (vt,vr,v))
    avv=[inner(at,vt),inner(at,vr)+inner(ar,vt),inner(ar,vr)]
    arv=inner(ar,vr);av=inner(at,v);arv0=inner(ar,v)
    size=coefficient_jets['coordinate_count'];count=v.shape[1]
    accum=[Jet.constant(0.,size) for _ in range(count)]
    time=[Jet.constant(0.,size) for _ in range(count)]
    radial=[Jet.constant(0.,size) for _ in range(count)]
    for i,c in enumerate(coefficient_jets['rows']):
        e,r,d,b,l,lt,lr=(c[k] for k in ('electric','radial','angular','shift','connection_lambda','lambda_tau','lambda_rho'))
        normal=lt-b*lr
        for j in range(count):
            kinetic=normal*(mt[i,j]-b*mr[i,j])+avv[0][i,j]-b*avv[1][i,j]+b*b*avv[2][i,j]
            magnetic=sum((polynomial[k][i,j]*l**k for k in range(4)),Jet.constant(0.,size))
            accum[j] += w[i]*(e*kinetic-r*(lr*mr[i,j]+arv[i,j])-d*magnetic)
            time[j] += w[i]*e*(normal*mv[i,j]+av[i,j]-b*arv0[i,j])
            radial[j] += w[i]*(-b*e*(normal*mv[i,j]+av[i,j]-b*arv0[i,j])-r*(lr*mv[i,j]+arv0[i,j]))
    unpack=lambda jj:dict(values=np.array([x.value for x in jj]),
                          geometric_jacobian=np.array([x.gradient for x in jj]),
                          geometric_hessians=np.array([x.hessian for x in jj]))
    return dict(weak=unpack(accum),temporal_momentum_test=unpack(time),
                radial_momentum_test=unpack(radial), clock=coefficient_jets['clock'],
                independent_gauge_coefficients_moved=False,
                background_connection_motion_count=1,
                normalization='per kappa1/SAME embedding index; unit-Tr16 basis',
                temporal_contact='final plus, initial minus',radial_contact='wall plus, pole minus',
                temporal_radial_Gauss_rows_replaced=False, complete_native_action=False)


def retained_background_mixed_application(repository, *, points=96, test_order=8, clock='coordinate_time'):
    """Evaluate a common-basis background coefficient block, not a saddle."""
    from numpy.polynomial.legendre import leggauss
    from .muon_parent_retarded_hypercharge import regular_radial_basis
    x,w=leggauss(points);rho=(x+1)*WALL/2;w=w*WALL/2
    q,v,m=retained_state(repository)
    c=geometric_connection_coefficient_jets(12,q,v,m,rho,clock=clock)
    H,Hr=regular_radial_basis(rho,test_order)
    M=np.sqrt(8)*np.column_stack((np.eye(3),np.zeros(3)))
    tests=H[:,:,None,None,None]*M
    tests_rho=Hr[:,:,None,None,None]*M
    zeros=np.zeros((points,1,3,4))
    out=spatial_maxwell_weak_geometric_jets(c,w,np.ones(1),
        gauge=zeros,gauge_tau=zeros,gauge_rho=zeros,gauge_angular=np.zeros((points,1,3,3,4)),
        tests=tests,tests_tau=np.zeros_like(tests),tests_rho=tests_rho,
        tests_angular=np.zeros((points,test_order+1,1,3,3,4)))
    return dict(application=out,coefficient_jets=c,rho=rho,quadrature=w,
                scope='EVALUATED_RETAINED_MECHANICAL_BACKGROUND_SPATIAL_GAUGE_GEOMETRY_WEAK_BLOCK',
                independent_gauge_reference='zero independent fluctuation at this coefficient reference; not a physical primal solve',
                stationary_E1_claim=False,physical_Pauli_contraction=False)


def materialize(output, repository=None):
    """Store the evaluated actual-reference mixed application reproducibly.

    The independent gauge fluctuation is zero at this coefficient reference;
    this is not a stationary full-field base.  The radial tests are numerical
    applications of the finite-energy representation, not a physical drive.
    """
    from .muon_birth_candidate_geometry_action import ROOT, RESET_RECEIPT, STATE_SOURCE
    from .muon_parent_retarded_hypercharge import SOURCE, _deterministic_npz
    repository=ROOT if repository is None else Path(repository)
    output=Path(output)
    if output.exists():
        raise FileExistsError('preserve prior evidence; use a new output directory')
    result=retained_background_mixed_application(repository)
    arrays=dict(rho=result['rho'],quadrature=result['quadrature'])
    for group,entries in result['application'].items():
        if isinstance(entries,dict):
            arrays.update({group+'_'+k:v for k,v in entries.items() if isinstance(v,np.ndarray)})
    for name in result['coefficient_jets']['rows'][0]:
        entries=[row[name] for row in result['coefficient_jets']['rows']]
        arrays['coefficient_'+name+'_values']=np.array([row.value for row in entries])
        arrays['coefficient_'+name+'_jacobian']=np.array([row.gradient for row in entries])
        arrays['coefficient_'+name+'_normal_hessian_columns']=np.array([row.hessian[:,-2:] for row in entries])
    output.mkdir(parents=True)
    _deterministic_npz(output/'application.npz',arrays)
    app=result['application'];weak=app['weak']
    refs=[STATE_SOURCE,RESET_RECEIPT,SOURCE,
          'src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',
          'src/bhsm/interface/muon_parent_maxwell_background_euler.py',
          'src/bhsm/interface/muon_parent_retarded_hypercharge.py',
          'src/bhsm/interface/muon_moving_geometric_action.py',
          'src/bhsm/interface/muon_matched_mechanical_source.py']
    receipt=dict(scope=result['scope'],
        input_hashes={p:sha256((repository/p).read_bytes()).hexdigest() for p in refs},
        representation=dict(radial_test_order=8,radial_quadrature_order=96,
            angular_rule='exact constant right-Maurer spatial background; Haar average one',
            radial_tests='CONTROL_ONLY finite-energy Jacobi representation and wall lift',
            clock=app['clock'],coordinate_count=result['coefficient_jets']['coordinate_count'],
            chart=result['coefficient_jets']['chart']),
        normalization=app['normalization'],
        weak_Euler=weak['values'].tolist(),
        geometric_jacobian_norm=float(np.linalg.norm(weak['geometric_jacobian'])),
        normal_value_mixed_column=weak['geometric_jacobian'][:,-2].tolist(),
        normal_rate_mixed_column=weak['geometric_jacobian'][:,-1].tolist(),
        temporal_momentum_test=app['temporal_momentum_test']['values'].tolist(),
        radial_momentum_test=app['radial_momentum_test']['values'].tolist(),
        temporal_contact=app['temporal_contact'],radial_contact=app['radial_contact'],
        independent_gauge_reference=result['independent_gauge_reference'],
        independent_gauge_coefficients_moved=app['independent_gauge_coefficients_moved'],
        background_connection_motion_count=app['background_connection_motion_count'],
        temporal_radial_Gauss_rows_replaced=False,
        source_value=0.,source_rate=0.,trial_normal=1.,
        primal_acceleration_evaluated=False,stationary_E1_claim=False,
        complete_native_action=False,physical_Pauli_contraction=False,
        error_scope='binary64 finite representation and radial quadrature; no continuum tail or stationary-base enclosure')
    (output/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',
                                    encoding='utf8',newline='\n')
    return receipt


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(materialize(args.output),sort_keys=True))
