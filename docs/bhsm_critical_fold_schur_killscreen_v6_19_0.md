# BHSM v6.19.0 critical-fold Schur-complement kill-screen

Primary theorem:
`BHSM_FOLD_KINETIC_REQUIRES_ONE_MISSING_ACTION_BLOCK`.

The calculation is performed directly at \(q=0\) on
\[
X_c=2,\quad N_0=\pi/4,\quad
a_0=\sqrt2\sin(\pi t/4),\quad
\sigma_0=0,\quad\delta\sigma=q(x)u_1(t).
\]

Fixed-\(\iota\) support sets \(\zeta=0\). After forming the invariant
\(S=B-a_0^2\partial_tE\), \(E=0\) is a transparent gauge. The v6.18
response eliminates the nonconstant threading trace and \(C_\Sigma=0\)
eliminates its homogeneous constant. The scalar zero mode is the physical
fold tangent. The remaining constrained metric variables are the lapse
multiplier \(A\) and radial Weyl scalar \(\psi\).

The required derivative form is
\[
S_{\rm deriv}^{(2)}
=\frac12\int\sqrt{-h}\left[
K_{\rm direct}(Dq)^2
+2(Dq)\langle J_{\rm rad},(A,\psi)\rangle
+\langle(A,\psi),\mathcal L_{A\psi}^{\rm crit}(A,\psi)\rangle
\right].
\]
The radial measure is \(N_0a_0^4dt\). The two reflected caps and common B1
are retained. The known direct terms are
\[
K_{\rm scalar}
=2\int_0^{\pi/4}a_0^2u_1^2d\rho\ge2
\]
and
\[
K_{\rm Weyl}
=\frac{3\chi_1^2(4-\pi)^2}{16\pi}
=1.220620174933802\ldots .
\]

The kill-screen fails at one exact object:
\[
\mathcal L_{A\psi}^{\rm crit}(t,t')
=\left.
\frac{\delta^2S_{\rm deriv}}
{\delta(A,\psi)(t)\delta(A,\psi)(t')}
\right|_{q=0}
=
\begin{pmatrix}
0&C_H^\dagger\\
C_H&H_{\psi\psi}
\end{pmatrix}.
\]
It is the \(2\times2\) formally self-adjoint radial saddle operator whose
off-diagonal block is the linear Hamiltonian constraint and whose lower
block is the Weyl Hessian. Its domain must combine regular pole series with
the independent B1 metric-junction conditions after the threading response.

This block is absent at
`src/bhsm/interface/fold_einstein_frame_kinetic_reduction.py:252`,
`src/bhsm/interface/fold_einstein_frame_kinetic_reduction.py:282`, and is
still recorded as absent at
`src/bhsm/interface/covariant_threading_response.py:295`.

Without it, \(A\) cannot be eliminated, \(J_{\rm rad}\) is not fixed, and
the adjoint domain, kernel, compatibility, and inverse cannot be defined.
The formal remaining reduction
\[
K_{\rm red}
=K_{\rm direct}
-\langle J_{\rm rad},
(\mathcal L_{A\psi}^{\rm crit})^{-1}J_{\rm rad}\rangle
\]
therefore has no value. No numerical solve or pseudoinverse is attempted.

Consequently \(K_{\rm shift+endpoint}^{\rm red}\), \(k_q^E\), its
uncertainty, and its sign remain undefined. The fold is not classified as
positive, ghost, or null, and no physical mass is inferred.

No measured or fitted input, primitive, scale, action term, threshold,
`tau_J`, boundary tension, neutral work, frozen-prediction change, or
official prediction-logic change is introduced.
