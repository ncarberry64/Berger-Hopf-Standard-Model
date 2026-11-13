# Fermionic seam identification: exact scope of the recovered action

Continuation from `8b74533c919df350ca176f8daaef4db6658f1f53`, on
`codex/muon-parent-maxwell-density-review`; scientific reference
`524ed90689bd5923c249bba2e699abf627e703cd`. The worktree began clean.
The completed source-role correction, Green columns/time jet, accepted
parent solve, reference wall rows, all old checks and frozen local results
were preserved without replay. No production operator was changed.

**New result.** The recovered *explicit* compatibility action has an
identically zero fermionic constraint Jacobian and mixed bulk/wall
derivative. Its reciprocal successor does too. This is proved from the
actual incidence types and expressions, not an open status label. Together
with the separate wall Euler action and the scope of the sheet/reset glue,
this establishes why those examined equations cannot supply the missing
independent-H4 attachment. It does **not** establish that the full native
AE4 mixed entry is zero. That entry remains unevaluated.

## Recovered variational terms and their field types

`master_action/reduction.py:authoritative_action` and v7.1 give

\[
S_{\rm compat}=\int_{M_5}\langle\Lambda_{85},g_5-Q_H(G_8)\rangle
 +\langle\lambda_\sigma,\sigma_5-P_0\sigma_8\rangle
 +\sum_\epsilon\int_{M_4}\Lambda_{54,\epsilon}^{ab}
 (h_{ab}-\iota_\epsilon^*g_{5,ab}).
\]

The original g_+/g_- here are **cap metrics**, not spinor seam arguments.
In the fermionic bridge below, g_+/g_- name spinor arguments; the two uses
must not be identified. `attachment_incidence_ledger_v11_3.incidence_rows`
types Q_H(G8) and id_5(g5) as symmetric covariant two-tensors, Lambda85 as
their dual density, lambda_sigma as scalar, and Lambda54 as a dual metric
tensor density. The actual reciprocal action is

\[
S_{\rm attach}=\int_{M_5}\langle\Lambda_{85},
 \upsilon^{-1/2}g_5-\upsilon^{1/2}Q_H(G_8)\rangle .
\]

It leaves the scalar and Lambda54 metric matchers unchanged. Its boundary
producer states that it is algebraic and creates no normal momentum or
presymplectic potential. This is a bosonic attachment, not a spinor normal
output. Later AE4 replaces independent Wilson *ownership* by one spectral
owner; no retired numerical coefficient is reintroduced here.

Let x_F=(bar-Psi5,Psi5,bar-w,w) with w=(L_L,e_R), and C the four
componentwise constraints (85, scalar,54+,54-). At fixed owned bosonic
inputs, every actual expression above is independent of x_F. Thus

\[
D_{x_F}C=0,\qquad\operatorname{rank}D_{x_F}C=0,\qquad
 D_{\bar w}D_{\Psi_5}S_{\rm compat}=0,\qquad
 D_{b_A}D_{\bar w}D_{\Psi_5}S_{\rm compat}=0.                 \tag{1}
\]

This is exact in the full tensor/scalar pairing: it holds componentwise
and hence against every Sobolev test direction, including the twelve
saved source directions and both sheet orientations. It requires no
finite compression, angular truncation or numerical cancellation. It
does not eliminate bosonic fields, set their mediated quantum responses
to zero, or evaluate the native heat contraction. The replay transcribes
the actual pairings componentwise and checks their producer expressions
and types before issuing this certificate.

## What the fermionic equations determine

The adopted v14.45 action supplies D5 and the bridge

\[
S_H=-\int_{M_4}(\bar g_+YH g_-+\bar g_-H^\dagger Y^\dagger g_+).
\]

Its left variations, with the bilinear order unchanged, are
-YH g_- and -H^dagger Y^dagger g_+. Its normal-mode restriction has
Psi_epsilon=W_eta psi_epsilon and unit normal overlap. The v15.56
successor explicitly calls Y_f **intrinsic** and proves its on-mode
coefficient is unchanged. It does not add an off-mode identification of
the bridge arguments with independent canonical H5/H4 unknowns.

AE31 independently transports the intrinsic active fields L_L,e_R,H:

\[
E_L=i\slash D L_L-Y_lH e_R,\qquad
E_R=i\slash D e_R-Y_l^\dagger H^\dagger L_L.
\]

This explicit action term has no Psi5 argument, so its fixed-coefficient
mixed derivative with Psi5 vanishes too. The assembled family LR mass
block and its units are retained. Nothing here reopens that block or
changes the common-A covariant derivative.

The complete *known* first variation consists of the bulk Euler terms,
the already evaluated normal Green term, the wall Euler terms, and the
bridge variations on its supplied arguments. For a joint interpretation,
the chain rule additionally needs

\[
(g_+,g_-)=\mathcal F_b(\gamma_{5,+}\Psi_{5,+},
                      \gamma_{5,-}\Psi_{5,-},L_L,e_R),       \tag{2}
\]

or the equivalent prescribed joint allowed-variation and normal-output
relation. This is the missing **field-identification equation**, not a
request for a new coupling constant. A nonlocal normalized overlap can
replace a pointwise gamma argument if the action prescribes it; neither
choice is inferred from a norm.

For a linear identification at the retained fermionic background, write
J5=D_Psi5 F and J4=D_w F, in the actual geometric duals. The bridge's
mixed contribution is

\[
c_{45}^{H}(v_4,g_5)=\langle J_4v_4,\mathcal H_H J_5g_5\rangle,
\quad\mathcal H_H=-\begin{pmatrix}0&YH\\H^\dagger Y^\dagger&0\end{pmatrix}.
                                                               \tag{3}
\]

Any prescribed domain/normal-output contribution must be included as
well. A nonlinear identification adds the action-gradient/second-jet
chain-rule term; no vanishing classical field is silently assumed here.
The same photon derivative of (3) contains J4_A, J5_A, H_H,A and the
pairing derivative. Specifying Xi5 and Xi4 alone does not specify those
attachment jets. Equation (1) supplies none of them. The replay evaluates
only (1); (3) is a defining conditional relation, not a new operator
evaluation accepting guessed matrices.

The global-spin prescription identifies two restrictions of one parent
field. Their opposite normal Green forms cancel for the transmitted
variations. AE2 likewise identifies event/child traces and the corresponding
normal outputs of that same field. Neither equation contains an independent
intrinsic w. Consequently their cancellation does not convert the known
bulk Green column into the independent wall Euler mixed row. No new birth
phase or physical boundary condition is requested.

The v15.69 fixed-trace functional names a normalized wall-spinor trace B
but does not give equation (2) on the current complement. A boundary
parameter of a critical-value functional is not, by its name alone, an
independent-H4 domain vector. AE4 selects the canonical direct-sum trace
and the E1 functional **of** D_strat; its definition cannot determine an
unassigned entry of D_strat by differentiating that same functional.

## Why the normalized restriction is insufficient on the reached space

From B_eta W_eta=I one knows only the restriction on ran(W_eta). For any
candidate linear identification T on a compatible domain, the addition
L(I-W_eta B_eta) leaves T W_eta unchanged. This is a restriction theorem,
not a selected physical interaction or proposed boundary-family member.

The existing node3 result already demonstrates the relevant distinction
on the actual source: normalized volume B_rad p=0.024964485717262674 Xi,
whereas its geometric material trace is zero. On W, normalized mode
projection and the appropriately scaled geometric trace both return the
wall coordinate. Thus the on-mode identity cannot decide the needed
off-mode map. These numbers and the earlier bounded-graph obstruction
are cited from their accepted artifacts, **not recalculated**. The forcing
p=Xi_A phi remains a diagnostic load/image and need not be in Dom(D_strat).
No Theta_p is assigned from either map.

## Local handoff recovery and limits of the finding

The focused recovery included Downloads' owned-connection, attachment
reconciliation, connection-attachment, radial-inclusion and daughter-collar
packets, plus the original workspace action-source and fermion-body reports.
Their exact file identities are saved in input_hashes.json.

The owned-connection report fixes the common associated-bundle connection;
the daughter packet fixes eta and normalization; radial run3 retains the
full W psi+chi event/child trace graph. The original action-source report
defines the required open-fermion/source insertions, and the fermion-body
report supplies intrinsic propagation. None of these examined equations
identifies an independent H4 variation with an off-mode parent trace or
provides its reverse normal output. The older missing-common-A interpretation
is superseded and was not used.

**Demonstrated insufficiency:** equations (1), the displayed wall Euler
action, and same-dimensional spin/reset glue cannot produce the missing
joint attachment; the bridge restriction does not determine (2).
**Recovery limit:** no additional equation (2) was found in these concrete
current producers and handoffs. This is not an exhaustive absence theorem
over all BHSM history, and is not a statement that BHSM cannot supply such
an equation. It is an open part of this examined current realization,
rather than a large numerical calculation awaiting more compute.

## Execution, error scope and continuation

Executed: AST extraction of the named producers and exact symbolic
derivatives of their explicit compatibility density. Run1 is preserved;
run2 corrects its overly narrow "first jets" wording for a possible nonlinear
identification. The derivative certificate is unchanged. Four new targeted
controls check producer-to-proof typing, the linear source chain rule, the
restriction theorem, and the nonlinear gradient/second/source-jet term.
No prior milestone check, production calculation, Green column,
parent solve, normalization or covariance witness was replayed.

No native wall row, wall Gram, updated solution, native heat or physical
transfer direction was executed. All native ledger entries remain null:
native_bulk_heat, state_variation, contact, domain_boundary,
completion_counterterm, strong_within_native. Zero in (1) belongs only to
the explicit known compatibility term and is never used to fill this ledger.

The exact algebra has no rounding uncertainty. The inherited node/trajectory,
endpoint/tube/interpolation and continuum scopes are unchanged. No bound on
unresolved attachment, spectral tails, renormalization, or a_mu is inferred.
Frozen local contributions remain
a_QED=0.00116550200495813, calibration-only uncertainty1.79e-13,
0<delta_h<3.500331e-9, and the already combined open selected-local interval
(0.0011655039493,0.0011655109506). Nothing is added to that interval; its
calibration uncertainty is not a total error bound. Physical a_mu and
g_mu=2(1+a_mu) remain unevaluated.

Reproduction (a new output directory is required):

```powershell
C:\Python314\python.exe scripts/replay_muon_fermion_seam_identification.py --output C:\Users\carbe\Downloads\BHSM_muon_fermion_seam_identification_replay
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_fermion_seam_identification.py
```

**One next unresolved operand:** equation (2), or its equivalent joint
allowed-variation/normal-output prescription, restricted to the twelve
source-reached response directions and differentiated under the same b_A.
Its producer is the pre-mode fermionic M5/M4 attachment in the current AE4
domain; its immediate consumer is E45 and the paired bulk normal output.
Once supplied, those jets can be consumed in the native wall row and coupled
response without changing the source, pairing, state or frozen locals.
