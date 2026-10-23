"""Local physical magnetic first jet in the reached full angular action.

At the identity chart g=wI-i q_a sigma_a, X_a=R4*q_a are normal
coordinates to first order.  A_can,i=epsilon_ikj B_k X_j/2 has zero
potential and prescribed magnetic curvature at that point.  Its exact
unit-right-coframe extension is n1 and includes the longitudinal part
missing from the eight retained curl eigenmodes.  This local first jet
does not identify an angular mode label with external Fourier momentum.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp, simpson
from scipy.linalg import cho_factor, cho_solve

from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
from .muon_primal_electromagnetic_source import higgs_aligned_charge, PAULI
from .muon_current_source_motion_cubic import current_face_source_jets
from .muon_matched_mechanical_source import epsilon
from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_parent_maxwell_full_retarded import _reduced_at


def local_magnetic_wavefunctions(angular):
    """Exact retained-frame coefficients of -epsilon_ijk*q_j, Haar normalized."""
    s=scalar_s3_discretization(3)
    odd=np.array([i for i,l in enumerate(s['real_basis_labels']) if l[0] in (1,3)])
    if [s['real_basis_labels'][i] for i in odd]!=list(angular['harmonic_labels']):
        raise ValueError('same right-coframe real n1+n3 harmonic frame required')
    # g=wI-i q_a sigma_a, so q_a=(i/2)Tr(sigma_a g).
    q=.5j*np.einsum('aij,pji->pa',PAULI,s['su2_points'])
    if np.max(abs(q.imag))>2e-14:
        raise ArithmeticError('quaternion normal-coordinate functions must be real')
    coefficients=np.einsum('ph,p,pa->ha',s['real_basis_values'][:,odd],s['haar_weights'],q.real)
    residual=s['real_basis_values'][:,odd]@coefficients-q.real
    if np.max(abs(residual))>2e-13:
        raise ArithmeticError('complete n1 normal-coordinate pullback required')
    # Higher shell coefficients vanish by exact Peter--Weyl orthogonality.
    coefficients[np.array([angular['harmonic_labels'][i][0] for i in range(20)])!=1]=0.
    wave=np.zeros((5,20,8))
    wave[2:,:,:3]=-np.einsum('ijk,hj->ihk',epsilon(),coefficients)
    return dict(wavefunctions=wave,quaternion_coefficients=coefficients,
        active_source_indices=[0,1,2],inactive_source_indices=[3,4,5,6,7],
        inactive_source_reason='three Cartesian magnetic first-jet directions only; padded columns identically zero by construction',
        angular_reconstruction_maximum=float(np.max(abs(residual))),
        source_chart='g=wI-i q_a sigma_a; observation point g=I; X_a=R4 q_a',
        global_uniform_field_or_Fourier_extension_claimed=False)


def _charge_coefficient_two_jet(h):
    v=[Jet(float(z),np.eye(4)[i],np.zeros((4,4))) for i,z in enumerate(h)]
    norm=sum(z*z for z in v)
    bloch=(2*(v[0]*v[1]+v[2]*v[3])/norm,
           2*(v[0]*v[3]-v[2]*v[1])/norm,
           (v[0]*v[0]+v[2]*v[2]-v[1]*v[1]-v[3]*v[3])/norm)
    gs=np.zeros((4,4));hs=np.zeros((4,4,4))
    for i,b in enumerate(bloch):
        gs[i]=-np.sqrt(2)*b.gradient;hs[i]=-np.sqrt(2)*b.hessian
    return gs,hs


def uniform_magnetic_source_first_jets(raw,angular,*,electric_charge):
    """Actually apply eR4²/2 and its full future-clock/H-axis first jets.

    The current variable is chi_hat=R4^(3/2)psi/(2pi²).  In that unit
    canonical current, Omega_ph=-i e Q_H A_can and no second 1/(2pi²)²
    or independent vertex normalization belongs in this insertion.
    The pole/Thomson matching convention is explicit; this does not
    establish interacting LSZ or the complete soft Pauli vertex.
    """
    x=np.asarray(raw)
    e=float(electric_charge)
    if not np.isrealobj(x) or x.shape!=(268,) or not np.isfinite(x).all() or not np.isfinite(e) or e<=0:
        raise ValueError('complete real raw268 and positive explicit canonical electric charge required')
    h,hd=x[-8:-4],x[-4:]
    alignment=higgs_aligned_charge(h[:2]+1j*h[2:],hd[:2]+1j*hd[2:])
    chart=local_magnetic_wavefunctions(angular);wave=chart['wavefunctions']
    S=np.einsum('fhA,c->fchA',wave,alignment['unit_Tr16_coefficients']).reshape(400,8)
    Sd=np.einsum('fhA,c->fchA',wave,alignment['unit_Tr16_coefficient_rate']).reshape(400,8)
    gs,hs=_charge_coefficient_two_jet(h)
    sh=np.einsum('fhA,ci->ifchA',wave,gs).reshape(4,400,8)
    sdh=np.einsum('fhA,ci->ifchA',wave,np.einsum('cij,j->ci',hs,hd)).reshape(4,400,8)
    ds=np.zeros((268,400,8));ds[-8:-4]=sh
    dsd=np.zeros_like(ds);dsd[-8:-4]=sdh;dsd[-4:]=sh
    face=current_face_source_jets(x[:100]);R=face['intrinsic_weights']['R4']
    factor=e*R*R/2;factor_rate=2*factor*face['log_R4_dot']
    fg=np.r_[factor.gradient,np.zeros(168)];fdg=np.r_[factor_rate.gradient,np.zeros(168)]
    Q=factor.value*S;Qd=factor_rate.value*S+factor.value*Sd
    old=np.asarray(angular['source_coefficients'])
    inclusion=np.linalg.solve(old.T@old,old.T@Q[:,:3]);remainder=Q[:,:3]-old@inclusion
    return dict(chart,connection_source=Q,connection_source_rate=Qd,
        Q=Q,Qdot=Qd,source=S,source_rate=Sd,
        Q_first_jet=fg[:,None,None]*S+factor.value*ds,
        Qdot_first_jet=fdg[:,None,None]*S+factor_rate.value*ds+fg[:,None,None]*Sd+factor.value*dsd,
        charge_alignment=alignment,R4=float(R.value),electric_charge=e,
        canonical_magnetic_factor=float(factor.value),canonical_magnetic_factor_rate=float(factor_rate.value),
        old_coexact_source_inclusion=inclusion,old_coexact_source_remainder=remainder,
        old_coexact_relative_remainder=float(np.linalg.norm(remainder)/np.linalg.norm(Q[:,:3])),
        source_motion_count=1,source_first_jets_are_analytic=True,
        source_scope='physical_local_magnetic_first_jet',
        linear_source_bound_to_background_H=True,
        nonlinear_angular_H_axis_response_included=False,
        Fourier_soft_limit_or_native_Pauli_completed=False,
        canonical_current='chi_hat=R4^(3/2)psi/(2pi²); unit current Gram',
        canonical_matching_premise='independently measured Thomson e is inserted once in Omega=-i e Q_H A_can; interacting residue matching not inferred')


def magnetic_point_jet(source,angular,background_spatial_connection):
    """Full covariant field-strength jet at g=I, including actual [A,deltaA]."""
    Q=np.asarray(source['connection_source'])
    base=np.asarray(background_spatial_connection)
    if Q.shape!=(400,8) or base.shape!=(3,4) or not np.isfinite(base).all():
        raise ValueError('complete source and actual unitTr16 spatial connection required')
    from .muon_intrinsic_scalar_discretization import scalar_basis_values,real_scalar_basis_transform,real_scalar_basis_labels
    labels=real_scalar_basis_labels(3);odd=np.array([i for i,l in enumerate(labels) if l[0] in (1,3)])
    v=(scalar_basis_values(np.eye(2,dtype=complex)[None],3)@real_scalar_basis_transform(3))[0,odd].real
    f=Q.reshape(5,4,20,8)[2:]
    value=np.einsum('ichA,h->icA',f,v)
    derivative=np.einsum('h,jhk,ickA->jicA',v,angular['derivative_matrices'],f)
    structure=2*np.einsum('ijk,kcA->ijcA',epsilon(),value)
    comm=np.zeros((3,3,4,8))
    for i in range(3):
        for j in range(3):
            comm[i,j,:3]=(np.cross(base[i,:3],value[j,:3].T).T-np.cross(base[j,:3],value[i,:3].T).T)/np.sqrt(2)
    curvature=derivative-derivative.swapaxes(0,1)+structure+comm
    expected=source['electric_charge']*source['R4']**2*np.einsum('ijA,c->ijcA',epsilon(),source['charge_alignment']['unit_Tr16_coefficients'])
    # epsilon third index is the magnetic direction; pad five absent directions.
    expected=np.concatenate((expected,np.zeros((3,3,4,5))),axis=-1)
    return dict(potential_at_point=value,coframe_derivative=derivative,
        coframe_structure_contact=structure,mechanical_commutator_contact=comm,
        full_curvature_at_point=curvature,expected_local_magnetic_curvature=expected,
        potential_zero_defect=float(np.linalg.norm(value)),
        magnetic_curvature_defect=float(np.linalg.norm(curvature-expected)),
        higher_spatial_jets_or_LSZ_selected=False)


def magnetic_turn_on_profile(time,duration):
    """C2 retarded turn-on followed by a constant applied magnetic trace.

    g=10z³-15z⁴+6z⁵, z=t/duration, is exactly zero with zero first
    and second derivatives initially, and exactly one after turn-on.
    The finite plateau is not an infinite-past adiabatic prescription.
    """
    t,D=float(time),float(duration)
    if not np.isfinite([t,D]).all() or D<=0:
        raise ValueError('finite time and positive turn-on duration required')
    if t<=0:return 0.,0.,0.
    if t>=D:return 1.,0.,0.
    z=t/D
    return z**3*(10-15*z+6*z*z),30*z*z*(1-z)**2/D,60*z*(1-z)*(1-2*z)/D**2


def magnetic_source_sample(raw,representation,angular,*,electric_charge):
    """Reached local first jet and full primitive lepton/current insertions."""
    from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
    from .muon_primal_electromagnetic_source import clifford_field_jet_projection
    from .muon_parent_maxwell_full_weak import M
    source=uniform_magnetic_source_first_jets(raw,angular,electric_charge=electric_charge)
    op=primal_trace_enriched_lepton_operator(raw,representation)
    align=source['charge_alignment']
    source['Clifford_application']=clifford_field_jet_projection(op,align)
    source['local_charge_evolution_commutator_norm']=float(np.linalg.norm(align['charge']@op['H_can']-op['H_can']@align['charge']))
    source['local_charge_covariant_time_norm']=float(np.linalg.norm(align['charge_rate']/op['N']+op['Omega_tau']@align['charge']-align['charge']@op['Omega_tau']))
    weights=current_face_source_jets(np.asarray(raw)[:100])['intrinsic_weights']
    wall=np.einsum('fcj,j->fc',representation['wall_trace_map'],np.asarray(raw)[100:180])
    wall[2:]+=M*(weights['mechanical_connection_lambda'].value-1)
    source['local_point_jet']=magnetic_point_jet(source,angular,wall[2:])
    return source


def magnetic_ramp_retarded_application(form,*,time_steps=64,rtol=2e-9,atol=2e-11):
    """Solve the actual reached eight-column Euler/Gauss source problem.

    The C2 turn-on and constant plateau are finite retarded applications. Its
    normalization and the moving full400 source actions are retained.
    The exported H80 response is newly solved on those actions; an old
    response outside their span is never substituted.
    """
    if type(time_steps) is not int or time_steps<16:
        raise ValueError('resolved source-response mesh required')
    n=400;k=8;T,D=form['final_time'],form['duration']
    def rhs(t,state):
        current_state=np.asarray(state).reshape(2*n,k)
        x,p=current_state[:n],current_state[n:]
        f=_reduced_at(form,t);mass,mixed,stiffness=(f[a] for a in ('M','B','K'))
        g,gd,_=magnetic_turn_on_profile(t,D)
        velocity=cho_solve(cho_factor(mass[:n,:n]),
            p-mixed[:n,:n].T@x-g*mixed[n:,:n].T-gd*mass[:n,n:])
        force=mixed[:n,:n]@velocity+g*stiffness[:n,n:]+gd*mixed[:n,n:]+stiffness[:n,:n]@x
        return np.r_[velocity,force].ravel()
    sol=solve_ivp(rhs,(0,T),np.zeros(2*n*k),method='DOP853',
        rtol=rtol,atol=atol,max_step=D/time_steps,dense_output=True)
    if not sol.success:raise ArithmeticError('reached action solve failed: '+sol.message)
    t=np.linspace(0,T,3*time_steps+1)
    states=sol.sol(t).T.reshape(-1,2*n,k)
    velocities=np.array([rhs(a,b.ravel()).reshape(2*n,k)[:n] for a,b in zip(t,states)])
    Ats=[];Gauss=[];Gauss_rel=[];reactions=[];work=[];quadratic=[];scalar_work=[];physical_traces=[];physical_trace_rates=[]
    for a,state,v in zip(t,states,velocities):
        f=_reduced_at(form,a);g,gd,_=magnetic_turn_on_profile(a,D)
        z=np.r_[state[:n],g*np.eye(k)];zd=np.r_[v,gd*np.eye(k)]
        y=f['At_value_map']@z+f['At_velocity_map']@zd;Ats.append(y)
        parts=(f['Gauss_matrix']@y,f['Gauss_value_row']@z,f['Gauss_velocity_row']@zd)
        Gauss.append(sum(parts));Gauss_rel.append(float(np.max(abs(sum(parts)))/(1+sum(np.max(abs(a)) for a in parts))))
        full=np.r_[y,z];full_dot=np.r_[np.zeros_like(y),zd]
        G0z,G0v,G1z,G1v=form['gauge_weak_rows'](a)
        reactions.append(g*(G0z@full+G0v@full_dot)+gd*(G1z@full+G1v@full_dot))
        mass,mixed,stiffness=(f[b] for b in ('M','B','K'))
        momentum=mass@zd+mixed.T@z
        work.append(-gd*momentum[n:]-g*(mixed[n:]@zd+stiffness[n:]@z))
        quadratic.append(zd.T@mass@zd+z.T@mixed@zd+zd.T@mixed.T@z+z.T@stiffness@z)
        sm,sb,sk=(form['intrinsic_'+b](a) for b in ('raw_M','raw_B','raw_K'))
        scalar_work.append(-gd*(sm@zd+sb.T@z)[n:]-g*(sb[n:]@zd+sk[n:]@z))
        Q,Qt=form['source_map'](a),form['source_rate_map'](a)
        physical_traces.append(g*Q);physical_trace_rates.append(gd*Q+g*Qt)
    readout=np.zeros((k,2*n));readout[:,:n]=form['intrinsic_raw_K'](T)[n:,:n]
    def adjoint_rhs(a,state):
        state=state.reshape(2*n,k);f=_reduced_at(form,a)
        mass,mixed,stiffness=(f[b][:n,:n] for b in ('M','B','K'))
        v=cho_solve(cho_factor(mass),state[:n]+mixed.T@state[n:])
        return np.r_[mixed@v-stiffness.T@state[n:],-v].ravel()
    adj=solve_ivp(adjoint_rhs,(T,0),readout.T.ravel(),method='DOP853',
        rtol=rtol,atol=atol,max_step=D/time_steps,dense_output=True)
    if not adj.success:raise ArithmeticError('reached adjoint solve failed: '+adj.message)
    adjoints=adj.sol(t).T.reshape(-1,2*n,k)
    contraction=simpson(np.array([a.T@rhs(b,np.zeros(2*n*k)).reshape(2*n,k)
        for a,b in zip(adjoints,t)]),x=t,axis=0)
    output=readout@states[-1]
    endpoint=states[-1,:n].T@states[-1,n:]-states[0,:n].T@states[0,n:]
    ff=_reduced_at(form,T);gz,gdt,_=magnetic_turn_on_profile(T,D)
    final_z=np.r_[states[-1,:n],gz*np.eye(k)];final_zd=np.r_[velocities[-1],gdt*np.eye(k)]
    final_source_momentum=(ff['M']@final_zd+ff['B'].T@final_z)[n:]
    work=simpson(np.array(work),x=t,axis=0)
    action_boundary=endpoint-simpson(np.array(quadratic),x=t,axis=0)
    return dict(times=t,state=states,velocity=velocities,A_tau=np.array(Ats),
        Gauss_residual=np.array(Gauss),Gauss_relative_maximum=max(Gauss_rel),
        gauge_Euler_reaction_integrand=np.array(reactions),
        paired_gauge_Euler_reaction=simpson(np.array(reactions),x=t,axis=0),
        source_trace=np.array(physical_traces),source_trace_rate=np.array(physical_trace_rates),
        intrinsic_H_response=states[:,320:400],
        intrinsic_H_canonical_momenta=states[:,n+320:n+400],
        intrinsic_scalar_wall_current_pairing=simpson(np.array(scalar_work),x=t,axis=0),
        wall_trace_reaction_pairing=work,action_temporal_endpoint=endpoint,
        action_boundary_pairing=action_boundary,
        action_boundary_relative_defect=float(np.max(abs(work-action_boundary))/(1+np.max(abs(work)))),
        advanced_adjoint=adjoints,adjoint_readout_map=readout,
        adjoint_output=output,adjoint_source_pairing=contraction,
        adjoint_pairing_maximum_defect=float(np.max(abs(output-contraction))),
        numerical_integrator=dict(method='DOP853',rtol=rtol,atol=atol,evaluations=sol.nfev),
        actual_new_reached_source_response=True,old_source_span_response_substituted=False,
        source_motion_count=1,source_motion_differentiated_before_Gauss=True,
        final_source_canonical_momentum=final_source_momentum,
        source_terminal_endpoint=gz*final_source_momentum,
        temporal_source_scope='smooth retarded turn-on then constant local magnetic trace; finite plateau, no adiabatic/Fourier limit',
        physical_free_wall_inverse=False,physical_native_heat_closed=False,physical_Pauli_value=False)
