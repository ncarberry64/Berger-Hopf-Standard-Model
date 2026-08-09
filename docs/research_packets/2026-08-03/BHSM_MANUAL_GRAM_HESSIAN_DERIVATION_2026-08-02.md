# BHSM Manual Gram–Hessian Sprint

**Date:** 2026-08-02  
**Repository baseline:** PR #217, merge `3e324a05e50b8128d28b84968b4ef3d2b064dd73`  
**Purpose:** Derive the action-normalized attachment Gram matrix, the constrained physical Hessian, exact stability gates, and the separate C3 triality spectrum without Codex.

## 1. Central attachment profiles

Use the normalized S3 harmonic and reciprocal depth profiles

\[
\Phi_C=\sqrt{\rho_0}\,Y_{k\ell m}\,e^{q_D/(2\lambda_D)}e^{-i\pi/3},
\qquad
\Phi_W=\sqrt{\rho_0}\,Y_{k\ell m}\,e^{-q_D/(2\lambda_D)}e^{+i\pi/3},
\]

with

\[
\int_{S^3}|Y_{k\ell m}|^2\,d\mu_{S^3}=1,
\qquad
\alpha=\frac1{2\lambda_D},
\qquad
s=\rho_0\alpha^2=\frac{\rho_0}{4\lambda_D^2}.
\]

At the central attachment boundary \(q_D=0\),

\[
\operatorname{Re}\langle\Phi_C,\Phi_W\rangle
=\rho_0\cos(2\pi/3)=-\frac{\rho_0}{2}.
\]

## 2. Pullback Gram matrix

For the attachment field \(\Psi=q_C\Phi_C+q_W\Phi_W\), supplemented by the canonical \(q_D\) kinetic term, the pullback Gram matrix in the order \((q_C,q_D,q_W)\) is

\[
G_{\rm att}=
\begin{pmatrix}
\rho_0 & \frac32\alpha\rho_0 & -\frac12\rho_0\\
\frac32\alpha\rho_0 & 1+3\alpha^2\rho_0 & -\frac32\alpha\rho_0\\
-\frac12\rho_0 & -\frac32\alpha\rho_0 & \rho_0
\end{pmatrix}.
\]

Its leading principal minors are

\[
\rho_0,
\qquad
\frac{\rho_0}{4}(4+3\alpha^2\rho_0),
\qquad
\det G_{\rm att}=\frac34\rho_0^2.
\]

Therefore

\[
\boxed{G_{\rm att}>0\quad\text{for every }\rho_0>0,\ \lambda_D>0.}
\]

This closes the Gram-positivity part of the sprint.

## 3. Exact attachment constraint and physical tangent space

The merged v11.3 multiplier equation is

\[
I_W=\upsilon I_C,
\qquad
\upsilon=e^{-q_D/\lambda_D}.
\]

Linearization at \(\upsilon=1\) gives

\[
-\delta q_C+\delta x_D+\delta q_W=0,
\qquad x_D=q_D/\lambda_D.
\]

Thus the exact constraint row is

\[
B=(-1,1,1).
\]

A tangent basis in the order \((q_C,q_D,q_W)\) is

\[
N=
\begin{pmatrix}
1&1\\
0&1\\
1&0
\end{pmatrix}.
\]

The physical Gram matrix is

\[
G_\parallel=N^TG_{\rm att}N
=
\begin{pmatrix}
\rho_0 & \rho_0/2\\
\rho_0/2 & 1+\rho_0+3\alpha\rho_0+3\alpha^2\rho_0
\end{pmatrix}.
\]

Its determinant is

\[
\det G_\parallel
=
\frac{\rho_0}{4}
\left(
4+3\rho_0+12\alpha\rho_0+12\alpha^2\rho_0
\right)>0.
\]

Hence the common attachment domain contains **two physical tangent modes**. The third coordinate direction is the exact multiplier-constraint normal.

## 4. General k=0 Hessian

Let

\[
U_{IJ}=\left.\frac{\partial^2V_{\rm rel}}
{\partial q_I\partial q_J}\right|_{\rm eq}.
\]

For \(k=0\), the user-specified profile terms give

\[
H_{\rm att}=
\begin{pmatrix}
U_{CC}+s & U_{CD}+s & U_{CW}+s/2\\
U_{CD}+s & 1+U_{DD} & U_{DW}+s\\
U_{CW}+s/2 & U_{DW}+s & U_{WW}+s
\end{pmatrix}.
\]

Write this as

\[
H=
\begin{pmatrix}
a&p&b\\
p&d&q\\
b&q&c
\end{pmatrix}.
\]

The unconstrained characteristic polynomial is

\[
\lambda^3-T\lambda^2+P\lambda-D=0,
\]

where

\[
T=a+d+c,
\]

\[
P=ad+ac+dc-p^2-b^2-q^2,
\]

\[
D=adc+2pbq-aq^2-db^2-cp^2.
\]

Positive definiteness in this ordering is equivalent to

\[
a>0,\qquad ad-p^2>0,\qquad D>0.
\]

## 5. Physical constrained Gram–Hessian

Projection onto the exact attachment tangent space gives

\[
H_\parallel=N^THN
=
\begin{pmatrix}
a+2b+c & a+b+p+q\\
a+b+p+q & a+2p+d
\end{pmatrix}.
\]

Define

\[
h_{11}=a+2b+c,\quad
h_{12}=a+b+p+q,\quad
h_{22}=a+2p+d,
\]

and

\[
g_{11}=\rho_0,\quad
g_{12}=\rho_0/2,\quad
g_{22}=1+\rho_0+3\alpha\rho_0+3\alpha^2\rho_0.
\]

The two physical restoring eigenvalues solve

\[
\det(H_\parallel-\mu G_\parallel)=0.
\]

With

\[
\Delta_G=g_{11}g_{22}-g_{12}^2,
\]

\[
B_\mu=h_{11}g_{22}+h_{22}g_{11}-2h_{12}g_{12},
\]

\[
C_\mu=h_{11}h_{22}-h_{12}^2,
\]

the exact roots are

\[
\boxed{
\mu_\pm=
\frac{B_\mu\pm\sqrt{B_\mu^2-4\Delta_GC_\mu}}
{2\Delta_G}.
}
\]

Because \(G_\parallel>0\), physical stability is equivalent to

\[
\boxed{h_{11}>0,\qquad C_\mu>0.}
\]

Nondegeneracy additionally requires

\[
B_\mu^2-4\Delta_GC_\mu>0.
\]

## 6. Core–wall symmetric equilibrium

If

\[
U_{CC}=U_{WW}=u,\quad
U_{CD}=U_{DW}=v,\quad
U_{CW}=w,\quad
U_{DD}=z,
\]

then the full unconstrained Hessian has one core–wall antisymmetric eigenvalue

\[
\lambda_A=u-w+\frac{s}{2},
\]

and two symmetric/depth eigenvalues

\[
\lambda_\pm=
\frac{
u+w+\frac32s+1+z
\pm
\sqrt{\left(u+w+\frac32s-1-z\right)^2+8(v+s)^2}
}{2}.
\]

The full 3x3 matrix is positive when

\[
u-w+\frac{s}{2}>0,
\]

\[
1+z>0,
\]

\[
\left(u+w+\frac32s\right)(1+z)>2(v+s)^2.
\]

Only the two generalized tangent roots \(\mu_\pm\) are physical while the v11.3 multiplier constraint remains exact.

## 7. Minimal geometric baseline

Set \(U_{IJ}=0\). Then

\[
H_0=
\begin{pmatrix}
s&s&s/2\\
s&1&s\\
s/2&s&s
\end{pmatrix}.
\]

The full matrix is positive for

\[
0<s<\frac34,
\]

and nondegenerate except at \(s=2/5\).

On the exact attachment tangent space, positivity holds in the wider range

\[
\boxed{0<s<\frac{12}{13}.}
\]

For the normalized demonstration point

\[
\rho_0=1,\qquad \lambda_D=1,\qquad s=\frac14,
\]

the physical generalized eigenvalues are

\[
\mu_1=0.15973954,\qquad
\mu_2=0.85588546,
\]

with restoring-mass ratio

\[
\sqrt{\mu_1}:\sqrt{\mu_2}=1:2.31473676.
\]

This is a stable attachment benchmark, not a charged-lepton prediction.

## 8. Separate C3 generation diagonalization

The exact C3 Hermitian response algebra is

\[
H_{\rm gen}
=
aI+x(C+C^2)+iy(C-C^2).
\]

Its exact family eigenvalues are

\[
\ell_0=a+2x,
\]

\[
\ell_1=a-x-\sqrt3\,y,
\]

\[
\ell_2=a-x+\sqrt3\,y.
\]

All three are positive when

\[
a+2x>0,
\qquad
a-x>\sqrt3|y|.
\]

They are nondegenerate when

\[
y\neq0,
\qquad
y\neq\pm\sqrt3x.
\]

A pure phase choice \(\theta=\pm\pi/3\) for one complex circulant coupling lies on
\(y=\pm\sqrt3x\) and therefore leaves a twofold degeneracy. The stated
G2/C3 **structural imbalance** must supply the action-derived departure from
that equality.

The coefficients are extracted without fitting by

\[
a=\frac13\operatorname{Tr}H_{\rm gen},
\]

\[
x=\frac16\operatorname{Tr}[(C+C^2)H_{\rm gen}],
\]

\[
y=\frac16\operatorname{Tr}[i(C-C^2)H_{\rm gen}].
\]

Equivalently, each family stiffness is the projection onto the exact rank-one
triality projector \(P_k\):

\[
\ell_k=\operatorname{Tr}(P_kH_{\rm gen}).
\]

The generation hierarchy, once \(a,x,y\) are action-derived, is

\[
m_e:m_\mu:m_\tau
=
\sqrt{\ell_{(1)}}:\sqrt{\ell_{(2)}}:\sqrt{\ell_{(3)}},
\]

with the roots sorted in increasing order.

## 9. Manual sprint verdict

### Derived

- Positive-definite action-normalized attachment Gram matrix.
- Positive-definite common-domain physical Gram matrix.
- Exact constrained 2x2 generalized eigenproblem.
- Exact stability and nondegeneracy conditions.
- Stable minimal geometry-only benchmark.
- Exact separation between the two attachment tangent modes and the three C3 family modes.
- Exact C3 positivity and nondegeneracy gates.

### Still action-dependent

- Numerical values of \(U_{IJ}\).
- Numerical \(\rho_0/\lambda_D^2\) normalization.
- Triality response coefficients \(a,x,y\).
- Selection of which stable attachment branch carries the charged-lepton family operator.
- Absolute mass scale.

### Exact next calculation

\[
\boxed{
\text{Project the inherited core/wall second variation onto }N,
\text{ evaluate }U_{IJ},
\text{ and project the selected stable branch onto }P_0,P_1,P_2.
}
\]

This is the shortest direct path to unconditional Mark II and a genuine
three-generation restoring-stiffness spectrum.
