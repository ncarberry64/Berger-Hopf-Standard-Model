# Same-owner matching of the proposed average-trace seam

Continuation from `00dac33bd0d42434315b4b46e76e70b2d47f1c74`, preserving
the completed proposal, normal bilinear, J_chi arrays, four checks, parent
solution and frozen locals. Scientific reference:
`524ed90689bd5923c249bba2e699abf627e703cd`; branch
`codex/muon-parent-maxwell-density-review`, initially clean. This calculation
does not install the proposal, rerun the parent production or solve a tail.

**Result:** the proposed summed action has a well-defined direct localized
pullback, but its canonical angular/photon and once-owned Yukawa coefficients
do not match the adopted intrinsic action. The discrepancy persists after
tracking both field norms and normalizing all terms together. It is an
explicit proposed-action residual, not proof that an unnormalized sum alone
constitutes physical double counting. No compensating action is selected.

## Which action and operation are being matched

`foundational_dirac_spin_glue_v14_45.py::foundational_action_payload` owns
the parent geometric/common-A/eta kinetic action and the separate S_H
bridge. Its displayed normal-mode restriction, lines200–215, substitutes
the normalized mode with A_eta u0=0 and normal integral1; that is a **direct
restriction**. The canonical collective fermion field is defined before
reading physical bilinear couplings. The same S_H becomes the intrinsic
Y_l H bridge with unchanged Y, not an additional second Yukawa interaction.
`ae31_c2_intrinsic_m4_lepton_action.action_composition_contract` displays
that intrinsic bridge once. Its family operator is reused unchanged.

The previous **proposal** specifies S5,sym (kinetic/common-A/eta), the
intrinsic S4 (kinetic and that one bridge), and its new normal bilinear.
It does not attach another parent copy of S_H. The bridge's ownership
must be retained when taking this proposed direct pullback. Z_H=1 here:
the intrinsic active H kinetic action is unchanged; the proposal adds no
second Higgs kinetic term. This is a direct fermion-quadratic test in the
owned Higgs background, not a new Higgs-state solution.

`aether_unified_m5_m4_pushforward_v15_69.py`, lines39–78, separately owns
a **fixed-trace boundary effective action**, integrating complementary
fields. `ae4_stratified_dirac_zeta_induced_owner.py`, lines187–205, makes
the local actions expansions of one completed owner. Those statements
neither add a free action copy nor turn restriction into elimination.
At quadratic order, the latter would require the actual same-owner blocks

\[
 A_{\rm eff}=A_{RR}-A_{RQ}\,\mathrm{solve}(A_{QQ},A_{QR}),              \tag{1}
\]

and the source return, domains, pairing/field derivatives and saved finite
subtraction of that functional. This sprint evaluates A_RR of the proposal.
It does not evaluate (1), declare complementary fields stationary, or use
an adjustable Schur term to rescue the direct restriction. The existing
parent-bulk component solve is not the missing complete joint Schur action.

## Actual Rw and the complete direct quadratic density

Keep the independent wall w=(L_L,e_R) when defining the joint action.
For this matching test alone restrict to Rw=(Ww,w), with the retained
current full-cap scalar inclusion in the common Spin x SM section. Smooth
matched traces give G1 Rw=0, so the proposed normal seam bilinear vanishes.
Its derivative also vanishes along a consistently varied smooth localized
path; this does not assign its general source/domain jets zero.

The volume wall measure is mu4=2 pi² R_b³ in the proper boundary clock.
The parent volume measure is mu5=2 pi² nu C r³; the temporal Cauchy measure
is mu5/nu. Use the full-cap probability

\[
 dP=\mu_4^{-1}\mu_5u^2d\rho,\quad
 u=I^{-1/2}(\nu/\nu_b)^{-1/2}(r/R_b)^{-3/2}\sin(\rho/2),
 \quad I=\int_0^{\pi/2}C\sin^2(\rho/2)d\rho.                         \tag{2}
\]

Node3 uses the cached current I≈0.276366467174252355, its action-generated
I_tau≈1.31030283886746669, branch24, action_arc6 and the saved proper-clock
Y_tau. The 512 cached Gauss points cover **all64 cap cells**, not just the
compact source. I and the u/actions are reused, not refined. The metric
producer reconstructs only the instantaneous r,A,B values missing from
the consumed point NPZ, using that actual state and the saved R_b, then
the same nodal interpolation. No historical RADIUS0, new field actions,
endpoint-frozen coefficients or affine-logR rate are introduced.

Set alpha_t=<1/nu>_P, alpha_s=<1/r>_P, alpha_g=<b_g>_P,
where b_g=-B/(A sqrt(A²+B²)). The supplied current radial prescription
retains the normal cancellation, angular spin/Kosmann action, shift and
normalization/time/frame terms already present in D5 W. The general
unmatched carrier and connected angular outputs are retained. The direct
first-order spatial/action coefficients are

\[
 Z_L=Z_R=Z=1+\alpha_t,\quad K_s=R_b^{-1}+\alpha_s,\quad
 K_g=b_{g,4}+\alpha_g,\qquad Z_H=1.                               \tag{3}
\]

Equality of these **scalar principal residues** follows from the proposed
same radial density for the two physical chiral orientations, not from
misidentifying right-spin LL with e_R. L_L is the left doublet; e_R is
the charge conjugate of the e_c singlet. Each physical chiral mode uses
its designated bulk orientation once. Neither a second wall copy per
sheet nor the Nambu bookkeeping doubles its physical trace. The e_R
scalar coefficient follows the stated proposal, but a full e_R carrier
attachment and global domain are not claimed from the supplied LL tests.
The inherited weak common-A acts on L_L; the singlet's weak action is zero
by its actual representation. Spin, hypercharge, color and family stay
separate. The family Yukawa matrix remains the action-owned three-family
matrix; no GeV conversion or measured mass is used.

Let K_spin+ang denote the retained S_S3+i Gamma^a E_a action and G_SM the
common-A gauge unit. The direct density contains K_s times that action,
K_g G_SM, the once-owned -bar L YH e_R+h.c., and the symmetric temporal
term

\[
 S_t={i\over2}\int\mu_4 Z\,[w^\dagger\partial_\tau w
                         -(\partial_\tau w^\dagger)w].            \tag{4}
\]

Use Dirac-bar/action pairings for first-order action maps, not a positive
D5^dagger D5 Gram. The saved unsymmetrized comparison coefficient is
beta_raw=<a0>_P+3H/2; the Hermitian action's Euler connection is

\[
 \beta_{\rm sym}=\tfrac12(Z_\tau+3HZ).                            \tag{5}
\]

A real scalar i beta_raw w†w cancels from the explicit symmetric density.
It is not a mass. The new computation saves beta_raw, beta_sym and their
small frozen-model discrepancy separately, and contracts the **saved**
selected DW/DtauW outputs to verify the new coefficient reconstruction.
It does not regenerate full parent point actions.

## Norm and simultaneous canonical transformation

In the independent joint architecture, the direct volume norm is

\[
 N_{\rm vol}=1+\langle1\rangle_P\simeq2,
 \qquad N_\Sigma=1+\langle\nu^{-1}\rangle_P=Z.                     \tag{6}
\]

Thus the volume Gram alone is not the kinetic residue. On this proper
boundary clock the temporal Cauchy norm and temporal kinetic residue agree.
Define w=C w_c, bar w=bar w_c C† with C=Z^-1/2 on both physical sectors.
The canonical Cauchy norm becomes1, while the volume norm is N_vol/Z.
There is no change to the physical wall radius or source coframe.

Time dependence is included, using exactly the same saved first actions:

\[
 \alpha_{t,\tau}=\left\langle{1\over\nu}
       (C_\tau/C-I_\tau/I-L_\nu)\right\rangle_P,
 \quad C_{\rm field,\tau}=-{Z_\tau\over2Z}C_{\rm field}.          \tag{7}
\]

Here metric C and field C_field are distinct. L_nu is the saved direct
Fourier rate, not interpolation of nodal nu_tau. Angular derivatives of
the scalar residue vanish in this radial homogeneous realization; matrix
frame/carrier and Higgs derivatives still belong to their owned operators.
Scalar normalization derivatives cancel in (4)'s bidirectional density;
the canonical Euler measure term is 3iH/2. Equivalently, transform the raw
Euler comparison row and include its C_tau term before comparing (5).

**All interactions transform at the same time:**

\[
 K_{s,c}=K_s/Z,\quad K_{g,c}=K_g/Z,\quad
 (YH)_c=Z_L^{-1/2}(YH)Z_R^{-1/2}=(YH)/Z.                         \tag{8}
\]

The H field, its kinetic normalization/potential and background amplitude
are not retuned. Even under a different justified H_c=sqrt(Z_H)H,
Y_c=Y/sqrt(Z_L Z_R Z_H) and H_c=sqrt(Z_H)H, so their product remains
YH/sqrt(Z_L Z_R). A Higgs rescaling alone cannot restore this bridge.
The saved family matrices Y_c, Y_c,tau and Delta Y are numerical maps;
H and its physical amplitude retain their existing provenance.

For the same independent photon coordinate b_A, beta=T_b b and A_Q=sqrt(2)
beta remain applied once. Its parent spatial lift is T_b/r times the saved
unit kernel; the wall lift is T_b/R_b times that same kernel. Thus

\[
 V_{b,\rm raw}=T_b K_s V_{\rm unit},\quad
 V_{b,c}=T_b K_sV_{\rm unit}/Z,\quad
 V_{b,4}=T_bV_{\rm unit}/R_b.                                   \tag{9}
\]

The actual eight-lift rank16 kernels for n1/n3 are saved before any physical
projection. The LL source restriction is kept distinct from e_c ledger
bookkeeping and a completed physical e_R realization. No index2/3, contact
fraction or family/mode multiplier is inserted. The photon and spatial
covariant derivative share K_s/Z: conserved Q remains fixed. Their common
change is an action/coframe mismatch, not a fitted electric charge or Pauli
coefficient. The time current has the canonical Cauchy normalization.

All source/spacetime transformations must be differentiated together:

\[
 (A_c)_A=(C^\sharp)_A A_R C+C^\sharp(A_R)_A C+C^\sharp A_R C_A,    \tag{10}
\]

where an operator acts on C and its derivatives. (A_R)_A includes R_A,
trace/normal transport, pairing and domain movement from the same source.
The geometric-adjoint derivative contains the measure derivatives. For
scalars C_A=-(Z_A/(2Z))C, and (Y_c)_A=Y_A/Z-Y Z_A/Z². The direct b-source
partial holds the cached geometry/history fixed, so this scalar Z partial
is zero by that declared source-coordinate independence. It is **not**
an evaluation of the total physical Z_A, state response or global source
jet. Those unknown total derivatives remain unevaluated, not zero. The
code also saves the actual temporal vertex derivative using
T_b,tau=-H T_b/2, R_b,tau=H R_b and alpha_s,tau from the same cache.

For reduced independent Grassmann coordinates this field change has
formal log Jacobian Tr_physical log Z (both bar/unbar variables transform).
No unconstrained doubled trace is used. This is the formal measure rule
for a reduced coordinate transformation, **not proof that restriction
defines the full joint path integral or its measure**. A regulated infinite
functional trace, its source variation and finite subtraction are not
evaluated or silently discarded. They cannot be chosen to force matching.

## Evaluated mismatch and the full diagnostic identity

Approximate node3 values in the frozen full-cap nodal quadrature model:

| Quantity | Value |
|---|---:|
| alpha_t | 1.108982901971856 |
| alpha_s | 1.2286849486710774 |
| Z_L=Z_R | 2.108982901971856 |
| N_vol | 2.0 |
| canonical volume norm | 0.948324426020733 |
| canonical angular/photon ratio to adopted | 1.0537969211428857 |
| once-owned Yukawa/Higgs factor | 0.4741622130103665 |
| canonical b-vertex scalar | 0.2390075938105358 |
| adopted b-vertex scalar | 0.22680612271226067 |

The explicit residual is

\[
 \Delta K_s={\alpha_s-\alpha_t/R_b\over Z},\quad
 \Delta K_g={\alpha_g-\alpha_t b_{g,4}\over Z},\quad
 \Delta(YH)=(Z^{-1}-1)YH,\quad
 \Delta V_b=T_b\Delta K_s V_{\rm unit}.                          \tag{11}
\]

The photon residual is the source derivative of the changed spatial action,
not another independent addend. The normal seam bilinear supplies no
localized correction when G1=0. A proposed replacement/compensation would
have to address (11), its source/spacetime derivatives, representation,
norm and measure together. Its negative is only a formal required
compensation; no examined equation makes it an adopted subtraction. Nor
is an unevaluated complementary Schur term (1) permission to select that
negative value. Direct matching is therefore **not established**.

The compact diagnostic p is not a joint-domain field or a prescribed wall
unknown. Use its **full** trace readout. From the saved proposal and cached
normalized WBp input, without recalculating J_chi,

\[
 F_L(WBp)+F_L(p-WBp)=b_{\rm vol}\Pi_L\Xi
                      -b_{\rm vol}\Pi_L\Xi=F_Lp=0.              \tag{12}
\]

The actual n1/n3 arrays and the residual of (12) are saved. Multiplying the
complete readout by sqrt(Z) for the canonical wall coordinate preserves
the zero. Differentiating the full identity retains all moving F,W,B,p
terms; none is an independent extra source. Compact support remains
separated from the material wall for the inherited source family. J_chi
alone cannot be inserted as a new forcing or anomaly contribution.

## Reproducibility and error boundary

`replay_muon_proposed_seam_matching.py` creates a new output directory with
coefficient enclosures, actual first-order/canonical/source maps, both
norms, temporal jets, interaction ledger, input hashes, revision and compact
checkpoint. `test_muon_proposed_seam_matching.py` checks full-cap norm versus
kinetic residue, simultaneous canonical transformations, cached-action
consistency, the shared spatial/source ratio and complete source cancellation.
Previous checks and parent production were not replayed.

Arb at192 bits encloses the indicated products of frozen binary operands
and the saved full-cap I/I_tau nodal certificate. The small instantaneous
metric reconstruction is frozen after its binary64 evaluation. These are
arithmetic enclosures of the existing512-point/8-per-cell quadrature model;
they are **not** a new quadrature, history/tube or continuum certificate.
Matrix outputs are binary64 representatives. An explicit nonzero model
residual is not a physical operator norm, anomaly or uncertainty estimate.

```powershell
C:\Python314\python.exe scripts/replay_muon_proposed_seam_matching.py --output artifacts/muon_proposed_seam_matching_20261005/replay_new
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_proposed_seam_matching.py
```

The accepted parent response is unchanged. Frozen a_QED=0.00116550200495813,
calibration-only uncertainty1.79e-13, Higgs local interval(0,3.500331e-9),
and already-combined selected-local interval(0.0011655039493,0.0011655109506)
are neither modified nor re-added. All six native contributions, physical
a_mu/g_mu and native uncertainty remain null. Next: an action-owned
replacement/compensation or evaluated same-owner complementary response
that supplies the **joint kinetic and interaction** matching; no such
term is derived merely by normalizing this proposed summed action.
