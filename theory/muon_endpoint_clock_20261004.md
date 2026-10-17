# Delta-free endpoint clock and consumed source/interface action

Starting revision: `a5fc2429c89e2c8e374852ac687cc9c78d1f959e`, branch
`codex/muon-parent-maxwell-density-review`, PR #465. Scientific reference:
`524ed90689bd5923c249bba2e699abf627e703cd`. The full-cap I, old nodal
I_dot, bulk/Cauchy overlaps, original local interface arrays, connected
outputs, prior certificates and frozen local contributions are unchanged.

The new result is an endpoint-value enclosure and an inherited-endpoint-tube
enclosure for the lapse rows, followed by actual n1/n3 source actions and
dependent local weak interface updates. The proof-center lapse result is not
substituted. No action Hessian, new eigenvalue solve, or 98-direction
derivative campaign was executed.

## Retained branch and endpoint enclosure

Inputs are `BHSM_N12_C2_LOHNER_STEP_1222.npz/.json`,
`BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1221.npz`,
`BHSM_N12_C2_LOHNER_GROWTH_1221.json`, and
`BHSM_N12_C2_LOHNER_RESPONSE_BALL_1221.json` under `flagship_integration`.
The producer equations are in
`audit_n12_c2_bordered_hard_response_matrix.py`,
`audit_n12_c2_exact_center_fixed_s_field_matrix.py`, and
`certify_n12_c2_cancelled_field_lohner_step.py`. These producers were read,
not replayed. Their selected branch is 24 and its orientation/reference and
state weights are retained.

The action-weighted displacement to `endpoint_predictor_center` is enclosed
by `[1.6847864734789115e-14,1.6847864734789120e-14]`. The inherited joint
domain use `1.0184939156893515e-10` is strictly smaller than the selected
domain radius `1.0267271323091184e-10`. The tube result uses that joint
radius about the original center, not the endpoint radius alone. The older
response-ball packet alone would not cover this enlarged domain.

With the inherited positive signed endpoint descriptor

    sigma_end = 1.773927204854387794910207227677695347285848247957188393603902077011601353618048897486676732531082225998046875e-20,

the clock and field are combined before intervalization:

\[
F_\sigma={b\Psi_w+\sigma V_w\over\Delta},\qquad
Y_\tau={\Delta\over N_b\sigma}W_Y^{-1}F_\sigma
={W_Y^{-1}(b\Psi_w+\sigma V_w)\over N_b\sigma}.
\]

Delta has canceled. No raw numerical eigenvalue supplies sigma. The saved
output weights in rows37:98 equal the state weights, so lapse rows reduce to
`m_tau=(b psi[37:49]+sigma response[37:49])/(N_b sigma)`.
The common signed b, sigma and lapse are retained. Interval dependency losses
are conservative; these enclosures are not claimed optimal.

The raw normalized line variation is bounded by `p1*r`, where p1 is
`fresh_line_bounds.weighted_selected_to_complement_first_variation_on_ball`.
Its output is RAW psi; no maximum output weight is multiplied again after
weight cancellation. The enlarged STEP first-response bound supplies
`||delta response||<=x1_ball*r`. For the small point enclosure, b uses the
retained first bound and centered second remainder coefficient

\[
B_2=p_2\|f_0\|+2p_1\|Df_0\|+f_2.
\]

This is a centered Taylor coefficient, not a newly asserted uniform Hessian
bound. The tube uses STEP's b and lapse intervals. Cached first actions on
the predictor displacement give convenient nominals, but intervals also
contain the centered variation range independently of those nominal shifts.
All certificates remain conditional on the retained branch/chart bounds and
their original numerical realization; continuum accuracy is not upgraded.

The exact configuration identity follows without a solve:
`Psi_q=0`, `V_q=W_q v`, hence `q_tau=v/N_b`. The physical boundary uses
`rho_b=pi/2` and `cos(2k rho_b)=(-1)^k`, so `L_nu(rho_b)=0` exactly.
An independent Arb evaluation at symbolic pi/2 encloses zero with absolute
bound below1e-35. Generic outward binary64 serialization of exact zero gives
`[-5e-324,5e-324]`; this is not a boundary residual.

## Evaluated endpoint lapse and dependent actions

\[
L_\nu(\rho)=\sum_{k=1}^{12}m_{\tau,k}[\cos(2k\rho)-(-1)^k].
\]

Across the original 64 source points:

| Enclosure | Range of L_nu over those points |
|---|---|
| Endpoint predictor value | `[4.221376555182814e12,9.634519921116314e12]` |
| Inherited endpoint tube | `[4.147113266331914e12,9.725791336569195e12]` |

These are operator/time coefficients, not anomaly contributions. Direct
Fourier values and interpolation of nodal `nu_tau` are saved separately.
On the fixed original instantaneous operands the signed correction is

\[
\delta(D_5W)=-{u\,i\Gamma^0\over2\nu}\delta L_\nu.
\]

It is applied to all retained n1/n3 source/inclusion directions, both spin
sectors and full carrier/angular outputs before the weak projection. The b
source, independent Q, and b/beta conversion remain unchanged; no 2/3 vertex
factor or new coupling is introduced.

The lapse-only weak row uses the actual existing right source action, with
its radial eta insertion, through `<delta D5W,D5p>5`. The complete local
temporal update also reconciles C_tau, r_tau, H and I_dot below; its weak row
retains BOTH first pair terms and `<delta D5W,delta D5p>5`. Angular adjoint
derivatives and their full outputs are retained. The separately saved
lapse-only row is a subset of the all-time update, not an extra addend.

| Intermediate norm | n1 | n3 |
|---|---:|---:|
| Lapse-only reached action | 1.3128222830502161e14 | 9.283055388376130e13 |
| Lapse-only local K54 correction | 3.565273488177402e13 | 3.337809380926124e13 |
| All-time local K54 correction | 3.548769709507243e13 | 3.329003930037628e13 |

These finite-array norms do not bound the global stratified operator or its
heat. The new source actions and local interface rows have been evaluated
and consumed, but are insufficient by themselves for a stationary global
exterior K/M solve.

## Same-endpoint reconciliation of other temporal coefficients

The current attachment and the same endpoint `q_tau=v/N_b` give

\[
\partial_\tau\log C=q_{0,\tau}+u_\tau+w_\tau,\quad
\partial_\tau\log r=q_{0,\tau}+u_\tau
-{A^2-B^2\over A^2+B^2}v_\tau,
\]

\[
H=q_{0,\tau}+u_{b,\tau}-\tanh(2v_b)v_{b,\tau},\quad
\dot I_{\rm action}=\int_0^{\rho_b}C_\tau\sin^2(\rho/2)d\rho.
\]

The entire-cap affine action derivative, at fixed retained instantaneous
nodal C, is enclosed by
`[1.3103412251403960,1.3103412251403965]`. The old right-cell nodal
certificate `[1.3810262615005096,1.3810262615005100]` is preserved under its
original label. The endpoint H enclosure
`[0.08877816767234148,0.08877816767234151]` lies in the inherited H interval.
The boundary proper-lapse derivative remains exactly zero. Raw N_b_dot and
the action-generated shift derivatives are retained separately.

After the radial half-density/spin terms are combined, the additional
fixed-instantaneous changes used in the local rows are

\[
\delta D_5W={u i\Gamma^0\over\nu}
[-\delta\dot I/(2I)-\delta L_\nu/2+3\delta H/2+\delta C_\tau/(2C)],
\]

\[
\delta D_5p={i\Gamma^0 p\over\nu}
[\delta C_\tau/(2C)+\delta r_\tau/(2r)-\delta H/2].
\]

Shift and source continuation are not independently changed. Shift_tau is
computed from the same multipliers/clock and saved; it does not appear in the
already-declared first-order D5W formula. The normal eta action, common-A and
instantaneous spin/angular terms remain retained. No new radial direction,
mass cancellation or wall action is selected.

The endpoint reconstruction matches the saved C, r, A and B arrays exactly.
Thus the full-cap I certificate is reused. Proper lapse and shift differ by
at most2.6645352591003757e-15 and1.3322676295501878e-15, respectively.
Old overlap certificates remain certificates of their original arrays.
The affine-cell lapse ratio hull propagates the small new input difference
without reintegration: bulk scalar is enclosed by
`[0.4851697335636420,0.4851697335636424]` and Cauchy scalar by
`[0.5521811994475889,0.5521811994475894]` for that point reconstruction.
No tube/continuum overlap certificate is inferred from this point estimate.

## Error propagation and scope

Coefficient uncertainties are propagated through the actual reached output
using a conservative finite-array Frobenius inequality
`||delta c Gamma0 Xi|| <= ||delta c||_2 ||Gamma0||_F ||Xi||_F`.
These bounds concern scalar-coefficient error on fixed binary64 matrices;
matrix roundoff and weak-form quadrature error remain unevaluated.

| Reached lapse-action error bound | n1 | n3 |
|---|---:|---:|
| Predictor coefficient enclosure | 1.642183558664121e9 | 1.161199130284457e9 |
| Inherited tube versus nominal action | 1.287525446236519e13 | 9.104179739840777e12 |
| Direct versus nodal interpolation | 1.817346909224492e11 | 1.285058323281051e11 |
| Instantaneous lapse input change, lapse summand only | 0.752220002585212 | 0.531899864772166 |

Thus even the tiny instantaneous input change is propagated, and the much
larger Fourier/interpolation discrepancy is not dismissed. Shared clock,
normalization and H dependencies are not treated as independent additive
anomaly uncertainties. The all-time weak-row norm has no certified total
error bound. Original branch numerical realization, metric representation,
continuum, global matching and connected propagation errors remain separate.

Volume and Cauchy pairings, material trace multiplier, original M4 and its
H derivative, and full projected-plus-complement field remain preserved.
Only the local primitive rows are updated. The same-owner stratified heat,
gauge/constraint, domain/interface, Higgs/seam and completion terms have not
been supplied by these rows. They remain unevaluated, never zero. No isolated
block heat or stationary conormal is claimed. Physical a_mu and g_mu remain
null; no experimental target or local calibration is used in this update.

## Execution and reproduction

One endpoint/tube contraction and dependent action/interface calculation ran
in about4 seconds. A second small error-receipt extension reused every array
and rate; no action was replayed. Five new targeted tests passed. The first
test invocation had four passes and one serializer-only assertion failure;
that test was corrected, independently strengthened at symbolic pi/2, and
rerun successfully. Earlier tests, productions, Gaussian searches and frozen
local integrals were not rerun. Input/source/output hashes and these scopes
are in `artifacts/muon_endpoint_clock_20261004`.

From the publication worktree, choose fresh output directories:

```powershell
C:\Python314\python.exe scripts/replay_muon_endpoint_clock_actions.py --output C:\Users\carbe\Downloads\BHSM_endpoint_new
C:\Python314\python.exe scripts/extend_muon_endpoint_error_receipt.py --input C:\Users\carbe\Downloads\BHSM_endpoint_new --output C:\Users\carbe\Downloads\BHSM_endpoint_error_new
C:\Python314\python.exe -m pytest -q tests/test_muon_endpoint_clock_actions.py
```

Use the new endpoint arrays in the same-owner exterior assembly on the full
inclusion plus connected trace. The locally computed rows are available now;
the saved `exterior_KM_partial.json` supplies only geometric cut pairings,
not an evaluated global stratified K/M or its stationary response. The current
endpoint coefficient no longer prevents constructing that coupled assembly.
