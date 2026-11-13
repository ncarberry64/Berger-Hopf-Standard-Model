"""Same-vector intrinsic Higgs/gauge/geometry weak action applications.

The numerical basis represents unknown doublets and gauge traces. It selects
no Higgs background or formation mode. The mechanical sigma1 connection and
the moving trace are constructed from their retained action owners. All cross
derivatives come from this one signed scalar action, including real-linear
conjugate Higgs variation. The quantum determinant load is a separate sector.
"""
from __future__ import annotations

import math
import numpy as np

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .bhsm_standard_model_gauge_vertices import su2_fundamental_generators
from .muon_intrinsic_lepton_primal import classical_bosonic_body_source


def higgs_u2_real_representation():
    """Unit-Tr16 connection basis on the owned Y_H=1/2 doublet.

    H_i=-i T_i/sqrt(2), H_Y=-i Y/sqrt(10/3). Thus sqrt(8)H_i
    represents jmath_i=-i sigma_i, with [H_i,H_j]=eps_ijk H_k/sqrt(2).
    This is a bundle representation, not an equality of the full physical
    gauge connection with its mechanical reference.
    """
    from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
    owned=retained_higgs_spin_charge_representation()
    if owned['higgs_hypercharge_exact']!='1/2':
        raise ValueError('retained Higgs hypercharge changed')
    weak=-1j*np.asarray(su2_fundamental_generators())/math.sqrt(2)
    hyper=-.5j*np.eye(2)/math.sqrt(10/3)
    complex_generators=np.concatenate((weak,hyper[None]))
    real=np.array([np.block([[a.real,-a.imag],[a.imag,a.real]]) for a in complex_generators])
    return dict(complex_generators=complex_generators,real_generators=real,
        scalar_order=('Re H1','Re H2','Im H1','Im H2'),
        internal_order=('unitTr16 H1','unitTr16 H2','unitTr16 H3','unitTr16 HY'),
        mechanical_generator_factor=math.sqrt(8), hypercharge='1/2',
        mechanical_owner='muon_intrinsic_higgs_connection.mechanical_higgs_connection_two_jet',
        unit_basis_owner='muon_matched_mechanical_source.realize')


def _lift(jet,size):
    if not isinstance(jet,Jet):
        raise ValueError('same material-chart geometric Jet required')
    old=len(jet.gradient)
    if old>size:
        raise ValueError('geometric coordinate count exceeds common vector')
    gradient=np.zeros(size);gradient[:old]=jet.gradient
    hessian=np.zeros((size,size));hessian[:old,:old]=jet.hessian
    return Jet(jet.value,gradient,hessian)


def _linear_maps(maps,variables,size):
    result=np.empty(maps.shape[:-1],dtype=object)
    for index in np.ndindex(result.shape):
        result[index]=sum((float(c)*variables[j] for j,c in enumerate(maps[index]) if c),Jet.constant(0.,size))
    return result


def intrinsic_higgs_gauge_action_jet(weights,*,scalar_coefficients,
        scalar_value_map,scalar_derivative_map,gauge_coefficients,gauge_trace_map,
        angular_quadrature,lambda_H,nu_squared_action=None,
        nu_squared_GeV_squared=None,log_energy_unit_GeV=None):
    """Construct S_H and its full common-vector gradient/Hessian.

    Coordinate order is the inherited geometry two-jet, real scalar
    coefficients, real gauge coefficients, and optionally log(E_unit/GeV).
    Values and ordinary derivatives are maps of the SAME scalar vector;
    every gauge trace is a map of the SAME five-component gauge vector.
    The temporal trace is A_t+2*wall_rate*A_rho because rho=2chi. This
    embedding motion is counted once. Spatial maps use unit-S3 derivatives.

    The action has physical intrinsic angular measure2*pi^2; a coupled cap
    application must apply its explicit orbit-volume normalization. Body
    J_H=0 is action-derived Grassmann-body provenance, not a deletion of the
    independent quantum/native load. A finite iterate is not stationary.
    The optional energy-unit variable evaluates the dimensional conversion
    nu_action^2=nu_GeV^2/E_unit^2; it does not invent its matching equation.
    """
    arrays=(scalar_coefficients,scalar_value_map,scalar_derivative_map,
            gauge_coefficients,gauge_trace_map,angular_quadrature)
    if any(not np.isrealobj(x) for x in arrays):
        raise ValueError('explicit realification required; no silent complex coefficient projection')
    c,V,D,g,A,w=(np.asarray(x,float) for x in arrays)
    if c.ndim!=1 or g.ndim!=1 or w.ndim!=1 or len(w)==0:
        raise ValueError('common finite scalar/gauge coefficient vectors and angular rule required')
    p=len(w)
    if V.shape!=(p,4,len(c)) or D.shape!=(p,4,4,len(c)) or A.shape!=(p,5,4,len(g)):
        raise ValueError('common scalar values/derivatives and five-component trace maps required')
    if any(not np.isfinite(x).all() for x in (c,V,D,g,A,w)) or np.any(w<=0):
        raise ValueError('finite maps and positive angular weights required')
    if not np.isclose(w.sum(),1,rtol=0,atol=1e-12):
        raise ValueError('angular quadrature must average one; Haar volume is in the action')
    lam=float(lambda_H)
    if not math.isfinite(lam) or lam<=0:
        raise ValueError('positive dimensionless owned lambda_H required')
    geometry_count=len(weights['wT'].gradient)
    scale_variable=log_energy_unit_GeV is not None
    size=geometry_count+len(c)+len(g)+int(scale_variable)
    variables=[]
    for j,value in enumerate(np.concatenate((c,g))):
        tangent=np.zeros(size);tangent[geometry_count+j]=1
        variables.append(Jet.affine(float(value),tangent))
    H=_linear_maps(V,variables[:len(c)],size)
    ordinary=_linear_maps(D,variables[:len(c)],size)
    gauge=_linear_maps(A,variables[len(c):],size)
    if scale_variable:
        if nu_squared_action is not None or nu_squared_GeV_squared is None:
            raise ValueError('one explicit Higgs-unit convention required')
        tangent=np.zeros(size);tangent[-1]=1
        ell=Jet.affine(float(log_energy_unit_GeV),tangent)
        nu2=float(nu_squared_GeV_squared)*(-2*ell).exp()
    else:
        if nu_squared_GeV_squared is not None or nu_squared_action is None:
            raise ValueError('explicit nu_squared_action or joint energy-unit coordinate required')
        nu2=Jet.constant(float(nu_squared_action),size)
    if not math.isfinite(nu2.value) or nu2.value<0:
        raise ValueError('finite nonnegative Higgs potential center required')
    rep=higgs_u2_real_representation();generators=rep['real_generators']
    wm=(_lift(weights[k],size) for k in ('wT','wS','wV'))
    wt,ws,wv=wm
    h=_lift(weights['mechanical_connection_lambda'],size)-1
    wall_rate=_lift(weights['wall_rate'],size)
    covariant=np.empty((p,4,4),dtype=object)
    scalar=Jet.constant(0.,size)
    polynomial=[Jet.constant(0.,size) for _ in range(3)]
    for point in range(p):
        for direction in range(4):
            for i in range(4):
                term=ordinary[point,direction,i]
                for internal in range(4):
                    connection=(gauge[point,0,internal]+2*wall_rate*gauge[point,1,internal]
                                if direction==0 else gauge[point,direction+1,internal])
                    if direction>0 and internal==direction-1:
                        connection=connection+math.sqrt(8)*h
                    if generators[internal,i].any():
                        applied=sum((float(generators[internal,i,j])*H[point,j]
                                     for j in range(4) if generators[internal,i,j]),Jet.constant(0.,size))
                        term=term+connection*applied
                covariant[point,direction,i]=term
        norm2=sum((x*x for x in H[point]),Jet.constant(0.,size))
        kinetic=wt*sum((x*x for x in covariant[point,0]),Jet.constant(0.,size))
        spatial=ws*sum((x*x for x in covariant[point,1:].flat),Jet.constant(0.,size))
        scalar=scalar+2*math.pi**2*w[point]*(kinetic-spatial-wv*lam*(norm2-nu2)**2)
        measure=2*math.pi**2*w[point]
        polynomial[0]=polynomial[0]+measure*(kinetic-spatial-wv*lam*norm2**2)
        polynomial[1]=polynomial[1]+measure*2*wv*lam*norm2
        polynomial[2]=polynomial[2]-measure*wv*lam
    body=classical_bosonic_body_source(p)
    values=lambda a:np.array([x.value for x in a.flat]).reshape(a.shape)
    return dict(action=scalar,H_real=values(H),DH_real=values(covariant),
        nu_squared_polynomial_coefficients=tuple(polynomial),
        nu_squared_polynomial_identity='S_H=S_H0+nu_action^2*S_H1+(nu_action^2)^2*S_H2; shared parameter, no branch/sample selection',
        geometric_count=geometry_count,scalar_slice=(geometry_count,geometry_count+len(c)),
        gauge_slice=(geometry_count+len(c),geometry_count+len(c)+len(g)),
        energy_unit_index=size-1 if scale_variable else None,
        nu_squared_action_evaluated=nu2.value,
        normalization='physical intrinsic S3 angular measure2*pi^2; coordinate time; real (+---) action',
        pairing='real gradient of S_H; equals2Re(complex weak dual)',
        mechanical_connection_motion_count=1,embedding_gauge_trace_motion_count=1,
        temporal_mechanical_zero_owner='sigma1 body reference Omega_bar=(lambda-1)jmath_i sigma1_i has no dt/drho component',
        classical_body_source_provenance=body['classification'],
        quantum_native_H_load_included=False,physical_background_selected=False,
        stationarity_claim=False,physical_Pauli_contraction=False)
