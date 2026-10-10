# Incoming parent trace response: normalized carrier entries

The incoming C1/E1-minus **positive-square carrier contribution** now has
evaluated entry enclosures in an action-normalized trace representation. On
the four spatial shells already covered by the retained theorem, there are
160 particle trace modes: 8, 24, 48 and 80. All 160 diagonal pairings have
uniform shared-family bounds; all 25,440 ordered off-diagonal carrier entries are
exactly zero. For every covered diagonal entry,

\[
9.512785673430680\,10^{-16}
\leq \lambda^2 (P_{\rm car})_{jj}
\leq 8.237301494782404\,10^{-15}.
\]

These outward display bounds summarize the exact rational, shell-specific
enclosures in `run_1/incoming_parent_trace_response.json`. They hold for the
same incoming family \(0<\lambda\leq1.33025636847111862\,10^{-30}\),
the retained zero-birth Dirichlet reference and negative-axis probe \(z=-1\).
The probe is not a physical pole or momentum. No amplitude, history member,
spinor ray or covariance has been selected.

This supplies a normalized matrix contribution and its entry contract to the
parent response calculation. It does **not** evaluate the full order-zero
`P_F` or provide a point-valued `parent_jet[0]`. In particular, the carrier
zeros do not set the corresponding full incoming LR entries to zero.

## Trace domain, normalization and multiplicity

The current incoming one-seam owner restricts the two-boundary Weyl relation
to zero external birth trace. Its retained response is \(M_f=M_{11}\), not
the superseded pre-E0 birth-graph restriction. The terminal E1 trace is the
free right-hand argument. Interior correction functions have homogeneous
traces at both endpoints. AE2 keeps its existing opposite outward normals,
unitary reset and paired conormal contact; no new fermion surface density is
introduced.

Let \(\phi_{n,\sigma,a}\) be any orthonormal eigenbasis of the unit round
\(S^3\) Dirac operator, with

\[
D_{S^3}\phi_{n,\sigma,a}
=\sigma(n+3/2)\phi_{n,\sigma,a},\qquad
a=1,\ldots,d_n,\quad d_n=(n+1)(n+2).
\]

Both spatial signs occur in **each** of the two Weyl copies \(b=L,R\).
The basis coefficient labels are \((n,b,\sigma,a)\), tensor the fixed
muon family vector \(e_\mu=(0,1,0)\). This family label is the inherited
charged-lepton slot \((k,j)=(5,2)\); it is not the spatial level \(n\).
There are \(4d_n\) particle modes on a complete signed shell. Thus the lowest
shell contains eight modes, not two and not an additional factor of four
times eight. The transfer coordinates \((u,A u)\) do not double the trace
dimension.

The collar zero mode already satisfies \(\int J|u_0|^2d\eta=1\).
On a radius-\(R_4\) spatial slice, the canonical half-density pullback is

\[
\psi=R_4^{-3/2}\sum_j q_j\phi_j e_\mu,\qquad
\int_{S^3}R_4^3d\Omega\,\psi^\dagger\psi=\sum_j|q_j|^2.
\]

The positive trace Gram matrix is therefore the identity. No extra sphere
volume, wall, family-rank or spin multiplicity multiplies a normalized
coefficient. Choosing coordinates within a degenerate eigenspace is a
unitary representation choice; the carrier acts as a scalar on that space,
so its result is independent of that choice. No coefficient vector is picked.

The self-dual coefficient space is the particle carrier plus its conjugate
carrier. Its dimensions are 16 on the lowest shell and 320 on the four
covered shells. The exchange conjugation, conjugate pairing and charged
lepton/conjugate charge maps are recorded. They are representation data,
not a CAR covariance or a prescription for lifting this positive carrier
matrix into the full statistics-booked `P_F`. Fermion supertrace signs and
the `N=I-C_plus` ordering sign belong to the consumed functional; neither
changes the positive Hilbert Gram matrix.

## Evaluated carrier action on the trace space

The exact unitary Dirac-to-chiral basis change gives
\(\alpha_i=\operatorname{diag}(-\sigma_i,+\sigma_i)\).
Write \(\epsilon_L=-1\), \(\epsilon_R=+1\). On a channel,

\[
A_{n,b,\sigma}=\partial_\tau+
\chi(n+3/2)e^{-x(\tau)},\qquad \chi=\epsilon_b\sigma.
\]

The carrier action is the retained positive form
\(\|A_{n,b,\sigma}u\|^2+\kappa^2\|u\|^2\), \(\kappa^2=1\),
with the stated birth/terminal trace restriction. Its Dirichlet-to-Neumann
entry is \(M_{n,\chi}(\lambda,-1)\), and

\[
(P_{\rm car}q)_{n,b,\sigma,a}
=M_{n,\epsilon_b\sigma}(\lambda,-1)q_{n,b,\sigma,a}.
\]

This is an operator-action contract for the whole round carrier spectrum.
The **numerically enclosed scope** is precisely the four retained rows
\(|\mu|=3/2,5/2,7/2,9/2\). It does not assert a uniform bound over all
spatial levels or all spectral probes. The four-shell matrix is an exact
carrier compression, not a physical angular cutoff of the complete action.

For each covered shell the existing stored \(|W|\) bound applies to both
\(\chi\) signs and every degeneracy copy. The new calculation reuses its
exact-decimal duration envelope and evaluates the rational scaled bounds
for every labelled diagonal entry. Equal enclosing intervals do not assert
equal \(M_+\) and \(M_-\) values. All entries retain the same
\(\lambda\), duration and coefficient dependence; their intervals are not
independently selectable values. The unscaled response has no finite uniform
upper bound as \(\lambda\downarrow0\).

## What the unchanged consumer requires

`solve_retarded_event_kkt_jet` infers \(n\) from its supplied parent matrix.
It consumes an entire Hermitian \(n\times n\) parent block, together with
the other five tuples, to construct
\(H_{\rm eff}=P-BL^{-1}B^\dagger\), solve the KKT system and form
\(Pq+Bc+J+C^\dagger\lambda\). It has no interface accepting an enclosure,
one arbitrary bilinear pairing or a continuum operator callback.

No finite angular index set is selected by the physical input inventory.
The present result binds the carrier part of candidate matrix entries and
the complete trace labels. It does not prove that the actual incoming
Higgs, charged-gauge, source, boundary or constraint response preserves the
four-shell space. Even the fixed family projector's available commutants
do not prove full spatial closure.

An exact smaller representation requires a reducing subspace of the full
operator/domain with compatible child coupling, source and constraints, or
an exact elimination of the omitted responses. After child elimination,
partition the parent space into retained \(K\) and omitted \(Q\). Where
the justified inverse exists, eliminating \(q_Q\) gives

\[
K_{\rm reduced}=
\begin{bmatrix}H_{KK}&C_K^\dagger\\C_K&0\end{bmatrix}
-X H_{QQ}^{-1}Y,\qquad
X=\begin{bmatrix}H_{KQ}\\C_Q\end{bmatrix},\quad
Y=\begin{bmatrix}H_{QK}&C_Q^\dagger\end{bmatrix},
\]
\[
b_{\rm reduced}=\begin{bmatrix}-J_K\\d\end{bmatrix}
+X H_{QQ}^{-1}J_Q.
\]

The retarded child response can make \(H\) non-Hermitian, so
\(Y=X^\dagger\) is used only when that stronger property is proved.
In particular the induced multiplier block is
\(-C_QH_{QQ}^{-1}C_Q^\dagger\). A compressed parent Schur complement
alone is generally insufficient for the unchanged solver's zero multiplier
block. This obstruction is checked with an exact finite counterexample,
classified `CONTROL_ONLY`; it is not a physical omitted-mode calculation.

## Incoming primal LR response: exact remaining operand

The next base calculation remains

\[
f_j=V_{ib}r_j,\qquad (A_0+V_{ii})w_j=f_j,\qquad
(R_{LR})_{ij}=p_i^\dagger W r_j-p_i^\dagger V_{bi}w_j.
\]

Here \(V\) must first be the actual full-minus-carrier **quadratic
form** on the stated domain. For a form perturbation the source belongs
to the dual interior form space. The previous positive-square audit proves
that a first-order normal term and conormal contacts can remain: the
cancelling algebraic mass partner is not the Hilbert adjoint. The full
Poisson extension or a verified correction enclosure is required.
Those proofs and the constrained-adjoint identities are reused unchanged.

The first unevaluated primal ingredient is the additive coefficient
restriction \(M_{LR}(H_{C1})\) in \(V_{ib}r_j\) and the paired boundary
form \(p_i^\dagger W r_j\). Its fixed Yukawa operator is owned, and the
active Higgs equation is

\[
-D^2H-2\lambda_H(H^\dagger H-\nu^2)H
-\bar e_RY_\ell^\dagger L_L=0.
\]

The original action's independent positive quartic stiffness
\(\lambda_H\) is distinct from its fixed profile parameter
\(\kappa_H=64\pi^5\). In the preceding report, a coefficient denoted
`kappa_H` in this scalar Euler expression must be read as an unfilled
quartic stiffness, not as permission to insert the profile constant.

The geometric incoming 98-coordinate packet and zero external fluctuation
trace do not supply the incoming active-Higgs/source/Cauchy application.
The independent connection and off-mode data explicitly retain a conditional
or unit-Higgs witness with physical amplitude unsolved. Their numerical
norms are not LR form bounds. The new primal receipt records source hashes,
line spans and the bounded recovery scope. It establishes no new missing
action definition and no physical underdetermination theorem.

Consequently no actual interior RHS \(f_j\), full-extension correction,
LR diagonal/off-diagonal entry or total-parent enclosure is supplied.
The exact carrier zeros remain preserved separately. Direct uniform
enclosures of these consumed LR pairings could still close the calculation
without selecting a family member or reconstructing an entire Higgs field.

## Classification and downstream boundary

- **DERIVED:** complete normalized channel labels, multiplicities, charge
  and conjugate representation maps; carrier diagonal operator action;
  exact entire-KKT complement-elimination contract.
- **EVALUATED:** 160 shared-family scaled carrier diagonal enclosures and
  25,440 exact off-diagonal carrier zeros, inherited source identities and
  deterministic replay hashes.
- **CONTROL_ONLY:** exact Clifford basis-change, matrix/pairing and
  omitted-constraint-reaction checks. No control matrix is a physical input.
- **UNEVALUATED:** actual incoming LR base pairings and their interior
  solves; full `P_F^(0)` and remaining orders/other five tuples; directional
  adjoint contractions, complete E1/CAR projection and physical moment span.
- **OWNER_DEFINITION_GAP:** none newly established.

The next directional contractions and constrained mixed responses depend
on that same unfilled primal restriction. The physical point guard remains
unchanged: its first unavailable slot is `P_F`, order zero,
`parent_jet[0]`; all 18 solver entries remain null. No KKT or Noether callback
is called and no Green cancellation is substituted. Filling the carrier
component does not fill `B_F`, `L_F`, `C_F`, `J_F` or `d_F`.

## Verification

Commands, complete captured outputs, source hashes, product hashes and error
scope are recorded in `verification.json`. New matrix mathematics and the
inherited physical guard are tested. Two new materializations must be byte
identical. All 72 published CAR, point-guard, carrier and a51 milestone paths
are verified unchanged against Git; the imported 43 exact checks and 43
source identities are reused. Required publication audits are run on this
additive result before commit and push. Their precision tolerance concerns
repository integrity, not a numerical uncertainty for the unresolved LR
response or any physical muon readout.

All commands below were run from the existing worktree with
`C:\Python314\python.exe`; tests used `PYTHONPATH=src`.

```powershell
python -m pytest -q tests/test_muon_birth_incoming_parent_trace_response.py tests/test_muon_birth_incoming_parent_trace_replay.py tests/test_muon_birth_fermion_event_kkt_inputs.py tests/test_muon_birth_covariance_sensitivity.py tests/test_muon_birth_parametric_fermion_seam.py tests/test_muon_birth_c1_lr_form_response.py tests/test_muon_birth_c1_lr_scalar_contraction.py tests/test_muon_birth_c1_lr_replay.py
python scripts/replay_muon_birth_incoming_parent_trace_response.py --out artifacts/muon_birth_incoming_parent_trace_response_20261008/run_1
python scripts/replay_muon_birth_incoming_parent_trace_response.py --out artifacts/muon_birth_incoming_parent_trace_response_20261008/run_2
python tools/audit_bhsm_status.py --format json
python tools/audit_forbidden_claims.py --format json
python tools/audit_frozen_prediction_integrity.py --format json
python tools/verify_precision.py
python tools/audit_public_readiness.py --format json
```

The focused suite returned `183 passed in 15.68s`, including the preserved
23 CAR tests and 26 point-input tests. Both final replay directories must
contain identical response, manifest and hash-list bytes; the captured
comparison and all product identities are in `verification.json`.

| Repository audit | Captured output |
| --- | --- |
| BHSM status | `passed: true`; frozen and official predictions unchanged |
| Forbidden claims | `passed: true`; `findings: []` |
| Frozen prediction integrity | `passed: true`; `frozen_predictions_changed: false` |
| Precision | `PASS: precision gate verified (1.066e-14 <= 1.000e-13).` |
| Public readiness | `passed: true`; `BHSM_REPOSITORY_PUBLIC_REVIEW_READY` |

The response packet is 367,919 bytes with SHA-256
`a56d7f6f6ff1968c40a57e42eb8ad2b3fe3ef93b5e48ecfa95354097389fc3f6`.
The new primal receipt is 18,764 bytes with SHA-256
`50e052e6433ae5d05641f104e3f3f3a2123dab4e6896f010136d04e59be651b0`.
The original point-input module remains byte-identical with SHA-256
`286ac459ec88c2c739cd6cdd829cdf2234518ed224e35140349a6ca14dbb5592`.
The product manifest is hashed separately so that the report does not
contain a self-referential report/manifest digest.

No numerical scientific check failed. Independent review corrected a
displayed lower-bound rounding and removed an unjustified Hermitian
assumption from the complement formula before verification. Expected
rejections for unstored spectral bounds and invalid compressed KKT reactions
are control scope only. The remaining LR error scope is an **unevaluated
physical coefficient/pairing**, with no claimed interval radius or point
precision. Source-recovery read diagnostics do not establish absence of a
physical solution. No upstream stiffness, amplitude or covariance was
inserted.
