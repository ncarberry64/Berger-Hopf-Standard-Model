"""External matching applications of the literal coupled Clifford current.

The field line is the original natural-wall inverse, including its Gauss
and frame reactions.  The fixed-Y polynomial is evaluated at physical Y;
the common-Y difference is formed before contraction.  A local first-energy
jet is retained as a jet, rather than identified with a global pole.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve, eig, sqrtm
from .muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection


def _array(value,name,shape=None):
    a=np.asarray(value,complex)
    if (shape is not None and a.shape!=shape)or not np.isfinite(a).all():
        raise ValueError('complete finite '+name+' required')
    return a


def physical_y_wall_current(coefficients,field_Green,*,y):
    """Execute -L(Y) K(Y)^-1 R(Y) G_B and both energy contacts.

    Energy contacts are the analytic dual +tau and right -tau at E=0.
    The field inverse and internal operator are held on this same graph.
    """
    yy=np.asarray(y)
    if yy.shape!=()or not np.isrealobj(yy)or not np.isfinite(yy)or yy<=0:
        raise ValueError('positive real physical fixed Y required')
    yy=float(yy);K=_array(coefficients['fermion_K0_K1_K2'],'quadratic fermion polynomial')
    R=_array(coefficients['right_numerator_coefficients'],'right numerator polynomial')
    RE=_array(coefficients['right_energy_coefficients'],'right energy polynomial',R.shape)
    L=_array(coefficients['literal_left_coefficients'],'literal left polynomial')
    LE=_array(coefficients['left_energy_coefficients'],'left energy polynomial',L.shape)
    nf=K.shape[-1];nb=R.shape[-1];GB=_array(field_Green,'same original field Green',(nb,nb))
    if K.shape!=(3,nf,nf)or R.shape!=(3,nf,6,nb)or L.shape!=(2,6,nf,nb):
        raise ValueError('complete C6 polynomial and natural-wall coordinates required')
    poly=lambda a:sum(yy**j*v for j,v in enumerate(a))
    k,r,re,l,le=map(poly,(K,R,RE,L,LE))
    rhs=np.column_stack((r.reshape(nf,-1),re.reshape(nf,-1),np.eye(nf)))
    answer=solve(k,rhs,assume_a='gen');count=6*nb
    u=answer[:,:count].reshape(r.shape);ue=answer[:,count:2*count].reshape(r.shape)
    g=answer[:,2*count:]
    contract=lambda a,b:-np.einsum('ofb,fik,bk->oi',a,b,GB,optimize=True)
    sigma=contract(l,u);sigmaE=contract(le,u)+contract(l,ue)
    return dict(self_energy_zero=sigma,self_energy_first=sigmaE,
        physical_y=yy,operator=k,right=r,right_energy=re,literal_left=l,left_energy=le,
        inverse=g,response=u,energy_response=ue,
        original_fermion_source_residual_max=float(np.max(abs(np.einsum('fg,gib->fib',k,u)-r))),
        current_energy_is_E0_first_jet=True,Gaussian_sign=-1,
        physical_finite_c_native_self_energy_identified=False)


def paired_physical_y_wall_current(coefficients,field_Green,*,y_middle,y_light):
    """Exact telescoping difference, without subtracting two currents.

    Gm-Ge=-Gm*(Km-Ke)*Ge.  All literal numerator and left contacts are
    included; odd Y terms and neutral fibers are never removed.
    """
    m=physical_y_wall_current(coefficients,field_Green,y=y_middle)
    e=physical_y_wall_current(coefficients,field_Green,y=y_light)
    ym,ye=float(y_middle),float(y_light);K=coefficients['fermion_K0_K1_K2']
    dK=(ym-ye)*K[1]+(ym*ym-ye*ye)*K[2]
    dg=-m['inverse']@dK@e['inverse']
    dpoly=lambda a:sum((ym**j-ye**j)*v for j,v in enumerate(a))
    dL=dpoly(coefficients['literal_left_coefficients']);dLE=dpoly(coefficients['left_energy_coefficients'])
    dR=dpoly(coefficients['right_numerator_coefficients']);dRE=dpoly(coefficients['right_energy_coefficients'])
    GB=np.asarray(field_Green,complex)
    apply=lambda g,r:np.einsum('fg,gib->fib',g,r,optimize=True)
    con=lambda l,u:-np.einsum('ofb,fik,bk->oi',l,u,GB,optimize=True)
    difference=lambda lm,le,dl,rm,re,dr:con(dl,apply(m['inverse'],rm))+con(le,apply(dg,rm))+con(le,apply(e['inverse'],dr))
    ds=difference(m['literal_left'],e['literal_left'],dL,m['right'],e['right'],dR)
    de=(difference(m['left_energy'],e['left_energy'],dLE,m['right'],e['right'],dR)
        +difference(m['literal_left'],e['literal_left'],dL,m['right_energy'],e['right_energy'],dRE))
    return dict(middle=m,light=e,paired_self_energy_zero=ds,paired_self_energy_first=de,
        paired_inverse=dg,odd_Y_terms_retained=True,
        telescoping_vs_raw_current_difference=m['self_energy_zero']-e['self_energy_zero']-ds,
        telescoping_vs_raw_energy_difference=m['self_energy_first']-e['self_energy_first']-de,
        paired_current_is_a_complete_fixed_Y_polynomial_application=True,
        paired_current_is_a_complete_native_or_Pauli_application=False)


def full_c6_positive_pole_jet(H,self_energy_zero,self_energy_first,*,family,matched_mass_action,tree_body=None):
    """Retain all four complementary fibers in the charged-upper test jet.

    With tree_body supplied, S6(E)=E(I-Sigma_E)-Hcan-Sigma_0 on the
    actual constant-angular coefficient action.  Otherwise this is only
    the mass-only normal-symbol matching pencil M_fixedY(H); a Wilson
    transform of the constant-angular current is still required.  The
    scalar part of the charged-upper test Schur block
    is the mass matching load, while the remaining spin/complex matrix is
    exported.  No counterterm changes a Yukawa or discards that remainder.
    The six roots below belong only to this affine local energy pencil.
    """
    h=_array(H,'actual Higgs doublet',(2,));s0=_array(self_energy_zero,'same C6 current',(6,6))
    s1=_array(self_energy_first,'same C6 energy first jet',(6,6));mm=np.asarray(matched_mass_action)
    if type(family)is not int or family not in(1,2)or mm.shape!=()or not np.isrealobj(mm)or not np.isfinite(mm)or mm<=0:
        raise ValueError('retained family and positive matched mass parameter required')
    m=float(mm);ids=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
    inj=charged_dirac_injection(h,family=family)
    U=np.column_stack((inj['charged'][ids],inj['neutral'][ids]))
    M=fixed_y_higgs_hamiltonian(h[None])[0][np.ix_(ids,ids)];G=np.eye(6)-s1
    body=M if tree_body is None else _array(tree_body,'actual C6 tree body',(6,6))
    S=m*G-body-s0;A=U.conj().T@S@U;D=U.conj().T@G@U
    # Eliminate four complementary fibers in one operation.  This equals
    # successive neutral and negative charged Schur reduction.
    C=A[2:,2:];X=solve(C,A[2:,:2],assume_a='gen')
    gC=solve(C,np.eye(4),assume_a='gen')
    ret=A[:2,2:]@X;pole=A[:2,:2]-ret
    dp=(D[:2,:2]-D[:2,2:]@X-A[:2,2:]@gC@D[2:,:2]
        +A[:2,2:]@gC@D[2:,2:]@X)
    right=np.vstack((np.eye(2),-X));left=np.column_stack((np.eye(2),-A[:2,2:]@gC))
    mass=np.trace(pole)/2;kinetic=np.trace(dp)/2
    roots,vl,vr=eig(body+s0,G,left=True,right=True)
    residues=[];den=[]
    for i in range(6):
        d=vl[:,i].conj()@G@vr[:,i];den.append(d)
        residues.append(np.outer(vr[:,i],vl[:,i].conj())/d)
    return dict(full_C6_inverse_symbol=S,full_C6_energy_derivative=G,
        charged_neutral_inverse_symbol=A,charged_neutral_energy_derivative=D,
        matched_positive_inverse=pole,matched_positive_energy_derivative=dp,
        full_complement_return=ret,positive_right_lift=U@right,positive_literal_left_lift=left@U.conj().T,
        isotropic_mass_matching_load=mass,remaining_complex_spin_pole_matrix=pole-mass*np.eye(2),
        isotropic_kinetic_matching_load=kinetic-1,
        remaining_complex_kinetic_matrix=dp-kinetic*np.eye(2),
        full_positive_residue=solve(dp,np.eye(2),assume_a='gen'),
        local_affine_pencil_poles=roots,local_affine_pencil_residue_matrices=np.array(residues),
        local_affine_pencil_residue_denominators=np.array(den),
        full_C6_to_positive_inverse_residual=(U.conj().T@solve(S,U[:,:2],assume_a='gen'))[:2]-solve(pole,np.eye(2),assume_a='gen'),
        derivative_dual_identity_residual=left@D@right-dp,
        complementary_block_condition_number=float(np.linalg.cond(C)),
        fixed_Y_operator=M,actual_tree_body=body,charged_neutral_injection=U,
        matched_mass_action=m,physical_family=family,
        matching_equations='S_plus(m)-delta_m*I=0 and S_plus_prime(m)+delta_Z=I; noncentral/imaginary remnants exported, not assigned zero',
        matched_mass_is_independent_of_tree_Y_H=True,
        same_background_constant_angular_tree_body_retained=tree_body is not None,
        mass_only_normal_symbol_matching_premise=tree_body is None,
        constant_angular_kernel_to_normal_Wilson_symbol_identified=False,
        charged_upper_tests_identified_as_actual_positive_pole_states=False,
        Yukawa_replaced_or_mass_counterterm_applied=False,
        local_energy_linearization_is_global_LSZ=False,
        physical_F2=None,physical_a_mu=None,physical_g_mu=None)


def normalized_pole_spin_covectors(pole_application,*,electric_charge):
    """Dualize the full complementary return before magnetic projection.

    The analytic symmetric normalizer is Z=S_+'(m)^(-1/2), and
    ell=Z*ell_raw, r=r_raw*Z.  Thus ell*S6'*r=I.  This is the exact
    linear contact at the supplied local mass point.  A nonzero S_+(m)
    remains a pole matching remainder, so no physical LSZ is inferred.
    """
    e=np.asarray(electric_charge)
    if e.shape!=()or not np.isrealobj(e)or not np.isfinite(e)or e<=0:
        raise ValueError('independently matched positive charge required')
    from .muon_magnetic_open_lepton_vertex import PAULI
    a=pole_application;dp=_array(a['matched_positive_energy_derivative'],'full pole derivative',(2,2))
    z=np.asarray(sqrtm(solve(dp,np.eye(2),assume_a='gen')),complex)
    left=z@a['positive_literal_left_lift'];right=a['positive_right_lift']@z
    m=float(a['matched_mass_action']);charge=float(e)
    weights=np.array([(m/charge*(right@s@left)).T for s in PAULI])
    return dict(normalized_literal_left_pole_test=left,normalized_right_pole_test=right,
        analytic_pole_Gram_normalizer=z,full_C6_magnetic_spin_tensor_weight=weights,
        pole_current_normalization_residual=left@a['full_C6_energy_derivative']@right-np.eye(2),
        inverse_sqrt_identity_residual=z@dp@z-np.eye(2),
        full_C6_source_error_amplification_estimate=np.array([np.linalg.norm(w)for w in weights]),
        pole_Gram_Hermitian_defect=dp-dp.conj().T,
        normalized_pole_matching_remainder=z@a['matched_positive_inverse']@z,
        negative_charged_and_neutral_state_motion_retained=True,
        normalization_rule='spin_k=(2m/e)*Tr(sigma_k ell V r)/2; ell S6_prime r=I with literal analytic left',
        matrix_source_bound_scope='Frobenius dual Cauchy estimate at this exact stored matching jet; no operator/eigen/continuum or physical error enclosure',
        physical_pole_and_LSZ_identified=False,physical_F2=None)
