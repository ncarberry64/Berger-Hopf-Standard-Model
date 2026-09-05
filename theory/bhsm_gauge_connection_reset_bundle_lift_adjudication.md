# Attachment-representative equivalence audit

Status: `ATTACHMENT_REPRESENTATIVE_PHYSICAL_EQUIVALENCE_UNDECIDED_BECAUSE_THE_RELATIVE_EVENT_CHILD_DIFFEO_QUOTIENT_IS_NOT_ACTION_OWNED`.

This audit begins from the earned case-4 result and does not reopen its
ontology proof. The event and child boundaries are abstract `S3 times S3`
copies, the gauge-vertical reset jet is `(G_R,dG_R)=(I,0)`, and no pointwise
spatial attachment is action-owned. The new question is whether BHSM needs a
representative `F_B` or only its physical equivalence class.

## Which diffeomorphisms are actually gauge?

The master symmetry ledger gives the controlling answer:

| Stratum | Diffeomorphism covariance |
|---|---|
| `S8` | yes |
| `S5|4` | yes before ADM gauge fixing |
| `S4` | yes |
| cross-level/reset intertwiner | **unproved** |

Thus the covariant bulk and boundary densities may be pulled back level by
level. That does not by itself define an independent relative action of
`Diff(Sigma_event) times Diff(Sigma_child)` on the reset-glued action domain.
For a supplied glue `F_B`, common reparametrizations satisfying

\[
 \phi_{\rm child}\circ F_B=F_B\circ\phi_{\rm event}
\]

describe the same fixed glue. They do not relate two distinct attachment
maps. Relating such maps requires a larger relative action together with its
action on the background, trace graph, Galerkin projectors, constraints, spin
structure, and BRST complex. No retained source supplies that contract.

Full `Diff(Sigma)` is especially not available as an automatic answer. The
current C2 germ is tied to a fixed background, radial Galerkin domain,
Berger/Hopf structure, and frozen internal projectors. The maximal candidate
at fixed background is their common stabilizer inside the orientation- and
spin-preserving diffeomorphisms, but BHSM has not made even that stabilizer a
relative event-child gauge group.

## The `id`/`Ad` witness

Take

\[
F_0={\rm id}\times {\rm id},\qquad
F_a={\rm Ad}_{\exp(\theta\tau_3)}\times {\rm id}.
\]

This one-parameter family preserves the Berger/Hopf vertical axis, horizontal
metric plane, product structure, marked group identity, orientation, and Haar
measure. Transforming the metric and fields together gives the standard
naturality identities:

\[
 F(\phi^*A)=\phi^*F(A),
 \qquad
 \Gamma_{\rm Maxwell}[\phi^*g,\phi^*A]
 =\Gamma_{\rm Maxwell}[g,A],
\]

and, for the natural spin lift,

\[
D_{\phi^*g,\phi^*A}\,U_\phi=U_\phi D_{g,A}.
\]

The executable tangent witness verifies zero residual, to numerical
roundoff, for:

- metric, measure, orientation, connection, and curvature pullback;
- Maxwell quadratic form and its cotangent-lift canonical forms;
- Dirac unitary equivalence, eigenvalues, and singular values;
- BRST nilpotency, complex rank, and ghost bilinear;
- the algebraic HS value and combined local tensorial GFHS value;
- commutation of the spatial spin lift with `U_R tensor I3`, leaving all nine
  frozen family/mode fibers untouched.

This proves covariance of every currently evaluable tensorial object for a
nontrivial admissible *candidate*. It does not prove physical reset
equivalence: the current local GFHS implementation has no spatial group action
on its radial Galerkin domain, and its nonfermion relative boundary graph is
still absent. The integrated cross-copy reset action, event balance, Noether
charges, and BRST cohomology on the actual reset domain therefore remain
unevaluable.

## Maxwell and connection classes

For any supplied representative, the common gauge frame gives

\[
F_B^*A_{\rm child}=A_{\rm event},\qquad
F_B^*\mathcal F_{\rm child}=\mathcal F_{\rm event}.
\]

Changing `F_B` and simultaneously pulling back all child data produces
isomorphic connection and curvature representatives. A unique class
`[A_child]`, however, exists only after the attachment group and its orbit
relation are defined. BHSM currently owns neither, so connection-class
transport is conditional rather than derived.

## Fermion, ghost, and HS naturality

The Dirac and gauge-fermion terms are natural under orientation- and
spin-structure-preserving diffeomorphisms when the metric, connection,
spinors, measure, and domain are transformed together. The fermion-HS term is
natural when the HS field is pulled back as a scalar. The gauge/ghost BRST
complex transforms by conjugation. These facts preserve intrinsic spectra,
singular values, trace/determinant invariants, nilpotency, complex ranks, and
internal projector ranks.

They do not create the missing spatial-diffeomorphism ghost sector or prove
that it intertwines with the retained internal gauge BRST quotient. AE2 owns
the fermion fiber lift, but not a relative base-diffeomorphism action on its
trace graph.

## Canonical reduction is not a naive quotient

On `T*Q_boundary`, every configuration-space diffeomorphism has a cotangent
lift preserving the canonical one-form `alpha` and symplectic form `omega`.
Nevertheless `alpha` is not horizontal on the full phase space:

\[
\iota_{\xi_{T^*Q}}\alpha=\langle J,\xi\rangle.
\]

Consequently it is not basic away from the momentum-map constraint. A
reduced symplectic form may descend on

\[
J^{-1}(0)/G_{\rm attachment}
\]

only after BHSM supplies the group action, moment map, constraint surface,
domain preservation, and the usual regularity conditions. The attachment
diffeomorphism ghost/BRST complex must also be supplied. None of those
objects is currently action-owned. Therefore `beta=R_B^*alpha-alpha` cannot
yet be classified as basic or representative invariant, and no reduced reset
generating germ or graph jets follow.

## Three-outcome adjudication

- **Outcome A — pure redundancy:** not proved. The relative attachment group
  does not act on the retained reset domain.
- **Outcome B — partial redundancy:** not proved. Possible relative Hopf
  frame, mapping-class, holonomy, or discrete seam sectors cannot be called
  residual invariants before the quotient group is defined.
- **Outcome C — physical nonuniqueness:** not proved. No two action-owned
  representatives have been compared on one complete reset action/domain.

The equality of the `id` and `Ad` witness is necessary evidence for Outcome A,
but is not sufficient. The identity map is therefore neither a derived
physical attachment nor an authorized gauge fixing.

## Hindsight 20/20

### VALIDATED

- all currently evaluable local GFHS tensorial objects are natural under the
  simultaneous `id`/`Ad` pullback and unitary identification;
- the canonical cotangent lift preserves `alpha` and `omega` representative
  by representative;
- the master action owns levelwise diffeomorphism covariance;
- `alpha` is not basic on the unreduced full phase space;
- frozen family, mode, representation, and projector content is unchanged.

### INVALIDATED

- inferring a reset quotient from levelwise covariance;
- declaring full `Diff(Sigma)` to be an admissible attachment group;
- declaring two matching examples sufficient to establish physical
  representative independence;
- using `F_B=id` as a gauge fixing before the quotient exists;
- forming a naive symplectic quotient without the moment-map constraint.

### OPEN

- whether the attachment ambiguity is pure, partial, or physical;
- the connection and curvature classes on an attachment quotient;
- the reduced Maxwell/BRST phase space and canonical reset;
- `beta`, the local reset generator, `Theta` and its first three derivatives;
- representative-independent global `S1`--`S4` beyond the reference slice.

### EXACT NEXT OBJECT

`ACTION_OWNED_EVENT_CHILD_RELATIVE_SPATIAL_DIFFEOMORPHISM_EQUIVALENCE_CONTRACT_ABSENT`

That contract must define the relative group and its action on backgrounds,
fields, spin structures, trace graphs, Galerkin projectors, constraints,
momenta, and ghosts. It must then state the moment-map/BRST reduction and
which large or framed transformations remain physical. Only then can BHSM
decide whether a representative `F_B`, only `[F_B]`, or a smaller residual
attachment datum is required.
