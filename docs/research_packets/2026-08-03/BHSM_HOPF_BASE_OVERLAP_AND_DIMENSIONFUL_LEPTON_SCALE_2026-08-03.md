# BHSM Hopf-Base-Normalized Overlap Semigroup and Dimensionful Charged-Lepton Scale

**Date:** 2026-08-03  
**Repository baseline:** BHSM v11.3, PR #217, merge `3e324a05e50b8128d28b84968b4ef3d2b064dd73`  
**Target:** `ACTION_DERIVED_HOPF_BASE_NORMALIZED_OVERLAP_SEMIGROUP_AND_DIMENSIONFUL_LEPTON_SCALE`

---

## 1. Executive result

The BHSM charged-lepton mass operator can be written as

\[
\boxed{
\mathsf M_\ell
=
M_{\rm lift}
\frac{\beta_\ell\tau}{R_\ell}
\exp\!\left(-\frac{\mathcal L_a}{4\pi}\right)
}
\]

on the exact charged-lepton family space, where

\[
M_{\rm lift}=4\pi^2v_{\rm BH},
\qquad
\beta_\ell=\frac{16}{1323},
\qquad
\tau=\frac{1}{4\pi^{3/2}},
\qquad
R_\ell=\operatorname{Tr}P_\ell=3,
\]

and \(\mathcal L_a\) is the positive Berger–Hopf spectral operator.

The three family eigenvalues are

\[
\boxed{
m_f
=
m_{\ell,0}
\exp\left[-\frac{\lambda_{k_f,j_f}(a)}{4\pi}\right],
}
\]

with

\[
\boxed{
m_{\ell,0}
=
\frac{16\sqrt{\pi}}{3969}\,v_{\rm BH}.
}
\]

Using the existing BHSM Planck-to-electroweak scale candidate produces

\[
\boxed{
m_{\rm heavy}=1.758930614523593\ {\rm GeV},
}
\]

\[
\boxed{
m_{\rm middle}=0.1056668260746751\ {\rm GeV},
}
\]

\[
\boxed{
m_{\rm light}=0.0005229143548875558\ {\rm GeV}.
}
\]

No observed charged-lepton mass or charged-lepton mass ratio is used.

---

## 2. Hopf-base action normalization

Let

\[
\pi_H:S^3_a\longrightarrow S^2
\]

be the BHSM Hopf fibration in the unit-base convention

\[
\operatorname{Area}(S^2)=4\pi.
\]

Let \(\mathcal L_a\) be the nonnegative self-adjoint Berger spectral operator
whose eigenfunctions satisfy

\[
\mathcal L_aY_{k,j,m}
=
\lambda_{k,j}(a)Y_{k,j,m}.
\]

The Hopf-base-normalized quadratic action is

\[
\boxed{
\mathcal A_{\rm BH}[\Psi]
=
\frac{1}{\operatorname{Area}(S^2)}
\langle\Psi,\mathcal L_a\Psi\rangle
=
\frac1{4\pi}
\langle\Psi,\mathcal L_a\Psi\rangle.
}
\]

The coefficient is not a family parameter. It is the normalized Haar/base
average of one unit Hopf base.

The associated positive generator is

\[
\overline{\mathcal L}_a
=
\frac{\mathcal L_a}{4\pi}.
\]

By the spectral theorem it generates the contraction semigroup

\[
\boxed{
\mathcal T_a(t)
=
e^{-t\overline{\mathcal L}_a},
\qquad t\ge0.
}
\]

For one normalized boundary-response step,

\[
t=1,
\]

so

\[
\boxed{
\mathcal T_a
=
\exp\left(-\frac{\mathcal L_a}{4\pi}\right).
}
\]

On an exact eigenmode,

\[
\mathcal T_aY_{k,j,m}
=
\exp\left[-\frac{\lambda_{k,j}(a)}{4\pi}\right]
Y_{k,j,m}.
\]

Thus the frozen overlap width

\[
S=\frac1{4\pi}
\]

is the Hopf-base-normalized action coefficient.

---

## 3. Semigroup properties

Because \(\mathcal L_a\ge0\),

\[
\|\mathcal T_a(t)\|\le1.
\]

The exact laws are

\[
\mathcal T_a(0)=I,
\]

\[
\mathcal T_a(t_1)\mathcal T_a(t_2)
=
\mathcal T_a(t_1+t_2),
\]

\[
-\frac{d}{dt}\mathcal T_a(t)
=
\overline{\mathcal L}_a\mathcal T_a(t).
\]

Hence the BHSM overlap response is a genuine positive spectral semigroup, not
a separately fitted family suppression rule.

---

## 4. Compatibility with the attachment seed

The lower attachment response obeys

\[
3\mu^2-2(h_C+K+1)\mu+h_C(K+1)=0.
\]

Its exact inverse is

\[
K
=
\frac{\mu(2h_C-3\mu)}{h_C-2\mu}-1.
\]

Therefore the action generator can also be written directly on the
nondegenerate attachment operator \(H_\ell^{(-)}\):

\[
\mathscr K_{h_C}(H_\ell^{(-)})
=
H_\ell^{(-)}
(2h_CI-3H_\ell^{(-)})
(h_CI-2H_\ell^{(-)})^{-1}
-I.
\]

With the Hopf-charge operator

\[
Q_\ell=\sum_fq_fP_f,
\]

the Berger generator is

\[
\boxed{
\mathcal L_a
=
\mathscr K_{h_C}(H_\ell^{(-)})
+
(a^2-1)Q_\ell^2.
}
\]

Thus the overlap semigroup acts on the action-derived nondegenerate attachment
response without changing the exact family ledger.

---

## 5. Trace-normalized charged source

The action-owned charged suppression kernel has total charged rank

\[
R_{\rm ch}=21
\]

and lepton projector trace

\[
R_\ell=\operatorname{Tr}P_\ell=3.
\]

The charged boundary bridge supplies the total lepton source

\[
\beta_\ell\tau
=
\frac{16}{1323}
\frac1{4\pi^{3/2}}
=
\frac4{1323\pi^{3/2}}.
\]

Trace normalization distributes this source uniformly over the three
lepton-incidence channels:

\[
\boxed{
g_{\ell,0}
=
\frac{\beta_\ell\tau}{R_\ell}
=
\frac4{3969\pi^{3/2}}.
}
\]

This is the unique scalar coefficient obtained from:

1. the existing total lepton boundary source;
2. the exact lepton projector rank;
3. uniform trace normalization.

No extra Yukawa coefficient is inserted.

---

## 6. Dimensionful Hopf lift

The repository's BHSM scale candidate is

\[
v_{\rm BH}
=
2\sqrt2E_P
\exp\left[
-4\pi^2
-\frac{\epsilon_\alpha}{4\pi^2}
\right],
\]

where

\[
\epsilon_\alpha
=
\frac{\alpha_{\rm low}^{-1}}{12\pi^2}-1.
\]

The Hopf lift is

\[
M_{\rm lift}=4\pi^2v_{\rm BH}.
\]

Multiplying the trace-normalized boundary source by the lift gives

\[
m_{\ell,0}
=
M_{\rm lift}g_{\ell,0}.
\]

Therefore

\[
\boxed{
m_{\ell,0}
=
4\pi^2v_{\rm BH}
\frac4{3969\pi^{3/2}}
=
\frac{16\sqrt\pi}{3969}v_{\rm BH}.
}
\]

Substituting \(v_{\rm BH}\),

\[
\boxed{
m_{\ell,0}
=
\frac{32\sqrt{2\pi}}{3969}
E_P
\exp\left[
-4\pi^2
-\frac{\epsilon_\alpha}{4\pi^2}
\right].
}
\]

This is the common dimensionful multiplier for the charged-lepton family
operator.

---

## 7. Complete charged-lepton mass operator

The final operator is

\[
\boxed{
\mathsf M_\ell
=
\frac{16\sqrt\pi}{3969}
v_{\rm BH}
\exp\left(-\frac{\mathcal L_a}{4\pi}\right).
}
\]

In the exact family-projector basis,

\[
\boxed{
\mathsf M_\ell
=
\sum_{f=0}^{2}
m_fP_f,
}
\]

where

\[
m_f
=
\frac{16\sqrt\pi}{3969}
v_{\rm BH}
\exp\left[
-\frac{
K_f+(a^2-1)q_f^2
}{4\pi}
\right].
\]

The exact charged-lepton modes are

\[
(K_0,q_0)=(0,0),
\]

\[
(K_1,q_1)=(35,1),
\]

\[
(K_2,q_2)=(99,3).
\]

---

## 8. Numerical values without charged-lepton inputs

Use

\[
E_P=1.220890\times10^{19}\ {\rm GeV},
\]

\[
\alpha_{\rm low}^{-1}=137.035999084.
\]

Then

\[
a=1.1570541357334329,
\]

\[
v_{\rm BH}=246.16986520825247\ {\rm GeV},
\]

\[
M_{\rm lift}=9718.396740299771\ {\rm GeV},
\]

\[
g_{\ell,0}
=
0.00018098979302107993,
\]

and

\[
m_{\ell,0}=1.7589306145235935\ {\rm GeV}.
\]

The family results are

| Family role | \((k,j)\) | \(q\) | \(\lambda_{k,j}\) | overlap | mass |
|---|---:|---:|---:|---:|---:|
| heavy | \((0,0)\) | 0 | \(0\) | \(1\) | \(1.7589306145235935\) GeV |
| middle | \((5,2)\) | 1 | \(35.33877427301784\) | \(0.060074470932609775\) | \(0.10566682607467506\) GeV |
| light | \((9,3)\) | 3 | \(102.04896845716057\) | \(0.0002972910645649244\) | \(0.0005229143548875558\) GeV |

No empirical charged-lepton comparison is used to choose or modify these
values.

---

## 9. Independence from the representative core stiffness

The attachment response values \(\mu_f\) depend on \(h_C\), but the exact
inverse reconstructs

\[
K_f
\]

identically. Therefore the final Berger costs and masses are independent of
the representative positive \(h_C\), provided:

1. the same lower branch generates and reconstructs \(\mu_f\);
2. \(0<\mu_f<h_C/2\);
3. the fixed family octave ledger is preserved.

This prevents the core-stiffness representative from becoming a hidden mass
fit.

---

## 10. Claim classification

### DERIVED

- Hopf-base-normalized quadratic generator:
  \[
  \overline{\mathcal L}_a=\mathcal L_a/(4\pi).
  \]
- Positive overlap semigroup:
  \[
  e^{-\mathcal L_a/(4\pi)}.
  \]
- Trace-normalized lepton source:
  \[
  \beta_\ell\tau/3.
  \]
- Closed dimensionful mass-operator formula.
- Three numerical charged-lepton mass candidates without lepton mass inputs.

### CONDITIONAL INPUTS

- Unit-radius Hopf-base convention:
  \[
  \operatorname{Area}(S^2)=4\pi.
  \]
- Alpha-anchored Berger squashing.
- Existing Planck-to-electroweak scale candidate.
- Existing author-selected profile Hessian/radius package.
- Interpretation of \(M_{\rm lift}\) as the dimensionful coefficient of the
  charged boundary response after reduction.

### NOT USED

- observed electron mass;
- observed muon mass;
- observed tau mass;
- observed charged-lepton ratios;
- post-comparison retuning;
- fitted family Yukawa coefficients.

---

## 11. Remaining unconditional action gate

The repository currently classifies the Planck-to-electroweak expression as a
scale screen and the profile radius/Hessian identifications as conditional
author theorems.

Therefore the absolute triplet is strongest as

\[
\boxed{
\texttt{
DERIVED\_CONDITIONAL\_DIMENSIONFUL\_CHARGED\_LEPTON\_PREDICTION
}
}
\]

rather than an unconditional complete-parent-action theorem.

The exact remaining action object is

\[
\boxed{
\texttt{
COMPLETE\_PARENT\_ACTION\_OWNERSHIP\_OF\_PLANCK\_TO\_EW\_HOPF\_LIFT\_AND\_TRACE\_NORMALIZED\_CHARGED\_MASS\_INSERTION
}
}
\]

---

## 12. Primary verdicts

\[
\boxed{
\texttt{
BHSM\_HOPF\_BASE\_NORMALIZED\_OVERLAP\_SEMIGROUP\_DERIVED\_CONDITIONALLY
}
}
\]

\[
\boxed{
\texttt{
BHSM\_DIMENSIONFUL\_CHARGED\_LEPTON\_SCALE\_CONSTRUCTED\_WITHOUT\_LEPTON\_MASS\_INPUTS
}
}
\]

\[
\boxed{
\texttt{
BHSM\_ABSOLUTE\_CHARGED\_LEPTON\_TRIPLET\_PREDICTED\_CONDITIONALLY
}
}
