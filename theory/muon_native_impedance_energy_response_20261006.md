# AE4 length and the retained operator-valued formation owner

Starting revision: `bec47682373873a6e6d8d5427a4ee20aa894b125`.
Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`.
Branch: `codex/muon-parent-maxwell-density-review`, PR #465.

The new result is an **owner reconciliation and exact mode-reduction
derivation**. The September 6 operator-valued formation rule supersedes the
old scalar holding-ratio interpretation. It does not supply the additional
identity connecting that formation mode to AE4's dimensional cutoff energy
and support-loss surface. The independent scalar constitutive-law route in
the earlier next-step wording is withdrawn.

This is a precise incomplete owner definition, not an unfinished scalar
numerical solve. It is not a proof that no compatible future amendment can
exist, and it does not supersede the AE4 finite-E1 heat functional itself.
Physical `E_vJ`, length jets, `R_ind`, native photon/family heat response,
`a_mu` and `g_mu` remain unevaluated.

## Chronology and current authority

| Record | Commit and committed time (UTCâˆ’05) | Actual prescription |
|---|---|---|
| AE4 spectral owner | `999be702056dce48850e1e91329d3beb12b98401`, September 1, 19:16:52 | `ell_star=1/E_impedance` at impedance/core equality **and outward-support loss** |
| Track-2 interface-action decision | `520b37207cb7a2de45440535dd9cfd196579d8c4`, September 6, 07:16:11 | excludes synthetic holding/impedance values and guessed scalar conservation laws |
| Minimal covariant interface mechanics | `c4eeb2d548b8e49d811af23e4ce58a743a136414`, September 6, 09:07:10 | selects the regular worldvolume action and `RHO-B2`; historical scalar ratio is only a valid one-mode/common-charge reduction |

These dates come from file-specific Git histories, not version-number
ordering. The three corresponding primary-checkout sources are byte-identical
to the PR copies; no newer primary-source change was discarded. The retained
materialized Track-2 decision and mechanics JSON are also read as scientific
provenance, rather than treating Git as the entire record.

The actual equations are in:

- `ae4_stratified_dirac_zeta_induced_owner.native_spectral_length_contract`,
  lines 68â€“91;
- `owner_authorized_encapsulation_interface_action.invariant_control_arguments`,
  its exclusion of historical synthetic scalar values, and the total-action
  Noether conservation rule;
- `covariant_bubble_interface_mechanics`, lines 213â€“265, including the
  formation Hessian, harmonic inertia and `RHO-B2` denominator;
- `theory/bhsm_covariant_bubble_interface_mechanics.md`, lines 110â€“117 and
 152â€“156, for the one-mode/common-charge restriction and Track-2 scope.

The older `IF5` functional freedom is not reopened: September 6 mechanics
selects its minimal area member. Its environmental stiffness is
`gamma_s=alpha_FSC ell_s^(-m_s)`. The actual record uses the regular length
in `Lambda_s`, with `ell_kappa` as the existing reference. It does not
declare `ell_s=ell_star`. No equality or additional scale is inserted here.

## What the formation quotient actually determines

On the relevant common constrained response space write

\[
 Z=H_{\rm impedance},\quad S=\gamma J_\Sigma,\quad
 R=S+Z,\quad D=H_{\rm event,drive},\quad A_{\rm form}=R-D.
\]

Here the identification of the constrained bulk response with the impedance
in the quotient is the **same response/domain identification in the retained
formation statement**, not replacement by the muon photon or spinor matrices.
The formation number is

\[
 \rho_B=\sup_{\psi\ne0}
       \frac{\langle\psi,D\psi\rangle}
            {\langle\psi,R\psi\rangle}.
\]

For an admissible selected simple crossing line,
`(R-D)psi_star=0`. A valid common-charge scalar reduction on that line,
with an **action-derived** positive normalization form `M_E`, gives

\[
 E_R=\frac{\langle\psi,R\psi\rangle}
             {\langle\psi,M_E\psi\rangle},\quad
 E_D=\frac{\langle\psi,D\psi\rangle}
             {\langle\psi,M_E\psi\rangle},\quad E_R-E_D=0.
\]

The denominator of this historical formation-ratio reduction is therefore
the **total resistance**, not bulk impedance alone. Using Z alone instead
gives the exact threshold residual

\[
 \frac{\langle\psi,(Z-D)\psi\rangle}
      {\langle\psi,M_E\psi\rangle}
 =-\frac{\gamma\langle\psi,J_\Sigma\psi\rangle}
          {\langle\psi,M_E\psi\rangle}.
\]

It vanishes only when that particular surface contraction vanishes. The
retained equations do not establish its vanishing on a selected muon
crossing line. The new symbolic calculation preserves this residual exactly;
no surface term is dropped and no synthetic numerical `rho_hold` is computed.

This identifies the formation-ratio denominator. It does **not** identify
either R or Z as AE4's `E_impedance`: neither the equation
`E_core_AE4=E_D` nor the equality of the formation and support-loss events
is supplied by these records.

## Formation eigenline versus energy eigenline

An important distinction controls the proposed derivative calculation:

\[
 (R-D)\psi=0\quad\not\Rightarrow\quad R\psi=E M_E\psi.
\]

A simple formation mode need not make the resistance Rayleigh quotient
stationary. For an `M_E`-normalized moving line,

\[
 E_{R,x}=\psi^\dagger(R_x-E_R M_x)\psi
   +\psi_x^\dagger(R-E_R M)\psi
   +\psi^\dagger(R-E_R M)\psi_x.
\]

The embedding terms disappear only if the actual energy eigenproblem
holds, or if a proved restricted identity removes them. A one-dimensional
compression is possible, but its derivative includes derivatives of the
embedding `iota_star`; the bare operator jet does not suffice.

An exact **identification control**, not a BHSM realization, demonstrates
this implication failure. Let `u=x+y`,

\[
 A(\tau,u)=\begin{pmatrix}\tau&u\\u&1\end{pmatrix},\qquad
 R=\begin{pmatrix}2&1\\1&3\end{pmatrix},\qquad
 \tau_*(u)=u^2,\quad
 \psi_*(u)=\frac{(1,-u)^T}{\sqrt{1+u^2}}.
\]

The line is exactly normalized and `A(tau_*,u)psi_*=0`, with a simple
crossing near zero. Yet `R psi_*(0)=(2,1)^T` is not `2 psi_*(0)`. Although
`R_x=R_y=R_xy=0`, its selected-line contraction is
`(2âˆ’2u+3uÂ²)/(1+uÂ²)`, with first derivativesâˆ’2 and mixed derivative 2.
Bare Hellmannâ€“Feynman on R would incorrectly return zero. No such matrix,
mode or number is installed in the physical action.

## Complete generalized energy-eigenbranch response, when justified

For a **genuine**, isolated Hermitian energy eigenbranch on a common
differentiable form pullback,

\[
 H\psi=E M\psi,\quad \psi^\dagger M\psi=1,\quad
 T_x=H_x-E M_x,\quad E_x=\psi^\dagger T_x\psi,
\]

the required complement response is obtained by a bordered linear solve:

\[
 \begin{pmatrix}H-EM&M\psi\\\psi^\dagger M&0\end{pmatrix}
 \binom{r_x}{\lambda_x}=\binom{-T_x\psi}{0},\qquad
 \psi_x=r_x-\tfrac12(\psi^\dagger M_x\psi)\psi.
\]

No full inverse is formed. This fixes `psiâ€ M r_x=0` and the phase gauge
`Im(psiâ€ M psi_x)=0` for real Hermitian source parameters. The mixed result is

\[
 E_{xy}=\psi^\dagger(H_{xy}-E M_{xy}-E_xM_y-E_yM_x)\psi
       +\psi^\dagger T_xr_y+\psi^\dagger T_yr_x.
\]

Equivalently, the two pair terms are minus the corresponding reduced
resolvent contractions. For fixed M this reduces to the familiar
`<H_xy>âˆ’<H_x psi,R_red H_y psi>âˆ’<H_y psi,R_red H_x psi>`.
Both first M-jets, the mixed M-jet, energy-metric cross terms and longitudinal
normalization are retained. Unit modal norm does not establish `M=I` as an
operator or prove its source jets zero.

For the actual complex current directions, extend coefficients of the real
`v,b_A` Hessian using the frozen current weights. Daggering a complex-linear
direction directly would conjugate those weights incorrectly. The local
32Ã—8 sources,224 current labels, `b/beta/A_Q` conversions and their source
directions remain unchanged; no photon variation is relabeled as a shape
variation or multiplied by the action-index factor 2/3.

If the selected physical line is only a formation eigenline, differentiate
that formation pencil and retain its first **and mixed** eigenline response
in the normalized resistance contraction. In particular the mixed terms
`psi_xyâ€ (R-E_R M)psi + adjoint` need not disappear. The code's energy-
eigenbranch routine cannot silently replace this calculation.

## Crossing and AE4 consumption

Only after the same-action energy/surface identification is justified may
the existing length formulas be consumed. On a simple selected crossing
`F=0`, implicit differentiation gives

\[
 \tau_x=-F_x/F_\tau,\quad
 \tau_{xy}=-\frac{F_{xy}+F_{\tau x}\tau_y+F_{\tau y}\tau_x
                         +F_{\tau\tau}\tau_x\tau_y}{F_\tau}.
\]

For an energy branch defined at fixed tau, the total selected-surface response
is `E_total,x=E_x+E_tau tau_x` and

\[
 E_{\mathrm{total},xy}=E_{xy}+E_{\tau x}\tau_y+E_{\tau y}\tau_x
                 +E_{\tau\tau}\tau_x\tau_y+E_\tau\tau_{xy}.
\]

Intrinsic eigenline motion belongs in the fixed tau energy jet; surface
motion is then included once. A direct computation along the surface already
contains both and must not receive a second crossing correction.

The previously derived `ell=1/E_total` and `c=ellÂ²` chain rules remain valid
conditionally. The AE4 lower-limit mixed contribution remains the retained

\[
 -\tfrac12c_x\operatorname{STr}(e^{-cP}P_y)
 -\tfrac12c_y\operatorname{STr}(e^{-cP}P_x)
 +\frac{T(c)}{2c}c_{xy}
 -\tfrac12\left[\frac{\operatorname{STr}(Pe^{-cP})}{c}
                 +\frac{T(c)}{c^2}\right]c_xc_y.
\]

No physical E/length jet has been supplied by this reconciliation, so no
numeric length contribution is inserted and no `ell=1` default is used.
`R_ind`, the completed photon response and the family heat consumer remain
unevaluated. No later Pauli requirement is used as a gate for this work.

## Exact owner amendment required

The unresolved owner identification concerns AE4's scalar inverse-energy/
support-loss prescription and the later operator/common-charge restriction
on the old scalar picture. The latter is current for formation; it is
**not** an amendment selecting a numerical cutoff energy. These distinct
event rules are not proved contradictory.

For the historical formation-ratio compatibility schema below, the smallest
useful matching statement must identify:

1. the same selected constrained eigenline/event, including the relation
   between the formation zero and AE4's support-loss/core surface;
2. the common-charge energy normalization `M_E`, with units making
   `E_impedance` an energy and `ell_starÂ² P_strat` dimensionless;
3. the operator combination whose normalized contraction is AE4's scalar.

A compatibility schema for the historical formation interpretation is

\[
 E_{\rm impedance}^{\rm AE4}
   =\frac{\iota_*^\dagger R\iota_*}{\iota_*^\dagger M_E\iota_*},\qquad
 E_{\rm core}^{\rm AE4}
   =\frac{\iota_*^\dagger D\iota_*}{\iota_*^\dagger M_E\iota_*}.
\]

This schema is **not adopted** here. Its normalization and event identities
are not consequences of the quotient. A different already-owned scalarization
would need its explicit action equality/provenance instead. Choosing Z alone,
choosing R by name, normalizing with an arbitrary identity matrix, or choosing
inverse eigenvalue versus inverse frequency would add a new assumption.
The harmonic equation `I_lambda D_tauÂ² a +(gamma j+Z)a=f` provides inertia;
it does not by itself identify its stiffness eigenvalue with an energy.
No observed mass, lifetime, anomaly, alpha, fitted scale or new function is
requested or inserted.

This is an explicit same-action matching amendment to the existing owner,
not a demand to reconstruct the entire history or close every Track-2/Gate-7
condition. It cannot be resolved by more precision on the frozen muon
matrices. A compatible amendment could exist; an absolute incompatibility
theorem for all possible reductions is not claimed.

## Executed checks and provenance

Eight new targeted checks pass. They include the actual owner equations and
chronology, exact total-resistance/bulk-only residual, formation-versus-energy
line distinction, generalized first/mixed perturbation, an independent mixed
equation and normalization solve, fixed-M reduction, and once-only crossing
chain rule. The old seven checks and all production were not rerun.

The 3-dimensional supplied **arithmetic control** uses a nonidentity M with
nonzero first/mixed M-jets. Its first directional equation residual is
6.94e-18 and mixed symmetry residual is zero. Its mixed derivative is
0.033374773374773375; direct two-parameter differences agree to 1.46e-11 at
step 1e-3. Smaller steps have larger subtraction roundoff (up to 3.35e-9 at
2.5e-4), so no convergent enclosure or rigorous remainder is inferred.
Perturbed M-normalization residuals are at most 6.66e-16. Dropping moving M
changes that control's mixed derivative by 0.00221704221704222. These numbers
are neither BHSM physical operands nor muon anomalies/error estimates.

The initial fetch emitted stale-worktree metadata permission warnings from
Git automatic maintenance. A fetch with automatic maintenance disabled
completed; no manual deletion, cleaning or metadata repair was attempted.
The working branch and PR head were verified. Physical domains, source
continuation, accepted parent solution, family/time jets, corrected source
arrays, primitive response and frozen local values are unchanged.

New artifacts are under
`artifacts/muon_native_impedance_energy_response_20261006/run_1/`.
They include 15 input/source SHA-256 identities, exact chronology,
reconciliation, normalized complement-control actions, conditional response
equations, the minimal amendment, error scope and checkpoint. Physical
H/M/state/source-jet and downstream quantities are explicitly null.

Reproduce into a fresh directory:

```powershell
C:\Python314\python.exe scripts/replay_muon_native_impedance_energy_response.py --output <fresh-directory>
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_native_impedance_energy_response.py
```

Source snapshots preserve executed bytes; canonical-LF hashes distinguish
line-ending changes from scientific source differences. Publication metadata
records the exact scientific revision and verified PR head. The older
checkpoint's local evaluated arrays and generic implicit-length identities
remain evidence; its independent scalar-law next-step wording is superseded
by this report.
