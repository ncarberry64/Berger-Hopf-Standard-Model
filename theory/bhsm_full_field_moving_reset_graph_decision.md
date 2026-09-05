# BHSM full-field moving-reset graph decision

Action version: BHSM-AE-3.2.6-FULL-FIELD-MOVING-RESET-GRAPH-DECISION

Status: CONDITIONAL_EQUIVARIANT_FULL_FIELD_GRAPH_AND_FIRST_VARIATION_DERIVED_BUT_NO_UNIQUE_ACTION_OWNED_RESET_DOMAIN_EXISTS.

## Result

Current BHSM authority determines a single form of full-field reset domain, but not one member of that family. For every supplied admissible spatial attachment and compatible collection of sector Lagrangian relations, the tensor, spin, bundle, canonical, projector, incidence, Galerkin, and causal pieces assemble naturally. The first moving-domain variation is therefore a conditional theorem.

The action selects neither the spatial map nor the nonfermion boundary relations. The surviving family is infinite-dimensional and contains members with different transfer spectra and boundary Hessians. This is not only a coordinate or basis ambiguity. The classification is R4; no member is adopted here.

## Existing reset contract

| Class | Existing objects |
|---|---|
| Defined map | AE2 spin/gauge lift U_R; fermion Gamma0 transmission and opposite-normal Gamma1 graph |
| Copied reference | boundary identities, incidence, frozen family/representation/projector labels, fixed Galerkin coordinates |
| Prescribed domain/value | orientation branch, common reset frame G_R=I and dG_R=0, AE4 future-retarded domain |
| Natural after inputs | tensors, densities, connection and curvature, canonical momenta, spin derivatives, projectors and moved Galerkin coordinates |
| Missing law | F_B, D F_B, nonfermion Lagrangian relation, reset polarization/counterterm, moving graph jets |

EH+GHY selects the regular-cap gravitational Dirichlet pair on its declared domain. The moving-interface theorem fixes the Hayward coefficient and corner pair. Neither selects the cross-reset matter graph. AE4 selects a causal trace space and retarded Schur complement, not a spatial reset map or boundary generating functional.

## Maximal authorized graph family

Use \(F_B:\Sigma_e\to\Sigma_c\) and compare all traces on \(\Sigma_e\). In sector \(s\), let \(T_{s,F}\) be the natural pullback/lift representation and \(L_s^{\rm ref}\) a compatible maximal-isotropic or canonical reference relation. Then

\[
L_s(F_B)=(I\oplus T_{s,F_B}^{-1})L_s^{\rm ref}.
\]

The complete conditional domain is

\[
\mathcal C_{\rm reset}(F_B,\{L_s^{\rm ref}\})
=\{(X_e,X_c,F_B):(\Gamma_eX_e,\Gamma_cX_c)_s\in L_s(F_B)\ \forall s,
\mathcal K=0,\ X_c\in\mathcal D_{\rm AE4}^{R}\}.
\]

Here \(\mathcal K=0\) denotes the owned constraints, incidence intertwiners, and retained-domain conditions. In a graph chart,

\[
\mathcal R_s=\Gamma_e(X_e)-C_s(F_B,\lambda_s)\Gamma_c(X_c)=0.
\]

AE2 fixes the fermion component. It does not fix \(F_B\) or the nonfermion \(\lambda_s\). This is one coherent full-field family, not disconnected per-field rules. Selecting a member would add authority absent from the action.

## Field rules

Ordinary tensors and scalars use pullback by \(F_B\); metrics and densities include tensor and Jacobian factors. Coframes use the oriented coframe lift. Spinors use the induced spin lift combined with AE2 \(U_R\). The connection and curvature rules are

\[
dU+(F_B^*A_c)U-UA_e=0,\qquad
F_B^*\mathcal F_c=U\mathcal F_eU^{-1}.
\]

Canonical momenta and electric/conormal data use the dual cotangent lift, including density and normal factors. On a selected diagonal internal-seam polarization, opposite outward normals introduce a minus sign. That polarization is a candidate, not an owned fact. Projectors transform by conjugation. Galerkin compatibility requires transported projectors to intertwine retained subspaces. Incidence must intertwine the trace map, and child traces must remain in the AE4 retarded domain.

## First moving-domain variation

Define

\[
\eta_c=\delta F_B\circ F_B^{-1}.
\]

For a natural tensor representation,

\[
\delta(F_B^*X_c)=F_B^*(\delta X_c+\mathcal L_{\eta_c}X_c).
\]

The full-sector tangent equation is

\[
\begin{split}
D\mathcal R_s[\delta X_e,\delta X_c,\delta F_B,\delta\lambda_s]
={}&D\Gamma_e[\delta X_e]-C_sD\Gamma_c[\delta X_c]\\
&-D_FC_s[\delta F_B]\Gamma_c(X_c)
-D_\lambda C_s[\delta\lambda_s]\Gamma_c(X_c)=0.
\end{split}
\]

For the connection,

\[
\begin{split}
0={}&d(\delta U)+F_B^*(\delta A_c+\mathcal L_{\eta_c}A_c)U
 +(F_B^*A_c)\delta U\\
&-\delta U A_e-U\delta A_e.
\end{split}
\]

The common gauge frame sets the gauge-vertical \(\delta G_R\) to zero, not the spatial spin-lift variation. Spinors require the spin/Kosmann derivative; momenta require the density-weighted cotangent derivative; moved projectors contribute a commutator; and Galerkin coefficients include the moved-basis or projector term.

A finite-dimensional witness verifies the moving metric pullback derivative below 4e-10, cotangent symplecticity below 2e-16, graph equivariance, and a nonzero relative \(\delta F_B\) with vanishing linearized graph residual.

## Relative tangent direction

The two-sided variation is

\[
\delta_{\xi_{\rm rel}}F_B
=\xi_c\circ F_B-(F_B)_*\xi_e.
\]

It is tangent to every supplied equivariant member of the conditional family. It is not tangent to the active BHSM reset domain because neither \(F_B\) nor the nonfermion reference relation is selected as an action variable or domain datum. Conditional tangency does not amend the action.

## Uniqueness and R4

All four audited base-map routes fail: common embedding, retained flow, collar/normal exponential, and implicit event-child construction. Two degree-one orientation-, metric-, volume-, incidence-, and marked-point-compatible maps have distinct tangent maps and transport connection components differently. The AE2 common frame removes the gauge-vertical one-jet ambiguity but not the base one-jet.

That multiplicity alone would not prove physical nonuniqueness. The decisive witness is the boundary relation. Two maximal-isotropic nonfermion graphs agree at the reference field and pass the same fixed-field Green and BRST conditions, but have different first graph jets and boundary Hessians. The moving-interface self-adjoint family likewise contains continuous transfer laws with inequivalent spectra. No proved representation or gauge quotient identifies those action-detectable differences.

- R1 fails: no unique graph is derived.
- R2 fails: the transfer-spectrum difference is not a relabeling.
- R3 fails: the freedom is not a finite or already-structured residual.
- R4 holds: an uncontrolled base-map function and continuous physical boundary-relation family remain.

Orientation-reversing maps, maps without a spin lift, nonisotropic or nonsymplectic relations, violations of AE2/AE4/constraints/incidence/retarded support, and incompatible Galerkin maps are eliminated. A nontrivial family still survives.

## Norman causal-reconstruction semantics

The recovered Norman principle is consistent with the architecture: complete parent data plus a selected event should determine the physical child modulo proved representational freedom. It forbids interpreting the open graph as permission for arbitrary independent child data. It is not itself an equation.

The repository contains no applicable action-owned map \(\mathcal P=\mathcal R\circ\mathcal E\circ\Phi_T\), singleton \(\operatorname{Fix}(\mathcal P_s)\), or full-field theorem \(D\mathcal P_s=0\). The Norman cycle is a type-correct parent-to-updated-parent composition, but its formation, persistence, and return arrows are not all action-derived. The master self-reconstruction map and fixed point are explicitly undefined.

Later N=3 work constructs full-rank local 26-variable child charts for specific selected finite events. This proves local solvability, not global function-space uniqueness, spatial \(F_B\) uniqueness, or a full-field boundary polarization theorem. The N=12 physical-identification bridge records a closed regular nonempty event-child relation with fixed-event fiber dimension 67, no unique physical domain, and open full-field attachment.

Thus

\[
\mathfrak C(X_e,s)=\bigcup_{F_B,\{L_s^{\rm ref}\}}
\operatorname{Sol}(\mathcal R_s=0,\mathcal K=0,\mathcal D_{\rm AE4}^{R})
\]

is neither proved singleton nor unique modulo an owned quotient. The child is genuinely underdetermined at the current action boundary.

| Candidate | Norman-semantics status |
|---|---|
| Natural diagonal graph | Consistent if derived, but not selected |
| Continuous self-adjoint family | Consistent members; deterministic reconstruction requires selection |
| Simultaneous coordinate/frame/basis relabeling | Representationally equivalent where established naturality applies |
| Arbitrary independent child data | Inconsistent with causal reconstruction |
| Members with inequivalent transfer spectra | Not representationally equivalent |

## Minimum missing datum

The minimum is not an arbitrary child state and need not make the whole raw \(F_B\) physical. It is one action-owned equivariant full-field Lagrangian reset correspondence, equivalently a boundary generating law, that selects the action-detectable class of \(F_B\) and the nonfermion polarization while deriving the child from parent/event data:

ACTION_OWNED_EQUIVARIANT_FULL_FIELD_RESET_LAGRANGIAN_CORRESPONDENCE_SELECTING_F_B_AND_NONFERMION_BOUNDARY_POLARIZATION

The law must leave coordinate, common-gauge, frame, and basis descriptions redundant while fixing every action-detectable transfer, holonomy, spectrum, flux, and seam consequence. Potential experimental discriminants after such a law exists include child transfer spectra, connection holonomy/electric flux, reset boundary energy or charge, and Galerkin mode mixing. No empirical selector is inserted here.

## Generator and downstream status

Because the conditional family is not the active variational domain,

\[
\delta H_{\xi_{\rm rel}}=\Omega_{\rm reset}(\delta,\delta_{\xi_{\rm rel}})
\]

still cannot be evaluated on the action. Differentiability remains G4; \(Q_e\), \(Q_c\), and \(Q_{\rm rel}\) remain unevaluated; charge remains U; outcome remains D. No relative BRST extension, reduced reset, identity fixing, beta, generator propagation, graph-jet campaign, or global S2--S4 result is earned. A second-order calculation is premature.

## Hopf adversarial witness

The compact constraint allows equal-and-opposite parent/child Hopf momentum with positive relative rotor energy. Any future correspondence must state whether this mode is transmitted, reflected, or retained. Naturality alone cannot quotient it. This does not identify the rotor with \(F_B\) or make it reset data by fiat.

## Hindsight ledger

### VALIDATED

- The maximal conditional equivariant full-field graph family is constructed.
- Its complete first moving-domain variation is explicit.
- The relative vector is tangent to supplied equivariant members, not the active domain.
- Base-map and nonfermion-relation freedoms are independent.
- Current evidence selects R4 and retains D.
- Norman semantics constrain interpretation but do not close the map.
- N=3 local child charts do not prove global/full-field uniqueness.

### INVALIDATED

- AE2 \(U_R\) alone defines a full-field spatial reset.
- Naturality selects \(F_B\).
- Self-adjointness selects the nonfermion graph.
- Deterministic intent implies identity attachment.
- All relative Hopf motion may be quotiented without a generator calculation.

### REDUNDANT

Objectwise Maxwell, Dirac, curvature, GFHS, cotangent, family, representation, and projector covariance proofs are inherited. The two-sided groupoid, orbit, and internal BRST audits are not repeated.

### OPEN

Only the exact next action-owned correspondence above is promoted as the first independent object. Its Euler--Lagrange domain must then be linearized and the Hamiltonian generator calculation rerun immediately.

### DECISION POWER

The constructed family converts the former implementation absence into a precise boundary: geometry fixes how a chosen reset transports fields, while the action does not choose physically inequivalent reset relations. This proves R4 without treating representation labels as physical and explains why G4/U/D remain the correct fail-closed classifications.
