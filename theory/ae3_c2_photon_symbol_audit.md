# AE3 photon diagnostic: static quotient, spectral derivative, and Maxwell shell

## Result and scope

The retained lowest-mode number `0.590609601652908` is reproduced. It is
`s*(-partial_q2 N)/N(s,0)`, where `s=n^2` and `q2=(omega R4)^2`. Its spatial
denominator is a static quotient, not `partial_s N`. It is a necessary test
for identifying the entire frozen trace with an exact local Maxwell kernel
`Z*(s-q2)`, but is not a universal Lorentz-symmetry diagnostic for nonlocal
operators.

The actual derivative ratio at `n=2` is `0.9089329912282743`, also below one.
This does not repair the retained local-Maxwell identification. A more direct
test is now available: the isolated frozen trace is strictly positive on the
reference Maxwell shell `q2=s`, where `Z*(s-q2)` would vanish. The numerical
witness is `N(4,4)=0.42828102464319007`.

These are statements about the specified frozen transverse boundary problem.
They do not establish a global violation of local Lorentz symmetry, the absence
of photons in every BHSM extension, or a completed physical propagator.

## The same radial action and two distinct derivatives

Write `p=W sin(rho)`, `m=W/sin(rho)`, with the retained positive interior
weight `W=1-4 sigma^2`. The wall is `b=pi/2`, `u(b)=1`, and the regular
endpoint condition is unchanged. The stationary form is

```text
N(s,q2) = integral_0^b [p u'^2 + (s m-q2 p) u^2] d rho.
```

The physical coexact levels have `s=n^2`, `n>=2`. Extending `s` to positive
real values in this same differential expression is a diagnostic analytic
family, not an additional physical spectrum. At `q2=0`, stationarity gives

```text
T = -partial_q2 N = integral p u^2,
M =  partial_s N  = integral m u^2,
G = integral p u'^2,
N(s,0) = G+s M.
```

At the singular endpoint `W~8 rho^3/(3 pi)` and the regular solution is
`u~rho^alpha`, `alpha=(-3+sqrt(9+4s))/2>0`. Integration-by-parts terms decay
as `rho^(2 alpha+3)`; differentiated terms with an additional logarithm also
vanish. The regular form has a common finite-energy variational description.

Consequently

```text
N(s,0)/s = M+G/s > M,
0 < s T/N(s,0) < T/M < 1.
```

The last strict inequality follows from `m-p=W cos(rho)^2/sin(rho)>0` in
the interior and a nonzero regular extension. It uses the common retained
metric and domain, without changing a cone or fitting a coefficient.

The unequal derivatives rule out the analytic frozen response being a function
only of `s-q2`. This conclusion can also be checked at two actual integer
coexact levels: `N(4,0)=1.679557832021268`, while
`N(16,12)=1.8927853135591917`, despite the same `s-q2=4`.
Along a constant `s-q2`, the derivative is
`partial_s N+partial_q2 N=integral (m-p)u^2>0`.
This is a finite-background response statement, not a claim that general
covariant curved-background kernels must depend only on that single combination.

## Direct reference-shell obstruction

On `q2=s`, the same stationary energy becomes

```text
N(s,s) = integral [p u'^2 + s (m-p) u^2] > 0.
```

Both terms are nonnegative, and the normalized nonzero trace makes the
integral strictly positive. Thus the isolated frozen DtN kernel has no zero
on the massless coexact Maxwell shell of the reference wall metric. Its
inverse cannot have a pole on that shell. The reflected two-sided assembly
doubles this positive kernel; it does not create a zero.

This conclusion is about the isolated frozen trace. Time-dependent history,
other action blocks, admissible coupling to additional boundary degrees of
freedom, global state selection, and the quantum propagator are separate
questions. The present result supplies none of those additional operands.

## Why the original ratio is not a universal symmetry test

The flat half-space decaying extension has symbol

```text
N_flat(s,q2)=sqrt(s-q2),  s>q2.
s*(-partial_q2 N_flat)/N_flat(s,0)=1/2,
(-partial_q2 N_flat)/(partial_s N_flat)=1.
```

It depends only on the tangential Lorentzian quadratic form on this branch,
yet fails the proposed value-ratio-equals-one test. It is nonlocal and of order
one, rather than an exact local second-order Maxwell kernel. This analytic
control is not substituted into BHSM and is not a constructed causal quantum
photon propagator.

The square-root DtN relation is standard; see Kwaśnicki and Mucha,
[Extension technique for complete Bernstein functions of the Laplace operator](https://arxiv.org/abs/1707.02475).
For the smooth-boundary principal symbol in the Riemannian setting see
Michael Taylor, [The Dirichlet-to-Neumann Map](https://mtaylor.web.unc.edu/wp-content/uploads/sites/16915/2018/04/dton.pdf), section 2.2.
Those references do not independently validate the BHSM model.

For the retained transverse equation, freezing the coefficients at the wall
gives the normal principal equation `u''-(s-q2)u=0`. On its decaying spacelike
branch the formal boundary principal symbol is therefore `sqrt(s-q2)`.
The boundary weight is positive and smooth; the remote endpoint and radial
variation affect lower-order/full-response data. This local identification
does not prove a uniform asymptotic expansion at the null/glancing set
`s=q2`, or a global Lorentzian Green function. In particular, it cannot be
used to override the direct finite-mode positive-energy shell test above.

Numerical static witnesses illustrate the distinction:

| Coexact level | Complete-mode ratio | Derivative ratio | N(n^2,0)/n |
|---|---:|---:|---:|
| 2 | 0.590609602 | 0.908932991 | 0.839778916 |
| 4 | 0.530807173 | 0.970470267 | 0.952358220 |
| 8 | 0.508468081 | 0.992255742 | 0.987527072 |
| 16 | 0.502171086 | 0.998050146 | 0.996845751 |

These samples support the stated principal-symbol interpretation; sampling
alone is not an asymptotic proof or evidence of a physical photon pole.

## Numerical verification and retained cutoff terms

The audit uses a separate Riccati/sensitivity solver, `y=u'/u`, to avoid
amplitude underflow. With `a=cot(rho)+W'/W` and `c=1/sin(rho)^2`,

```text
y' = -a y+s c-q2-y^2,
(partial_s y)' = c-(a+2y) partial_s y,
(partial_q2 y)' = -1-(a+2y) partial_q2 y.
```

At the numerical cutoff epsilon, the leading Frobenius Robin condition is
`y=alpha/epsilon`, with `partial_s y=1/(epsilon sqrt(9+4s))` and
`partial_q2 y=0`. The finite-cutoff form includes
`B=p(epsilon)*alpha*u(epsilon)^2/epsilon`. Its spatial envelope includes
`B_s=p(epsilon)*u(epsilon)^2/(epsilon sqrt(9+4s))`.
Thus the implemented checks are `N=G+s M+B`, `N_s=M+B_s`, and `-N_q2=T`.
No small nonzero boundary term is discarded.

The same weight is evaluated as `4 delta(1-delta)`, where
`delta=(2 rho-sin(2 rho))/(2 pi)`. A short sine series near the pole prevents
subtractive cancellation; high-precision evaluation independently checks it.
This changes numerical evaluation only, not the analytic profile or action.

The report cross-checks the retained second-order solver, independent energy
integrals, centered parameter differences, and a halved cutoff. It is a
binary64 numerical audit, not an outward enclosure of the singular-limit
problem. Its repeated JSON materializations must be byte-identical.

```sh
python scripts/materialize_ae3_c2_photon_symbol_audit.py
python -m pytest -q tests/test_ae3_c2_photon_symbol_audit.py
```

Artifact: `artifacts/action_extension/BHSM_AE3_C2_PHOTON_SYMBOL_AUDIT.json`.
`FULL_BHSM_COMPLETE = FALSE`; no physical photon is promoted.
