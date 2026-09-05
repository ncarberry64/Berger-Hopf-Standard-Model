# Background-covariant GFHS operator family: maximal local derivation and exact blocker

## Result

This sprint does not obtain the global object

\[
\Gamma_{\mathrm{GFHS}}[B;A,c,\bar c,\psi,\bar\psi,H]
\]

on an arbitrary reset-glued BHSM history.  It does obtain the maximal
action-owned regular-current-C2 generating germ and identifies one exact first
source failure:

`ACTION_OWNED_BACKGROUND_AND_FIELD_PARAMETRIC_NONFERMION_RELATIVE_BOUNDARY_GRAPH_THETA_GFHS[B;A,c,cbar,H]_WITH_ITS_FIRST_FIELD_JET`.

The earned status is

`GFHS_OPERATOR_FAMILY_PARTIALLY_DERIVED_NONFERMION_RELATIVE_BOUNDARY_GRAPH_FIRST_FIELD_JET_ABSENT`.

This is more specific than saying that the stratified operator is open.  The
missing object is the graph operator that turns the already available local
gauge, ghost, and HS expressions into one closed reset-glued operator domain.
The zero-field match does not determine its derivative with respect to the
nonzero GFHS fields.

## Source-to-action reconstruction

The reconstruction observes a strict source rule: a response may be used as a
reduction target, but never as the coefficient of a new action.

| Retained object | Classification | Use |
|---|---|---|
| N12 JAX local geometry action | `GENERATING_ACTION_SOURCE` | Already attached in PR #357 |
| Parent Maxwell radial energy form | `GENERATING_ACTION_SOURCE` | Discretized before eliminating the radial field |
| Stored continuous-frequency DtN/residue values | `DERIVED_RESPONSE` | Reduction target only |
| Foundational eta Dirac action | `GENERATING_ACTION_SOURCE` | Canonical free Weyl and representation-connection germ |
| Rank-16 Standard-Model bundle ledger | `STRUCTURAL_PROJECTOR` | U(1), SU(2), and SU(3) generators |
| Local coefficient-free Einstein--Cartan reduction | `GENERATING_ACTION_SOURCE` | Regular-interior HS inverse kernel and unit LR incidences |
| Four-channel heat/HS normalization | `DERIVED_RESPONSE` | Not used as a bare action |
| Common gauge--HS pushforward | `DERIVED_RESPONSE` | Not used as a generating functional |
| AE2 fermion reset graph | `DOMAIN_TERM` | Exact event-to-child fermion trace law |
| AE3 enclosure/family bridge | `TRANSPORT_RULE` | Exact projector/family transport |
| AE4 event-flux assembly | `TRANSPORT_RULE` | Algebraic balance after sector blocks exist |
| Nonfermion relative boundary graph jet | `OPEN_SOURCE` | First global failure |

The old free superdeterminant is therefore not promoted.  Its stored response
matrices do not become coefficients of this action.

## Executable local generating germ

On a regular current-C2 interior chart, the code represents the even action
and the formal odd bilinears as

\[
\Gamma_{\rm germ}
=\Gamma_{\rm even}[B,A,H]
+\bar c\,M_{\rm FP}[B,A]c
+\bar\psi\,D_{\rm GFHS}[B,A,H]\psi .
\]

The transverse gauge coefficient is obtained by assembling the finite-element
radial Maxwell quadratic form and taking its Schur complement.  This ordering
matters: no stored DtN or residue is pasted back into the action.

The fermion operator is

\[
D_{\rm GFHS}=D_{n=0}(B)+\rho_{16}^{\oplus3}(A)
+\sum_{f\in\{u,d,e,\nu\}}H_f I_f .
\]

Here `rho_16` is built from the exact hybrid-bundle hypercharges, Pauli
generators, and Gell-Mann generators.  It is family central.  The free term is
the common representation-central `n=0` Weyl seed.  Distinct frozen Berger
family levels are deliberately not inserted as free masses: doing so would
both rebuild the particle spectrum and break the SU(2) representation before
the Higgs/HS action acts.

The local HS quadratic coefficient is the regular-interior coefficient-free
Einstein--Cartan inverse kernel

\[
G_{\rm EC}^{-1}/K_{G5}=\frac43(1-4\sigma^2),\qquad |\sigma|<\frac12,
\]

with the exact channel multiplicities `(9,9,3,3)`.  Its unit LR incidences are
coefficient placement in an auxiliary-field identity.  They are not physical
Yukawa residues and they do not select a physical Higgs direction.

The four channel amplitudes do not contain a full dynamical Higgs-doublet
realization.  Consequently no gauge--HS kinetic interaction is claimed in
this reduction; the U(1) covariance of each LR incidence is nevertheless
checked exactly.

## Ordered derivatives

The local germ supplies matrix-free directional `S1`, `S2`, `S3`, and `S4`
from this one functional.  JAX differentiates the even scalar and the odd
coefficient matrices.  Odd derivatives use ordered left conventions at the
zero odd background.  In particular,

\[
D_{\bar\psi}D_\psi\Gamma=M_\psi,
\qquad
D_\psi D_{\bar\psi}\Gamma=-M_\psi^{\mathsf T},
\]

and similarly for `cbar,c`.  No ordinary symmetric Hessian is demanded of
Grassmann blocks.  Gauge--fermion and HS--fermion third derivatives are
derivatives of the same `D_GFHS`; they are not manually populated cross
blocks.

Two distinct regular local backgrounds are evaluated.  The even action,
ghost operator, and fermion operator all change.  The mixed derivatives
`D_B D_A Gamma`, `D_B D_H Gamma`, and `D_B D_psibar D_psi Gamma` agree with
direct centered differentiation.  This closes genuine background dependence
for the local germ only.

## Strata and domains

The retained composition is:

\[
\Gamma=\Gamma_{\rm bulk}+\Gamma_{\rm history}+\Gamma_{\rm seam}
+\Gamma_{\rm junction}+\Gamma_{\rm event\text{-}child}
+\Gamma_{\rm boundary}.
\]

Its current ownership is uneven:

- The bulk has an executable local geometry and GFHS germ, but no global
  reset-glued realization.
- The history has the AE2 fermion action/domain and the retained geometry
  history machinery.  It has no common global nonfermion operator domain.
- The independent fermion seam density is exactly zero.  Fermion Green forms
  cancel on the graph of `U_R`.
- The retained junction action is exactly zero.  No junction term is invented.
- The event child inherits the fermion spin/gauge trace and unchanged family
  projectors.  Gauge/ghost/HS inheritance away from zero field is not defined
  by action ownership.
- The boundary contains owned geometry GHY completion and the fermion graph,
  but not the required nonfermion relative graph.

## AE2 to AE4 transport

The executable part of the diagram is

```text
AE2 fermion graph(U_R)
        |
        | U_R tensor I_family, then enclosure restriction
        v
AE3 C2 carrier tensor Spin-G_SM tensor nine frozen family/mode fibers
        |
        | requires Theta_GFHS[B;Phi_SM]
        v
AE4 reset-glued maximal-history GFHS domain
```

`U_R tensor I_family` commutes exactly with every family projector.  Thus the
nine frozen family/mode fibers do not need rebuilding.  The first unavailable
term is not a dimension mismatch; it is

\[
D_{\Phi_{SM}}\Theta_{\rm GFHS}[B;0]
\]

on gauge, ghost, and HS reset traces.

The module supplies an exact nonuniqueness witness.  `Theta_0(phi)=0` and
`Theta_1(phi)=phi P_nonfermion` are both Hermitian, gauge central in the
witness, and projector preserving.  They agree as graph operators at
`phi=0`, but their first field jets and their boundary actions at nonzero
`phi` differ.  Therefore the existing zero-background match cannot select the
nonzero-field domain or its resolvent.

## Event child and Noether/Hamiltonian balance

The inherited AE4 KKT identity gives

\[
\Pi_{parent}+\Pi_{child\ return}+J+C^\dagger\lambda=0.
\]

Contracting it with an anti-Hermitian infinitesimal generator gives the
canonical event Noether-flux identity.  The artifact includes a numerical
algebraic witness with residual near machine zero.  That witness is not a
physical event balance: the physical residual is explicitly `null` because
the nonfermion parent/child blocks depend on the missing `Theta_GFHS`.

Thus the relevant balance is a canonical constraint/Noether boundary flux,
with Hamiltonian interpretation only after the action-selected temporal
generator and complete domain exist.

## Critical reductions

The local construction passes the reductions it is entitled to pass:

1. At zero SM fields, its zero-reference-subtracted contribution vanishes, so
   PR #357's retained geometry action is unchanged.
2. The gauge-only restriction is generated from the discretized parent
   Maxwell form.
3. The fermion-only restriction is the common free Weyl Dirac germ, with no
   Berger level relabelled as a mass.
4. The HS-only restriction is the local regular Einstein--Cartan auxiliary
   action.
5. The fermion+HS restriction contains the action-owned unit LR incidences,
   but not physical Yukawa normalizations.
6. The sigma-zero local enclosure limit exists.
7. The current-C2 family/mode bridge is unchanged.

The full geometry/history/seam reduction, global gauge-only action, physical
Yukawas, and physical event balance remain unavailable for the one exact
domain-source reason above.

## Hindsight 20/20

### VALIDATED

- Maximal regular-current-C2 GFHS generating germ.
- Exact U(1), SU(2), SU(3), family-projector, and LR-incidence algebra.
- Graded local derivatives through fourth order.
- Genuine local background mixed derivatives.
- Fermion/family AE2-to-AE3 transport.
- Algebraic event Noether-flux identity.

### INVALIDATED

- Treating a stored response Hessian as the generating action.
- Treating frozen internal Berger levels as free Standard-Model masses.
- Treating a zero-field boundary match as authority for a nonzero-field
  operator domain.
- Treating local HS unit vertices as physical Yukawas.

### OPEN

Only the first source blocker is retained:

`ACTION_OWNED_BACKGROUND_AND_FIELD_PARAMETRIC_NONFERMION_RELATIVE_BOUNDARY_GRAPH_THETA_GFHS[B;A,c,cbar,H]_WITH_ITS_FIRST_FIELD_JET`.

### EXACT NEXT OBJECT

Derive

\[
D_{\Phi_{SM}}\Theta_{\rm GFHS}[B;0]
\]

on the gauge, ghost, and HS reset traces from the retained bulk variation.
Then insert that graph into the AE4 retarded direct sum and evaluate the
physical event balance residual.  No new numerical campaign is indicated.

## Claim boundary

All of the following remain false:

- `physical_background_bound`
- `physical_HS_direction_derived`
- `physical_yukawas_derived`
- `physical_spectrum_derived`
- `FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND`
- `FULL_BHSM_COMPLETE`
