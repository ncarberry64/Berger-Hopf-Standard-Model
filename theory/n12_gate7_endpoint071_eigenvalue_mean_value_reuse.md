# Endpoint 71: eigenvalue refinement from frozen primal evidence

The endpoint-71 primal pair and selected normalized eigenbranch are already
independently reproduced on the original tube. No point solve is repeated here.
The new scalar derivative calculation uses the saved 75 weighted directions:
one longitudinal direction scaled by rL and 74 frame directions scaled by rT.
The state coordinates are unweighted before taking action derivatives; the
descriptor has no direct dependence in the action Hessian.

For the normalized symmetric eigenpair, differentiation of H psi = lambda psi
gives D lambda[v] = D3S[(0,psi),(0,psi),v]. The auxiliary bordered-solve coordinate
is not used as an eigenvalue derivative. Existing implicit invertibility and
orientation certify the same smooth family along every radial tube segment.

Let s_0,...,s_74 enclose these uniform scalar derivatives on the original domain.
The mean-value support is

    B = |s_0| + sqrt(sum_{k=1}^{74} |s_k|^2),

with each absolute value and square root evaluated outwardly in Arb. The
verified point eigenvalue plus [-B,B] therefore encloses the same selected
eigenvalue throughout the tube. All radii are already included in the saved
directions. This calculation does not shrink the physical domain.

The resulting eigenvalue radius is approximately 2.0103345867612657e-15,
compared with the previous 3.853653327947852e-15. Both the numerical archive and
record reproduced byte-for-byte in a fresh process. The paired files are under
`tmp/gate7_resume_20260923/exact_hessian_snapshot/tmp/endpoint071_eigenvalue_pair_run3`.

This is a reusable eigenvalue lemma. It does not certify a mixed Hessian,
neighborhood remainder, full-history contraction, or Gate-7 closure.
