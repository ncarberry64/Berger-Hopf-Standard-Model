# BHSM v15.44 — Lorentzian enclosure operator

Use the regular nine-coordinate chart

\[
C=Re^{u+w},\qquad
A=Re^{u+v}\cos\chi,\qquad
B=Re^{u-v}\sin\chi,
\]

\[
u=u_2\cos2\chi+u_4\cos4\chi,
\]

\[
w=\sin^2(2\chi)(w_0+w_1\cos2\chi),\qquad
v=\sin^2(2\chi)(v_0+v_1\cos2\chi),
\]

\[
f=\chi+q_2\sin2\chi+q_4\sin4\chi.
\]

At every time,

\[
\sigma=C_J[f]-\frac12,\qquad \Lambda=1-4\sigma^2.
\]

The Lorentzian reduced action is

\[
L=\operatorname{Vol}(S^3)^2\int CA^3B^3
\left[
{\kappa_1\over2}(R_7+K_{ij}K^{ij}-K^2)
-{\kappa_0\over2}-\Lambda F(X_\eta)
\right]d\chi-{J^2\over2I_H},
\]

\[
X_\eta=X_{\rm spatial}-\dot f^{\,2},\qquad J^2=\frac14.
\]

Projection of the exact v15.43 TT slice into this chart is corrected only by
the uniquely determined factor required to impose the reduced Hamiltonian:

\[
\alpha_{\rm proj}=0.98883226,\qquad H_{\rm red}=0.
\]

The velocity Hessian is nonsingular, so the Euler acceleration exists. The
orientation-odd coordinates are

\[
(u_2,w_1,v_0,q_2).
\]

Linearizing their eight-dimensional first-order system on the moving slice
gives

\[
\boxed{\max\operatorname{Re}\lambda=1.32507>0.}
\]

Therefore the symmetric constraint slice is an encapsulation saddle. Its two
conjugate unstable branches are selected by the already existing formation
orientation. This is an instantaneous nonautonomous growth exponent, not a
Floquet multiplier.

A fourth-order constraint-projected evolution along the child-oriented
unstable manifold reaches

\[
\boxed{x=-0.00207504<0}
\]

at \(\tau=2.0\). The projected Hamiltonian remains zero, its independent-grid
residual is \(2.6\times10^{-5}\), and the eta Legendre coefficient remains
positive.

Separation is derived rather than inserted. Let \(\chi_c\) solve
\(\sigma(\chi_c)=0\), let \(\chi_p\) solve \(A(\chi_p)=B(\chi_p)\), and define

\[
d[\Phi]=\int_{\chi_c}^{\chi_p}C(\chi)\,d\chi.
\]

At the evolved slice,

\[
\chi_c=0.78554372,\qquad
\chi_p=0.78730696,\qquad
\boxed{d=0.00121243>0.}
\]

The material child surface and geometric parent Hopf surface are therefore
distinguishable. This is nonlinear encapsulation and separation in the
controlled Lorentzian system. It is not yet a persistence result.
