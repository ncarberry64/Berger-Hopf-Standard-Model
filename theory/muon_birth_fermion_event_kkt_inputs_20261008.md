# Physical E1 fermion-family inputs to the retained event jet solver

The first genuinely unavailable physical argument is **`P_F`, derivative order 0**, exactly **`parent_jet[0]`** of `solve_retarded_event_kkt_jet`. It is the incoming C1/branch23/E1-minus parent quadratic trace/traction block `H_pp,F`, before child elimination. Its value is null. This is an evaluated input-availability result, not a missing assembly definition or a covariance-selection result.

The existing solver and Noether implementation remain unchanged. No Green cancellation is substituted, no synthetic event solve is run, and no unavailable matrix or derivative is zero-filled. Physical traction jets, the complete CAR sensitivity and minimal state moments therefore remain unevaluated. The existing first-input stop occurs before a physical `H_eff` can be formed.

## Publication of the preserved CAR milestone

The user authorized committing the current CAR milestone exactly as it stood. Commit **`86a602c8c4b357d6e13dd4409ee5e2f1bcb37e1c`** advanced PR #465 from `a6e3ceebb0a9b8322be333c7be116a01ca6b837d`. HEAD, fetched origin and the GitHub PR head agreed; the worktree was clean before this separate calculation began. All twelve CAR files were preserved, including its 23 passing tests, byte-identical replay products and five passing repository audit receipts. Its original statements that the draft was uncommitted remain historical receipt contents, rather than current Git status.

The staged whitespace check reported one existing blank line at the end of the CAR verification JSON. It was preserved under the explicit instruction to commit the milestone unchanged. The new calculation's commands and publication evidence are recorded separately in [verification.json](../artifacts/muon_birth_fermion_event_kkt_inputs_20261008/verification.json).

Starting head for this calculation: `86a602c8c4b357d6e13dd4409ee5e2f1bcb37e1c`. Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`. Branch: `codex/muon-parent-maxwell-density-review`.

## The six existing arguments, on one incoming domain

The [retained callback](../src/bhsm/interface/ae4_event_response_jet_integration.py) already constructs the retarded child reaction, KKT solve, four traction jets and their residuals. The new module is an input receipt and direct handoff guard; it adds no assembly equation.

| Existing argument | Requested operands | Numerical entries |
|---|---|---|
| `parent_jet` | `P_F, P_F,s, P_F,ss` | null, null, null |
| `coupling_jet` | `B_F, B_F,s, B_F,ss` | null, null, null |
| `child_retarded_jet` | `L_F, L_F,s, L_F,ss` | null, null, null |
| `response_jet` | `C_F, C_F,s, C_F,ss` | null, null, null |
| `source_jet` | `J_F, J_F,s, J_F,ss` | null, null, null |
| `response_target_jet` | `d_F, d_F,s, d_F,ss` | null, null, null |

Here `C_F` is the response operator, not a CAR covariance. Derivative orders are `(0,1,2)`, rather than Taylor coefficients. For parent dimension `n`, child dimension `m` and response dimension `r`, the callback requires Hermitian `P_F` matrices of shape `n×n`, `B_F` of shape `n×m`, invertible base `L_F^R` of shape `m×m`, `C_F` of shape `r×n`, and vectors `J_F[n]`, `d_F[r]`. Its adjoints assume the inherited action pairing is already represented in normalized common-domain coordinates. No geometric 98-coordinate Gram or older compact-probe Gram is substituted for that fermion trace pairing.

The physical input inventory binds incoming C1/branch23/E1-minus and outgoing C2/branch24/E1-plus to the same event. The reset pullback, opposite normal orientations, charge-conjugate doubling, family projectors, measure/metric/spin variations, additive Yukawa terms, source/response contacts and moving trace/domain variation remain requirements of the numerical input producer. These are the action derivatives established in the CAR report; naming them does not manufacture their numerical matrix entries. The real source direction `s` is not replaced by a chosen control direction or zero derivatives.

The exact owned zero of the independent fermion reset surface density is recorded with AE2 provenance. It makes **none** of these six arguments zero. Likewise, zero-background HS contractions do not remove their retained higher vertices or sourced response rows. No unavailable entry carries zero provenance.

## What `P_F` means and the available incoming producer

`P_F=H_pp,F` is the parent block of the common-domain quadratic trace functional, with parent traction `P_F q_F`. In a boundary realization, the retained parent interior is eliminated while the incoming event trace is retained. It is distinct from the stress variation kernel, the bulk differential Dirac operator, `P_strat=D_strat^dagger D_strat`, and the already child-reduced `H_eff`.

There is an executable incoming product-Dirac component in [aether_forward_channel_transfer.py](../src/bhsm/interface/aether_forward_channel_transfer.py):

```text
A = d_tau+W, W=chirality*lambda_spatial*exp(-x_C1(tau)),
K = A^star A,
Phi' = [[-W,1],[-z,W]] Phi,
M_form = [[a/b,-1/b],[c-d*a/b,d/b]],
M_f = M11 = d/b on the retained external zero-birth-source reference.
```

`product_dirac_compact_history_weyl_jets` consumes `log_radius_jets(rho)` and `proper_duration_jets`, with `base`, `first_left`, `first_right`, `mixed_second`. `restrict_two_boundary_weyl_to_dirichlet_birth_jets` performs the existing birth-trace restriction. Thus the incoming response definition is closed; no new boundary law is requested.

The inspected production caller is a Laurent-germ convergence witness using an affine terminal radius and durations `1e-3` and `5e-4`. It is not an actual incoming coefficient callback. The finite-amplitude incoming packet supplies a parametric interval family with `positive_member_selected:false`; its proof-box edge is explicitly not a physical endpoint. Neither that edge, a constant/affine interpolation nor an interval midpoint is selected here.

The actual refined endpoint supplies geometry/rates/lapse/shift but no numerical incoming arm duration, interval coefficient callback or complete fermion parent trace matrix. The full `P_F` must also retain LR/Higgs/gauge/HS/internal composition and the action pairing/statistics; a separated lowest product-channel scalar alone is not that matrix.

The operator's interval dependence is mathematical, rather than a generic request for a full history. Differentiating the retained transfer equation gives

```text
delta Phi(1,0) = integral_0^1 Phi(1,rho)
                delta(T G(rho)) Phi(rho,0) d rho,
delta M11 = (b delta d-d delta b)/b^2.
```

On a fixed-duration Dirichlet test solution `u(0)=0,u(T)=1` of `(A^star A-z)u=0`, its form derivative is `delta M11=2 Re integral (A u)^star(delta A)u d tau`, with additional owned terms for moving duration/domain. The actual incoming coefficient realization and arm duration enter this response. This does not prove arbitrary histories physically admissible or rule out deriving the required callback from the action orbit; it identifies the numerical input absent from the inspected producers.

The older incoming envelope is not rejected merely because its endpoint hash differs. The retained weighted displacement of the refined endpoint is `2.6812120877544624e-13`, below the older terminal action radius `6.2e-13`. Subject to its theorem/domain assumptions, that envelope can cover the refined endpoint. It still supplies a family enclosure rather than the actual point operator required by the finite callback. Details, input hashes and source spans are in [parent_operand_receipt.json](../artifacts/muon_birth_fermion_event_kkt_inputs_20261008/parent_operand_receipt.json).

## Numerical alternatives inspected before stopping

The incoming negative-axis product-channel enclosure is approximately `[5.375724686360878e44,4.654941939686264e45]` at its unselected proof edge. It is not a physical `P_F` value.

The real outgoing C2 Friedrichs carrier has lowest-channel Weyl values `6769.190672162356` and `6772.205986753091`, with affine72 first jets at `n=0,z=-1`. Its domain is the outgoing accepted C2 canonical-stop carrier, family-central before full internal composition. It does not supply the incoming C1 parent block, mixed coupling or complete second jet.

The C2 1222-segment product-Dirac K/M and reduced LR/HS V/Q forms are available local pieces on another arm/source scope. The event materializer's fermion `1×1` parent value `2.22` comes from its explicitly synthetic formula `1.7+0.13*sector_index`. Its genuine particle-fiber attachment is expressly not inserted into that witness. The jet materializer similarly supplies synthetic triples. None is passed to the physical call.

The other five arguments are also unbound at this actual E1 scope in the inspected sources, but the callback stops **first** at `parent_jet[0]`. A lack of an independent seam density does not set `B_F`, retarded `L_F`, response, source or target columns to zero.

## Independent quadratic identity and its retarded condition

For Hermitian `H` and anti-Hermitian `T`,

```text
2 Re <Tq,Hq>
 = q^dagger(T^dagger H+H^dagger T)q
 = q^dagger(HT-TH)q
 = <q,[H,T]q>.
```

The sign is **`HT−TH`**. The code verifies the identity with noncommuting symbols; the focused tests independently verify a general complex symbolic two-dimensional family and exact supplied matrices. Those matrices are CONTROL_ONLY, and no synthetic KKT solve is performed.

The retained solver permits a non-Hermitian retarded child block. Consequently `H_eff=P_F-B_F(L_F^R)^(-1)B_F^dagger` need not be Hermitian. Without verified Hermitianity, the exact real quadratic kernel is

```text
K_T = H_eff^dagger T-T H_eff.
```

For `H_eff=A+iD`, with `A,D` Hermitian, this is `[A,T]-i{D,T}`. The commutator simplification cannot discard the retarded imaginary part. This is a condition on the requested identity, not a claim that the physical E1 operator has a particular imaginary value.

The explicit source term is `2 Re <Tq,J_F>=-q^dagger T J_F+J_F^dagger Tq`, linear in `q` at fixed `J_F`. It cannot be folded into a quadratic commutator without an owned dependence of `J_F` on `q`. Multiplier/contact terms likewise retain their originating action dependence and are counted once. For an actually supplied ordered one-body quadratic, `N=I-C_plus` gives the covariance sensitivity `-Tr(delta C_plus K_T)`. This rule applies to that quadratic piece, rather than to all affine/contact terms by declaration.

The physical `H_eff`, traction jets and generator are not evaluated, so no actual quadratic covariance kernel is emitted. The frozen full CAR projection and minimal-moment basis remain downstream of those physical inputs. Their value, rank, coefficients and state-independence verdict remain null. No upstream covariance selector is addressed.

## Stop, verification and scope

**`P_F` at derivative order 0 (`parent_jet[0]`) is the first unavailable physical operand.** The retained incoming parent response producer exists, but its actual same-E1 coefficient realization/duration and complete paired fermion block are not populated in the inspected inputs. The guard therefore calls neither `solve_retarded_event_kkt_jet` nor `canonical_noether_flux_balance_jet` with a substitute.

| Label | Scope |
|---|---|
| DERIVED | Existing six-argument contract, parent DtN/transfer dependency, exact Hermitian and general retarded quadratic identities, source/occupation sign |
| EVALUATED | Physical input-availability inventory, current source/packet hashes/spans, stored endpoint comparison and exact symbolic identity |
| CONTROL_ONLY | Supplied exact algebra in focused tests; no synthetic event solve or physical state |
| UNEVALUATED | `P_F[0]` first, remaining physical input entries, traction/Noether jets, complete CAR sensitivity and moments |
| OWNER_DEFINITION_GAP | None; no new E1 assembly, boundary law, source state or pairing selected |

```text
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_birth_fermion_event_kkt_inputs.py
python -m pytest --noconftest -q tests/test_muon_birth_covariance_sensitivity.py
python scripts/replay_muon_birth_fermion_event_kkt_inputs.py --out artifacts/muon_birth_fermion_event_kkt_inputs_20261008/run_1
python scripts/replay_muon_birth_fermion_event_kkt_inputs.py --out artifacts/muon_birth_fermion_event_kkt_inputs_20261008/run_2
```

The focused E1 suite passed **26 tests in 2.00s**; the preserved CAR suite passed **23 tests in 1.77s**. A prior receipt-tamper regression failed before the embedded parent receipt was bound to its hash-checked file; that repair passed the final suite. This was a receipt-validation error, with no physical solver invocation. The packet also binds the exact event sides, source slices, common-domain flag and eighteen tuple entries to their audited rows.

The two replays materialize the same eighteen nullable entries, 39 source identities, independent quadratic proof and exact first-input stop. The physical-input payload is **38,184 bytes**, SHA-256 **`6195cc50e0fc63e8d0eecc686df85b5abbcd1522c9e1ef5c709d7530851a6e5c`**; its exact symbolic identity residual is `0`, and both callback-called flags are false. Source-manifest and hash-receipt digests, byte comparisons, actual command outputs and all five repository audit results are recorded in verification.json. All twelve CAR files retain their committed content; its two replay copies retain their original identical bytes.

Exact symbolic/rational algebra has no numerical rounding error; it does not certify an uncomputed physical operator or continuum tail. The endpoint comparison uses retained binary64 arrays and weights; inherited family enclosures retain their original theorem/domain assumptions and are not converted to point estimates. Frozen CAR artifacts and historical inputs are preserved.
