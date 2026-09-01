# N=12 finite-stop bordered hard-inverse theorem

Status: `ALL_3008_STOP_PATH_BORDERED_HARD_INVERSES_CERTIFIED`.

Let `H` be the retained symmetric reduced descriptor Hessian, `lambda` its
certified selected eigenvalue, and `psi` the corresponding unit vector.  The
bordered operator is

`K=[[H-lambda I,psi],[psi^T,0]]`.

In the instantaneous orthonormal eigenbasis its selected/border block is
`[[0,1],[1,0]]`, while every hard coordinate is multiplication by
`lambda_j-lambda`.  Hence its singular values are exactly

`{1,1,|lambda_j-lambda|:j not equal to 24}`,

and

`||K^-1||_2=max(1,1/gap_24,hard)`.

The complete boundary-cluster theorem supplies the hard gap on every one of
the 3008 correlated stop-path balls.  The selected-projector graph supplies a
single coherent center chart.  If its graph radius is `k<1`, the proof-only
chart condition is bounded by `(1+k)/(1-k)`.

The minimum gap is `1.7274638520643627e-7`.  The maximum instantaneous
inverse norm is `5788833.143483581`, the maximum chart factor is
`1.028682589928863`, and the maximum charted inverse norm is
`5944620.595773861`, owned by seam 45, subspan 63.  This is not an
inversion of the ill-conditioned kinetic/Dirac block: it is the spectral
formula for the already-quotiented bordered descriptor operator.

The inverse tube alone does not create or zero a source.  The next object is
the action-owned internal bordered right-hand side assembled from the closed
BHSM seam.  Only after that insertion is the bordered hard response itself
closed.
