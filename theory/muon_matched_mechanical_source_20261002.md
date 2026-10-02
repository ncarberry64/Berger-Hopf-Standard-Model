# Matched mechanical source and primitive mixed weak application

Checkpoint: `BHSM_MUON_MATCHED_MECHANICAL_PRIMITIVE_WEAK_ROW_20261002`.
Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`.
Publication begins at PR465 `cee6fdb8221097109b73cf382dcb5a1f08615f3c` on
`codex/muon-parent-maxwell-density-review`. The existing worktree was clean.
No prior normalization, covariance witness, n2 contact, history solve or
conditional angular producer was rerun. Their artifacts remain unchanged.

The within-child coframe/carrier conversion is now explicit and evaluated
on the eight retained photon modes. The primitive mechanical mixed Hessian
has been applied in the inherited Lorentz weak coefficient operator at the
65 supplied past-cut radial nodes. This resolves the coordinate/gauge part
of the last checkpoint. It does **not** identify this mechanical background
with the physical total SM connection entering the current chiral and
stratified operator. The first unresolved attachment is stated below.

## Producers and input scope

The mechanical connection comes from `diagonal_quotient_contract` and
`action_ownership_ledger` in v15.50; the right coframe/Hodge convention from
`angular_derham_blocks` in v16.04 and the saved photon coefficient arrays;
the carrier from `rank16_connection_attachment`; the spin convention from
the already saved `gamma_LR`. No reference `RADIUS0` is consumed.

| Operand | Retained producer/data | Classification in this calculation |
|---|---|---|
| Quotient, mechanical connection, index8 carrier | v15.50; rank16 attachment arrays | Derived geometric/representation data |
| Eight source lifts and Clifford frame | saved `real_mode_coefficients`, `gamma_LR` | Evaluated canonical reference source, not a physical muon state |
| Parent A,B,C,r,lapse,shift; e,r,W | parent geometry, connection weight, inherited weak coefficient packets | Conditional numerical reconstruction on supplied current history |
| H and T_b at the cut | prior corrected exterior-face packet | Reused; prior H interval remains certified in its own scope |
| Connection lambda_tau, lambda_rho | derivatives of supplied 12-mode parent ansatz | Newly evaluated, conditional numerical input jets |
| Physical muon covariance/external pole state | Not consumed or fabricated | Still absent from this intermediate operator evaluation |
| Physical total SM connection/background attachment | v15.50 vs v15.53, current D/interface contract | Explicit unresolved physical identification |

All eleven input identities and nine producer identities are in
`artifacts/muon_matched_mechanical_source_20261002/input_refs.json`.
The six older scientific packets remain unchanged. The newer primary
history reconciliation is inherited: only the consumed initial face and
terminal descriptor agree with the reference; the full history is not
declared identical or recertified. The targeted producer comparison found
only line-ending changes for producers present in both worktrees. The three
new muon realization modules belong to the PR branch and are absent from
the scientific-reference primary checkout. Unrelated primary work remains
untouched; its branch, HEAD and tracked changes are recorded separately.

## Base, section, coframe, carrier and coordinate

The diagonal right action is `(u,v)->(uq,vq)`. Its base is
`w=uv^-1`, with smooth sections

\[
\sigma_0(w)=(w,1),\qquad
\sigma_1(w)=(1,w^{-1})=\sigma_0(w)w^{-1}.
\]

Let `theta_L=w^-1dw`, `theta_R=dw w^-1`, and `R=Ad_w`. Then
`theta_R=R theta_L`. In the saved **right** coframe the sigma0 connection is

\[
(\Omega_0)_a=\lambda\sum_dR_{ad}\jmath_d,\qquad
\lambda=A^2/(A^2+B^2).
\]

Use the retained carrier representation `U=rho(w)`, for which
`jmath_a=-2iT_a`. With the requested minus derivative convention,

\[
\Omega_1=U\Omega_0U^{-1}-dUU^{-1}
 =(\lambda-1)\jmath_a\theta_R^a.
\]

This is a carrier transformation while the spatial coframe stays right.
There is no separate spin-frame rotation: the saved Clifford frame is held
fixed. A passive left-to-right coframe conversion is already accounted for
by the `R_ad` in Omega0. The reference source is transported as a complete
one-form:

\[
a_0=T_b b_A Y_{A,c}\theta_R^c(-iQ),\qquad a_1=Ua_0U^{-1}.
\]

Its identification with the physical source in the total SM connection
remains an attachment question, not an inference from this computational
section. The differentiation coordinate is b; `beta=T_b b` and
`A_Q=sqrt(2) beta` are the saved relations. No `2/3` multiplier is applied
to the Dirac insertion. `K_Q=(2/3)K_component` is already in e,r,d;
for unit-trace carrier tests the prefactor is `K_trace=K_Q/(16/3)`.

The rotation U depends on the quotient coordinate w only, at fixed supplied
history and source-independent frame. Thus `delta_b U=partial_tau U=
partial_rho U=0`. It generates no temporal/radial source component. It does
generate the derivative

\[
dQ_1=[\jmath(\theta_R),Q_1],\qquad Q_1=UQU^{-1}.
\]

That derivative is included **once**, by applying the saved curl to the
complete transformed harmonic coefficients. The factored arrays
`i_gamma_source_coeff_n1/n3`, `unit_trace_carrier_basis` and `saved_gamma_LR`
also materialize `i gamma^c(a_1)_c` with the retained +--- source sign.
These are local Clifford actions, not a cross-stratum source lift.

## Exact covariance and connected angular output

The normalized coefficient functions are
`phi_nmk=sqrt(n+1) conjugate D^(n/2)_mk`. Their right derivative acts on
coefficient vectors as `E=i2J`, yielding the saved `curl=*d=2I+S.2J`.
The existing normalized Gaunt and conjugation rules are reused. Ad_w is a
spin1 coefficient function: its `1/sqrt(3)` expansion factor normalizes
that new rotation and does not renormalize the saved photon modes.

Multiplication of the eight n1 sources by this rotation generates exactly
n1+n3. The rotation of the sigma0 curvature image can additionally generate
n5, which is retained before checking cancellation. The identities

\[
d_{\Omega_1}a_1=Ud_{\Omega_0}a_0U^{-1},\qquad
F_{\Omega_1}=UF_{\Omega_0}U^{-1}
\]

follow for every smooth source from the product rule and the gauge law,
with the same right Hodge operator. The focused coefficient check uses the
actual eight supplied modes, not selected finite-rank covariance examples.
The n5 cancellation does not justify a heat/resolvent/evolution tail bound.
Smooth U on the same child preserves its H1 form space and transforms its
trace. This statement does not assemble the reset, parent interface or
strong domain of `Ddagger D`.

## Complete primitive angular row and weak consumption

Use unit-trace anti-Hermitian carrier coordinates

\[
H_a=-iT_a/\sqrt2,\quad H_Y=-iY/\sqrt{10/3},\quad
-iQ_1=\sqrt2 R_{a3}H_a+\sqrt{10/3}H_Y.
\]

For each retained output level n1,n3, the full spatial/internal row is

\[
C_h=C_0+hT,\quad h=\lambda-1,\quad
T_{ic,jd}=\epsilon_{iaj}(\operatorname{ad}_{\jmath_a})_{cd},
\]
\[
H_\lambda=C_h^\dagger C_h+4\lambda(\lambda-1)B,\qquad
B_{ic,jd}=\sum_k\epsilon_{kij}\epsilon_{kcd}.
\]

The B term is the **background-curvature contact**
`<F,W(v wedge a+a wedge v)>`; the first term is `<dOmega v,W dOmega a>`.
The spectator harmonic weight is retained. There are 240 independent
spatial coefficient directions across n1+n3, rather than a projection onto
the old eight mode indices or the child's independent16 fermion test frame.
The source has zero temporal/radial components, but all scalar temporal and
radial test rows are also retained (160 further coefficient directions).

The saved Lorentz primitive weak form carries

\[
q_{\rm mech}(v,a)=\int {1\over Q_{\rm norm}}
\{e\langle D_\tau v,D_\tau a\rangle-r\langle v_\rho,a_\rho\rangle
-d\langle C_hv,C_ha\rangle+\text{signed curvature contacts}\},
\]

where `Q_norm=16/3`, `D_tau=partial_tau-zeta partial_rho-H/2` and
`d=r(C_rho/r_orbit)^2`. Full pointwise `W=Lambda(1+X_eta^3)` stays in the
supplied coefficients. The angular dual `-d H_lambda a/Q_norm` is
**evaluated** at every supplied radial cut node and saved as
`weak_angular_row_n1/n3`. Temporal/radial derivative duals and conormal
coefficients are also saved. Coefficient derivatives remain inside the
weak divergence; no constant-coefficient strong operator is substituted.
The regular-pole density uses its existing analytic zero limit.

Connection jets are derived without a new parent solve:

\[
v=\sin^2\rho\sum_jq_{v,j}\cos(2j\rho),\quad
\lambda_\rho=2\lambda(1-\lambda)(2v_\rho-\csc\rho),\quad
\lambda_\tau=4\lambda(1-\lambda)\dot v/N_{\rm boundary}.
\]

Writing `G=dOmega` on scalar angular coefficients and
`J(a)=-sum_i ad_jmath_i a_i`, the evaluated scalar rows are

\[
R_\tau=-eG^\dagger aD_\tau b
 +e(\lambda_\tau-\zeta\lambda_\rho)J(a)b,
\]
\[
R_\rho=e\zeta G^\dagger aD_\tau b+rG^\dagger a b_\rho
 -(e\zeta(\lambda_\tau-\zeta\lambda_\rho)+r\lambda_\rho)J(a)b.
\]

These retain both background jets and the moving-frame derivative. They
do not supply BRST gauge-fixing coefficients or the AE4 induced remainder.
No radial source profile, new exterior forcing, free endpoint condition,
positive Maxwell minimum or future tail is chosen. The past temporal face
remains step1222 with core orientation -1; the future is the inherited
canonical stop. Temporal conormal and radial/material traction are distinct.

## Evaluated result and error scope

At the retained past/material corner `lambda=0.5066207222913062`:

| New control/result | Value |
|---|---:|
| Covariance absolute coefficient residual, all eight sources | 2.0050401905981628e-15 |
| Retained n5 cancellation residual | 1.9724042404289787e-16 |
| Nonzero n3 source norm | 3.2659863237109037 |
| Full mixed curvature contact norm | 4.6179923118940325 |
| QQ curvature contact residual | 8.088351673759241e-17 |
| Full angular mixed row norm | 64.16152903672352 |
| Matched mechanical QQ corner eigenvalues | 9.513329112509913 through 9.513329112509930 |

These norms refer to normalized Haar/primitive carrier coefficients of the
unit-beta reference source; they are not Pauli coefficients. The QQ contact
vanishes because both source columns share the same transported generator;
its full mixed row is nonzero. The old unmatched numbers are neither
manually corrected nor overwritten. The matched QQ value is a consequence
of the evaluated full row, not a criterion for choosing a section/sign.

The identities/support statements are exact representation results. The
new numbers are binary64 evaluations at retained reconstruction inputs,
with absolute implementation checks, not certified physical enclosures.
Parent-H and affine-logR errors remain distinct and unknown here. New
lambda-jet input error, induced matching, interface/evolution tails and
physical attachment error are null, not zero. No native renormalization,
finite-E1 response, exterior solve, shifted resolvent or physical transfer
direction was evaluated. All six physical native ledger entries remain
null; strong terms would be a native subset, never an extra duplicate term.

## First unresolved attachment, producer and consumer

The concrete next operand is the internal background one-form
`Omega_SM^(0)` in the actual source insertion, with the geometric spin
connection kept in `D_geom`:

\[
D_{\rm strat}[b]=D_{\rm geom}+M_l+
c_{\rm src}\left(\Omega_{\rm SM}^{(0)}+
 T_b\sum_A b_A Y_A(-iQ)\right).
\]

The missing equation must say whether the internal background in this
formula is `rho_*(omega_mech)` (zero **fluctuation** around that connection)
or zero (an independently reconstructed zero **total** SM connection), and
give the compatible carrier section for Q. This is the specific coefficient
and source identification that the broader attachment notation denotes:

\[
\Omega_{\rm strat}^{(0)}=
\operatorname{Att}_{\rm current}[\rho_*(\omega_{\rm mech}),A_{\rm SM}^{(0)}],
\qquad
\delta_b\Omega_{\rm strat}=T_bY_A(-iQ)
\quad\text{in that same carrier/Clifford section}.
\]

Its input is a mechanical ad(P_diag) connection plus the SM rank16 bundle
and fixed-Q source. Its output is the total connection and tangent used by
the current chiral D_L,D_R, positive-parent operator and interface trace.

v15.50 `action_ownership_ledger` explicitly selects the **mechanical**
classical background and says its curvature is already in R8. v15.53
`hybrid_bundle_gluing` explicitly reconstructs postevent SM connections in a
**zero-background sector** with inherited kinetic norm. The rank16 module
fixes the algebra representation, source sign and trace index. Neither
that index nor the v15.69 fixed-trace functional/AE4 heat owner supplies an
equation distinguishing total SM background zero from fluctuation zero
around `rho_*(omega)`, and fixing the relative Higgs/Q section if required.

This is a physical attachment equation missing from the targeted recovered
chain, not a remaining coframe/gauge sign choice or a missing diagonal
matrix inversion. Nonzero mechanical curvature at this supplied corner
cannot be gauge transformed into a zero-curvature total connection. We do
not assert that both are valid solutions of the full theory; we decline to
select an interpretation that the actual operator equation has not supplied.

The consumer is the **physical** mixed parent weak form and its same-source
exterior forcing return `j_ext`, followed by parent/interface Xi and the
same-owner finite-E1 response. The local continued kernel and the evaluated
mechanical coefficient rows are not `j_ext`. The first exterior response
cannot be reported by solving a newly selected mechanical SM background.
Next: recover/derive this attachment equation from the current action and
operator, then use the already evaluated row where that equation permits.

## Frozen local terms and reproduction

The existing local contributions are copied byte-for-byte:
`a_mu_QED_local=0.00116550200495813`, calibration-only standard uncertainty
`1.79e-13` under `alpha_inverse=137.035999084`, uncertainty `2.1e-8`, with
other original conditional inputs fixed;
`0<delta_a_mu_h_local_1<3.500331e-9`; already-combined selected-local interval
`0.0011655039493<a_mu_selected_local<0.0011655109506`.
They are not refitted, refined, added again or promoted to a total bound.
Physical `a_mu` and `g_mu=2(1+a_mu)` remain unevaluated.

Standalone packet:
`C:\Users\carbe\Downloads\BHSM_muon_matched_mechanical_source_524ed906_20261002`.
It contains `replay.py`, implementation snapshot, input references,
`run_1/matched_source_and_weak_actions.npz`, result, receipts, hashes and this
report. In the PR worktree the equivalent reproduction is:

```powershell
python scripts/replay_muon_matched_mechanical_source.py --output C:\Users\carbe\Downloads\BHSM_muon_matched_mechanical_replay_new
python -m pytest -q tests/test_muon_matched_mechanical_source.py
```

Five targeted tests passed (four in the initial targeted run, followed by
one added source-sign check in its own targeted run): independent
symmetric-power point evaluation of
the **actual** transported one-forms; all-mode covariance retaining n5;
full rank16 commutator contraction of the curvature contact; weighted
Lorentz weak/constraint consumption with physical claims kept unset; and
the Clifford source sign against the saved lepton Xi columns, without
recalculating their contact.
No full suite or earlier producer replay was run. A preliminary curl
transpose implementation defect was corrected against the saved curl before
the persisted calculation; it changed no earlier input or scientific result.
The persisted calculation took about 0.053 seconds excluding imports and
input loading. This is not a token-cost or native-solve cost estimate.
