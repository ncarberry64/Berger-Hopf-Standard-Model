# First-order complementary action of the proposed seam

Continuation from `262621da4f006929ee62b73d7565e2624054fb75` on
`codex/muon-parent-maxwell-density-review`, initially clean. Scientific
reference remains `524ed90689bd5923c249bba2e699abf627e703cd`.
The average-trace law and its new normal bilinear remain **unadopted**.
No completed parent production, normalization producer, direct-matching
residual or corrected auxiliary photon calculation is repeated or refined.

**New result:** the complete proposed action has an executable first-order
mixed form on a compact, domain-valid LL restriction. Its complementary
Galerkin solve and correction matrix are evaluated. This is a restricted
stationary action reduction, **not** the full retarded complementary
reduction or a physical muon observable. The reached forcing is not closed
in the trial frame. Full kinetic/interaction matching remains unevaluated;
the earlier direct restriction remains nonmatching at its stated scope.

## Action, dual and cancellation

Use the literal symmetric parent action in the proposal, its intrinsic
wall action including the once-owned Yukawa bridge, and its ordered seam
term together. In the existing common frame the raw action row is

\[
 B_5=\Gamma^0D_5,\qquad
 A_5=\tfrac12(B_5+B_5^{\mathrm{formal}}).                         \tag{1}
\]

The formal dual uses the volume density and the transported Dirac-bar
convention. It is not the positive L2 inverse of D5†D5. The instantaneous
volume density is mu5=2 pi² nu C r³; the temporal-Cauchy density is mu5/nu.
The known normal action coefficient is

\[
 B_\eta=i\Gamma^0\Gamma^4\eta,\qquad
 \eta=-[2C\tan(\rho/2)]^{-1}.                                   \tag{2}
\]

The actual cached Clifford representation makes Gamma0 Gamma4 Hermitian,
so B_eta is skew-Hermitian and its formal-dual sign reverses. For the
displayed metric/common-A realization the divergence completion of the
geometric coefficients is checked from the same density and clock:

\[
 \mu_5^{-1}\{\partial_\tau(\mu_5 i/\nu)
       +\partial_\rho[-\mu_5 iz/\nu]\}=2ih_0,\qquad
 \mu_5^{-1}\partial_\rho(\mu_5/C)=2h_4.                          \tag{3}
\]

Therefore A5 psi=B5 psi-B_eta psi on interior compact tests. In particular
the raw normal cancellation in D5 W does not remove the connected normal
output of A5 W. This is a consequence of the **literal proposed symmetric
action**, not a change to the saved D5, eta identification or native action.
Projection of a bare D codomain with a wall chiral projector would erase
legitimate opposite-spin output; it is not performed.

For Rw=(Ww,w), smooth matched G1 Rw=0, and bulk-only Qchi=(chi,0),

\[
 P_\partial G_0\chi=0,\quad(1-P_\partial)G_1\chi=0,\qquad
 a_{QQ}(\zeta,\chi)=\langle\zeta,A_5\chi\rangle_5,\quad
 a_{QR}(\zeta,w)=\langle\zeta,A_5Ww\rangle_5,                    \tag{4}
\]
\[
 a_{RQ}(v,\chi)=\langle Wv,A_5\chi\rangle_5
                    -\langle Ev,G_1\chi\rangle_\Sigma
 =\langle A_5^{\mathrm{formal}}Wv,\chi\rangle_5
                    +\mathcal G_{\rm other}(Wv,\chi).          \tag{5}
\]

This combines the cancelling material terms before numerical application.
On a general history the other-face term remains. The literal symmetric
finite-element action has an additional -G_other/2 relative to the Euler
row (5). Both formulations agree on the compact tests used here, since
all other-face products vanish. No symmetry is imposed on an unknown
causal return. Hermitian finite compact action matrices follow from the
explicit symmetric density, not a claimed retarded adjoint equality.

The intrinsic wall and seam terms have zero QQ/QR contribution on these
compact bulk-only variations. They are included in this classification,
not treated as missing zero-filled native blocks. The unchanged intrinsic
action stays in A_RR once. The saved `A_eff_parent_restricted` is explicitly
the parent component plus the complementary correction, not the complete
intrinsic-plus-parent action and not an independent wall determinant.
The additional `run_2/ll_completion` assembles that unchanged intrinsic LL
term in the same canonical convention and reuses the complementary solve:

\[
 A_{RR}^{LL}=A_{RR,5}^{LL}+A_{4}^{LL},\qquad
 A_{\rm eff,compact}^{LL}=A_{RR}^{LL}+\Delta A_{RR}^{\rm compact}.
\]

This is the complete classical parent/intrinsic/seam action on the tested
LL/compact-Q subspace. It does not complete the other chiral sectors,
causal response, quantum measure or global domain realization.

## Actual domain and frames

Use node3/action_arc6 and node4/action_arc8 from the retained tail cache,
each with its own branch24, descriptor and clock. Reuse I, I_tau, u, p,
C_tau_nodes, r_tau_nodes and direct Fourier L_nu. No trajectory, first-field
campaign, mode normalization or endpoint freezing is used. The saved raw
DW/Dp arrays are selected-source contractions, so the retained
`muon_coupled_cut_forms.field_actions` recipe evaluates the needed full
columns with these existing coefficients. Independent comparison to the
selected caches is saved. Instantaneous r,C,nu,shift values/derivatives use
the same metric producer and nodal cells.

The twelve-column angular source image Xi contains both Lorentz spins of
the SM weak doublet. Its Gamma0 image is already in that span (residual
6.54e-16); dependent companion columns are not added or regularized.
The physical wall LL frame is the rank6 quotient

\[
 \Phi_L=\Pi_L\Xi T_L,\qquad
 w_L=\iota^\sharp\Phi_La,\quad R_Lw_L=(W\Phi_La,w_L).            \tag{6}
\]

The actual input-frame reconstruction residual is 3.71e-16. The retained
material trace gives G0 W Phi_L=kappa Phi_L, G1 W Phi_L=0, hence
P_boundary G0 R_L=Ew_L. Right-spin LL is **unmatched**, not physical e_R.
The full twelve-column Q frame and full64 carrier output are retained;
the physical e_R sector and global chiral realization are not supplied
by this LL test. Charge-conjugate bookkeeping introduces no extra trace
or orientation multiplicity. Pairings are counted as in the preserved
direct calculation, not duplicated per trace sheet.

Let x run over this one interior arc element. The two temporal tests are
phi0=x(1-x), phi1=x(1-x)(2x-1), extended by zero. The Q fields are
phi_i p Xi with **zero wall component**. Their radial compact support is
the original saved hat; both material traces and the pole trace vanish.
The temporal tests have zero traces on both artificial element faces and
are zero at the inherited reset, past-prefix and true stop. Smooth cutoff
approximation gives the same H1 test class. This selects a computational
subspace, not a new physical endpoint law. It is not p-W B_vol p and does
not impose the latter's nonzero average trace as a Q-domain coordinate.

The R test basis and the original load's projection into it are diagnostic
variations. They do not prescribe Theta_p, a wall forcing or an external
muon state. Inputs are projected to physical LL **before** action; action
outputs, including the unmatched spin and connected angular fields, are
not projected back to that input span.

## Evaluated first-order reduction

Keep the previous canonical field convention. Node3 C and C_tau are
loaded directly from the matching packet. Node4 C comes from the saved
WW Cauchy moment; only the time derivative consumed by this new element
is constructed from its already-supplied I_tau/I and metric/clock jets.
No field/profile is normalized again. The moving R columns obey
B0,R=C B0,W+C_tau B1,W and B1,R=C B1,W. All terms are transformed together.

For E=(C W Phi_L,p Xi), the first-order moment densities are

\[
 S_0=\tfrac12(E^\dagger M_5 B_0+B_0^\dagger M_5 E),\qquad
 S_1=E^\dagger M_5 B_1,\qquad S_1^\dagger=-S_1.                 \tag{7}
\]

They are not the squared-action A/B/C caches. On the declared linear
density model, interpolate tau_x S0 and S1 between the two actual points
and integrate

\[
 A_{ij}=\int_0^1[\phi_i\phi_j\,\tau_x S_0
     +\tfrac12(\phi_i\phi'_j-\phi'_i\phi_j)S_1]dx.              \tag{8}
\]

Five-point Gauss integrates these polynomial moments; an independent
exact rational-moment check passes. The model has 24 Q coordinates and
12 physical LL R coordinates. Solve all required R columns together:

\[
 A_{QQ}X=A_{QR},\qquad\Delta A_{RR}^{\rm compact}=-A_{RQ}X.       \tag{9}
\]

No explicit inverse, diagonal regularizer or positive D5†D5 component
inverse is used. QQ has both signs. Its condition estimate is
1.000014862251973; the matrix equation residual is 7.56e-18. The correction
matrix's Frobenius norm is 0.1858604319471593 in the saved geometric/test
coordinates. It is a coordinate/model diagnostic, not a physical norm or
Pauli coefficient.

The original diagnostic load has LL test-coordinate norm6.43e-17; its
correction contraction is -2.47e-39+1.63e-55 i. This is at the inherited
source/frame arithmetic scale and is **not a measured nonzero effect or
exact global decoupling theorem**. The spatial Clifford chirality map
explains the near-zero LL projection of this chosen input; the full
six-column correction remains nonzero. Neither the source nor the
witness is changed to force a nonzero selected contraction.

Full first-order forcing is not closed in the compact p frame. At node3
its six-column volume L2 norm is45.27 and its off-frame norm43.71. The
normal part alone has norm8.10, with6.96 outside the compact p support.
Node4 corresponding values are66.15/53.79 and8.10/6.96. These are saved
model diagnostics, not certified tail bounds. They prevent promoting (9)
to the full complementary action or using its residual as continuum
accuracy. No propagation complement is discarded from the full target.

## Matching, same source and remaining causal action

The once-owned YH bridge occurs only in the intrinsic wall action at this
fixed Higgs orientation/background order. The computed compact mixed/QQ
forms add no explicit Y/H bridge. In the previous canonical convention
the retained C_L^sharp YH C_R therefore remains unchanged. No retuning of
Y,H,radius or photon coordinate occurs. No full physical e_R coefficient,
post-elimination pole residue or low-energy coefficient expansion is
inferred from two temporal bubbles. Genuine nonlocal dressing is retained
as a needed kernel rather than required to vanish.

The intrinsic LL amplitude and time-jet densities are evaluated at the
same two retained states, with the same wall radius, common-A background,
angular spin action, physical left input and Dirac-bar dual. Both transform
by C squared into the preserved canonical convention. The scalar C_tau
and pure imaginary time connection cancel in the explicit bidirectional
action density; its Euler measure derivative is not discarded or replaced
by a new physical rate. The LL-only Yukawa matrix is zero because the test
has no e_R component; the physical once-owned YH bridge is unchanged.
There is no independently added determinant or Yukawa copy.
Here "unchanged" preserves ownership and the prior raw bridge, together
with the existing canonical convention C_L^sharp(YH)C_R. The new LL script
does not evaluate that off-diagonal coefficient or eliminate e_R. This is
an LL--LL restriction, not an effective LL action after eliminating e_R.

The completed compact LL matrix minus the retained local kinetic reference
has Frobenius norm 0.1858604319440642. This compares the two temporal test
forms in one field convention. It does **not** extract Z_L/Z_R at a pole,
prove low-energy matching, or require an allowed nonlocal term to vanish.
The full retarded matching outcome remains unevaluated. No compensating
action is selected by subtraction.

For the same photon b_A, all total domain/frame/pairing/source variations
must be taken on one common pullback. Algebraically,

\[
 X_A=\mathrm{solve}(A_{QQ},(A_{QR})_A-(A_{QQ})_A X),\qquad
 (A_{\rm eff})_A=(A_{RR})_A-(A_{RQ})_A X-A_{RQ}X_A.              \tag{10}
\]

The subscripts denote total jets, including moving allowed variations,
trace/normal maps, measures, canonical maps and photon source return.
For a nonzero complementary affine load also retain
f_eff=f_R-A_RQ solve(A_QQ,f_Q) and its total derivative. None of these
physical jets or loads is set to zero. The earlier corrected auxiliary
L lift is preserved and is not the full stationary photon extension.
The quantum measure, its regulated source variation and the same-owner
finite subtraction remain unevaluated; they are not replaced by a finite
Galerkin determinant or chosen compensation.

The **one next required action** is

\[
 X_Q^R(w)=G_Q^R a_{QR}w,\quad
 a_{QQ}(\zeta,X_Q^Rw)=a_{QR}(\zeta,w)\quad(\forall\zeta\in Q),
 \quad\mathrm{supp}(X_Q^Rw)\subset J^+\mathrm{supp}(a_{QR}w).    \tag{11}
\]

It must act on the reached normal, temporal and angular outputs with
P G0 X=0,Q_boundary G1 X=0, inherited U_R reset transport and the actual
first-order other-face realization. Its consumer is (5), then (10).
The supplied squared-action tail pivots do not evaluate it. AE31's finite
intrinsic M4 retarded-existence statement does not construct this proposed
bulk complementary response. The stop bridge supplies a **nonnegative
Friedrichs form** closure; it does not evaluate a first-order retarded
terminal relation. The saved terminal packet's physical_terminal_graph
is null. A compatible first-order trace/normal relation must be realized
or retained in full when an inverse chart fails. No terminal condition,
state, new physical endpoint parameter or desired compensation is inferred
from this gap. This is an unevaluated causal realization of the proposal,
not a demonstrated absence theorem or a new microscopic prerequisite.

## Evidence and scope

Accepted run2, actual coefficient/actions, canonical/frame maps, QQ/QR/RQ,
right-hand side, solution, residual and correction are saved under
`artifacts/muon_first_order_complement_20261006/run_2`. The old full-carrier
R attempt is retained as **unaccepted run1** with its exact source snapshot:
it included right-spin LL in R and cannot represent the physical wall.
Only the affected new calculation was rerun after fixing that domain
defect. No accepted parent/old production was rerun or changed.

Five new cache-based checks pass: domain/physical frames, actual formal
dual and reached complement, rational temporal moments, and first-order
solve/claim boundary, plus once-owned intrinsic LL completion. An initial
test wrongly required an exactly real
cached Cauchy diagonal; its imaginary part is2.16e-17 on a real diagonal
of21.56. The check now uses the declared binary64 arithmetic scope; the
failed receipt is retained and only that check was rerun. No byte-level
or precision campaign followed.

All numerical outputs are binary64 representatives of the existing
512-point nodal spatial quadrature and a new, declared linear **first-order
moment-density** temporal model. There is no certified interpolation,
history, quadrature-continuum or operator-norm bound. Existing endpoint,
tube and interpolation authorities are not relabelled. Residuals measure
only the executed finite equations.

```powershell
C:\Python314\python.exe scripts/replay_muon_first_order_complement.py --output artifacts/muon_first_order_complement_20261006/replay_new
C:\Python314\python.exe scripts/complete_muon_first_order_LL_restriction.py --input artifacts/muon_first_order_complement_20261006/replay_new --output artifacts/muon_first_order_complement_20261006/replay_new/ll_completion
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_first_order_complement.py
```

Input hashes, defining equations, source-jet ledger, runtime and revision
are saved. The earlier direct residuals, corrected auxiliary source,
accepted parent solution and every frozen local contribution are unchanged.
No native operator, compensation, wall Gram or local determinant is
installed. Physical a_mu/g_mu and native uncertainty remain unevaluated.
