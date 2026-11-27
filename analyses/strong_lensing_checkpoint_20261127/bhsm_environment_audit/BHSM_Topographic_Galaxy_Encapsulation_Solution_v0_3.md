# BHSM–Topographic Galaxy Encapsulation Solution v0.3
**Date:** 2026-09-15  
**Status:** Conditional analytic galaxy solution with the remaining action-owned normalization isolated.

This revision supersedes the unit-threshold assumption in v0.2. It does **not** use the observed galaxy acceleration scale to choose the BHSM threshold.

## 1. Existing scalar-topographic operator

The static scalar equation is

\[
\nabla^2T-B\nabla^4T=S.
\]

Factor it as

\[
\nabla\cdot
\left[
\nabla T-B\nabla(\nabla^2T)
\right]
=S.
\]

Define

\[
\mathbf F_T
=
\nabla T-B\nabla(\nabla^2T).
\]

The clean zero-new-parameter BHSM completion of the phenomenological acceleration map is

\[
\mathbf g_T=-Q\mathbf F_T,
\]

which fixes

\[
Q_1=Q,\qquad Q_2=-BQ_1
\]

and gives

\[
\nabla\cdot\mathbf g_T=-QS.
\]

This is the **canonical-flux closure candidate**.

---

## 2. Neighborhood-flow source

A stationary outward BHSM neighborhood flow through nested surfaces has conserved throughput. In a spherically averaged local patch,

\[
j_n(r)\propto r^{-2}.
\]

The minimal scalar source exported by that flow is therefore

\[
QS_{\rm enc}(r)=\frac{V_\Sigma^2}{r^2},
\qquad r\ge r_\star.
\]

Impose continuous activation,

\[
g_T(r_\star)=0.
\]

Then

\[
\boxed{
g_T(r)
=
V_\Sigma^2
\left(
\frac1r-\frac{r_\star}{r^2}
\right).
}
\]

---

## 3. Action-geometric seam amplitude

For a physical seam worldtube, decompose the extrinsic curvature into

- the spatial mean curvature \(H_\Sigma\);
- the acceleration-like timelike normal component
  \[
  \kappa_u\equiv \Delta K_{uu}.
  \]

In the static weak-field limit,

\[
c^2\kappa_u\simeq g_{b,n}.
\]

The Gauss/GHY quadratic invariant contains

\[
K^2-K_{ab}K^{ab}.
\]

After decomposition, its mixed piece is

\[
2H_\Sigma\kappa_u.
\]

The Einstein normalization therefore singles out the dimensionful boundary scalar

\[
\boxed{
V_\Sigma^2
=
\frac{c^2}{16\pi}
\int_{\Sigma_\star}
2H_\Sigma\kappa_u\,dA
=
\frac{c^2}{8\pi}
\int_{\Sigma_\star}
H_\Sigma\Delta K_{uu}\,dA.
}
\]

For a spherical weak-field seam,

\[
H_\Sigma=\frac2{r_\star},
\qquad
c^2\Delta K_{uu}=\frac{GM_b}{r_\star^2},
\]

hence

\[
\boxed{
V_\Sigma^2=\frac{GM_b}{r_\star}.
}
\]

This is precisely the seam amplitude required for the flat exterior solution.

**Claim boundary:** the mixed geometric invariant and its normalization are standard consequences of the boundary geometry. The still-open BHSM statement is that this mixed invariant is exactly the scalar-topographic source charge exported into the neighborhood.

---

## 4. Exact leading exterior rotation solution

Outside most baryonic mass,

\[
g_b=\frac{GM_b}{r^2}.
\]

Using

\[
V_\Sigma^2=\frac{GM_b}{r_\star},
\]

the total acceleration is

\[
g_{\rm obs}
=
g_b+g_T
=
\frac{GM_b}{r_\star r}.
\]

Therefore

\[
\boxed{
v_c^2(r)
=
r g_{\rm obs}
=
\frac{GM_b}{r_\star}
=
V_\Sigma^2
}
\]

and

\[
\boxed{v_c(r)=V_{\rm flat}}
\]

for the leading spherical exterior solution.

The total potential is

\[
\boxed{
\Phi_{\rm total}
=
V_{\rm flat}^2\ln(r/r_\star)+C.
}
\]

This part is mathematically closed once the neighborhood source and seam-export identifications hold.

---

## 5. Do not assume the threshold is one

The parent supplies the only large geometric length,

\[
R_H.
\]

The acceleration-like seam differential can be normalized as

\[
\Xi_\Sigma
=
R_H|\Delta K_{uu}|
\simeq
\frac{g_bR_H}{c^2}.
\]

Let the actual galaxy-scale BHSM instability occur at an **action-selected** universal value

\[
\boxed{\Xi_\Sigma=\xi_c.}
\]

Then

\[
\frac{GM_b}{r_\star^2}
=
\xi_c\frac{c^2}{R_H},
\]

so

\[
\boxed{
r_\star^2
=
\frac{GM_bR_H}{\xi_c c^2}.
}
\]

Using \(V_{\rm flat}^2=GM_b/r_\star\),

\[
\boxed{
V_{\rm flat}^4
=
\xi_c GM_b\frac{c^2}{R_H}.
}
\]

Thus the BTFR exponent four is independent of the exact threshold value.

Define the emergent galaxy acceleration scale

\[
\boxed{
a_{\rm gal}^{\rm BHSM}
=
\xi_c\frac{c^2}{R_H}.
}
\]

Then

\[
\boxed{
V_{\rm flat}^4=GM_ba_{\rm gal}^{\rm BHSM}.
}
\]

No separate galactic acceleration constant is introduced.

---

## 6. Outer radial-acceleration relation

For \(r\ge r_\star\),

\[
g_b
=
a_{\rm gal}^{\rm BHSM}
\left(\frac{r_\star}{r}\right)^2,
\]

while

\[
g_{\rm obs}
=
a_{\rm gal}^{\rm BHSM}
\frac{r_\star}{r}.
\]

Therefore

\[
\boxed{
g_{\rm obs}^2
=
a_{\rm gal}^{\rm BHSM}g_b
}
\]

or

\[
\boxed{
g_{\rm obs}
=
\sqrt{
\xi_c\frac{c^2}{R_H}g_b
}.
}
\]

This is the deep/outer RAR branch.

The seam thickness and higher harmonic content, not a hand-chosen interpolation function, must determine the crossover shape.

---

## 7. Hyperspherical parent form

On \(S^3(R_H)\) with \(r=R_H\chi\), conserved flow is diluted over

\[
4\pi R_H^2\sin^2\chi.
\]

The source becomes

\[
QS_{\rm enc}(\chi)
=
\frac{V_\Sigma^2}
{R_H^2\sin^2\chi}.
\]

The radial flux equation integrates to

\[
\boxed{
g_T(\chi)
=
\frac{V_\Sigma^2}{R_H}
\frac{\chi-\chi_\star}{\sin^2\chi}.
}
\]

For \(\chi\ll1\),

\[
g_T
\to
V_\Sigma^2
\left(
\frac1r-\frac{r_\star}{r^2}
\right).
\]

So the galactic solution is the local limit of the same compact parent geometry.

---

## 8. Environmental harmonics

Write the neighborhood throughput as

\[
QS(r,\Omega)
=
\frac1{r^2}
\sum_{\ell m}A_{\ell m}Y_{\ell m}(\Omega).
\]

The monopole \(\ell=0\) determines the flat rotation support.

For \(\ell\ge1\),

\[
\nabla^2\Phi_{\ell m}
=
\frac{A_{\ell m}}{r^2}Y_{\ell m}
\]

has the particular solution

\[
\Phi_{\ell m}
=
-\frac{A_{\ell m}}{\ell(\ell+1)}
Y_{\ell m},
\]

producing angular forces of order \(1/r\).

Therefore neighborhood structure naturally enters as harmonic distortions. To first order, a pure external dipole need not change the spherical monopole normalization; it instead produces lopsidedness/directional residuals. Monopole shifts require nonlinear seam-shape/environment coupling.

This is a distinct BHSM target for environment tests.

---

## 9. Lensing

If the exterior metric potentials are

\[
\Phi=V_{\rm flat}^2\ln r,\qquad
\Psi=\gamma_{\rm slip}\Phi,
\]

then the topographic deflection across the logarithmic regime is

\[
\boxed{
\alpha_{\rm enc}
=
(1+\gamma_{\rm slip})
\pi\frac{V_{\rm flat}^2}{c^2}.
}
\]

For zero slip,

\[
\boxed{
\alpha_{\rm enc}
=
2\pi\frac{V_{\rm flat}^2}{c^2}.
}
\]

Thus rotation fixes the lensing normalization except for the metric slip. BHSM must derive \(\gamma_{\rm slip}\); it cannot fit lensing independently.

---

## 10. What galaxy data would measure

Galaxy rotation does not separately determine \(R_H\) and \(\xi_c\). It measures

\[
\boxed{
a_{\rm gal}
=
\xi_c\frac{c^2}{R_H}.
}
\]

Thus cosmology and galaxy dynamics become an independent cross-scale test:

\[
\boxed{
\xi_c
=
a_{\rm gal}\frac{R_H}{c^2}.
}
\]

If BHSM derives \(\xi_c\) before the final cosmological \(R_H\) comparison, there is no freedom left.

For the commonly quoted empirical scale \(a_{\rm gal}\approx1.2\times10^{-10}\ {\rm m\,s^{-2}}\), the \(\xi_c\) values that would correspond to several **illustrative** parent radii are:

| \(R_H\) (Gpc) | \(c^2/R_H\) (m/s²) | implied \(\xi_c\) |
|---:|---:|---:|
| 24 | 1.213611e-10 | 0.9888 |
| 25 | 1.165067e-10 | 1.0300 |
| 30 | 9.708891e-11 | 1.2360 |
| 33 | 8.826264e-11 | 1.3596 |
| 35 | 8.321906e-11 | 1.4420 |
| 40 | 7.281668e-11 | 1.6480 |

These values are not to be fitted into BHSM. They are targets against which an independently derived instability root can later be tested.

---

## 11. Current closure ledger

| Question | Status |
|---|---|
| Can the existing topographic operator support flat exterior rotation? | **YES, exactly under canonical-flux closure** |
| Does a conserved neighborhood flow generate the needed \(1/r^2\) scalar source? | **YES geometrically in spherical symmetry; BHSM source ownership open** |
| Does the resulting correction turn \(1/r^2\) baryonic acceleration into total \(1/r\)? | **YES** |
| Is the exterior circular speed flat? | **YES** |
| Does the model produce \(V^4\propto M_b\)? | **YES if the galaxy instability root \(\xi_c\) is universal** |
| Is the acceleration scale tied to cosmology rather than inserted independently? | **YES: \(a_{\rm gal}=\xi_c c^2/R_H\)** |
| Is the exact normalization already predicted? | **NO: \(\xi_c\) must be derived from the galaxy-scale BHSM event/shape Hessian** |
| Is lensing fixed? | **PARTLY: rotation fixes \(\Phi\); BHSM must derive gravitational slip \(\Psi/\Phi\)** |
| Is the environment effect built in? | **YES structurally through higher neighborhood harmonics; sign/magnitude not yet derived** |
| Is this ready as a promoted physical BHSM prediction? | **NO** |

---

## 12. Exact next calculation

The galaxy problem has been reduced to one primary action calculation:

\[
\boxed{
\lambda_{\rm seam}(\Xi)=0
\quad\Longrightarrow\quad
\xi_c
}
\]

where \(\lambda_{\rm seam}\) is the lowest physical shape/encapsulation Hessian eigenvalue of the galaxy-scale child-parent seam in the existing BHSM/topographic action.

That calculation must:

1. use the existing Einstein/GHY + scalar-topographic action;
2. use the cosmological parent \(S^3(R_H)\);
3. use the physical moving seam, not an arbitrary coordinate sphere;
4. include neighborhood flux as boundary/environment data;
5. derive the instability root \(\xi_c\);
6. derive the metric slip;
7. introduce no galaxy-fit coefficient.

If this gives one universal \(\xi_c\), the leading galaxy rotation problem is closed:

\[
\boxed{
V_{\rm flat}^4
=
\xi_c GM_b\frac{c^2}{R_H}.
}
\]
