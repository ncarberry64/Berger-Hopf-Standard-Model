# BHSM–Topographic Galaxy Rotation: Gravity-Loaded Seam Hessian v0.5
**Date:** 2026-09-15  
**Status:** Gravity-only threshold derived; coupled topographic normalization reduced to one explicit Schur term. Not yet a promoted BHSM physical prediction.

## 1. Inputs already owned by the combined program

The calculation uses only:

1. Einstein gravity with GHY-completed boundary variation.
2. A compact hyperspherical parent \(S^3(R_H)\).
3. The scalar-topographic action
   \[
   S_T=\int\sqrt{-g}\left[-\frac12(\nabla T)^2-\frac{B}{2}(\Box T)^2+TS\right],
   \qquad B>0.
   \]
4. A physical child-parent seam with no independently fitted pressure or wall tension.
5. The BHSM rule that the physical Hessian is the constraint/gauge-reduced Schur complement.

No galaxy rotation datum is used to select a coefficient below.

---

## 2. The gravitational load is a boundary curvature, not a new driver

For a weak, static, spherical baryonic source define

\[
m\equiv\frac{GM_b}{c^2}.
\]

The spatial Schwarzschild metric is

\[
dl^2=\frac{dr^2}{1-2m/r}+r^2d\Omega_2^2.
\]

For the sphere \(r=\mathrm{const}\), each angular principal curvature is

\[
k_{\rm grav}^{\rm phys}
=
\frac{\sqrt{1-2m/r}}{r}.
\]

Relative to the locally flat reference value \(1/r\), the gravitational curvature deficit is therefore

\[
\boxed{
\delta k_g(r)
=
\frac{1-\sqrt{1-2m/r}}{r}.
}
\]

In the galactic weak-field limit,

\[
\delta k_g
=
\frac{m}{r^2}
+\frac{m^2}{2r^3}
+\cdots
=
\frac{g_b}{c^2}
+O\!\left(\frac{m^2}{r^3}\right).
\]

Thus the quantity previously written heuristically as \(g_b/c^2\) is the leading Brown–York/GHY curvature deficit of the actual gravitational geometry.

---

## 3. Parent Aether curvature

The hyperspherical parent has one geometric inverse length,

\[
\boxed{k_H=\frac1{R_H}.}
\]

In the Aether-surface interpretation this is the umbilic principal curvature of the parent \(S^3(R_H)\) in its canonical hyperspherical embedding.

This statement is the explicit cosmology-to-BHSM bridge used here. Intrinsic closed-FLRW geometry by itself does not require an embedding; the Aether/topographic interpretation does.

---

## 4. Why no dimension-dependent coefficient appears

Let \(P\) be the projector onto the isotropic seam tangent block of rank \(d>1\). For an umbilic shape operator

\[
K=\kappa P,
\]

the GHY canonical momentum uses the trace reversal

\[
\mathcal P(K)
=
K-(\operatorname{tr}K)P
=
(1-d)\kappa P.
\]

Both the parent curvature and the spherical gravitational deficit occupy the same projector, so their common factor \((1-d)\) cancels in a stress-free matching equation.

Therefore the zero-wall-tension canonical momentum crossing is

\[
\boxed{\delta k_g(r_\star)=k_H.}
\]

This is why the leading threshold coefficient is not inserted by hand.

---

## 5. Exact gravity-only seam threshold

The exact crossing is

\[
\boxed{
\frac{1-\sqrt{1-2m/r_\star}}{r_\star}
=
\frac1{R_H}.
}
\]

Squaring gives

\[
1-\frac{2m}{r_\star}
=
\left(1-\frac{r_\star}{R_H}\right)^2,
\]

hence

\[
\boxed{
m
=
\frac{r_\star^2}{R_H}
-
\frac{r_\star^3}{2R_H^2}.
}
\]

Equivalently,

\[
\boxed{
\frac{GM_b}{r_\star^2}
=
\frac{c^2}{R_H}
\left(
1-\frac{r_\star}{2R_H}
\right).
}
\]

Define

\[
\Xi_N
\equiv
\frac{GM_bR_H}{c^2r_\star^2}.
\]

Then the gravity-only result is

\[
\boxed{
\xi_g
=
1-\frac{r_\star}{2R_H}.
}
\]

Since \(r_\star/R_H\sim10^{-7}\) for galaxies,

\[
\boxed{\xi_g=1}
\]

to observationally negligible geometric error.

This is a result of the gravity/GHY matching, not an assumed threshold.

---

## 6. Gravity-loaded seam Hessian

BHSM already treats an encapsulation event as a reduced-Hessian crossing. Let \(q\) be the physical monopole seam/handoff mode after gauge and constraints are removed.

The gravity-only quadratic coefficient can therefore be normalized as

\[
\boxed{
\lambda_g(\Xi)
=
Z_g(\Xi-\xi_g)
+O((\Xi-\xi_g)^2),
\qquad Z_g>0,
}
\]

where the sign convention is chosen so the local gravity-dominated branch is stable for \(\Xi>\xi_g\) and the parent/neighborhood response becomes available as gravity falls through the crossing.

The root itself is independent of this orientation convention.

---

## 7. Full constrained Schur Hessian

Let \(y\) contain all coupled response variables: topographic field, lapse/shift response, compatibility multipliers, and any other physical complement that is not the seam coordinate \(q\).

Write the full physical quadratic block as

\[
\mathbb H(\Xi)
=
\begin{pmatrix}
Z_g(\Xi-\xi_g)+A_{\rm dir}(\Xi) & b(\Xi)^\dagger\\
b(\Xi) & K(\Xi)
\end{pmatrix}.
\]

After solving the complement equations, the physical seam Hessian is the Schur complement

\[
\boxed{
\lambda_{\rm seam}(\Xi)
=
Z_g(\Xi-\xi_g)
+
A_{\rm dir}(\Xi)
-
b^\dagger K^{-1}b.
}
\]

The exact galaxy threshold is therefore

\[
\boxed{
\lambda_{\rm seam}(\xi_c)=0.
}
\]

No fitted acceleration constant is required.

At leading order, if the response coefficients vary slowly across the root,

\[
\boxed{
\xi_c
=
\xi_g
+
\frac{
b^\dagger K^{-1}b-A_{\rm dir}
}{Z_g}.
}
\]

This is the requested gravity-loaded galaxy seam Schur-Hessian formula.

---

## 8. What the topographic action fixes about the sign

For the static mean-zero topographic sector,

\[
K_T=-\nabla^2+B\nabla^4.
\]

On a scalar harmonic with

\[
-\nabla^2Y_{\ell m}=k_\ell^2Y_{\ell m},
\]

its eigenvalue is

\[
\Lambda_\ell
=
k_\ell^2(1+B k_\ell^2)>0
\]

for every nonconstant physical mode when \(B>0\).

If

\[
b_T
=
\sum_{\ell\ge1,m}b_{\ell m}Y_{\ell m},
\]

then the relaxation part is

\[
\boxed{
\mathcal R_T
=
b_T^\dagger K_T^{-1}b_T
=
\sum_{\ell\ge1,m}
\frac{|b_{\ell m}|^2}
{k_\ell^2(1+B k_\ell^2)}
\ge0.
}
\]

Thus **response relaxation alone lowers the bare seam stiffness**.

The only possible competing shift at this order is the direct moving-domain/topographic term \(A_{\rm dir}\). Its value and sign must come from the coupled action; it cannot be inferred from stability alone.

If the canonical-flux coupling produces no independent direct \(q^2\) surface term, then

\[
\xi_c\ge\xi_g\simeq1.
\]

That inequality is conditional on \(A_{\rm dir}=0\), not promoted as an unconditional theorem.

---

## 9. Galaxy rotation after the action-selected root

Once the action supplies \(\xi_c\),

\[
\frac{GM_b}{r_\star^2}
=
\xi_c\frac{c^2}{R_H}.
\]

Hence

\[
\boxed{
r_\star^2
=
\frac{GM_bR_H}{\xi_cc^2}.
}
\]

The seam charge derived previously gives

\[
V_\Sigma^2=\frac{GM_b}{r_\star},
\]

and the conserved neighborhood/topographic flow gives

\[
g_T(r)
=
V_\Sigma^2
\left(
\frac1r-\frac{r_\star}{r^2}
\right).
\]

Therefore

\[
g_{\rm obs}
=
\frac{GM_b}{r_\star r},
\]

so

\[
\boxed{
V_{\rm flat}^4
=
\xi_cGM_b\frac{c^2}{R_H}.
}
\]

The outer radial-acceleration relation is

\[
\boxed{
g_{\rm obs}
=
\sqrt{
\xi_c\frac{c^2}{R_H}\,g_b
}.
}
\]

Thus the BTFR exponent and the deep-RAR square-root law survive the full threshold calculation; only the universal normalization \(\xi_c\) awaits the complete Schur block.

---

## 10. Compact-parent conservation forces a return flow

Because \(S^3\) is compact and without boundary,

\[
\int_{S^3}\nabla^2T\,dV
=
\int_{S^3}\nabla^4T\,dV
=
0.
\]

Therefore every global solution of

\[
\nabla^2T-B\nabla^4T=S
\]

must satisfy

\[
\boxed{
\int_{S^3}S\,dV=0.
}
\]

So the local outward \(1/r^2\) neighborhood source that supports flat rotation **cannot continue unchanged over the entire hypersphere**. It must be compensated by return flow / counter-source elsewhere.

This is not an extra assumption: it is the Fredholm/zero-mode solvability condition of the compact topographic equation.

Locally, for \(r\ll R_H\), the compensating return sector changes the galaxy field only by powers of \(r/R_H\), so the flat-rotation solution is unaffected over galactic scales.

Conceptually this provides a precise mathematical version of the owner statement that differentiated structures participate in a larger cycle returning toward Aether.

---

## 11. What is now genuinely derived

### Derived in the present calculation

1. The macroscopic gravitational driver is the Brown–York/GHY curvature deficit:
   \[
   \delta k_g=(1-\sqrt{1-2m/r})/r.
   \]

2. Stress-free isotropic GHY momentum matching cancels the seam-dimension factor.

3. The gravity-only Aether handoff is
   \[
   \delta k_g=1/R_H,
   \]
   giving
   \[
   \xi_g=1+O(r_\star/R_H).
   \]

4. The complete physical threshold is the Schur root
   \[
   Z_g(\Xi-\xi_g)+A_{\rm dir}-b^\dagger K^{-1}b=0.
   \]

5. Stable topographic relaxation contributes a nonnegative
   \[
   b^\dagger K_T^{-1}b.
   \]

6. Compact \(S^3\) requires zero total topographic source and therefore a global return flow.

7. Once \(\xi_c\) is supplied by that one reduced Hessian, the galaxy law is
   \[
   V_{\rm flat}^4
   =
   \xi_cGM_b c^2/R_H.
   \]

### Still not derived

1. The exact bridge identifying the Aether parent's embedded umbilic curvature with the GHY parent momentum must be attached explicitly to the canonical BHSM action.
2. The gravity-to-topographic coupling vector \(b\).
3. The direct shape term \(A_{\rm dir}\).
4. The resulting numerical \(\xi_c\).
5. The metric slip/lensing relation.
6. Realistic disc/seam thickness corrections.

No empirical galaxy value is permitted to select items 2–4.

---

## 12. Exact next executable object

The remaining numerical/action object is now extremely small conceptually:

\[
\boxed{
\mathcal C_{\rm gal}
=
\frac{
b^\dagger K^{-1}b-A_{\rm dir}
}{Z_g}.
}
\]

Then

\[
\boxed{
\xi_c
=
1+\mathcal C_{\rm gal}
+O(r_\star/R_H).
}
\]

The galaxy-rotation normalization problem is therefore reduced to **one dimensionless action-owned Schur correction**, not an arbitrary interpolation function or dark halo.
