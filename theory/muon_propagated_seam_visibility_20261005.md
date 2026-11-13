# Existing seam-witness visibility on the accepted parent response

Continuation from `fc612beac32e886ad8d5dde5d33cf4021d082561` on
`codex/muon-parent-maxwell-density-review`, scientific reference
`524ed90689bd5923c249bba2e699abf627e703cd`. The worktree began clean.
The existing witness, exact frozen-nodal eta enclosure, its four checks,
Dirac-bar pairing, accepted parent solution, all prior operator evidence
and frozen local contributions were preserved. No witness, source,
profile, coefficient action, history or coupled parent solve was rebuilt.

**New result:** the existing witness is visible on the accepted propagated
parent-model field at node3. Its full left and unit-Higgs output norms are
both approximately 3.50449121965181e-9 in the saved model conventions.
This is neither a native coupling nor evidence of Pauli sensitivity.
No lambda, Y amplitude, physical Higgs amplitude, wall Gram or operator
update is installed.

## Recovery and coordinate provenance

The accepted source-centered solve is `coupled_run_3` of
`muon_retained_tail_core_20261005`, not either failed earlier chart or
`run_1/tail_response.solution`. Its accepted decimal144-component solution
and the exact binary64 `tail_trace_injection` yield the actual node2 trace
x2. This agrees with its stored binary64 `solved_node2_trace` to a norm
bound of4.06e-18 under the stated decimal-export convention.

The tail producer already saves the elimination equations

\[
 x_{i+1}=-Y_i x_i+y_i.
\]

Thus this diagnostic computes, without a new tail solve,

\[
 x_3=-Y_0x_2+y_0=(a_3,c_3),\qquad
 \Psi_3=u_3\Xi a_3+p_3\Xi c_3.                              \tag{1}
\]

The **same nonzero affine source y0 is included**. x2 differs from the
old prescribed tail entrance by norm0.008191919018910185; the reconstructed
x3 differs from the earlier tail solution at node3 by0.008062313842306589.
Substituting that earlier solution would therefore answer a different
question. The new norms are ||a3||=6.069058847184023e-7 and
||c3||=0.7955163883512484.

The solved trace is in the same unprojected W/p coordinates used by the
retained element builder, with W first12 and p last12. The fixed source
basis is the stored32-to12 `independent_source_map`; it is not recomputed
by an eigensolve. The tail and witness input receipts bind the same cut,
corrected source, raw source coefficients and node3 background. Before
contraction, recomposition of those raw arrays with the saved map agrees
with the witness's wall/source columns with zero binary64 residual.
There is no independent Spin/carrier rotation or source rescaling here.
The stored source profiles already own Tb, radius and photon conventions.
No action-index2/3, charge factor, family count or extra normalization is
inserted.

## Existing witness, applied after the cancellation

The adopted mode identity used by the existing diagnostic witness is
K_L W=0. It is applied **before** any numerical contraction:

\[
 K_L\Psi_3=\eta\Pi_L\Xi c_3,\qquad
 d_3=\eta H_1^\dagger\Pi_L\Xi c_3.                           \tag{2}
\]

The quantity a3+b3 c3 is B Psi3, not the argument in (2). This distinction
avoids subtracting a large W contribution from a projected/complement
result. Y and the physical Higgs amplitude remain symbolic. H1 is exactly
the saved, same-section unit-Higgs map; it is not reconstructed or selected
by this diagnostic.

Both output arrays are saved separately. Full left levels n1,n3, and
Higgs-extracted n0,n2,n4 are retained, including the small connected n4
output. No projection back to a convenient angular subset is performed.
The existing distributed reverse remains a volume Euler action, **not a
boundary conormal**. No reverse or wall interference term enters the
frozen native operator.

For the frozen numerical inputs and accepted export rounding convention,
the validated arithmetic enclosures are

| Quantity | Enclosure |
|---|---|
| Full left output norm | [3.5044912196518093e-9,3.5044912196518105e-9] |
| Unit-Higgs output norm | [3.504491219651809e-9,3.50449121965181e-9] |
| M4-weighted left norm | [1.545148419162303e-8,1.545148419162304e-8] |
| M4-weighted unit-Higgs norm | [1.545148419162303e-8,1.5451484191623035e-8] |

The M4 Haar pairing uses the inherited scalar19.439739968060266 once.
These are positive geometric L2 diagnostics, not Lorentz scalar bilinears
or physical magnetic moments. The reconstructed full field has volume
norm0.2241775866048107 and temporal-Cauchy norm0.23834876984729617 in the
two separately retained pairings. Neither is substituted for M4.

## Error propagation and its precise limits

The calculation uses320-bit complex balls on the frozen binary64 maps and
the accepted decimal solution. Printed nonzero decimal components carry
half a last printed decimal unit of quantization error; exact printed zero
is retained as zero. This bounds the exported representation, **not** the
accepted linear solve's total error. The old80-digit equation residuals
remain model diagnostics and are not silently turned into solution bounds.

The eta interval is reused as supplied, never narrowed. Its propagated
absolute contribution to either output is at most4.632e-25. The direct
binary64 node3 reconstruction differs from the decimal/ball reconstruction
by at most6.105e-17 in coefficient norm. Its propagated visibility
differences, including the scalar interval, are at most5.387e-25 for the
full left output and4.268e-25 for the unit-Higgs output. Smallness in these
particular output directions does not remove errors in other directions.

A separate error diagnostic consumes the first cached reduced equation:

\[
 D_0x_3+L_0x_2-r_{\rm eff}=e_0,\qquad
 r_{\rm eff}=f_1-U_1y_1,\qquad
 \delta x_3=-D_0^{-1}e_0.                                    \tag{3}
\]

Here D0 is the saved first interior pivot, L0 the saved lower block, and
all later elimination/affine maps are held fixed. A validated24-coordinate
solve is used **only to bound this local reconstruction defect**; it does
not update the parent/tail solution. The residual norm is at most2.838e-11,
||delta x3|| at most1.814e-16, and its propagated contribution to either
output at most2.576e-25.

Equation (3) does not certify the full block elimination, its coefficient
errors or the continuous exterior solution. Full tail reduction/coefficient
error, inherited history/interpolation error, and continuum error remain
unevaluated. No endpoint/tube/interpolation certificate is relabeled by
this calculation. Consequently the displayed enclosures are **conditional
arithmetic bounds for the frozen model**, not total response or physical
uncertainty bounds. All these scopes are separate in `result.json`.

## Small output and the invariant-subspace check

Tangential Clifford source insertion anticommutes with intrinsic gamma5;
carrier transport commutes with it. On the four saved spin probes this
means output-left corresponds to input-right. Let R32 be the repeated
input-right projector and let S be the saved32-to12 quotient map. With the
saved Haar pairings, the source-coordinate projector is

\[
 P=G_{12}^{-1}S^\dagger G_{32}R_{32}S,\qquad
 \Pi_L\Xi=\Xi P,\qquad P_{24}=\operatorname{diag}(P,P).        \tag{4}
\]

No new rank threshold or eigenvector choice is used. The array
intertwinement and projector residuals are recorded. An invariant right
subspace would require

\[
 P_{24}x_2=0,\quad P_{24}y_0=0,\quad
 P_{24}Y_0(I-P_{24})=0.                                     \tag{5}
\]

Those conditions fail in the saved numerical model: the accepted node2
left norm is4.067397512367924e-7, and the right-to-left recurrence block
norm is6.901566643316048e-5. The y0 left component is small, but cannot
repair these failures. Because P is a Gram projector and the moment
matrices are covariant forms, the correct form-reduction defect is
P24^dagger A-A P24, rather than a plain matrix commutator. Its norms are
approximately115.15 for A,7.49545 for B, and floating-roundoff size for C,
volume M and Cauchy Ms. Geometric self-adjointness and the form defects
are recorded explicitly.

This has the expected structure of the saved action: its tangential D
flips Lorentz chirality; the p normal Gamma4 term preserves it. Their
mixed contributions in the amplitude and amplitude/time-jet forms need
not preserve chirality. The mass and pure time-jet pairings have the
separate chirality-preserving tensor form. The near-zero original load
therefore does not imply exact decoupling under propagation. This statement
concerns the saved source frame and component operator, not the full
stratified action, a physical state or a Pauli coefficient.

## Execution and continuation

New code: `muon_propagated_seam_visibility.py` and its standalone replay.
Executed: cache identity/frame checks, one matrix recurrence, existing
witness contractions, chirality diagnostics, validated arithmetic and the
small local pivot error diagnostic. No new history/field actions, full
parent solve, witness refinement, old check, wall Gram or heat action.

The first attempt's save failed because a symmetric magnitude ball near
zero was squared and square-rooted as though its lower bound were
nonnegative. Its scientific arrays are preserved in run1. The corrected
norm uses explicit nonnegative component lower/upper bounds. Run2/3 preserve
the repaired arithmetic result. Run4 is accepted and run5 materializes the
same in-memory result without another reconstruction; these correct the
form-type diagnostic to P^dagger A-A P. The initial field/contraction arrays
are unchanged.
Four new targeted checks cover trace/source/frame recovery, W cancellation,
failure of exact invariant decoupling and the near-zero norm regression.

```powershell
C:\Python314\python.exe scripts/replay_muon_propagated_seam_visibility.py --output C:\Users\carbe\Downloads\BHSM_muon_propagated_visibility_replay
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_propagated_seam_visibility.py
```

**One action-level target remains:** the joint seam identification on the
reached complement and its same-photon variation,
J_chi,j=D_Psi5 F_b[chi_j] and D_bA J_chi,j, with its actual trace/volume
and reverse role. Visibility of a proposed witness does not supply this
rule or authorize its installation. Any choice requiring that postulate
remains a proposed completion. Frozen local contributions, accepted parent
solution and native null ledger are unchanged; physical a_mu and g_mu
remain unevaluated.
