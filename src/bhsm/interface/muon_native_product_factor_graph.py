"""Reached intrinsic product-factor graph on the retained common family.

The input is the finite-family coefficient vector, not a supplied
positive pencil.  This module evaluates its actual scalar, gauge and metric
maps and calls the owned canonical spatial/mass Hamiltonian producer.  Its
temporal factor uses the same unitary bundle covariant derivative, rather
than the Lorentz Hamiltonian's -i Omega_tau.  This is a covariant component
extension of the separated factor; it is not a global native/Wick certificate.

The whole constant-angular 18-component trial image is kept.  The family
uses sigma1 in the right body frame and angular-constant H/independent A,
so these component operators preserve this angular trial space exactly.
No claim is made about the child's Ad_g patch or the whole stratified core.
Both temporal endpoint traces remain free.  They are not E0 or a canonical
stop; an exterior/reset application must subsequently attach them.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import solve, eigh
from scipy import sparse
from scipy.sparse.linalg import splu

from .aether_hybrid_standard_model_bundle_v15_53 import yukawa_and_anomaly_ledger
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_native_dirac_hamiltonian import (
    canonical_lepton_hamiltonian_maps, electromagnetic_hamiltonian_source_maps,
    lepton_current_hilbert_representation,
)
from .muon_parent_gauge_geometry_correction import finite_common_iterate_at_time, compact_temporal_basis
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL


def _finite(value, name, shape=None, real=False):
    if value is None:
        raise ValueError(f'{name} is required')
    if real and not np.isrealobj(value):
        raise ValueError(f'explicit real {name} required; no imaginary projection')
    result = np.asarray(value, dtype=float if real else complex)
    if not np.isfinite(result).all() or (shape is not None and result.shape != shape):
        raise ValueError(f'finite {name} with shape {shape} required')
    return result


def lepton_unit_trace_gauge_representation():
    """Retained unit-Tr16 Sp1/U1 generators on all eighteen Weyl entries."""
    charges = yukawa_and_anomaly_ledger()['charges']
    if charges['L'] != '-1/2' or charges['e_c'] != '1':
        raise ValueError('retained lepton hypercharge ledger changed')
    weak = retained_higgs_spin_charge_representation()['higgs_su2_generators']
    result = np.zeros((4, 18, 18), complex)
    for a in range(3):
        result[a, :12, :12] = -1j*np.kron(weak[a], np.eye(6))/math.sqrt(2)
    # e_R is the conjugate of the retained left e_c ledger entry.
    Y = np.diag(np.r_[-.5*np.ones(12), -np.ones(6)])
    result[3] = -1j*Y/math.sqrt(10/3)
    return dict(generators=result, hypercharge=Y,
        component_order='unitTr16 H1,H2,H3,HY',
        owner='muon_intrinsic_higgs_gauge_action.higgs_u2_real_representation',
        physical_EM_generator=lepton_current_hilbert_representation()['EM_charge'])


def finite_common_family_intrinsic_operator(time, coefficients, representation, reference):
    """Evaluate this family's actual intrinsic sigma1 fields and operator.

    Gauge coefficients are MATERIAL_REFERENCE one-form components.  Their
    exact intrinsic temporal trace is A_t_ref, then divided by induced
    lapse for proper clock.  Eulerian radial advection cancels the chart
    conversion; adding 2 wall_rate A_rho_ref again would double count it.
    Spatial mechanical M*(lambda-1) is added once.
    No mean/compact scalar coordinate or gauge field is substituted by zero.
    """
    c = _finite(coefficients, 'coupled coefficients', (representation['count'],), real=True)
    if not representation.get('include_scalar_mean'):
        raise ValueError('retained scalar mean coordinate must be included')
    data = finite_common_iterate_at_time(time, c, representation, reference, rho=np.array([WALL]))
    weight = intrinsic_m4_weight_jet(12, data['q'], data['qdot'], data['m'],
        source_value=data['normal'], source_rate=data['normal_rate'])
    N, R4 = float(weight['induced_lapse'].value), float(weight['R4'].value)
    lam, wall_rate = float(weight['mechanical_connection_lambda'].value), float(weight['wall_rate'].value)
    b, _ = compact_temporal_basis(np.array([time]), representation['length'])
    hc = c[representation['scalar_start']:]
    h_real = b[0]*hc[:4]+hc[4:8]
    H = (h_real[:2]+1j*h_real[2:])[None]
    field = data['fields']['gauge'][0, 0]
    spatial = field[2:]+M*(lam-1)
    coordinate_temporal = field[0]
    generators = lepton_unit_trace_gauge_representation()['generators']
    omega_t = np.einsum('a,aij->ij', coordinate_temporal, generators)
    omega_s = np.einsum('pa,aij->pij', spatial, generators)
    connection = np.concatenate(((omega_t/N)[None], omega_s))[None]
    operator = canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
        spatial_derivative_map=np.zeros((1, 3, 18, 18)), H=H, R4=R4,
        gauge_connection=connection)
    return dict(N=N, R4=R4, H=H[0], lambda_geom=lam, wall_rate=wall_rate,
        Omega_t=omega_t, Omega_tau_Lorentz=omega_t/N,
        W=operator['spatial_mass_hamiltonian_map'][0],
        H_can=operator['hamiltonian_map'][0],
        common_coefficients=c, full18_frame=operator['frame_order'],
        temporal_trace_equation='Omega_t=rho_L(At_ref); At_phys=At_ref-rhodot Ar_ref/J and Ar_phys=Ar_ref/J imply At_phys+rhodot Ar_phys=At_ref; Omega_tau=Omega_t/Ninduced',
        temporal_pullback_owner='muon_material_higgs_gauge_action.material_intrinsic_higgs_gauge_action_jet',
        physical_wall_velocity_set_to_zero=False,
        mechanical_patch='parent_sigma1: unit-S3 coefficient lambda_geom-1, right body frame',
        angular_complement_invariance='E_a 1=0; H and A components are angular-constant in this retained sigma1 family; W maps C18 tensor span{1} into itself',
        outside_constant_angular_image_residual=0.,
        scope='actual finite130 parameter trial on outgoing branch24 E1+ germ; not incoming temporal C1 or stationary native base')


def finite_family_temporal_frame_transport(*, coefficients, representation, reference,
        times, initial_frame, rtol, atol):
    """Execute Sdot_t=-Omega_t S and retain the endpoint holonomy.

    S is a frame transport, not a selected matter state or birth reset.
    The initial frame is supplied explicitly.  In the transported frame
    U=S^dagger, Omega'_t=0.  W'=U W U^dagger and trace maps keep endpoint U.
    This does not assert a Lorentz-to-native analytic continuation.
    """
    ts = _finite(times, 'coordinate time samples', real=True)
    if ts.ndim != 1 or len(ts)<2 or np.any(np.diff(ts)<=0):
        raise ValueError('strictly future coordinate time samples required')
    if ts[0]<-representation['length'] or ts[-1]>0:
        raise ValueError('frame transport cannot extrapolate the retained local family')
    if not all(math.isfinite(x) and x>0 for x in (rtol, atol)):
        raise ValueError('positive explicit numerical tolerances required')
    initial = _finite(initial_frame, 'initial frame identification', (18,18))
    if np.max(abs(initial.conj().T@initial-np.eye(18)))>1e-12:
        raise ValueError('unitary initial frame identification required')
    for alpha in lepton_current_hilbert_representation()['alpha']:
        if np.max(abs(alpha@initial-initial@alpha))>1e-12:
            raise ValueError('internal unitary gauge initial frame required; spin/coframe change is separate')
    def rhs(t, flattened):
        omega = finite_common_family_intrinsic_operator(t, coefficients, representation, reference)['Omega_t']
        return (-omega@flattened.reshape(18,18)).ravel()
    solution = solve_ivp(rhs,(ts[0],ts[-1]),initial.ravel(),t_eval=ts,
                         method='DOP853',rtol=rtol,atol=atol)
    if not solution.success:
        raise RuntimeError(solution.message)
    S = solution.y.T.reshape(len(ts),18,18)
    return dict(times=ts, parallel_frame=S, temporal_gauge_frame=S.conj().transpose(0,2,1),
        endpoint_holonomy=S[-1],
        unitarity_residual=float(np.max(abs(S.conj().transpose(0,2,1)@S-np.eye(18)))),
        numerical_method='DOP853', rtol=rtol, atol=atol,
        graph_law='T_temporal_frame=U_child T_owned U_parent_dagger; endpoint holonomy not discarded',
        source_jets='For the fixed-field spatial photon partial used by the core below, delta Omega_t=0 and frame first/mixed source jets exactly zero. Total coupled source jets require differentiating this same IVP.',
        actual_reset_lift_selected=False, analytic_continuation_certified=False,
        native_heat_permitted=False)


def finite_family_retarded_source_transport(*, coefficients, representation, reference,
        times, electromagnetic_coupling, spatial_photon_component,
        source_v_nodes, source_J_nodes, rtol, atol):
    """Retarded Lorentz fundamental solution and its advanced form adjoint.

    U(t0,t0)=I is the definition of a fundamental operator, not a reset or
    selected fermion state.  Source jets solve the differentiated IVP with
    BOTH ordered insertions.  This is distinct from product-factor heat.
    """
    ts=_finite(times,'future source transport times',real=True)
    if ts.ndim!=1 or len(ts)<2 or np.any(np.diff(ts)<=0):
        raise ValueError('strictly future source transport times required')
    if ts[0]<-representation['length'] or ts[-1]>0:
        raise ValueError('source transport cannot extrapolate the retained family')
    if type(spatial_photon_component) is not int or spatial_photon_component not in (1,2,3):
        raise ValueError('declared spatial photon component1,2,3 required')
    sv=_finite(source_v_nodes,'source v profile',ts.shape,real=True)
    sj=_finite(source_J_nodes,'source J profile',ts.shape,real=True)
    if not all(math.isfinite(x) and x>0 for x in (rtol,atol)):
        raise ValueError('positive explicit numerical tolerances required')
    initial=np.zeros((4,18,18),complex);initial[0]=np.eye(18)
    def rhs(t,flattened):
        u,uv,uJ,uvJ=flattened.reshape(4,18,18)
        d=finite_common_family_intrinsic_operator(t,coefficients,representation,reference)
        G=-1j*d['N']*d['W']-d['Omega_t']
        one=np.zeros((1,4));one[0,spatial_photon_component]=1
        Xi=electromagnetic_hamiltonian_source_maps(value_map=np.eye(18)[None],
            R4=d['R4'],photon_one_form=one,electromagnetic_coupling=electromagnetic_coupling,
            delta_H=np.zeros((1,2),complex))['spatial_mass_source_operator'][0]
        Gv=-1j*d['N']*np.interp(t,ts,sv)*Xi
        GJ=-1j*d['N']*np.interp(t,ts,sj)*Xi
        return np.array([G@u,G@uv+Gv@u,G@uJ+GJ@u,
                         G@uvJ+Gv@uJ+GJ@uv]).ravel()
    sol=solve_ivp(rhs,(ts[0],ts[-1]),initial.ravel(),t_eval=ts,method='DOP853',rtol=rtol,atol=atol)
    if not sol.success:raise RuntimeError(sol.message)
    u=sol.y.T.reshape(len(ts),4,18,18)
    final=u[-1,0]
    # U(t,E1) is the advanced-adjoint kernel paired to U(E1,t).
    advanced=u[:,0]@final.conj().T
    return dict(times=ts,retarded_fundamental=u[:,0],retarded_v=u[:,1],
        retarded_J=u[:,2],retarded_vJ=u[:,3],advanced_adjoint_to_final=advanced,
        source_equation='Udot=(-i N W-Omega_t)U; U_vJdot=G U_vJ+G_v U_J+G_J U_v',
        unitarity_residual=float(np.max(abs(u[:,0].conj().transpose(0,2,1)@u[:,0]-np.eye(18)))),
        advanced_endpoint_identity_residual=float(np.linalg.norm(advanced[-1]-np.eye(18))),
        genuine_mixed_generator_zero_scope='declared fixed-field affine spatial photon partial only',
        source_state_selected=False,native_heat_or_Pauli_evaluated=False,
        rtol=rtol,atol=atol,method='DOP853')


def finite_family_source_paired_core(*, coefficients, representation, reference,
        time_nodes, negative_spectral_parameter, electromagnetic_coupling,
        spatial_photon_component, source_v_nodes, source_J_nodes, quadrature_order):
    """Produce the core from A maps, then Poisson/adjoint/contact pairings.

    A=(partial_t+Omega_t)/N+W and d_tau=N dt.  The negative-axis probe
    adds (-z)||u||^2.  Both endpoint traces are exported, never identified
    with physical E0/stop.  Sources are explicitly fixed-field partials on
    a declared unit-S3 spatial one-form; their total field/domain response
    remains a subsequent coupled application.  All18 entries are retained.
    """
    nodes = _finite(time_nodes, 'coordinate time nodes', real=True)
    if nodes.ndim != 1 or len(nodes)<3 or np.any(np.diff(nodes)<=0):
        raise ValueError('at least three strictly future core nodes required')
    if nodes[0] < -representation['length'] or nodes[-1] > 0:
        raise ValueError('core cannot extrapolate the retained local coefficient family')
    z = float(negative_spectral_parameter)
    if not math.isfinite(z) or z>=0:
        raise ValueError('explicit finite negative-axis spectral probe required')
    if type(quadrature_order) is not int or quadrature_order<2:
        raise ValueError('explicit quadrature order >=2 required')
    if type(spatial_photon_component) is not int or spatial_photon_component not in (1,2,3):
        raise ValueError('declared spatial photon one-form component1,2,3 required')
    sv = _finite(source_v_nodes, 'source v nodal profile', nodes.shape, real=True)
    sj = _finite(source_J_nodes, 'source J nodal profile', nodes.shape, real=True)
    dimension = 18*len(nodes)
    forms = {key:np.zeros((dimension,dimension),complex) for key in ('M','K','v','J','vJ')}
    gx, gw = np.polynomial.legendre.leggauss(quadrature_order)
    snapshots=[]
    for cell,(lo,hi) in enumerate(zip(nodes[:-1],nodes[1:])):
        h=hi-lo
        local={key:np.zeros((36,36),complex) for key in forms}
        for x,w in zip((gx+1)/2,gw*h/2):
            t=lo+h*x; data=finite_common_family_intrinsic_operator(t,coefficients,representation,reference)
            N,R = data['N'],data['R4']
            V=np.concatenate(((1-x)*np.eye(18),x*np.eye(18)),axis=1)
            Dt=np.concatenate((-np.eye(18)/h,np.eye(18)/h),axis=1)
            A=(Dt+data['Omega_t']@V)/N+data['W']@V
            one_form=np.zeros((1,4));one_form[0,spatial_photon_component]=1
            Xi=electromagnetic_hamiltonian_source_maps(value_map=np.eye(18)[None],
                R4=R,photon_one_form=one_form,electromagnetic_coupling=electromagnetic_coupling,
                delta_H=np.zeros((1,2),complex))['spatial_mass_source_operator'][0]
            Av=((1-x)*sv[cell]+x*sv[cell+1])*Xi@V
            AJ=((1-x)*sj[cell]+x*sj[cell+1])*Xi@V
            weight=w*N*2*np.pi**2
            local['M']+=weight*(V.conj().T@V)
            local['K']+=weight*(A.conj().T@A)
            local['v']+=weight*(Av.conj().T@A+A.conj().T@Av)
            local['J']+=weight*(AJ.conj().T@A+A.conj().T@AJ)
            local['vJ']+=weight*(Av.conj().T@AJ+AJ.conj().T@Av)
            snapshots.append((t,N,R))
        sl=slice(18*cell,18*(cell+2))
        for key in forms: forms[key][sl,sl]+=local[key]
    H=forms['K']-z*forms['M']
    boundary=np.r_[np.arange(18),np.arange(dimension-18,dimension)]
    interior=np.arange(18,dimension-18)
    E=np.zeros((dimension,36),complex);E[boundary]=np.eye(36)
    E[interior]=-solve(H[np.ix_(interior,interior)],H[np.ix_(interior,boundary)],assume_a='pos')
    S=E.conj().T@H@E
    def interior_inverse(rhs):
        out=np.zeros_like(rhs)
        out[interior]=solve(H[np.ix_(interior,interior)],rhs[interior],assume_a='pos')
        return out
    vE=forms['v']@E;JE=forms['J']@E
    GvE,GJE=interior_inverse(vE),interior_inverse(JE)
    direct=E.conj().T@forms['vJ']@E
    pair_vJ=vE.conj().T@GJE
    pair_Jv=JE.conj().T@GvE
    mixed=direct-pair_vJ-pair_Jv
    return dict(core_forms=forms,negative_axis_form=H,Poisson_map=E,
        paired_two_endpoint_graph=S,graph_v=E.conj().T@forms['v']@E,
        graph_J=E.conj().T@forms['J']@E,graph_vJ=mixed,
        source_square_contact=direct,two_insertion_vJ=pair_vJ,two_insertion_Jv=pair_Jv,
        genuine_mixed_factor_jet=np.zeros_like(direct),
        genuine_mixed_zero_scope='Exact ONLY for the declared affine spatial-photon, fixed H/geometry/basis/domain partial; not a total physical source jet',
        boundary_coefficient_indices=boundary,interior_coefficient_indices=interior,
        temporal_core_nodes=nodes,quadrature_geometry_samples=np.array(snapshots),
        equations='S_vJ=E_dagger H_vJ E-E_dagger H_v G_D H_J E-E_dagger H_J G_D H_v E',
        Poisson_interior_residual=float(np.linalg.norm((H@E)[interior])),
        adjoint_pair_residual=float(np.linalg.norm(pair_Jv-pair_vJ.conj().T)),
        graph_Hermitian_residual=float(np.linalg.norm(S-S.conj().T)),
        full_constant_angular_image_dimension=18,
        outside_constant_angular_image_residual=0.,
        angular_complement_proof='sigma1 right-body A components and H are angular-constant; E_a1=0; factor and photon spatial insertions preserve all18 constant-angular entries. No global/child Ad_g invariance claimed.',
        factor_scope='covariant product component using retained unitary connection; no Lorentz square or Wick equality',
        adjoint_scope='same fixed-core positive-form Dirichlet adjoint; not advanced child physical propagation',
        physical_endpoint_or_reset_conditions_selected=False,
        total_coupled_source_domain_jets_evaluated=False,
        full_native_heat_or_Pauli_evaluated=False)


def reset_graph_in_temporal_frames(*, owned_reset_lift, parent_frame, child_frame):
    """Keep the owned reset while changing its two temporal bundle frames.

    The lift is required; it is never replaced by an identity.  This is a
    point-fiber coordinate application.  Spatial pullback/Jacobian and their
    jets remain in the actual worldvolume trace operator.
    """
    from .action_extension_global_spin_reset_ae2 import validate_unitary
    R=validate_unitary(_finite(owned_reset_lift,'owned reset lift',(18,18)))
    Up=validate_unitary(_finite(parent_frame,'parent temporal frame',(18,18)))
    Uc=validate_unitary(_finite(child_frame,'child temporal frame',(18,18)))
    T=Uc@R@Up.conj().T
    return dict(trace_map=T,positive_current_point_dual=T.conj().T,
        trace_equation='u_child_frame=T u_parent_frame',
        outward_conormal_equation='p_parent_frame+T_dagger p_child_frame=0',
        owner='action_extension_global_spin_reset_ae2.action_definition',
        endpoint_holonomies_discarded=False,
        spatial_pullback_or_global_domain_certified=False)


def reset_graph_jet_in_temporal_frames(*, owned_reset_jet, parent_frame_jet, child_frame_jet):
    """Source-paired trace/dual graph, including endpoint holonomy jets."""
    keys=('value','v','J','vJ')
    def jet(data,name):
        if not isinstance(data,dict) or any(k not in data for k in keys):
            raise ValueError(f'all value/v/J/vJ entries of {name} required')
        values={k:_finite(data[k],f'{name}.{k}',(18,18)) for k in keys}
        u=values['value'];v=values['v'];j=values['J'];m=values['vJ']
        if max(np.linalg.norm(u.conj().T@u-np.eye(18)),
               np.linalg.norm(v.conj().T@u+u.conj().T@v),
               np.linalg.norm(j.conj().T@u+u.conj().T@j),
               np.linalg.norm(m.conj().T@u+v.conj().T@j+j.conj().T@v+u.conj().T@m))>1e-10:
            raise ValueError(f'{name} must be a unitary frame two-jet')
        return values
    def product(a,b):
        return dict(value=a['value']@b['value'],
            v=a['v']@b['value']+a['value']@b['v'],
            J=a['J']@b['value']+a['value']@b['J'],
            vJ=a['vJ']@b['value']+a['v']@b['J']+a['J']@b['v']+a['value']@b['vJ'])
    R=jet(owned_reset_jet,'owned reset jet')
    Up=jet(parent_frame_jet,'parent endpoint frame jet')
    Uc=jet(child_frame_jet,'child endpoint frame jet')
    T=product(product(Uc,R),{k:x.conj().T for k,x in Up.items()})
    return dict(trace_map_jet=T,positive_current_point_dual_jet={k:x.conj().T for k,x in T.items()},
        equation='T=U_child R_owned U_parent_dagger; T_vJ includes all three genuine jets and both orders of every cross term',
        point_fiber_only=True,spatial_pullback_or_global_domain_certified=False,
        actual_reset_lift_selected=False)


def retained_eight_q_fermion_source_image(repository=None):
    """Actual raw-beta eight-source images from n0 into COMPLETE n1+n3.

    Q is a connection direction in the retained unit-Tr16 basis.  It is
    not a scalar electromagnetic charge, and no extra e or old T_b is
    multiplied into this raw convention.  Radial/time/native trace lifts
    and final charge matching are separate same-owner applications.
    """
    from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    angular=(retained_full_q_angular_space() if repository is None
             else retained_full_q_angular_space(repository))
    Q=angular['source_coefficients'][160:].reshape(3,4,20,8)
    if np.max(abs(angular['source_coefficients'][:160]))!=0:
        raise ValueError('retained raw eight-source must be spatial in this application')
    alpha=lepton_current_hilbert_representation()['alpha']
    generators=lepton_unit_trace_gauge_representation()['generators']
    image=-1j*np.einsum('iuv,cvw,ichA->Ahuw',alpha,generators,Q).reshape(8,360,18)
    # Unit-Haar real scalar basis; all4 n1 and all16 n3 functions retained.
    return dict(angular=angular,unit_radius_source_image=image,
        frame='harmonic then full18 Weyl fiber',
        source_coordinate='raw primitive betaPhoton in unit-Tr16 internal basis',
        raw_source_Gram=angular['source_gram'],
        normalized_source_Gram=angular['saved_normalized_source_gram'],
        normalization_relation='saved normalized Gram=(3/16)*raw Gram; raw Gram=(16/3)I8',
        extra_measured_e_or_old_T_b_applied=False,
        full_stratified_source_lift_evaluated=False)


def finite_family_eight_q_source_pairing(*, coefficients, representation, reference,
        time_nodes, negative_spectral_parameter, source_beta_nodes,
        quadrature_order, repository=None):
    """Actual source-directed n0 contact minus n1/n3 pair on the finite core.

    The full angular action space is (n0+n1+n3) tensor C18, dimension378.
    The operator is assembled shellwise from the actual common-family
    fields, right derivatives and positive factor.  Each pair uses the
    whole n1/n3 Dirichlet complement, not a compression to eight sources.
    Both n0 temporal endpoint traces remain unknown output coordinates.
    """
    source=retained_eight_q_fermion_source_image(repository)
    angular=source['angular'];D=angular['derivative_matrices']
    nodes=_finite(time_nodes,'source-directed time nodes',real=True)
    if nodes.ndim!=1 or len(nodes)<3 or np.any(np.diff(nodes)<=0):
        raise ValueError('at least three strictly future source-directed nodes required')
    if nodes[0]<-representation['length'] or nodes[-1]>0:
        raise ValueError('source-directed core cannot extrapolate the local family')
    beta=_finite(source_beta_nodes,'raw betaPhoton nodal profiles',(len(nodes),8),real=True)
    z=float(negative_spectral_parameter)
    if not math.isfinite(z) or z>=0:
        raise ValueError('explicit negative-axis probe required')
    if type(quadrature_order) is not int or quadrature_order<2:
        raise ValueError('explicit quadrature order>=2 required')
    labels=angular['harmonic_labels'];shells={n:np.array([i for i,l in enumerate(labels) if l[0]==n]) for n in (1,3)}
    cross=max(float(np.max(abs(D[:,shells[1]][:,:,shells[3]]))),
              float(np.max(abs(D[:,shells[3]][:,:,shells[1]]))))
    if cross>1e-12:
        raise ValueError('background derivative does not preserve the retained complete shells')
    alpha=lepton_current_hilbert_representation()['alpha']
    gx,gw=np.polynomial.legendre.leggauss(quadrature_order)
    samples=[]
    for cell,(lo,hi) in enumerate(zip(nodes[:-1],nodes[1:])):
        for x,w in zip((gx+1)/2,gw*(hi-lo)/2):
            t=lo+(hi-lo)*x
            d=finite_common_family_intrinsic_operator(t,coefficients,representation,reference)
            samples.append(dict(cell=cell,x=x,width=hi-lo,time=t,measure=w*d['N']*2*np.pi**2,
                N=d['N'],R=d['R4'],W0=d['W'],Omega_t=d['Omega_t'],
                beta=(1-x)*beta[cell]+x*beta[cell+1]))
    def shell_form(indices):
        count=1 if indices is None else len(indices);size=18*count
        identity=sparse.eye(size,format='csc',dtype=complex)
        if indices is None:
            principal=sparse.csc_matrix((size,size),dtype=complex)
        else:
            deriv=D[:,indices][:,:,indices]
            principal=sum((-1j*sparse.kron(sparse.csc_matrix(deriv[a]),
                sparse.csc_matrix(alpha[a]),format='csc') for a in range(3)),
                sparse.csc_matrix((size,size),dtype=complex))
        blocks=[[None for _ in nodes] for _ in nodes]
        for s in samples:
            i,x,h=s['cell'],s['x'],s['width']
            B=principal/s['R']+sparse.kron(sparse.eye(count),
                sparse.csc_matrix(s['W0']+s['Omega_t']/s['N']),format='csc')
            aa=(-identity/(h*s['N'])+(1-x)*B,identity/(h*s['N'])+x*B)
            phi=(1-x,x)
            for a in range(2):
                for b in range(2):
                    val=s['measure']*(aa[a].conj().T@aa[b]-z*phi[a]*phi[b]*identity)
                    previous=blocks[i+a][i+b]
                    blocks[i+a][i+b]=val if previous is None else previous+val
        # Explicitly sized zero blocks retain every endpoint and interior.
        zero=sparse.csc_matrix((size,size),dtype=complex)
        H=sparse.bmat([[zero if b is None else b for b in row] for row in blocks],format='csc')
        return H,principal,size
    H0,_,size0=shell_form(None);H0=H0.toarray()
    b0=np.r_[np.arange(18),np.arange(len(H0)-18,len(H0))]
    i0=np.arange(18,len(H0)-18)
    E0=np.zeros((len(H0),36),complex);E0[b0]=np.eye(36)
    E0[i0]=-solve(H0[np.ix_(i0,i0)],H0[np.ix_(i0,b0)],assume_a='pos')
    S0=E0.conj().T@H0@E0
    direct=np.zeros((8,8,36,36),complex);pair=np.zeros_like(direct)
    shell_results={}
    for n,indices in shells.items():
        Hn,principal,size=shell_form(indices)
        interior=np.arange(size,Hn.shape[0]-size)
        Hii=Hn[interior][:,interior].tocsc();factor=splu(Hii)
        forcing=np.zeros((Hn.shape[0],8,36),complex)
        image=source['unit_radius_source_image'].reshape(8,20,18,18)[:,indices].reshape(8,size,18)
        direct_n=np.zeros_like(direct)
        for s in samples:
            i,x,h=s['cell'],s['x'],s['width']
            u0=(1-x)*E0[18*i:18*(i+1)]+x*E0[18*(i+1):18*(i+2)]
            du0=(E0[18*(i+1):18*(i+2)]-E0[18*i:18*(i+1)])/h
            Au0=(du0+s['Omega_t']@u0)/s['N']+s['W0']@u0
            Xi=s['beta'][:,None,None]*image/s['R']
            Xiu=np.einsum('Aoi,ic->Aoc',Xi,u0)
            XiAu=np.einsum('Aoi,ic->Aoc',Xi,Au0)
            g=np.einsum('Aoi,Boj->ABij',Xiu.conj(),Xiu)
            direct_n+=s['measure']*(g+g.transpose(1,0,2,3))
            B=principal/s['R']+sparse.kron(sparse.eye(len(indices)),
                sparse.csc_matrix(s['W0']+s['Omega_t']/s['N']),format='csc')
            for endpoint,(phi,dphi) in enumerate(((1-x,-1/h),(x,1/h))):
                slab=slice((i+endpoint)*size,(i+endpoint+1)*size)
                for A in range(8):
                    forcing[slab,A]+=s['measure']*(dphi*Xiu[A]/s['N']
                        +phi*(B.conj().T@Xiu[A]+XiAu[A]))
        F=forcing[interior].reshape(len(interior),8*36)
        G= factor.solve(F)
        pair_n=(F.conj().T@G).reshape(8,36,8,36).transpose(0,2,1,3)
        direct+=direct_n;pair+=pair_n
        residual=float(np.linalg.norm(Hii@G-F)/max(1.,np.linalg.norm(F)))
        shell_results[str(n)]=dict(scalar_angular_count=len(indices),full18_shell_dimension=size,
            interior_dimension=len(interior),source_image_rank=int(np.linalg.matrix_rank(image.transpose(1,0,2).reshape(size,144))),
            source_square_contact=direct_n,ordered_two_insertion=pair_n,
            complementary_Poisson_application=G.reshape(len(interior),8,36),
            complementary_Poisson_residual_relative=residual,
            all_shell_columns_used=True,eight_source_compression_used=False)
    mixed=direct-pair-pair.transpose(1,0,2,3)
    return dict(source=source,n0_Poisson_map=E0,n0_two_endpoint_graph=S0,
        source_square_contact=direct,ordered_two_insertion=pair,
        opposite_order_two_insertion=pair.transpose(1,0,2,3),source_paired_graph_mixed=mixed,
        shell_applications=shell_results,temporal_core_nodes=nodes,
        full_source_action_space_dimension=378,complete_n0_constant_angular_fiber_dimension=18,
        higher_n_source_directed_core_remainder=0.,
        higher_n_remainder_proof='On this fixed sigma1 core, A/A_dagger and the Dirichlet Green preserve each complete PW shell. P_A n0 has only n1+n3. The second-derivative n0 row therefore uses exactly those Green blocks plus Xi_A_dagger Xi_B contact. This is not the whole heat supertrace or an exterior-domain tail theorem.',
        cross_shell_background_derivative_residual=cross,
        direct_contact_is_full_exact_Haar_pairing=True,
        genuine_mixed_factor_jet_zero_scope='affine raw-beta connection partial at fixed computed H/geometry/core/trace; total coupled genuine jets remain required',
        temporal_chart='At_ref/N; material advection counted once',
        normalization='raw betaPhoton unit-Tr16 connection derivative; no extra e,old T_b,Tr16Q² orfamily multiplicity inserted',
        physical_E0_stop_or_reset_domain_selected=False,
        physical_source_lift_or_total_domain_response_evaluated=False,
        complete_native_heat_or_Pauli_evaluated=False)


def _source_core_samples(coefficients, representation, reference, nodes, beta, order):
    """Actual coordinate-to-proper-clock coefficients at all core quadratures."""
    gx,gw=np.polynomial.legendre.leggauss(order)
    result=[]
    for cell,(lo,hi) in enumerate(zip(nodes[:-1],nodes[1:])):
        h=hi-lo
        for x,w in zip((gx+1)/2,gw*h/2):
            t=lo+h*x
            d=finite_common_family_intrinsic_operator(t,coefficients,representation,reference)
            result.append(dict(cell=cell,x=x,h=h,N=d['N'],R=d['R4'],W=d['W'],
                Omega_t=d['Omega_t'],weight=w*d['N']*2*np.pi**2,
                beta=(1-x)*beta[cell]+x*beta[cell+1]))
    return result


def _family_shell_heat_forms(samples, node_count, derivatives, fiber_indices):
    """Assemble A†A and its positive FE Gram on one complete PW shell."""
    count=1 if derivatives is None else derivatives.shape[1]
    size=6*count;dimension=size*node_count
    eye=np.eye(size)
    alpha=lepton_current_hilbert_representation()['alpha'][:,fiber_indices][:,:,fiber_indices]
    principal=(np.zeros((size,size),complex) if derivatives is None else
               -1j*sum(np.kron(derivatives[a],alpha[a]) for a in range(3)))
    K=np.zeros((dimension,dimension),complex);M0=np.zeros((dimension,dimension),complex)
    for s in samples:
        i,x,h=s['cell'],s['x'],s['h']
        W=s['W'][np.ix_(fiber_indices,fiber_indices)]
        omega=s['Omega_t'][np.ix_(fiber_indices,fiber_indices)]
        B=principal/s['R']+np.kron(np.eye(count),W+omega/s['N'])
        A=np.concatenate((-eye/(h*s['N'])+(1-x)*B,eye/(h*s['N'])+x*B),axis=1)
        V=np.concatenate(((1-x)*eye,x*eye),axis=1)
        ids=slice(i*size,(i+2)*size)
        K[ids,ids]+=s['weight']*(A.conj().T@A)
        M0[ids,ids]+=s['weight']*(V.conj().T@V)
    interior=np.arange(size,dimension-size)
    Ki=K[np.ix_(interior,interior)];Mi=M0[np.ix_(interior,interior)]
    # eigh(K,M) is exactly the M^(-1/2) Hilbert realification followed by
    # a unitary spectral basis: V† M V=I, V† K V=diag(lambda).
    eigenvalues,vectors=eigh(Ki,Mi,check_finite=True)
    if eigenvalues[0]<=0:
        raise ValueError('computed Dirichlet positive factor has no strictly positive spectral gap')
    residual=np.linalg.norm(Ki@vectors-(Mi@vectors)*eigenvalues)/max(1.,np.linalg.norm(Ki)*np.linalg.norm(vectors))
    return dict(K=Ki,M=Mi,eigenvalues=eigenvalues,vectors=vectors,size=size,
        principal=principal,interior=interior,
        generalized_eigen_residual_relative=float(residual),
        positive_Gram_orthogonality_residual=float(np.linalg.norm(vectors.conj().T@Mi@vectors-np.eye(len(interior)))))


def _family_source_heat_blocks(samples, node_count, image, zero, shell, fiber_indices):
    """Full cross-shell first jets and n0 Xi†Xi mixed contact, before heat."""
    size=shell['size'];d0=6*node_count;dn=size*node_count
    cross=np.zeros((8,dn,d0),complex)
    contact=np.zeros((8,8,d0,d0),complex)
    count=size//6;eye0=np.eye(6);eyen=np.eye(size)
    for s in samples:
        i,x,h=s['cell'],s['x'],s['h']
        W=s['W'][np.ix_(fiber_indices,fiber_indices)]
        omega=s['Omega_t'][np.ix_(fiber_indices,fiber_indices)]
        B0=W+omega/s['N']
        Bn=shell['principal']/s['R']+np.kron(np.eye(count),B0)
        A0=np.concatenate((-eye0/(h*s['N'])+(1-x)*B0,eye0/(h*s['N'])+x*B0),axis=1)
        An=np.concatenate((-eyen/(h*s['N'])+(1-x)*Bn,eyen/(h*s['N'])+x*Bn),axis=1)
        V0=np.concatenate(((1-x)*eye0,x*eye0),axis=1)
        Vn=np.concatenate(((1-x)*eyen,x*eyen),axis=1)
        Xi=s['beta'][:,None,None]*image/s['R']
        X0=Xi@V0
        xn=np.einsum('Aoi,ij->Aoj',Xi,A0)
        local=An.conj().T@X0+Vn.conj().T@xn
        cross[:,i*size:(i+2)*size,i*6:(i+2)*6]+=s['weight']*local
        g=np.einsum('Aki,Bkj->ABij',X0.conj(),X0)
        contact[:,:,i*6:(i+2)*6,i*6:(i+2)*6]+=s['weight']*(g+g.transpose(1,0,2,3))
    F=cross[:,shell['interior']][:,:,zero['interior']]
    C=contact[:,:,zero['interior']][:,:,:,zero['interior']]
    # Source spectral coefficients retain every reached complementary mode.
    f=np.einsum('ni,Anm,mj->Aij',shell['vectors'].conj(),F,zero['vectors'],optimize=True)
    c=np.einsum('mi,ABmn,ni->ABi',zero['vectors'].conj(),C,zero['vectors'],optimize=True)
    return dict(first_jet_n0=f,mixed_contact_n0_spectral_diagonal=c)


def finite_eight_q_heat_core(*, coefficients, representation, reference, time_nodes,
        source_beta_nodes, quadrature_order, family_indices=(1,2), repository=None):
    """Build source-reached positive-factor heat coefficients from actual fields.

    This is the complete fixed-core n0 projected heat derivative, with every
    n1/n3 intermediate mode, for each requested inherited family.  It is
    not a heat on eight source coordinates.  The homogeneous temporal
    Dirichlet condition is a declared numerical core; it does not select
    E0, the canonical stop, or the physical exterior/reset graph.  No
    formation cutoff is supplied or assigned here.
    """
    nodes=_finite(time_nodes,'heat core time nodes',real=True)
    if nodes.ndim!=1 or len(nodes)<3 or np.any(np.diff(nodes)<=0):
        raise ValueError('at least three strictly future heat core nodes required')
    if nodes[0]<-representation['length'] or nodes[-1]>0:
        raise ValueError('heat core cannot extrapolate the retained local family')
    beta=_finite(source_beta_nodes,'heat raw betaPhoton profiles',(len(nodes),8),real=True)
    if type(quadrature_order) is not int or quadrature_order<2:
        raise ValueError('explicit heat quadrature order>=2 required')
    families=tuple(family_indices)
    if not families or len(set(families))!=len(families) or any(type(f) is not int or f not in (0,1,2) for f in families):
        raise ValueError('distinct inherited family indices from (0,1,2) required')
    frame=lepton_current_hilbert_representation()
    Y=frame['family_Y']
    if np.max(abs(Y-np.diag(np.diag(Y))))!=0:
        raise ValueError('the retained fixed-Y family operator is not diagonal; separate family traces are invalid')
    source=retained_eight_q_fermion_source_image(repository)
    angular=source['angular'];D=angular['derivative_matrices'];labels=angular['harmonic_labels']
    image=source['unit_radius_source_image'].reshape(8,20,18,18)
    samples=_source_core_samples(coefficients,representation,reference,nodes,beta,quadrature_order)
    result={}
    for family in families:
        fiber=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
        complement=np.array([i for i in range(18) if i not in fiber])
        if any(np.max(abs(s['W'][np.ix_(fiber,complement)]))>1e-14 or
               np.max(abs(s['Omega_t'][np.ix_(fiber,complement)]))>1e-14 for s in samples):
            raise ValueError('computed background couples distinct families; requested partial trace is not invariant')
        zero=_family_shell_heat_forms(samples,len(nodes),None,fiber)
        rows={};contact=np.zeros((8,8,len(zero['eigenvalues'])),complex)
        for n in (1,3):
            ids=np.array([i for i,l in enumerate(labels) if l[0]==n])
            shell=_family_shell_heat_forms(samples,len(nodes),D[:,ids][:,:,ids],fiber)
            Xi=image[:,ids][:,:,fiber][:,:,:,fiber].reshape(8,6*len(ids),6)
            block=_family_source_heat_blocks(samples,len(nodes),Xi,zero,shell,fiber)
            contact+=block['mixed_contact_n0_spectral_diagonal']
            rows[str(n)]=dict(eigenvalues=shell['eigenvalues'],first_jet_n0=block['first_jet_n0'],
                full_shell_scalar_count=len(ids),full_shell_fiber_dimension=6*len(ids),
                all_complementary_eigenmodes_retained=True,
                generalized_eigen_residual_relative=shell['generalized_eigen_residual_relative'],
                positive_Gram_orthogonality_residual=shell['positive_Gram_orthogonality_residual'])
        result[str(family)]=dict(inherited_family=('heavy','middle','light')[family],
            fixed_Y=float(Y[family,family]),point_fiber_indices=fiber,n0_eigenvalues=zero['eigenvalues'],
            mixed_contact_n0_spectral_diagonal=contact,intermediate_shells=rows,
            generalized_eigen_residual_relative=zero['generalized_eigen_residual_relative'],
            positive_Gram_orthogonality_residual=zero['positive_Gram_orthogonality_residual'])
    return dict(families=result,temporal_core_nodes=nodes,source_beta_nodes=beta,
        quadrature_order=quadrature_order,
        operator='P=A_dagger A; A=(partial_t+Omega_t)/N+W; positive measure=N dt*2pi^2',
        generalized_Gram='eigh(K,M); V_dagger M V=I, equivalent to M^(-1/2) K M^(-1/2)',
        normalization='raw primitive betaPhoton unit-Tr16 connection source; no extra e,T_b or family factor',
        angular_row='n0 constant-angular trace only; complete n1+n3 intermediate shells',
        family_invariance='fixed diagonal Y and family-identity U2 connection/source; no family-selected statistics or state',
        numerical_core_domain='homogeneous Dirichlet at both finite chart faces; not E0/stop or physical boundary selection',
        temporal_chart='At_ref/N once; not At_ref+2wall_rate Ar_ref',
        physical_cutoff_selected=False,physical_native_domain_closed=False,
        Lorentz_to_native_analytic_continuation_certified=False,
        complete_native_heat_supertrace_or_Pauli_evaluated=False)


def _ordered_heat_lag(lambda_zero,lambda_shell,proper_time):
    """Exact positive Duhamel lag integral with a stable coincident limit."""
    a=lambda_zero[None,:];b=lambda_shell[:,None];s=proper_time
    # Gauss integration on t/s avoids subtracting close eigenvalues.
    # The refinement diagnostic is exposed by the public consumer below.
    def rule(order):
        x,w=np.polynomial.legendre.leggauss(order)
        x=(x+1)/2;w=w/2
        return s*s*sum(wi*(1-xi)*np.exp(-s*((1-xi)*a+xi*b)) for xi,wi in zip(x,w))
    return rule(32),rule(64)


def finite_eight_q_heat_application(core, proper_time):
    """Contact and BOTH Duhamel terms for the computed fixed-core n0 trace.

    proper_time is an explicit operator-function parameter, never a
    physical formation cutoff.  The returned trace uses positive Hilbert
    Gram; it is not a graded whole-stratum trace or a Pauli readout.
    """
    s=float(proper_time)
    if not math.isfinite(s) or s<=0:
        raise ValueError('explicit positive finite proper-time parameter required')
    rows={}
    for name,family in core['families'].items():
        lam=family['n0_eigenvalues']
        contact=-s*np.einsum('ABi,i->AB',family['mixed_contact_n0_spectral_diagonal'],np.exp(-s*lam))
        pair=np.zeros((8,8),complex);error=0.
        for shell in family['intermediate_shells'].values():
            lag32,lag64=_ordered_heat_lag(lam,shell['eigenvalues'],s)
            f=shell['first_jet_n0']
            p=np.einsum('Aji,Bji,ji->AB',f.conj(),f,lag64)
            old=np.einsum('Aji,Bji,ji->AB',f.conj(),f,lag32)
            pair+=p;error+=float(np.linalg.norm(p-old))
        total=contact+pair+pair.T
        rows[name]=dict(inherited_family=family['inherited_family'],proper_time=s,
            source_square_contact=contact,ordered_two_insertion=pair,
            opposite_order_two_insertion=pair.T,paired_heat_mixed=total,
            lag_quadrature_refinement_absolute_Frobenius_difference=error,
            formula='-s Tr0(exp(-s P0) P_vJ00)+sum_n int_0^s(s-t)Tr0(exp(-(s-t)P0)P_v0n exp(-t Pn)P_Jn0)dt+(v<->J)',
            relative_overlap_subtraction_performed=False)
    return dict(proper_time=s,families=rows,
        numerical_refinement_is_rigorous_enclosure=False,
        physical_cutoff_or_native_Pauli_selected=False)


def _ordered_cutoff_heat_lag(lambda_zero,lambda_shell,cutoff):
    """Integrate the Duhamel lag over s in [c,infinity), including its tail.

    With q(x)=(1-x)lambda0+x lambda_n, Tonelli gives the exact positive
    scalar kernel integral_0^1 (1-x) exp(-c q)(c/q+1/q²) dx.  No upper
    proper-time truncation or subtraction of nearly equal E1 values occurs.
    """
    a=lambda_zero[None,:];b=lambda_shell[:,None];c=cutoff
    def rule(order):
        x,w=np.polynomial.legendre.leggauss(order);x=(x+1)/2;w=w/2
        out=np.zeros((len(lambda_shell),len(lambda_zero)))
        for xi,wi in zip(x,w):
            q=(1-xi)*a+xi*b
            out+=wi*(1-xi)*np.exp(-c*q)*(c/q+1/(q*q))
        return out
    return rule(32),rule(64)


def finite_eight_q_cutoff_heat_application(core, cutoff):
    """Complete finite-core integral_c^infinity ds/s of the n0 mixed heat.

    c is a positive function parameter.  The actual action-owned heat length
    c=i/r, whole graded trace, exterior/child domain, and overlap subtraction
    are not inferred from this local core.  No finite proper-time tail is
    discarded.  Middle-minus-light is an evaluated mathematical difference
    of the two retained family applications; it does not assert the native
    relative-completion/LSZ subtraction equals that difference.
    """
    c=float(cutoff)
    if not math.isfinite(c) or c<=0:
        raise ValueError('explicit positive finite cutoff parameter required')
    rows={}
    for name,family in core['families'].items():
        lam=family['n0_eigenvalues']
        contact=-np.einsum('ABi,i->AB',family['mixed_contact_n0_spectral_diagonal'],np.exp(-c*lam)/lam)
        pair=np.zeros((8,8),complex);error=0.
        for shell in family['intermediate_shells'].values():
            lag32,lag64=_ordered_cutoff_heat_lag(lam,shell['eigenvalues'],c)
            f=shell['first_jet_n0']
            p=np.einsum('Aji,Bji,ji->AB',f.conj(),f,lag64)
            old=np.einsum('Aji,Bji,ji->AB',f.conj(),f,lag32)
            pair+=p;error+=float(np.linalg.norm(p-old))
        rows[name]=dict(inherited_family=family['inherited_family'],
            integrated_source_square_contact=contact,integrated_ordered_two_insertion=pair,
            integrated_opposite_order_two_insertion=pair.T,
            integrated_paired_heat_mixed=contact+pair+pair.T,
            scalar_kernel_quadrature_refinement_absolute_Frobenius_difference=error)
    difference=(rows['1']['integrated_paired_heat_mixed']-rows['2']['integrated_paired_heat_mixed']
                if '1' in rows and '2' in rows else None)
    return dict(cutoff_parameter=c,families=rows,middle_minus_light_fixed_core_difference=difference,
        proper_time_upper_tail='included analytically to infinity through the positive scalar kernel',
        kernel='int_0^1(1-x)exp[-c((1-x)lambda0+x lambda_n)]*(c/q+1/q^2)dx',
        raw_Hilbert_trace_integral='integral_c^infinity ds/s of projected mixed heat; no graded/action/charge factor inserted',
        relative_overlap_subtraction_performed=False,
        numerical_refinement_is_rigorous_enclosure=False,
        physical_cutoff_or_complete_native_Pauli_selected=False)
