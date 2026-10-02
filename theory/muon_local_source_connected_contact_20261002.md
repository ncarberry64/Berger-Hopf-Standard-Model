# Eight-lift local photon source and its connected contact

2 October 2026. Continue PR #465 at
`1e66ee87a3bc3ace8f907015f091135815bbcd89`; scientific reference
`524ed90689bd5923c249bba2e699abf627e703cd`.
Checkpoint: `BHSM_MUON_LOCAL_SOURCE_COMPLETE_CONTACT_524ED906_20261002`.

The new executed object is the actual **local M4 b-source insertion and its
common-child form actions**, including the previously unrepresented n=2
contact output. It is not a complete native AE4 operator, induced response,
physical muon state, or anomalous moment. The earlier index-8 result,
K_Q=(2/3)K_component, pointwise Lambda(1+X_eta^3) weight, arrays, replays,
audits and frozen conditional local contributions are preserved.

## Coordinate and actual local insertion

Differentiate with respect to b, with the history held fixed in the direct
source derivative. The retained relations are

\[
 \beta=T_b b,\quad A_Q=\sqrt2\,\beta,\quad
 T_b=(2\pi^2R_4)^{-1/2},\quad f_R=T_b/R_4=(2\pi^2R_4^3)^{-1/2}.
\]

The coordinate one-form is T_b Y_A b_A; its orthonormal coefficient is f_R.
No second volume conversion or 2/3 action-index factor multiplies the vertex.
An A_Q derivative would instead be the beta derivative divided by sqrt2.

`ae31_c2_local_em_ward_identity._gamma_matrices()` supplies the +--- Dirac
Clifford matrices. The explicit unitary with columns
U=(1/sqrt2)[[I,I],[-I,I]] puts them in the saved (L,R) order, with
gamma5=diag(-I,+I) and alpha_a=diag(-sigma_a,+sigma_a). Thus the actual
source is

\[
 \Xi_A^{(4)}=f_R c_{src}(Y_A)Q,\qquad
 \gamma^0_{LR}\Xi_A^{(4)}
 =f_R V_A,\quad V_A=Q\,\mathrm{diag}(-J_A,+J_A).
\]

This matches `fermion_body.photon_source_generators()` and the saved
`canonical_B_H_photon_source_unit` to Frobenius residual
1.1749496091904413e-15. No sign or i is chosen to obtain this agreement:
c_src is the source derivative Q gamma^a of the retained local action.
Multiplication by gamma0 converts the covariant bar-psi action to the
canonical chi-dagger B_H chi action; it is not a new normalization.

`charged_lepton_qem_ledger()` gives Q_mu=-1 on both physical Dirac chiral
components, while the all-left-Weyl e_c slot has +1. Its conjugate gives
the right charged lepton. Both charge sectors are kept. In the supplied
Clifford basis, the field charge-conjugation representative is i gamma2 K;
its overall phase cancels in conjugation. Combining it with
Y_nmk*=(-1)^((m-k)/2)Y_n,-m,-k gives the stored C_input and C_output.
The evaluated identity C_out conjugate(Xi_Q) C_input-dagger=Xi_-Q has
residual 5.384295521873979e-15. This representative does not choose a CAR
covariance, Feynman state, or a massive neutral pole.

The concrete angular input is the saved `angular_currents.npz` produced by
`angular_overlap.first_nonuniform_overlap()`: its eight real gauge lifts,
Cartesian transverse columns, Wigner labels and real-basis transform are
consumed directly. That old producer and its tests were not rerun.
`full_local_source()` uses the same normalized Gaunt equation to extend the
action to all one-source output modes, without changing a source mode.

## Evaluated connected complement and form actions

The input spatial levels are n=0 and n=1 (10 Weyl components, 20 LR
components). A photon coefficient has Wigner spin 1/2, so its product with
these inputs has only n=0,1,2. The full rectangular Xi has 56 output and
20 input components. Its n=2 output is saved explicitly. This proves finite
support for **one action on these inputs**, not a resolvent, repeated-action
or native heat tail bound.

For the actual input span, the complete source-pair contact is

\[
 G_{AB}=\Xi_A^\dagger\Xi_B+\Xi_B^\dagger\Xi_A.
\]

The discarded n=2 output contributes to this Gram even though it is outside
the saved 20-component compression. Let P0 have rank4 and P1+ rank12 in
the saved LR carrier. The real complete eight-mode addition theorem gives
sum_A Xi_A-dagger Xi_A=8I. The n0 inputs map only into P1+; Hermiticity
and equivariance imply sum_A V_A P0 V_A=(8/3)P1+. Therefore exactly

\[
 P_{1+}\sum_A G_{AA}P_{1+}=16P_{1+},\quad
 P_{1+}\sum_A G_{AA}^{ret}P_{1+}=\tfrac{16}{3}P_{1+},\quad
 P_{1+}\sum_A G_{AA}^{n2}P_{1+}=\tfrac{32}{3}P_{1+}.
\]

The connected complement carries **two-thirds** of the summed diagonal
contact on the generated n1+ columns. This ratio is derived from the
addition theorem and representation dimensions, not fitted from the
numerical trace. It is unrelated to the earlier quadratic-action conversion.
The complete-contact residual is 2.0234709331072518e-14 and the projected
n2 sum-rule residual is 1.6663704229186144e-14. The n2 action on P_cur has
Frobenius norm 7.9999999999999964. These residuals are rounding observations.

The evaluated test columns are the actual saved E0 and its current images:

\[
 \Phi(\tau)=[E_0,f_R V_0E_0,\ldots,f_R V_7E_0].
\]

E0 is a canonical n0 test frame, not a physical muon LSZ injection. These
are local restrictions/test functions; their global native admissibility
is not asserted. All 48 nodes and 47 finite-core segments are retained,
without imposing a new condition at the last cached node.

On this child contribution use the saved B_H=i partial_tau-H, with
H=R4^-1 K_kin+m K_mass, and q=norm(gamma0 B_H Phi)^2=norm(B_H Phi)^2.
The common-domain derivatives are evaluated directly:

\[
 q_A=\langle\Xi_A\phi,D_0\psi\rangle+
      \langle D_0\phi,\Xi_A\psi\rangle,\qquad
 q_{AB}=\langle\Xi_A\phi,\Xi_B\psi\rangle+
         \langle\Xi_B\phi,\Xi_A\psi\rangle.
\]

The local direct connection coordinates are affine, so local Xi_AB=0.
This is not a certified zero of native eliminated/interface contacts.
The geometric pairing and these test columns are held fixed under direct
b differentiation; local M_A,M_AB are consequently zero. Native M jets,
pairing pullbacks and source-dependent test/LSZ injection jets are not set
to zero.

For columns f_R^i U_i and f_R^j U_j (i,j=0 or1), the first form retains
the kinetic term -f_R^(1+i+j) R4^-1 U_i-dagger{K_kin,V_A}U_j and temporal
term +i(3/2)(i-j) H_affine f_R^(1+i+j) U_i-dagger V_A U_j.
The mass first-jet coefficient vanishes by {K_mass,V_A}=0; no numerical
mass is needed or selected. This holds for the retained family mass
endomorphism because it commutes with this family-central charge.

The temporal profiles use the already-retained affine-logR reconstruction
on each proper-clock segment. Exponential moments are integrated directly
with expm1/exprel, rather than a new history solve or trapezoidal surrogate.
The full arrays include first forms per segment, integrated q_A and q_AB,
the n2 subset, the test Gram M, node source actions and source actions on
all 47 actual midpoint-generated profiles.

The integrated generated-column summed contact trace is

```text
[0.000199877558570605411422651188565335877446227350 +/- 3.65e-49]
```

and its n2 subset is

```text
[0.000133251705713736940948434125710223918297484900 +/- 2.43e-49].
```

These are action-coordinate child test-form contractions, not dimensionless
anomalous moments. The Arb192 balls certify the exact representation sum
rules times exponential moments of the exact cached binary64 history inputs.
They do not certify history/interpolation error or the full numerical
matrices, and they are not physical total-uncertainty bounds.

## Common domain, interface evidence, and first absent parent map

On each compact finite core R4>0 and the profiles are bounded. The local
insertion is therefore a bounded zeroth-order perturbation. It leaves the
already-owned first-order principal symbol and Green form unchanged;
bounded perturbation preserves a supplied closed first-order domain V.
The finite angular evaluation has a common H1 proper-clock domain. It
does not require the old 20-mode space to be invariant under multiplication.

For the positive realization, q_b has this same form domain when the
insertion is bounded on the entire owned Hilbert space. Its **strong**
domain is still {psi in V:D_b psi in Dom D_b-dagger}; it is not declared
source independent. Source conormal/flux changes must be derived from the
same form. The old unsourced squared-domain flux graph is not reused as
a proof of zero variation.

`ae2_covariant_seam_response.transition_covariant_derivative()` supplies
dU+A_child U-U A_event. At fixed bundle transition its connection variation
is a_child U-U a_event=0 after the base pullback. If U varies, retain
d(delta U)+a_child U+A_child delta U-delta U A_event-U a_event.
The AE2 Gamma0 graph and smooth internal-enclosure transmission are preserved.
The evaluated reconstructed child mesh source/test traces have zero jump.
This is a child-mesh result, **not** a measured positive-parent/reset residual.
The latter are null because the parent one-form is not supplied.

The first concrete unevaluated map, on the given boundary one-form, is

\[
 \boxed{\mathcal E_{54,Q}^+:a_A^{(4)}=T_bY_Ap(\tau)Q
                  \longmapsto A_A^{(5,+)}}.
\]

Input: the eight retained angular one-forms and their temporal profiles
on M4. Output: admissible current positive-parent connection one-forms,
with the owned M5-to-M4 trace, reset compatibility and gauge form domain.
Only their Clifford actions on the required generated profiles and connected
complement are needed; a sufficient contracted representation can replace
a complete extension kernel.
`unified_parent_boundary_functional()` states the single bulk Hessian and
boundary trace; `weighted_parent_operator()` states the pointwise local
weighted gauge form. `assemble_stratified_direct_sum()` accepts sector
blocks, and `microscopic_owner_contract()` fixes the owner and geometric
trace. None of these inspected functions produces this nonzero positive
parent source one-form or its current source-extension arrays.

If the owned source path is stationary parent elimination, the required
equations are L5,Q^+ E a=0, B5 E a=a, E a in the owned parent domain, where
L5,Q^+ is the same AE4 quadratic variation including its induced response.
This conditional equation is not adopted as a new harmonic-extension,
Wick, cap, or boundary prescription. The retained source pullback must
actually specify it or an equivalent map. A wall spinor injection u0 U54
alone cannot determine the missing gauge one-form.

After it is supplied the actual Clifford/trace identification must obey
T54 c_src,5(E a)Q=c_src,4(a)Q T54. Its residual and the reset-source residual
can then be evaluated. The owner is selected, but this positive-parent
source realization is uninstantiated in the recovered route. It is not
merely an unspecified long numerical solve, and the checkpoint does not
claim an exhaustive absence theorem over unrelated evidence.

This missing map prevents the parent/cross-stratum Xi and required Xi_AB
and pairing/domain jets from entering the induced form. The new local
q_A/q_AB cannot replace that form or be added again as an independent
primitive term of a second determinant.

## Finite-E1 consumer and what was executed

The existing `HeatPencil.mixed()`/`frechet_second_response()` consumer needs
the actual same-owner positive body and source jets. With both K and M,

\[
 A_A=M^{-1}(K_A-M_AA),\quad
 A_{AB}=M^{-1}(K_{AB}-M_{AB}A-M_AA_B-M_BA_A),
\]

\[
 \Gamma_{AB}=\mathrm{STr}(DQ[A_B]A_A+QA_{AB}),
 \quad Q=\tfrac12 A^{-1}e^{-\ell_\star^2A},
\]

plus the owned length/domain/completion jets when applicable. The native
parent slots remain null. Thus no native E1 evaluator or K+sM source solve
was run; no canonical child norm or old scalar potential-four/Lambda-only
cache was substituted into it. Native length, strong subset, grading,
relative-zeta/eta subtraction and finite local/native matching are preserved.

New numerical source, contact and form arrays were executed once. Three
focused tests passed in 0.94 seconds: source/frame/conjugation compatibility;
independent SU(2) Haar quadrature including n2 (no Gaunt routine in that
check); and direct first-order pairing on the actual history/test columns.
The latter uses a nonzero mass solely as an arithmetic control to check its
cancellation, not as a physical operand.

An initial Haar test used an overly narrow 5e-14 Frobenius tolerance for
864 summed binary64 quadrature terms. Its observed difference was
9.360815676716553e-14; the 2e-12 rounding-check tolerance and passing result
are recorded, without calling either a rigorous physical bound. A focused
independent review also corrected the reset-equation metadata. The actual
source/form functions and numerical arrays were unchanged. Their original
code identity and cache hashes were verified before two identical final
metadata/materialization replays; no old calculation was repeated.

The original passing publication audits are inherited under the user's
instruction to preserve them without rerunning. New source/layout tests and
scoped diff checks are recorded separately; no new global-audit pass or
full-suite pass is claimed. The primary tree and unrelated newer work are
preserved. New files extend the existing isolated PR #465 branch.

All six physical native ledger entries remain null: native_bulk_heat,
state_variation, contact, domain_boundary, completion_counterterm,
strong_within_native. The evaluated child contact is not an evaluated
physical native ledger entry. Physical a_mu, g_mu=2(1+a_mu), and total
theoretical uncertainty remain null; no experimental comparison is used.
Later renormalization, three physical transfer directions and post-division
soft-limit bounds are required but were not used to delay this local source
calculation.

Frozen local inputs remain a_mu_QED_local=0.00116550200495813, calibration-only
standard uncertainty=1.79e-13, 0<delta_a_mu_h_local_1<3.500331e-9, and
0.0011655039493<a_mu_selected_local<0.0011655109506. The calibration is
alpha inverse=137.035999084 with standard uncertainty=2.1e-8 and the other
original conditional inputs fixed. The selected-local interval is already
combined, and no component or native contribution is added again.

This code is muon realization data using the existing child-to-observable
machinery. It does not generalize these spin, source, state or formation
assumptions into a second universal framework.

## Reproduction and next operand

Standalone, from this directory:

```text
python replay.py --output <new-directory>
python -m pytest test_muon_local_source_jet.py -q
```

Repository layout:

```text
python scripts/replay_muon_local_source_jet.py --output <new-directory>
python -m pytest tests/test_muon_local_source_jet.py -q
```

The fresh replay evaluates the small new source/form calculation. To reuse
the original validated numerical cache, use the explicit cache arguments
in the saved replay receipt. Every output directory must be new. The code
verifies cache input, code scope and output identities before reuse.

Exact equations, input/source SHA-256 hashes, revisions, relevant source
diff, stage arrays, verification and publication receipt accompany this
report. Numerical/interpolation, native operator/domain, complement for
heat/resolvent, state, finite subtraction and theoretical uncertainties
remain separate from fixed-input arithmetic.

**One next operand:** actual values of E_plus_54_Q on these eight boundary
source profiles, with its owned trace/domain realization. Use them to
materialize the parent/cross-stratum source forms, evaluate the same AE4
induced response, and then apply the completed K+sM with complement control.

The publication-layout source tests also passed: 3 checks in 3.12 seconds.
A quantitative full-M4 finite-core multiplier bound is recorded in
`verification.json`: each unit b-source norm is at most sqrt8 sup(f_R),
using the exact addition theorem and the saved affine-logR minimum.
This supports the common first-order child-domain argument beyond the
finite angular compression; it is not a positive-parent lift bound.
