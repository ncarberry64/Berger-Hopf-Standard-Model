# Interval 14: shared right-entry remainder

This continuation concerns only the zero-based right entry `DR[73,14]`.
It does not reopen interval 13. No result in this note closes Gate 7.

## Exact dependency graph

Let `u = E_right e_14`, `P = R_frozen^{-1} T`, and let `h` be the
retained interval-14 step. With the original physical rate `F`, define

```
A(theta) = DF(z_15(theta)) u
w(theta) = u/2 - h A(theta)/8
B(theta) = DF(m_14(theta)) w(theta)
a(theta) = e_73^T P (-u + h A(theta)/6 + 2h B(theta)/3).
```

The identity entry in `I - P Dr_right E_right` vanishes at `(73,14)`.
The same `A(theta)` occurs directly and inside `w(theta)`. In particular,
expansion around an anchor contains
`-h^2 e_73^T P (DF(m)-DF(m_0))(A-A_0)/12`; dropping this term is invalid.

The endpoint has 75 original parameters: one longitudinal interval and one
74-dimensional Euclidean ball. The midpoint has the original 249 parameters:
two longitudinal intervals, two 74-dimensional Euclidean balls, and 99
retained rate-remainder intervals. Endpoint parameter 0 maps to midpoint
parameter 1; endpoint parameters 1 through 74 map to midpoint parameters
76 through 149. The remaining midpoint parameters are not set to zero.

## Implicit solves and normalization

Write `H` for the reduced action Hessian, `psi` for its selected normalized
eigenvector, `lambda` for the eigenvalue, and `(k,b)` for the response. Their
equations are

```
G_e = ((H-lambda I) psi, (psi^T psi-1)/2) = 0
G_k = ((H-lambda I) k + b psi - f, psi^T k) = 0.
```

For a direction `u`, including a direction that depends on common state
parameters, use `lambda_u = psi^T H_u psi` and

```
G_eu = ((H-lambda I) psi_u + gamma_u psi
        + (H_u-lambda_u I) psi, psi^T psi_u) = 0
G_ku = ((H-lambda I) k_u + b_u psi
        + (H_u-lambda_u I) k + b psi_u - f_u,
        psi^T k_u + psi_u^T k) = 0.
```

Here `gamma_u` is the auxiliary bordered-solve variable, not `lambda_u`.
Differentiating an implicit equation `G(theta,y(theta))=0` gives

```
y_i  = -G_y^{-1} G_i
y_ij = -G_y^{-1}(G_ij + G_iy y_j + G_jy y_i + G_yy[y_i,y_j]).
```

The computational residual method below bounds the resulting Taylor error
without constructing the entire high-order action tensor. It must not be
reported as a separately evaluated pointwise Hessian tensor enclosure.

For the retained rate numerator `N` and descriptor numerator `delta`,
normalization is differentiated as

```
DF u = (N_u, delta_u)/||N||
       - (N, delta) (N^T N_u)/||N||^3.
```

Both appearances of `N` and the common parameters in every numerator are
retained. The original-domain enclosure must prove `||N||^2 > 0` before
reciprocal or logarithm evaluation.

## Original-domain residual inclusion

A scalar model is `c + l(theta) + [-r,r]`, with common affine parameters
and a rigorous nonlinear tail. Primitive unary tails use
`|f'(c)| r + sup_I |f''| (support(l)+r)^2/2`, where `I` contains the
entire modeled argument on the original domain. Products include the
quadratic affine product and every product involving an existing tail.

Let `yhat(theta)` be an exact affine predictor. For the nonlinear eigenpair
solve, both `yhat(theta)` and the previously enclosed actual solution must
lie in the original convex eigenpair box. The segment mean-value matrix
then has the retained weighted defect bound. With fixed preconditioner
`R`, weights `d_i > 0`, and row bounds `V_i`, put

```
q = max_i V_i/d_i < 1
e_i = sup |[R G(theta,yhat(theta))]_i|
t = max_i(e_i/d_i)/(1-q)
|y_i-yhat_i| <= min(e_i+V_i t, d_i t).
```

The state coefficients are combined before computing `e_i`. Using the
anchor-only defect in place of the original-domain defect is invalid.
For the response and directional solves the operator is linear in the
unknown at the actual eigenpair. Its bordered matrix differs from the
eigenpair Jacobian by a sign in the last column. Reflecting that unknown
leaves the absolute weighted error bound unchanged.

## Final comparison and budget discipline

The candidate assembled entry must be compared with the independently
reproduced point anchor and half-Hessian jet, not just with its own
Taylor center. The comparison includes the midpoint anchor displacement,
coefficient uncertainty, and all 99 midpoint remainder parameters.

If `E` is the resulting outward upper bound for `sup_D |e_a|`, the first
test is the strict comparison `E < 0.000394150`. The frozen transverse
transport then bounds the unbooked contribution by

```
c_T (E + TT_first_jet_support),
```

where `c_T` is the already reproduced entry sensitivity. The existing
LL/LT contribution is not charged again. Independent reproduction of the
complete enclosure and transport is required before any ledger debit.

Process parallelism is permitted only between separate scalar action
contractions. It preserves each contraction's operation order, parent
action, precision, common parameters, and original domain. A worker result
must use the active producer binding; supplementary receipts identify the
execution backend. Parallel execution is not independent reproduction.
