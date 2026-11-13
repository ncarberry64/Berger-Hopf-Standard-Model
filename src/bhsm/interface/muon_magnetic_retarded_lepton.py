"""Actual Lorentz lepton magnetic source on its chronological coefficient cell.

The current-rescaled eighteen-component Hilbert field evolves with
K=-i N H_can.  The magnetic first response is an open fermion operator
application, distinct from the closed positive-factor heat trace.
No quantum photon covariance, external pole or LSZ residue is invented.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation,fixed_y_higgs_hamiltonian
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation


def reached_lorentz_magnetic_vertices(inputs):
    """Apply delta Hcan to the saved total gauge/H first fields, all families.

    The Lorentz temporal connection is -i deltaOmega_tau.  Using the
    positive factor's +deltaOmega_tau here would give a different action.
    The spatial source already contains measured eR4²/2 exactly once.
    """
    source=inputs['source'];times=inputs['times'];active=inputs['active_source_indices']
    if active!=[0,1,2]:raise ValueError('complete three-axis magnetic first jet required')
    frame=lepton_current_hilbert_representation();G=lepton_unit_trace_gauge_representation()['generators']
    raw_nodes=source['raw_fields'];ops=[primal_trace_enriched_lepton_operator(r,inputs['representation']) for r in raw_nodes]
    N=CubicSpline(source['times'],np.array([o['N'] for o in ops]))
    R=CubicSpline(source['times'],np.array([o['R4'] for o in ops]))
    Hcan=CubicSpline(source['times'],np.array([o['H_can'] for o in ops]))
    wall=inputs['contacts']['source_trace'][...,:3].transpose(0,2,1).reshape(len(times),3,5,4,20)
    h=inputs['phase']['state'][:,320:400,:3].transpose(0,2,1).reshape(len(times),3,4,20)
    H=np.stack((h[:,:,0]+1j*h[:,:,2],h[:,:,1]+1j*h[:,:,3]),axis=-1)
    spatial=-1j*np.einsum('iuv,cvw,tAich->tAhuw',frame['alpha'],G,wall[:,:,2:])/R(times)[:,None,None,None,None]
    temporal=-1j*np.einsum('cuv,tAch->tAhuv',G,wall[:,:,0])/N(times)[:,None,None,None,None]
    mass=fixed_y_higgs_hamiltonian(H.reshape(-1,2)).reshape(len(times),3,20,18,18)
    vertex=spatial+temporal+mass
    adjoint_defect=float(np.max(abs(vertex-vertex.conj().swapaxes(-1,-2))))
    if adjoint_defect>2e-13*max(1.,float(np.max(abs(vertex)))):
        raise ArithmeticError('actual Lorentz source lost its positive-current Hermitian pairing')
    return dict(times=times,magnetic_Hcan_vertex=vertex,spatial_vertex=spatial,
        temporal_vertex=temporal,fixed_Y_H_vertex=mass,N=N,R4=R,Hcan=Hcan,
        vertex_interpolant=CubicSpline(times,vertex),Hermitian_vertex_defect=adjoint_defect,
        all18_leptons_and_fixed_Y_used=True,source_e_inserted_once=True,
        complete_angular_geometry_first_variations_evaluated=False,
        geometry_first_zero_scope='only represented homogeneous geometry projection of literal odd n1/n3 source; no unrepresented angular geometry filled zero')


def retarded_magnetic_lepton_application(inputs,angular,*,source_time=0.,observation_times=None,
        initial_transport=None,initial_first_response=None,rtol=2e-11,atol=2e-13):
    """Execute all source-reached open fermion Duhamel columns.

    dU0/dt=K0 U0, d(deltaU_n)/dt=Kn deltaU_n+deltaKn0 U0.
    Thus deltaU_n(t,s)=-i integral_s^t Un(t,u) N(u)
    deltaHcan_n0(u) U0(u,s)du.  Complete72 and288 intermediate
    images are retained; this n0 source reduction is not a full trace.
    """
    rows=reached_lorentz_magnetic_vertices(inputs);times=rows['times'];T=float(times[-1]);s=float(source_time)
    if not np.isfinite(s) or not 0<=s<T:raise ValueError('actual chronological lepton source time required')
    t=inputs['source']['times'] if observation_times is None else np.asarray(observation_times)
    if not np.isrealobj(t) or t.ndim!=1 or not np.isfinite(t).all() or np.any(np.diff(t)<=0) or np.any(t<s) or np.any(t>T):
        raise ValueError('actual increasing causal lepton observation times required')
    frame=lepton_current_hilbert_representation();alpha=frame['alpha'];E=angular['derivative_matrices']
    shells={};offset=324
    for n in (1,3):
        labels=np.array([j for j,l in enumerate(angular['harmonic_labels']) if l[0]==n]);d=len(labels);size=3*d*18*18
        principal=-1j*sum(np.kron(E[a][np.ix_(labels,labels)],alpha[a]) for a in range(3))
        shells[n]=dict(labels=labels,dimension=d*18,principal=principal,begin=offset,end=offset+size)
        offset+=size
    initial=np.zeros(offset,complex)
    Uinit=np.eye(18,dtype=complex) if initial_transport is None else np.asarray(initial_transport)
    if Uinit.shape!=(18,18) or not np.isfinite(Uinit).all():raise ValueError('complete finite eighteen-component transport required')
    initial[:324]=Uinit.ravel()
    if initial_first_response is not None:
        if initial_transport is None:raise ValueError('inherited first response requires its same base transport')
        for n,sh in shells.items():
            value=np.asarray(initial_first_response[str(n)])
            if value.shape!=(3,sh['dimension'],18) or not np.isfinite(value).all():
                raise ValueError('all actual source-reached inherited angular columns required')
            initial[sh['begin']:sh['end']]=value.ravel()
    def rhs(a,state):
        out=np.zeros_like(state);U=state[:324].reshape(18,18)
        lapse=float(rows['N'](a));radius=float(rows['R4'](a));H=rows['Hcan'](a)
        out[:324]=(-1j*lapse*H@U).ravel();V=rows['vertex_interpolant'](a)
        for shell in shells.values():
            d=shell['dimension'];begin,end=shell['begin'],shell['end']
            response=state[begin:end].reshape(3,d,18)
            Hn=shell['principal']/radius+np.kron(np.eye(d//18),H)
            insertion=V[:,shell['labels']].reshape(3,d,18)
            out[begin:end]=(-1j*lapse*(np.einsum('ij,Ajk->Aik',Hn,response)+insertion@U)).ravel()
        return out
    sol=solve_ivp(rhs,(s,T),initial,method='DOP853',rtol=rtol,atol=atol,max_step=T/64,dense_output=True)
    if not sol.success:raise ArithmeticError('open lepton magnetic application failed: '+sol.message)
    values=sol.sol(t).T;U=values[:,:324].reshape(len(t),18,18)
    response={str(n):values[:,sh['begin']:sh['end']].reshape(len(t),3,sh['dimension'],18) for n,sh in shells.items()}
    return dict(source_time=s,observation_times=t,constant_angular_retarded_transport=U,
        magnetic_open_fermion_response=response,
        initial_transport_identity_defect=float(np.linalg.norm(U[0]-np.eye(18))) if t[0]==s else None,
        unitary_transport_defect=float(max(np.linalg.norm(u.conj().T@u-np.eye(18)) for u in U)),
        complete_source_image_dimensions={'1':72,'3':288},
        initial_transport_identity_is_basis_not_fermion_state=True,
        inherited_open_fermion_source_columns_used=initial_first_response is not None,
        global_birth_bundle_reset_or_selected_fermion_state_claimed=False,
        Lorentz_temporal_vertex_minus_i_preserved=True,
        source_primitive_e_inserted_once=True,
        native_positive_factor_temporal_vertex_used_as_Lorentz_vertex=False,
        numerical_integrator=dict(method='DOP853',rtol=rtol,atol=atol,evaluations=sol.nfev),
        source_response_includes_actual_gauge_and_fixed_Y_H=True,
        quantum_Feynman_photon_or_Keldysh_kernel_evaluated=False,
        mixed_mean_second_operator_vertex_evaluated=False,
        external_pole_LSZ_or_normalized_Pauli_completed=False)
