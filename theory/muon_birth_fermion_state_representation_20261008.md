# Muon birth fermion state: CAR covariance and state-uniform interface identities

The retained AE3.1 physical quasifree fermion state datum is a **self-dual CAR Cauchy covariance**, not a required nonzero classical spinor one-point function. The previous universal stop at `g_F^- = Gamma0,E1^- Psi_C1` was too strong: a vector accepted by `transmit_trace` establishes a linear domain map, not the representation or selection of a quantum state. This report supersedes that interpretation while preserving the prior geometric calculation and every historical input.

The exact AE2 opposite-normal Green balance cancels for every admissible state. The same cancellation holds for any complete matched oriented one-body kernel. It does not follow that every sourced E1 stress, returned-child or Noether kernel is matched. An actual selected muon two-point state still requires **`C_C1,E1^-^BHSM`**, transported into the existing current-C2 covariance operand. That is one state-selection problem. No numerical covariance or one-particle ray is chosen here.

Starting HEAD: `1d94ce8ed77f8bfe1f13c729dd3d8885dbee5b69`. Branch: `codex/muon-parent-maxwell-density-review`. Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`.

## Frozen numerical and owner results

The incoming C1/branch23 and outgoing C2/branch24 one-sided values remain on the same E1 event. The prior unchanged geometric 57-row reset has norm **7.64107108345298e-15** and maximum row **5.628594097932515e-15**, at its retained order12/96-point, Decimal60-action/binary64-normalization scope. This milestone reads that packet and hashes its sources; it does not rerun or reinterpret the residual as a full physical muon birth.

`BRANCH_REALIZATION_TRANSFER_EVENT` and the muon child-side birth cutoff remain adopted. No support semantics, precursor species, family selector, common-A, eta identity, local child persistence or global continuation campaign is reopened.

## Action, Cauchy space and state type

The [AE2 action/domain owner](../src/bhsm/interface/action_extension_global_spin_reset_ae2.py) specifies

```text
S_F = (1/2) integral_(M_event union_R M_child)
      [barPsi iD Psi - overline(iD Psi) Psi] dmu,
S_Sigma,F = 0,
Gamma0,child Psi = U_R Gamma0,event Psi,
Gamma0,child deltaPsi = U_R Gamma0,event deltaPsi.
```

The zero independent seam density is an internal-gluing action statement. It does not set the fermion field, bulk current or stress to zero. The first-order Euler/domain equation is linear in the operator-valued field or supplied test/Cauchy vector. Its expectation need not be a nonzero c-number ray.

The [AE3.1 state contract](../src/bhsm/interface/ae31_c2_fermion_hadamard_state_class.py), `cauchy_covariance_selection_contract`, owns the completed Dirac-inner-product Cauchy-data Hilbert space, CAR pairing and causal evolution. On its self-dual doubling the state is

```text
C = C^dagger,  0 <= C <= I,  C + Gamma C Gamma = I,
C^2 = C only for a pure state.
```

A pure state is a specialization, not an independently selected vacuum. The Hadamard principal polarization is fixed modulo smoothing terms; the smooth bisolution part is not selected. A quasifree state can have zero odd expectations and nonzero two-point/bilinear data. This is the standard quasifree field definition, rather than a zero-field assumption; see [Dappiaggi, Hack and Pinamonti, definition 3.2](https://arxiv.org/html/0904.0612).

The legitimate later external-one-particle alternative is separate. [universal_lsz](../src/bhsm/interface/universal_lsz.py) requires actual simple-pole modes and unit descriptor residue for an external amplitude. PEI06/PEI07 do not establish that an incoming classical ray is the universal birth datum. No ray is inferred from (5,2), eta inclusion, an FR rotor, a mechanical normal mode or a basis vector.

## Required fermionic observable types

The two source receipts give raw hashes and checked function/section bounds. Their classifications distinguish a mathematical argument of a helper from the physical quantum state.

| Type | Retained consumer | Physical state use |
|---|---|---|
| LINEAR_TRACE | AE2 Gamma0 field/variation graph and `transmit_trace`; Dirac Euler equation | Linear field/test/domain law. No nonzero one-point expectation required. |
| BILINEAR_CURRENT | `barPsi_L gamma T_plus Psi_L`, its conjugate, electromagnetic charge current, Yukawa scalar source | Ordered two-point contraction with the action's current kernel. |
| STRESS_ENERGY | Metric/domain variation of the Dirac density; full normal stress and traction | Differentiated two-point contraction, including inherited pairing/measure/contact terms. |
| GREEN_PAIRING | Joined AE2 outward-normal Green form | Exact form cancellation on the graph, before selecting a state. |
| TWO_POINT/COVARIANCE | CAR state, Feynman function, finite fermion determinant and charged-lepton/composite response | Smooth completion can survive; singular/principal data alone do not give the state. |
| EXTERNAL_ONE_PARTICLE_STATE | Pole-normalized external LSZ/Pauli legs | Separate action-owned external-mode/pole normalization when that consumer is reached. |

PEI06 binds the actual quantum state/restriction in addition to the geometry and other active sectors. PEI07 consumes complete constraints, tractions, sources, contacts and Noether balance. Neither row is replaced by a c-number spinor norm.

## Exact convention: positive two-point covariance versus occupation

The [retained AE3.1 two-point convention](ae31_c2_state_observable_audit.md) and [retained fermion-body implementation](../artifacts/muon_native_family_difference_20261006/inputs/fermion_body.py) use different but compatible ordinary-particle coordinates:

```text
C_plus,ij = <chi_i chi_j^dagger>,
N_ij      = <chi_j^dagger chi_i>,        N = I - C_plus,

W_plus(t,s)  = V_t C_plus V_s^dagger,
W_minus(t,s) = V_t (I-C_plus) V_s^dagger,

G_F(t,s) = -i V_t [C_plus - theta(s-t) I] V_s^dagger,
delta G_F = -i V_t delta C_plus V_s^dagger
          = +i V_t delta N V_s^dagger.
```

The external body's greater factor is I-N and its lesser factor is N. These agree away from the equal-time distribution convention, which that body leaves to its caller.

For a finite or legitimately smeared ordinary ordered quadratic,

```text
Q_A = chi^dagger A chi,
<Q_A> = Tr(A N) = Tr[A(I-C_plus)],
delta <Q_A> = Tr(A delta N) = -Tr(A delta C_plus).
```

Blindly inserting Tr(A C_plus) reverses this convention. The new `occupation_difference_contraction` implements only the finite relative-state identity. It does not manufacture an absolute local quantum current or a reference state.

For current and stress, polarize/differentiate the **existing action** to obtain its bidifferential kernel K_j or K_T, then apply it to the ordered two-point distribution. For two Hadamard states on the same domain, delta W_minus is smooth, so relative values are K_j[delta W_minus] and K_T[delta W_minus] with the prescribed coincidence/smearing and geometric dual. The full Noether contraction uses its actual total traction kernel; it cannot be assigned a universal trace from the finite q helper.

The inspected action/state owners do not supply an absolute local Wick/point-split subtraction prescription. No normal-order reference, finite subtraction or doubled-CAR factor is inserted here. The kinetic factor 1/2 symmetrizes action differentiation; it does not authorize another arbitrary factor 1/2 in a quantum observable. This bounded convention finding is recorded in the owner receipt. It is not used to obstruct an exact zero form or to claim that selecting C alone completes every later renormalized value.

## Implemented reset and family restriction

The new `transport_muon_covariance` reuses [transport_self_dual_covariance](../src/bhsm/interface/ae31_c2_reset_hadamard_transport.py). For supplied compatible operands,

```text
C_E1+ = U_R C_E1- U_R^dagger,
Gamma(v) = G conjugate(v),
U_R G_- = G_+ conjugate(U_R),    G conjugate(G) = I.
```

Unitarity preserves Hermiticity, positivity/order, purity when present and the self-dual identity. The implementation checks these and the family/reset relations; no default covariance is supplied. Finite matrices cannot certify a continuum Hadamard condition. The retained smooth spin/gauge bundle isomorphism and future-null Dirac-symbol intertwining preserve the Hadamard wavefront/principal class for every admissible upstream state. This is the existing state-class transport theorem, not state selection.

Reuse the slot1 muon projector, with its conjugate-charge partner:

```text
Q_mu = Pi_mu,particle direct_sum conjugate(Pi_mu,particle),
Gamma Q_mu Gamma = Q_mu,       [U_R,Q_mu] = 0,
C_mu = Q_mu C Q_mu,
C_mu + Gamma C_mu Gamma = Q_mu.
```

The right side is the identity on Ran(Q_mu), not ambient I. Pure C restricts to a pure C_mu only when the subspace is C-invariant, equivalently [C,Q_mu]=0. Compression otherwise need not be pure.

The enclosure map T_enc contains P_D L_sigma and is generally nonunitary. A transported two-point kernel T_enc C T_enc^dagger has CAR pairing T_enc T_enc^dagger. Its interpretation uses the owned induced pairing/restriction. Localization weighting is not silently turned into a unitary covariance automorphism.

## Cancellation before selection

Let A_- and A_+ include the actual outward-normal signs. For legitimately trace-class or smeared matched kernels,

```text
C_+ = U C_- U^dagger,
Delta_A = A_- + U^dagger A_+ U,

Tr(C_- A_-) + Tr(C_+ A_+) = Tr(C_- Delta_A).
```

The same statement holds for the ordered I-C contraction and for consistent charge-doubled normalization. If A_+ = -U A_- U^dagger, then Delta_A=0 for **all** C, including all allowed smooth completions. If the unoriented child operator is +U A_- U^dagger, opposite-normal subtraction produces the same result. The replay proves the pulled-back operator zero symbolically with no numerical C.

This is sufficient, not necessary: a nonzero Delta_A can still annihilate every allowed smoothing direction. For an affine physical response, the actual test is its contraction with every admissible X satisfying X=X^dagger, Gamma X Gamma=-X and the required charge/family conditions. A generic nonzero matrix, one real-angle witness or a frozen gradient of a nonlinear functional is not a proof about the full physical target.

| Consumed combination | Result |
|---|---|
| AE2 internal Green graph | **DERIVED exact zero**, because J_+=-U J_- U^dagger and both fields/variations use U. No selected C needed. |
| Internal charged-lepton electromagnetic normal flux | **DERIVED exact zero** on that graph: the central charged-lepton generator transports with the Green form. No selected C needed. |
| Matched oriented current kernel | **DERIVED conditional zero** when its complete generator, normal form and pairing intertwine. Individual current values remain separate. |
| Full E1 stress/traction | **UNEVALUATED operator matching**; Dirac principal-symbol transport alone does not prove metric/background/domain/contact derivatives match. |
| Full E1 sourced Noether/KKT balance | **UNEVALUATED operator matching**; returned-child, source and multiplier terms do not vanish merely from free Green isotropy. |

The retained resolved smooth Sigma_enc interface law is not substituted for a value certificate of the different E1 reset. For PEI07, the actual traction is the full parent + returned child + J + C_response^dagger lambda combination. Its Noether contraction is 2 Re <Tq,Pi_total>. Zero total traction implies zero total contraction, but neither source nor individual sector is thereby evaluated.

The stronger electromagnetic subcase follows from the local phase variation of this same Dirac action and [charged_lepton_qem_ledger](../src/bhsm/interface/ae31_c2_local_em_ward_identity.py). Its normal kernel is proportional to J_Green Q_l in the fixed boundary-variation convention; Q_l=-I_spin tensor I_family transports through U. Therefore its oriented kernel also obeys A_Q,+=-U A_Q,- U^dagger. The generic Green helper does not assign a physical current prefactor, and none is inserted here. The cancellation holds before that kernel is contracted with a state. It does not evaluate individual current magnitudes or complete sourced Noether balance.

## What survives and the single upstream state operand

The free CAR anticommutator W_plus+W_minus=V_t V_s^dagger and free retarded G_R are state independent. The local Hadamard singularity and principal polarization are likewise independent of the smooth completion.

The selected muon **two-point state itself** is not state independent. The retained [fixed-history theorem](../src/bhsm/interface/ae31_c2_fixed_history_state_nonuniqueness.py) permits distinct compatible Hadamard covariances differing smoothly within the same family. For nonzero such X supported in the muon/conjugate sector,

```text
delta W_mu = V_C2 U_R X U_R^dagger V_C2^dagger != 0.
```

Family-preserving unitary causal/reset maps are invertible, so their conjugation cannot erase X. In particular delta G_F=-i V_t X V_s^dagger is nonzero. An exact zero seam balance admits all these states; it does not select one.

Existing finite consumers explicitly retain the smooth part:

```text
M_eHS[C] = Tr(G_e[C] V_HS G_e[C] V_intrinsic),
M_eHS,fin[C] = sum_f y_f chi_f,fin[C] P_f,
H_C = K_LR^(-1) - Pi_Had,sing I - Pi_fin[C].
```

These are the retained charged-lepton/composite and HS formulas, not newly evaluated native numbers. Cancellation of a common singular pole does not remove Pi_fin[C]. This is not a claim that every heat, KKT or Pauli functional depends on C, nor a proof of surviving dependence of the unevaluated full birth Noether combination. Each such target needs its own consumed-operator test.

In particular, the [retained HeatPencil](../src/bhsm/interface/arb_heat_pencil_contractions.py) is covariance independent **at fixed complete sourced family**: it consumes K, M, ell and the complete source jets, without a C argument. This preserves the earlier fixed-family heat result. It does not establish that a caller's unevaluated physical injection, domain or relative completion is fixed, or supply a physical heat value here.

The one state source is

```text
C_E1+^BHSM = U_reset C_C1,E1-^BHSM U_reset^dagger,
C_mu,Sigma^BHSM =
    Q_mu V_C2(Sigma,E1+) U_reset C_C1,E1-^BHSM
         U_reset^dagger V_C2(Sigma,E1+)^dagger Q_mu.
```

Thus the incoming covariance is the upstream source of the existing current-C2 muon covariance. No independent child vacuum is introduced. Sigma in this equation is a Cauchy slice, distinct from the material enclosure level set.

The exact selected-state operand is **C_C1,E1-^BHSM**, on the already-owned Dirac Cauchy Hilbert space. Its producer must be an action-owned covariance/boundary-state/complex-structure prescription. Reset and causal evolution are its consumers. The retained selector audit finds no selected boundary covariance or complex structure; time orientation, Hadamard condition and AE2 transport do not select the smooth part. Instantaneous diagonalization, a chosen Bogoliubov angle, temperature, measured muon input or phenomenological vacuum is not supplied. Euclidean-cap/reflection and asymptotic in-state candidates have no owned current-C2 selection rule.

This covariance is required for the actual selected matter state and its state-dependent two-point response. It is **not** required for the exact Green zero, **not** proved necessary for every untested birth-balance combination, and **not** sufficient by itself to close all active sectors, contacts or the mechanical formation mode.

## Downstream and verification boundary

Full physical I_phys has not passed. Matter covariance, mechanical psi_star, action-inertia normalization, xi_psi, seven-port source, stationary physical KKT base, six derivatives, h_psi, delta_psi, z_psi, r/i, heat, R_ind, native photon response, paired heat and signed Pauli readout remain without physical values. The matter covariance, external LSZ ray and mechanical normal mode are different mathematical types.

| Label | This milestone |
|---|---|
| DERIVED | CAR representation, reset/family identities, owned Green zero, conditional complete-kernel cancellation, convention conversion and one upstream/C2 covariance chain. |
| EVALUATED | Retained-source/hash/citation audit and exact symbolic zero; frozen reset read without recomputation. |
| CONTROL_ONLY | Supplied finite matrices in focused API tests; none is a selected BHSM state or physical error certificate. |
| UNEVALUATED | Selected covariance, complete interacting E1 matching and downstream physical values. |
| OWNER_DEFINITION_GAP | No action-owned covariance selection prescription supplied; the adopted support/family/cutoff definitions remain frozen. |

Replay:

```text
python scripts/replay_muon_birth_fermion_state_representation.py --out artifacts/muon_birth_fermion_state_representation_20261008/run_1
python scripts/replay_muon_birth_fermion_state_representation.py --out artifacts/muon_birth_fermion_state_representation_20261008/run_2
python -m pytest --noconftest -q tests/test_muon_birth_fermion_state_representation.py
```

The focused checks cover CAR positivity/reality, charge-doubled family restriction, possible loss of purity under noninvariant compression, reset compatibility, covariance sign and state-uniform symbolic cancellation. They select no physical vacuum and rerun no prior numerical controls. Command outputs, final byte comparisons, every source identity, error scope and publication audits are recorded in [verification.json](../artifacts/muon_birth_fermion_state_representation_20261008/verification.json).

Focused output: **31 passed in 1.34s**, exit0. The replay verifies **55 Python citations**, **28 retained hash identities** and **242 source/input files**. Final packet/manifest/hash-receipt products are materialized twice and their exact byte comparison and SHA256 values are in verification.json. The formal operator zero is exact; finite test tolerances are API diagnostics, not continuum or physical state certificates. Publication commands are the repository status, forbidden-claim, frozen-integrity, precision and public-readiness audits, with their actual outputs in the same receipt.

The retained action defines the CAR state class, reset/causal transport and matched Green zero, but supplies no selected value of **C_C1,E1-^BHSM**. The existing current-C2 muon covariance is its transported restriction. The prior demand for nonzero incoming classical spinor coefficients is withdrawn.
