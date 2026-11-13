"""Reached intrinsic-Higgs Jacobi Green and fixed-Y mixed Green contraction.

The domain is the existing coefficient-cell temporal Dirichlet tent and
complete scalar n=1,3 shells.  This is the elliptic intrinsic-M4 Gaussian
block, not the EC-HS auxiliary or the Lorentz retarded field inverse.
No interacting external pole, statistics factor, or Pauli value is assigned.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eigh
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from .muon_parent_maxwell_corrected_retarded import higgs_u2_real_representation
from .muon_current_source_motion_cubic import current_face_source_jets
from .muon_parent_maxwell_full_weak import M


def common_heat_two_green_kernel(p,q,cutoff,*,order=24):
    """Exact integral definition of the common-cutoff two-Green kernel.

    L_c(p,q)=int_{u,v>=0,u+v>=c}exp(-up-vq)du dv
             =-g_c[1](p,q), g_c(p)=exp(-cp)/p.
    The positive simplex formula removes p=q cancellation.  Its c=0
    value is exactly 1/(pq).  Quadrature errors are diagnostics here.
    """
    p,q=np.asarray(p,float),np.asarray(q,float);c=float(cutoff)
    if p.ndim!=1 or q.ndim!=1 or min(len(p),len(q))==0 or any(not np.isfinite(a).all() or np.min(a)<=0 for a in (p,q)) or not np.isfinite(c) or c<0:
        raise ValueError('positive finite operator spectra and explicit nonnegative common cutoff required')
    if type(order) is not int or order<8:raise ValueError('resolved divided-difference quadrature required')
    if c==0:return 1/(p[:,None]*q[None,:])
    nodes,weights=np.polynomial.legendre.leggauss(order);nodes=(nodes+1)/2;weights/=2
    out=np.zeros((len(p),len(q)))
    for v,w in zip(nodes,weights):
        k=(1-v)*p[:,None]+v*q[None,:]
        out+=w*np.exp(-c*k)*(c/k+1/k**2)
    return out


def intrinsic_higgs_cell_jacobi(raw_fields,representation,angular,*,length):
    """Build the actual real-linear positive cell Jacobi and its action Gram.

    Real scalar chart (ReH1,ReH2,ImH1,ImH2); kinetic pairing2Re.
    S4 enters the common cap action with 1/V², V=2pi².  Thus its
    real-field tent Gram is 2 V wV L/(3 V²), and K=Gram*P.
    Temporal b b' integrates to zero but the material At² remains.
    The positive spatial kinetic and potential Hessian are retained.
    """
    x=np.asarray(raw_fields);L=float(length)
    if not np.isrealobj(x) or x.shape!=(268,) or not np.isfinite(x).all() or not np.isfinite(L) or L<=0:
        raise ValueError('actual complete real raw268 and positive existing cell length required')
    op=primal_trace_enriched_lepton_operator(x,representation)
    w=current_face_source_jets(x[:100])['intrinsic_weights'];wt,ws,wv=(w[k].value for k in ('wT','wS','wV'))
    if min(wt,ws,wv)<=0:raise ValueError('positive actual intrinsic metric weights required')
    A=np.einsum('fcj,j->fc',representation['wall_trace_map'],x[100:180])
    A[2:]+=M*(w['mechanical_connection_lambda'].value-1)
    T=higgs_u2_real_representation()['real_generators'];Omega=np.einsum('fc,cij->fij',A,T)
    I=np.eye(20);E=np.asarray(angular['derivative_matrices'])
    Dt=np.kron(Omega[0],I)
    Ds=np.array([np.kron(np.eye(4),E[i])+np.kron(Omega[2+i],I) for i in range(3)])
    H=x[-8:-4];lam=float(representation['scalar_matching']['lambda_H'])
    # The evaluated endpoint/phase carries nu²4; caller must bind this
    # assigned parameter explicitly through representation below.
    if 'native_positive_nu_squared_action' not in representation:
        raise ValueError('explicit same-action nu_squared binding required')
    nu=float(representation['native_positive_nu_squared_action'])
    if not np.isfinite([lam,nu]).all() or lam<=0 or nu<0:raise ValueError('actual scalar coupling/center required')
    potential=np.kron(lam*(4*np.outer(H,H)+2*(H@H-nu)*np.eye(4)),I)
    temporal=(12*wt/(wv*L**2))*np.eye(80)
    time_connection=(wt/wv)*(Dt.T@Dt)
    spatial=(ws/wv)*sum(d.T@d for d in Ds)
    P=temporal+time_connection+spatial+potential
    values,U=eigh(P)
    if values[0]<=0:raise ArithmeticError('actual assigned cell Higgs Jacobi is not positive')
    V=2*np.pi**2;gram=2*V*wv*L/(3*V**2)
    inverse=(U/values)@U.T/gram
    return dict(operator=P,action_Hessian=gram*P,action_Gram=gram*np.eye(80),
        action_Gram_scalar=gram,Green=inverse,eigenvalues=values,eigenvectors=U,
        temporal=temporal,time_connection=time_connection,spatial=spatial,potential=potential,
        covariant_angular_derivative=Ds,material_temporal_connection=Dt,
        inverse_residual=float(np.linalg.norm(gram*P@inverse-np.eye(80))),
        scalar_matching=dict(lambda_H=lam,nu_squared_action=nu),operator_lepton=op,
        temporal_domain='existing Dirichlet tent b; int b²=L/3, int bprime²=4/L, int b bprime=0',
        angular_domain='complete real scalar n1+n3 shells tensor weak doublet;80 real coordinates',
        pairing='real2Re; unitHaar timesV once; common cap S4/V²',
        intrinsic_H_identified_with_EC_HS_auxiliary=False,
        induced_Gamma_positive_claimed=False,physical_native_domain_complete=False)


def intrinsic_higgs_mixed_green_application(raw_fields,representation,angular,*,length,cutoff,order=24):
    """Apply the actual fixed-Y B_H to positive field/fermion Green blocks.

    The exported matrix is the literal common-proper-time contraction
    sum_a B_a^dagger L_c(P_F,p_Ha) A_F^dagger B_a / Gram_H.
    B_H is the mixed open-lepton/field Hessian, with both LR placements.
    The b³/b²=3/4 vertex moment is included once.  No Grassmann/Wick
    sign, complete graded determinant, exterior LSZ or F2 is inferred
    from this contraction.  It is not the Lorentz retarded inverse.
    """
    H=intrinsic_higgs_cell_jacobi(raw_fields,representation,angular,length=length)
    op=H['operator_lepton'];L=float(length);E=angular['derivative_matrices']
    alpha=lepton_current_hilbert_representation()['alpha']
    A=-1j*sum(np.kron(E[i],alpha[i]) for i in range(3))/op['R4']+np.kron(np.eye(20),op['W']+op['Omega_tau'])
    PF=(12/(op['N']**2*L**2))*np.eye(360)+A.conj().T@A
    f,V=eigh(PF)
    if f[0]<=0:raise ArithmeticError('same native fermion product factor is not positive')
    mass_vertices=canonical_open_field_vertices(op['R4'],op['N'])['scalar']
    B=np.zeros((80,360,18),complex)
    for c in range(4):
        for h in range(20):B[c*20+h,h*18:(h+1)*18]=(3/4)*mass_vertices[c]
    transformed=(H['eigenvectors'].T@B.reshape(80,-1)).reshape(B.shape)
    left=transformed.conj().transpose(0,2,1)@V
    right=(V.conj().T@A.conj().T)@transformed
    weights=common_heat_two_green_kernel(f,H['eigenvalues'],cutoff,order=order)
    value=np.einsum('aij,ja,ajk->ik',left,weights,right)/H['action_Gram_scalar']
    inverse_fermion=(V/f)@V.conj().T
    weighted=(H['Green']@B.reshape(80,-1)).reshape(B.shape)
    unregulated=np.einsum('aiu,auj->ij',B.conj().transpose(0,2,1),(inverse_fermion@A.conj().T)@weighted)
    return dict(Higgs=H,fermion_positive_operator=PF,fermion_factor=A,
        fermion_eigenvalues=f,fermion_eigenvectors=V,
        mixed_vertices=B,mixed_Green_contraction=value,
        unregulated_mixed_Green_contraction=unregulated,
        cutoff=float(cutoff),divided_difference_order=order,
        common_cutoff_on_total_two_Green_proper_time=True,
        native_factor_Green_order='(A_dagger A+temporal)^(-1) A_dagger; no nonnormal reorder',
        derivative_source_projection='same tent mixed source has int b² bprime=0; full differential source/image complement not removed by an operator identity',
        temporal_vertex_moment=3/4,complete_lepton_fiber_dimension=18,
        actual_fixed_Y_operator_retained=True,both_LR_mass_placements_retained=True,
        no_c_number_fermion_or_CAR_state_selected=True,
        lepton_source_Gram='chi_hat=R4^(3/2)psi/V; unit canonical current',
        EC_HS_and_gauge_ghost_blocks_included=False,
        graded_quantum_self_energy_completed=False,
        external_photon_derivative_or_LSZ_or_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 exact supplied coefficient-cell application with quadrature diagnostic; no upstream, continuum or physical matching enclosure')
