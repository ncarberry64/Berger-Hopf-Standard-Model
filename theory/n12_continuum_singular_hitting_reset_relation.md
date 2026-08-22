# N12 continuum singular hitting and reset relation

## Scope

This note uses only the retained BHSM action, the certified N12 complete-child
root ball, the existing gauge-fixed Euler--Dirac flow, and the certified
inverse-square continuum tail. It adds no equation, gate, selector, scale, or
identification. Physical time remains oriented and forward. The formal sign
reflection is not quotiented.

## One-sided singular hitting law

Let `D(Y)` be the retained reduced Euler--Dirac block, let its simple ordered
eigenpair be

    D psi = lambda psi,       <psi,psi> = 1,

and write `P=psi psi^T`, `Q=I-P`. On the regular side `lambda != 0`, the
existing flow equation is

    D zdot = b_ED.

With `b_psi=<psi,b_ED>` and the hard reduced inverse
`S=Q(D-lambda)^{-1}Q`, its exact pole decomposition is

    zdot = (b_psi/lambda) psi + S Q b_ED.

The eigenvalue derivative along the same retained flow therefore has the
form

    lambda_dot = c_psi b_psi/lambda + R(Y),

where

    c_psi = D^3 L[(0,psi),(0,psi),(0,psi)]

and `R` contains only the configuration derivative and the hard-complement
term. Consequently, for `u=lambda^2`,

    u_dot = 2 c_psi b_psi + 2 lambda R(Y).

The already-certified event ball has nonzero `b_psi`, nonzero `c_psi`, and a
simple hard complement. Continuity then gives a one-sided neighborhood in
which the sign of `u_dot` is the sign of `c_psi b_psi`. At the represented
event this product is negative. Every forward solution which enters that
positive-`lambda` terminal chart therefore reaches `lambda=0` in finite time,
with the square-root boundary law

    lambda(t)^2 = -2(c_psi b_psi)_E (tau-t) + o(tau-t).

This is a local terminal-hitting theorem. It does not prove that the presently
certified child history enters the terminal chart.

The formally reflected Cauchy state has the opposite product and a
forward-emergent boundary role. It lies in the same single forward clock
domain when re-expressed as initial data; it is neither backward physical time
nor an established gauge copy.

## Continuum transfer

The continuum complete-child certificate encloses its correction to the N12
anchor by `r_infinity`. Existing action bounds give conservative Lipschitz
controls

    Lip(b_psi) <= C_P C_b + C_Db,
    Lip(c_psi) <= C_D4 + 3 C_D3 C_P.

Here `C_P` is the existing ordered eigenprojector derivative bound and the
other constants are the existing Euler--Dirac/action derivative bounds. The
products of these bounds with `r_infinity` are far below the already-certified
finite N12 lower bounds for `|b_psi|`, `|c_psi|`, and the hard eigenvalue gap.
Thus their nonzero signs and the terminal/emergent classification transfer to
the certified continuum child graph.

## Event-to-child reset is a relation

At the stored N12 state, write the unchanged paired Jacobian in event/child
columns and event/coupled rows. Direct rank evaluation gives:

    event rows versus event variables:       rank 26,
    event rows versus child variables:       exactly zero,
    coupled rows versus fixed-event child:   rank 31 of 31,
    smallest fixed-event child singular:     0.01057621916679917.

Therefore the implicit-function theorem makes the fixed-event complete-child
solution set a regular local fiber of dimension

    98 - 31 = 67,

or 66 after the already-existing one-dimensional whole-system time quotient.
The certified numerical normal section chooses a reproducible representative
of this fiber, but that chart choice is not an action-owned physical selector.
The correct object is consequently a local correspondence
`mathfrak C(E)`, not an intrinsically single-valued physical map `C(E)`.

The full-action nonlinear majorant times `r_infinity` is negligible relative
to the fixed-event child singular gap. Together with the existing continuum
normal graph theorem and summable tail, this transfers the regular local
correspondence to the certified continuum setting. It does not collapse its
physical tangent fiber.

## Closed and open statements

Closed:

- the action-owned one-sided singular hitting law;
- its terminal/emergent boundary sign at the represented and reflected roles;
- continuum preservation of the nonzero hitting factors and hard gap;
- regularity of the continuum event-to-complete-child reset relation;
- non-uniqueness of the reset without an additional action-owned selection
  mechanism.

Still open:

    PROVE_THAT_AT_LEAST_ONE_EXISTING_FORWARD_COMPLETE_CHILD_HISTORY_REACHES_
    THE_CERTIFIED_TERMINAL_SINGULAR_EVENT_CHART_BEFORE_ANY_EXISTING_PHYSICAL_
    DOMAIN_EXIT_OR_PROVE_THAT_NO_SUCH_HISTORY_DOES.

Only after such reachability is established can an action-selected fixed or
periodic orbit of the hybrid flow/relation be sought. No current child return,
parent subtraction, mass, observable, or prediction is promoted here.
