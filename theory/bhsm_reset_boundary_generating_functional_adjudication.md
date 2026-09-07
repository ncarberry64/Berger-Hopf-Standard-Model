# GFHS reset-boundary generating-functional adjudication

## Outcome

The retained AE4 reset is **incompletely defined** on the action-owned GFHS
boundary phase space. It is therefore not yet possible to classify the full
reset as exact symplectic, symplectic but non-exact, or non-symplectic.

The first missing map component is

`ACTION_OWNED_NONZERO_GAUGE_CONNECTION_TRACE_AE4_RESET_MAP_R_A[B;GAMMA0_A_EVENT]_TO_GAMMA0_A_CHILD`.

Without this configuration-trace map there is no derivative to pull back the
Maxwell symplectic form, no cotangent rule to test on the Maxwell conormal,
and no nonzero BRST-induced ghost map. Consequently
`R_B^* alpha_GFHS-alpha_GFHS` cannot be formed and `S_RESET_GFHS` cannot be
derived.

## Boundary phase space and reduction

The boundary variables separate into four types.

1. The gauge sector has the true canonical pair
   `(Gamma0 A, Gamma1^A A)` after gauge reduction. Its Maxwell Green form is
   nondegenerate on the transverse quotient.
2. The longitudinal gauge, ghost, and antighost data form the graded BRST
   complex. Global gauge zero modes are quotiented. A ghost reset map must be
   induced from the gauge reset map, and the antighost map is its adjoint.
3. The fermion Dirac Green trace space is nondegenerate and already has the
   AE2 unitary reset lift `U_R tensor I3`.
4. The HS trace is algebraic. Since `pi_H=0`, it is a presymplectic null
   direction and is omitted from the reduced symplectic form, while remaining
   an algebraic trace whose nonzero child incidence still requires a rule.

No canonical partner is added for HS. Constraint and BRST-null directions
are quotiented before any canonicality claim.

## Actual reset-map ledger

| Sector | Status | Retained content |
|---|---|---|
| Geometry/background | `DEFINED` | N12 event-child relation and current-C2 bridge |
| Gauge | `MISSING` | only zero trace maps to zero trace |
| Ghost | `BRST_INDUCED` | cannot instantiate until the gauge map exists |
| Antighost | `ADJOINT_INDUCED` | cannot instantiate until the ghost map exists |
| Fermion | `DEFINED` | `Gamma0_c=U_R Gamma0_e`, `Gamma1_c=-U_R Gamma1_e` |
| HS | `STRUCTURAL_ZERO` symplectically | nonzero algebraic trace map remains missing |
| Constraints | `DEFINED` conditionally | AE4 KKT rows consume supplied sector blocks |
| Mixed GFHS | `MISSING` | cannot differentiate a nonexistent gauge map |

The returned `Spin x G_SM` bundle isomorphism class does not cure the gauge
entry: the retained bundle source explicitly states that connection one-forms
are not transported through the pregeometric firewall.

## Canonicality tests

For a unitary trace map `U`, its cotangent lift on `(q,p)` is

\[
R_U=\operatorname{diag}(U,U).
\]

With `alpha=p^dagger dq` and `omega=d alpha`, the executable witness verifies

\[
R_U^\dagger\omega R_U=\omega,
\qquad
R_U^\dagger\alpha R_U=\alpha
\]

for the zero-field gauge identity and the AE2 fermion lift. Their normalized
generating functional is therefore zero on their actual retained scope,
consistent with the independent AE2 fermion seam action being zero.
For the fermion comparison the child outward conormal is first converted to
the common orientation, so the retained law
`Gamma1_child=-U_R Gamma1_event` becomes the cotangent rule
`p_child_common=U_R Gamma1_event`.

The older v15.57 “full Sobolev reset” cannot be used as the missing map. It is
a constant reconstruction to the selected zero SM background and has
`D R=0`. On the nondegenerate Maxwell boundary space this gives

\[
(D R)^\dagger\omega(D R)-\omega=-\omega\ne0.
\]

This disproves its use as a nonzero canonical GFHS reset; it does not prove
that the still-undefined AE4 map is non-symplectic.

The N12 “full reset action Jacobian” is also not the missing map. Its rows are
the geometry constraints, ordered-event row, attachment traces, and geometry
canonical-momentum mismatch. Its event/child state coordinates contain no
GFHS connection trace or Maxwell conormal argument.

The v17.97 result is likewise only an origin statement: it proves that the
homogeneous nonfermion graph contains `(0,0)` and explicitly withholds the
nonzero fluctuation Calderon matrices. The AE4 retarded direct-sum code is an
assembler given sector blocks, not a generator of those blocks.

## Exactness and topology

On the defined reference maps,

\[
\beta=R^*\alpha-\alpha=0,
\qquad S_{\rm reset}=0.
\]

For nonzero GFHS data, `beta` itself is unavailable. Closedness, exactness,
and its cohomology class are therefore not evaluated, and simple connectivity
is not assumed. This is a failure before the topology question, not evidence
for a nontrivial boundary cohomology class.

## BRST and HS consequences

The common-frame zero-background BRST relation remains exact. No independent
ghost or antighost coefficient is introduced. At nonzero field the induced
maps cannot be instantiated because the connection trace map is absent.

The retained action has no independent HS reset term, kinetic boundary term,
or canonical HS mixed boundary coupling. That establishes zero independent
HS symplectic contribution. It does not authorize declaring all HS graph
derivatives zero: a nonzero algebraic child trace or mixed reset interaction
has not been ruled out by an action-owned incidence map.

## Global consequences

`S_RESET_GFHS`, its graph equations, and `D Theta`, `D^2 Theta`, and
`D^3 Theta` remain unavailable. Global S1 exists only on the reference slice;
global S2--S4 remain blocked. The old `Theta_0` and `Theta_1` witnesses are
not discriminated.

The event balance remains decomposed as follows:

- bulk: zero local/algebraic residual;
- canonical reset: unavailable;
- history/seam: zero on the owned AE2 fermion graph;
- event-child: unavailable in nonzero nonfermion sectors;
- constraint/BRST: unavailable beyond the reference relation;
- total: unavailable.

No empirical repair is inserted. Full-field child inheritance is not
promoted, while the fermion lift and nine frozen family/mode fibers remain
unchanged.

## Hindsight 20/20

### VALIDATED

- The boundary phase space and its presymplectic reduction.
- Exact symplecticity and exact one-form preservation of the defined
  reference gauge and AE2 fermion maps.
- BRST/adjoint dependence of ghost/antighost maps.
- Rank-zero HS handling without a manufactured momentum.

### INVALIDATED

- Using the constant v15.57 reconstruction as a nonzero canonical reset.
- Treating the returned bundle isomorphism class as a connection map.
- Treating the v17.97 origin match as a nonzero graph.
- Treating the AE4 assembler as the missing sector map.
- Treating HS presymplectic nullity as selection of every HS graph jet.

### OPEN / EXACT NEXT OBJECT

`ACTION_OWNED_NONZERO_GAUGE_CONNECTION_TRACE_AE4_RESET_MAP_R_A[B;GAMMA0_A_EVENT]_TO_GAMMA0_A_CHILD`.

Derive that incidence from the retained event attachment. Then test its
Maxwell-conormal cotangent lift. Only if it is symplectic is it legitimate to
form `R_A^* alpha-alpha` and attempt to integrate the reset generating
functional.

All physical and Gate-7 promotion flags remain false.
