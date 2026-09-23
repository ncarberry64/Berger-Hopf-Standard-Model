# Cross-scale child closure with interaction-specific transitions

Status: `CANDIDATE_CROSS_SCALE_CHILD_CLOSURE_ARCHITECTURE`.

Owner hypothesis integrated on 23 September 2026 against authoritative branch
`codex/g7-vector-endpoint-final-closure`, source checkpoint
`91630d922ce661457f1d59ed3acd098804efd446`.

BHSM can support this as a common **conditional architecture**, using its
existing admissibility, reset, boundary-domain and constrained-response
objects. It does not yet supply a single action-derived physical realization
across all the scales below. This is the proposed conceptual keystone:

> Rigidity follows coherent child closure, not constituent count, subject to
> the action-derived response conditions. Closure, competition and transition
> dynamics are distinct. The same architecture does not mean the same interaction.

Here “follows” is a proposed organizing principle, not unconditional response
monotonicity. Coherence alone does not prove a small susceptibility. A child
may keep its identity, respond strongly to its environment, and have either
few or many available transition channels.

No action term, physical selector, closure scalar, fitted threshold, numerical
prediction or gate criterion is added. The current full-history physical
inequalities remain **FAIL TO CERTIFY / UNKNOWN**; Gate 7 remains open and
`FULL_BHSM_COMPLETE = FALSE`. Existing frozen predictions and all prior verdicts
are preserved. The numerical critical path remains in
[the current reproduction guide](../docs/GATE7_CURRENT_REPRODUCTION.md).

## THEOREM-LEVEL EXISTING BHSM

The following are inherited results with their original assumptions and scope.
The environmental postulate itself is owner physics; its consequences and
counterexamples must not be presented as a derivation of that postulate.

| Authority | Existing result | Limit preserved here |
|---|---|---|
| [Environmental child compatibility](bhsm_environmental_child_compatibility_selection.md) | E5 filters the conditional family by typed support, invariants, scale, boundary constraints and causality; incompatible structures are excluded | The support principle is recovered owner physics. `SUPPORTED`, `EXCLUDED` and `UNRESOLVED` remain distinct; E5 does not choose a member within a supported sector |
| [Reset-selector recovery](bhsm_environment_conditioned_reset_selector_recovery.md) | Conditional N=3 reconstruction is locally determined after its required event/boundary inputs are supplied; the N12 fixed-event block has rank 31 in 98 variables | N12 has a 67-dimensional fiber, or 66 after the existing time quotient. These are state-fiber dimensions, not 67 or 66 decay channels. The full-field selector is absent |
| [Finite local encapsulation](n12_finite_encapsulation_local_branch.md) | The desingularized retained flow gives local finite-positive-time formation, a nonempty event-to-complete-child relation and certified positive-duration child persistence | No globally unique child, universal reachability, post-event return or global stability is established |
| [Formation/decay chronology](n12_gate7_formation_decay_chronology_supersession.md) | Formation precedes the event and reset; child evolution follows. The retained maximal exterior allows a later event, canonical domain exit or infinite end under its existing endpoint rules | “Decay/evolution” is a chronology label, not a proof of a particle decay width or a requirement to hit another event |
| [Response representation](bhsm_encapsulation_response_representation_theorem.md) | At fixed owned domains and actual stabilizer, covariant response jets are graded intertwiners; canonical compatibility restricts them | RSP5 operator/function freedom remains; representation allowance is not a nonzero transition amplitude |
| [Collective response](bhsm_collective_encapsulation_response_candidate.md) | Constrained KKT response, energy-norm restriction inequality, reducing-subspace ordinary-norm inequality and the exact changed-interaction identity | Ordinary-norm susceptibility can increase under tangent restriction. No monotonic law in constituent number, universal pair rigidity or derived Cooper pairing |
| [Fixed-history state nonuniqueness](ae31_c2_fixed_history_state_nonuniqueness.md) | A continuous family of pure Hadamard covariances survives fixed history and unitary reset transport | History selection and boundary transport do not select a unique quantum state |
| [Complete channel ledger](universal_complete_channel_ledger.md) and [phase-space engine](../src/bhsm/interface/universal_decay_collision.py) | Conditional channel/threshold/amplitude classification and two-, three- and multibody phase-space readouts are implemented | Physical stability or widths require a complete same-action spectrum, selection rules, amplitudes and background. Infrastructure is not a promoted BHSM prediction |

The older [full-field attachment audit](bhsm_current_full_field_action_attachment.md)
also separates the 98-variable local geometry oracle from a physical
gauge/fermion/scalar amplitude engine. Later sector calculations below are
real progress within their scopes; none cited here provides a completed
cross-scale child operator. The inherited E5, RSP5, F4/L4/D4/G4, charge-class U
and Outcome D verdicts are not changed by this note.

## OWNER-SUPPLIED PHYSICAL HYPOTHESIS

### 1. Typed action and child space

Use the existing environmental descriptor

```text
E_s = (alpha_s, tau_s, I_s, Lambda_s, B_s).
```

Its entries retain their existing structure-stratum, event-class, transported
invariant, scale and boundary/Noether meanings. `tau_s` is a scenario label,
not a time coordinate. Write `A_scale` for the **action together with its
owned fields, operator domains, constraints, boundary ensemble, physical
quotient and any derived effective-scale map**. It is not an adjustable force
or a freely chosen scale-dependent matrix. The provisional S8, relative
two-cap S5|4 and intrinsic S4 descriptions still need their explicit
compatibility maps. A metric or time flow is not extended onto the
pregeometric C_A stratum by notation.

For a supplied event `X_e`, use `R_A(X_e)` as shorthand in this note for the
existing set-valued reset/child relation. Its points include the boundary
attachment/correspondence `(F_B,L_s)` and child data solving the retained
constraints and reconstruction equations. This name adds no reset map.
Define the retained, not-excluded family

```text
C_ret(X_e,E_s;A_scale)
  = { [X_c] : (X_e,X_c) belongs to R_A,
              Compatibility(E_s,R(X_c)) != EXCLUDED }.
C_sup = { [X_c] in C_ret : Compatibility(E_s,R(X_c)) = SUPPORTED }.
```

`R(X_c)` is the existing child requirement signature. Brackets identify only
the equivalences actually owned by the physical quotient; an arbitrary
choice of representative is not a selector. `C_sup` and the unresolved part
of `C_ret` must be reported separately. A necessary condition that is not yet
evaluated does not certify admissibility or dynamical access.

The user's `C(X,E;A_scale)` denotes this typed child family, with its evidence
partition retained. Away from a reset event, extension to particle or
many-body descendants requires an action-derived transition relation at that
scale. It is a candidate extension, not a claim that every atomic excitation
or scattering event uses the N12 topological reset.

### 2. Child identity and closure

Separate a physical child **sector** C from an individual state `x` in it.
Let `M_C(E_s;A_scale)` be the states on its action-owned domain satisfying
the retained constraint surface, boundary relation, environment compatibility
and declared identity data. Identity data may include topology, incidence,
spin/bundle class, conserved labels and constituent organization, but only
where the relevant physical sector map is actually defined. Do not quotient
away physical state or multiplicity directions to create uniqueness.

Closure has three tests, rather than one phenomenological scalar:

1. **Admissible closure:** `x` belongs to `M_C`, all its required support
   predicates are established and the boundary/constraint equations hold.
2. **Dynamical persistence on a stated interval:** the actual evolution with
   the prescribed environment remains in the same identity sector on that
   interval, allowing changes of its continuous state. Existence, domain
   preservation and constraint propagation are required.
3. **Robust or exact dynamical closure:** persistence holds for the declared
   physical perturbation class, or the child subspace is invariant under the
   full dynamics, respectively. Either claim needs its own proof and domain.

For regular classical flow `Phi_A(t,t0)` the second test is

```text
Phi_A(t,t0)x in M_C(E_s(t);A_scale), for every t in the certified interval.
```

At a regular constrained background, the inherited physical perturbation
space is `ker D C_constraints / residual gauge`, with the owned norm and
boundary-domain restrictions. Rank changes require stratum-specific analysis.
For quantum physics one instead needs the physical Hilbert/state space and
evolution; an invariant child subspace is a possible exact counterpart, not
currently a universal BHSM construction. Thermal or open-system closure must
specify the enlarged environment or reduced generator and observation time.

A stable identity need not be a fixed state, an isolated system, a unique
covariance, or a rigid object. Conservation-compatible exchange can occur
within a persistent child. A positive constrained static Hessian is local
information and is not by itself a global, quantum or dynamical closure proof.

### 3. Competing child channels and their transitions

Where an owned sector map exists, group physically equivalent descendant
descriptions into channel sectors `C_alpha`. Define `B_C` as the resulting
**labelled transition relation**, recording each candidate target, its
support/kinematic status, selector status and dynamical evidence. It is not a
scalar branching score. Continuous states inside one sector remain a fiber;
they are not automatically distinct daughter channels.

Competition means at least two physically inequivalent descendants survive
the stated kinematic/dynamical checks and are not eliminated by the physical
selector. Report whether this is verified dynamic competition, kinematic
competition awaiting an operator, or merely unresolved candidate multiplicity.
In classical dynamics, several outcomes for nearby initial states need not
mean more than one outcome for a fully specified deterministic initial state.

In a quantum realization, the appropriate objects can be channel amplitudes
and their probabilities. A classical single-valued reset selector cannot be
silently substituted for a Born-rule or measurement/state-selection law.
Where mutually orthogonal channel projectors and an action-derived transition
operator exist, the schematic blocks are

```text
T_beta,alpha = P_beta T[A_scale] P_alpha.
```

This formula requires a common physical domain and a definition of `T`
(evolution, scattering or effective transition operator). For classical or
stratified systems use the actual flow/transition correspondence instead.
Different sectors may share field couplings; a full action need not split
into independent commuting force operators. Neither kinematic permission
nor a nonzero formal vertex alone proves a finite physical transition rate.

### 4. Child paths and decay

The candidate path is a hybrid/stratified concatenation

```text
parent flow -> owned event -> admissible child fiber
            -> physically realized child -> within-child evolution
            -> next owned event, canonical exit, or maximal continuation.
```

An individual path includes a choice of fiber member; the mathematics of a
set-valued relation alone does not explain that physical choice. Between
events the flow must solve the appropriate action equations. Across events
the traces must satisfy the existing relation, boundary balance and support
predicates. Infinite event sequences need additional continuation and
accumulation control. The local N12 formation/reset/persistence arrows are
inherited; global path selection, cross-scale matching and eventual return
are open. No finite proof cutoff is made into a physical event.

The proposed wording, “decay occurs when the current child no longer remains
admissibly closed and another allowed channel is followed,” needs a precise
qualification. **Loss of instantaneous admissibility is not necessary for
decay.** A metastable local branch may remain a valid configuration while
the full dynamics permits escape or quantum leakage. Losing a chart, a
coercivity estimate or a proof certificate is not evidence of decay either.

The usable candidate definition is: decay is a realized loss of the parent's
declared persistent identity through a dynamically accessible, compatible
daughter channel of the full action. When applicable, a nonzero inclusive
width quantifies that loss. This must be distinguished from reversible
excitation, identity-preserving exchange, and an unobserved candidate channel.
One nonzero accessible daughter channel is sufficient; multiple descendants
are not necessary. Daughters need not be stable: cascades can continue.
Environmental stress may activate a channel, but spontaneous decay does not
require a changing environment or a newly opened channel at the decay time.

This interpretation agrees conditionally with the existing complete-channel
ledger. It does not replace that ledger's amplitude, spectrum, completeness
and threshold requirements, or relabel all post-reset “decay/evolution” as
particle instability.

## NEW CONDITIONAL DERIVATIONS

These deductions formalize the hypothesis under explicit assumptions. They
are not additional BHSM physical laws or promoted sector predictions.

### 5. Invariance, escape and quantum closure

**Classical regular stratum.** Let constraints `c(x,E(t))=0` define an embedded
smooth manifold of constant rank, let the prescribed environment be smooth,
and let `xdot=f_A(x,E(t))` be locally Lipschitz with locally unique solutions.
If throughout the relevant manifold

```text
D_x c f_A + D_E c Edot = 0,
```

then the extended vector field is tangent and solutions starting there remain
there locally, while they exist in the owned domain. This follows by the
restricted vector field and uniqueness. Sector-boundary inequalities require
inward viability conditions as well; checking tangency at one point is
insufficient. Noncompact escape, collisions, rank changes or a domain boundary
can invalidate continuation. This is a closure criterion, not a theorem of
eternal child stability or a selector for the next child.

**Quantum exact subspace.** Assume a self-adjoint Hamiltonian H on a supplied
physical Hilbert space and an orthogonal child projector P that reduces H
(including its domain, equivalently commuting with its spectral measure).
Then `U(t)P = P U(t)`, and `||(1-P)U(t)psi||=0` for `psi` in `ran P`.
That proves exact no-leakage closure. Conversely, invariance for all positive
and negative times implies reduction. A formal commutator on an unspecified
core is not sufficient. For normalized `psi` in `ran P` and `D(H)`,

```text
||(1-P)U(t)psi||^2
    = t^2 ||(1-P)H psi||^2 / hbar^2 + o(t^2).
```

Thus a nonzero block can cause short-time leakage while the parent remains
kinematically admissible. Leakage alone can be reversible oscillation; a
decay width needs the continuum, state preparation and appropriate resonance
or long-time/weak-coupling analysis. H is not assumed to be the static Hessian.

### 6. Susceptibility is independent of branch multiplicity

On a regular stationary branch use the existing constrained Lagrangian
`L=S+lambda.c`, physical tangent injection Q and environmental forcing B:

```text
H_C = Q* L_XX Q,       B_C^force = -Q* L_XE,
S_C = D_E X_C = Q H_C^(-1) B_C^force.
```

The superscript distinguishes the forcing block from branching structure
`B_C`. This expression assumes environment-independent constraints and a
valid inverse on the physical domain. For environment-dependent constraints
differentiate the full bordered KKT system with the `c_E` term, as in the
[collective response authority](bhsm_collective_encapsulation_response_candidate.md).
Constraint curvature and non-gauge zero modes cannot be discarded.

Report the response kernel, singular values and physical/environmental norms,
and the relevant constrained spectrum. “High” and “low” below are comparative
within a declared normalization and observation regime, not new thresholds.

| Within-child response | Few/no outgoing verified channels | Several verified competing channels |
|---|---|---|
| High rigidity / small susceptibility | A persistent stiff child is possible; global stability still needs channel completeness | A locally stiff but metastable child is possible; outgoing amplitudes/barriers determine escape |
| Low rigidity / large susceptibility | A deformable identity can persist with no available decay channel | Strong deformation can coexist with exchange, escape or competing decay outcomes |

No implication runs from one column to the other. A local stationary branch
can retain exactly the same action germ, tangent Hessian and environmental
forcing while the action is changed outside its neighborhood to add a distant
well or escape route. Hence the local response cannot determine the global
branch relation. This is a mathematical counterexample construction, not a
permitted alteration of the BHSM action. Quantum access to that route still
depends on the full barrier/operator.

Likewise, let H be positive definite on V and J isometrically include W in V,
with the same forcing B. The restricted response

```text
S_W = J (J* H J)^(-1) J* B
```

is the H-orthogonal projection of `S_V=H^(-1)B`. Its energy norm is no larger.
Its ordinary physical norm is no larger under the additional condition that
the physical orthogonal projector onto W commutes with H. Without that
condition the existing exact example `H=[[1,2],[2,5]], B=[2;5], W=span(e1)`
increases ordinary susceptibility from 1 to 2. Changed interaction/forcing
requires the complete response comparison already derived in the authority.
Adding constituents does not even establish `W subset V`.

### 7. Constraint restriction is not child selection

At fixed parent, environment and ambient domains, adding an actual compatible
constraint gives `C_sup,new subseteq C_sup,old`. At a regular finite-dimensional
point its tangent codimension increases by the independent added rank. This
is set restriction and the rank theorem, not evidence that the new set is
nonempty, connected or a singleton. Constraints may split connected branches;
changing the interaction or field domain need not be a pure restriction.

Even one surviving sector can contain a continuous state fiber. The N12
67-dimensional fixed-event fiber and fixed-history Hadamard family demonstrate
why representation closure, branch count, state selection and actualization
must be recorded separately. Existing quotient constraints are counted once.

## OPEN PHYSICAL DERIVATIONS

### 8. A single particle and a coherent pair

**Single stable particle:** the proposed child is a declared identity sector
with persistent local closure. BHSM would need a physical state, spectrum,
environmental vertex and exhaustive outgoing-channel analysis. Identity
stability does not prohibit large position, polarization or other response.
The one-particle example does not supply the missing BHSM state selector.

**Coherent pair `C_12`:** a joint state and action-derived interaction can
replace independently variable constituent responses with a constrained
collective response. Establish the physical quotient, shared domain, Hessian,
forcing and one of the sufficient response inequalities above before claiming
reduced response. Relative/collective modes can soften or remain responsive.
The result is conditional; no universal pair rigidity or Cooper-pair physics
is derived.

### 9. Generic three-body systems and a candidate competition envelope

`C_12|3`, `C_13|2`, `C_23|1` and `C_123` are candidate organization labels,
not four automatically distinct allowed children. Define their boundaries
from the actual action, binding/escape criteria, conserved quantities,
environment and time window. Account for identical-particle equivalences.
Hierarchical binding and long-lived collective configurations are allowed.

A precise set-valued replacement for the proposed “decay envelope” is the
set of initial/environment data for which a declared admissible perturbation
family reaches at least two distinct channel sectors, with no certified
single invariant child covering that family on the declared interval.
The reachable-set map, perturbation family and sector classifier must all be
specified. With missing dynamics this is only an unresolved envelope, not a
certified physical region. No meaning of “dominates” is invented without an
owned probability, basin or selection rule. Prefer “competing-child envelope”
until actual decay is established.

| Proposed outcome | Required dynamical evidence |
|---|---|
| Exchange | Change of bound-subsystem identity along a constraint-compatible trajectory |
| Ejection | Escape criterion, energy/flux balance and outward continuation; a positive instantaneous pair energy alone is insufficient |
| Merger | An owned collision/finite-size/relativistic continuation and loss channels where needed; point-particle singularity is not a merger law |
| Capture | Entry into a persistent bound sector with energy/angular-momentum transfer accounted for; a third body or radiation may carry the balance |
| Temporary hierarchical binding | A hierarchical sector retained over an explicitly finite interval, with a later exit or unproved long-time status |
| Sensitive dependence | Growth of the physical variational flow in a declared norm/time regime; channel multiplicity alone supplies no Lyapunov or chaos result |

Several basins can coexist without sensitive dependence, and sensitive
dependence can occur inside one identity sector. A complete classical initial
state can have a unique trajectory despite nearby competing outcomes. This
does not solve generic three-body dynamics and does not make them generically
unsolvable. Nothing here assigns their evolution to an electroweak operator.

### 10. Three quarks: gauge-compatible collective child

The standard comparison is SU(3) color with quarks in the fundamental,
gluons in the adjoint, non-Abelian field strength, and color-singlet hadrons.
These are external physics inputs, not new BHSM derivations; see
[PDG QCD, section 9.1](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-qcd.pdf).

For three fundamental color factors, the algebraic decomposition is

```text
3 tensor 3 = 6 direct-sum 3bar,
3 tensor 3 tensor 3 = 10 direct-sum 8 direct-sum 8 direct-sum 1.
```

The invariant tensor satisfies
`epsilon_abc U^a_d U^b_e U^c_f = det(U) epsilon_def = epsilon_def`.
Consequently the epsilon contraction is a singlet intertwiner; there is one
color singlet in this three-factor tensor product. The color part of different
pair-first couplings to that singlet need not define different physical
children. They can be alternative descriptions of the same invariant color
line. A separated pair is not thereby an independent color-neutral child.
This is a representation-theoretic conditional deduction, not confinement.

A local baryon interpolating operator can schematically contract
`epsilon_abc q^a q^b q^c`, with appropriate spin/flavor/fermionic structure.
Separated fields require gauge transport to a common point or an equivalent
gauge-invariant construction. The candidate BHSM child therefore includes
the gauge field and boundary flux data, not just three independent positions:

```text
(q,q,q,A_color; Gauss/BRST domain, physical boundary data) -> C_baryon.
```

The BHSM reuse is concrete but limited. The inherited representation/BRST
and response-intertwiner framework can enforce a singlet incidence rule on
an owned physical carrier. The
[current-C2 quark LR calculation](ae31_c2_quark_gauge_lr_channel_ray.md)
already uses color Casimir `4/3` and obtains
`K_LR=2 G_C2 diag(7/5,13/10)`. That is a specific quark bilinear exchange
kernel with a common nonlocal geometry factor. It is not a three-quark
bound-state operator, a baryon pole, or a confinement certificate. Its stated
absolute-coupling, Higgs-direction and residue limitations remain intact.

To earn **gauge-enforced collective child closure**, BHSM must attach its
color constraints and non-Abelian interactions to the same physical child
domain, construct a gauge-invariant baryon state/correlator, and demonstrate
the relevant spectral pole/binding and allowed daughter channels. The local
Gauss constraint and global singlet condition must not be conflated; neither
alone implies binding or confinement. Boundary flux sectors matter. The
one-dimensional color invariant does not fix spatial, spin, flavor, gluonic
or quantum-state multiplicities. Higher Fock components and color-neutral
multihadron channels are not excluded by that algebra.

This is the decisive counterexample to a constituent-count rule: three
constituents are compatible with a collective invariant sector. It remains
open whether BHSM derives the required dynamical closure. A baryon can be
closed against particular strong channels while remaining unstable under
other interactions; color neutrality is not universal stability.

### 11. Electroweak decay as an interaction-specific transition

The external SM comparison is the charged-current structure, schematically
`L_CC = -(g2/sqrt(2)) W_mu^+ (ubar_L gamma^mu V d_L
+ nubar_L gamma^mu ell_L) + h.c.`, with conventions and the relevant family
bases specified. The weak vertices plus kinematics and physical external
states determine possible transitions; they are not a universal three-body
force. See [PDG electroweak model, section 10.1](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-standard-model.pdf).

BHSM already records the
[charged-current coefficient form](../docs/weak_charged_current_coefficient_form.md)
`g2_BH/sqrt(2)` while distinguishing it from a derived coupling value.
Its [current-C2 gauge/ghost Hessian](ae3_c2_lorentzian_gauge_ghost_hessian.md)
and [photon symbol audit](ae3_c2_photon_symbol_audit.md) retain the local
Maxwell-residue obstruction; a nonlocal DtN form factor cannot be substituted
for a physical local electroweak coupling. The full-field attachment and
state-selection gaps also remain.

The proposed realization is therefore parent dynamical nonclosure under the
full action, compatible daughter channels, an action-derived amplitude,
and daughter evolution. It need not involve a newly lost static minimum or
newly opened kinematic threshold. BHSM must calculate the same-action
vertices/propagators, physical masses and residues, flavor projectors, phase
space and total/inclusive rates through its existing channel/decay engines.
Off-shell mediation requires the full amplitude, not a direct nonzero
Hamiltonian matrix element guessed from constituent count. Descendants may
subsequently decay. No weak width, CKM/PMNS value or physical coupling is
promoted by this interpretation.

### 12. Electromagnetic, atomic, molecular and lattice closure

Atoms, molecules and lattices are candidate higher-order child sectors if
their bound/collective states and environment coupling follow from the owned
effective action and scale map. Calculate electronic and vibrational spectra,
ionization/dissociation thresholds, response operators and allowed radiative
or material transition channels. For a lattice include phonon/elastic modes,
boundary conditions, defects and thermal state where relevant.

The existing constrained-response formalism supplies the calculation template,
not those many-body solutions. Translation, acoustic and gauge zero modes
must be handled explicitly; a uniform positive gap cannot be assumed for an
extended system. Coherence can suppress some independent responses while
enhancing a collective one. There is no monotonic rigidity law in particle
count and no automatic transfer of the current-C2 gauge kernel to atomic QED.

### 13. Gravitational and cosmic realization

For binaries, hierarchical triples and bound clusters, define the child
sector using the appropriate gravitational action, matter model, boundary
conditions and physical perturbations. Exchange/ejection use the channel
tests in section 9. Merger requires the appropriate spacetime/material
continuation and flux accounting; fragmentation requires actual unstable
modes and nonlinear development. Persistence of large-scale structure is
relative to the evolving environment and observation regime.

The BHSM reset geometry is not yet a derived map to Newtonian N-body dynamics,
relativistic compact-object merger or cosmological structure formation. Each
needs a justified effective limit and its own domain/observable correspondence.
Radiation, matter and expansion cannot be inserted as unspecified selectors.
This is a possible reuse of admissibility/closure/competition architecture;
gravity remains a different interaction from QCD and electroweak physics.

### 14. Falsifiable distinctions and calculation obligations

The categories overlap: a gauge-enforced or many-body child can be stable,
metastable or environmentally disrupted. State the environment, domain,
perturbation class, conserved labels, resolution and time regime before testing.

| Candidate category | What BHSM must calculate | Observation or mathematical result that would defeat the stated classification |
|---|---|---|
| Stable child | Owned persistent identity and dynamics; complete outgoing spectrum/channel ledger with all accessible widths zero or forbidden; appropriate classical invariance when applicable | One verified identity-changing accessible transition with nonzero rate defeats exact stability; finite non-observation only bounds a lifetime |
| Metastable child | A persistent local branch/quasibound state plus an accessible escape mechanism, resonance/width or first-exit law under stated conditions | Exact invariant-subspace proof excludes the proposed leakage; a proposed lifetime incompatible with independently compared data rejects that quantitative realization |
| Competing-child envelope | Sector classifier and reachable-set/basin or quantum channel map, with at least two verified distinct outcomes and selector status | Exhaustion proves only one reachable sector on the declared family, or purported alternatives are gauge/basis copies |
| Gauge-enforced collective child | Independent Gauss/BRST and boundary constraints, singlet intertwiners, gauge-invariant state/correlator and dynamical binding/persistence | No nonempty physical bound sector on the claimed domain, or the alleged closure depends on unphysical gauge representatives; an allowed other-interaction decay refutes only full stability |
| Higher-order many-body collective child | Actual many-body state, constrained Hessian/operator spectrum, forcing and shared response in compatible norms; dissociation/fragmentation/collective channels | The proposed response inequality fails, soft modes reverse it, or no persistent collective sector exists in the claimed regime |

For every row report branch count or dimension only where the quotient and
sector map justify it; separate selector uniqueness from sector uniqueness.
Report gaps/signatures only for the relevant physical operator with zero modes
and domain stated. Conservation/gauge compatibility excludes channels but
does not assign rates. Measured spectra, responses or lifetimes are later
comparisons, never inputs used to choose an upstream BHSM branch or coefficient.

The abstract architecture alone predicts no unique numerical value and is
not independently confirmed by redescribing known systems. It becomes
physically testable only when BHSM derives a specific exclusion, response
inequality, spectrum or rate with fixed action-owned inputs. A failed sector
realization must be reported as such, not rescued by redefining “child.”

## Optional Gate-7 connection: existing map only

There is already an explicit mathematical reuse in
[collective response, section 6](bhsm_collective_encapsulation_response_candidate.md#6-actual-gate-7-shared-map-and-its-limitation):

```text
F(theta) = (z_i(theta),m_i(theta),z_(i+1)(theta))_i,
m_i = (z_i+z_(i+1))/2 + h_i(f(z_i)-f(z_(i+1)))/8.
```

The shared endpoint appears in adjacent intervals and the midpoint is derived,
not independently variable. For the same residual, domain inclusion gives a
restricted supremum bound; it does not identify this history map with a
physical many-body child or environmental susceptibility. For scalar output g,

```text
D2(g o F)[u,v] = D2g[DF u,DF v] + Dg[D2F[u,v]].
```

The curvature term, moving eigenline/response legs, physical normalization,
booked quadratic-function subtraction and signed causal transport remain
required under the [current remainder formulation](n12_gate7_uniform_remainder_formulation.md).
Duplicated slots do not make DF a contraction in every norm. No new operator
correspondence from a baryon, weak decay or gravitational triple to Gate 7 has
been derived. This note launches no numerical campaign and changes no radius,
budget, proof criterion, booking or frozen certificate.

## Scientific checkpoint

The common architecture is supportable as a typed conditional organization of
existing BHSM objects. Its physical keystone is the separation of persistent
child identity, within-child response, competing descendant sectors and the
action-specific transition law. Gauge constraints can change which collective
sectors are admissible; interactions and state/domain data determine whether
those sectors bind, persist or decay.

The next conceptual obligation is an action-owned sector/transition map for
one physical realization, with supported versus unresolved children, physical
state selection and nonzero/zero channel evidence. The important QCD target
is a gauge-invariant baryon child with a derived dynamical operator; the weak
target is an attached same-action decay amplitude and channel ledger. Neither
obligation replaces or changes the active Gate-7 numerical dependency.

No theorem of universal rigidity, three-body instability, force identity,
generic three-body solution, Cooper pairing or baryon confinement is claimed.

## Focused validation at this checkpoint

- Status, forbidden-claim and frozen-prediction-integrity audits pass. The
  forbidden-claim scanner was also applied explicitly to this new note.
- The existing precision audit passes: `1.066e-14 <= 1.000e-13`. This checks
  the retained benchmark, not a new physical calculation.
- All 20 Markdown targets, required status/sections, code fences and whitespace
  pass the focused note check. The readiness hygiene checker passes when scoped
  to this note.
- The five existing shared-history/response mathematical tests pass when invoked
  directly without the repository-wide pytest write machinery. All three
  chronology assertion groups also pass against the retained report read-only.
- The initial pytest invocation reported eight passing tests, but exited with
  failure because the chronology subprocess regenerated its tracked report.
  The repository guard restored that report; no resulting report diff remains.
  The subsequent read-only check did not regenerate it.
- The full public-readiness audit remains blocked by three existing large
  artifacts: `BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.npz`,
  `BHSM_N12_GATE7_PHYSICAL_ENDPOINT_FIRST_ERRORS.npz` and
  `BHSM_N12_GATE7_STORED_COVARIANCE_FORMATION.npz`, all under
  `artifacts/flagship_integration/`. Its other checks pass. This note neither
  removes those artifacts nor changes their retention policy.

This is a documentation checkpoint, not a public physical release or a new
numerical certificate. No deterministic numerical artifact was produced for it.
