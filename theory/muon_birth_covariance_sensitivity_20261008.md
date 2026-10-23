# E1 birth covariance sensitivity: complete-row quotient and operator dependency

The complete consumed E1 fermion sensitivity has **not been evaluated**. Neither a state-independent birth balance nor a specific nonzero physical sensitivity has been established in this audit. The new result is an exact decision criterion on the complete admissible CAR tangent, together with the directional action kernel that must be supplied to that criterion. **Selecting a covariance is not proved necessary for this birth balance and cannot replace that kernel.** This supersedes the previous report's selected-covariance stopping sentence for the birth question.

Starting HEAD: `a6e3ceebb0a9b8322be333c7be116a01ca6b837d`; branch `codex/muon-parent-maxwell-density-review`; scientific reference `524ed90689bd5923c249bba2e699abf627e703cd`. The fixed event is incoming C1/branch23/E1-minus to outgoing C2/branch24/E1-plus. This audit does not rerun the geometric reset, the closed Green/EM identities, earlier controls or a global continuation campaign.

The user's requested A/B fork remains unresolved. It would be false to label an unpopulated operator zero, or to label an older nonzero current probe the sensitivity of the complete birth balance. The deterministic replay explicitly emits `actual_question_answered:false`, with physical `Delta_stress`, `Delta_Noether`, `Delta_contacts`, `Delta_B`, `S_B`, rank and consumed moments all null. A successful audit exit means the dependency and symbolic checks passed.

## Exact convention and independent consumed rows

The retained particle convention is `C_plus=<chi chi^dagger>`, `N=I-C_plus`. For a finite or properly smeared ordered quadratic, `B_A=Tr(A N)`, hence

```text
B_A[C]-B_A[C_ref] = -Tr((C_plus-C_plus_ref) A),
D_C B_A[X] = -Tr(X A).
```

Smooth relative Hadamard differences require no invented absolute Wick subtraction. The canonical kinetic action's one-half is not automatically a quantum Nambu-doubling factor. The self-dual contraction must come from the owned ordered observable. In the formulas below, `Delta` already includes that sign and any genuinely owned factor.

Let `alpha` index independent consumed PEI06/PEI07 directions: oriented metric/interface traction rows, canonical event rows and any separately owned integrated Hamiltonian row. For a fixed, completely supplied sourced background and common domain, a one-body row has an oriented pulled-back kernel

```text
K_alpha = K_event,alpha
        + U_R^dagger K_child,DR(alpha),oriented U_R
        + K_return/source/constraint/domain,alpha.

D_C B_alpha[X] = -Tr(X K_alpha).
```

`DR(alpha)` denotes the geometric reset pullback of the variation as well as the normal orientation. Differentiating a moving pullback also produces derivatives of `U_R`, the trace maps and the pairing. Principal-symbol matching alone does not remove them.

Stress, canonical momentum and its Noether contraction are different readouts of the same action variation. Adding a stress term once as traction and again as an independent Noether action would double count it. The correct object is a vector of independent rows, or their action-owned prescribed linear combination. No new scalar weighting of those rows is introduced here. For a covariance-dependent on-shell background, induced field/source/multiplier/domain derivatives must also be included before claiming a total affine response.

## Differentiate the retained density before asserting stress matching

The literal AE2 density is polarized without changing its overline or operator convention. Set `P=iD`, let `beta` be its actual Dirac-adjoint matrix, and let `mu` be the spacetime measure. For fixed test spinors `f,g`,

```text
S_D[f,g] = 1/2 integral mu [f^dagger beta P g - (P f)^dagger beta g].
b = delta(mu)/mu = 1/2 g^MN delta(g_MN).

delta S_D = 1/2 integral mu {
 f^dagger [(b beta+delta beta)P+beta delta P]g
 -(P f)^dagger (b beta+delta beta)g
 -(delta P f)^dagger beta g }.
```

For compact tests, the base-measure formal-adjoint representation is

```text
K_v = 1/2 [(b beta+delta beta)P+beta delta P
          -P^dagger_mu(b beta+delta beta)-delta P^dagger_mu beta].
```

Multiplication by `b` stays inside `P^dagger_mu`; moving it outside loses derivatives of the measure. The replay verifies the ordered product rule exactly with noncommuting symbols. This is a formal density identity, not an evaluated E1 stress matrix.

For the kinetic representative,

```text
delta P = i delta gamma^M nabla_M+i gamma^M delta Omega_M,
delta gamma^M = Gamma^A delta e_A^M,
delta Omega = 1/4 delta omega_AB Gamma^AB+delta Omega_gauge.
```

The torsion-free spin jet satisfies the differentiated Cartan equation `d delta e^A+delta omega^A_B wedge e^B+omega^A_B wedge delta e^B=0`, with antisymmetry. Setting the spin variation zero is not this derivative. The adopted common-A composition remains available and is differentiated in that composition.

For a separately represented retained Yukawa term `-integral mu f^dagger beta M_H g`, add

```text
K_v,Y = -(b beta M_H+delta beta M_H+beta delta M_H).
```

The AE3.1 Yukawa owner is additive and is varied as such. Absorption into `P` requires a proved action-to-operator embedding. In particular, inserting a beta-Hermitian `P_Y=-M_H` into the literal antisymmetrized AE2 density gives `1/2(beta P_Y-P_Y^dagger beta)=0`, rather than the separate `-beta M_H` term. The Hermitian chiral mass template alone is not that equivalence proof. The inherited LR mass and family-central reset intertwining remain closed; this convention guard does not reopen their definition.

The complete domain derivative is obtained by differentiating the trace graph itself:

```text
Gamma0,c delta g_c = U_R Gamma0,e delta g_e
                  + delta U_R Gamma0,e g_e
                  + U_R delta Gamma0,e g_e-delta Gamma0,c g_c.
```

The fixed-U field-variation graph covers only the first term. A moving interface adds the Reynolds surface contribution or its equivalent pulled-back Lie derivatives, once. These terms are retained in the dependency ledger; the compact-test strong kernel does not pretend to evaluate them.

AE4 explicitly retains AE3.1 as predecessor. The AE3.2 Einstein-Cartan quartic completion is a nonpromoted candidate with an unresolved global stationary domain. It is not silently inserted into this one-body birth ledger, and no quartic Wick convention is invented.

This exclusion does not erase the retained gauge-derived HS interaction. Its exact uneliminated auxiliary rewrite is quadratic in the fermions at a fixed supplied HS background. Eliminating gauge/HS fields or differentiating a self-consistent background can produce nonlinear state dependence. Those induced responses must be supplied before extending the fixed-background affine quotient to the full coupled functional. The gauge-derived up/down auxiliaries, intrinsic charged-lepton Higgs and failed EC candidate remain distinct.

## Complete sourced canonical/Noether row

The existing AE4 supplied-block assembly defines

```text
G = (H_cc^R)^(-1),
H_eff = H_pp-H_pc G H_cp,
E = H_eff q+J+C_response^dagger lambda.
```

Its complete directional derivative is

```text
D H_eff = D H_pp-(D H_pc)G H_cp-H_pc G(D H_cp)
        + H_pc G(D H_cc^R)G H_cp,
D E = (D H_eff)q+H_eff Dq+DJ
    +(D C_response)^dagger lambda+C_response^dagger Dlambda.

B_T = 2 Re <Tq,E>,
D B_T = 2 Re <D(Tq),E>+2 Re <Tq,D E>.
```

Returned-child, current/source and response-multiplier contacts belong in `E` before state contraction. Noether is its contraction, not a second action term. The integrated composite-minus-parent Hamiltonian is expressly outside the jet helper's readout. It needs its own same-owner complete kernel if consumed.

The solver's small residual at its solved `q,lambda` proves stationarity of a **supplied** KKT system. It does not prove that the physical CAR kernel vanishes for every state at the retained E1 background. Differentiating the physical solution would require its induced jets. A conservation law likewise cannot identify all unknown lower-order, returned-child and contact coefficients by itself.

## Complete affine CAR tangent and minimal state data

In normalized finite CAR coordinates let `Gamma=G conjugation`, `H=Herm(Delta)`. Variations satisfy `X=X^dagger` and `G conjugate(X) G^dagger=-X`. Charge compatibility is block dephasing; family-only variation has support in the charge-doubled `Q_mu`. When these owned symmetry projections commute,

```text
S = Q_mu E_charge((H-G conjugate(H)G^dagger)/2) Q_mu,
Re Tr(X Delta) = Re Tr(X S) for EVERY admissible affine X.
```

The projection is orthogonal for the real Hilbert-Schmidt pairing. Necessity on the complete finite affine tangent follows by taking `X=S`; sufficiency follows from the pairing equality. Mixed-interior finite covariances permit small variations in both signs. A finite `I/2` argument is not promoted to a continuum Hadamard state.

In canonical Gamma-swap particle/conjugate-charge blocks, with `H=Herm(Delta)`,

```text
X = diag(A,-conjugate(A)), A=A^dagger, A=Pi_mu A Pi_mu,
K_mu = Pi_mu(H_pp-conjugate(H_hh))Pi_mu,
S = diag(K_mu/2,-conjugate(K_mu)/2),
Re Tr(X Delta) = Tr(A K_mu).
```

For a general compatible `G=[[0,V],[V^T,0]]`, the lower tangent is `-V^T conjugate(A) conjugate(V)` and the particle kernel is `Pi_mu(H_pp-V conjugate(H_hh)V^dagger)Pi_mu`. The implemented full projection retains this intertwiner; the simplified canonical block formula is not imposed on it.

Off-charge/family and Gamma-even pieces are annihilators. Reset compatibility is `X_child=U_R X_event U_R^dagger`; it does not impose the additional restriction `[X_event,U_R]=0`. No fixed-charge expectation or fixed occupation is added to charge compatibility.

For independent row kernels `K_mu,alpha`, the smallest number of independent finite/smeared state moments is

```text
dim_R span{K_mu,alpha}.
```

This is not the matrix rank of one kernel. A scalar row consumes one moment even when its kernel has large operator rank. Relative moments `Tr((C-C_ref)K)` are legitimate when the smooth difference can be paired; absolute `Tr(CK)` may still need an owned subtraction. The code returns an exact independent subset and row coefficients for supplied rational kernels.

Pure-state tangents add `CX+XC=X`. A zero local projection at one pure covariance proves stationarity there, not independence over all pure states. Continuum conclusions require actual smoothing/domain/tail justification. None of these restrictions licenses a physical verdict from one arbitrary test variation.

## What the retained E1 operands actually determine

| Consumed contribution | Actual status |
|---|---|
| Normal Dirac Green form | Frozen exact state-uniform zero; read for bookkeeping only |
| Internal EM normal current | Frozen exact state-uniform zero; read for bookkeeping only |
| Independent fermion reset density | Owned zero; does not set bulk stress/current zero |
| Full oriented stress including metric/spin/measure/lower-order/domain variation | Formal density derivative above; complete actual E1 coefficient kernel unpopulated |
| Returned-child/source/multiplier canonical row | Complete supplied-block formula above; actual same-E1 physical blocks/contacts unpopulated |
| Noether current | Contraction of that complete row; physical derivative unpopulated |
| Integrated event Hamiltonian | Separate consumed readout; not supplied by the Noether jet helper |
| Total physical `Delta_B`, tangent projection and moment rank | UNEVALUATED, not zero |

The [source receipt](../artifacts/muon_birth_covariance_sensitivity_20261008/operator_owner_receipt.json) binds every conclusion to current source hashes and symbol spans. AE3's resolved `[T_nn]=0` law explicitly belongs to the spatial enclosure and excludes the reset locus. The available metric/common-A Dirac body is a later `C2_step1222` compact-probe calculation. The actual E1 98-coordinate states contain geometry/rates/lapse/shift, rather than the six supplied physical AE4 blocks and their complete directional contacts. Different frozen lapse/ADM samples do not prove a nonzero stress defect; their correct geometric/domain pullback could cancel them.

Consequently the exact next operand is **`K_E1,alpha^complete`**, the complete one-sided action-variation kernel pulled to the common CAR domain, including returned-child/source/constraint/domain contacts for each independent consumed row. This is a producer/evaluation requirement in the existing action architecture. It is not a request for an additional seam action, a new common-A identification, a full history or a selected vacuum.

The dependency is direct: the CAR projection is linear in the complete kernel. The two frozen zero summands constrain neither the complementary projected kernel nor its rank. Solved conditional KKT stationarity constrains a supplied solution, not an unpopulated physical operator. Those checks establish neither A nor B, and choosing `C` does not establish an operator identity. This is a bounded inventory/derivation result, **not an impossibility theorem for constructing the operator from the retained action equations**. No specific nonzero physical sensitivity is claimed.

## Downstream and claim scope

Physical I_phys has not passed. The mechanical formation mode, energy test, full inertia, displacement, seven-port source, physical KKT base, six derivatives, `h_psi`, `z_psi`, resistance/inertia jets, heat length, AE4 heat, relative zeta/eta, induced action, photon response, paired heat and Pauli value remain unevaluated. No available physical contraction is intentionally withheld.

Fixed-complete-family `HeatPencil` still has no independent covariance operand. Unknown physical birth/source/domain selection is separate from heat evaluation once the entire sourced operator is supplied. This audit propagates no automatic covariance error into native heat and creates no second child vacuum. If an actual projected birth kernel survives, its moments will use the existing chain `Q_mu V_C2 U_R C_C1,E1- U_R^dagger V_C2^dagger Q_mu`.

| Label | Scope |
|---|---|
| DERIVED | Exact complete affine CAR dual projection and moment-span criterion; literal Dirac density variation; complete canonical-row chain rule and single booking of Noether/contacts |
| EVALUATED | Exact symbolic product-rule residual and current source/hash/span audit; frozen identities read |
| CONTROL_ONLY | Supplied exact finite algebra in focused tests; no physical E1 kernel or state selected |
| UNEVALUATED | Actual complete E1 kernel, `S_B`, rank/moments, physical birth and downstream values |
| OWNER_DEFINITION_GAP | None asserted here; existing theory/action/composition owners are defined |
| UNDETERMINED_OPERATOR | Complete actual E1 directional row-kernel values are unpopulated in the inspected producers; no impossibility theorem is claimed |

## Reproduction and error scope

```text
python -m pytest --noconftest -q tests/test_muon_birth_covariance_sensitivity.py
python scripts/replay_muon_birth_covariance_sensitivity.py --out artifacts/muon_birth_covariance_sensitivity_20261008/run_1
python scripts/replay_muon_birth_covariance_sensitivity.py --out artifacts/muon_birth_covariance_sensitivity_20261008/run_2
```

Actual commands, outputs, exit codes, deterministic product comparisons, input hashes and publication audits are recorded in [verification.json](../artifacts/muon_birth_covariance_sensitivity_20261008/verification.json). Exact symbolic and rational algebra has no floating rounding error. Its finite supplied scope does not certify an uncomputed continuum physical kernel. Source-read path errors are logged separately from mathematical checks. Historical inputs and frozen predictions remain unchanged.

Focused output: **23 passed in 1.77s**, exit0. The status, forbidden-claim, frozen-integrity and public-readiness audits returned `passed:true`; the existing precision gate returned `PASS: precision gate verified (1.066e-14 <= 1.000e-13)`. These repository checks do not certify the unevaluated E1 sensitivity. This continuation is left uncommitted because the required physical A/B result was not established; PR #465 remains at the starting head.
