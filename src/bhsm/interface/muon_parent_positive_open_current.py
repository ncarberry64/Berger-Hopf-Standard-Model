"""Apply retained YM curvature contact to the complete lepton wall image.

These are full18 action-current contractions on the executed finite
positive reference, with stable inverse differences.  Neither point-fiber
currents nor a finite Lorenz section are called interacting LSZ states.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP


def canonical_current_wall_contraction(wall_kernel,vertices):
    """Full n0-to-odd18 current contraction, normalized angular modes.

    phi_h=Y_h/sqrt(V), phi0=1/sqrt(V), int dOmega Y_h Y_j=V delta.
    Thus the angular product has no further V.  Ar has no intrinsic
    Dirac vertex; its propagation/mixed contacts remain in wall_kernel.
    This contraction does not insert the intermediate fermion Green.
    """
    K=np.asarray(wall_kernel);V=np.asarray(vertices)
    if (K.shape!=(400,400) or V.shape!=(5,4,18,18) or
        not np.isfinite(K).all() or not np.isfinite(V).all()):
        raise ValueError('full400 wall form and full18 canonical current vertices required')
    K=K.reshape(20,20,20,20) # (field*internal,harmonic,field*internal,harmonic)
    contracted=np.einsum('ahbh->ab',K)
    v=V.reshape(20,18,18)
    return np.einsum('aij,ab,bjk->ik',v.conj().transpose(0,2,1),contracted,v)


def actual_positive_open_current_application(raw_fields,representation,gauge):
    """Consume the actual form/Gram/current; no inferred quotient or Pauli.

    Pi=I-DG*K_FP^-1*B is the evaluated finite Lorenz section.  The
    nonzero off-shell Euler contact prevents declaring it a physical
    quotient.  Its curvature form is tested on the actual Riesz image
    of every wall current, not just a vector unrelated to the consumer.
    G-G0=-G0*C*G retains the small literal curvature contribution.
    Scalar boundary gauge-H mixed blocks are still composed separately.
    """
    required=('one_form_YM_Hessian','one_form_curvature_contact','one_form_Gram',
        'ghost_FP_Hessian','weak_gradient_pairing','ghost_gradient_coordinate_injection',
        'Lorenz_gauge_fixing','gauge_fixed_Green','wall_projected_value_map')
    if any(key not in gauge for key in required):raise ValueError('same full retained gauge application required')
    K,C,G,Kg,B,Z,fix,Green,W=(np.asarray(gauge[key]) for key in required)
    if any(not np.isrealobj(a) or not np.isfinite(a).all() for a in (K,C,G,Kg,B,Z,fix,Green,W)):
        raise ValueError('finite real retained action and same Hilbert/trace maps required')
    op=primal_trace_enriched_lepton_operator(raw_fields,representation)
    vertex=canonical_open_field_vertices(op['R4'],op['N'])['gauge']
    Pi=np.eye(1120)-Z@solve(Kg,B,assume_a='gen')
    image=Pi@solve(G,W.T,assume_a='gen')
    wall_contact=image.T@C@image
    open_contact=canonical_current_wall_contraction(wall_contact,vertex)
    no_contact=K-C+fix
    # Reuse the SAME Hilbert congruence rather than losing small terms in
    # an original-coordinate eigenvector reconstruction.
    from scipy.linalg import cholesky,solve_triangular
    chol=cholesky(G,lower=True);P0=solve_triangular(chol,no_contact,lower=True)
    P0=solve_triangular(chol,P0.T,lower=True).T
    inv=solve(P0,np.eye(1120),assume_a='gen')
    Green0=solve_triangular(chol.T,inv,lower=False)
    Green0=solve_triangular(chol.T,Green0.T,lower=False).T
    stable=-(W@Green0)@C@(Green@W.T)
    # The retained Maxwell action is per kappa1; the common assigned cap
    # action uses MAXWELL_TO_CAP.  Its Green is larger by its inverse.
    open_return=canonical_current_wall_contraction(stable,vertex)/MAXWELL_TO_CAP
    from .muon_parent_positive_gauge_form import stored_inverse_neumann_majorant
    return dict(canonical_gauge_vertices=vertex,finite_Lorenz_projection=Pi,
        complete_wall_current_Riesz_image=image,wall_current_curvature_form=wall_contact,
        full18_open_current_curvature_form=open_contact,
        no_curvature_normalized_operator=P0,no_curvature_normalized_Green=inv,
        stable_wall_curvature_Green_return=stable,
        full18_open_current_curvature_Green_return_cap=open_return,
        no_curvature_inverse_majorant=stored_inverse_neumann_majorant(P0,inv),
        current_image_Lorenz_relative_defect=float(np.linalg.norm(B@image)/(np.linalg.norm(B)*np.linalg.norm(image))),
        no_curvature_inverse_relative_backward_error=float(np.linalg.norm(no_contact@Green0-np.eye(1120))/(np.linalg.norm(no_contact)*np.linalg.norm(Green0))),
        common_cap_action_Maxwell_factor=float(MAXWELL_TO_CAP),
        full18_current_and_complete_odd_harmonics_retained=True,
        intermediate_fermion_Green_inserted=False,
        stable_inverse_difference_used=True,
        physical_Gauss_BRST_quotient_or_canonical_P_strat_identified=False,
        scalar_gauge_boundary_mass_mixed_blocks_included=False,
        interacting_pole_LSZ_or_Pauli_assigned=False,
        physical_a_mu=None,physical_g_mu=None)
