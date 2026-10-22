# Independent check of the stationary-nodal Hopf-charge bound

2026-10-21; internal AI-assisted proof and originality check.

## Primary literature and originality

The scalar Berger spectrum is established. A useful direct reference is Emilio A. Lauret, *The smallest Laplace eigenvalue of homogeneous 3-spheres*, Bull. Lond. Math. Soc. **51**(1), 49–69 (2019), DOI [10.1112/blms.12213](https://doi.org/10.1112/blms.12213). [Proposition 3.9 and equation (3.8)](https://arxiv.org/html/1801.04259v3) give the full spectrum for g_(a,b,b), with inverse fibre/horizontal scale convention. It yields degree-2 eigenvalues 8 and 4+4a² when horizontal scale is one. The text points to Tanno's 1979 Lemma 4.1 as an earlier spectrum source. See also the explicit independent scalar computation in Egidi et al., [Appendix A.3](https://ems.press/content/serial-article-files/47035?nt=1), already audited in prior_art.md.

A targeted search covered combinations of Berger spectrum, harmonic quadratic forms, singular/stationary nodal great circles, Hopf decomposition and two-plane Kähler angle. It did not locate the particular constrained charge-fraction formula below. This is evidence of a plausible application-specific addition, not proof of first publication. The algebra is an elementary sharp consequence of standard quadratic harmonic/projector structure. Present it as a proved geometric restriction on the previously supplied nodal state family, not a new Berger spectrum or uniquely BHSM geometry theorem.

## Exact derivation

Let F_A(x)=xᵀAx on unit S³⊂R⁴, with A nonzero, real symmetric and tracefree. Let P be a real two-plane. Require

\[
F_A(x)=0,\qquad \nabla_{S^3}F_A(x)=0
\quad\text{for all }x\in P\cap S^3.
\]

Because \(\nabla_{S^3}F_A=2(Ax-F_Ax)\), this is equivalent to A|P=0. Merely requiring the derivative tangent to the nodal circle to vanish is insufficient: that derivative already vanishes when F is identically zero along the circle.

In the orthogonal splitting P⊕W, W=P⊥, symmetry and zero trace give

\[
A=0\oplus C,\qquad
C=\begin{pmatrix}p&q\\q&-p\end{pmatrix}\ne0.
\]

For an orthogonal complex structure J, define the fibre-charged projector

\[
P_2A=\tfrac12(A-J^TAJ).
\]

Let \(\kappa=\langle Je_1,e_2\rangle\) for an oriented orthonormal basis of P. Its square is independent of that basis. The compression of J to W is ±κK, where K is the standard orthogonal complex structure of W. Since KᵀCK=−C,

\[
\langle A,J^TAJ\rangle_F=-\kappa^2\|A\|_F^2.
\]

Consequently

\[
\boxed{f_2:=\frac{\|P_2A\|_F^2}{\|A\|_F^2}
=\frac{1+\kappa^2}{2}\ge\frac12.}
\]

This is sharp: equality holds for a totally real plane (κ=0). The upper endpoint f₂=1 holds exactly when P is J-invariant (|κ|=1), so the nodal great circle is a Hopf fibre. The value is independent of p,q and hence of the transverse shear orientation.

The identity was checked symbolically with arbitrary p,q and the complete orthogonal-complex-structure family

\[
J=\begin{pmatrix}
0&-\kappa&-u&-v\\
\kappa&0&-v&u\\
u&v&0&-\kappa\\
v&-u&\kappa&0
\end{pmatrix},\qquad \kappa^2+u^2+v^2=1,
\]

and the opposite orientation component follows by an orthogonal reflection. Exact symbolic output was \(\operatorname{tr}(AJ^TAJ)=-2\kappa^2(p^2+q^2)\), \(\operatorname{tr}(A^2)=2(p^2+q^2)\).

Normalized round measure satisfies \(\int F_A^2d\mu=\operatorname{tr}(A^2)/12\). For the homogeneous Berger deformation with fixed horizontal radius, dvol differs from round dvol by a spatially constant factor; normalized measure therefore gives the same fractions.

## Spectral consequence and normalization

For fixed horizontal radius R, inverse relative fibre scale a, and the same spatial function A, the **Rayleigh quotient** is

\[
\mathcal R_a[A]=\frac1{R^2}[8+4(a^2-1)f_2]
=\frac1{R^2}[8+2(a^2-1)(1+\kappa^2)].
\]

In general this is not an individual Berger eigenvalue: A has both neutral and charged components unless |κ|=1. With ν=a²−1,

\[
\frac{\partial\mathcal R_a}{\partial\nu}
=\frac{4f_2}{R^2}\in[2/R^2,4/R^2].
\]

The derivative with respect to a at a=1 is instead in [4/R²,8/R²]. State which parameter is differentiated and which geometric radius is held fixed. At fixed Berger volume one has R(a)=R₀a^(1/3); the derivative with respect to a² at one becomes \((4f_2-8/3)/R_0^2\), which can be negative. Thus a universal positive susceptibility claim without its scale convention is false.

## Optional persistence corollary

Suppose, as an additional dynamical assumption, a scalar operator is diagonal in these two Hopf sectors, with evolution

\[
A(t)=u_0(t)P_0A+u_2(t)P_2A.
\]

If the original stationary nodal circle is required to persist and the sector histories differ at some time, then \((P_0A)|P=0\). But P₀A is fibre-neutral, whereas the boxed bound forbids any nonzero stationary-nodal fibre-neutral quadratic. Hence P₀A=0, f₂=1 and P is Hopf-invariant. Mixed-sector stationary nodes generically cease to be stationary nodes when their histories split. This is conditional on the diagonal dynamics and persistent-node requirement; it must not be inserted as an independently derived cosmological boundary condition.

## Scientific interpretation

The bound supplies a genuine geometric restriction: the old stationary nodal degree-2 optical profile cannot be made fibre-neutral by changing the Hopf orientation; at least half its normalized spatial power is charged. The special Hopf-fibre case is entirely charged. A purely round R1 optical calculation may then explain how that state family couples to light, conditional on the declared effective action and source/lens prescriptions.

The bound supplies no amplitude, temporal state, microscopic action identification, stability result, optical projection, squashed-spacetime Jacobi correction or detection. It is defensible to separate this exact spatial geometry theorem from the conditional round optical application. Whether that combination merits the desired scientific ambition depends on the value of the actual lens-transfer consequences and should not be inferred from the sharp constant alone.
