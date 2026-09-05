# Attachment-representative equivalence audit

Status: `OUTCOME_D_RELATIVE_ATTACHMENT_EQUIVALENCE_UNDECIDABLE_UNTIL_A_DIFFERENTIABLE_RELATIVE_BOUNDARY_DIFFEO_GENERATOR_IS_ACTION_OWNED`.

This audit begins from the earned case-4 result and does not reopen its
ontology proof. The event and child boundaries are abstract `S3 times S3`
copies, the gauge-vertical reset jet is `(G_R,dG_R)=(I,0)`, and no pointwise
spatial attachment is action-owned. The new question is whether BHSM needs a
representative `F_B` or only its physical equivalence class.

## Track-2 result: the candidate is an action groupoid

Let `A` be the space of admissible orientation- and spin-preserving maps
`F:Sigma_event -> Sigma_child`. The largest formal two-sided action is

\[
  F\longmapsto \phi_c\circ F\circ\phi_e^{-1}.
\]

Its correct mathematical type is the action groupoid
`(H_child times H_event) action A`. It is not canonically a subgroup of one
copy of `Diff(Sigma)`, because the event and child are distinct abstract
boundary copies and BHSM owns no reference identification between them.
For a supplied `F`, the already justified simultaneous reparametrizations are
exactly the stabilizer arrows

\[
 \operatorname{Stab}(F)=
 \{(\phi_e,\phi_c):\phi_c\circ F=F\circ\phi_e\}.
\]

These arrows relabel one fixed glue. They do not move `F` and therefore do
not remove attachment nonuniqueness.

The formal action on every natural field is inherited in one stroke: tensor
and form pullback, spin-lift pullback, inverse-adjoint cotangent transport of
momenta, and conjugation of induced trace projectors. The reset graph would
have to transform from `Graph(R_F)` to `Graph(R_Fprime)`; graph jets use the
corresponding jet prolongation. Galerkin compatibility requires either
`U_phi P_N=P_N U_phi` or a transformed projector. AE2 requires preservation
of its trace, variation, and squared-operator graphs, while AE4 requires
preservation of the future-retarded parent/child trace domain. No current
source defines these latter spatial actions. This general construction makes
new objectwise Maxwell, Dirac, curvature, ghost, HS, and GFHS covariance
checks redundant.

## Domain intersection

The v15.57 quotient

\[
 X_{\rm phys}^s=\mathcal C_{\rm constraints}^s/
 (\operatorname{Diff}^{s+1}_0\times\operatorname{Gauge}^{s+1}_0)
\]

acts on a complete seven-dimensional Cauchy configuration. `F_B` is not a
configuration variable in that contract, so this is not an independent
event/child attachment action. Likewise the framed
`Diff^(s+1)_(0,fr)(S7)` geometry quotient has no owned restriction/extension
theorem to the two `S3 times S3` seam copies. Its large diffeomorphisms are
explicitly not quotiented.

Intersecting all declared requirements gives only a characterization of
candidate factors `H_event,H_child`: they must preserve Sobolev regularity,
orientation and spin, fixed incidence and boundary identities, the AE2
graphs, the AE4 retarded domain, Berger/Hopf data (or its declared background
orbit), Galerkin projectors, canonical constraints, and BRST domains. The
repository owns no nontrivial group satisfying this list that moves `F`.
The maximal proved domain-preserving structure remains the stabilizer
subgroupoid of each already supplied glue.

## Conditional orbit, stabilizer, and identity theorem

If admissible factors are later derived, then

\[
 \operatorname{Orb}(F)=H_c\,F\,H_e^{-1},\qquad
 \mathcal A/(H_c\times H_e)=H_c\backslash\mathcal A/H_e.
\]

After choosing a reference identification, `id` is a global representative
precisely when there are `h_c,h_e` with
`h_c F h_e^(-1)=id`; the analogous germ condition is necessary and
sufficient locally. Full independent diffeomorphism factors would be
transitive on an allowed orientation/spin component, but those factors are
not action-owned. A finite `S3` adversarial model verifies the
orbit-stabilizer identity while showing that `id` can lie in the full-group
orbit and fail to lie in the orbit of a proper domain-preserving subgroup.
Thus identity is neither a global nor local authorized gauge choice in the
present theory.

## Decisive canonical and BRST test

The necessary relative generator must be differentiable on the actual reset
domain. In covariant phase-space notation its variation has the schematic
form

\[
 \delta H_{(\xi_e,\xi_c)}=
 \sum_{s=e,c}\int_{\partial M_s}
 (\delta Q_{\xi_s}-\iota_{\xi_s}\Theta_{\rm retained})
 -\delta B_{(\xi_e,\xi_c)}.
\]

BHSM does not yet own the complete retained `Theta`, both relative
`Q_xi` terms, the boundary ensemble/counterterm `B_xi`, or the action of this
generator on `F_B` and the reset trace graph. It therefore does not determine
whether the relative charge vanishes, whether the vector is tangent to the
nonlinear reset solution space, or whether it lies in the presymplectic
kernel. The seam-slide no-go supplies the relevant adversarial precedent: a
null auxiliary multiplier direction with zero candidate generator is not
gauge when it is not an action symmetry or tangent to the nonlinear domain.

The retained AE2 ghost is an internal `G_SM` gauge ghost. No relative spatial
diffeomorphism ghost, constraint, BRST differential, or closure theorem is
present. The v15.57 notation `Diff_0` does not materialize such a BRST
complex. Adding one now would require first selecting the boundary ensemble,
charge sector, and domain representation; it is therefore a new physical
postulate rather than a unique consequence of the existing action.

## Residual adversarial audit

Orientation and incidence are fixed input sectors, not newly derived
continuous residuals. Mapping-class, holonomy, connection, curvature, and
static Hopf-frame classes cannot be promoted before the actual group orbit is
known. One blanket shortcut is nevertheless falsified: the compact momentum
constraint admits equal-and-opposite parent/child Hopf momentum, and the
relative rotor has positive energy `J^2/(2 I_rel)`. Hence all relative Hopf
transformations cannot be declared gauge. This dynamical rotor is not yet
identified with a static `F_B` Hopf-frame class, so it is an obstruction to
overquotienting, not proof of Outcome B or C.

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

## Four-outcome adjudication

- **Outcome A — pure redundancy:** not proved. The relative attachment group
  does not act on the retained reset domain.
- **Outcome B — partial redundancy:** not proved. Possible relative Hopf
  frame, mapping-class, holonomy, or discrete seam sectors cannot be called
  residual invariants before the quotient group is defined.
- **Outcome C — physical nonuniqueness:** not proved. No two action-owned
  representatives have been compared on one complete reset action/domain.
- **Outcome D — existing BHSM is insufficient:** **derived** after exhausting
  the formal action groupoid, actual domain intersection, canonical generator,
  BRST ownership, conditional orbit/stabilizer, identity criterion, and
  residual candidates. The missing differentiable relative boundary
  generator and boundary ensemble prevent the theory from deciding A, B, or C.

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
- the most general candidate attachment action is a two-sided action groupoid;
- conditional orbit, stabilizer, double-coset quotient, and identity criteria
  are derived;
- only fixed-glue stabilizer reparametrizations are presently action-owned;
- Outcome D is earned at the differentiable-generator boundary.

### INVALIDATED

- inferring a reset quotient from levelwise covariance;
- declaring full `Diff(Sigma)` to be an admissible attachment group;
- declaring two matching examples sufficient to establish physical
  representative independence;
- using `F_B=id` as a gauge fixing before the quotient exists;
- forming a naive symplectic quotient without the moment-map constraint.
- treating the v15.57 diagonal `Diff_0` quotient as a relative attachment group;
- inferring gauge from a null auxiliary or multiplier direction;
- declaring every relative Hopf transformation gauge;
- declaring identity representative admissible for an underived subgroup.

### REDUNDANT

- new objectwise covariance proofs for Maxwell, curvature, Dirac, ghosts, HS,
  GFHS, canonical pullbacks, frozen representations, or projectors;
- a second `id`/`Ad` naturality witness;
- rebuilding the frozen family/representation calculation.

### OPEN

- whether the attachment ambiguity is pure, partial, or physical;
- the connection and curvature classes on an attachment quotient;
- the reduced Maxwell/BRST phase space and canonical reset;
- `beta`, the local reset generator, `Theta` and its first three derivatives;
- representative-independent global `S1`--`S4` beyond the reference slice.

### EXACT NEXT OBJECT

`ACTION_OWNED_DIFFERENTIABLE_RELATIVE_EVENT_CHILD_SPATIAL_DIFFEO_GENERATOR_ON_THE_RESET_TRACE_DOMAIN_ABSENT`

This object must be derived from the complete parent/child variational action.
It must provide the retained symplectic potential, both boundary Noether
charges, the differentiability counterterm/ensemble, and its action on `F_B`
and the reset trace domain. Its charge and kernel then decide whether relative
arrows are gauge, partially gauge, or physical. A spatial BRST extension is
permitted only if that generator is first established.
