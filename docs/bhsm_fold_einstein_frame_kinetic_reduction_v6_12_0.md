# BHSM v6.12.0 Einstein-frame fold kinetic reduction

Primary result:
`BHSM_FOLD_KINETIC_SIGN_REQUIRES_MOVING_ENDPOINT_SHIFT_BOUNDARY_CONDITION`.

This sprint derives the exact four-dimensional frame function through first
order and its positive Weyl kinetic contribution. It also proves that the
zero-shift promotion of the v6.11 static fold tangent violates the radial
momentum constraint. The existing repository does not specify the scalar
radial-shift Green-function boundary condition at the moving B1 endpoint, so
the constraint-reduced Jordan metric and total Einstein-frame kinetic sign
cannot be computed.

The stored cusp is additionally an on-shell, \(X(q)\)-substituted action, not
an off-shell Jordan potential. Its Einstein-frame curvature requires the
second frame response \(F_2[a_2,N_2]\) and the off-shell coefficients of
\(V_J\). No kinetic, mass, or sheet-instability sign is manufactured.

## Exact frame function

Use the fixed-domain coordinate \(t\in[0,1]\):

\[
a_0(t)=\sqrt2\sin(\pi t/4),\qquad N_0=\pi/4,
\]

\[
a_1(t)=\chi_1\left[
\frac{a_0}{4}-\frac{\sqrt2\,t\cos(\pi t/4)}4\right],
\qquad N_1=-\frac{\chi_1}{4}.
\]

For two caps, the bulk P1 coefficient of \(R_4[h]\) is

\[
F_{\rm bulk}(q)=2\kappa_1\int_0^1N(t,q)a(t,q)^2dt.
\]

The intrinsic B1 term contributes \(F_{\rm B1}=2C_\partial=1\).
GHY cancels radial second derivatives but contains no independent \(R_4\)
density. Endpoint motion is already included by
\(N(q)=\rho_J(q)\) in fixed-domain gauge.

The exact critical integrals are

\[
I_0=\int_0^1N_0a_0^2dt=\frac{\pi}{4}-\frac12,
\]

\[
I_1=\int_0^1[N_1a_0^2+2N_0a_0a_1]dt
=\frac{\chi_1(\pi-4)}8.
\]

Therefore

\[
F_0=2I_0+1=\frac{\pi}{2},
\]

\[
F_{1,\tau}=\tau\,2I_1
=\tau\frac{\chi_1(\pi-4)}4.
\]

With Taylor conventions
\(a=a_0+\tau a_1q+\frac12a_2q^2+\cdots\) and similarly for \(N\),

\[
F_2=4\int_0^1\left[
N_0(a_1^2+a_0a_2)+2N_1a_0a_1+\frac12N_2a_0^2
\right]dt.
\]

The analytic \(a_2,N_2\) response is not stored.

## Einstein frame

Define

\[
g_{\mu\nu}^E=\Omega^2h_{\mu\nu},\qquad
\Omega^2=\frac{F(q)}{F_0}.
\]

Then the Einstein coefficient is exactly

\[
M_4^2=F_0=\frac{\pi}{2}
\]

in the normalized action unit. The scalar-tensor transformation gives

\[
k_E(q)=\frac{F_0}{F}K_J
+\frac{3F_0}{2}\left(\frac{F'}F\right)^2.
\]

At the fold, the exact Weyl contribution is sheet independent:

\[
K_{\rm Weyl}(0)
=\frac{3F_1^2}{2F_0}
=\frac{3\chi_1^2(4-\pi)^2}{16\pi}>0.
\]

This does not decide the total sign without the constraint-reduced
\(K_J\).

## ADM gauge sector

The radial ADM form is

\[
ds_5^2=N^2dt^2+h_{\mu\nu}
(dx^\mu+N^\mu dt)(dx^\nu+N^\nu dt).
\]

The scalar sector requires lapse \(A_q\), radial shift
\(N_\mu=\partial_\mu B_q\), Weyl scalar \(\psi_q\), longitudinal scalar
\(E_q\), endpoint displacement, and the bulk scalar fluctuation.

Under radial and four-dimensional scalar diffeomorphisms,

\[
\delta\sigma\mapsto\delta\sigma-\xi^\rho\sigma_0',
\qquad
\psi\mapsto\psi-H\xi^\rho,
\]

\[
A\mapsto A-N_0^{-1}\partial_t(N_0\xi^\rho),
\]

\[
B\mapsto B-N_0^2\xi^\rho-a_0^2\partial_t\xi,
\qquad E\mapsto E-\xi,
\]

\[
\delta\rho_J\mapsto\delta\rho_J-\xi^\rho_J.
\]

The induced intrinsic curvature perturbation remains invariant when the
endpoint pullback is transformed. Hence
\(\delta X=\tau\chi_1\) is not pure radial gauge.

## Momentum-constraint obstruction

The radial momentum constraint is

\[
D_\nu(K^\nu{}_\mu-\delta^\nu{}_\mu K)
=\kappa_1^{-1}Z_5(n\sigma)D_\mu\sigma.
\]

At the critical background \(\sigma_0'=0\), so the linear scalar flux
vanishes. For the v6.11 metric tangent,

\[
H_1(t)
=\delta_q\left(\frac{a_t}{Na}\right)
=\frac{\chi_1t}{4\sin^2(\pi t/4)}.
\]

Setting the scalar shift to zero leaves the exact mismatch

\[
-3\tau H_1(t)\partial_\mu q
=-\frac{3\tau\chi_1t}
{4\sin^2(\pi t/4)}\partial_\mu q\ne0.
\]

Thus the static tangent cannot simply be promoted to \(q(x)\). The lapse,
shift, longitudinal metric, and endpoint compensators must be solved
together.

Regularity supplies the pole condition, but the stored B1 analysis gives
only homogeneous-background junction and conservation identities. It does
not give the x-dependent scalar radial-shift/longitudinal boundary condition
at the moving endpoint. Consequently the shift Green function has an
unfixed homogeneous trace. One cannot classify that trace as residual gauge
or a boundary radion, prove boundary-flux cancellation, or construct a
unique constraint inverse.

## Jordan moduli metric

The formal decomposition is

\[
K_J=K_{\rm scalar}+K_{\rm EH}+K_{\rm GHY}+K_{\rm B1}
+K_{\rm constraint}+K_{\rm endpoint}.
\]

The known scalar part is preserved:

\[
K_{\rm scalar}
=2Z_5\int_0^{\rho_J}Na^2(\partial_q\sigma)^2d\rho\ge2.
\]

The remaining terms are separately gauge dependent. EH supplies the bulk
scalar metric form; GHY cancels radial derivative variations and contributes
to the endpoint form; B1 controls the intrinsic metric constraint;
lapse/shift elimination supplies the Schur term; and the moving endpoint is
paired with the shift trace. Their sum is denoted

\[
K_{\rm shift+endpoint}^{\rm red}.
\]

It is not a new primitive: it is an unevaluated part of the existing action.
Without the endpoint shift boundary condition,

\[
K_J(0)
\]

and therefore

\[
k_q^E(0)=K_{\rm scalar}
+K_{\rm shift+endpoint}^{\rm red}
+\frac{3\chi_1^2(4-\pi)^2}{16\pi}
\]

have no determined sign.

## Einstein-frame potential

The v6.11 expression

\[
\Gamma_{{\rm red},\tau}
=\Gamma_c+\frac{\delta\mu}{4}q^2
-\tau\frac{\nu_1}{6}q^3+\cdots
\]

was obtained after substituting the maximally symmetric \(X(q)\) solution
and its \(X\)-dependent regulated four-volume. It is not the off-shell
Jordan potential \(V_J(q)\).

Formally,

\[
V_E=\left(\frac{F_0}{F}\right)^2V_J.
\]

Writing \(V_J=V_0+V_1q+\frac12V_2q^2+\cdots\),

\[
V_E''(0)=V_2-4\frac{F_1}{F_0}V_1
+\left[
6\left(\frac{F_1}{F_0}\right)^2
-2\frac{F_2}{F_0}
\right]V_0.
\]

The repository does not supply \(V_0,V_1,V_2\) before the \(X\) equation or
\(F_2[a_2,N_2]\). Therefore neither \(B_{\rm ext}^E\),
\(B_{\rm core}^E\), nor either canonical mass squared is derived. The
v6.11 reduced-frame signs are preserved as a theorem but not promoted to
Einstein-frame mass signs.

## Physical verdict

The result is Case E. Positive norm, ghost, gauge, and nondynamical
classifications all remain unproved. No Rayleigh quotient or Morse-index
lower bound is available, and neither sheet is selected.

The exact next construction is to derive the scalar radial-shift Green
function from the bulk momentum constraint with the x-dependent B1
moving-endpoint matching condition, then reconstruct the off-shell
\(V_J\) and \(F_2\).

No new action term, `tau_J`, new primitive, measured input, neutral
construction, fermion loop, physical bulk Dirac law, sheet relabeling,
frozen-prediction change, or official prediction-logic change is introduced.
