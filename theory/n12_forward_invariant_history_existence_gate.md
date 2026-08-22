# Forward invariant-history existence gate

Status: **the conditional first-return map is derived, but its forward domain
has not been proved nonempty; no invariant child history is yet selected**.

This audit keeps BHSM physical time oriented and forward.  Formal reversal is
not a quotient and cannot manufacture a positive-time return.

## 1. Exact forward return domain

Let \(\Sigma\) be the existing simple ordered-event section and
\(\mathcal C_\infty\) the certified local continuum event-to-child
reconstruction.  For \(E\in\Sigma\), put

\[
f_E(t)=e_{\rm ord}\!\left(\varphi_t(\mathcal C_\infty(E))\right),
\]

where \(\varphi_t\) is the retained forward Euler--Dirac flow.  The domain of
the already-derived first-return map is exactly the set of \(E\) for which:

1. \(\mathcal C_\infty(E)\) is defined in the certified child chart;
2. the maximal forward solution remains in the existing eta, metric, lapse,
   inertia, gauge, trace, and Dirac domain through some finite \(\tau>0\);
3. \(f_E(t)\ne0\) for \(0<t<\tau\) and \(f_E(\tau)=0\);
4. the returned event is simple and transverse, \(f_E'(\tau)\ne0\);
5. \(\mathcal C_\infty\) is defined at the returned event.

Only then is

\[
\mathcal P(E)=\mathcal C_\infty\!\left(\varphi_\tau(
\mathcal C_\infty(E))\right)
\]

defined on the existing gauge and whole-system time-translation quotient.
No formal-reversal quotient is taken.

## 2. Forward landing-chirality lemma

There is one exact chirality statement that does not require a new sign gate.
If \(f_E(0)\ne0\), a finite first zero \(\tau\) exists, and that zero is
transverse, then continuity and the definition of first return imply

\[
\operatorname{sgn} f_E'(\tau)=-\operatorname{sgn} f_E(0).
\]

Indeed, \(f_E\) keeps its initial sign on \([0,\tau)\); at a differentiable
transverse first zero it must cross toward the opposite side.  Thus the
forward landing chirality is selected *conditionally by a proved first
return and the action-evaluated initial child side*.  It is not an acceptance
condition.

The stored N12 child has \(f_E(0)>0\) at 96, 192, and 384 point quadrature.
The existing persistence endpoint remains positive and moves farther from
zero.  These are finite-anchor facts.  The audited continuum artifacts do not
separately enclose the sign of \(e_{\rm ord}\) evaluated on the continuum
child rather than on the event state, so this note does not promote the N12
sign to an independent continuum theorem.

Formal reversal changes the sign of \(G=De_{\rm ord}V\), but the identity
\(\mathcal R\varphi_t=\varphi_{-t}\mathcal R\) relates positive time to
negative time.  It therefore does not turn an unproved forward return into a
second forward return.  Event-to-child graph equivariance and forward-return
equivariance are different claims.

## 3. Invariant-history criterion

An action-selected fixed, periodic, or relative-periodic child history would
be a periodic point of \(\mathcal P\), modulo only existing gauge and
whole-system time translation.  Before any fixed-point or periodic-point
argument can be invoked, the following are required:

- a nonempty forward return domain;
- return into the certified continuum child chart;
- a controlled domain on which the relevant iterate of \(\mathcal P\) is
  continuous;
- a compact trapping set, a nonzero return degree/index, or another
  action-owned existence mechanism.

The repository currently supplies none of these global ingredients.  It
supplies a local continuum flow, a maximal continuation-or-domain-exit
alternative, and conditional differentiability of \(\mathcal P\).  The one
stored persistence history records no return.  The constraint energy is zero,
the unreduced energy is noncoercive, the child boundary Hamiltonian is absent,
and no compact invariant energy shell or stable reference cycle is available.
Consequently recurrence, Schauder/Lefschetz degree, and a variational periodic
orbit theorem cannot presently be invoked.

## 4. Localized retained-action failure

The earliest failure is not the absence of a better nonlinear solver.  It is

`NONEMPTY_ADMISSIBLE_FORWARD_FIRST_RETURN_DOMAIN_NOT_ESTABLISHED`.

This is not a proof that the return domain is empty or that no invariant child
history exists.  It is the first missing hypothesis in the exact existing
state-selection construction.  The next mathematical dependency is:

`PROVE_THAT_AT_LEAST_ONE_EXISTING_COMPLETE_EVENT_HAS_A_FINITE_SIMPLE_TRANSVERSE_FIRST_FORWARD_RETURN_WHOSE_HISTORY_REMAINS_IN_THE_EXISTING_CONTINUUM_CHILD_DOMAIN_AND_LANDS_INSIDE_THE_CERTIFIED_EVENT_TO_CHILD_CHART_OR_PROVE_THAT_EVERY_SUCH_FORWARD_HISTORY_EXITS_OR_NEVER_RETURNS`.

Only after a nonempty return domain is proved may a periodic-point mechanism
be established.  Numerical trajectory sampling, formal reversal, a new event
sign, or a fabricated parent section cannot substitute for this theorem.
