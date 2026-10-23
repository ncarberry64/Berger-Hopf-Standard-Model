# Incoming C1 LR response: positive-square obstruction and constrained contraction

Baseline: `ad750077f1a3138418a2dc4ee65f7c50236b5608`, PR #465,
branch `codex/muon-parent-maxwell-density-review`. Scientific reference:
`524ed90689bd5923c249bba2e699abf627e703cd`. The incoming domain is
C1/branch23/E1-minus and the outgoing domain is C2/branch24/E1-plus.

## Result

The new action-specific calculation distinguishes the cancelling Dirac
partner from the positive adjoint square. In the retained gamma convention
the latter contains the normal first-order coefficient `-2 p0 B(m)`.
Consequently a mass-only multiplication bound cannot close the physical
incoming LR response by using the cancelling partner. A conditional
same-factor form enclosure is now executable, including the conormal
contact and amplitude weights. The scalar contribution is reduced to an
identifiable constrained adjoint contraction, with the multiplier curvature
and moving constraints retained.

An actual incoming LR response enclosure or exact cancellation was **not**
obtained. The precise first unevaluated solver operand remains `P_F`, order
zero, `parent_jet[0]`: the incoming paired-trace action response including
the additive LR contribution. Its required contracted form is stated below.
This is an evaluation frontier in an existing action, not a new action
definition gap. No physical scalar ambiguity or need to select a carrier
member/covariance has been proved. All 38 files from the three published
milestones, including the point-valued guard, are preserved.

## Action and domain recovered

The adopted collar action has the additive bridge

`S_LR=-integral_M4 dmu [bar(Psi_+) Y_f H Psi_-+h.c.]`.

Its normalized zero-mode pullback has `integral ds J |u0|^2=1`; the two-sheet
overlap is one. Its normalized directional overlap derivative is therefore
exactly zero. The intrinsic-M4 action keeps active weak-doublet `H`, active
`L_L,e_R` and fixed family `T_l`, with `Y_l=(16 sqrt(2 pi)/3969)T_l`.
The LR density contains no `D_n H`, so its **bare** scalar normal canonical
momentum is exactly zero. Scalar kinetic, induced and moving-domain
contacts remain. These zeros have action/normalization provenance in
[the source receipt](../artifacts/muon_birth_c1_lr_response_20261008/incoming_source_domain_receipt.json).

The current AE4 owner selects future retarded regularity/outgoing support,
the parent-child trace identification and the retarded child Schur response.
The inherited Cauchy/Wentzell, gravity/eta/scalar and selected zero-background
matching certificates are retained. They do not evaluate the active intrinsic
`H_C1` or its source. The historical constant reset `H_SM=0` is superseded by
event-conditioned reconstruction and cannot be copied into this calculation.

Independent Downloads/Git recovery found the evaluated eight-polarisation
Higgs/gauge source row in the 2026-10-02 connection report. It uses the explicit
conditional **local** branch `H0=nu(0,1)` and leaves its coupled scalar inverse
unevaluated. It supplies incidence/source structure, not incoming C1 Higgs
Cauchy data. The 98-coordinate incoming geometric packet has q37, velocity37
and multiplier24; its free conformal Casimir term is not an active-Higgs energy
bound. The source receipt records 17 sources/28 symbol spans and five external
hashes, including the original author-supplied M4 action. No scalar graph,
retarded prescription or whole-history absence is used as a generic stop.

## Exact LR-to-positive-operator calculation

At a fixed orthonormal spin frame/family compression, put

`M(m)=m P_R+conjugate(m)P_L=Re(m) I+i Im(m) gamma5`,
`B(m)=beta M(m)`.

In the adopted `(+---)` convention, `gamma^a M=M^dagger gamma^a`,
`B^dagger=B` and `M^dagger M=|m|^2 I`. Thus

`(Dkin+M^dagger)(Dkin-M)=Dkin^2-i gamma^a(nabla_a M)-|m|^2 I`.

The principal cross terms cancel in this **algebraic partner**. However, for
all real cotangent components the actual positive local symbol is

`(gamma.p-M)^dagger(gamma.p-M)`
` = (gamma.p)^dagger(gamma.p)+|m|^2 I-2 p0 B(m)`.

The spatial principal cross vanishes; the normal first-order coefficient does
not vanish identically. For real m it is `-2 m p0 beta`. These are coefficient
identities, with no selected physical m or momentum. They disprove replacing
the positive-square perturbation by the mass/gradient-only partner expression.
AE4 owns `D_strat^dagger D_strat`; no Wick rotation or unproved Lorentzian-body
to heat/carrier identification is inserted. The literal antisymmetrized AE2
kinetic insertion also gives zero for a beta-Hermitian mass; it cannot replace
the separate additive Yukawa density. Source-bound details are in
[the embedding receipt](../artifacts/muon_birth_c1_lr_response_20261008/lr_embedding_receipt.json).

## Form route retaining derivative and boundary terms

If the actual same-pairing/domain realization is proved to have `A1=A0+E`,
`A0=partial_tau+W`, the exact full one-end form difference is

`q1[u]-q0[u]=2 Re<A0 u,E u>+||E u||^2`,
`q0=||A0u||^2+kappa_probe^2||u||^2`, `u(0)=0`, arbitrary `u(T)`.

For regular E in that normalized trivialization, its differential difference
is `(E^dagger-E)partial_tau-E'+W^dagger E+E^dagger W+E^dagger E`.
The conormal changes by `E(T)u(T)`. Integration by parts retains
`<u(T),E(T)v(T)>`; it is already in the polarized form and is not added twice.
Hermitian E cancels the derivative principal cross but leaves its derivative,
quadratic and conormal contributions. Independent exact integrations test both
Hermitian and non-Hermitian, noncommuting E and nonzero terminal traces;
omitting the cross/contact gives a nonzero residual.

On **every** one-end form-domain vector, one-end Poincare gives
`||u||<=ell sqrt(q0[u])`, `ell=T/(3/2-S T)`. For `a>=||E||`,

`|q1-q0|<=eta q0`, `eta=2w+w^2`, `w=a ell`.

This needs no E derivative bound. The sharp sufficient condition is
`w<sqrt(2)-1`. The rational condition `w<=2/5` gives `eta<=24/25<1`, so the
same nonnegative returned-child load implies `||S1^-1||<=25 b_star`.
It is a conditional positive-seam subcase, not coercivity of the complete
retarded AE4 KKT system.

With the exact inherited duration/superpotential fractions, its sufficient
threshold begins `a<=3.2254348118165267172782941053079e44`. A conservative
short condition is `a<=3.225434811816e44` in the normalized **first-order
insertion** units. No physical a is supplied. For the whole unselected family,
the weighted condition is

`sup_lambda lambda^2 ||E_lambda||`
` <=(2/5)(3/2-S a_duration lambda_star^2)/a_duration`,

whose threshold begins `5.7076714040584085494433060985962e-16`.
The entire coupled sector must obey the baseline bound; a nonconstant Higgs
restriction is not assumed to preserve the lowest angular channel.

The imported companion's different bounded-**quadratic**-L2 route is preserved:
`d_star<=3.844885874782e-91`, `e_star^2<=8.267619165321e-46`,
`c_star<=1.922442937391e-90`, `b_star^2 e_star^2<=2.860924693214e-135`.
Its `c_star||V||<1` hypothesis still requires the actual bounded V on the
same domain. Neither this prefactor nor either threshold is a physical muon
correction. Exact fractions/outward decimal brackets are retained in the replay.

## Minimal actual consumed LR calculation

For the actual common action realization, let `V=L_full-L_car`. The zero-order
correction consumed by `P_F` is

`R_LR=E_0,L^dagger V E_1,R`
` = W-V_bi(A_0+V_ii)^(-1)V_ib`,

with `W=E_0,L^dagger V E_0,R`, and the three interior couplings given in the
replay. Against each consumed trace pair p,r only `p^dagger R_LR r` is needed.
Its primitive additive LR pairing is
`-integral_C1 dmu u_L^dagger beta M_LR(H_C1)u_R` with actual extensions and
contacts. Those paired forms, the action-matched positive realization and a
uniform enclosure are unevaluated. A raw local mass matrix is not a DtN matrix.

For a direction alpha, use `D_alpha Lambda=E_L^dagger(D_alpha L)E_R`.
`L_tilde=T_L^dagger L T_R` has all three product-rule terms. Scalar response
obeys the real-linear Jacobi equation

`L_H h=-D^2 h-2 kappa_H[(H^dagger H-nu^2)h+(H^dagger h+h^dagger H)H]`.

If the source is self-consistent, `D_H J` belongs in the coupled operator and
`delta J|H` in its forcing. Metric/measure, both connection factors,
coefficient and normalized-time pullbacks remain. The moving trace equation
has the inhomogeneous forcing
`(delta T_H)Gamma_e H_e+T_H(delta Gamma_e)H_e-(delta Gamma_c)H_c`.
The current boundary/gauge/constraint rows augment `A_H h_alpha=f_alpha`.
Then one compatible real adjoint gives

`A_H^* p_alpha=ell_alpha`,
`ell_alpha(h_alpha)=Re<p_alpha,f_alpha>`.

This finite consumed contraction includes source and boundary multipliers.
It can be enclosed directly without reconstructing all H variations. On
finite supplied exact rows it is unique precisely when `ell|ker A_H=0`, even
if the field or adjoint is nonunique. An ambiguity claim requires an actual
constrained homogeneous vector with a nonzero consumed pairing. The new code
checks this criterion without selecting a primal branch or pseudoinverse.
For continuum operators the appropriate dual spaces/closed-range or valid
adjoint-existence hypothesis are required. No physical C1 witness is available;
the finite witnesses in tests do not prove physical underdetermination.

For stationary constrained scalar elimination use the Lagrangian
`L=A_action+lambda^dagger R` and the actual constrained block
`K_H=[[L_hh,R_h^dagger],[R_h,0]]`. The mixed readout is

`L_xC-[L_xh,R_x^dagger] K_H^(-1) [L_hC;R_C]`,

on the justified inverse/quotient. This retains multiplier curvature and
constraint-source/domain contacts. The nonlinear-constraint control gives
the exact mixed derivative 16; omitting curvature, `R_x` or `R_C` changes it.
The small carrier inverse is not a bound for the scalar response inverse.

## Complete E1, CAR and physical frontier

The local combination `t_alpha=b_alpha m_mu+delta_alpha m_mu` is retained
before taking norms. `||B(t_alpha)||=|t_alpha|` and its two local quadratures
are preserved; they give no complete E1 moment-rank verdict. No chirality-only
annihilator or Green-cancellation substitution is made.

The six solver triples remain null in their physical packet. The first is
`P_F`, derivative order 0. Its complete physical response must include the
paired LR forms above; first-direction contractions then include
`Re<p_alpha,f_alpha>` and direct contacts. The canonical traction must also
retain returned child, explicit J, response multipliers, measure/frame/trace
and domain contributions exactly once. A separately consumed integrated
Hamiltonian row remains separate. The existing solver/Noether/CAR consumers
are reused; no new E1 assembly is designed.

Without those physical pairings the complete E1 kernel, its CAR projection
and real minimal moment span cannot be evaluated. This does not prove an
independent missing datum or prohibit a whole-family cancellation/enclosure.
The stationary physical KKT response and downstream normalized Pauli readout
are still unevaluated; `a_mu` and `g_mu` remain null.

| Classification | This milestone |
|---|---|
| DERIVED | LR algebraic-partner/positive-adjoint distinction; exact conormal/form identities; constrained contraction and full mixed-KKT response; conditional whole-family thresholds |
| EVALUATED | Exact source/coefficient identities and rational thresholds; imported carrier bounds; source/hash/span verification |
| CONTROL_ONLY | Exact finite symbol/response controls and constrained homogeneous witnesses; nonlinear constraint and omitted-contact examples |
| UNEVALUATED | Actual incoming LR response and scalar source contraction; complete E1/CAR/moment span; physical KKT/native heat/Pauli values |
| OWNER_DEFINITION_GAP | None newly proved; existing action and retarded domain class retained |

## Verification and publication scope

The original archive SHA256 is
`60c2005c4ad13a703772d7c1b5e7c602d2fbe102310ef93479561f35c9872ae2`.
Its 17 files are integrated byte-for-byte under the companion directory.
The bounded source-checked import reproduces 43 exact checks and 43 pinned
sources, result SHA256
`269452297e37de4d19450413d8422e281ae2402cef52acd4a4d811083ddffcf0`.
The standalone original verification receipt is preserved separately from
this repository publication; no old producer campaign was rerun.

Run from the worktree with `C:\Python314\python.exe`:

```text
python -m pytest -q tests/test_muon_birth_c1_lr_form_response.py tests/test_muon_birth_c1_lr_scalar_contraction.py tests/test_muon_birth_c1_lr_replay.py tests/test_muon_birth_covariance_sensitivity.py tests/test_muon_birth_fermion_event_kkt_inputs.py tests/test_muon_birth_parametric_fermion_seam.py
python scripts/replay_muon_birth_c1_lr_response.py --out artifacts/muon_birth_c1_lr_response_20261008/run_1
python scripts/replay_muon_birth_c1_lr_response.py --out artifacts/muon_birth_c1_lr_response_20261008/run_2
python tools/audit_bhsm_status.py --format json
python tools/audit_forbidden_claims.py --format json
python tools/audit_frozen_prediction_integrity.py --format json
python tools/verify_precision.py
python tools/audit_public_readiness.py --format json
git diff --check
```

Actual command outputs, replay hashes, preservation identities, audit receipts
and error scope are recorded in
[verification.json](../artifacts/muon_birth_c1_lr_response_20261008/verification.json).
The focused command returned `163 passed in 8.41s`: 47 new checks and the
preserved 23 CAR, 26 point-input and 67 parametric checks. The two new response
packets are byte-identical, SHA256
`9ab23386fe49b2ddb31e8bc28510199a927981a9a797e6cc788e58dce8c3b4e3`.
All five publication audits passed with exit code zero. The precision output
was `1.066e-14 <= 1.000e-13`; it remains a repository diagnostic.
The imported companion has a scoped `* -text` Git attribute so its original
byte hashes survive Windows checkouts. The final source-manifest pair is
rematerialized after this report/attribute update; no physical inputs change.
This report does not infer physical error from exact arithmetic digits or the
repository precision diagnostic. Publication records the verified additive
result; it does not claim an instantiated physical E1 milestone.
