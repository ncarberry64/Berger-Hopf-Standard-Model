# A concrete proposed seam equation, outside the frozen native operator

Continuation from `223e2bd7fd3fa89358595676addbc3f8386a0ce0`, branch
`codex/muon-parent-maxwell-density-review`; scientific reference
`524ed90689bd5923c249bba2e699abf627e703cd`. The worktree began clean.
The completed visibility calculation, its four checks, eta, witness,
accepted parent solution, all previous operator results and locals are
unchanged. No history, field action, solve, old test or production replay
was rerun. The new computation is a cache-only application of the proposal
below to the original twelve source columns, not a new witness.

**Result:** an explicit proposed average-trace field identification and
dynamic material normal law, with its necessary action term, full ordered
photon jet and boundary reverse. It supplies conditional numerical
`J_chi` arrays on the saved source space. It is **not an adopted BHSM seam
prescription**, a native operator update or a physical muon result.
In particular it changes matched material transmission and its localized
kinetic matching is not established. No wall Gram or response is updated.

## Adopted facts and the extra postulate

The concrete retained field/action definitions used here are:

* `completion/foundational_dirac_spin_glue_v14_45.py`,
  `foundational_action_payload`: two oriented restrictions `Psi_+,Psi_-`
  of the parent spinor; a normal kinetic term and the ordered bridge
  `bar(Psi_+) Y H Psi_- + h.c.`. Its global Spin glue identifies the two
  parent restrictions, not an independent intrinsic wall field.
* `ae31_c2_intrinsic_m4_lepton_action.action_composition_contract`:
  independent active `L_L,e_R,H`, intrinsic kinetic action and one Yukawa
  bridge, with its fixed family operator. The LR mass block is already
  assembled in `ae31_c2_chiral_green_domain.chiral_operator_assembly`.
* `ae31_c2_chiral_green_domain.domain_provenance_reconciliation`:
  smooth internal material transmission, opposite Green orientations,
  inherited reset graph. Its reset `Gamma1` law belongs to the squared
  domain; it must not be confused with the first-order jump below.
* `ae4_stratified_dirac_zeta_induced_owner.py`: independent canonical
  H5/H4 summands and one stratified owner. Naming that owner does not
  specify its off-mode seam entries or establish kinetic subtraction.

These facts remain adopted. They do not imply the following **additional
physical postulate**:

> The independent physical lepton wall field equals the normalized matched
> average of the two transported parent traces. Their conjugate matched
> jump exerts the wall force. Unmatched channels retain smooth transmission.
> Implement this through the normal seam bilinear (5), with no free coupling.

This is one explicit candidate material completion, not a uniqueness
claim. Its rule is independent of the diagnostic profile `h=p_scalar/u`,
the computational source basis and the muon anomaly. It neither chooses
that profile nor installs `K_L`, lambda, a new state, a cap or a boundary
law on the temporal faces. It is new precisely because the retained
matched material transmission did not allow this dynamic jump.

## Field spaces, pairings and orientations

Let `a=gamma_+ Psi_+` and `c=U_b^{-1} gamma_- Psi_-` be the two actual
material Sobolev traces in the inherited common section. Here `U_b` is
the inherited Spin x SM transport, not a fitted interpolation. Use the
action-associated Euler operator `A5=Gbar5 D5` in this common frame, with
the corresponding formal adjoint, rather than assuming bare Lorentzian
`D5` is formally self-adjoint in positive L2. The actual saved density is

\[
 J_{\rm bar}=\mu_4 i\Gamma^0\Gamma^4,\qquad
 j=J_{\rm bar}/\mu_4,\quad j^\sharp=-j,\quad j^2=-I.       \tag{1}
\]

It comes from `material_green_columns` and
`run_2/node3_joint_known_variations.npz`. `mu4` enters the boundary
geometric measure exactly once. The bare L2 Green density `mu4 i Gamma4`
has a different adjoint convention. A spin boost is accompanied by its
pairing transformation; no Euclidean unitarity is assumed. Equation (1)
is the saved common-frame material model, not a global strong conormal.

Write **new first-order** trace coordinates

\[
 G_0=(a+c)/2,\qquad G_1=j(a-c),\qquad
 \mathcal G(U,V)=\langle G_0U,G_1V\rangle_\Sigma
                 -\langle G_1U,G_0V\rangle_\Sigma.        \tag{2}
\]

This exactly equals the two opposite outward Green forms. `G1` is an
algebraic first-order jump, not the temporal momentum, radial traction,
`N_out`, or AE2/AE31 squared-domain normal trace. A zero jump on an old
smooth column says nothing about its solved exterior conormal.

Let `iota_b` inject the actual physical wall `(L_L,e_R)` into material
carrier traces. Work in the **doubled charge-conjugate carrier**, so this
injection is complex-linear on the formal doubled space:
`L_L=(1,2,-1/2)` with Lorentz left projector;
`e_R=(1,1,-1)` in the conjugate of the ledger's `e_c=(1,1,+1)` using the
retained charge-conjugation map. On the undoubled ledger that map would
be real-linear/antilinear and could not use an ordinary complex adjoint.
Family factors are unchanged. The right-spin coordinates of the
computational LL doublet are **unmatched**, not `e_R`. The doubled notation
is bookkeeping with redundancy `Psi_N=(Psi,C Psi)` for the retained
antilinear charge-conjugation map C. Its reality involution is
`J_N(x,y)=(C^{-1}y,Cx)`; allowed physical pairs are its fixed set. No doubled
quantum trace or additional species is used here. A complex-linear joint
operator would have to preserve that redundancy and its functional trace
would have to descend to the original independent carrier. That full
realization and trace prescription are not established by this proposed
law; an unconstrained doubled trace is not justified. The new numerical
evaluation is only the supplied LL particle-sector restriction; it does
not claim to materialize an unseen e_R matrix or discard that sector.

Use the actual geometric dual, `iota^sharp=M4^{-1} iota^dagger M_Sigma`,
`iota^sharp iota=I`, `P=iota iota^sharp`, `Q=I-P` and
`E_b=kappa_b iota_b`. Here `kappa=1/sqrt(2 I)` is the full inherited
mode's material value, with units L^{-1/2} when s has length units; it
is not a new dimensionless coupling. At node3 kappa=1.3450620783610998
in the inherited coordinates. Angular/family counts and index2/3 do
not multiply it. This is a material trace normalization, not B54.

## Proposed joint action, allowed variations and reverse

The proposed local material law and Euler row are

\[
 P G_0\Psi=E_b w,\quad QG_1\Psi=0,\qquad
 (A_{\rm joint}(\Psi,w))_4=A_4w-E_b^\sharp G_1\Psi.       \tag{3}
\]

The matched jump is free and is determined by the coupled wall equation;
the wall field remains an unknown. The normal reverse is fixed by (2):

\[
 \mathcal G(U,V)
 +\langle w_U,-E^\sharp G_1V\rangle_4
 -\langle-E^\sharp G_1U,w_V\rangle_4=0.                  \tag{4}
\]

**Varying the displayed old bulk+wall action alone does not produce (3).**
For its inherited symmetric bulk variation, the proposed completion
requires the explicit additional ordered normal bilinear

\[
 S_{\rm seam}=-\tfrac12\{
       \langle w,E^\sharp G_1\Psi\rangle_4
      +\langle G_1\Psi,Ew\rangle_\Sigma\}.               \tag{5}
\]

The symmetrized bulk Green variation contributes a free `delta G1`;
(5) cancels it and yields the full wall row in (3), not half of that
row. Equivalently, on the proposed domain the quadratic form is
`<Psi,A5 Psi>5 + <w,A4 w-E^sharp G1 Psi>4`. The 1/2 is the inherited
action symmetrization, not a source normalization. Fermion bar/unbar
variations retain their order and their corresponding conjugate terms.
No extra Yukawa bridge is added: the existing `A4` contains it once.
The normal bilinear is new, however, and cannot be called a recovered
action term. No additional heat determinant is appended.

For the forward field identification define on traces

\[
 F_b\Psi=\kappa_b^{-1}\iota_b^\sharp G_{0,b}\Psi,
 \qquad F_b\Psi=w\ \hbox{on (3)}.                       \tag{6}
\]

Its pullback of an action-Euler wall cotangent `e4` is the boundary
cotangent `G0^sharp iota e4/kappa`: half on each transported sheet,
with the second sheet's transport dual. It modifies the boundary
normal balance, not the distributed bulk Euler equation. The action
Euler covector already includes the Dirac-bar map; converting back
to a bare Dirac row uses the appropriate inverse bar map once. The
reverse in (3) is similarly an action-associated normal row, not the
distributed reverse of the old bounded h witness.

If the complete complementary material trace space is surjective,
an adjoint-domain test gives (3) again: arbitrary matched `G1` forces
`P G0=Ew`; arbitrary unmatched `G0` forces `QG1=0`; arbitrary wall
variation forces the row `-E^sharp G1`. This is local material formal
maximality under that stated trace assumption, not a theorem about
the global retarded Lorentzian realization or D^dagger D.
An unbounded Sobolev trace identification can be dense in independent
H5+H4: smooth thin-collar lifts have fixed boundary trace and bulk L2
norm tending to zero. It is not the nondense bounded radial graph
`w=B_rad Psi5`. Closedness and the inherited other-face domains still
need their appropriate functional-analytic realization. No new
physical endpoint condition follows from the material algebra.

## Actual saved directions and complete photon derivative

Use the cached node3 volume projection `b_vol=0.024964485717262674`,
not eta, the temporal-Cauchy projection, or a fitted coefficient.
For the diagnostic complement `chi_j=p_j-W Bp_j`, compact p has
zero geometric material trace and W has material value kappa Xi_j.
Both traces have been put in the same inherited section before applying
the map. Therefore, **conditional on the new postulate**, on all twelve
saved columns

\[
 G_0\chi_j=-\kappa b_{\rm vol}\Xi_j,\quad
 J_{\chi,j}=D_{\Psi5}F_b[\chi_j]
            =-b_{\rm vol}\iota^\sharp\Xi_j.              \tag{7}
\]

The script saves actual `J_chi_left_n1/n3`, the full unmatched average
trace and an e_R zero array justified by this source's LL carrier
support. It retains the right-spin LL output. Negative-sheet traces
are the same saved arrays in the transported common section; no
opposite sign is inserted into a field trace. The sign is in (2).
The old smooth columns have zero G1 jump. They are only arguments of
the trace readout, not prescribed joint-domain solutions; in particular
no Theta_p is selected and p need not belong to Dom(D_strat).

Differentiate the **same photon coordinate b_A**, with beta=T_b b and
A_Q=sqrt(2) beta already in the source arrays. Let a subscript A denote
its total derivative, including induced map/frame/domain movement:

\[
 J_A=F_A\chi+F\chi_A,\quad
 \chi_A=p_A-W_A Bp-WB_Ap-WBp_A,                            \tag{8}
\]
\[
 F_A=-\frac{\kappa_A}{\kappa}F
      +\kappa^{-1}(\iota^\sharp)_A G_0
      +\kappa^{-1}\iota^\sharp(G_0)_A.                   \tag{9}
\]

Here `p_A=Xi_{j,A} phi_j+Xi_j phi_{j,A}`. The actual motion of the
insertion is not replaced by a fixed-spinor derivative. In a compatible
volume realization

\[
 B_A=-M_4^{-1}M_{4,A}B
       +M_4^{-1}W_A^\dagger M_5
       +M_4^{-1}W^\dagger M_{5,A},                       \tag{10}
\]
\[
 (\iota^\sharp)_A=-M_4^{-1}M_{4,A}\iota^\sharp
       +M_4^{-1}\iota_A^\dagger M_\Sigma
       +M_4^{-1}\iota^\dagger M_{\Sigma,A}.              \tag{11}
\]

If the material kappa relation is preserved, `kappa_A/kappa=-I_A/(2I)`;
I_A is not set to zero and I_tau is not substituted for it. Source
jets of the carrier/Higgs/reset transport are retained as required.
Explicitly `c_A=-U^{-1}U_A c+U^{-1}(gamma_-)_A Psi_-`
for the map derivative, plus `U^{-1}gamma_- (Psi_-)_A` for field motion;
the plus trace has the corresponding gamma/field terms. Then
`G1_A=j_A(a-c)+j(a_A-c_A)`. Differentiate the allowed variations too:

\[
 P_A G_0\Psi+P(G_0\Psi)_A=E_Aw+Ew_A,\quad
 Q_A G_1\Psi+Q(G_1\Psi)_A=0,                             \tag{12}
\]
\[
 (E_{4,\rm seam})_A=-(E^\sharp)_A G_1\Psi
                         -E^\sharp(G_1\Psi)_A.          \tag{13}
\]

Thus even a fixed first-order trace relation does not erase source or
pairing derivatives. The full formula is executable in the new ordered
jet evaluator. The new arrays provide its known zero-source kernels,
including the **partial** `dJ/dlog(kappa)=-J` at fixed trace argument,
injection and average map. Along the preserved material relation in (7),
the trace's kappa dependence cancels that explicit partial term; the total
derivative still requires (8)-(11). **No numerical total physical photon jet
is claimed:** retained total map/state derivatives for this not-adopted
completion have not been generated. The old local affine-source partial
derivative, holding history and columns fixed, does not set (8) to zero.
An explicit one-control polynomial/duality test checks all product and
pairing terms; it is arithmetic, not a native source evaluation.

The selected proposal is linear in the fermion fields, so its second
fermionic derivative vanishes by its definition; its photon and geometry
jets do not vanish for that reason. For any nonlinear alternative keep
`D45(S_H o F)=D2 S_H[F4,F5]+DS_H[F45]`; its photon derivative includes
`D3 S_H[F_A,F4,F5]`, `D2 S_H[F4_A,F5]+D2 S_H[F4,F5_A]`,
`D2 S_H[F_A,F45]+DS_H[F45_A]` and all moving argument/pairing terms.
There is no zero action-gradient assumption and no extra bridge added
to an intrinsic action already owning it.

## Compatibility test and promotion boundary

On the physical localized range `F W=I`; on the full computational
rank16 range it is a physical projection, not identity. The representation
map respects Spin x SM, conjugate charge, family and common-A source
covariance with the correct transformed pairings. This does not select
a CAR covariance or prove new-domain state/evolution compatibility.

The **kinetic no-double-counting test is substantive**. On a localized
joint vector `Rw=(Ww,w)` with smooth trace, the proposed seam jump is zero,
and

\[
 R^\sharp A_{\rm joint}R=W^\sharp A_5W+A_4.               \tag{14}
\]

The adopted v14.45 bulk restriction already produces a wall kinetic
term. Calling both blocks one owner or using BW=I does not prove that
(14) equals the retained canonical local action. No equality or prescribed
subtraction accomplishing that matching is demonstrated here. Consequently
this candidate cannot yet be installed as the frozen native completion.
One would need an action-owned assignment of these kinetic contributions
or an explicit new compensating action term; neither is silently chosen.
The proposal also changes the matched smooth material law. These are
exposed limitations, not assertions that multiple complete BHSM solutions
exist. The additional physical decision remains the **joint seam action/
domain postulate with its localized kinetic matching**, not an eta value,
probe profile, measured mass, precursor wavefunction or numerical tolerance.

## Evidence and error scope

`replay_muon_proposed_dynamic_seam.py` hashes the two actual NPZ inputs,
state receipt, representation, relevant action/domain/source producers,
new derivation/code/test and records branch/HEAD. It evaluates no old
visibility, parent point, witness, normalization or history. Its source
frame equality checks are narrow guards on the two consumed caches.
New controls use the actual n1/n3 arrays for the Green coordinate identity,
material balance and unmatched-output preservation. Local adjoint arguments
are analytical; passing finite tests is not a uniqueness or tail theorem.

Adjacent binary64 endpoint arrays enclose each exact frozen binary scalar
product in (7). These certify multiplication rounding only. The inherited
b_vol/source, normalization, interface, history and continuum errors are
not replaced by those enclosures. Frobenius norms are descriptive, not
certified physical operator norms or Pauli uncertainties. The full total
photon derivative and coupled response remain unevaluated.

Reproduce this new calculation (a new output directory is required):

```powershell
C:\Python314\python.exe scripts/replay_muon_proposed_dynamic_seam.py --output artifacts/muon_proposed_dynamic_seam_20261005/replay_new
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_proposed_dynamic_seam.py
```

Frozen a_QED=0.00116550200495813; calibration-only standard uncertainty
1.79e-13 under the earlier alpha-inverse convention; Higgs local interval
(0,3.500331e-9); selected already-combined local interval
(0.0011655039493,0.0011655109506). They were not refined or re-added.
All six native ledger entries, physical a_mu, g_mu and native uncertainty
remain null. There is no experimental comparison. The result is a concrete
proposed seam action and conditional source-space readout, not an anomaly.

Executed scalar/readout results: b_vol=0.024964485717262674,
unweighted twelve-column J_left Frobenius norm=0.06115025169829208,
unmatched average-trace Frobenius norm=0.08225088464160911. These are
coordinate/model diagnostics. Maximum exact-product component rounding
errors are bounded by 1.710324995346446e-18 (n1) and
7.308150601506222e-19 (n3), excluding inherited input errors.
Four new checks passed in 0.87s. After independent review clarified the
fixed-trace partial normalization kernel and charge-conjugate bookkeeping,
the affected readout test was extended and rechecked: 1 passed in 0.81s;
the three unchanged checks are reused. Run1 is historical before that
kernel-label correction; run2 is the accepted packet. Its cache application
is rerun solely to save the corrected partial-kernel name/provenance,
without changing the J values or performing any old production calculation.
