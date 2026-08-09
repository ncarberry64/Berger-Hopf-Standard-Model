# BHSM Attachment-to-Berger Overlap Hierarchy Bridge

**Date:** 2026-08-03  
**Scope:** dimensionless charged-lepton restoring hierarchy  
**Constraint:** no measured charged-lepton masses used as derivation inputs

---

## 1. Inputs already present in BHSM

The charged-lepton family ledger is

\[
P_0:(k,j)=(0,0),\qquad
P_1:(k,j)=(5,2),\qquad
P_2:(k,j)=(9,3).
\]

Define

\[
q=k-2j,
\qquad
K=k(k+2).
\]

The three exact charged-lepton labels are therefore

\[
(K_0,q_0)=(0,0),
\qquad
(K_1,q_1)=(35,1),
\qquad
(K_2,q_2)=(99,3).
\]

The frozen BHSM geometric constants are

\[
a=\frac{\alpha_{\rm low}^{-1}}{12\pi^2},
\qquad
S=\frac1{4\pi}.
\]

No observed charged-lepton mass occurs in these definitions.

---

## 2. Nondegenerate attachment seed

For positive core stiffness \(h_C\), the selected lower generalized
attachment root is

\[
\mu_-(K;h_C)
=
\frac{
h_C+K+1-
\sqrt{(K+1)^2-h_C(K+1)+h_C^2}
}{3}.
\]

It obeys

\[
3\mu^2-2(h_C+K+1)\mu+h_C(K+1)=0.
\]

For \(K\ge 0\) and \(h_C>0\),

\[
0<\mu_-(K;h_C)<\frac{h_C}{2},
\]

so the branch is positive, nondegenerate, and lies in an invertible domain.

---

## 3. Exact inverse of the attachment branch

Rearrange the characteristic equation:

\[
(K+1)(h_C-2\mu)=\mu(2h_C-3\mu).
\]

Therefore

\[
\boxed{
K
=
\mathscr K_{h_C}(\mu)
=
\frac{\mu(2h_C-3\mu)}{h_C-2\mu}-1.
}
\]

This is not a fit. It is the exact inverse of the selected KKT branch.

Consequently, the nondegenerate response eigenvalue \(\mu_f\) contains the
family octave \(K_f\) without requiring a measured mass.

---

## 4. Berger spectral operator

The frozen Berger scalar eigenvalue is

\[
\lambda_{k,j}(a)
=
a^2(k-2j)^2
+
2\left((2j+1)k-2j^2\right).
\]

Using \(q=k-2j\) and \(K=k(k+2)\),

\[
2\left((2j+1)k-2j^2\right)=K-q^2.
\]

Hence

\[
\boxed{
\lambda_{k,j}(a)
=
K+(a^2-1)q^2.
}
\]

Substitute the exact attachment inverse:

\[
\boxed{
\lambda_{\rm att}(\mu,q;h_C,a)
=
\frac{\mu(2h_C-3\mu)}{h_C-2\mu}
-1
+
(a^2-1)q^2.
}
\]

Thus the complete geometric spectral cost can be reconstructed directly from
the nondegenerate attachment seed and the exact Hopf charge.

---

## 5. Nonlinear restoring map

The existing BHSM overlap law is the spectral exponential

\[
\mathcal Z=e^{-S\lambda}.
\]

The attachment-to-overlap restoring map is therefore

\[
\boxed{
\mathcal Z(\mu,q)
=
\exp\left[
-S\left(
\frac{\mu(2h_C-3\mu)}{h_C-2\mu}
-1
+
(a^2-1)q^2
\right)
\right].
}
\]

For a reference family \(0\), the dimensionless hierarchy is

\[
\boxed{
R_f
=
\frac{\mathcal Z_f}{\mathcal Z_0}
=
\exp[-S(\lambda_f-\lambda_0)].
}
\]

For the charged-lepton heavy mode, \(\lambda_0=0\), so \(R_f=\mathcal Z_f\).

This map explains why the raw attachment stiffness splitting may be modest
while the final restoring hierarchy is large: the attachment response is first
decoded into the full boundary spectral cost, and the overlap semigroup then
acts exponentially on that cost.

---

## 6. Operator-level form

Let

\[
H_{\ell}^{(-)}
=
\sum_{f=0}^{2}\mu_fP_f
\]

be the nondegenerate attachment-response operator, and let

\[
Q_\ell=\sum_{f=0}^{2}q_fP_f.
\]

Because the exact family projectors commute, define the inverse attachment
operator by functional calculus:

\[
\boxed{
\mathscr K_{h_C}\!\left(H_{\ell}^{(-)}\right)
=
H_{\ell}^{(-)}
\left(2h_CI-3H_{\ell}^{(-)}\right)
\left(h_CI-2H_{\ell}^{(-)}\right)^{-1}
-I.
}
\]

The Berger restoring operator is

\[
\boxed{
L_{\ell}^{\rm BH}
=
\mathscr K_{h_C}\!\left(H_{\ell}^{(-)}\right)
+
(a^2-1)Q_\ell^2.
}
\]

The full dimensionless charged-lepton hierarchy operator is

\[
\boxed{
\mathcal R_\ell
=
\exp\left(-S L_{\ell}^{\rm BH}\right).
}
\]

Its three exact eigenvalues are the heavy, middle, and light restoring
coefficients.

---

## 7. Numerical evaluation

Use only:

\[
\alpha_{\rm low}^{-1}=137.035999084,
\qquad
a=\frac{137.035999084}{12\pi^2},
\qquad
S=\frac1{4\pi},
\]

the family ledger, and the selected attachment branch.

The Berger spectral costs are

\[
\lambda_0=0,
\]

\[
\lambda_1
=
35+(a^2-1)
=
35.33877427301784,
\]

\[
\lambda_2
=
99+9(a^2-1)
=
102.04896845716057.
\]

Therefore

\[
\boxed{
R_{\rm heavy}=1,
}
\]

\[
\boxed{
R_{\rm middle}
=
e^{-S\lambda_1}
=
0.06007447093260976,
}
\]

\[
\boxed{
R_{\rm light}
=
e^{-S\lambda_2}
=
0.00029729106456492414.
}
\]

The resulting dimensionless charged-lepton restoring hierarchy is

\[
\boxed{
1:
0.06007447093260976:
0.00029729106456492414.
}
\]

These values exactly reproduce the frozen BHSM charged-lepton hierarchy under
ordinary binary floating-point evaluation.

---

## 8. Input firewall

The calculation uses:

- the fixed charged-lepton mode ledger;
- the exact KKT attachment characteristic;
- the selected lower positive branch;
- the exact Hopf charge \(q=k-2j\);
- the frozen alpha-anchored Berger anisotropy;
- the frozen overlap width \(S=1/(4\pi)\).

It does **not** use:

- the electron mass;
- the muon mass;
- the tau mass;
- either observed charged-lepton mass ratio;
- a fitted exponent;
- a fitted family coefficient;
- a new mediator;
- a post-freeze adjustment of \(a\), \(S\), or the modes.

The observed masses may be used later only as an external comparison layer.

---

## 9. What is now closed

### VALIDATED

1. The positive nondegenerate attachment seed can be converted exactly back
   into the family octave.
2. The Berger eigenvalue can be written as an exact function of the attachment
   response and Hopf charge.
3. The frozen overlap exponential converts the reconstructed spectral costs
   into the complete dimensionless charged-lepton hierarchy.
4. The middle and light ratios are reproduced with no charged-lepton mass
   inputs.
5. The construction is diagonal in the exact family-projector basis.
6. No new continuous coefficient is introduced.

### REFINED

1. The raw \(\mu_f\) values are not themselves the final mass ratios.
2. The hierarchy is not produced by exponentiating the small differences
   \(\mu_f-\mu_0\) directly.
3. The correct nonlinear map first applies the exact inverse KKT function,
   restores the Berger spectral cost, and only then applies the overlap
   exponential.
4. The new attachment seed is compatible with and supplies an action-side
   encoding of the frozen spectral hierarchy; it does not replace the exact
   family mode ledger.

### OPEN

1. An action derivation, rather than author-axiom selection, of

   \[
   S=\frac1{4\pi}.
   \]

2. A complete action derivation of the alpha-anchored squashing parameter

   \[
   a=\frac{\alpha_{\rm low}^{-1}}{12\pi^2}.
   \]

3. The absolute charged-lepton mass scale. The present result fixes only

   \[
   m_e:m_\mu:m_\tau
   \]

   up to one common dimensionful multiplier.

4. A proof that the overlap semigroup is the unique physical restoring map
   selected by the complete local boundary action.

---

## 10. Verdicts

\[
\boxed{
\texttt{
BHSM\_NONDEGENERATE\_ATTACHMENT\_SEED\_TO\_BERGER\_SPECTRAL\_COST\_MAP\_DERIVED
}
}
\]

\[
\boxed{
\texttt{
BHSM\_FULL\_CHARGED\_LEPTON\_DIMENSIONLESS\_RESTORING\_HIERARCHY\_RECOVERED\_WITHOUT\_MASS\_INPUTS
}
}
\]

Claim qualifier:

\[
\boxed{
\texttt{
CONDITIONAL\_ON\_FROZEN\_BERGER\_ANISOTROPY\_AND\_OVERLAP\_WIDTH
}
}
\]

Absolute-scale verdict:

\[
\boxed{
\texttt{
BHSM\_ABSOLUTE\_CHARGED\_LEPTON\_MASS\_SCALE\_REMAINS\_OPEN
}
}
\]

Exact next object:

\[
\boxed{
\texttt{
ACTION\_DERIVED\_HOPF\_BASE\_NORMALIZED\_OVERLAP\_SEMIGROUP\_AND\_DIMENSIONFUL\_LEPTON\_SCALE
}
}
\]
