# Independent audit: retained carrier interior, Poisson and bounded perturbation estimates

Result: the proposed constants and combined criterion are mathematically valid under the L2-bounded, fixed-domain scope below. They are not yet an enclosure of the physical LR contribution.

Use kappa_probe^2=-z=1, distinct from carrier amplitude lambda and Higgs quartic lambda_H. Let

q0[u]=||(partial_tau+W)u||_L2^2+kappa_probe^2||u||_L2^2,

on [0,T], in the canonical proper-time L2 norm, with ||W||_infty<=S. A bounded matrix W is also permitted: A†A defines the positive base form. No bound on W' is needed for these estimates because they are form-level base inequalities.

## Interior inverse

For u in H_0^1(0,T), ||u'||>=pi||u||/T. If ST<3<pi,

q0[u]>=((3/T-S)^2+kappa_probe^2)||u||^2.

Thus the two-end Dirichlet base inverse R0 obeys

d(T)=||R0|| <= T^2/[(3-ST)^2+kappa_probe^2 T^2].

This right-hand side increases with T on ST<3, since its reciprocal is (3/T-S)^2+kappa_probe^2. Evaluation at Tmax is a valid family bound.

## Base Poisson extension

Let E0 b be the q0-harmonic extension with u(0)=0 and u(T)=b. It minimizes q0 on that affine trace class. The linear trial u(tau)=(tau/T)b gives

q0[E0 b] <= [1/T+S+(S^2+kappa_probe^2)T/3]||b||^2.

For any H1 function vanishing at 0 only, ||u'||>=pi||u||/(2T). Therefore, for ST<3/2,

q0[u]>=[(3/(2T)-S)^2+kappa_probe^2]||u||^2.

Combining these and dropping the positive kappa_probe^2 denominator term yields

||E0||^2 <= T[1+ST+(S^2+kappa_probe^2)T^2/3]/(3/2-ST)^2.

This right-hand side is increasing for ST<3/2: the numerator has nonnegative coefficients and the positive denominator decreases. Substitution of Tmax is valid. This is the boundary-to-bulk *L2* norm, not the energy norm.

## Fixed-domain L2-bounded perturbation

Let V be an L2-bounded bulk operator, ||V||<=v. A sesquilinear perturbation qualifies only if it obeys |v[u,w]|<=v||u||_L2||w||_L2 and hence represents an L2-bounded operator. Require the same form domain, trace maps, pairing, and no new boundary action/contact. Hermiticity of V is unnecessary.

For d v<1, the perturbed harmonic extension and response satisfy

E_V=(I+R0 V)^(-1)E0,

DeltaLambda=E0† V(I+R0 V)^(-1)E0.

These are Neumann/Schur identities. The minimization argument was used only for Hermitian-positive q0, not for the full non-Hermitian form.

Writing e2>=||E0||^2,

||DeltaLambda||<=e2 v/(1-d v),

||DeltaLambda-E0† V E0||<=e2 d v^2/(1-d v).

If S0 is the complete retained positive carrier seam and ||S0^(-1)||<=b, then

(d+b e2)v<1

is sufficient both for the perturbed Dirichlet solve and the perturbed seam inverse. It yields the useful combined bound

||(S0+DeltaLambda)^(-1)|| <= b(1-d v)/[1-(d+b e2)v].

This criterion does not require V Hermitian; it proves invertibility rather than positivity of the perturbed seam. A positivity conclusion needs extra assumptions.

## Units and trace normalization

With proper time measured in length units, S and kappa_probe have units length^-1; d has units length^2; e2 and b have units length; v has units length^-2. Hence (d+b e2)v is dimensionless. The reported threshold near 5.2017e89 has units inverse proper-time squared in the retained model normalization. It is not a fermion mass threshold in GeV and not a bound on the muon anomaly.

The trace norm must be the same canonical norm used in the retained carrier DtN and seam bound. If a nonunitary trace-density/source transformation is introduced, its norm factors must be included in e2 and the response/seam comparison.

## Physical scope caveats that are mathematically necessary

1. A bound on a first-order LR mass matrix cannot be substituted for v. Squaring D_car+E_LR generally produces D_car†E_LR+E_LR†D_car+E_LR†E_LR; the cross terms are typically first-order differential or form-relative perturbations, not L2-bounded multiplication operators. They require their own form/energy estimate or a verified cancellation/representation producing L2-bounded V.
2. The literal additive LR action has to be bound to this positive carrier quadratic realization before this numerical threshold applies. The source receipt explicitly leaves that embedding unproved.
3. Domain changes, moving trace maps and boundary-supported contacts are not contained in this bulk V norm. Their derived pullback/contact operators must be accounted for separately, or included in a proved transformed same-domain operator with the correct norm.
4. This establishes a new conditional numerical tolerance for a supplied perturbation. It does not enclose the unknown incoming H, its variation, the physical LR response, the complete CAR kernel, or moment rank.

The proposed leading values d approximately 3.8449e-91, e2 approximately 8.2676e-46, and threshold approximately 5.2017e89 have the expected scaling: d~Tmax^2/9, e2~4Tmax/9, b~Tmax, so d+b e2~5Tmax^2/9.
