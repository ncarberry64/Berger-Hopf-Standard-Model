# Unreduced photon source jets and the native length response

Continuation of PR #465 at `229c20ff0c556ab9e6a1b74d4555a470c778dee4`;
scientific reference `524ed90689bd5923c249bba2e699abf627e703cd`.

The new result is an **evaluated local mixed source-square contact and
compact first-form/time-jet rows**, followed by the differentiated native
length rule. The complete `R_ind(v,J)` has not been evaluated. These
matrices, their norms, and the arithmetic control are not a muon anomaly.

## Preserved evidence and execution

The actual branch is `codex/muon-parent-maxwell-density-review`. Initial
status was clean, fetch succeeded, and GitHub PR #465 contained the supplied
head. The primary checkout and unrelated work were not changed. The
starting revision/status and intentional new files are recorded in
`artifacts/muon_native_induced_polarization_20261006/run_1/starting_revision.json`.

The previous 240-dimensional primitive angular form, 32-dimensional response
space, 224 current labels, three shifted solves, six checks and consumed
stored-matrix certificate remain frozen. There were **zero** replays of
earlier producers/shifted solves and **zero** native heat evaluations.
The new source evaluation took approximately0.56 seconds. Seven new targeted
checks passed. The accepted parent solution, family mass/time jets, profile,
common-A prescription, fixed normalization and local calibration were reused
as provenance and were not recalculated.

## Physical inputs, source coordinates and pairing

The source coordinate is `b`, with `beta=T_b b` and `A_Q=sqrt(2) beta`.
The saved orthonormal coframe gives the local insertion `Xi=f_R c_src(a)`
at the cut, `f_R=T_b/r`. Both this factor and the coframe/carrier conversion
are applied once. The quadratic-action index2/3 is already in the owned
primitive form and never multiplies a Dirac vertex.

The source compiler is `muon_parent_source_contact.parent_insertion`:
`i gamma_LR^a` contracted with the actual coefficients in the retained
anti-Hermitian primitive-Tr16 carrier basis. All 64 Spin4Ã—SM16 fibre rows and
columns are kept. There is no second charge-conjugate trace or family factor.
Normalized harmonics are `phi_nmk=sqrt(n+1) conjugate(D_mk^(n/2))`; their
unit-Haar pairing is the identity. No extra `1/(n+1)` is inserted.

| Input | Producer / realization | Classification and scope |
|---|---|---|
| Actual source and Clifford/carrier coefficients | saved matched-source packet; `parent_insertion` | evaluated realization data, same section/coframe |
| Cut one-form geometric pairing | frozen `M_geometric_scalar=0.959045109007034` | evaluated local scalar density; not the full stratifiedM |
|32 test directions | frozen residual-enriched frame | computational seed; no new enrichment or physical state selection |
|224 current covectors | family `Gamma_bar_complete`, frozen component packet | evaluated canonical test-current data, not LSZ states |
| Corrected compact `D0 p_A`, `D0 phi` | `parent_source_rate_corrected.npz` | frozen parent-component right-cell/Gauss model; H-rate repair retained |
| Full native source/operator/quotient action | AE4 owner and inherited domain | unevaluated; local actions are not its substitute |
| Native length and scalar energy source response | AE4 first-future impedance/core crossing rule | rule derived/adopted; values/jets unevaluated |
| Frozen local anomaly terms | unchanged `frozen_local.json` | conditional local; alpha calibration convention unchanged |

The current is a **covector**. Its local field direction is explicitly

\[
 a_J=S\eta_J,\qquad
 \eta=(S^\dagger S)^{-1}C/M_{\rm geom},\qquad
 M_{\rm geom}S\eta=J_{\rm dual}.
\]

No raw covector is used as a connection variation. This is a cut geometric
Riesz identification; it does not supply its global physical continuation.

The complex span of the frozen 32-column frame is expressed in 32 real photon coordinates using
the **existing** harmonic involution. This changes coordinates only:
the M-Gram residual is 1.61e-15 and the same-span residual is 3.36e-13.
The reality residual is exactly zero in the stored operations. The full
224-column current is treated by complex-bilinear extension of this real
Hessian, retaining the 48+192 n1/n3 coefficient order.

## Evaluated mixed contact

On the local, unreduced, fixed-frame affine connection path,

\[
 D_{vA}=0,\qquad
 C_{vA}=\langle\Xi_v^\dagger\Xi_A+\Xi_A^\dagger\Xi_v\rangle_{S^3}.
\]

This supplies the **source-square part** of the mixed form, evaluated for
32 real directions Ã—8 saved sources on all 64 fibre inputs/outputs. It
does not supply the full global `P_vJ`: the remaining pullback/domain and
`D_vJ` terms are not assigned zero. Full mixed jets are

\[
 K_{vJ}=D_v^\dagger D_J+D_J^\dagger D_v
       +D_{vJ}^\dagger D_0+D_0^\dagger D_{vJ}.
\]

`affine_source_contacts.npz` stores the factorization
`C_vJ=sum_A C_vA eta_AJ` for **all224 labels**. It preserves the whole
64-carrier action without allocating a redundant32Ã—224Ã—64Ã—64 tensor.
There are32 nonzero reached columns. Its finite-coefficient Frobenius norm
is 0.058316529673110365. The real32Ã—8 contact norm is 0.6575736489779195;
Hermiticity residual 2.15e-17. These are coordinate-dependent local operator
diagnostics, not graded heat traces, dimensionless anomalies or error bounds.
The connected n3 source action is retained (norm 1.721800503656227).

## Evaluated first-form and temporal cross rows

No stationary photon extension is demanded before unreduced differentiation.
The retained `muon_source_weak_extension.weak_extension_contract` explicitly
allows differentiating the unreduced fixed-trace functional/coupled equations.
Demanding a completed induced stationary source lift before constructing
that Hessian would be circular. A pointwise normal derivative is also not
necessary to evaluate the compact weak form below.

Use the SAME cached compact `phi` columns and eight insertion images
`p_A=Xi_A phi`, as diagnostic tests, not a native Hilbert basis or a selected
wall input. Their frozen local dependence is affine, so these tests are
held fixed in this local derivative:

\[
 K_x(p_A,\phi)=\langle D_0p_A,\Xi_x\phi\rangle_5
                 +\langle p_A,\Xi_x^\dagger D_0\phi\rangle_5.
\]

The volume quadrature, radial profiles, corrected `D0p_A` amplitudes and
time jets are consumed from the existing packet. No point/body actions or
quadrature refinement are rerun. For the second product the complete
angular-field adjoint includes the saved weight reversal and phase:

\[
 (\Xi^\dagger)_{mk}=(-1)^{(m-k)/2}\Xi_{-m,-k}^\dagger.
\]

The builder evaluates amplitude, left-time and right-time rows separately,
retaining the full output before pairing. `compact_weak_first_jets.npz`
contains the 32-direction rows and their complex-linear 224-current versions.
The local norms are `||K_v||=1.2354479551530708`,
`||K_J||=0.19919498467801033`, and both temporal cross norms are approximately
0.223121527065135. A nonzero checked entry is
`K_v[7,2,1,3]=-0.02235799257268061+0.0005495312412234953 i`.
The independent test sums the actual coefficient products node by node.
Reverse local rows are the adjoints in this fixed positive form pairing;
this does **not** impose reciprocity on a retarded reduced response.

These are radial integrals at the inherited cut in the frozen nodal/Gauss
model, not time-history elements or continuum-certified native `P_J`.
Both local `M` and local `D_vJ` jets are exactly zero only because the
unreduced geometric metric, frame and test fields are fixed and the
connection source is affine. Moving reduced embeddings/Gram matrices,
reset/material/stop/BRST and global source-map jets remain unevaluated.
The historical H=0 placeholder is not consumed. The corrected cached rate
and the declared right-cell body/interpolation errors remain distinct.

## Differentiate the owner length rule

Let `I=E_impedance`, `C=E_core`, `F=I-C`. On a simple persistent selected
first-future/support-loss branch, `F(tau_star,b)=0` gives

\[
 \tau_v=-F_v/F_\tau,\quad \tau_J=-F_J/F_\tau,
\]
\[
 \tau_{vJ}=-\frac{F_{vJ}+F_{\tau v}\tau_J+F_{\tau J}\tau_v
                       +F_{\tau\tau}\tau_v\tau_J}{F_\tau}.
\]

For `E(b)=I(tau_star(b),b)`:

\[
 E_v=I_v+I_\tau\tau_v,
\quad E_{vJ}=I_{vJ}+I_{\tau v}\tau_J+I_{\tau J}\tau_v
       +I_{\tau\tau}\tau_v\tau_J+I_\tau\tau_{vJ}.
\]

Then `ell=1/E`, `c=ellÂ²`:

\[
 \ell_v=-E_v/E^2,\quad
 \ell_{vJ}=2E_vE_J/E^3-E_{vJ}/E^2,
\]
\[
 c_v=-2E_v/E^3,\quad c_{vJ}=6E_vE_J/E^4-2E_{vJ}/E^3.
\]

If the crossing is not simple, these formulas require an appropriate
branch representation; no new crossing is selected here. Fixed geometry
alone does not establish independence of the energy/source pullback. The
retained rule does not identify which source-response components of Phi
are fixed or produce the scalar energy action. Neither zero nor nonzero
physical length jets have been established; all are `UNEVALUATED`.

For `T(c)=STr exp(-cP)`, add to the fixed-length mixed heat Hessian:

\[
 -\tfrac12c_v\operatorname{STr}(e^{-cP}P_J)
 -\tfrac12c_J\operatorname{STr}(e^{-cP}P_v)
 +\frac{T(c)}{2c}c_{vJ}
 -\tfrac12\left[\frac{\operatorname{STr}(Pe^{-cP})}{c}
                    +\frac{T(c)}{c^2}\right]c_vc_J.
\]

Source/domain/event motion belongs in the same total P-jets; it must not be
counted again. Relative-completion length derivatives are also part of the
same owner. No physical length is chosen, fitted, or set to1.

## One explicit unavailable operand

The exhibited operand is

\[
 \boxed{E_{vJ}=\delta_v\delta_J
 E_{\rm impedance}[\Phi(b);\Sigma_*(b)]}.
\]

This is one scalar contracted response per consumed direction pair, not
the sole remaining input to the full native calculation. It enters
`c_vJ` and hence `[T(c)/(2c)]c_vJ`. No theorem making that whole graded term
cancel has been established. Other native P and completion actions are
explicitly null/unevaluated in the saved ledger.

The concrete producer `native_spectral_length_contract` supplies the
first-future crossing and inverse-energy rule, but no callable scalar
`I(tau,b)` or its source jets. `seam_wronskian_lower` only combines supplied
DtN/Wentzell lower bounds; it is not that scalar energy. The retained
`H_impedance` operator ratio and `spectral_formation_number`'s supplied
impedance argument do not define the needed scalar-energy contraction.
The240-dimensional primitive photon response and 72-coordinate SpinÃ—SM
parent solution have different operators/input spaces and supply no such
energy response.

There is a precise insufficiency statement for the **displayed crossing
rule**: adding `k b_v b_J` to both I and C leaves F, the crossing/support
branch, unsourced values and first source jets unchanged, while changing
`E_vJ` by k. Thus the rule alone cannot determine its value. This is not a
new BHSM solution, a physical coefficient, or a parameter to sweep. The
needed next equation is the action-owned scalar impedance/core energy
pullback under the SAME photon source, sufficient to evaluate this mixed
response (or a derived source-independence/cancellation identity).

## Heat, completion and local ownership

The fixed-length bulk expression remains
`STr[Q(P0)P_vJ + DQ[P_J]P_v]`, with
`P0=D_stratâ€ D_strat` on the inherited zero-mode/BRST quotient and
`Q(x)=exp(-ellÂ²x)/(2x)`. Both pieces are unevaluated on that native space.
The 32 test frame is only a source seed. Multiplication by a nonzero smooth
source is **not finite rank on the continuum Hilbert space**: on an open
region where its fibre action is nonzero, infinitely many disjoint-support
smooth tests have linearly independent images. Finite harmonic support
implies finite support for one specified finite-input action, not a heat
or repeated-action complement theorem. The evaluated64-fibre contact
therefore cannot replace the graded/native trace.

The relative completion belongs to this same functional. The recovered
historical zeta identity is
`logdet_zeta(P/muÂ²)=-zeta_P'(0)-2 log(mu) zeta_P(0)`.
Its source/phase response requires the current relative reference,
subtraction and eta/domain prescription; the inspected source supplies
the identity, not their current numerical contractions. The exact
reduced-diamond boundary-zeta implementation is not substituted for the
current stratified one. No second independent determinant is added.

`owned_local_angular_operand.npz` evaluates only
`H_angular(v,J)/kappa1=F_realâ€  K_angular S eta` in the SAME source frame.
It contains the already-owned local Maxwell angular kinetic and curvature
contact terms, with their existing pointwise weight/index normalization.
It is an eligible subtraction operand, not a completed subtraction from
an unknown Gamma Hessian. Frame conversion residual 7.11e-13 is below the
propagated binary64 same-span consistency allowance 4.78e-10; neither is a
native error certificate. The whole primitive diagnostic is not subtracted.

| Ledger entry | Full-native subtraction/remainder status | Actually available |
|---|---|---|
| Primitive Maxwell | UNEVALUATED | angular kinetic/curvature subtraction operand; other components not assembled here |
| common-A/background | UNEVALUATED | shared angular background contact already in previous row; no extra addend |
| Higgs/gauge local mixed | UNEVALUATED | retained conditional prior rows, not promoted here |
| gauge-fixing/ghost | UNEVALUATED | quotient/partner actions required, not filled with zeros |
| induced heat | UNEVALUATED | evaluated local source-square/weak ingredients only |
| relative-zeta/eta | UNEVALUATED | historical identity, not current response |
| domain/interface | UNEVALUATED | inherited reset/material/stop class retained |
| completion | UNEVALUATED | same-owner completion retained, no adjustable subtraction |

No entry is marked `OWNED_LOCAL_SUBTRACTED`, `NATIVE_REMAINDER`, or
`COMMON_CANCELLED` before that operation/cancellation has been evaluated.
The complete photon response and electron-muon family heat consumer remain
unevaluated; no isolated Lorentz/angular/probe block is heated as native P0.

## Arithmetic checks and uncertainty scope

The deliberately generated 3-dimensional common-D **arithmetic control**,
with explicit test length 0.7, retains nonzero D_vJ and both moving-M terms.
Dense divided differences, a noncommuting block FrÃ©chet action, factorized
source application and proper-time quadrature agree to 4.34e-19 for its
fixed-M value. The existing 192-bit Arb HeatPencil encloses
`-0.00261262804513669149575061570783754199924178185656379924804`
for that supplied control. The moving-M control value is approximately
`-0.003723219480725369087773827411965874044566369257823251882`;
independent block-action agreement 2.60e-18. The SciPy quadrature error is
an estimate; Arb intervals enclose only the exact supplied finite control
matrices. These are extraction/arithmetic checks, never physical operands.

New actual local rows have binary64 consistency checks at their declared
frozen-component scope; no certified full-operator numerical bound,
spectral-tail bound, continuum error or native theoretical uncertainty is
assigned. The prior stored-matrix certificate is preserved and is not used
to certify these new actions. Increasing a native source-generated Krylov
space and bounding its consumed contraction have **not** been executed.

Frozen local values are unchanged:
`a_QED_local=0.00116550200495813`, calibration-only standard uncertainty
`1.79e-13`, using inverse alpha 137.035999084 with standard uncertainty 2.1e-8
and the other original conditional inputs fixed. The already-combined
selected-local interval remains `(0.0011655039493,0.0011655109506)`.
No QED/Higgs term is added again. There is no new physical a_mu, g_mu,
strong-sector value, total error bound or experimental comparison.

## Reproduction and checkpoint

From the PR worktree, use a **fresh** output directory:

```powershell
C:\Python314\python.exe scripts/replay_muon_native_induced_polarization.py --output <fresh-directory>
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_native_induced_polarization.py
```

All source/input SHA-256 identities are in `run_1/input_hashes.json`;
the actual executed source bytes are archived separately with text
conversion disabled. Source canonical-LF identities are also recorded,
so line-ending-only checkout differences do not trigger a replay campaign.
`compact_weak_first_jets.npz`, `affine_source_contacts.npz`, length equations,
ownership/domain ledgers, output hashes, test receipt and publication
receipt provide a resumable checkpoint. A context restart need not rerun
the previous photon, parent, family or calibration production.
