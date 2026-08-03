# BHSM Minimal-Class Uniqueness and Stratified-Provenance Theorem

**Date:** 2026-08-03  
**Repository baseline:** BHSM v11.3, PR #217, merge `3e324a05e50b8128d28b84968b4ef3d2b064dd73`  
**Input:** the manually completed intrinsic \(M_4\) Higgs–charged-lepton action  
**Target:** determine uniqueness and upstream provenance

---

## 1. Result

The completed charged-lepton action is unique within the following declared
class:

1. intrinsic \(M_4\) ownership of \(H,L_L,e_R\);
2. four-dimensional locality;
3. Standard Model gauge invariance;
4. operators of canonical dimension at most four;
5. one Higgs doublet;
6. exact frozen rank-three family projector module;
7. one nonnegative Berger family generator;
8. a strongly continuous positive overlap semigroup;
9. uniform trace normalization of the total lepton boundary source;
10. one profile/Hopf lift and one universal dimensionful calibration;
11. no extra family coefficient, fitted matrix, field, or mediator.

Within that class:

\[
\boxed{
V_{\rm BH}(H)
=
\lambda_H
\left(H^\dagger H-\nu_{\rm BH}^2\right)^2
}
\]

is the unique renormalizable one-doublet potential with the selected vacuum
and zero vacuum energy, up to the positive radial stiffness \(\lambda_H\).

The overlap operator

\[
\boxed{
\mathcal T_\ell(t)
=
\exp\left[-t\,r_H^2\mathcal L_{a,\ell}\right]
}
\]

is the unique strongly continuous semigroup with generator
\(-r_H^2\mathcal L_{a,\ell}\).

The trace-normalized Yukawa operator

\[
\boxed{
\mathbb Y_\ell^{\rm BH}
=
\sqrt2\,
\kappa_H\tau^2
\frac{\beta_\ell\tau}{3}
\exp\left(-r_H^2\mathcal L_{a,\ell}\right)
}
\]

is the unique minimal operator satisfying the declared source, lift, family,
and no-extra-coefficient rules.

An \(S_8\) derivation of this term is not an open calculation inside the
current architecture. It is excluded because the stratified action declares
\(H,L_L,e_R\) to be intrinsic boundary-localized fundamental fields, with no
map from \(S_8\) or \(S_5\). Their equations therefore arise exclusively from
the \(M_4\) action.

---

## 2. Exact ownership theorem

The authoritative stratified action has the form

\[
S_{\rm strat}
=
S_8[G,\chi,\sigma]
+
S_5[g_\epsilon,\sigma_5]
+
S_{4,\rm loc}[h,A_{\rm SM},\Psi,H]
+
S_{\rm compatibility}.
\]

The current field-transport ledger states

\[
A_{\rm SM},\Psi,H:
\quad
\text{boundary-localized fundamental fields on }M_4,
\]

with no \(M_8\to M_4\) field map.

Consequently,

\[
\frac{\delta S_8}{\delta H}
=
\frac{\delta S_5}{\delta H}
=
\frac{\delta S_{\rm compatibility}}{\delta H}
=0,
\]

and likewise

\[
\frac{\delta S_8}{\delta L_L}
=
\frac{\delta S_5}{\delta L_L}
=
\frac{\delta S_{\rm compatibility}}{\delta L_L}
=0,
\]

\[
\frac{\delta S_8}{\delta e_R}
=
\frac{\delta S_5}{\delta e_R}
=
\frac{\delta S_{\rm compatibility}}{\delta e_R}
=0.
\]

Therefore

\[
\boxed{
\frac{\delta S_{\rm strat}}{\delta(H,L_L,e_R)}
=
\frac{\delta S_{4,\rm loc}}{\delta(H,L_L,e_R)}.
}
\]

This proves exact intrinsic \(M_4\) ownership.

A claimed \(S_8\) derivation would require at least one of:

- a new bulk Higgs field;
- a new bulk fermion/chiral carrier;
- a nonlocal boundary functional of \(S_8\);
- a new reduction map carrying such fields;
- a reclassification of \(H,\Psi\) away from boundary-localized fundamental
  status.

Each option changes the declared theory architecture. It is not a missing
calculation within v11.3.

---

## 3. Minimal renormalizable Higgs-potential uniqueness

For one Standard Model Higgs doublet, define

\[
X=H^\dagger H.
\]

The most general local gauge-invariant potential of canonical dimension at
most four is

\[
V(X)=c_0+c_1X+c_2X^2.
\]

Require:

1. \(c_2=\lambda_H>0\);
2. the selected minimum is \(X=\nu_{\rm BH}^2\);
3. the vacuum energy in this intrinsic block is normalized to zero.

Stationarity gives

\[
V'(\nu_{\rm BH}^2)
=
c_1+2c_2\nu_{\rm BH}^2
=0,
\]

so

\[
c_1=-2\lambda_H\nu_{\rm BH}^2.
\]

Zero vacuum energy gives

\[
c_0=\lambda_H\nu_{\rm BH}^4.
\]

Therefore

\[
\boxed{
V(X)
=
\lambda_H(X-\nu_{\rm BH}^2)^2.
}
\]

There is no second renormalizable gauge-invariant polynomial with the same
conditions. The remaining \(\lambda_H>0\) controls radial stiffness, not the
vacuum location.

With

\[
\nu_{\rm BH}^2=4E_\star^2e^{-2\mathcal I_{\rm BH}},
\]

the Higgs saddle is

\[
v_{\rm BH}=2\sqrt2E_\star e^{-\mathcal I_{\rm BH}}.
\]

---

## 4. Overlap-semigroup uniqueness

Let \(\mathcal F_\ell\cong\mathbb C^3\) be the exact charged-lepton family
module and let

\[
\mathcal L_{a,\ell}
=
\sum_{f=0}^{2}\lambda_fP_f
\]

be the fixed nonnegative Hermitian Berger generator.

Assume \(\mathcal T(t)\) is a strongly continuous family satisfying

\[
\mathcal T(0)=I,
\]

\[
\mathcal T(t+s)=\mathcal T(t)\mathcal T(s),
\]

and

\[
\left.\frac{d\mathcal T}{dt}\right|_{t=0}
=
-r_H^2\mathcal L_{a,\ell}.
\]

On each rank-one eigenspace \(P_f\),

\[
\mathcal T(t)P_f=t_f(t)P_f.
\]

The semigroup equation becomes

\[
t_f(t+s)=t_f(t)t_f(s),
\qquad
t_f(0)=1,
\]

and the generator condition gives

\[
t_f'(0)=-r_H^2\lambda_f.
\]

Strong continuity yields the unique solution

\[
t_f(t)=e^{-tr_H^2\lambda_f}.
\]

Thus

\[
\boxed{
\mathcal T(t)
=
e^{-tr_H^2\mathcal L_{a,\ell}}.
}
\]

At one normalized response step,

\[
\boxed{
\mathcal T_\ell
=
e^{-r_H^2\mathcal L_{a,\ell}}
=
e^{-\mathcal L_{a,\ell}/(4\pi)}.
}
\]

Any other spectral function violates either the fixed generator or the
semigroup law.

---

## 5. Trace-normalized source uniqueness

The total charged-lepton boundary source is

\[
s_\ell=\beta_\ell\tau.
\]

Let a family-symmetric scalar coefficient \(g_\ell\) act uniformly on the
rank-three lepton projector \(P_\ell\). Conservation of the total source
requires

\[
\operatorname{Tr}(g_\ell P_\ell)
=
g_\ell\operatorname{Tr}P_\ell
=
s_\ell.
\]

Since

\[
\operatorname{Tr}P_\ell=3,
\]

the unique uniform coefficient is

\[
\boxed{
g_\ell=\frac{\beta_\ell\tau}{3}.
}
\]

No other scalar coefficient preserves both uniform family normalization and
the declared total source.

---

## 6. Yukawa-prefactor uniqueness

The standard Higgs convention gives

\[
\mathbb M_\ell=\frac{v_{\rm BH}}{\sqrt2}\mathbb Y_\ell.
\]

The single profile/Hopf lift is

\[
M_{\rm lift}
=
\kappa_H\tau^2v_{\rm BH}.
\]

Require the mass operator to contain exactly once:

- the lift \(M_{\rm lift}\);
- the normalized source \(g_\ell\);
- the overlap semigroup \(\mathcal T_\ell\).

Then

\[
\mathbb M_\ell
=
M_{\rm lift}g_\ell\mathcal T_\ell.
\]

Solving for the Yukawa operator gives uniquely

\[
\boxed{
\mathbb Y_\ell
=
\sqrt2\,\kappa_H\tau^2g_\ell\mathcal T_\ell.
}
\]

Therefore

\[
\boxed{
\mathbb Y_\ell^{\rm BH}
=
\sqrt2\,
\kappa_H\tau^2
\frac{\beta_\ell\tau}{3}
e^{-\mathcal L_{a,\ell}/(4\pi)}.
}
\]

An extra scalar multiplier would be a new independent Yukawa parameter and
would violate the minimal-class assumptions.

---

## 7. Uniqueness class versus absolute uniqueness

The theorem proves uniqueness **inside the declared minimal class**.

It does not prove uniqueness among all imaginable theories. Nonminimal
alternatives include:

- higher powers of \(H^\dagger H\);
- nonlocal form factors;
- additional Higgs multiplets;
- family-dependent source coefficients;
- a different semigroup generator;
- bulk fermion or Higgs extensions;
- additional dimensionful calibrations.

Those alternatives add fields, operators, scales, or assumptions and are
outside the present BHSM completion class.

---

## 8. Refined provenance verdict

The previous phrase

\[
\text{“upstream }S_8\text{ provenance remains open”}
\]

is too weak.

The correct result is:

\[
\boxed{
\text{Current-architecture }S_8\text{ provenance is excluded.}
}
\]

The charged-lepton block is not supposed to descend from \(S_8\). It is an
intrinsic \(M_4\) Wilson/action term constrained by BHSM geometry,
projectors, profile coefficients, and compatibility data.

This is fully consistent with the stratified action's no-double-counting
ownership rule.

---

## 9. Manual completion status

### VALIDATED

- Exact \(M_4\) ownership of the Higgs and fermion variations.
- Unique one-doublet renormalizable potential for the selected vacuum.
- Unique positive overlap semigroup for the fixed generator.
- Unique uniform trace-normalized lepton source.
- Unique minimal Yukawa prefactor producing the single Hopf lift.
- No duplicate mass insertion.
- No charged-lepton mass input.
- No new field or mediator.
- Frozen family hierarchy preserved.

### INVALIDATED

- Treating \(S_8\) provenance as a remaining calculation within the current
  field architecture.
- Claiming the completed \(M_4\) block is unique without stating its
  minimality assumptions.
- Adding the geometric Yukawa operator while retaining an independent \(Y_e\)
  in the same completion branch.
- Multiplying the trace-normalized source by an additional free family scalar.

### OPEN

- Repository integration, review, protected CI, and status-ledger update.
- Independent minimal-class completions of \(Y_u\) and \(Y_d\).
- The common left-handed up/down intertwiner required for nontrivial CKM.
- RG transport from the BHSM boundary scale to comparison scales.
- A uniqueness theorem for the complete BHSM action beyond the restricted
  Higgs–charged-lepton class.

---

## 10. Verdicts

\[
\boxed{
\texttt{
BHSM\_STRATIFIED\_M4\_HIGGS\_CHARGED\_LEPTON\_COMPLETION\_UNIQUE\_WITHIN\_MINIMAL\_RENORMALIZABLE\_SEMIGROUP\_CLASS
}
}
\]

\[
\boxed{
\texttt{
BHSM\_S8\_PROVENANCE\_OF\_BOUNDARY\_LOCALIZED\_HIGGS\_LEPTON\_BLOCK\_EXCLUDED\_BY\_CURRENT\_FIELD\_OWNERSHIP
}
}
\]

\[
\boxed{
\texttt{
BHSM\_CHARGED\_LEPTON\_ACTION\_SECTOR\_LOCALLY\_COMPLETE\_CONDITIONALLY
}
}
\]

Exact next object:

\[
\boxed{
\texttt{
ACTION\_OWNED\_UP\_DOWN\_YUKAWA\_OPERATOR\_PAIR\_WITH\_COMMON\_LEFT\_HANDED\_CHARGED\_CURRENT\_INTERTWINER
}
}
\]
