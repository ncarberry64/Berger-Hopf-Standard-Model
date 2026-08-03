# BHSM Final Manual Parent-Action Completion:
# Planck-to-EW Hopf Lift and Trace-Normalized Charged-Lepton Mass Insertion

**Date:** 2026-08-03  
**Repository baseline:** BHSM v11.3, PR #217, merge `3e324a05e50b8128d28b84968b4ef3d2b064dd73`  
**Target:** `COMPLETE_PARENT_ACTION_OWNERSHIP_OF_PLANCK_TO_EW_HOPF_LIFT_AND_TRACE_NORMALIZED_CHARGED_MASS_INSERTION`

---

## 1. Completion status

The missing action term is supplied on the intrinsic \(M_4\) stratum of the
v7.1 stratified master action. No false claim is made that the Standard Model
fermions or Higgs descend from the \(M_8\) metric.

The completion replaces the independent charged-lepton Yukawa matrix by one
BHSM geometric operator and replaces the unspecified Higgs vacuum target by
one positive gauge-invariant BHSM potential.

The result is an explicit variational action. It introduces:

- no new dynamical field;
- no new mediator;
- no family-fitted coefficient;
- no charged-lepton mass input;
- no separate post-EWSB mass term;
- no duplicate Hopf-lift term.

It uses the one universal dimensionful calibration already licensed by the
v7.1 coefficient ledger.

---

## 2. Authoritative stratified action

Write the existing correspondence action schematically as

\[
S_{\rm BHSM}^{\rm strat}
=
S_8
+\sum_{\epsilon=\pm}(S_{5,\epsilon}+S_{{\rm GHY},\epsilon})
+S_{4,\rm loc}
+S_{\rm compatibility}^{(11.3)}.
\]

The reciprocal compatibility term remains

\[
S_{\rm attach}
=
\int_{M_5}d\mu_5
\left\langle
\Lambda_{85},
\upsilon^{-1/2}I_W-\upsilon^{1/2}I_C
\right\rangle.
\]

The final completion changes only the intrinsic \(M_4\) Higgs/lepton block.
All other action strata and compatibility equations remain intact.

---

## 3. Existing BHSM invariants

Use the already selected profile data

\[
r_H^2=\frac1{4\pi},
\]

\[
\kappa_H=64\pi^5,
\]

\[
\tau=\frac1{4\pi^{3/2}}.
\]

They obey

\[
\boxed{\kappa_H\tau^2=4\pi^2.}
\]

Let \(a>0\) be the frozen Berger squashing parameter. Define the dimensionless
Hopf/profile action cost

\[
\boxed{
\mathcal I_{\rm BH}
=
\kappa_H\tau^2
+
\frac{a-1}{\kappa_H\tau^2}.
}
\]

Therefore

\[
\mathcal I_{\rm BH}
=
4\pi^2+\frac{a-1}{4\pi^2}.
\]

Let the one common length calibration be \(\ell_\star\), and define

\[
E_\star=\ell_\star^{-1}.
\]

In the unreduced Planck convention this may be tied to the intrinsic
Einstein coefficient by

\[
C_\partial=\frac{E_\star^2}{16\pi}.
\]

No lepton datum enters this calibration.

---

## 4. Action-owned Planck-to-EW Higgs potential

Define

\[
\nu_{\rm BH}^2
=
4E_\star^2e^{-2\mathcal I_{\rm BH}}.
\]

Replace the unspecified scalar vacuum target by

\[
\boxed{
V_{\rm BH}(H)
=
\lambda_H
\left(
H^\dagger H-\nu_{\rm BH}^2
\right)^2,
\qquad
\lambda_H>0.
}
\]

This is local, gauge invariant, real, bounded below, and dimension four.

For the vacuum convention

\[
H_{\rm vac}
=
\frac1{\sqrt2}
\begin{pmatrix}
0\\ v_{\rm BH}
\end{pmatrix},
\]

the Higgs equation gives

\[
\frac{v_{\rm BH}^2}{2}
=
\nu_{\rm BH}^2.
\]

Hence

\[
\boxed{
v_{\rm BH}
=
2\sqrt2E_\star
e^{-\mathcal I_{\rm BH}}.
}
\]

Explicitly,

\[
\boxed{
v_{\rm BH}
=
2\sqrt2E_\star
\exp\left[
-4\pi^2-\frac{a-1}{4\pi^2}
\right].
}
\]

The former external Planck-to-electroweak formula is now the stationary point
of a declared action term.

The radial Higgs Hessian is

\[
m_{h,\rm radial}^2=2\lambda_Hv_{\rm BH}^2>0.
\]

The value of \(\lambda_H\) affects the radial Higgs stiffness but not the
selected vacuum scale.

---

## 5. Exact charged-lepton spectral operator

Let \(P_0,P_1,P_2\) be the exact family projectors and use the fixed
charged-lepton ledger

\[
(k_0,j_0)=(0,0),
\qquad
(k_1,j_1)=(5,2),
\qquad
(k_2,j_2)=(9,3).
\]

Define

\[
q_f=k_f-2j_f,
\]

\[
K_f=k_f(k_f+2),
\]

\[
\lambda_f(a)
=
K_f+(a^2-1)q_f^2.
\]

The finite family spectral operator is

\[
\boxed{
\mathcal L_{a,\ell}
=
\sum_{f=0}^{2}\lambda_f(a)P_f.
}
\]

It is Hermitian and nonnegative.

The Hopf-base/profile-normalized overlap operator is

\[
\boxed{
\mathcal T_\ell
=
\exp(-r_H^2\mathcal L_{a,\ell})
=
\exp\left(-\frac{\mathcal L_{a,\ell}}{4\pi}\right).
}
\]

Because this operator acts only on the finite family space, it is local in
four-dimensional spacetime.

---

## 6. Trace-normalized charged-lepton source

Use the existing charged boundary source

\[
\beta_\ell=\frac{16}{1323}
\]

and the lepton incidence trace

\[
R_\ell=\operatorname{Tr}P_\ell=3.
\]

The total boundary source is \(\beta_\ell\tau\). Uniform trace normalization
gives the source per family channel:

\[
\boxed{
g_{\ell,0}
=
\frac{\beta_\ell\tau}{R_\ell}
=
\frac4{3969\pi^{3/2}}.
}
\]

This coefficient is used exactly once.

---

## 7. Action-owned charged-lepton Yukawa operator

Define the dimensionless Yukawa operator

\[
\boxed{
\mathbb Y_\ell^{\rm BH}
=
\sqrt2\,
\kappa_H\tau^2\,
\frac{\beta_\ell\tau}{R_\ell}\,
\mathcal T_\ell.
}
\]

Using the profile identity,

\[
\mathbb Y_\ell^{\rm BH}
=
\sqrt2\,(4\pi^2)
\frac4{3969\pi^{3/2}}
\exp\left(-\frac{\mathcal L_{a,\ell}}{4\pi}\right).
\]

Therefore

\[
\boxed{
\mathbb Y_\ell^{\rm BH}
=
\frac{16\sqrt{2\pi}}{3969}
\exp\left(-\frac{\mathcal L_{a,\ell}}{4\pi}\right).
}
\]

The completed intrinsic \(M_4\) block is

\[
\boxed{
\begin{aligned}
S_{4,\ell H}^{\rm BH}
=
\int_{M_4}d\mu_4\Big[
&|D_\mu H|^2
-
V_{\rm BH}(H)
+
i\bar L_L\gamma^\mu D_\mu L_L
+
i\bar e_R\gamma^\mu D_\mu e_R
\\
&-
\big(
\bar L_L\mathbb Y_\ell^{\rm BH}He_R
+\mathrm{h.c.}
\big)
\Big].
\end{aligned}
}
\]

The operator acts in family space and commutes with the
\(SU(2)_L\times U(1)_Y\) gauge representation. The standard Yukawa contraction
is therefore gauge invariant.

---

## 8. Variational equations

Variation with respect to \(\bar L_L\) gives

\[
i\gamma^\mu D_\mu L_L
-
\mathbb Y_\ell^{\rm BH}He_R
=
0.
\]

Variation with respect to \(\bar e_R\) gives

\[
i\gamma^\mu D_\mu e_R
-
(\mathbb Y_\ell^{\rm BH})^\dagger H^\dagger L_L
=
0.
\]

Variation with respect to \(H^\dagger\) gives

\[
-D_\mu D^\mu H
-
2\lambda_H
(H^\dagger H-\nu_{\rm BH}^2)H
-
\bar e_R(\mathbb Y_\ell^{\rm BH})^\dagger L_L
=
0,
\]

up to the repository's overall Euler-Lagrange sign convention.

At the fermion-free vacuum, this reduces to

\[
H^\dagger H=\nu_{\rm BH}^2.
\]

Thus both the electroweak saddle and the charged-lepton source come from the
same intrinsic action block.

---

## 9. Post-symmetry-breaking mass operator

Insert

\[
H=
\frac1{\sqrt2}
\begin{pmatrix}
0\\ v_{\rm BH}+h
\end{pmatrix}.
\]

The charged-lepton mass operator is

\[
\mathbb M_\ell^{\rm BH}
=
\frac{v_{\rm BH}}{\sqrt2}
\mathbb Y_\ell^{\rm BH}.
\]

Therefore

\[
\boxed{
\mathbb M_\ell^{\rm BH}
=
v_{\rm BH}
\kappa_H\tau^2
\frac{\beta_\ell\tau}{R_\ell}
\exp\left(-\frac{\mathcal L_{a,\ell}}{4\pi}\right).
}
\]

Since

\[
\kappa_H\tau^2=4\pi^2,
\]

\[
\boxed{
\mathbb M_\ell^{\rm BH}
=
4\pi^2v_{\rm BH}
\frac{\beta_\ell\tau}{3}
\exp\left(-\frac{\mathcal L_{a,\ell}}{4\pi}\right).
}
\]

This recovers the Hopf-lift expression

\[
M_{\rm lift}=4\pi^2v_{\rm BH}
\]

as an identity derived from profile action coefficients, not as a second
independent mass term.

The common heavy-family scale is

\[
\boxed{
m_{\ell,0}
=
\frac{16\sqrt\pi}{3969}v_{\rm BH}.
}
\]

---

## 10. Full absolute mass formula

For family \(f\),

\[
\boxed{
m_f
=
\frac{16\sqrt\pi}{3969}
v_{\rm BH}
\exp\left[
-\frac{
K_f+(a^2-1)q_f^2
}{4\pi}
\right].
}
\]

Substituting the action-owned Higgs saddle gives

\[
\boxed{
m_f
=
\frac{32\sqrt{2\pi}}{3969}
E_\star
\exp\left[
-\mathcal I_{\rm BH}
-\frac{
K_f+(a^2-1)q_f^2
}{4\pi}
\right].
}
\]

Every family dependence is discrete and projector owned.

---

## 11. Numerical conditional prediction

Use the one universal calibration

\[
E_\star=1.220890\times10^{19}\ {\rm GeV}
\]

and the frozen Berger value

\[
a=\frac{137.035999084}{12\pi^2}.
\]

Then

\[
v_{\rm BH}
=
246.16986520825247\ {\rm GeV}.
\]

The action eigenvalues are:

\[
\boxed{
m_{\tau\text{-slot}}
=
1.7589306145235935\ {\rm GeV},
}
\]

\[
\boxed{
m_{\mu\text{-slot}}
=
0.10566682607467506\ {\rm GeV},
}
\]

\[
\boxed{
m_{e\text{-slot}}
=
0.0005229143548875558\ {\rm GeV}.
}
\]

The naming of the sorted heavy, middle, and light slots as
\(\tau,\mu,e\) follows the frozen charged-lepton ledger.

---

## 12. No-double-counting ledger

### Removed

The independent charged-lepton matrix \(Y_e\) is removed from the completed
BHSM branch.

### Retained

- \(Y_u\) and \(Y_d\) remain separate until their own action closures.
- The reciprocal \(\Lambda_{85}\) attachment remains unchanged.
- The Higgs kinetic term is unchanged.
- The gauge and fermion kinetic terms are unchanged.
- The positive scalar quartic coefficient \(\lambda_H\) remains the radial
  stiffness input.
- The one universal scale \(\ell_\star\) remains the sole dimensionful
  calibration.

### Used exactly once

- \(\beta_\ell\tau\): charged boundary source;
- \(R_\ell=3\): trace normalization;
- \(\kappa_H\tau^2\): Hopf/profile lift;
- \(r_H^2\): overlap-semigroup time;
- \(\mathcal L_{a,\ell}\): family spectral generator;
- \(E_\star\): universal scale.

No standalone mass term is added after symmetry breaking.

---

## 13. Validation gates

The completion passes:

1. **Reality:** the Yukawa term includes its Hermitian conjugate.
2. **Gauge invariance:** the standard \(\bar L_LHe_R\) representation
   contraction is unchanged.
3. **Mass dimension:** \(\mathbb Y_\ell^{\rm BH}\) is dimensionless.
4. **Family covariance:** the operator is a function of exact family
   projectors.
5. **Positivity:** every exponential eigenvalue is positive.
6. **Vacuum stability:** \(\lambda_H>0\) gives a positive radial Hessian.
7. **No tachyonic lepton stiffness:** all three mass eigenvalues are positive.
8. **No measured lepton input:** no charged-lepton mass or ratio occurs in the
   action.
9. **No duplicate scale term:** \(M_{\rm lift}\) is an identity, not an
   additional coefficient.
10. **Frozen hierarchy preservation:** the dimensionless ratios remain
    unchanged.
11. **Attachment preservation:** the v11.3 reciprocal matcher is not modified.
12. **No new field or mediator:** the completion uses only \(H,L_L,e_R\) and
    existing finite family operators.

---

## 14. Hindsight 20/20 classification

### VALIDATED

- The Planck-to-EW scale law can be owned by a positive gauge-invariant Higgs
  potential.
- The Hopf lift is exactly \(\kappa_H\tau^2v_{\rm BH}=4\pi^2v_{\rm BH}\).
- The trace-normalized charged source defines a dimensionless Yukawa operator.
- The complete absolute charged-lepton triplet follows by standard Higgs
  symmetry breaking.
- No charged-lepton data are needed.
- The action is variationally complete on the intrinsic \(M_4\) stratum.

### REFINED

- The correct parent architecture is stratified action ownership, not a false
  claim that \(H\) and the fermions descend from the \(M_8\) metric.
- The one universal Planck calibration is an action/unit input, not a lepton
  fit.
- The completion fixes the charged-lepton Yukawa operator but does not yet fix
  the quark Yukawa operators.
- The numerical triplet is conditional on the frozen \(a\), profile
  normalization, and universal Planck calibration.

### OPEN BEYOND THIS STEP

- A uniqueness theorem proving that no other gauge-invariant scalar potential
  realizes the same BHSM axioms.
- An upstream \(S_8\) derivation of the intrinsic \(M_4\) Higgs potential,
  which is not required by the stratified ownership architecture.
- Independent action closures for \(Y_u\), \(Y_d\), and the absolute neutrino
  scale.
- External experimental comparison and RG transport remain separate.

---

## 15. Final verdict

\[
\boxed{
\texttt{
BHSM\_COMPLETE\_PARENT\_ACTION\_OWNERSHIP\_OF\_PLANCK\_TO\_EW\_HOPF\_LIFT\_AND\_TRACE\_NORMALIZED\_CHARGED\_LEPTON\_MASS\_INSERTION\_CLOSED\_CONDITIONALLY
}
}
\]

\[
\boxed{
\texttt{
BHSM\_ABSOLUTE\_CHARGED\_LEPTON\_TRIPLET\_ACTION\_OWNED\_WITHOUT\_LEPTON\_MASS\_INPUTS
}
}
\]

The former missing term is no longer absent. The only remaining question for
this sector is uniqueness/upstream provenance, not action ownership or
variational completeness.
