# BHSM full-field action attachment before Gate 7

## Scope and conclusion

This note specifies the additive, background-parametric attachment layer that
may receive a future Gate-7 background. It does not select such a background,
derive a physical spectrum, or create a new BHSM action version.

The research decision is **Case B**. The repository owns the conceptual
single-functional doctrine, the regulated free superdeterminant, restricted
operator/source/contact jets, the retained N12 geometry action, and the AE2
reset domain. It does not yet own one executable current-domain functional

\[
\Gamma_{\rm GFHS}[B;A,c,\bar c,\psi,\bar\psi,H]
\]

on arbitrary fields and background. In particular, the `one_functional`
entries in the historical pushforward artifacts are formulas encoded as
strings, while the executable Fréchet routines consume already assembled
operators and response vertices. The free superdeterminant accepts a cycle
scale, not interacting gauge, ghost, fermion, and HS field coordinates.
Response matrices therefore cannot be spliced into a Hessian and called an
action.

The strongest newer AE4 integration authority reaches the same conclusion:
one background-covariant, reset-glued stratified operator remains to be
realized. The AE4 owner is a selected successor ontology, not permission to
silently combine an AE2 geometry oracle with AE4 terms. A version-compatibility
record remains mandatory at that transition.

## Full-field state space

The deterministic order is

\[
\Phi=(q,\dot q,\lambda,A,c,\bar c,\psi,\bar\psi,H).
\]

The retained N12 dimensions are 37 configuration coefficients, 37 velocity
coefficients, and 24 multipliers. The retained internal ranks are twelve gauge
generators, twelve ghost and twelve antighost species, three times sixteen
left-Weyl fermion species and their independent conjugates, and four HS
channels. Spacetime/history basis multiplicities are explicit realization
parameters. The default registry value of one means one formal basis element
per retained fiber; it is not a physical discretization.

Every block records its deterministic slice, statistics, coordinate role,
coarse labels, a unique label for every coordinate, source, and background
dependency. Square projectors and rectangular restriction maps are derived
from those slices. Mode index is outermost and the recorded internal index is
innermost. The registry contains no mass, mixing, gauge coupling, or
experimental number.

## Common action and current attachment

The intended action has the one-owner form

\[
S_{\rm full}[\Phi;B]
=S_{N12}^{\rm local}+S_{\rm history/seam}^{\rm AE2}
+\Gamma_{\rm GFHS}^{\rm current-domain}.
\]

An action component is admissible only when it supplies scalar value and exact
ordered directional derivatives through fourth order, has an action version,
background dependence, and provenance, and uses no empirical input. A stored
response object is rejected at registration. Source action version and
assembled action version are separate fields: if they differ, a hashed
version-transition certificate is mandatory. Thus the selected AE4 successor
owner is representable without silently rebadging the retained AE2 kernel.

At the present frontier, only the retained local N12 geometry action is a
callable component. The wrapper evaluates this action exactly when every
unowned field is zero. A nonzero gauge, ghost, fermion, antifermion, or HS
field raises `MissingActionSourceError`; it is never interpreted as an action
zero. The same rule applies to derivatives whose directions touch an unowned
sector.

## Domain, history, and seam

AE2 makes the fermion field a section on the event/child union with its two
traces glued by the reset-owned spin–gauge lift. The independent fermion
surface density is exactly zero because the reset is an internal glue, not an
extra material surface. This is an action-domain statement, not an executable
history Dirac operator.

The retained N12 JAX oracle is explicitly a local kernel and excludes history
and seam terms. Gauge/ghost, Weyl, and HS history-parametric incidence and
source jets exist, but the complete current-domain operator and any
nonfermionic Wentzell/seam forms have not been assembled. They are not
defaulted to zero. The geometry component therefore carries
`LOCAL_N12_KERNEL`, not the background's full domain identifier; physical
promotion requires a separately hashed `RESET_GLUED_MAXIMAL_HISTORY` coverage
certificate for every component. Hence the complete geometry and current
GFHS blocks remain missing-action-source.

## Derivative and graded conventions

The interface exposes matrix-free

\[
S^{(n)}[v_1,\ldots,v_n],\qquad 1\le n\le4,
\]

and never forms dense cubic or quartic tensors. Bosonic directions use the
ordinary multilinear derivative. Fermion, antifermion, ghost, and antighost
directions have odd parity. Ordered left derivatives obey the Koszul rule:
permuting two odd derivative directions contributes a minus sign; exchanging
an odd and an even direction does not. The interface checks that each
direction has homogeneous parity, requires any odd-sector component to
declare a graded-left-derivative oracle, and exposes the exact
permutation-sign function. It does not convert an ordinary commuting oracle
into a Grassmann oracle. A future GFHS component must implement this ordered
graded oracle; the existing real-valued universal JAX expansion alone cannot
certify a Grassmann Hessian.

Derivative ownership is signature-based rather than sector-union based. A
requested mixed contraction must be covered by one component that owns every
participating field block, including both ghost/antighost or
fermion/antifermion blocks where relevant. Separate self-sector components do
not imply a zero mixed derivative. Full promotion additionally requires all
sector signatures through fourth order. An S2 structural zero is accepted
only with separate action/BRST provenance and does not stand in for higher
variation coverage.

## Quadratic block structure

All fifteen unordered sector pairs among geometry, gauge, ghost, fermion, and
HS are materialized in the audit. `ACTION_DERIVED` is reserved for a complete
same-action block. The local geometry Hessian is action-derived, but the full
history/seam completion depends on the future realization, so the complete
geometry–geometry entry is `MISSING_ACTION_SOURCE` until that assembly exists.
Every current GFHS self or mixed block has the same classification. A
separate local-subblock record identifies the retained N12 geometry Hessian
as `ACTION_DERIVED`. No compatible historical response is upgraded to
`ACTION_DERIVED`.

`STRUCTURAL_ZERO` may be used only after the governing action or BRST complex
proves the absence of a term. It is not inferred from a zero-background
evaluation. `NOT_APPLICABLE` is reserved for pairs outside a particular
realization.

## Reduction identities

Embedding the 98 retained geometry coefficients and setting all other fields
to zero gives exactly the retained local action,

\[
S_{\rm attachment}[g,0_{\rm SM}]=S_{N12}^{\rm local}[g],
\]

and the first geometry variation is the same nested-JVP derivative. The
wrapper adds no coefficient or constant. Gauge-only, fermion-only, HS-only,
and interaction reductions are presently negative tests: each must fail with
the exact missing owner. When the current-domain GFHS component is supplied,
the same tests become positive reductions against its scalar action, not
against stored response matrices.

## BRST quotient

The prepared consumer adapter reuses the inverse-free BRST quotient only
after at least a mathematical background is bound. It is not a complete BRST
interface because its full-field generator/gauge-condition provider is open.
The eventual caller must supply the
ungauge-fixed constant and momentum-linear quadratic symbols, tangent
constraints, complete gauge-orbit generators, and the derivative of an
action-owned gauge condition. The Faddeev–Popov operator remains derived as
the gauge-condition derivative along the same orbit. Regularity, constraint
tangency, gauge-null identities, and AE2 reset intertwining remain mandatory.
No physical quotient is frozen in this sprint.

## Background authority and momentum symbol

The semantic states are `UNBOUND_BACKGROUND`,
`CERTIFIED_MATHEMATICAL_BACKGROUND`, and `PHYSICAL_BACKGROUND`. A mathematical
center carries an exact array digest and provenance but cannot promote.
Physical binding requires an authority JSON whose path and digest are
configured as a trust anchor before binding and then recomputed. Its contract
explicitly closes Gate 7, authorizes physical use, matches the action version,
and binds the exact 98-coordinate retained-geometry digest, registry digest,
domain and metric/tetrad digests, background
identifier, domain identifier, and provenance. Every path in the authority's
source-hash ledger is resolved beneath an explicit repository root and its
bytes are rehashed; path escape, a missing file, or any mismatch rejects the
binding. The registry also requires a separately hashed finite-basis
realization artifact; changing a formal mode count does not certify a physical
discretization. A later full-field expansion state may contain additional SM
coordinates, but its first 98 coordinates must reproduce the bound Gate-7
geometry exactly.

This removes the earlier boolean-only promotion path. The momentum adapter can
construct a mathematical `ActionMomentumMap`; its other operation is only a
conditional S2 contraction against caller-supplied lifts and is never labeled
a physical symbol. The full action-owned momentum-lift provider remains open.
The eventual symbol must be derived from bound \(S^{(2)}\), then quotiented; a
local historical symbol is not a physical substitute.

## Yukawa, HS, and saddle discipline

The four allowed Yukawa channel classes and the action-level derivative
location are retained. Numerical physical matrices remain false until the
same-action HS Hessian selects a direction and amplitude. The historical unit
LR vertex is a coefficient-placement identity, not a fitted physical Yukawa.
No measured mass, CKM/PMNS entry, Higgs pole, decay width, or gauge coupling is
used.

The replacement-saddle consumer can form the ambient first variation and pass
it to the retained constraint-projected force algebra. The full graded S1 and
current constraint provider are still open, so the full saddle interface is
not complete and no physical saddle is selected. Likewise, the HS consumer
can request the same-action Hessian but deliberately implements no physical
eigenvector selection: a certified saddle, quotient, mixed Schur block, and
isolated eigenspace are still required.

## Exact remaining object and claim boundary

The smallest missing public action source is the executable scalar

\[
\Gamma_{\rm GFHS}[B;A,c,\bar c,\psi,\bar\psi,H]
\]

with its ordered derivatives. Its necessary lower-level owner includes

\[
P_{\rm GFHS}[B;A,c,\bar c,\psi,\bar\psi,H]
\]

and the selected current-domain stratified Dirac family whose square supplies
that operator, on the reset-glued maximal-history domain with explicit
source/contact, response-multiplier, gauge-fixing, ghost, regulator, and seam
data. The operator is not equivalent to the generating functional until the
graded trace/action construction is executable. The resulting scalar must
provide directional jets through fourth order. Existing zero-source
operators and restricted \(P_0,V,Q\) jets can be reused only where their
action version, domain, background map, and field coordinates match; missing
cross contacts must fail closed.

Validated here are the registry, projectors, strict binder, retained geometry
embedding and reduction, matrix-free dispatch, graded convention, and prepared
BRST/momentum consumers. Invalidated are response-matrix splicing,
closed-cycle-to-current-domain promotion, and boolean-only physical binding.
Open are the Gate-7 background, the interacting current-domain GFHS operator,
full history/nonfermion seam assembly, the global gauge generator and gauge
condition, the physical saddle, HS direction, and Yukawa matrices.

Therefore the milestone is
`FULL_FIELD_ACTION_ATTACHMENT_FRAMEWORK_READY_GFHS_OPERATOR_FAMILY_OPEN`, not
`FULL_FIELD_PHYSICAL_ACTION_DERIVED`. `FULL_BHSM_COMPLETE` remains false.
