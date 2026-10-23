# Evaluated coupled action applications for the calibrated muon response

The actual retained E1+ Maxwell action has now been applied to every saved
photon direction in the full five-component angular representation. The
eight saved directions are **not an invariant subspace**: the maximum
uncompressed image outside their span is `28363.94`, and the Gauss image
norm is `384906.06` in the declared coefficient coordinates. An inverse of
their eight-by-eight corner cannot produce the full parent response. The
new implementation retains all 400 real angular coordinates and their
100 geometric first derivatives and material-normal second columns.

This is an evaluated action application at the retained geometric candidate,
not yet the physical native Pauli remainder. The calibrated bosonic weak
logarithm has also been evaluated and added once to the prior component
ledger. No measured anomaly, g factor or magnetic moment is a calibration
input. Frozen predictions and prior milestone receipts are preserved.

## Common action, domain and normalization

`muon_parent_maxwell_full_weak.py` implements the literal real Lorentzian
connection action on all five one-form components
`(A_tau,A_rho,A_1,A_2,A_3)` and all four unit-Tr16 internal generators:

\[
S_M=\frac12\int\{kF_{\tau\rho}^2+
e(F_{\tau i}-\beta F_{\rho i})^2-rF_{\rho i}^2-dB_i^2\},
\qquad k=er/d.
\]

The curvature expressions, including their nonlinear commutators, are

\[
F_{\tau\rho}=\partial_\tau A_\rho-\partial_\rho A_\tau+[A_\tau,A_\rho],
\]
\[
F_{\tau i}=\partial_\tau A_i-E_iA_\tau+[A_\tau,A_i],\quad
F_{\rho i}=\partial_\rho A_i-E_iA_\rho+[A_\rho,A_i],
\]
\[
B_i=2A_i+\epsilon_{ijk}E_jA_k+
\tfrac12\epsilon_{ijk}[A_j,A_k].
\]

The common geometry is the retained N12 outgoing C2 E1+ reset germ, with
no finite birth-side temporal offset. Its source identity is the existing
refined reset, not the old 1222-segment Higgs profile. The mechanical
reference is `Abar_i=sqrt(8)H_i(lambda-1)`, `Abar_tau=Abar_rho=0`.
Its time/radial first jets are derived from that same retained geometry.
This reference is not asserted to be the complete physical gauge field.

The independent addition to the geometric action is exactly

\[
S_M[\bar A(q)+a]-S_M[\bar A(q)].
\]

The subtracted mechanical curvature is already in R8. At `a=0` the extra
scalar action and both geometric derivatives vanish by this identity;
the gauge Euler row, gauge Hessian and geometric/gauge mixed block do not
vanish. The diagnostic reference Maxwell action is
`-8319.5455728175`, and is not added to R8 a second time.

The angular rule averages one under Haar measure. Tr16 is the internal
pairing, with positive real coefficient representation. The radial/time
weak pairings are not surface traces. An actual boundary cotangent is
evaluated on the face or obtained from a represented DtN reaction; an
integrated radial momentum test cannot be relabeled a wall traction.

## Full photon source application and off-shell identity

`muon_parent_maxwell_full_q_application.py` reconstructs the retained
geometry-independent `transformed_n1` and `transformed_n3` source data.
There are 20 real scalar harmonics, five one-form components and four
internal coordinates. The literal source Gram is `16/3 I8`; its maximal
angular reconstruction residual is at binary64 roundoff. The old
geometry-dependent e/r/d/Tb arrays are not imported into this application.

The reference quadratic operator preserves each Peter-Weyl shell: its
internal matrices are constant, and each `E_i` preserves n. Thus the
full 400-coordinate representation is closed for this linearization.
The eight-source compression is not closed. Nonlinear products can populate
additional even/higher harmonics, so this linear closure is not claimed
for a nonlinear truncation.

The implementation evaluates the full source image, its source corner,
Gauss components and factorized geometric/normal jets at 96 radial nodes.
It checks all eight sources against 80 same-shell gauge parameter directions,
including temporal/radial components. The required identity is

\[
S''[Q,D_{\bar A}\eta]+S'[[Q,\eta]]=0.
\]

The maximal absolute defect is `2.27e-11`, with a nonzero Euler contact
of about `1380.21`. Dropping that contact would falsely treat a
nonstationary reference Hessian as an operator on the physical gauge
quotient. Neither this Ward check nor a matrix inverse establishes a
stationary interacting base or a native heat operator.

## Intrinsic Higgs/gauge/geometry action on one coefficient vector

`muon_intrinsic_higgs_gauge_action.py` now differentiates the owned scalar
action directly, rather than accepting an uncomputed scalar residual:

\[
S_H=2\pi^2\int\{w_T|D_tH|^2-w_S|D_iH|^2
-w_V\lambda_H(|H|^2-\nu^2)^2\}.
\]

The common vector contains the geometric two-jet, real scalar coefficients,
all five gauge coefficients and, when requested, the log of the common
physical energy unit. Real scalar coordinates are
`(Re H1,Re H2,Im H1,Im H2)` without a hidden square-root-two rescaling.
Its real derivative equals `2 Re` of the complex action dual. A numerical
basis represents fields; it selects no covariance or physical carrier.

The unit-Tr16 fundamental generators are
`H_i=-i T_i/sqrt(2)` and `H_Y=-i I/(2 sqrt(10/3))`.
The spatial mechanical term is `sqrt(8)(lambda-1)H_i=-i(lambda-1)sigma_i`.
The temporal pulled-back independent connection is
`A_t+2 wall_rate A_rho`, since `rho=2 chi`. Embedding motion is counted
once; the radius is in the metric weights, not inserted again into the
unit-S3 derivative. The current numerical chart supports a homogeneous
radial normal graph. A general angular normal graph requires its full
metric-density tensor and spatial trace pullback.

The producer retains the exact common-parameter polynomial

\[
S_H=S_{H0}+\nu_{\rm action}^2 S_{H1}
+(\nu_{\rm action}^2)^2 S_{H2},
\]

including every gradient and Hessian block. It also implements
`nu_action²=nu_GeV² exp(-2 log(E_unit/GeV))` with its derivatives when the
scale is a joint coordinate. This conversion does not determine the scale
or turn its derivative into a stationarity equation. The matching row is
`G_F_measured=c_F[action]/E_unit²`, with c_F supplied by the action-normalized
charged-current response. A local tree weak identity that cancels E_unit
does not independently evaluate that response.

The body of the uneliminated Grassmann Higgs source is zero with explicit
action provenance. The quantum/native Higgs load is separate and has not
been discarded. At a supplied scalar/gauge iterate this implementation
produces actual internal, mixed and geometric action applications. It
does not declare that iterate stationary.

Independent checks use the complex doublet Lagrangian, first directional
differences, mixed Hessian differences, the scale conversion, the exact
nu polynomial and the off-shell gauge identity including its second
action cotangent. All ten Higgs producer tests pass.

## Additive calibrated weak contribution and current accounting

The bosonic leading logarithm uses the exact weak-angle polynomial from
[the primary two-loop calculation, Eqs. 10–11](https://arxiv.org/abs/hep-ph/9512369),
independently reproduced from the dipole and open-current mixing in
[the EFT calculation, Eqs. 11–24](https://arxiv.org/abs/hep-ph/9803384):

\[
a_{\mu,\rm bos,LL}=\frac{G_F\alpha m_\mu^2}{8\sqrt2\pi^3}
\frac{-65+92s_W^2-184s_W^4}{9}\log(M_W^2/m_\mu^2)
=-2.1415901496597387\,10^{-10}.
\]

Closed fermion loops, VVA, fixed-Y lepton Hgamma/HZ, QED and hadronic
sectors are excluded from this added row. No Higgs or quark Yukawa was
assigned to obtain the log. An independent 70-digit calculation differs
from binary64 by `1.00e-26`. Changing the logarithm endpoint to MZ
changes the value by `-4.08e-12`; that finite convention diagnostic is
not a bound on the uncomputed bosonic constant.

The new additive ledger consumes the published ledger and this log:

| Evaluated contribution | a_mu contribution |
|---|---:|
| Preserved QED alpha1/alpha2 and literal fixed-Y radial Higgs | 0.0011655419088320725 |
| Leptonic QED alpha3–alpha5 | 3.052798240740239e-7 |
| Rematched evaluated weak subset | 1.7592934564604527e-9 |
| Hadronic two-current LO/NLO/NNLO | 6.883273877717739e-8 |
| Connected published hadronic four-current projection | 1.019e-9 |
| Lowest electromagnetic top VP, no top Yukawa inferred | 6.096275717098775e-14 |
| Bosonic weak leading logarithm | -2.1415901496597387e-10 |
| **Evaluated subtotal** | **0.001165918585590328** |

For this subtotal, `g=2.0023318371711807` and the moment at spin
`S_z=+hbar/2` is `+4.490446171003096e-26 J/T` for mu+ and its negative
for mu-. These are subtotal accounting outputs, not a completed BHSM
prediction. The complete contribution remains
`a_mu = evaluated components + unexecuted finite weak terms + disjoint native remainder`.

The log's input gradient is added to the shared primitive gradient before
covariance propagation. The common decay-theory GF sensitivity is
`0.00013247881961500426`; its estimated standard uncertainty contribution
is `2.645802603894407e-17`, and its omitted-order size estimate is
`7.760040467675991e-18`. These quantities do not bound the native response.
The supplied-input, hadronic, truncation and arithmetic scopes remain
distinct. Unknown HLbL metrological derivatives are not assigned zero.
No complete observable uncertainty or anomaly enclosure is claimed.

## Verification and remaining production work

`scripts/verify_muon_coupled_action_application.py --tests` ran the four
new frozen producer suites: **59 tests passed in 2.83 s**, exit zero.
The receipt contains exact argv, working directory, environment, stdout,
stderr, hashes and byte-identical replay comparisons. The new combined
action solve and later numerical extensions have their own verification
records, so this count is not a claim that they were tested here.

The five repository publication audits all returned exit zero: status,
forbidden claims, frozen prediction integrity, precision and public
readiness. The unchanged precision check reports `1.066e-14 <= 1.000e-13`.
Full audit stdout and stderr are preserved in the verification JSON.

Reproduction commands from the worktree, with `PYTHONPATH=src`, include:

```powershell
C:\Python314\python.exe -m bhsm.interface.muon_parent_maxwell_full_q_application --output artifacts/muon_parent_maxwell_full_q_20261010/new_replay
C:\Python314\python.exe scripts/evaluate_muon_calibrated_bosonic_weak_log.py --output artifacts/muon_calibrated_bosonic_weak_log_20261010/new_replay
C:\Python314\python.exe scripts/evaluate_muon_calibrated_extended_ledger.py --output artifacts/muon_calibrated_extended_ledger_20261010/new_replay
C:\Python314\python.exe scripts/verify_muon_coupled_action_application.py --tests
C:\Python314\python.exe scripts/verify_muon_coupled_action_application.py --audits
```

Use a fresh replay directory to preserve existing evidence. A repository
session fixture can restore tracked artifacts changed by another process;
concurrent focused action checks therefore use `--noconftest`. This avoids
a global artifact rollback while retaining the explicit scientific tests
and publication audits.

The fullweak packet is losslessly compressed with fixed archive member
order/timestamps. All 42 decompressed arrays agree exactly with the earlier
uncompressed computation; the final packet is 3,097,435 bytes. The older
unpublished diagnostic files remain preserved. This packaging change does
not alter an operator or a numerical operand.

The next physical application must retain full source images, actual
Gauss/constraint reactions, same-action mixed response and the sourced
Dirac term including fixed `Y_l H`. A retarded computational gauge slice
must expose any nonzero consistency reaction rather than claim a quotient
identity. The branch-birth cutoff, relative zeta/eta completion, two-insertion
heat contacts, source/adjoint soft derivative, LSZ normalization and common
overlap still have to be consumed on the same physical domain. These are
continuing action applications; no independent-input obstruction or theory
definition gap has been established by their unfinished status.

| Classification | Scope |
|---|---|
| DERIVED | Same-vector Higgs/gauge/geometry two-jet, full Maxwell curvature/weak forms, Ward identity, full angular linear closure, common GF tangent |
| EVALUATED | Actual E1+ source images and Gauss contacts, geometric/normal derivatives, bosonic log and updated subtotal |
| CONTROL_ONLY | Numerical trial representations, Ward parameters and primitive-independence illustration |
| UNEVALUATED | Complete stationary interacting base and branch cutoff, native heat/relative completion and Pauli remainder, finite weak completion |
| OWNER_DEFINITION_GAP | None established |

`action_selected`, `Gate7_closed` and `complete_observable` remain false.
