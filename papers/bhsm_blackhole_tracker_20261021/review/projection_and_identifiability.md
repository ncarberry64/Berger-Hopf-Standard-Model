# Projection and conditional identifiability of the normalized R1 exterior

This is an internal mathematical and prior-art check, with no edits to the main manuscript. The useful result is a conditional transfer and information theorem. It does not establish an action-selected black-hole boundary amplitude, a horizon observable, or uniqueness against arbitrary ordinary matter. The independent script `check_projection_identifiability.py` passes 25 algebraic/numerical controls; its JSON receipt includes matched-profile projections and exact stationary-branch finite differences.

## 1. Inputs and normalization

Use the isolated, frozen, weak-metric cubic exterior, outside a declared worldtube r0. Its l=2 radial transfer satisfies

\[
(r^2K_r f')'-6K_\Omega f=0,\quad f(r_0)=1,
\quad f(r)\sim C_o r^{-3}\quad(r\to\infty),
\]
\[
K_r=C\sqrt{1+(r_V/r)^3},\quad
K_\Omega=K_r+\tfrac12rK_r',\quad C>0,
\quad r_V>0.
\]

The infinity condition belongs to this isolated local matching model. A cosmological finite-endpoint projection must retain its specified outer completion and geometric weights. It is not a global flat-space solution on the recovered compact S3 background.

Let Cij be a real STF 3 by 3 matrix with tr(C²)=1, and set

\[
Y_C(n)=\sqrt{15/(8\pi)}\,C_{ij}n_i n_j,
\qquad\int_{S^2}Y_C^2d\Omega=1.
\]

Then a fY_C is a scalar boundary state of L2 norm |a| at r0. The Weyl/metric coefficient multiplying a is the one derived from the same action and must be retained, with its factor of two depending on whether W denotes Phi+Psi or their mean. Define the projection below after factoring out that fixed coefficient, the harmonic normalization, and the known thin-lens distance prefactor. No independently fitted scalar-to-photon coupling is introduced. An independent harmonic metric quadrupole remains a separate allowed integration datum.

The elliptic maximum principle gives f>0, and the flux equation gives f'<0. Integration by parts supplies the positive conormal impedance

\[
-r_0^2K_r(r_0)f'(r_0)
=\int_{r_0}^{\infty}[r^2K_r(f')^2+6K_\Omega f^2]dr>0.
\]

This proves uniqueness at a fixed boundary value, not selection of that value by a black-hole interior.

## 2. Exact STF projection and its null space

Take a frozen straight ray (b cos phi,b sin phi,z), b>=r0, with symmetric full-line integration. Parameterize

\[
C=\begin{pmatrix}-c/2+s_1&s_2&u\\s_2&-c/2-s_1&v\\u&v&c\end{pmatrix},
\quad\operatorname{tr}C^2=\tfrac32c^2+2(s_1^2+s_2^2+u^2+v^2).
\]

Direct integration gives

\[
\mathcal P_f[C](b,\phi)=cA_0(b)+T(b)[s_1\cos2\phi+s_2\sin2\phi],
\]
\[
T(b)=b^2\int_{-\infty}^{\infty}\frac{f(\sqrt{b^2+z^2})}{b^2+z^2}\,dz>0,
\]
\[
A_0(b)=\int_{-\infty}^{\infty}f(\sqrt{b^2+z^2})
\left(1-\frac{3b^2}{2(b^2+z^2)}\right)dz.
\]

The xz and yz terms are odd in z and vanish exactly. Hence no one-view full-line experiment of this form can reconstruct all five STF components, including an arbitrary three-dimensional orientation and norm. If the three visible boundary coefficients are inferred with the fixed action normalization, they give the lower bound

\[
a^2\ge\tfrac32(ac)^2+2[(as_1)^2+(as_2)^2],
\]

but equality requires the two hidden components to vanish.

There is an important exception to an unqualified rank-three claim: for a harmonic f=C_o/r³, A0 is identically zero. The ordinary isolated mass quadrupole therefore has rank two and projects only onto its transverse STF part. For the genuinely screened cubic response above, rank three holds in the representation space. To prove it, put Y=r³f. The radial equation becomes

\[
(K_r r^{-4}Y')'=6K_r'r^{-5}Y.
\]

Since Y>0, K_r'<0 and K_r r^-4Y' tends to zero at infinity, integration from r to infinity gives Y'>0. Also, using zf->0 at both endpoints,

\[
A_0(b)=\frac12\int_{-\infty}^{\infty}\frac{z^2}{r^2}
[rf'(r)+3f(r)]dz
=\frac12\int\frac{z^2}{r^4}Y'(r)dz>0.
\]

Consequently the representation map has exactly the two-dimensional kernel span(Cxz,Cyz), and rank three. The extra axial channel becomes small in the outer harmonic limit and is not automatically observable separately from the monopole. A finite observer/source interval, unequal weights, lens motion during crossing, or a second viewing direction changes this projection and its nulls; none may be assumed to resolve them without calculation.

## 3. Deep-screened and harmonic projections

In the overlap r0<=b<<rV the matched radial function has f~Ad/r, with Ad fixed by r0 normalization and outer matching. The leading transverse projection is

\[
T(b)\sim2A_d,
\qquad b^2\int r^{-3}dz=2.
\]

It is a constant radial spin-two potential. This is distinct at the potential level from the compact harmonic quadrupole, T=4Co/(3b²), and uniform external shear proportional to b². The r^-1 radial behavior is known cubic-Galileon prior art, not a new exponent.

For a symmetric cutoff Z within the ideal r^-1 profile,

\[
A_0(b;Z)=A_d[2\operatorname{asinh}(Z/b)-3Z/\sqrt{Z^2+b^2}]
\sim A_d[2\ln(2Z/b)-3].
\]

The matched profile replaces the cutoff dependence by a fixed matching constant and subleading radial corrections. The leading axial -2Ad ln b is a point-mass potential and is mass-degenerate; the additive constant is invisible to delays and deflections. The deep approximation cannot be extended to infinite z in this axial integral. The exact matched T and A0, rather than an imposed cutoff, belong in numerical optics. Their first nonconstant terms can also be highly correlated with allowed shear or other radial nuisances.

## 4. Potential-space radial discrimination

For a calibrated spin-two potential amplitude

\[
p_2(b)=q+\mu b^{-2}+\gamma b^2,
\qquad D=b\partial_b,
\]

the algebraic identity (D²-4)p2=-4q removes precisely the compact harmonic quadrupole and constant external shear. At three distinct positive radii xi=bi² the design rows (1,xi^-1,xi) have determinant

\[
-\frac{(x_2-x_1)(x_3-x_1)(x_3-x_2)}{x_1x_2x_3}\ne0.
\]

Each real spin-two coefficient is identifiable from those calibrated potential samples. With two radii the two nuisance columns already span the whole sample space and q is unidentifiable. An explicit contrast is q=sum wi p2(bi), with

\[
w_i=-\frac{x_i(x_j+x_k)}{(x_i-x_j)(x_i-x_k)}.
\]

For covariance Sigma its variance is w^T Sigma w; near-coincident radii can make it unusably noisy. For the actual matched transfer replace the first column 1 by T(bi), and test that actual determinant and condition number. Angular coverage is also required to extract both spin components. These are representation-space statements about inferred potential coefficients, not a direct theorem about three image radii. Sparse image positions, fluxes and delays sample gradients, Hessians and potential differences with unknown source positions.

Arbitrary extended matter defeats this restricted separation: Delta_2[q cos2phi]=-4q cos2phi/b², so a distributed quadrupolar surface density proportional to cos2phi/b² can reproduce this constant spin-two potential on an annulus. A sufficiently positive monopole can make a small signed quadrupolar perturbation physically admissible. The filter therefore neither proves a modified-gravity origin nor excludes an extended envelope. Ordinary matter priors must be independently justified.

## 5. The scalar mass-estimator null is real

Use dimensionless point-lens reference potential ln r, source y=u e, s=sqrt(u²+4), radii a=(u+s)/2 and d=1/a, with images a e and -d e. Put h(u)=us/2+2 asinh(u/2). The known point-lens delay/flux mass estimator has the following first-order responses for a perturbation p=q(r) cos2(phi-phiq):

\[
\delta\ln M_{\rm app}=\cos2(\phi_s-\phi_q)\,\mathcal K_q(u),
\quad\mathcal K_1=\mathcal K_{r^2}=\frac{s^3}{u h(u)}.
\]

Thus (r²-1)cos2phi is an exact first-order null of this scalar estimator for every u>0. Deep-screened constant spin two and external shear cannot be separated by that statistic alone, even over arbitrarily many alignments if their angular coefficients and reference normalization match. Distinct projected radial powers are insufficient to claim observable discrimination.

For q=1 both image angles differ by pi and p+ equals p-, so the first-order delay correction is zero at fixed source. The first-order log flux-ratio correction is -4 cos2phi s/u and the estimator response comes entirely from flux. Tangential astrometry can see the orthogonal angular component that this scalar statistic misses. The result assumes nonsingular continued primary images and small perturbations away from u=0; it says nothing about total flux of any extra central images. The full-transfer radial dependence can yield a nonzero delay correction, but its nuisance-profiled response must be evaluated.

## 6. A precise geometry and observable-null proposition

At fixed observed positions theta_i, reference Jacobians Ai=I-Hpsi0(theta_i), and fixed time-delay prefactor, let a potential change be p and let the source shift freely by delta y. To preserve both image positions, it is necessary and sufficient at first order that

\[
\nabla p(\theta_+)=\nabla p(\theta_-)=-\delta y.
\]

This eliminates the unknown source without assuming its trajectory. Under this condition the remaining first-order tests are

\[
\delta\Delta\tau=(\theta_+-\theta_-)\cdot\delta y+p_+-p_-,
\]
\[
\delta\ln R=\operatorname{tr}(A_+^{-1}Hp_+)
-\operatorname{tr}(A_-^{-1}Hp_-).
\]

Their simultaneous zeros characterize the local null at fixed astrometric data for the declared parameters. Mass, center, convergence, source-redshift/time-distance variations and calibration parameters must be added to p or to the prefactor before taking a rank. In forward fixed-source differentiation, displaced image positions instead contribute the third-derivative/background-Hessian term; this term must not be dropped from the flux derivative. The fixed-data and fixed-source derivatives are different calculations.

For the particular difference p=(r²-1)cos2phi, direct Cartesian differentiation gives

\[
\nabla p(ae)-\nabla p(-de)=2s\cos2\phi_s\,e.
\]

It cannot be hidden by one unknown source vector when cos2phi_s is nonzero and the center is calibrated. A point-mass perturbation delta m ln r cancels the pair-gradient difference only for delta m=-2 cos2phi_s, but that changes Mapp by delta m. Hence pair geometry plus the scalar estimator distinguishes this particular difference when the time-distance conversion is fixed, mass is the only added compensator, and cos2phi_s is nonzero. Equivalently, the first variation of the geometric angular mass ag dg is zero for constant spin two and 2 cos2phi_s for r² spin two. Comparing that angular mass with a delay-derived physical mass requires the distance conversion.

At cos2phi_s=0 the difference is a genuine first-order joint null for a single freely positioned source: the gradients are equal, delta y is tangential, p+ equals p-=0, the delay change vanishes, and the flux-ratio change vanishes. Varying source angle, independently calibrated source structure, or other data can remove that special null. Adding free convergence, moving center, arbitrary source maps, unknown distance factors or further multipoles can restore broader degeneracies. The complete multi-epoch data Jacobian after profiling the declared nuisance family, and its singular values/noise weighting, are the relevant identifiability test. Potential-space rank alone is not sufficient.

## 7. Closest primary prior art and defensible novelty

Chu and Trodden, PRD87 024011 (2013), Sec.III.2.1 Eqs.(118)-(124), give the cubic static multipole equation and exact hypergeometric modes. Brito et al., PRD90 124035 (2014), Sec.VII Eq.(60), explicitly give outer r^(-l-1) and screened r^(-l/2) multipoles. Kobayashi and Takadera's 2026 EFT preprint, Appendix B, includes the same cubic r^-l/2 limit while studying different beyond-Horndeski behavior. Neither the multipole linearization nor its l=2 exponent can be claimed as new. [Chu–Trodden](https://arxiv.org/abs/1210.6651), [Brito et al.](https://arxiv.org/abs/1409.0886), [Kobayashi–Takadera](https://arxiv.org/abs/2607.09098).

Turyshev and Toth, PRD105 024022 (2022), derive the TT projection of general ordinary STF mass multipoles, with two projected parameters at each order. This is the directly relevant harmonic rank-two limit. Trotter, Winn and Hewitt (2000) already infer internal/external quadrupole structure with multipole-Taylor lens models. Bernstein and Nakajima, ApJ693 1508 (2009), derive shear/flexion multipole relations and internal/external mass-moment limitations. [Turyshev–Toth](https://doi.org/10.1103/PhysRevD.105.024022), [Trotter–Winn–Hewitt](https://arxiv.org/abs/astro-ph/0001022), [Bernstein–Nakajima](https://arxiv.org/abs/0807.1931).

Point-lens delay/flux inversion, astrometric compact-mass tracking, relative-motion delay drift and source-position degeneracy also have established antecedents: [Muñoz et al.](https://arxiv.org/abs/1605.00008), [Sahu et al.](https://arxiv.org/abs/2201.13296), [Van Tilburg et al.](https://arxiv.org/abs/1804.01991), [Dai–Lu](https://arxiv.org/abs/1706.06103), [Schneider–Sluse](https://arxiv.org/abs/1306.4675).

The possible contribution is the same-action, normalized worldtube-to-metric-to-photon transfer for this recovered rolling R1 state, together with its explicit projection nulls and an honest nuisance-profiled tracker calculation. The axial positivity proof and the estimator-versus-geometry distinction are useful specialized results. This directed priority search does not establish first-ever status. A paper confined to known exponents plus a freely prescribed amplitude would be substantially weaker than the user's requested breakthrough; publication strength depends on a reproducible full-transfer observable result that survives physically justified nuisance and calibration tests. No derived horizon relation or microscopic BHSM identification is supplied by these results.
