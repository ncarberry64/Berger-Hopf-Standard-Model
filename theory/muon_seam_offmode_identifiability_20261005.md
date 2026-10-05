# Pre-mode seam identification: a source-directed identifiability result

Continuation from `065b6e0fe2b477e5b89867e5de6a9c685228ef02` on
`codex/muon-parent-maxwell-density-review`; scientific reference
`524ed90689bd5923c249bba2e699abf627e703cd`. The worktree began clean.
No old production calculation, exclusion proof, normalization identity,
reference wall contraction, handoff recovery, or prior check was repeated.
The accepted parent solution and all frozen local contributions are unchanged.

**New result:** a bounded, explicitly typed complement-to-seam witness is
nonzero on the actual twelve saved source columns after the chiral and Higgs
maps. Its forward and reverse actions satisfy the geometric Dirac-bar
pairing. This proves a specific limitation of the localized restriction:
it cannot determine the unrestricted mixed derivative. The witness is a
**proposed field assignment for an identifiability test**, not a selected
physical coupling, a new domain, an alternative solved BHSM background, or
a native operator update. No completion coordinate is selected.

## What the pre-mode fields actually denote

`completion/foundational_dirac_spin_glue_v14_45.py`,
`foundational_action_payload`, names the two oriented parent spinors
`Psi_eps` in the collar kinetic action and names `Psi_+,Psi_-` in

\[
 S_H=-\int_{M_4}(\bar\Psi_+Y_fH\Psi_-+\mathrm{h.c.}).       \tag{1}
\]

The spin/glue relation is between restrictions of that parent field. It
does not by itself identify an independent intrinsic wall variable with
one of these spinors. The later
`ae31_c2_intrinsic_m4_lepton_action.action_composition_contract` owns the
active intrinsic fields `L_L,e_R,H`, with their kinetic and Yukawa action.
AE4 retains independent canonical H5 and H4 summands and makes their local
terms expansions of one owner. A formula for this owner **as a function of
D_strat** is not a field identification constructing D_strat.

The inherited representation ledger fixes

\[
 L_L=(1,2,-\tfrac12),\quad e_R=(1,1,-1),\quad H=(1,2,+\tfrac12).
\]

Thus the left seam argument must have the left doublet type and the right
argument the right singlet type for the charged-lepton bridge. H carries
the representation map between them. A Spin-frame transition cannot
replace H. The rank16 all-left-Weyl ledger's `e_c` is the conjugate of e_R;
the right spin coordinates of the computational L-doublet carrier are
not thereby e_R. The normal auxiliary Clifford polarization is distinct
from intrinsic Lorentz chirality. The old metric `g_+,g_-` never enter this
fermionic identification.

These are adopted definitions. What is **not supplied by these definitions**
is the equality expressing the pre-mode seam spinors in the joint independent
parent/wall variables, including off-mode normal data. This is the relevant
action-matching postulate, rather than a missing value of Y or a missing
numerical implementation of the already assembled chiral mass block.

## Joint first variation and normal output

Write x=(Psi5+,Psi5-,w), w=(L_L,e_R), with the owned normal/trace data denoted
z5. If the action specifies g=F_b(z5,w), let F5 and F4 be its derivatives in
the actual geometric duals. A proposed joint realization can be organized
as S_rest+S_H(F_b), with **this same bridge excluded from S_rest**. It must
not append another Yukawa bridge to the full intrinsic action that already
contains it. The complete realization is not constructed by this notation.

Keeping barred/unbarred fermions independent and their bilinear order fixed,

\[
 e_H=\begin{pmatrix}-YH g_R\\-H^\dagger Y^\dagger g_L\end{pmatrix},
 \qquad \delta S=\delta S_{\rm rest}+\langle e_H,DF_b[\delta x]\rangle
                  +\text{bar-conjugate terms}.                 \tag{2}
\]

The general joint weak identity is consequently

\[
 \langle E_{{\rm rest},5},\delta\Psi\rangle_5
 +\mathcal G_{\rm rest}[\delta\gamma\Psi]
 +\langle E_{{\rm rest},4},\delta w\rangle_4
 +\langle e_H,F_5\delta\Psi+F_4\delta w\rangle_4
 =\ell[\delta x].                                             \tag{3}
\]

The known bulk Green form retains its adopted orientation and
symmetrization. **If F5=T gamma_trace**, the pullback T^sharp_D e_H is a
boundary cotangent and enters the normal balance with the known Green term.
In contrast, a bounded volume map F5=K adds K^sharp_D e_H to the
**distributed bulk Euler equation**. It is not a conormal. The wall equation
receives F4^sharp_D e_H in either case. An action-owned joint
allowed-variation relation may encode the trace version without a new
surface density. Neither Green cancellation nor a normalized mode selects
these field maps. The independent wall unknown is not assigned from Bp.
The insertion p=Xi_A phi is a diagnostic load/image; (2)-(3) do not require
p itself to belong to Dom(D_strat).

For a nonlinear F, the mixed derivative is

\[
 D_{45}(S_H\circ F)[v_4,v_5]
 =D^2 S_H(F)[F_4v_4,F_5v_5]
   +DS_H(F)[F_{45}(v_4,v_5)].                                  \tag{4}
\]

Its photon derivative differentiates both terms, all arguments, pairings,
and prescribed normal/domain maps. No action gradient or second jet is
silently dropped. Equations (2)-(4) are derived consequences **conditional
on a specified F**; they are not an adopted numerical F.

## A concrete coefficient that the restriction fails to select

Use only the inherited instantaneous volume inclusion W and its geometric
adjoint B, with the established BW=I. No identity is recalculated. Set
P_perp=I-WB. For this mathematical diagnostic choose the bounded real scalar
h=p_scalar/u on the saved compact source support and zero outside it. This
is a witness, **not a physical source extension or a wall profile**. In the
saved node3 nodal model h_max=0.24367577081469646; u is positive on its support.
The saved nonzero Gauss support is rho=0.5895359393258219..0.9812603874690746.

Define the full left-doublet map

\[
 K_L=\Pi_{L_L}B hP_\perp,\qquad
 g_L=L_L+\lambda K_L\Psi_5,\quad g_R=e_R,
                  \quad\lambda\in\mathbb R\text{ symbolic}.     \tag{5}
\]

Equation (5) is an **additional proposed argument assignment** in the
existing bridge, not a redefinition of L throughout its kinetic action.
Such a full redefinition would also require its kinetic cross and quadratic
terms. Neither operation is installed in the action.

From BW=I, K_L W=0. Therefore (5) preserves the bridge's localized-mode
restriction for every lambda. It is not claimed to preserve the unrestricted
Euler equations, physical pole or stationary solution. On any specified
dense domain where a bounded perturbation of this type is permitted, it
does not replace that domain by the nondense graph w=B Psi. Whether the
actual action permits or forbids this assignment remains part of the
missing matching postulate. The witness is not proof of two full physical
solutions to the retained theory.

On the actual source columns, with frozen b=Bp=0.024964485717262674,
chi=p-bu, and inherited mu4=19.439739968060266,

\[
 K_Lp_j=\eta\Pi_{L_L}\Xi_j,\qquad
 \eta=\frac1{\mu_4}\sum_i w_i\,\mathrm{volume}_i\,p_i(p_i-bu_i).
                                                               \tag{6}
\]

The direct p*chi contraction avoids recovering a small term by subtracting
large projected quadratic forms. The exact rational sum of the **frozen
binary inputs**, enclosed by adjacent binary64 values, is

\[
 \eta\in[0.0034617715565696053,\ 0.0034617715565696057].         \tag{7}
\]

This certifies this nodal contraction only. It does not recertify b, BW=I,
the continuum integral, temporal interpolation, endpoint trajectory, or
the physical action. Volume and Cauchy pairings are not interchanged.
No scalar norm, covariance angle, fitted parameter or physical scale is used.

The same-section unit Higgs is H1(w)=w(0,1), transported from sigma0 to
the saved sigma1 carrier. In the retained normalized harmonic convention,

\[
 \phi_{nmk}=\sqrt{n+1}\overline{D^{n/2}_{mk}},\quad
 H_{1,\rm upper}=-\phi_{1,-1,+1}/\sqrt2,\quad
 H_{1,\rm lower}=+\phi_{1,+1,+1}/\sqrt2.
\]

The new focused array check compares H1 H1^dagger with
(I-sum_a R_a3 sigma_a)/2 using the saved Ad_w coefficients. Its residual is
1.11e-16; H1^dagger H1 has no connected remainder in this representation.
This fixes the representation convention, not a Higgs amplitude or state.
The family Y and Higgs amplitude are left symbolic with their existing
producer/unit provenance; no GeV conversion or measured mass is inserted.

The **conditional** new mixed Euler coefficient per lambda is

\[
 E_{R5}^{(\lambda)}=-H^\dagger Y^\dagger K_L,\qquad
 E_{5R}^{(\lambda)}=-K_L^{\sharp_D}YH,\quad
 K_L^{\sharp_D}=\Gamma_{0,5}^{-1}K_L^{\sharp_{L2}}\Gamma_{0,4}.
                                                               \tag{8}
\]

For this volume witness, the reverse in (8) is distributed with radial
factor chi. It is not a boundary normal output and selects no boundary law.
The barred spinor dual exchanges Lorentz chiral projections. A Euclidean
transpose of the forward row would be the wrong reverse action. The full
projected unit-Higgs map H1^dagger Pi_L Xi on twelve coordinate columns
has norm 2.4494897427831783; (8)'s forward norm per lambda and unit Y/H
amplitude is 0.008479573919675807. The geometric bar pairing with the reverse
on all twelve test directions has absolute residual 7.35e-17. These norms
are diagnostics, not physical operator bounds or anomaly uncertainties.

Forward levels n=0,2,4 and reverse n=1,3,5 are evaluated before any
projection. The n4/n5 arrays cancel to floating precision on these
particular matched-image directions and remain saved. This is not a
resolvent/evolution complement theorem.

**Material limit:** the selected original source-coordinate combination
is nearly annihilated by this left extraction: projected norm 6.44e-17.
The full twelve-column operator is nonzero, but sensitivity of this
particular load, its propagated solution, or the complete Pauli readout is
not established. No alternative extraction was chosen to make it nonzero.

## Same photon source and remaining matching postulate

The differentiated coordinate is b, with beta=Tb b and AQ=sqrt(2) beta.
The cached source scalar/columns already contain their existing factors.
The quadratic action index 2/3, contact fraction and charge trace are not
inserted as vertex factors. The carrier and Higgs are in the same section;
the Higgs representation map is distinct from a spin-frame transition.

For an actual source-dependent identification the required derivative is

\[
 K_{L,A}=\Pi_{L,A}BhP_\perp+\Pi_LB_AhP_\perp
           +\Pi_LBh_AP_\perp+\Pi_LBhP_{\perp,A},\quad
 P_{\perp,A}=-W_AB-WB_A,                                      \tag{9}
\]

and the forward derivative is
-(H^dagger Y^dagger)_A K_L-H^dagger Y^dagger K_L,A, together with the owned
pairing/domain terms. A family preserving K_L(b)W(b)=0 must satisfy
K_L,A W+K_L W_A=0. If h is held fixed it is explicitly a diagnostic
definition, not a deduction that a physical profile/source jet vanishes.
No W_A, B_A, Higgs response or domain jet is filled with zero. Full gauge
covariance requires W/B to be the actual associated-bundle intertwiners;
the frozen-section witness does not establish it from a scalar norm.
Both oriented sheets and conjugate representations retain their prescribed
maps in (2)-(4); evaluation of one left-doublet witness assigns no zero to
their unevaluated physical entries.

**One additional physical postulate needed:** the pre-mode/current-owner
action must identify the seam spinors in terms of parent normal data and
independent L_L/e_R, or prescribe the equivalent joint variation and normal
incidence law. In particular it must determine its derivative on the
complement chi_j, and its same-b source derivative. Equations (5)-(8)
exhibit an explicit unselected coefficient there, while agreeing on the
localized restriction. The question is which assignment the action permits,
forbids or fixes; it is **not a request to choose lambda numerically**.
This is an additional model-identification requirement at the examined
effective-action scope, not an unfinished high-cost numerical solve.

The earlier scoped recovery limit is retained: this does not prove absence
of an identifying equation throughout all BHSM history. No same inspected
handoff was reopened. No full native wall Gram or coupled solve is updated
until an action-owned identification supplies (3)-(4) and its source jets.

## Evidence and replay

New module: `muon_seam_offmode_identifiability.py`. The standalone replay
reads the cached node3 state/branch24/actions, volume weights, independent
source columns, spin matrices, representation ledger and matched rotation.
It executes no previous producer. `input_hashes.json` binds those exact
files and the code. `joint_equations.json` separates adopted, derived and
proposed equations; `exact_nodal_eta.json` stores the rational numerator
and denominator. Arrays include forward, reverse, connected levels,
original coordinates, and the actual state/clock identities.

Four new targeted checks cover the fundamental/adjoint Higgs matching,
the exact nodal enclosure and nonzero projected source operator with the
original-load limitation, the geometric reverse Dirac-bar pairing, and
the distributed-versus-trace type of the evaluated reverse.
All pass. The new final packet is materialized twice from one in-memory
calculation for deterministic evidence; no old production is repeated.
Run1 preserves the initial numerical result; run2/3 record the
no-double-counting decomposition and original-load limitation. Run4/5
correct the general variational rule to distinguish the distributed
volume adjoint from a boundary cotangent. No previous output is overwritten;
all evaluated numerical arrays are unchanged.

```powershell
C:\Python314\python.exe scripts/replay_muon_seam_offmode_identifiability.py --output C:\Users\carbe\Downloads\BHSM_muon_seam_offmode_replay
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_seam_offmode_identifiability.py
```

All six native ledger entries remain null, never zero. No new physical
transfer direction or native heat action is evaluated. Frozen
a_QED=0.00116550200495813 with calibration-only uncertainty1.79e-13,
0<delta_h<3.500331e-9, and the already combined open selected-local interval
(0.0011655039493,0.0011655109506) are untouched. Physical a_mu, g_mu and
native theoretical uncertainty remain unevaluated.
