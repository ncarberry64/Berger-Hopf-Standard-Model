# Forward invariant-history existence gate

Status: **the local singular hitting/reset relation is certified, but global
forward reachability remains open; no invariant child history is selected**.

This audit uses the single existing forward clock domain
\(dt>0\), \(N_{\rm boundary}>0\), and
\(d\tau=N_{\rm boundary}dt>0\). Formal reversal is an algebraic/chiral state
pairing inside that domain, not a second temporal orientation or quotient, and
cannot manufacture a positive-time return.

## 1. Exact forward return domain

Let \(\Sigma\) be the existing simple ordered-event section and
\(\mathfrak C_\infty\) the certified regular local continuum event-to-child
relation. For \(E\in\Sigma\) and \(C\in\mathfrak C_\infty(E)\), put

\[
f_{E,C}(t)=e_{\rm ord}\!\left(\varphi_t(C)\right),
\]

where \(\varphi_t\) is the retained forward Euler--Dirac flow.  The domain of
the already-derived first-return map is exactly the set of \(E\) for which:

1. \(C\in\mathfrak C_\infty(E)\) lies in the certified child chart;
2. the maximal regular forward solution remains in the existing eta, metric,
   lapse, inertia, gauge, trace, and invertible-Dirac domain for
   \(0\le t<\tau\);
3. \(f_{E,C}(t)\ne0\) for \(0<t<\tau\) and \(f_{E,C}(\tau)=0\);
4. the one-sided state has a limit \(E'\) in the simple ordered-event locus;
5. the action-owned singular hitting product
   \(c_\psi b_\psi\) is nonzero and the boundary-hitting limit is regular;
6. the regular relation \(\mathfrak C_\infty(E')\) is defined.

Only then is

\[
\mathcal P(E,C)=\{(E',C'):C'\in\mathfrak C_\infty(E')\},\qquad
E'=\lim_{t\uparrow\tau}\varphi_t(C)
\]

defined on the existing gauge and whole-system time-translation quotient.
No formal-reversal quotient is taken.

## 2. Forward singular-hitting orientation

The ordinary derivative \(f_E'(\tau)\) is not available: at the event the
same Dirac block inverted by the Euler--Dirac vector field has kernel
\(\psi\).  On a regular one-sided approach the retained action instead gives

\[
\lim_{t\uparrow\tau}\frac12\frac d{dt}f_E(t)^2
=c_\psi b_\psi,
\quad
c_\psi=D^3L[(0,\psi)^3],
\quad
b_\psi=\langle\psi,b_{\rm ED}\rangle.
\]

The sign of this product labels terminal versus emergent event sides.  Formal
reflection flips it, while the current event-to-child rows impose neither
sign.  This is not an acceptance condition.

The tracked child eigenline is now certified on the complete N12 root ball.
Its center value is \(1.430742563850721\times10^{-9}\), its entire root-ball
shift is at most \(3.377961828824433\times10^{-15}\), and hence the exact N12
root has value at least \(1.430739185888892\times10^{-9}>0\).  Transferring
through the existing continuum action-graph correction and the already
certified complete compact observation coefficient uses

\[
|De_{\rm ord}(Y)[h]|
=|\langle\psi,DH(Y)[h]\psi\rangle|
\le C_{\rm compact}\|h\|_G
\]

on the existing source-restricted action ball and changes the value by less
than \(8.61\times10^{-73}\).  Thus the continuum child independently satisfies
\(f_E(0)>0\).  The 96, 192, and 384 point evaluations are retained only as
cross-quadrature diagnostics, not as the analytic bound.

The positive initial child side and the event-free first local interval remain
valid.  They do not determine the sign of a future singular hit or establish
that the return domain is nonempty.

The existing local continuum-flow certificate also excludes an event zero on
its entire first interval.  The finite-core third-variation bound and certified
action path give

\[
\Delta e_{\rm core}
\le 8.180992616262165\times10^6
   (3.814697264862058\times10^{-17})
<3.121\times10^{-10}.
\]

The two-endpoint Galerkin/projector correction is below
\(2.79\times10^{-85}\).  Therefore

\[
e_{\rm ord}(Y(t))
\ge 1.118659084317772\times10^{-9}>0
\]

through the certified coordinate duration
\(6.019140402936717\times10^{-32}\).  Any first forward return must occur
after exit from this first action ball.  This is an analytic enclosure of the
already-certified local flow, not a new trajectory sample or acceptance gate.

Formal reversal changes the sign of \(c_\psi b_\psi\), but the identity
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
- a regular one-sided singular hit and return into the certified continuum
  child chart;
- a controlled domain on which the reset composition \(\mathcal P\) is
  continuous;
- a compact trapping set, a nonzero return degree/index, or another
  action-owned existence mechanism.

The repository now supplies the local hitting theorem and regular reset
relation, but none of the remaining global ingredients. It supplies an
event-free first local continuum interval and a maximal
continuation-or-domain-exit alternative. The one stored
persistence history records no return.  The constraint energy is zero,
the unreduced energy is noncoercive, the child boundary Hamiltonian is absent,
and no compact invariant energy shell or stable reference cycle is available.
Consequently recurrence, Schauder/Lefschetz degree, and a variational periodic
orbit theorem cannot presently be invoked.

## 4. Localized retained-action failure

The earliest failure is not the absence of a better nonlinear solver. It is

`GLOBAL_FORWARD_REACHABILITY_OF_THE_CERTIFIED_TERMINAL_SINGULAR_EVENT_CHART_BEFORE_PHYSICAL_DOMAIN_EXIT_NOT_ESTABLISHED`.

This is not a proof that the return domain is empty or that no invariant child
history exists.  It is the first missing theorem in the exact existing
state-selection construction.  Nonemptiness is downstream.  The next
mathematical dependency is:

`PROVE_THAT_AT_LEAST_ONE_EXISTING_FORWARD_COMPLETE_CHILD_HISTORY_REACHES_THE_CERTIFIED_TERMINAL_SINGULAR_EVENT_CHART_BEFORE_ANY_EXISTING_PHYSICAL_DOMAIN_EXIT_OR_PROVE_THAT_NO_SUCH_HISTORY_DOES`.

The first interval is now rigorously covered; the next proof step is to extend
the same analytic action-ball cover until a transverse return or an existing
physical-domain exit is certified.  Only after a nonempty return domain is proved may a periodic-point mechanism
be established.  Numerical trajectory sampling, formal reversal, a new event
sign, or a fabricated parent section cannot substitute for this theorem.
