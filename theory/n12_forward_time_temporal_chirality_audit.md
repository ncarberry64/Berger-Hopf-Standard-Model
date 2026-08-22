# Forward-time domain and chiral-reflection audit

Status: **BHSM has one forward physical-time orientation; formal reversal is
an algebraic/chiral pairing of Cauchy states, not a competing temporal
orientation**.

BHSM physical time is oriented and always forward.  Define only as an algebraic
field reflection

\[
\mathcal R(q,v,\ell,s)=(q,-v,\ell,-s).
\]

It is not a gauge transformation and is not physical backward evolution. It
maps one set of Cauchy data to another. The existing clock domain already fixes
\(dt>0\), positive boundary lapse, and
\(d\tau=N_{\rm boundary}dt>0\). Since the reflection does not act on \(dt\)
or lapse, the re-expressed reflected state has its own forward solution and
lies in the same single time-oriented domain. There is no forward-versus-
backward action-selection problem.

## Existing candidate invariants

### Eta-clock and shift current

The retained eta contribution uses

\[
X_\eta=X_{\rm spatial}-(\beta/N)^2,
\qquad
\frac{\partial X_\eta}{\partial\beta}=-2\beta/N^2.
\]

Hence its shift current is odd under \(\mathcal R\). This is an action-owned
covector in the radial diffeomorphism Ward identity, not a positive conserved
clock charge.  Its retained modal coefficients have both signs even within one
evaluated state.  The shift constraint changes sign with the current, so its
zero set admits both reflected sectors.  Positive lapse and forward proper-time
parametrization do not impose a sign on this spatial shift current.

### Canonical and symplectic orientation

The canonical momentum satisfies \(p(\mathcal RY)=-p(Y)\), and \(\mathcal R\)
is anti-symplectic for the reduced canonical form. This distinguishes the two
Cauchy states; it does not give them opposite physical time orientations.
The complete-child row is momentum *matching*, \(p_C-p_E=0\); simultaneous
reflection changes the sign of the row and preserves its zero set.  There is no
retained inequality selecting outgoing normal momentum.  The historical
contact/ejection ledger explicitly records that its sign is unselected.

### Singular ordered-event hitting orientation

The event equation nulls the same Dirac block used in the regular
Euler--Dirac solve.  Therefore \(V(E)\) is not defined by the unbordered
equations and the earlier candidate \(D e_{\rm ord}(E)V(E)\) must not be used.
For a normalized kernel vector \(\psi\), define instead

\[
\chi_{\rm hit}(E)=\operatorname{sgn}\left(
D^3L[(0,\psi)^3]\langle\psi,b_{\rm ED}\rangle\right).
\]

On a regular one-sided approach this is the sign of the finite limit of
\(\tfrac12d(e_{\rm ord}^2)/dt\).  The cubic factor is even under
\(\mathcal R\), the soft Fredholm forcing is odd, and hence
\(\chi_{\rm hit}\) flips.  The retained N12 representative has negative
product while its formal reflection has positive product.  But the event
equation contains no sign condition on either factor, so this labels the two
sectors without selecting one through the current event-to-child
correspondence.

### Hopf, boundary, attachment, and topological orientation

The fixed Hopf degree, spatial boundary orientation, outward-normal convention,
FR parity, incidence, and attachment configuration depend on \(q\) and are
unchanged by \(\mathcal R\).  The degree \(+1\) and \(-1\) Hopf branches are
genuinely distinct spatial topological components, but formal velocity/shift
reflection leaves the degree of a given component fixed.  The distributional
event flux is signed by that spatial orientation; no retained cross-term ties
its sign to \(\chi_{\rm temp}\).  The two-sided attachment flux equation also
flips both canonical sides together.  None of these structures selects a
temporal chirality.

### Clock orientation

The proper-time law on a regular future-oriented worldtube gives forward
transport once a Cauchy state, generator, and domain are supplied.  It does not
choose the signs of the supplied velocity, momentum, or shift data.  The
repository also contains no action-selected stable reference cycle whose
orientation could provide that missing selection.

## Result

The existing retained action owns a one-sided terminal/emergent boundary
**label**,
\(\operatorname{sgn}(c_\psi b_\psi)\), on nondegenerate simple singular-event
components, and owns odd canonical/shift covectors that distinguish the paired
Cauchy states. The existing positive clock domain already supplies the unique
physical time orientation. Therefore

\[
\mathcal C_\infty(\mathcal RE)=\mathcal R\mathcal C_\infty(E)
\]

is equivariance between forward-oriented chiral state partners, not an
equivalence relation and not a second temporal orientation. Neither state is
discarded or quotiented. Choosing a physical state or family from a trajectory,
solver basin, or desired observable would still be a new physical gate, but no
choice of time direction remains open.

The matched-parent route remains unavailable. The event is now certified
locally as a singular boundary hit followed by a regular, set-valued
event-to-child relation, not an ordinary transverse Poincare section. The
exact analytic dependency is

`PROVE_THAT_AT_LEAST_ONE_EXISTING_FORWARD_COMPLETE_CHILD_HISTORY_REACHES_THE_CERTIFIED_TERMINAL_SINGULAR_EVENT_CHART_BEFORE_ANY_EXISTING_PHYSICAL_DOMAIN_EXIT_OR_PROVE_THAT_NO_SUCH_HISTORY_DOES`.

The previously proposed globally one-signed event-forward estimate cannot
prove this, and no numerical campaign is authorized as a substitute.
