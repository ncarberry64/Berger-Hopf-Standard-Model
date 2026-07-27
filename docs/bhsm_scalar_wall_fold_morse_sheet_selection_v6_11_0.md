# BHSM v6.11.0 scalar-wall fold Morse sheet selection

Primary result:
`BHSM_TWO_FOLD_SHEETS_HAVE_OPPOSITE_REDUCED_HESSIAN_SIGN`.

The fixed-parameter reduced potential is now determined through cubic order,
but a physical negative-mode theorem is not. The upper/exterior fold branch
has negative leading reduced curvature and the lower/core-facing branch has
positive leading reduced curvature. The total gauge-reduced kinetic norm
remains open because the repository does not contain the required
four-dimensional gravitational, lapse/shift, endpoint, and boundary
quadratic reduction.

No `tau_J`, phenomenological junction action, neutral transport term, new
primitive, or fermion determinant is introduced.

## Frozen action and branch

The calculation uses the existing P1+GHY+B1+scalar action,

\[
S_{\rm bulk}=\int\sqrt{-g}\left[
\frac{\kappa_1}{2}R_5-\frac{\kappa_0}{2}
-\frac{Z_5}{2}(\nabla\sigma)^2-U_5(\sigma)\right],
\]

\[
U_5=\frac{A_5}{2}\sigma^2+\frac{G_5}{4}\sigma^4,
\]

with the frozen normalized representative. The action control is
\(\mu=-A_5/Z_5\); \(X\), the warp factor, lapse/length, and junction position
are solved variables in the v6.1.7 ensemble.

The Puiseux branch is

\[
\mu_\tau=\mu_c+\tau\nu_1r+O(r^2),\qquad
X_\tau=2+\tau\chi_1r+O(r^2),
\]

where \(r=|\epsilon|\), \(s=\operatorname{sign}\epsilon\), and
\(\tau=\pm1\). Hence

\[
\frac{d\mu_\tau}{dr}=\tau\nu_1,\qquad
\frac{dX_\tau}{dr}=\tau\chi_1.
\]

The raw solution-branch tangent changes \(\mu\). It is therefore not itself a
fixed-theory physical fluctuation.

## Physical tangent and quotient

The smallest raw perturbation vector is built from

\[
(\delta\sigma,\delta a,\delta N,\delta\rho_J,\delta X,\delta\mu).
\]

The lapse equation supplies the normal/Hamiltonian constraint. Radial
reparameterizations generate the gauge subspace. Junction traces impose
\(\delta\sigma_J=0\), \(\delta a_J=0\), and the differentiated
\(a'_J=X/2\) condition, including endpoint terms. Thus

\[
T_{\rm phys}=\ker C/\operatorname{im}G.
\]

In the fixed-domain coordinate \(t\in[0,1]\),

\[
a_0=\sqrt2\sin(\pi t/4),\qquad N_0=\ell_0=\pi/4,
\]

and the stored leading correction is

\[
a_1=\chi_1\left[
\frac{a_0}{4}
-\frac{\sqrt2\,t\cos(\pi t/4)}{4}\right],
\qquad N_1=-\frac{\chi_1}{4}.
\]

After discarding the external \(\delta\mu=\tau\nu_1\) component, the
one-sided candidate vector is

\[
Z_q^{\rm phys}
=[s u_1,\tau a_1,\tau N_1,0,\tau\chi_1]\mod\operatorname{im}G.
\]

It obeys the stored linearized constraint and endpoint conditions. It is not
pure gauge because \(\delta X=\tau\chi_1\) changes intrinsic four-curvature.
The collective coordinate is the fold amplitude \(q=r=|\epsilon|\), not a
literal rigid wall displacement \(b\).

## Kinetic norm

Promoting \(q\) to a slowly varying M4 field gives the positive scalar
contribution

\[
k_q^{\rm scalar}
=2Z_5\int_0^{\rho_J}Na^2
(\partial_q\sigma)^2\,d\rho.
\]

At the critical point,

\[
k_q^{\rm scalar}
=2\int_0^{\pi/4}a_0^2u_1^2\,d\rho.
\]

The frozen normalization is
\(\int a_0^4u_1^2d\rho=1\) per cap. Since
\(0<a_0^2\le1\), \(a_0^2\ge a_0^4\), so

\[
k_q^{\rm scalar}\ge2>0.
\]

This is not the total kinetic norm. The fold vector also contains metric,
curvature, lapse, and endpoint components. The missing existing-action
calculation is

\[
k_q^{\rm grav,red}
=\langle Z_g,(K_{\rm P1}+K_{\rm GHY}+K_{\rm B1})Z_g\rangle
-\langle Z_g,K_{gC}K_{CC}^{-1}K_{Cg}Z_g\rangle
\]

after removing gauge kernels. Therefore

\[
k_q=k_q^{\rm scalar}+k_q^{\rm grav,red}
\]

has unresolved sign. It is not normalized to one. `Z_partial` contributes
nothing because the B1 field \(\sigma_{\partial}\) is distinct from the bulk
fold amplitude and no action/domain map identifies them.

## Fixed-parameter Lyapunov--Schmidt action

Write

\[
\Phi=\Phi_c+q u_1+w(q,\mu),\qquad
\langle u_1,w\rangle_{a_0^4}=0.
\]

The complement equation eliminates \(w\) and the solved metric/endpoint
variables order by order. The Feynman--Hellmann identity gives

\[
\partial_\mu\widehat\Gamma
=\frac{1}{X^2}\int a^4\sigma^2d\rho
=\frac{q^2}{4}+O(q^3)
\]

at \(X_c=2\). Hence the coefficient of
\(\delta\mu q^2\) in the reduced action is \(1/4\).

Matching stationarity to
\(\delta\mu=\tau\nu_1q+O(q^2)\) fixes the one-sided cubic term:

\[
\Gamma_{{\rm red},\tau}
=\Gamma_c+\frac{\delta\mu}{4}q^2
-\tau\frac{\nu_1}{6}q^3
+O(q^4,\delta\mu q^3).
\]

Indeed,

\[
\partial_q\Gamma_{{\rm red},\tau}
=\frac{q}{2}(\delta\mu-\tau\nu_1q)+O(q^3).
\]

On the stationary branch this yields

\[
\Gamma_\tau-\Gamma_c
=\tau\frac{\nu_1}{12}q^3+O(q^4),
\]

exactly reproducing the frozen cusp coefficient. The cubic is a one-sided
term in \(q=|\epsilon|\) after eliminating the double-root \(X\) constraint;
it is not an odd term in the signed scalar amplitude.

The physical potential curvature differentiates at fixed \(\mu\):

\[
B_\tau^{\rm red}
=\left.\partial_q^2\Gamma_{{\rm red},\tau}\right|_\mu
=-\tau\frac{\nu_1}{2}q+O(q^2).
\]

No \(d^2\Gamma_\tau(r)/dr^2\) along the parameter-changing branch is used.

## Sheet map

Intrinsic curvature fixes the orientation-independent branch label:

\[
\operatorname{sign}(X-2)=\tau.
\]

Thus \(\tau=+1\) is the upper/high-curvature branch and \(\tau=-1\) the
lower/low-curvature branch. Normal reversal flips signed extrinsic curvature
and the scalar normal derivative, but not \(X\) or \(\tau\). Reversing the
radial coordinate changes the endpoint representation without exchanging
the two curvature roots.

The exterior/core-facing names inherit the explicit v6.2 BHSM sheet axiom:

- \(\tau=+1\): upper, exterior/spacetime-facing;
- \(\tau=-1\): lower, core-facing.

## Morse result

For sufficiently small \(q>0\),

\[
B_{\rm exterior}^{\rm red}
=-\frac{\nu_1}{2}q+O(q^2)<0,
\]

\[
B_{\rm core}^{\rm red}
=+\frac{\nu_1}{2}q+O(q^2)>0.
\]

The requested core-facing negative curvature is therefore not produced by
the leading fixed-control fold action. The signs are opposite to that target.

Rayleigh--Ritz still requires \(k_q>0\). Because
\(k_q^{\rm grav,red}\) is unavailable, no physical tachyon, ghost, modulus,
or Morse-index lower bound is certified on either sheet. A negative witness
alone would not prove exact Morse index one, and this sprint does not claim
global stability.

The existing action is sufficient in principle and already fixes the
reduced potential. `tau_J` is unnecessary. The exact active construction is
the x-dependent P1+GHY+B1 scalar-sector quadratic action followed by
lapse/shift elimination and the radial gauge quotient to determine
\(k_q^{\rm grav,red}\).

The v6.8 universal `lambda_geom` theorem and the v6.9/v6.10 junction
no-mixing results remain unchanged. Static junction mixing remains rejected;
propagation-dependent compact-mode transport is a separate future target.
