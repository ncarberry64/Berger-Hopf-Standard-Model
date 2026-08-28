# N=12 correlated defect--Krawczyk first-hit theorem

Status: `IDENTITY_DERIVED; NUMERICAL_RADII_AND_INTERVAL_REMAINDER_OPEN`.

## Retained graph and defect sign

Let `X` denote the 73-dimensional action-constraint tangent quotient of the
regular child manifold and let

`f(y)=G(y,lambda(y))/||G(y,lambda(y))||`

be the retained denominator-free forward action-arclength field on the
selected descriptor graph.  No full Euler--Dirac inverse is formed.  For a
piecewise polynomial center `y_hat` define

`d=y_hat'-f(y_hat)`.

If `y=y_hat+e` is an exact history, then

`e'=J e-d+N(e)`,

where `J=Df(y_hat)` and

`N(e)=f(y_hat+e)-f(y_hat)-J e`.

The Green source is therefore **minus** the stored defect.  Transporting
`+d` reverses the signed correction and is not the shadow equation.

## Correlated Green operator

Let `U(t,s)` solve the physical quotient variational equation

`partial_t U(t,s)=J_X(t)U(t,s)`,  `U(s,s)=I_X`.

The initial reset member is fixed, so `e(0)=0`.  Variation of constants gives

`e(t)=-integral_0^t U(t,s)d_X(s) ds`
`     +integral_0^t U(t,s)N_X(e(s)) ds`.

This identity must be evaluated as a matrix-correlated composition.  The
product of scalar step norms is not a substitute: the retained center has a
moderate complete physical fundamental norm even though individual ambient
generators are strongly nonnormal.

Choose time-dependent invertible proof frames `P(t)` and the norm

`||e||_P=sup_t ||P(t)e(t)||_2`.

For a numerical inverse/Green approximation `A`, define outward-rounded
bounds

- `Y=||A(-d)||_P`;
- `Z1=||I-A L||_P`, where `L=e'-J_X e` with the fixed reset condition;
- `Z2` so that `||A(N(e)-N(e_tilde))||_P <= Z2*r*||e-e_tilde||_P`
  on the radius-`r` tube.

The radii inequality

`Y+Z1*r+Z2*r^2 < r`

and `Z1+2*Z2*r<1` proves a unique exact retained history in that tube.  The
frames, Green blocks, residual quadrature, and all three constants are proof
coordinates only and introduce no physical selector or scale.

## Descriptor consistency and terminal time

The propagated scalar descriptor center `s_hat` has its own interpolation
defect

`d_s=s_hat'-Dlambda(y_hat)f(y_hat)`.

On the graph, the first terminal correction is

`delta s_T=Dlambda(y_hat(T))e(T)-integral_0^T d_s(t)dt`,

with the same minus-defect convention.  The terminal-time variable is fixed
by the existing stop equation

`0=s_hat(T)+delta s_T+s_dot(T)*delta T+R_T`,

where `s_dot(T)=Dlambda f<0` is already nonzero.  An interval Newton step in
`delta T` is therefore nonsingular and adds no endpoint condition.

## First-hit and domain margins

The Krawczyk inclusion promotes a Gate-7 witness only if the same tube also
proves, before the terminal interval,

1. `s(t)>0`;
2. the selected line stays simple;
3. lapse, radius, duration, and retained coefficient margins stay strict;
4. reset/constraint rank stays constant;
5. no earlier singular-event or physical boundary is crossed.

On the final interval, interval Newton must prove one and only one descending
zero of `s`, while `Delta<0` and every other margin remains strict.  The
result is then a finite forward history from the certified reset relation to
the already retained Euler--Dirac stop `Sigma_ED`.  It proves the
existence-only Gate-7 alternative and makes no universal reachability claim.

The center-side part is exact for the selected quarter-action DOP853
polynomial: rational Bernstein replay proves positivity on all 369 complete
preterminal segments and strict monotone descent on the terminal segment
with one bracketed zero.  See
`n12_c2_stop_dense_descriptor_first_hit.md`.  What remains is not another
center search; it is transfer of those inequalities through the same
correlated shadowing radius, allowing the terminal time to move by its
interval-Newton correction.

## Current executable dependency

The selected quarter-step path already supplies certified selected-line
clusters, projector graphs, bordered hard inverses, and complete internal
response tubes on the 8,692-cell adaptive cover.  The remaining executable quantities are the
outward-rounded correlated `Y,Z1,Z2` bounds on the refined center and the
strict transfer of the certified center first hit and other domain margins.
Only after those inequalities close may
the finite endpoint be passed to the compact Calderon/Weyl force, KKT, and
physical-Hessian chain.
