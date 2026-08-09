# BHSM v14.45 — Foundational eta-bound Dirac action, global spin glue, and renormalized bifurcation gate

## Primary verdict

`BHSM_V14_45_ADOPTS_THE_CANONICALLY_NORMALIZED_TWO_SIDED_ETA_BOUND_DIRAC_ACTION_AND_GLOBAL_PARENT_SPIN_BUNDLE_AS_FOUNDATIONAL_EFFECTIVE_DATA_NOT_AS_A_DERIVATION_FROM_PATH_B`

## Secondary verdict

`THE_NORMAL_ETA_ZERO_MODE_PULLBACK_AND_GLOBAL_SPIN_GLUE_FIX_THE_FOUR_DIMENSIONAL_KINETIC_NORMALIZATION_AND_SEAM_MATCHER_WITHOUT_GENERATING_RELATIVE_FLAVOR_HOLONOMY`

## Renormalization verdict

`THE_L2_L3_FERMION_DETERMINANT_CANNOT_PREDICT_A_BIFURCATION_UNTIL_TWO_INDEPENDENT_RENORMALIZED_GRAVITATIONAL_COUNTERTERM_CONDITIONS_ARE_FIXED`

## Exact next object

`FULL_PREIMAGE_MICROSCOPIC_REGULATOR_OR_RENORMALIZATION_CONDITION_FIXING_C2REN_C4REN_TOGETHER_WITH_NORMALIZED_COMPACT_CAP_SPINOR_HARMONICS_AND_L2_L3_KOSMANN_SPECTRAL_SUMS`

---

## 1. Why this sprint takes a foundational branch

v14.43 and v14.44 established that the bosonic Path-B eta action, its moduli
Hamiltonian, and the flat FR sign line do not derive local Grassmann fields or a
spacetime Clifford principal symbol.  Continuing to relabel the conditional
Dirac normal form as “derived” would violate the action-ownership firewall.

The honest remaining branch is to declare the local eta-bound Dirac sector as
foundational low-energy data.  This is analogous to adopting the Path-B color–eta
action as foundational physical data: the declaration advances the effective
action while preserving an explicit provenance label.

The adopted collar action is

\[
S_F^{14.45}
=
\sum_{\epsilon=\pm}
\int d\mu_4\,ds\,J(s)\,
\bar\Psi_\epsilon
\left[
 i\gamma^\mu\nabla_\mu^{\rm total}
 +i\epsilon\Gamma_\perp
 \left(
 \partial_s+\frac12\partial_s\log J+m_\eta
 \right)
\right]
\Psi_\epsilon
+S_H,
\]

with

\[
m_\eta(s)=-\partial_s\log\sin f_\eta(s).
\]

The two opposite collar orientations carry the retained left- and right-handed
zero modes.  The seam bridge is

\[
S_H=-\int d\mu_4
\left[
\bar\Psi_+\,\mathbb Y_fH\Psi_-+\mathrm{h.c.}
\right].
\]

This action is **foundational**, not derived from the bosonic Path-B action.
The canonical unit coefficient is a definition of the normalized Grassmann
field, not an additional measurable coupling.

---

## 2. Exact eta zero-mode pullback

Define

\[
A_\eta
=
\partial_s+\frac12\partial_s\log J+m_\eta.
\]

Then

\[
\boxed{
 u_0(s)=\mathcal N J^{-1/2}(s)\sin f_\eta(s)
}
\]

satisfies

\[
A_\eta u_0=0
\]

identically.  Its normalization is

\[
1
=
\int ds\,J|u_0|^2
=
\mathcal N^2\int ds\,\sin^2f_\eta.
\]

Consequently the four-dimensional kinetic pullback is exactly canonical:

\[
\int ds\,J|u_0|^2\,
\bar\psi i\gamma^\mu\nabla_\mu\psi
=
\bar\psi i\gamma^\mu\nabla_\mu\psi.
\]

For the two oriented sheets, the same normalized normal profile gives

\[
\zeta_{+-}=\int ds\,J u_+^*u_-=1.
\]

Therefore the seam Higgs operator is not multiplied by an arbitrary normal
overlap factor.

For a tangential Kosmann operator,

\[
V_\beta
=-i\left[
\beta^i\nabla_i
+\frac14(D_i\beta_j)\gamma^{ij}
\right],
\]

the normal reduction also has coefficient one:

\[
\langle u_0\chi_t|V_\beta|u_0\chi_s\rangle_{5D}
=
\langle\chi_t|V_\beta|\chi_s\rangle_{4D}.
\]

This closes the normal/radial normalization gate.  It does not calculate the
remaining tangential spinor-harmonic reduced element.

---

## 3. Global parent spin bundle and seam cancellation

The two collar sheets are now declared to be restrictions of one oriented,
time-oriented parent spin manifold with one global spinor bundle.  The seam map
is therefore not an independently chosen unitary matrix.  It is the transition
function induced by the parent spin lift,

\[
\psi_-
=
\rho(\widetilde\Lambda_{cw})\psi_+.
\]

In a common parent coframe this is the identity transition, up to the globally
fixed spin sign and ordinary gauge transformations.

The internal seam Green form is

\[
\mathfrak B
=-i\int_\Sigma
\left[
\psi_+^\dagger\alpha_{n_+}\phi_+
+
\psi_-^\dagger\alpha_{n_-}\phi_-
\right].
\]

Because

\[
n_-=-n_+,
\]

and the fields are restrictions of one global spinor, the two terms cancel.
The glued operator is therefore self-adjoint on the global `H1` domain under the
same regularity assumptions used in the earlier compact-domain theorem.

The residual overall sign or common gauge phase is family central.  It cannot
produce CKM or a relative up/down holonomy.

---

## 4. No-double-counting contract

The adopted local fermion field represents the second-quantized collective and
topological eta-knot sector.  The corresponding collective tangent modes must
not also be integrated as ordinary bosonic Gaussian fluctuations.

Let

\[
\zeta_A=\frac{\partial\eta_*}{\partial q^A},
\qquad
G_{AB}=\langle\zeta_A,\zeta_B\rangle.
\]

Define

\[
P_{\rm coll}v
=
\zeta_A G^{AB}\langle\zeta_B,v\rangle,
\qquad
Q_\eta=I-P_{\rm coll}.
\]

Then

\[
P_{\rm coll}^2=P_{\rm coll},
\qquad
Q_\eta\zeta_A=0.
\]

The measure contract is:

- the fermionic path integral quantizes the retained FR/topological collective
  sector;
- the bosonic one-loop factor uses
  \(\det{}'(Q_\eta H_\eta Q_\eta)\);
- the collective-coordinate/Faddeev–Popov Jacobian is included once.

This prevents the foundational local field from becoming a second independent
ultraviolet copy of the same eta collective modes.

---

## 5. Exact renormalization underdetermination

After the local fermion action is declared, the determinant is mathematically
definable once the compact spectrum is supplied.  However, the physical
coexact Hessian still has the form

\[
\Lambda_L^{\rm ren}
=
c_2^{\rm ren}q_L
+c_4^{\rm ren}q_L^2
+\Pi_L^{\rm nonlocal},
\qquad
q_L=(L-1)(L+3).
\]

For the required channels,

\[
\begin{pmatrix}
\Lambda_2-\Pi_2\\
\Lambda_3-\Pi_3
\end{pmatrix}
=
\begin{pmatrix}
5&25\\
12&144
\end{pmatrix}
\begin{pmatrix}
c_2^{\rm ren}\\
c_4^{\rm ren}
\end{pmatrix}.
\]

The determinant of the channel matrix is

\[
5\cdot144-12\cdot25
=
\boxed{420}\ne0.
\]

Therefore the two local renormalized coefficients independently control the two
critical channels.  For any chosen total pair \((\Lambda_2,\Lambda_3)\),

\[
\boxed{
c_2^{\rm ren}
=
\frac{144(\Lambda_2-\Pi_2)-25(\Lambda_3-\Pi_3)}{420},
}
\]

\[
\boxed{
c_4^{\rm ren}
=
\frac{-12(\Lambda_2-\Pi_2)+5(\Lambda_3-\Pi_3)}{420}.
}
\]

Thus even exact values of the nonlocal fermion sums do not decide whether the
`L=2` channel, the `L=3` channel, both channels, or neither channel crosses
zero.  A microscopic full-preimage regulator or two physical renormalization
conditions are required.

Setting curvature-squared coefficients to zero at an unspecified scale is a
scheme choice, not a BHSM prediction.

---

## 6. Hindsight 20/20

### Validated

- A foundational two-sided eta-bound Dirac action can be written with no new
  continuous localization coefficient.
- The eta normal zero mode gives an exact unit four-dimensional kinetic
  pullback.
- The two-sheet Higgs overlap is exactly one.
- One global parent spin bundle fixes the spinor seam transition and cancels the
  internal Green form.
- The global spin transition is family central.
- The collective projector removes double counting between local fermions and
  bosonic zero modes.
- The `L=2/L=3` local-counterterm map has full rank and determinant 420.

### Invalidated

- Describing the adopted local fermion sector as derived from Path B.
- Treating self-adjoint seam matching as a physical flavor phase.
- Claiming that an exact nonlocal determinant alone predicts the bifurcation.
- Setting the curvature-squared subtraction to zero without declaring a scale
  and renormalization condition.

### Reclassified

- The local Dirac sector is now foundational effective data.
- The normal-mode and spin-glue gates are closed on that foundational branch.
- The determinant bottleneck has moved from existence of the operator to the
  microscopic regulator, tangential spectrum, and renormalized gravitational
  coefficients.

### Open

- normalized compact-cap spinor harmonics selected for every frozen family slot;
- full `L=2,L=3` Kosmann tangential matrix elements;
- complete species and response spectrum;
- full-preimage microscopic regulator or physical renormalization conditions;
- total renormalized zero crossing;
- nonlinear branch, relative-holonomy orientation, CKM and CP;
- absolute scale, masses, couplings and full BHSM completion.

---

## 7. Completion status

Mark III is not reached.  BHSM remains incomplete.  Frozen predictions and
official prediction logic are unchanged.  No physical determinant, `Pi_2`,
`Pi_3`, CKM matrix, CP phase, mass, coupling, radius, or scale is emitted.  The
USB remains untouched.
