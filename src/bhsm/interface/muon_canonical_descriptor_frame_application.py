"""Literal named-frame and reference-image application of a canonical Hessian.

No physical line is selected here. A historical reference is a labelled
control of a newly evaluated Schur source image. Its scalar eigenvalue
uses coefficient coordinates; only its zero can characterize the full
quotient kernel when the exported internal block is invertible. Hilbert
positivity and a physical formation/pole mode are not inferred.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import null_space


def canonical_named_frame_section(D,C,Z,geometry_indices):
    """Keep all action rows, using only the two supplied literal frames."""
    D,C,Z=(np.asarray(a,complex)for a in(D,C,Z))
    g=np.asarray(geometry_indices,int);n=len(D);nf=len(C)
    if D.shape!=(n,n)or C.shape!=(nf,n)or Z.shape!=(n,nf)or len(set(g))!=len(g):
        raise ValueError('complete original Hessian, named frames/generators and literal geometry labels required')
    if np.max(abs(C.imag),initial=0)>1e-14 or np.any(C[:,g]):
        raise ValueError('the original real-coefficient named frame must leave these geometry labels unchanged')
    ids=np.array([j for j in range(n)if j not in set(g)])
    N=null_space(C[:,ids].real)
    if N.shape!=(len(ids),len(ids)-nf):raise ValueError('every named frame must be independent')
    for j in range(N.shape[1]):
        k=np.argmax(abs(N[:,j]))
        if N[k,j]<0:N[:,j]*=-1
    Q=np.zeros((n,len(g)+N.shape[1]),complex);Q[g,np.arange(len(g))]=1
    Q[ids[:,None],len(g)+np.arange(N.shape[1])]=N
    CZ=C@Z;projection=np.eye(n)-Z@np.linalg.solve(CZ,C)
    return dict(section=Q,geometry_indices=g,internal_original_indices=ids,
        internal_section=N,quotient_hessian=Q.T@D@Q,
        original_generator_image=D@Z,named_frame_kernel_defect=C@Q,
        section_coefficient_Gram_defect=Q.T@Q-np.eye(Q.shape[1]),
        action_gauge_section_projection=projection,projection_action_defect=D@projection-D,
        gauge_frame_pairing=CZ,numerical_eigenvectors_deleted=0,
        coefficient_section_Gram_is_physical_normal_Gram=False)


def canonical_reference_schur_application(D,C,Z,geometry_indices,reference):
    """Apply an exact internal action solve to the labelled reference control.

    Both independent cross blocks are retained. The original full source
    and named reactions, not only a reduced eigenvector, are returned.
    """
    a=canonical_named_frame_section(D,C,Z,geometry_indices)
    Q=a['section'];H=a['quotient_hessian'];ng=len(geometry_indices)
    G,B,F,I=H[:ng,:ng],H[:ng,ng:],H[ng:,:ng],H[ng:,ng:]
    reference=np.asarray(reference,complex)
    if reference.shape!=(ng,)or not np.linalg.norm(reference):raise ValueError('literal labelled geometry reference required')
    ref=reference/np.linalg.norm(reference)
    row=1/np.maximum(np.max(abs(I),axis=1),np.finfo(float).tiny)
    col=1/np.maximum(np.max(abs(row[:,None]*I),axis=0),np.finfo(float).tiny)
    lift=col[:,None]*np.linalg.solve(row[:,None]*I*col[None,:],-row[:,None]*F)
    S=G+B@lift
    values,vectors=np.linalg.eig(S)
    scores=abs(vectors.conj().T@ref)/np.linalg.norm(vectors,axis=0)
    selected=int(np.argmax(scores));psi=vectors[:,selected]
    psi/=np.linalg.norm(psi)
    anchor=np.vdot(ref,psi)
    if anchor:psi*=np.exp(-1j*np.angle(anchor))
    coefficient=values[selected]
    internal=lift@psi;direction=Q@np.r_[psi,internal]
    full_source=Q[:,:ng]@(coefficient*psi)
    remainder=np.asarray(D)@direction-full_source
    reaction=np.linalg.solve(np.asarray(C)@np.asarray(C).T,np.asarray(C)@remainder)
    original_rows=remainder-np.asarray(C).T@reaction
    inverse_vectors=np.linalg.inv(vectors)
    left=inverse_vectors[selected]
    dual=left@vectors[:,selected]
    left/=dual
    # Left here is a ROW analytic dual. It is not a Hilbert dagger.
    internal_singular_values=np.linalg.svd(I,compute_uv=False)
    internal_eigenvalues=np.linalg.eigvals(I)
    return dict(**a,internal_hessian=I,internal_singular_values=internal_singular_values,
        internal_eigenvalues=internal_eigenvalues,geometry_hessian=G,geometry_internal_cross=B,
        internal_geometry_cross=F,implicit_internal_geometry_lift=lift,
        internal_linear_rows=I@lift+F,reduced_geometry_hessian=S,
        supplied_reference=ref,primitive_reference_full_image=np.asarray(D)@(Q[:,:ng]@ref),
        primitive_reference_internal_source=F@ref,internal_response_to_reference=lift@ref,
        reduced_reference_image=S@ref,reference_control_selected_index=selected,
        reference_control_eigenvalue=coefficient,reference_control_overlap=scores[selected],
        reference_control_right_geometry=psi,reference_control_left_geometry=left,
        reference_control_eigenvalues=values,reference_control_full_direction=direction,
        reference_control_full_source=full_source,named_source_frame_reaction=reaction,
        original_full_source_rows=original_rows,reduced_eigen_rows=S@psi-coefficient*psi,
        analytic_left_eigen_rows=left@S-coefficient*left,
        coefficient_left_right_pairing=left@psi,
        physical_stop_or_formation_or_pole_reference_selected=False,
        internal_balanced_condition_number=float(np.linalg.cond(row[:,None]*I*col[None,:])),
        internal_raw_condition_number=float(internal_singular_values[0]/internal_singular_values[-1]),
        internal_zero_eigenvalue_distance=float(np.min(abs(internal_eigenvalues))),
        full_kernel_Schur_equivalence_requires_internal_invertibility=True,
        reference_gap=float(np.min(abs(np.delete(values,selected)-coefficient))))
