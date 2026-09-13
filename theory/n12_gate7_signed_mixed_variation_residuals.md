# Signed mixed bordered-system residuals

The physical Hessian diagnostic uses the unchanged selected eigenpair
(p,lambda) and physical response (h,b), with

    K = [[H-lambda I, p], [p^T, 0]].

For a fixed variation center z0, directly enclose R(rhs-K z0) by contracting
the original action derivatives with the rows of the fixed preconditioner R.
Forming interval rhs first and then multiplying by R can lose cancellations
between its coordinates. The following identities change the evaluation
order; they do not alter any equation or remove uncertain operands.

For row k, let c_k be the raw-state embedding of R[k,:n], with zeros in the
configuration block. Denote R[k,n] by beta_k. Write S_j for the symmetric jth
derivative of the original action, evaluated on the full physical domain.
Let u,v be fixed raw input directions, and p_u,p_v be the already enclosed
first selected-line variations. The graph's mixed eigenvalue expression is

    lambda_uv = S4[p,p,u,v] + S3[p_v,p,u] + S3[p_u,p,v],

where reduced vectors in action slots carry their raw lower-block embedding.
The preconditioned mixed eigenline right-hand side is

    -S4[c_k,p,u,v] - S3[c_k,p_v,u] - S3[c_k,p_u,v]
    +(R_k p) lambda_uv + lambda_u R_k p_v + lambda_v R_k p_u
    -beta_k (p_u.p_v).

The final term is the differentiated eigenline-normalization equation; it
must not be dropped. If z0=(a0,d0), subtract K z0 in the same signed form:

    -S2[c_k,a0] + lambda R_k a0 - (R_k p)d0 - beta_k(p.a0).

For the physical response, the existing `response_legs` helper supplies the
raw weighted gradient leg g_k, configuration-Hessian leg a_k, configuration
vector d and its first variations d_u,d_v. These contain the original state,
configuration and reduced metric weights, including every inverse weight.
The preconditioned mixed response right-hand side is

    S3[g_k,u,v] - S4[a_k,d,u,v]
    -S3[a_k,d_v,u] - S3[a_k,d_u,v]
    -S4[c_k,h,u,v] + lambda_uv R_k h - b R_k p_uv
    -S3[c_k,h_v,u] + lambda_u R_k h_v - b_v R_k p_u
    -S3[c_k,h_u,v] + lambda_v R_k h_u - b_u R_k p_v
    -beta_k(h.p_uv + p_u.h_v + p_v.h_u).

Subtract the same signed K z0 expression. This is precisely the mixed
derivative of K(h,b)=(physical source,0): the source_uv, K_uv, K_u, K_v,
and differentiated orthogonality terms all remain present. The numerical
consumer still uses the existing paired inverse-variation bounds, fixed
centers and complete original scalar contractions. It flips the last
coordinate when changing between K and the paired Jacobian convention,
as in the previous centered first-variation consumer.

Independent tests assemble dense H, H_u, H_v and H_uv matrices for an action
with two exponential modes, form both complete bordered right-hand sides,
subtract K z0, and only then multiply by R. They cover nonzero centers,
bottom-row terms, nonsymmetric fixed R, unequal metric weights, and two
transverse columns. Exact evaluations agree; signed interval evaluations
contain the dense evaluations at both endpoints of an uncertain action
coefficient. Those coefficient perturbations belong to the synthetic test
family and do not change any BHSM parameter.

The physical numerical run remains a one-direction diagnostic unless
independent reproduction and full required domain/direction coverage are
established separately. Source binding, point containment and agreement
tests cannot establish full-path contraction or the physical quotient.
