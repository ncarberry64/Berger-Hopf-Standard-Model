# BHSM v6.17.0 minimum threading axiom and fold kinetic closure

Primary domain result:
`BHSM_MINIMUM_THREADING_AXIOM_OVERCONSTRAINS_FOLD_CONSTRAINT`.

Kinetic result:
`BHSM_FOLD_KINETIC_REMAINS_UNRESOLVED_BY_EXACT_OPERATOR_OBSTRUCTION`.

The Minimum Net Threading Axiom is adopted exactly as requested:

\[
\bar S_\Sigma(x)
=\frac12\left(S_{{\rm out},\Sigma,+}(x)
+S_{{\rm out},\Sigma,-}(x)\right)=0
\]

for all admissible scalar harmonics in the resting interface domain. With
the inherited Z2 relation
\(S_{{\rm out},\Sigma,+}=S_{{\rm out},\Sigma,-}\), its one-cap form is
\(S_\Sigma=0\).

This is an explicitly adopted, coefficient-free BHSM interface-domain axiom.
It was not derived from the frozen P1+GHY+B1+scalar action, is not a gauge
quotient, and was not licensed before v6.17. No seam potential or stiffness
coefficient is added. Its interpretation is that uniform contact with an
unmarked common core selects zero net longitudinal threading bias in the
resting configuration. No metric, distance, duration, density, ordinary
stress tensor, or ordinary inside/outside relation is assigned to the common
core.

## Kinematic consistency

The axiom is well defined under the inherited gauge and reflection structure.
The gauge-invariant trace is

\[
S_\Sigma=
\left[B+N_0^2\zeta-a_0^2\partial_\rho E\right]_\Sigma .
\]

All previously declared bulk and boundary diffeomorphisms leave this
combination invariant. In the allowed fixed-support \(E=0\) gauge,
\(\zeta=0\), so the axiom is \(B_\Sigma=0\). The two-cap average rule and
one-cap zero rule are equivalent in outward conventions. The glue-jet
difference
\(\lambda_{\rm jet}=S_{{\rm out},+}-S_{{\rm out},-}\) remains distinct and
is still removed by Z2.

The axiom neither duplicates the metric junction condition

\[
\kappa_1[Q_{\mu\nu}]
+2C_\partial G_{\mu\nu}^{(4)}
=T_{\partial,\mu\nu}
\]

nor promotes a Codazzi/Bianchi Ward identity to an extra equation. It
supplies exactly the one boundary trace that v6.15 left open. Pole regularity
alone is compatible with a zero trace.

Fixed-\(\iota\) support is the official domain because it is already adopted
and is least assumption-heavy. The conditional composite support of v6.14
reconstructs \(\zeta\) from \(\widehat\sigma\), but the same invariant
\(S_\Sigma\) is set to zero, so it cannot change the result below.

The v6.16 P1 seam Hessian makes zero threading a stationary point of the
minimal seam variation, but does not derive the new axiom or prove that the
point is a physical minimum. The displayed spatial-harmonic quadratic form
has nonzero convention-dependent sign. The official construction remains a
domain declaration, not a boundary potential.

## Leading fold momentum constraint

At the critical cap,

\[
a_0(t)=\sqrt2\sin\frac{\pi t}{4},\qquad
N_0=\frac{\pi}{4},\qquad X_c=2 .
\]

The frozen fold tangent has

\[
H_{q,\tau}(t)
=\tau\frac{\chi_1t}{4\sin^2(\pi t/4)} .
\]

The exact v6.12 source is therefore

\[
J_{\rm shift}(t)
=-3H_{q,\tau}(t)
=-\frac{3\tau\chi_1t}
{4\sin^2(\pi t/4)} .
\]

Retaining \(B,E,\zeta\) through the gauge-invariant trace, the
constant-curvature commutator in the ADM momentum constraint gives the
leading longitudinal subblock for
\(S_q=\partial_qS|_{q=0}\):

\[
J_{\rm shift}(t)+L_S(t)S_q(t)=0,
\qquad
L_S(t)=-\frac{3X_c}{N_0a_0(t)^2}.
\]

This is a radial multiplication operator. The shift enters
\(K_{\mu\nu}\) through tangential derivatives and has no radial derivative.
Solving the subconstraint gives

\[
S_{q,{\rm req},\tau}(t)
=-\frac{N_0a_0(t)^2}{X_c}H_{q,\tau}(t)
=-\tau\frac{\pi\chi_1}{16}t .
\]

It is regular at the pole and vanishes linearly there. At B1, however,

\[
S_{q,{\rm req},\tau}(1)
=-\tau\frac{\pi\chi_1}{16}\ne0 .
\]

Equivalently, imposing the adopted value \(S_\Sigma=0\) leaves

\[
J_{\rm shift}(1)=-\frac32\tau\chi_1\ne0 .
\]

The critical scalar flux is zero, so it cannot cancel this residual. The
same endpoint value follows from the differentiated fixed-\(C_\partial\)
junction tangent \(H_{q,\tau}(1)=\tau\chi_1/2\). This uses the Ward relation
as a compatibility check, not as another boundary equation.

With
\(\chi_1=5.268307871542120\ldots\), the required endpoint magnitude is

\[
\frac{\pi\chi_1}{16}=1.034\ldots,
\]

and the residual magnitude is

\[
\frac32\chi_1=7.902461807313180\ldots .
\]

The two sheets have equal magnitudes and opposite signs. The scalar sign
does not enter. Analytic continuation therefore gives the actual transient
trace

\[
S_\Sigma(q)
=-\tau\frac{\pi\chi_1}{16}q+O(q^2).
\]

Consequently the hard rule \(S_\Sigma(q)=0\) for every \(q\) has the wrong
linear response and cannot contain the dynamical fold tangent. The direct
\(q=0\) level-set division remains unused.

## Rest--transition--rest interpretation

The obstruction permits a qualified temporal reconciliation. If the axiom
is a condition only on resting configurations, the seam can occupy different
domains at different stages of its M4/interface history:

1. In an early or initial resting phase, \(D_\mu q=0\) and the selected
   representative has \(\bar S_\Sigma=0\).
2. During a fold transition, \(D_\mu q\ne0\) and the momentum constraint
   requires
   \[
   S_\Sigma(x)
   =-\tau\frac{\pi\chi_1}{16}q(x)+O(q^2)
   \]
   in the fixed potential convention.
3. In a late or final resting phase, \(D_\mu q=0\), the physical
   longitudinal shift vanishes, and the zero constant representative may be
   selected again.

This is compatible with the v6.16 observation that a spacetime-constant
shift potential is a trivial stabilizer: only its gradient enters the
longitudinal displacement. A white-hole-like early release is therefore a
possible BHSM interpretation of the transition, not a consequence derived
by the present equations. “Early” and “late” refer solely to M4/interface
history; no time variable is assigned to the nonspatiotemporal common core.

This phase-separated picture is a BHSM identification and active
construction target, not a new adopted evolution law. It needs a covariant
phase criterion or action-derived switching law connecting the resting and
transition domains. It does not make the hard condition
\(S_\Sigma=0\) compatible with every dynamical scalar harmonic; that stronger
domain remains overconstrained.

## Domain and operator verdict

The full requested compensator vector would be

\[
Y=(A,B,\psi,E,\delta\sigma,\zeta)^T.
\]

Formally the axiom changes the free-trace count from one to zero and does not
duplicate a junction or Ward equation. But the source is not in the range of
the leading threading subblock with the adopted endpoint trace. Thus the
nominally closed domain contains no nonconstant critical fold tangent.

For the real radial pairing

\[
\langle u,v\rangle_0
=\int_0^1N_0a_0^4\bar u v\,dt,
\]

\(L_S\) is a formally self-adjoint multiplication operator, has zero
interior kernel, and has vanishing Green boundary form. Its unconstrained
local inverse reproduces \(S_{q,\rm req}\), but does not map the source into
the adopted B1 domain.

Per the required stop rule, no full \(L_C\), adjoint domain, full kernel,
adjoint kernel, Fredholm index, projected inverse, shooting solve,
collocation solve, or spectral solve is manufactured. In particular, no
generic pseudoinverse is used.

## Kinetic verdict

Because the constraint source fails before a Schur complement exists,

\[
K_{\rm shift+endpoint}^{\rm red}
\]

is not defined on the adopted fold domain. The inherited positive pieces
remain

\[
K_{\rm scalar}(0)\ge2>0
\]

and

\[
K_{\rm Weyl}(0)
=\frac{3\chi_1^2(4-\pi)^2}{16\pi}
=1.220620174933802\ldots>0 .
\]

They cannot determine

\[
k_q^E(0)
=K_{\rm scalar}
+K_{\rm shift+endpoint}^{\rm red}
+K_{\rm Weyl}
\]

when the middle term has no admissible constraint solution. No positive,
ghost, null, strongly coupled, or nondynamical classification is issued.
The fold coordinate is not promoted to a four-dimensional field in this
domain.

The static v6.11 result remains

\[
B_\tau^{\rm red}
=-\tau\frac{\nu_1}{2}q+O(q^2),
\qquad
\nu_1=109.666681740423\ldots .
\]

Thus the exterior \(\tau=+\) sheet has negative reduced static curvature and
the core-facing \(\tau=-\) sheet has positive reduced static curvature in
the tested direction. These are not physical Einstein-frame mass
numerators. Neither \(m_{\rm ext}^2\) nor \(m_{\rm core}^2\) is calculated.

## Model-wide closure map

- Parent/core/topology: the non-spatiotemporal-core and topology ledgers are
  retained; a core transfer mechanism remains an independent construction
  target. Ordinary core metric assignments remain rejected.
- P1 geometry: bulk constraints and junction projections are available in
  the conditional P1+GHY representative; parent source and coefficient
  selection remain open. GHY is not a physical tension.
- B1 intrinsic action: the provisional action supplies the metric junction
  and Ward structure; its coefficient-lock/source theorem remains open.
- Scalar-wall fold: the two static Puiseux sheets and their continuation
  constants remain validated. Direct division by the vanishing \(q=0\)
  scalar slope remains rejected.
- Fold kinetic sector: v6.17 adopts the requested trace axiom but rejects it
  as a domain for nonconstant fold harmonics. An action-selected condition
  admitting \(S_{{\rm req},\Sigma}\) is now the exact construction target.
- Gauge connections: localized domains and action normalization remain
  independent targets.
- Fermionic action/domain: the chiral ledger remains conditional on a
  complete sourced Dirac action and domain.
- Charged-current/CKM: basis misalignment remains the interpretation;
  independent current normalization remains open.
- Neutral propagation/PMNS: effective response scaffolds remain conditional
  on operator and scale closure.
- Dimensionful scale bridge: no absolute scale is introduced here; a sourced
  mechanism remains open.
- Scalar/topographic sector: the finite-basis operator remains conditional;
  the full action Hessian and spectrum remain open.
- Prediction/falsification layer: frozen screens and their claim
  classifications are unchanged; independent mode selection remains active.

No new action term, fitted coefficient, measured input, dimensionful
primitive, boundary tension, `tau_J`, radion potential, seam potential,
neutral construction, physical bulk Dirac law, frozen-prediction change, or
official prediction-logic change is introduced.
