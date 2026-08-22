# Forward invariant-history existence gate

Status: **the candidate forward boundary-return relation is typed, but its
singular hitting/reset theorem and forward domain remain open; no invariant
child history is selected**.

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
2. the maximal regular forward solution remains in the existing eta, metric,
   lapse, inertia, gauge, trace, and invertible-Dirac domain for
   \(0\le t<\tau\);
3. \(f_E(t)\ne0\) for \(0<t<\tau\) and \(f_E(\tau)=0\);
4. the one-sided state has a limit \(E'\) in the simple ordered-event locus;
5. the action-owned singular hitting product
   \(c_\psi b_\psi\) is nonzero and the boundary-hitting limit is regular;
6. \(\mathcal C_\infty\) is defined at \(E'\), with a regular reset
   composition.

Only then is

\[
\mathcal P(E)=\mathcal C_\infty(E'),\qquad
E'=\lim_{t\uparrow\tau}\varphi_t(\mathcal C_\infty(E))
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

The repository currently supplies none of these global ingredients.  It
supplies an event-free first local continuum interval and a maximal
continuation-or-domain-exit alternative.  It does not yet supply regularity of
the singular hitting/reset composition \(\mathcal P\).  The one stored
persistence history records no return.  The constraint energy is zero,
the unreduced energy is noncoercive, the child boundary Hamiltonian is absent,
and no compact invariant energy shell or stable reference cycle is available.
Consequently recurrence, Schauder/Lefschetz degree, and a variational periodic
orbit theorem cannot presently be invoked.

## 4. Localized retained-action failure

The earliest failure is not the absence of a better nonlinear solver.  It is

`ONE_SIDED_SINGULAR_ORDERED_EVENT_HITTING_AND_RESET_REGULARITY_NOT_ESTABLISHED`.

This is not a proof that the return domain is empty or that no invariant child
history exists.  It is the first missing theorem in the exact existing
state-selection construction.  Nonemptiness is downstream.  The next
mathematical dependency is:

`DERIVE_AND_CERTIFY_THE_EXISTING_ACTION_OWNED_ONE_SIDED_SINGULAR_ORDERED_EVENT_HITTING_LAW_AND_ITS_EVENT_TO_CHILD_RESET_REGULARITY_OR_LOCALIZE_THE_FIRST_RETAINED_ACTION_FAILURE`.

The first interval is now rigorously covered; the next proof step is to extend
the same analytic action-ball cover until a transverse return or an existing
physical-domain exit is certified.  Only after a nonempty return domain is proved may a periodic-point mechanism
be established.  Numerical trajectory sampling, formal reversal, a new event
sign, or a fabricated parent section cannot substitute for this theorem.
