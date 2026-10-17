"""Reached open-lepton field vertices for the actual local magnetic source.

The source solve supplies gauge and Higgs fields.  Here they are inserted in
the canonical first-order lepton action with both LR mass placements.  The
local positive-band reduction is a stated matched Dirac-symbol application;
it neither supplies the interacting pole nor a quantum self-energy loop.
"""
from __future__ import annotations
import numpy as np

from .muon_native_dirac_hamiltonian import (
    lepton_current_hilbert_representation, fixed_y_higgs_hamiltonian,
)
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from .muon_primal_electromagnetic_source import higgs_aligned_charge, PAULI
from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator


def magnetic_open_fields_at_node(inputs, response_time):
    """Sample saved total fields, retaining measured spline roundoff at birth.

    The frozen source form reconstructs its coefficient nodes through a
    cubic spline.  This keeps the saved trace rather than replacing it by
    the analytic Q; only a 32-epsilon relative reconstruction discrepancy
    is accepted.  That guard is a finite-array comparison, not an outward
    bound on the source solve or its interpolation between nodes.
    """
    from .muon_magnetic_source_mean_load import magnetic_source_jet_at_node
    from .muon_electromagnetic_soft_magnetic_source import magnetic_turn_on_profile
    from .muon_parent_retarded_hypercharge import regular_radial_basis
    t=float(response_time);times=inputs['times'];source=inputs['source']
    hits=np.flatnonzero(times==t);nodes=np.flatnonzero(source['times']==t)
    if not np.isfinite(t) or len(hits)!=1 or len(nodes)!=1:
        raise ValueError('exact retained magnetic response and source node required')
    i,j=int(hits[0]),int(nodes[0]);receipt=inputs['receipt'];rep=inputs['representation']
    profile=receipt['source_temporal_profile']
    if profile=='smooth_retarded_turn_on_then_constant_magnetic_trace':
        p,pt,_=magnetic_turn_on_profile(t,receipt['turn_on_duration'])
    elif profile=='constant_magnetic_trace_inherited_from_incoming_birth' and receipt['side']=='outgoing':
        p,pt=1.,0.
    else:raise ValueError('actual common magnetic turn-on and inherited plateau required')
    jet=magnetic_source_jet_at_node(inputs,t)
    wall=inputs['contacts']['source_trace'][i];wall_rate=inputs['contacts']['source_trace_rate'][i]
    expected,expected_rate=p*jet['Q'],pt*jet['Q']+p*jet['Qdot']
    discrepancy=[];guard=[]
    for saved,exact in ((wall,expected),(wall_rate,expected_rate)):
        error=float(np.max(abs(saved-exact)))
        allowance=32*np.finfo(float).eps*float(max(np.max(abs(saved)),np.max(abs(exact))))
        if not np.isfinite(saved).all() or error>allowance:
            raise ValueError('saved magnetic source differs beyond spline reconstruction rounding')
        discrepancy.append(error);guard.append(allowance)
    state=inputs['phase']['state'][i];velocity=inputs['velocity']['velocity'][i]
    interior=np.r_[inputs['contacts']['A_tau'][i],state[:320]].T.reshape(8,5,4,20)
    rate=np.r_[inputs['Gauss_time_interpolant'](t,1),velocity[:320]].T.reshape(8,5,4,20)
    wall,wall_rate=wall.T.reshape(8,5,4,20),wall_rate.T.reshape(8,5,4,20)
    basis,derivative=regular_radial_basis(rep['rho'],1)
    shape=lambda a:a[:,None,None,None,None]
    return dict(raw_fields=source['raw_fields'][j],response_time=t,
        coordinate_time=float(source['coordinate_times'][j]),
        first_gauge=shape(basis[:,0])*interior+shape(basis[:,1])*wall,
        first_gauge_rate=shape(basis[:,0])*rate+shape(basis[:,1])*wall_rate,
        first_gauge_radial=shape(derivative[:,0])*interior+shape(derivative[:,1])*wall,
        first_wall_gauge=wall,first_wall_gauge_rate=wall_rate,
        first_H=state[320:400].T.reshape(8,4,20),
        first_H_rate=velocity[320:400].T.reshape(8,4,20),
        profile=float(p),profile_rate=float(pt),source_temporal_profile=profile,
        source_value_reconstruction_discrepancy=discrepancy[0],
        source_rate_reconstruction_discrepancy=discrepancy[1],
        finite_array_reconstruction_guard=guard,
        saved_source_values_replaced=False,all_solved_first_fields_used=True,
        source_coordinate_clock='incoming coordinate_time=u-L; outgoing coordinate_time=u; future derivative+1',
        actual_local_magnetic_first_jet=True,active_source_indices=[0,1,2],
        inactive_source_indices=[3,4,5,6,7],physical_history_selected=False,
        At_time_derivative_scope='saved Gauss interpolant derivative; unused by literal Maxwell/Higgs action')


def canonical_open_field_vertices(radius, lapse):
    """Literal delta_field Hcan matrices, unit canonical current Gram.

    Gauge coordinates are unit-Tr16 material A_t and unit-S3 A_i.  The
    radial connection has no direct intrinsic Dirac action.  No e is
    reinserted: the actual magnetic field coordinate already contains e.
    Hreal order is ReH1,ReH2,ImH1,ImH2.  These are the mixed Hessian
    vertices between the bosonic field and an open canonical lepton leg.
    """
    R,N=float(radius),float(lapse)
    if not np.isfinite([R,N]).all() or min(R,N)<=0:
        raise ValueError('positive actual radius and lapse required')
    alpha=lepton_current_hilbert_representation()['alpha']
    G=lepton_unit_trace_gauge_representation()['generators']
    gauge=np.zeros((5,4,18,18),complex)
    gauge[0]=-1j*G/N
    gauge[2:]=-1j*np.einsum('iuv,cvw->icuw',alpha,G)/R
    Hbasis=np.array([[1,0],[0,1],[1j,0],[0,1j]],complex)
    scalar=fixed_y_higgs_hamiltonian(Hbasis)
    return dict(gauge=gauge,scalar=scalar,
        canonical_current='chi_hat=R4^(3/2)psi/(2pi^2); GramI18',
        radial_zero_scope='intrinsic first-order wall action only; parent radial/conormal action retained separately',
        gauge_temporal_coordinate='material A_t; proper rate divided by N once',
        separate_e_inserted=False,HS_auxiliary_identified_with_intrinsic_H=False)


def charged_dirac_injection(H, *, family=1):
    """Actual H-selected charged fiber in the retained Dirac spin frame.

    It is an algebraic charged fiber injection.  Its leakage into the
    neutral component under the actual background remains an output.
    It is not an interacting LSZ pole selection.
    """
    h=np.asarray(H,complex)
    if h.shape!=(2,) or not np.isfinite(h).all() or np.vdot(h,h).real<=0 or type(family) is not int or family not in (0,1,2):
        raise ValueError('nonzero actual H and retained family required')
    norm=np.sqrt(np.vdot(h,h).real);h=h/norm
    chiral=np.zeros((18,4),complex)
    for weak in range(2):
        chiral[6*weak+2*family:6*weak+2*family+2,:2]=h[weak]*np.eye(2)
    chiral[12+2*family:14+2*family,2:]=np.eye(2)
    frame=retained_higgs_spin_charge_representation()
    J=chiral@frame['Dirac_to_LR_columns'].conj().T
    neutral=np.array([h[1].conjugate(),-h[0].conjugate()])
    K=np.zeros((18,2),complex)
    for weak in range(2):
        K[6*weak+2*family:6*weak+2*family+2]=neutral[weak]*np.eye(2)
    charge=higgs_aligned_charge(norm*h,np.zeros(2,complex))['charge']
    return dict(charged=J,neutral=K,
        current_Gram_defect=float(np.linalg.norm(J.conj().T@J-np.eye(4))),
        charge_defect=float(np.linalg.norm(charge@J+J)),
        charged_neutral_orthogonality=float(np.linalg.norm(K.conj().T@J)),
        interacting_LSZ_selected=False)


def matched_symbol_magnetic_spin_reduction(point_vertex, physical_spatial_gradient,
                                         *, matched_mass_action, electric_charge):
    """First local positive-band magnetic reduction of supplied action vertices.

    At the matched free rest symbol H0=m beta, the cross of alpha.p with
    the odd perturbation gives -i/(4m) P+ sum_j[alpha_j,d_j V] P+.
    The point P+ V P+ is also retained.  This is the ordinary first
    nonrelativistic derivative expansion on that explicit symbol, not a
    Lorentz-covariant F2 extraction on an interacting/background pole.
    """
    V=np.asarray(point_vertex,complex);dV=np.asarray(physical_spatial_gradient,complex)
    m,e=float(matched_mass_action),float(electric_charge)
    if V.ndim!=3 or V.shape[1:]!=(4,4) or dV.shape!=(len(V),3,4,4) or not np.isfinite(V).all() or not np.isfinite(dV).all() or not np.isfinite([m,e]).all() or min(m,e)<=0:
        raise ValueError('finite complete local vertices/gradients and positive explicit mass/charge required')
    scale=max(1.,np.max(abs(V)),np.max(abs(dV)))
    if max(np.max(abs(V-V.conj().swapaxes(-1,-2))),np.max(abs(dV-dV.conj().swapaxes(-1,-2))))>2e-12*scale:
        raise ValueError('Hermitian canonical action vertices required')
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac']
    alpha=np.array([gamma[0]@g for g in gamma[1:]])
    comm=sum((alpha[j]@dV[:,j]-dV[:,j]@alpha[j] for j in range(3)),np.zeros_like(V))
    direct=V[:,:2,:2];derivative=(-1j*comm/(4*m))[:,:2,:2]
    result=direct+derivative
    spin=np.einsum('kij,Aji->Ak',PAULI,result)/2
    spinless=np.trace(result,axis1=1,axis2=2)/2
    relative=(2*m/e)*spin
    return dict(positive_band_point_response=direct,positive_band_gradient_response=derivative,
        positive_band_total_response=result,spin_coefficients=spin,
        spinless_coefficients=spinless,relative_to_minimal_Dirac_spin_coefficient=relative,
        matched_mass_action=m,electric_charge=e,
        denominator='minimal electron energy shift +e sigma.B/(2m); source B is local action-unit curvature',
        approximation='first spatial-gradient positive-band expansion of explicitly matched free Dirac rest symbol',
        background_operator_or_LSZ_replaced=False,interacting_background_expansion_justified=False,
        quantum_self_energy_or_native_Pauli_completed=False)


def reached_magnetic_open_vertex(fields, representation, angular, *, electric_charge, family=1):
    """Apply the reached full gauge/H fields and all angular derivatives.

    No source-only field replaces the solved H80 response.  Actual
    background leakage is measured before any local-symbol projection.
    The coefficient source has three physical local B axes plus five
    exact representation zeros.  This derivative is open-legged and
    remains distinct from the bosonic determinant/source Hessian.
    """
    raw=np.asarray(fields['raw_fields']);a=np.asarray(fields['first_wall_gauge']);h=np.asarray(fields['first_H'])
    if not np.isrealobj(a) or a.shape!=(8,5,4,20) or not np.isrealobj(h) or h.shape!=(8,4,20) or not np.isfinite(a).all() or not np.isfinite(h).all():
        raise ValueError('complete actual magnetic wall gauge and solved H80 response required')
    op=primal_trace_enriched_lepton_operator(raw,representation)
    basis=canonical_open_field_vertices(op['R4'],op['N'])
    gauge=np.einsum('fcuv,Afch->Ahuv',basis['gauge'],a)
    scalar=np.einsum('cuv,Ach->Ahuv',basis['scalar'],h)
    full=gauge+scalar
    from .muon_intrinsic_scalar_discretization import scalar_basis_values,real_scalar_basis_transform,real_scalar_basis_labels
    labels=real_scalar_basis_labels(3);odd=[j for j,l in enumerate(labels) if l[0] in (1,3)]
    value=(scalar_basis_values(np.eye(2,dtype=complex)[None],3)@real_scalar_basis_transform(3))[0,odd].real
    derivative=np.einsum('h,jhk->jk',value,angular['derivative_matrices'])/op['R4']
    injection=charged_dirac_injection(op['H'],family=family);J=injection['charged'];K=injection['neutral']
    point=np.einsum('h,Ahuv->Auv',value,full)
    gradient=np.einsum('jh,Ahuv->Ajuv',derivative,full)
    project=lambda V:np.einsum('ui,...uv,vj->...ij',J.conj(),V,J)
    charged=project(point);charged_gradient=project(gradient)
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac']
    mass=float(np.diag(lepton_current_hilbert_representation()['family_Y'])[family].real*np.linalg.norm(op['H']))
    matching=matched_symbol_magnetic_spin_reduction(charged,charged_gradient,
        matched_mass_action=mass,electric_charge=electric_charge)
    return dict(open_field_vertices=basis,operator=op,charged_injection=injection,
        canonical_gauge_source_vertices=gauge,canonical_fixed_Y_H_source_vertices=scalar,
        canonical_total_source_vertices=full,canonical_point_vertices=point,
        canonical_physical_spatial_gradient=gradient,
        charged_point_vertices=charged,charged_physical_spatial_gradient=charged_gradient,
        covariant_charged_point_vertices=-gamma[0]@charged,
        neutral_point_source_leakage=np.einsum('ui,Auv,vj->Aij',K.conj(),point,J),
        neutral_background_leakage=K.conj().T@op['H_can']@J,
        charged_background_Hamiltonian=J.conj().T@op['H_can']@J,
        matched_local_tree_symbol_spin_application=matching,
        fixed_Y_mass_action=mass,external_charge_or_volume_inserted_twice=False,
        gauge_and_H_total_first_response_used=True,both_LR_mass_vertices_retained=True,
        Psi_dependent_mixed_action_vertex_applied=True,
        complete_angular_geometry_first_response_claimed=False,
        native_loop_P_A_ghost_HS_contracted=False,
        physical_a_mu=None,physical_g_mu=None,complete_observable=False)
