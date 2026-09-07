# BHSM reset-correspondence stationarity adjudication

Action version: BHSM-AE-3.2.7-RESET-CORRESPONDENCE-STATIONARITY-AUDIT

Status: F4_L4_D4_G4_U_OUTCOME_D_NEW_INTERFACE_LAW_REQUIRED.

## Decisive result

The existing BHSM action restricts consistently to every supplied member of the conditional moving-reset family, but it does not define a functional on the union of those domains. Field stationarity inside a supplied graph derives momentum/flux transversality. It does not promote the graph, its base map, or its polarization into variational variables and therefore cannot select them.

The existing action is F4 with respect to \(F_B\), L4 with respect to the nonfermion Lagrangian relation, and D4 for deterministic child reconstruction. No reset member is adopted.

## 1. Action terms touching the reset

All 13 registered master-action terms were traced.

| Term | Bulk variation | Boundary/reset-supported contribution |
|---|---|---|
| T8_EH | Einstein equation | Metric normal derivative and Brown--York pair on a declared regular face |
| T8_vacuum | Vacuum stress | Shape/measure term only if an embedding is already varied |
| T8_carrier | \(\chi,\sigma\) equations and stress | Carrier conormal potential |
| T8_scalar | \(\sigma\) equation and stress | Scalar conormal potential |
| T5_caps | Cap Einstein/scalar equations | Ordinary cap metric/scalar pairs |
| T5_GHY | none | Cancels EH normal derivatives and defines geometric momentum |
| T4_B1 | Intrinsic geometry/matter equations | Boundary-of-\(B1\) or corner terms |
| T4_matcher | none | Matches each declared cap metric to \(B1\), not event points to child points |
| T4_gauge | Yang--Mills equation and stress | Electric/conormal Green form |
| T4_fermion | Dirac equation and current | First-order Green form canceled on the AE2 graph |
| T4_Yukawa | Algebraic sources | No derivative seam term |
| T4_scalar | Higgs equation and stress | Gauge-covariant scalar conormal potential |
| T4_neutral_aux | Conditional neutral response | Neutral conormal term if active |

No registered term explicitly contains \(F_B\) or a nonfermion graph parameter. AE2 owns \(S_{\Sigma,F}=0\) and its fermion domain. The algebraic attachment potential and flux are zero. No nonfermion seam action is present.

## 2. Restricted reset action

For every supplied conditional member,

\[
S_{F,L}[X_e,X_c]
=
S_{\rm existing}[X_e,X_c]\big|_{\mathcal C_{\rm reset}(F_B,L_s)}.
\]

The bulk density is unchanged. Dependence on \(F_B\) and \(L_s\) appears only through trace pullbacks, moving trace conditions, connection/spin lifts, cotangent momenta, moved projectors and Galerkin bases, incidence conditions, and AE4 retarded admissibility.

The repository does not define

\[
S:\bigcup_{F,L}\operatorname{Dom}(S_{F,L})\longrightarrow\mathbb R.
\]

There is no action-owned configuration slot, momentum, measure, or allowed cross-domain variation for \(F_B\) or \(L_s\). Thus \(S_{F,L}\) is a family of restricted functionals, not one action in which \(F\) and \(L\) are dynamical variables.

## 3. Boundary one-form and \(\delta_{F_B}S\)

In a finite trace chart let

\[
q_e=C(F_B,\lambda)q_c.
\]

The two-sided boundary one-form is

\[
\Theta_{\partial}=\langle p_e,\delta q_e\rangle+\langle p_c,\delta q_c\rangle.
\]

Its restriction is

\[
\Theta_{\partial}\big|_{\rm graph}
=
\langle C^*p_e+p_c,\delta q_c\rangle
+
\langle p_e,\delta C\,q_c\rangle.
\]

The first coefficient gives the natural momentum equation

\[
C^*p_e+p_c=0
\]

after the configuration graph has been chosen. The second is a domain-motion term. Requiring it to vanish for every unrestricted \(\delta C\) gives a degeneracy condition such as

\[
p_e\otimes q_c=0,
\]

which overconstrains the trace data and does not solve for \(C\).

For a natural moving map, the formal on-shell map variation is

\[
\delta_F S_{F,L}
=
\int_\Sigma \mathcal J_{\rm reset}(\eta_c),
\qquad
\eta_c=\delta F_B\circ F_B^{-1},
\]

where \(\mathcal J_{\rm reset}\) contains tangential stress, canonical momentum, gauge and spin currents, projector motion, and any applicable geometric corner moment map. Its formal vanishing is a conditional interface momentum/Noether balance on a supplied moving domain. It is not an action-owned Euler--Lagrange equation for \(F_B\).

Therefore the base-map result is F4:

- F1: false.
- F2: false.
- F3: false; no legitimate \(F_B\) equation is defined.
- F4: true; the current action is blind to the required choice.

The common-embedding, retained-flow, normal-collar, and implicit-spatial routes are neither selected nor eliminated. Identity attachment is not selected.

## 4. Variation of the nonfermion relation

With \(C_s=C_s(F_B,\lambda_s)\), the formal graph-parameter term is

\[
\delta_{\lambda}S_{F,L}
=
\sum_s
\left\langle
\Pi_{e,s},
D_{\lambda}C_s[\delta\lambda_s]\Gamma_cX_c
\right\rangle_\Sigma.
\]

The bulk action contains no \(\lambda_s\), and \(\lambda_s\) is not an action variable. The prior two-graph witness remains decisive: both graphs are maximal isotropic and cancel all allowed fixed-graph field variations, but their first graph jets and boundary Hessians differ. The self-adjoint transfer family also has inequivalent spectra.

Well-posed field stationarity is stronger than self-adjointness in deriving momentum matching after a graph is supplied. It is not stronger in selecting the graph itself.

Therefore the relation result is L4:

- L1: false.
- L2: false.
- L3: false; no graph-selection equation exists.
- L4: true.

## 5. Natural transversality

Conditional on a supplied configuration graph, the sectors yield:

\[
C_s(F_B)^*\Pi_{e,s}+\Pi_{c,s}=0.
\]

For geometry this becomes the Brown--York/corner momentum jump with the existing matcher and corner variations. Maxwell gives transported electric/conormal matching. Scalar and topographic sectors give transported scalar momentum matching. AE2 already supplies the fermion trace graph and opposite-normal Dirac Green-form cancellation. Canonical coordinates are domain data; their conjugate momentum equation is derived.

These equations do not combine into an action-selected full-field relation because the configuration half and common boundary ensemble remain unselected.

## 6. Corners and endpoints

GHY is the coefficient-locked completion required for the declared regular gravitational cap. The Hayward term and area/relative-angle pair are coefficient-locked on the v15.12 moving geometric interface. Neither selects the matter/core trace unitary or cross-copy base map.

The AE3 smooth-enclosure cancellation is not the reset locus. AE2 fixes the independent fermion seam action to zero. No canonical endpoint term contains an \(F_B\) or \(L_s\) generator, and the complete reset counterterm remains absent. No unique zero-new-parameter variational completion is forced.

## 7. Hopf rotor

The compact constraint permits equal-and-opposite parent/child Hopf momentum with positive relative energy. Minimum-energy selection is not invoked. Because \(\delta_F S\) is not defined on the active reset domain, stationarity along an attachment Hopf direction cannot be evaluated. It neither fixes the orientation nor proves that the rotor is continuous or discrete reset data.

## 8. Stationary child set

Define

\[
\mathfrak C_{\rm stat}(X_e,s)
=
\bigcup_{(F_B,L_s)}
\{X_c:
{\rm EL}_{\rm bulk}=0,
{\rm conditional\ trace/flux}=0,
\mathcal K=0,
X_c\in\mathcal D_{\rm AE4}^{R}\}.
\]

The field equations apply memberwise and do not select the member. No proved quotient identifies all surviving members. Local finite-dimensional rank does not change that conclusion.

The deterministic-child result is D4:

- D1: false.
- D2: false.
- D3: false.
- D4: true.

## 9. New-law boundary

A general admissible interface law would have schematic form

\[
S_{\rm seam}
=
\int_\Sigma \mu_e\,
\mathcal L_{\rm seam}
(\Delta_s,\Pi_s,DF_B,\nabla DF_B,A,\mathcal F,
{\rm corner},P_s,\ldots)
+
S_{\rm top/hol}(F_B,U).
\]

This is characterization only; no term is implemented.

It must depend on the attachment map and admissible jets, sector trace mismatches and momenta, geometry/frame/corner data, connection/curvature/holonomy, scalar traces, projector/Galerkin intertwiners, incidence sectors, and nonfermion relation parameters. It must preserve diagonal orientation/spin diffeomorphisms, the existing Spin x GSM and BRST domain, family/projector intertwiners, incidence/topology, constraints, Noether balance, and AE4 causality.

At least first derivatives of \(F_B\) are necessary for connection transport. Extrinsic-curvature or curvature terms may require second derivatives. Local scalar densities may control trace and stress matching, but mapping, holonomy, and topology may require a global or topological component.

Existing normalization fixes the EH/GHY/Hayward geometric coefficients and the AE2 zero fermion surface term. It fixes no nonfermion polarization, \(F_B\) selector, or mapping/holonomy-sector weight. Symmetry allows several invariant classes and does not force a unique zero-parameter term.

The minimum deficit is one independent choice, but that choice is an arbitrary symmetry-compatible functional on the full boundary-field and attachment-jet space. It is not reducible to one continuous coefficient or a finite parameter set.

## 10. Generator and downstream result

No action-owned reset is selected, so the relative tangent direction is still absent from the active domain. Consequently:

- differentiability: G4;
- \(Q_e=Q_c=Q_{\rm rel}=\mathrm{None}\);
- charge: U;
- gauge kernel: unevaluated;
- A/B/C: false;
- D: true;
- reduced reset and beta: absent;
- graph jets: conditional first formula only;
- S1: reference slice only;
- S2--S4: blocked.

## Hindsight ledger

### VALIDATED

- The existing action restricts memberwise to every supplied reset graph.
- Field stationarity derives conditional momentum/flux transversality.
- Formal map variation is an interface momentum/Noether balance, not a map selector.
- The active action has no cross-domain \(F_B\) or \(L_s\) variation.
- The stationary child set remains D4.

### INVALIDATED

- Bulk-action stationarity selects \(F_B\).
- Well-posed field stationarity selects the nonfermion polarization.
- GHY or Hayward terms select the full-field reset.
- Variation over every graph selects a graph instead of overconstraining traces.
- Positive Hopf energy implies a stationary minimum selector.

### REDUNDANT

The moving graph, first moving-domain variation, covariance, groupoid, quotient, BRST, R4, and Norman-semantics audits are inherited.

### OPEN

OWNER_AUTHORIZED_SYMMETRY_COMPATIBLE_FULL_FIELD_RESET_INTERFACE_GENERATING_FUNCTIONAL_WITH_NONDEGENERATE_F_B_AND_POLARIZATION_VARIATIONS

### DECISION POWER

F4 and L4 establish that the existing action has memberwise natural transversality but no mechanism selecting its domain. Hence D4, G4, U, and Outcome D remain.

### NEW-PHYSICS DEFICIT

ONE_ARBITRARY_SYMMETRY_COMPATIBLE_INTERFACE_FUNCTIONAL
