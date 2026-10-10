"""Established NGE bilinear super-heat operator from action Hessian blocks.

Reference: Neufeld, Gasser, Ecker, hep-ph/9806436, equations 15--19.
This is a standard QFT computational representation, not a new BHSM action.
Physical BHSM kinetic blocks, domains, and matching are calling operands.
"""
from __future__ import annotations

import numpy as np


def laplace_source_jets(*, A, A_a, A_pair, A_a_pair,
                        B, B_a, B_tilde, B_tilde_a,
                        gamma_bar, gamma_bar_a, gamma, gamma_a,
                        auxiliary_mass: float):
    """Seven jets of Delta through a*bar_s*s, in graded_heat's convention.

    A=bosonic Hessian; B=Dirac Hessian; gamma_bar/gamma are coefficients
    of bar_s/s in the mixed action vertices. All contacts are explicit.
    B_tilde is the prescribed conjugate/squaring factor, gamma5 B gamma5
    in the vector-like NGE construction. No inverse or square root of an
    arbitrary bosonic Hessian is chosen. Source dependence in the fermion
    pair sector beyond a bilinear bare fermion action is outside this API.
    """
    values = [np.asarray(x,complex) for x in
              (A,A_a,A_pair,A_a_pair,B,B_a,B_tilde,B_tilde_a,
               gamma_bar,gamma_bar_a,gamma,gamma_a)]
    A,Aa,AR,AaR,B,Ba,Bt,Bta,gb,gba,g,ga = values
    if A.ndim != 2 or A.shape[0] != A.shape[1] or B.ndim != 2 or B.shape[0] != B.shape[1]:
        raise ValueError("Square bosonic and Dirac Hessian blocks required")
    nb,nf = len(A),len(B)
    expected = ((nb,nb),)*4+((nf,nf),)*4+((nb,nf),)*2+((nf,nb),)*2
    if any(x.shape != shape or not np.isfinite(x).all() for x,shape in zip(values,expected)):
        raise ValueError("Compatible finite action blocks and jets required")
    mu = float(auxiliary_mass)
    if not np.isfinite(mu) or mu <= 0:
        raise ValueError("Positive auxiliary unit required; it cancels by similarity")
    size = nb+nf
    grade = np.diag(np.r_[np.ones(nb),-np.ones(nf)])
    ordinary = {mask:np.zeros((size,size),complex) for mask in range(8)}
    ordinary[0][:nb,:nb] = A
    ordinary[0][nb:,nb:] = B@Bt
    ordinary[1][:nb,:nb] = Aa
    ordinary[1][nb:,nb:] = Ba@Bt+B@Bta
    ordinary[2][:nb,nb:] = np.sqrt(2/mu)*gb@Bt
    ordinary[4][nb:,:nb] = np.sqrt(2*mu)*g
    ordinary[6][:nb,:nb] = AR
    ordinary[3][:nb,nb:] = np.sqrt(2/mu)*(gba@Bt+gb@Bta)
    ordinary[5][nb:,:nb] = np.sqrt(2*mu)*ga
    ordinary[7][:nb,:nb] = AaR
    # Standard supermatrix entries multiply using ordinary Grassmann-entry
    # rules. The graded-tensor API writes parameters left of graded matrix
    # coefficients. The exact isomorphism is P_I = ordinary_I G**parity_I.
    jets = {mask:value@grade if mask in (2,3,4,5) else value
            for mask,value in ordinary.items()}
    return jets,grade
