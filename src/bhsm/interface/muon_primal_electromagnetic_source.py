"""Higgs-aligned electromagnetic source on the reached common action.

The local neutral line is derived from the actual H doublet.  Its eight
spatial wavefunctions are the retained coexact photon wavefunctions, not
an arbitrary embedding of a Lorentz current into the old transported Q8.
The resulting connection source and its motion precede Gauss elimination.
This selects neither external LSZ states nor an external soft momentum.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_attached_phase import load_attached_endpoint
from .muon_chronological_charged_current import chronological_phase_cell
from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from .muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from .muon_current_source_motion_cubic import current_face_source_jets
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from .aether_exact_radial_schur_lift_v15_83 import Jet


PAULI = np.array([[[0,1],[1,0]], [[0,-1j],[1j,0]], [[1,0],[0,-1]]],complex)


def higgs_aligned_charge(H,H_rate):
    """Exact local neutral line and derivative on an explicitly nonzero H.

    P_H=HH†/(H†H), Q_L=-P_H, Q_R=-1.  This commutes with M(YH),
    but need not commute with the actual charged spatial connection.
    H_rate is on the future coordinate clock; it is never an input gap.
    """
    arrays=[np.asarray(x,complex) for x in (H,H_rate)]
    if any(x.shape!=(2,) or not np.isfinite(x).all() for x in arrays):
        raise ValueError('actual finite complex H and H_rate doublets required')
    h,hd=arrays;norm=float(np.vdot(h,h).real)
    if norm<=0:raise ValueError('H-selected neutral line requires nonzero actual H')
    P=np.outer(h,h.conj())/norm
    Pd=(np.outer(hd,h.conj())+np.outer(h,hd.conj()))/norm-P*(2*np.vdot(h,hd).real/norm)
    bloch=np.einsum('aij,ji->a',PAULI,P).real
    bloch_rate=np.einsum('aij,ji->a',PAULI,Pd).real
    s=np.r_[-np.sqrt(2)*bloch,np.sqrt(10/3)]
    sd=np.r_[-np.sqrt(2)*bloch_rate,0.]
    Q=np.zeros((18,18),complex);Q[:12,:12]=-np.kron(P,np.eye(6));Q[12:,12:]=-np.eye(6)
    Qd=np.zeros_like(Q);Qd[:12,:12]=-np.kron(Pd,np.eye(6))
    radius=np.sqrt(norm);rd=np.vdot(h,hd).real/radius
    U=np.array([[h[1].conjugate(),h[0]],[-h[0].conjugate(),h[1]]])/radius
    Ud=np.array([[hd[1].conjugate(),hd[0]],[-hd[0].conjugate(),hd[1]]])/radius-U*rd/radius
    frame=np.zeros_like(Q);frame[:12,:12]=np.kron(U,np.eye(6));frame[12:,12:]=np.eye(6)
    frame_rate=np.zeros_like(Q);frame_rate[:12,:12]=np.kron(Ud,np.eye(6))
    G=lepton_unit_trace_gauge_representation()['generators']
    return dict(charge=Q,charge_rate=Qd,unit_Tr16_coefficients=s,
        unit_Tr16_coefficient_rate=sd,H_projector=P,H_projector_rate=Pd,
        aligned_frame=frame,aligned_frame_rate=frame_rate,
        generator_reconstruction_defect=float(np.linalg.norm(np.einsum('c,cij->ij',s,G)+1j*Q)),
        generator_derivative_defect=float(np.linalg.norm(np.einsum('c,cij->ij',sd,G)+1j*Qd)),
        mass_charge_commutator_defect=float(np.linalg.norm(Q@fixed_y_higgs_hamiltonian(h[None])[0]-fixed_y_higgs_hamiltonian(h[None])[0]@Q)),
        neutral_H_residual=float(np.linalg.norm(P@h-h)),
        coordinate_rate='future coordinate time; proper rate is divided by induced N once',
        global_charge_invariant_background_claimed=False)


def higgs_aligned_source(angular,H,H_rate):
    """Reuse the exact retained coexact wavefunctions with the actual Q_H.

    Hypercharge is unchanged by the retained carrier transport, hence its
    component recovers the spatial photon wavefunctions without rotating
    spin/coframe indices.  Every original and residual angular column is
    retained.  A nonzero span residual forbids reusing an old Q8 inverse.
    """
    old=np.asarray(angular['source_coefficients'])
    if not np.isrealobj(old) or old.shape!=(400,8) or not np.isfinite(old).all():
        raise ValueError('complete retained real full400x8 source required')
    coefficients=old.reshape(5,4,20,8)
    wavefunctions=coefficients[:,3]/np.sqrt(10/3)
    if np.any(wavefunctions[:2]):raise ValueError('retained spatial photon wavefunctions required')
    alignment=higgs_aligned_charge(H,H_rate)
    Q=np.einsum('fhA,c->fchA',wavefunctions,alignment['unit_Tr16_coefficients']).reshape(400,8)
    Qd=np.einsum('fhA,c->fchA',wavefunctions,alignment['unit_Tr16_coefficient_rate']).reshape(400,8)
    inclusion=np.linalg.solve(old.T@old,old.T@Q)
    remainder=Q-old@inclusion
    return dict(source=Q,source_rate=Qd,wavefunctions=wavefunctions,
        charge_alignment=alignment,source_Gram=Q.T@Q,
        old_source_best_fit=inclusion,old_source_span_remainder=remainder,
        old_source_span_relative_residual=float(np.linalg.norm(remainder)/np.linalg.norm(Q)),
        source_owner='same unit-Tr16 Q_H=T_H+Y and inherited eight spatial coexact wavefunctions',
        old_transported_source_inverse_reused=False,
        canonical_electric_charge_or_soft_momentum_selected=False)


def higgs_aligned_source_first_jets(raw,angular):
    """Analytic Q/Qdot raw268 derivatives for the sourced cubic chain rule.

    Q=Tb S(H), Qdot=Tbdot S(H)+Tb D_H S(H) Hdot.  Differentiating
    Qdot needs the exact Hessian of the normalized Bloch vector, not a
    frozen H axis or a second independently fitted source motion.
    """
    x=np.asarray(raw)
    if not np.isrealobj(x) or x.shape!=(268,) or not np.isfinite(x).all():
        raise ValueError('complete finite real reached raw268 required')
    h=x[-8:-4];hd=x[-4:];H=h[:2]+1j*h[2:];Hd=hd[:2]+1j*hd[2:]
    source=higgs_aligned_source(angular,H,Hd)
    v=[Jet(float(z),np.eye(4)[i],np.zeros((4,4))) for i,z in enumerate(h)]
    norm=sum(z*z for z in v)
    bloch=(2*(v[0]*v[1]+v[2]*v[3])/norm,
           2*(v[0]*v[3]-v[2]*v[1])/norm,
           (v[0]*v[0]+v[2]*v[2]-v[1]*v[1]-v[3]*v[3])/norm)
    gs=np.zeros((4,4));hs=np.zeros((4,4,4))
    for i,b in enumerate(bloch):gs[i]=-np.sqrt(2)*b.gradient;hs[i]=-np.sqrt(2)*b.hessian
    wave=source['wavefunctions'];S=source['source'];Sd=source['source_rate']
    S_h=np.einsum('fhA,ci->ifchA',wave,gs).reshape(4,400,8)
    Sd_h=np.einsum('fhA,ci->ifchA',wave,np.einsum('cij,j->ci',hs,hd)).reshape(4,400,8)
    ds=np.zeros((268,400,8));ds[-8:-4]=S_h
    dsd=np.zeros_like(ds);dsd[-8:-4]=Sd_h;dsd[-4:]=S_h
    face=current_face_source_jets(x[:100]);t=face['T_b'];td=face['T_b_dot']
    tg=np.r_[t.gradient,np.zeros(168)];tdg=np.r_[td.gradient,np.zeros(168)]
    source.update(connection_source=t.value*S,connection_source_rate=td.value*S+t.value*Sd,
        Q_first_jet=tg[:,None,None]*S+t.value*ds,
        Qdot_first_jet=tdg[:,None,None]*S+td.value*ds+tg[:,None,None]*Sd+t.value*dsd,
        T_b=float(t.value),T_b_dot=float(td.value),
        first_jet_order='raw268 geometry100, independent gauge80/value-rate80, Hreal4/Hdotreal4',
        source_motion_count=1,future_coordinate_time_rate=True,
        source_first_jets_are_analytic=True)
    return source


def clifford_field_jet_projection(operator,alignment,*,family=1):
    """Apply the fixed-base charged LR Clifford projector to reached jets.

    The primitive covariant field insertion is -gamma0 D(H_can).  Its
    Clifford tensor component is not an on-shell F2: scalar Gordon terms,
    open-fermion loops and moving external injections can survive that
    projector.  The full neutral-left leakage is returned explicitly.
    """
    if type(family) is not int or family not in (0,1,2):raise ValueError('retained family index required')
    gamma=retained_higgs_spin_charge_representation()['gamma_LR']
    gamma5=1j*gamma[0]@gamma[1]@gamma[2]@gamma[3]
    tensors=np.array([.5j*(gamma[i]@gamma[j]-gamma[j]@gamma[i]) for i in range(4) for j in range(i+1,4)])
    basis=np.array([np.eye(4),gamma5,*gamma,*[g@gamma5 for g in gamma],*tensors])
    U=alignment['aligned_frame'];jets=operator['H_can_raw_first_jet']
    aligned=np.einsum('ij,rjk,kl->ril',U.conj().T,jets,U)
    ids=np.array([6+2*family,7+2*family,12+2*family,13+2*family])
    neutral=np.array([2*family,2*family+1])
    vertices=-gamma[0]@aligned[:,ids][:,:,ids]
    coeff=np.einsum('aij,rji->ra',basis.conj().transpose(0,2,1),vertices)/4
    reconstructed=np.einsum('ra,aij->rij',coeff,basis)
    return dict(covariant_primitive_field_vertices=vertices,Clifford_coefficients=coeff,
        Clifford_tensor_coefficients=coeff[:,10:],Clifford_basis=basis,
        complete_Clifford_reconstruction_defect=float(np.linalg.norm(reconstructed-vertices)),
        charged_to_neutral_first_jet=aligned[:,neutral][:,:,ids],
        Clifford_tensor_projection_norm=float(np.linalg.norm(coeff[:,10:])),
        primitive_tensor_zero_is_physical_Pauli_zero=False,
        reason='on-shell Gordon equivalence and genuine delta_barPsi delta_Psi delta_A quantum vertex are separate',
        external_soft_derivative_evaluated=False)


def matched_breit_pauli_projection(vertex,mass,spatial_transfer):
    """Two-spin on-shell quotient on the matched LOCAL Dirac pole.

    Both spin columns are retained, with ubar u=2m.  This ordinary
    projection is also sensitive to scalar Gordon terms which an
    off-shell Clifford-tensor trace would miss.  It cannot turn a beta
    amplitude into external q or supply the interacting native vertex.
    """
    v=np.asarray(vertex,complex);q=np.asarray(spatial_transfer)
    if (v.shape!=(4,4,4) or not np.isfinite(v).all() or not np.isrealobj(q)
        or q.shape!=(3,) or not np.isfinite(q).all() or not np.isfinite(mass) or mass<=0 or not np.any(q)):
        raise ValueError('finite covariant vertex, positive matched mass and nonzero real transfer required')
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac']
    E=float(np.sqrt(mass**2+(q@q)/4));r=np.sqrt(E+mass)
    spin=lambda p:np.vstack((r*np.eye(2),np.einsum('a,aij->ij',p,PAULI)/r))
    incoming=spin(-q/2);outgoing=spin(q/2);bar=outgoing.conj().T@gamma[0]
    qc=np.r_[0.,-q]
    p=np.array([sum((-.5*(gamma[mu]@gamma[nu]-gamma[nu]@gamma[mu])*qc[nu]/(2*mass)
                    for nu in range(4)),np.zeros((4,4),complex)) for mu in range(4)])
    D=bar@gamma@incoming;P=bar@p@incoming;actual=bar@v@incoming
    basis=np.column_stack((D.ravel(),P.ravel()));coeff,_,rank,singular=np.linalg.lstsq(basis,actual.ravel(),rcond=None)
    if rank!=2:raise ArithmeticError('nondegenerate matched on-shell Dirac/Pauli quotient required')
    remainder=actual.ravel()-basis@coeff
    return dict(F1=complex(coeff[0]),F2=complex(coeff[1]),
        on_shell_vertex=actual,Dirac_amplitudes=D,Pauli_amplitudes=P,
        relative_tensor_remainder=float(np.linalg.norm(remainder)/max(np.linalg.norm(actual),np.finfo(float).tiny)),
        basis_condition=float(singular[0]/singular[-1]),
        incoming_spin_columns=incoming,outgoing_spin_columns=outgoing,
        mass_shell_residual=float(np.linalg.norm((gamma[0]*E+np.einsum('a,aij->ij',q/2,gamma[1:])-mass*np.eye(4))@incoming)),
        pole_scope='measured matched local Dirac pole; actual interacting native pole/vertex not supplied by this quotient',
        native_Pauli_or_zero_transfer_limit_completed=False)


def retained_phase_source_inputs(phase_directory,*,repository=ROOT):
    """Bind the full220 saved phase and every action/hash before applying Q_H."""
    root=Path(repository);folder=Path(phase_directory)
    if not folder.is_absolute():folder=root/folder
    receipt_path=folder/'result.json';archive=folder/'application.npz'
    receipt=json.loads(receipt_path.read_bytes())
    if (receipt['scope']!='EVALUATED_ATTACHED_FULL_FIELD_ACTION_PHASE_CONTINUATION'
        or receipt['steps']!=1 or receipt['completed_steps']!=1
        or receipt['stages'][0]['status']!='REPRESENTED_PHASE_TOLERANCE'):
        raise ValueError('completed actual full220 one-cell phase required')
    if sha256(archive.read_bytes()).hexdigest()!=receipt['numerical_sha256']:
        raise ValueError('same-action phase archive changed')
    hashes=dict(receipt['input_hashes'])
    for path,digest in hashes.items():
        if sha256((root/path).read_bytes()).hexdigest()!=digest:raise ValueError('action owner changed: '+path)
    endpoint=load_attached_endpoint(receipt['consumed_paired_endpoint_path'],side=receipt['side'],repository=root,
        radial_points=receipt['radial_points'],cap_points=receipt['cap_points'])
    if endpoint['receipt']['row_count']!=220 or endpoint['receipt_sha256']!=receipt['consumed_receipt_sha256']:
        raise ValueError('same full220 endpoint attachment required')
    with np.load(archive,allow_pickle=False) as a:values={k:a[k].copy() for k in a.files}
    if not np.array_equal(values['initial_master'],endpoint['master']):raise ValueError('phase initial attachment differs')
    cell=chronological_phase_cell(values['stage_jacobian'][0],values['stage_unknowns'][0],values['initial_master'],values['initial_p'],endpoint['representation'],receipt['span'])
    if not np.array_equal(cell['midpoint_raw'],values['stage_midpoint_raw'][0]):raise ValueError('same actual midpoint required')
    for p in (receipt_path,archive):hashes[p.relative_to(root).as_posix()]=sha256(p.read_bytes()).hexdigest()
    return dict(receipt=receipt,representation=endpoint['representation'],cell=cell,values=values,input_hashes=hashes)


def electromagnetic_source_sample(raw,representation,angular):
    """Evaluate the actual future-clock H-frame and metric source motion."""
    a=primal_trace_enriched_lepton_operator(raw,representation)
    rate=np.asarray(raw)[-4:];Hd=rate[:2]+1j*rate[2:]
    source=higgs_aligned_source_first_jets(raw,angular)
    source.update(lepton_operator=a,
        local_charge_evolution_commutator_norm=float(np.linalg.norm(source['charge_alignment']['charge']@a['H_can']-a['H_can']@source['charge_alignment']['charge'])),
        local_charge_covariant_time_norm=float(np.linalg.norm(source['charge_alignment']['charge_rate']/a['N']+a['Omega_tau']@source['charge_alignment']['charge']-source['charge_alignment']['charge']@a['Omega_tau'])),
        Clifford_application=clifford_field_jet_projection(a,source['charge_alignment']),
        source_coordinate='unit charged connection beta=Tb*b; no separate fitted gauge normalization',
        canonical_EM_conversion='Omega_photon=-i e Q_H A_can; canonical residue/charge matching must transform source action and currents consistently',
        source_motion_count=1,physical_Pauli_value=False)
    return source
