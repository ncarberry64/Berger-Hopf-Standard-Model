# Relative event–child diffeomorphism generator and charge adjudication

Status: `OUTCOME_D_G4_AND_CHARGE_U_BECAUSE_THE_ACTIVE_RESET_DOMAIN_HAS_NO_VARIED_SPATIAL_ATTACHMENT_ARGUMENT_OR_F_B_DEPENDENT_TRACE_GRAPH`.

This sprint starts after the relative attachment action groupoid and its
fixed-attachment stabilizer have already been derived. It does not repeat
tensorial covariance. Its only question is whether the retained BHSM action
defines a differentiable relative spatial-diffeomorphism generator and its
event/child charge.

## 1. Presymplectic potential inventory

The repository contains the following sectorwise action information.

| Sector | Action-owned boundary information | Missing on the reset domain |
|---|---|---|
| Einstein geometry | EH plus capwise GHY fixes the regular Dirichlet metric pair | no varied reset attachment or complete event/child reset potential |
| support scalar | `Theta_D^A=-sqrt(-G) partial^A q_D delta q_D` | scalar ensemble is unselected; complete support/core potential absent |
| eta/sigma/topographic | reduced Legendre momenta exist | no single coupled reset symplectic form |
| Maxwell | weighted conormal Green form | Green form does not select the relative trace graph |
| FP ghost/antighost | cross-Green form and BRST relation | common graph value and moving graph variation unselected |
| Dirac | AE2 maximal-isotropic trace graph cancels opposite Green forms | the graph contains `U_R` but no spatial `F_B` pullback |
| HS | algebraic normal momentum and Green form are zero | zero supplies no graph selection or spatial generator |
| algebraic attachment | new potential, momentum, and flux are zero | it inherits unspecified trace/pullback maps |
| compatibility multipliers | no kinetic term | no relative canonical generator |
| AE4 | future-retarded parent/child trace space | no boundary functional or spatial action |
| Galerkin restriction | finite-mode restriction of owned forms | no moving-basis/projector law tied to `F_B` |

The AE3 enclosure result does not fill this table. Its Brown–York/GHY
cancellation is for a smooth internal level set in one spacetime, and its own
ledger says that level set is not the reset locus. Likewise the v15.12
Hayward term fixes a gravitational corner pair but does not select the matter
or core transfer graph.

Therefore neither `Theta_e` nor `Theta_c` exists as a complete full-field
potential on the event–child reset domain, and their relative combination
cannot be formed. Ordinary shifts of a completed potential by a coherent
field-space exact term would be conventional. The missing trace graph and
boundary polarization are different: they change the variational domain and
are unresolved choices. Selecting either by hand would add physical input.

## 2. Infinitesimal relative transformation

Linearizing

\[
 F' = \phi_c\circ F\circ\phi_e^{-1}
\]

gives the vector along the space of attachments

\[
 \delta_\xi F=\xi_c\circ F-F_*\xi_e.
\]

The stabilizer algebra is exactly

\[
 \xi_c\circ F=F_*\xi_e,
\]

for which `delta F=0`. A genuine relative direction has nonzero right-hand
side. Metrics, measures, scalars, curvature, connections, spinors, canonical
coordinates, and momenta receive their standard Lie/spin/cotangent-lift
variations. For a connection,

\[
 \mathcal L_\xi A=\iota_\xi F_A+D_A(\iota_\xi A),
\]

where the last term must remain distinguished from the independent internal
gauge action.

If the reset trace were spatially typed, its schematic relation would be

\[
 T_F=F^*\Gamma_cX_c-U_R\Gamma_eX_e=0,
\]

and its moving-domain variation would contain

\[
 \delta(F^*q_c)=F^*\left(\delta q_c+
 \mathcal L_{\delta F\circ F^{-1}}q_c\right).
\]

The executable AE2 graph is instead only
`Gamma0_child(Psi)=U_R Gamma0_event(Psi)`. The nonfermion moving graph is
also incomplete. Consequently `delta_xi` is not a tangent vector on the
active reset domain. A two-dimensional finite-difference witness verifies
the formula for `delta F` and equivariance of the hypothetical `F`-dependent
trace, but is explicitly not promoted into BHSM.

## 3. Candidate Hamiltonian and differentiability

The desired generator would satisfy

\[
 \delta H_\xi^{\rm rel}=\Omega_{\rm reset}(\delta X,\delta_\xi X)
\]

and, after integration by parts, have separate event and child contributions,

\[
 \delta H_\xi^{\rm rel}=
 \sum_{s=e,c}\left[C_s[\xi_s]+
 \int_{\partial\Sigma_s}(\delta Q_{\xi_s}
 -\iota_{\xi_s}\Theta_s)\right]-\delta B_\xi^{\rm rel}.
\]

BHSM owns sectorwise bulk constraints, but the chain fails before this
expression becomes a functional differential:

1. `F_B` is not a varied configuration argument.
2. The full-field reset graph has no `F_B` dependence or first moving-domain
   variation.
3. Hence `delta_xi` is not tangent-defined on the reset domain.
4. Hence `Omega(delta,delta_xi)` cannot be evaluated.
5. Only after those steps could the complete `Theta_s`, charge assemblers,
   and boundary ensemble/counterterm be tested.

The present differentiability class is therefore **G4**. This is stronger
than saying that a counterterm has not been tried: there is no candidate
generator on the current domain to improve. Once a moving graph exists, the
unselected boundary ensemble may create a later G3 choice, but that stage has
not been reached.

## 4. Independence proof

The missing graph is not a routine calculation hidden in the bulk action.
The existing nonfermion audit constructs two first graph jets that:

- agree at the zero-field graph;
- are maximal isotropic;
- cancel every tested fixed-field vertical boundary variation;
- obey the retained BRST compatibility relations;
- nevertheless give different hypothetical boundary potentials.

Separately, the coefficient-locked GHY/Hayward gravity construction allows a
continuous unitary family of self-adjoint matter transfer graphs with
inequivalent conservative spectra. Its ledger explicitly states that the
matter/core domain is not selected. The canonical provenance table also
records the seam embedding with no action-owned momentum and
`VARIABLE_EMBEDDING_ABSENT_FROM_ACTIVE_ACTION`.

These counterexamples prove that bulk covariance, Green isotropy,
self-adjointness, BRST compatibility, and the gravitational corner term do
not determine the required moving trace graph. It is independent domain
data, not an omitted algebraic manipulation.

## 5. Charges and gauge kernel

Because no differentiable generator exists on the current domain,

\[
 Q_e=\text{undefined},\qquad
 Q_c=\text{undefined},\qquad
 Q_{\rm rel}=\text{undefined}.
\]

The charge classification is **U**, not Z. Neither zero charge nor
equal-and-opposite cancellation is inferred. No charge kernel or gauge group
is derived. The fixed-`F` stabilizer is the kernel of the kinematic map
`(xi_e,xi_c) -> delta F`; it is not thereby the kernel of an undefined
Hamiltonian charge.

## 6. Hopf rotor and Noether constraints

The positive-energy Hopf rotor is a bulk collective parent/child relative
rotation satisfying `J_child+J_parent=0`. Its positive
`J^2/(2 I_rel)` energy survives the compact momentum constraint. No owned map
identifies its rotor angle or Killing field with `delta F` on the reset trace
domain. It therefore remains an adversarial obstruction to quotienting all
relative Hopf motion, but it is not the missing attachment boundary charge.

The N12 endpoint-fixed radial Ward identity is likewise an owned within-side
identity generated by the radial momentum constraint and completed by the
eta clock current. Its generator vanishes at the radial endpoints and does
not move `F_B`. Neither it nor the compact total-momentum constraint supplies
a relative event–child Noether identity. The existing executable constraint
algebra therefore does not generate attachment motion.

## 7. Outcome and downstream consequence

Outcome **D** remains, now at a strictly sharper boundary. A, B, and C cannot
be distinguished because the proposed relative transformation is not a
vector field on the active variational domain. No BRST extension, gauge
kernel, identity fixing, reduced reset, connection/curvature quotient,
`beta`, generator propagation, or global S1–S4 construction is earned.

## Hindsight ledger

### VALIDATED

- the infinitesimal two-sided formula and stabilizer condition;
- the complete sectorwise potential/Green-form inventory;
- absence of complete `Theta_e`, `Theta_c`, and relative `Theta`;
- absence of `F_B` as a varied action argument;
- G4 differentiability and U charge classification;
- independence of the missing moving graph;
- Outcome D at the sharper domain-tangency boundary.

### INVALIDATED

- assembling a complete potential from disconnected sectorwise forms;
- using smooth-enclosure GHY cancellation at the reset;
- using the Hayward corner pair to select the GFHS graph;
- treating AE4 causality as a spatial attachment action;
- relabeling the radial Ward identity as an attachment generator;
- relabeling Hopf rotor energy as `Q_rel`;
- cancelling undefined event and child charges;
- adding a relative ghost or selecting an ensemble to force zero charge.

### REDUNDANT

- objectwise covariance proofs;
- recomputation of the Hopf rotor;
- repetition of the finite orbit/stabilizer audit.

### OPEN

`ACTION_OWNED_F_B_DEPENDENT_FULL_FIELD_RESET_TRACE_GRAPH_WITH_FIRST_MOVING_DOMAIN_VARIATION_ABSENT`

### DECISION POWER

The formal infinitesimal formula alone has no A/B/C/D decision power. The
absence and demonstrated nonuniqueness of the moving trace graph have direct
decision power: they force G4, charge U, and Outcome D. The Hopf rotor rules
out a blanket Hopf quotient but cannot distinguish B, C, or D for `F_B`.
The within-side radial Ward identity has no attachment decision power.

### EXACT NEXT OBJECT

`ACTION_OWNED_F_B_DEPENDENT_FULL_FIELD_RESET_TRACE_GRAPH_WITH_FIRST_MOVING_DOMAIN_VARIATION_ABSENT`

This object must place `F_B` in the variational domain, specify the spatial
pullback for every participating trace sector, and define the first variation
of that graph under `delta F`. Only then can the complete relative potential
be assembled, the boundary ensemble tested, and `Q_e`, `Q_c`, and `Q_rel`
classified as Z, K, or N.
