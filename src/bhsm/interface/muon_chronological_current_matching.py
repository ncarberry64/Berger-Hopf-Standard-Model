"""Source-paired matching on the unchanged chronological current graph.

These contractions use the literal analytic transpose.  The geometric
Hilbert Gram is a separate computational test-space form; its inverse
does not assign a physical pole residue, charge or external state.
"""
from __future__ import annotations
import numpy as np


def current_transfer_chunk(left_source, right_source, response, adjoint):
    """Contract one complete row shard, including every saddle coordinate.

    The two independently computed contractions must agree when
    H u=J_R and H^T p=J_L.  No conjugation, inverse, gauge row deletion,
    source Gram division or physical normalization occurs here.
    """
    L,R,u,p=(np.asarray(x,complex) for x in
              (left_source,right_source,response,adjoint))
    if (L.ndim!=3 or R.shape!=L.shape or u.shape!=L.shape or p.shape!=L.shape
            or not all(np.isfinite(x).all() for x in (L,R,u,p))):
        raise ValueError('all original rows and complete common source columns required')
    n,d,c=L.shape
    return dict(source_transfer=L.reshape(n*d,c).T@u.reshape(n*d,c),
                transpose_transfer=p.reshape(n*d,c).T@R.reshape(n*d,c))


def current_test_forms(values, analytic_measure, geometric_measure, body):
    """Keep analytic action forms and the Hilbert Gram distinct.

    values are the owned temporal functions. body acts on the complete
    C6 x real-angular space before the temporal Kronecker product.  The
    resulting order is (temporal test, C6, real-angular).  A computational
    Hilbert Gram is positive only for linearly independent functions on
    the supplied positive-measure domain.
    """
    b,m,mu,H=(np.asarray(x,complex) for x in
              (values,analytic_measure,geometric_measure,body))
    if (b.ndim!=2 or m.shape!=(len(b),) or mu.shape!=m.shape
            or H.ndim!=3 or H.shape[0]!=len(b) or H.shape[1]!=H.shape[2]
            or not all(np.isfinite(x).all() for x in (b,m,mu,H))
            or np.any(mu.imag) or np.any(mu.real<=0)):
        raise ValueError('owned full tests, analytic measure and positive geometric Gram required')
    A=np.einsum('q,qi,qj->ij',m,b,b,optimize=True)
    G=np.einsum('q,qi,qj->ij',mu.real,b.conj(),b,optimize=True)
    D=np.einsum('q,qi,qj,qab->iajb',m,b,b,H,optimize=True)
    d=H.shape[-1];k=b.shape[-1]
    return dict(analytic_test_Gram=np.kron(A,np.eye(d)),
                Hilbert_test_Gram=np.kron(G,np.eye(d)),
                analytic_body_form=D.reshape(k*d,k*d),
                temporal_analytic_Gram=A,temporal_Hilbert_Gram=G,
                physical_pole_or_charge_normalization_assigned=False)


def continued_base_dual_images(body, reflected_body, coefficients, vertices, dual_vertices):
    """Apply a complex base shift with independent differentiation duals.

    The literal analytic dual consumes the SAME coefficient. A separately
    reflected Hilbert base consumes its conjugate. This checks a reached
    equality; it never substitutes the latter for the action dual.
    """
    H,Hs,v,X,Xs=(np.asarray(x,complex) for x in
                 (body,reflected_body,coefficients,vertices,dual_vertices))
    if (H.ndim!=2 or H.shape[0]!=H.shape[1] or Hs.shape!=H.shape
            or v.ndim!=1 or X.shape!=(len(v),)+H.shape or Xs.shape!=X.shape
            or not all(np.isfinite(x).all() for x in (H,Hs,v,X,Xs))):
        raise ValueError('one full represented body and independently fixed source dual required')
    right=H+np.einsum('c,cij->ij',v,X)
    literal=Hs+np.einsum('c,cij->ij',v,Xs)
    reflected=Hs+np.einsum('c,cij->ij',v.conj(),Xs)
    return dict(right_body=right,literal_analytic_dual_body=literal,
                separately_reflected_base_body=reflected,
                literal_minus_Hilbert_dagger=literal-right.conj().T,
                reflected_minus_Hilbert_dagger=reflected-right.conj().T,
                source_coefficients_conjugated_in_analytic_dual=False)
