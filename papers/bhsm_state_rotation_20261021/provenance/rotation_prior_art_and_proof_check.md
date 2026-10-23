# Rotation route: primary literature and independent proof check

Prepared 2026-10-21. Internal AI-assisted review. This is a directed originality/scope check, not independent peer review or an exhaustive literature search.

## Closest primary results

1. Asantha Cooray and Wayne Hu, *Second Order Corrections to Weak Lensing by Large-Scale Structure*, ApJ **574**, 19–23 (2002), DOI [10.1086/340892](https://doi.org/10.1086/340892), [full text](https://arxiv.org/html/astro-ph/0202411v1). They distinguish corrections from evaluating potentials on perturbed rays from lens–lens coupling; their Section 3.2 produces image rotation through ordered products of tidal Hessians. A smooth scalar field can therefore induce rotation beyond first order within ordinary gravity.

2. Christopher M. Hirata and Uroš Seljak, *Reconstruction of lensing from the cosmic microwave background polarization*, PRD **68**, 083002 (2003), DOI [10.1103/PhysRevD.68.083002](https://doi.org/10.1103/PhysRevD.68.083002), [full text](https://arxiv.org/html/astro-ph/0306354v1). Section IV, especially equations (47)–(49), contains ordered double-distance potential integrals and scalar-induced field rotation, including nonzero spatial curvature through sin_K and cot_K. Closed-background ordered rotation alone is therefore not a new result.

3. Ue-Li Pen and Shude Mao, *Rotation in gravitational lenses*, MNRAS **367**, 1543–1550 (2006), DOI [10.1111/j.1365-2966.2006.10056.x](https://doi.org/10.1111/j.1365-2966.2006.10056.x), [full preprint](https://arxiv.org/html/astro-ph/0506053v2). Equation (7) gives the two-plane Jacobian \(A=I-U_1-U_2+\beta_{12}U_2U_1\). Misaligned shear matrices generate its antisymmetric part; Section 3 discusses resolved quadruple-image inference. Their physical-source rotation language must be considered alongside the source-remapping freedom below; raw matrix antisymmetry is not by itself a source-independent diagnostic.

4. Giuseppe Fanizza, Enea Di Dio, Ruth Durrer and Giovanni Marozzi, *The gauge invariant cosmological Jacobi map from weak lensing at leading order*, JCAP **08** (2022) 052, DOI [10.1088/1475-7516/2022/08/052](https://doi.org/10.1088/1475-7516/2022/08/052), [preprint](https://arxiv.org/abs/2201.11552). The physical Jacobi map in a consistently transported screen is symmetric at first order, including general perturbation types. Rotation of a coordinate basis cannot be identified directly with observable image rotation.

5. **Especially close current result:** Matteo Magi, Francesca Lepori and Julian Adamek, *Perturbative and numerical study of nonlinear relativistic effects in weak lensing*, JCAP **08** (2026) 024, DOI [10.1088/1475-7516/2026/08/024](https://doi.org/10.1088/1475-7516/2026/08/024), [full text](https://arxiv.org/html/2603.24179v2). Section 3.2, equations (31)–(37), derives the second-order Jacobi solution from \(R^{(2)}D^{(0)}+R^{(1)}D^{(1)}\). It explicitly isolates rotation from nested first-order tidal products, gives the difference of plus/cross ordered integrals, and explains why the genuinely second-order symmetric tidal matrix does not supply the leading antisymmetric map. Their consistent Sachs-basis treatment also shows why shear B-modes cannot generally be equated with rotation. Consequently the general commutator mechanism and its independence from unknown second-order fields are already established.

6. Pierre Fleury, Julien Larena and Jean-Philippe Uzan, *Gravitational lenses in arbitrary space-times*, CQG **38**, 085002 (2021), DOI [10.1088/1361-6382/abea2d](https://doi.org/10.1088/1361-6382/abea2d), [full text](https://arxiv.org/html/2011.04440v4), equations (7), (11)–(14), gives a common-domain source/lens/observer Jacobi framework. Schneider's [1997 equivalent-lens construction](https://arxiv.org/abs/astro-ph/9706185) establishes the associated lens-representation freedom. These should be used to prevent a calibrated transfer coefficient from becoming an unsupported observable-identification claim.

## Independent proof: exactly what follows from first-order tides

Use a single exact null ray, an affine parameter λ and a parallel-transported orthonormal Sachs screen. Let

\[
D''=T D,\quad D(0)=0,\quad D'(0)=I,
\qquad T=t_0I+\epsilon T_1+\epsilon^2T_2+O(\epsilon^3),
\]

where every coefficient T_j is symmetric. Expand \(D=dI+\epsilon D_1+\epsilon^2D_2+\cdots\); the coefficient convention contains no factorials. Let G(b,a) be the scalar retarded Green function for \(\partial_b^2-t_0(b)\), with G(a,a)=0 and ∂_bG(a,a)=1. Then

\[
D_1(L)=\int_0^Lds\,G(L,s)d(s)T_1(s)
\]

is symmetric, and

\[
D_2(L)=\int_0^Lds\,G(L,s)\{d(s)T_2(s)+T_1(s)D_1(s)\}.
\]

Writing \(\operatorname{Asym}M=(M-M^T)/2\) gives

\[
\boxed{\operatorname{Asym}D_2(L)=\frac12\int_0^Lds\int_0^sdt\,
G(L,s)G(s,t)d(t)[T_1(s),T_1(t)].}
\]

Thus unknown symmetric second-order tidal terms do not contribute to this coefficient. Changes of the reference path and of the screen may be absorbed into T₂ only if T is expanded in the exact orthonormal parallel screen, consistently transported from a fixed observer screen. Computing coordinate Hessians on straight rays and calling them the complete physical screen is not that proof.

For a round closed conformal background of unit radius, \(t_0=-1\), \(d(s)=\sin s\), \(G(b,a)=\sin(b-a)\). The formula applies away from conjugate-point normalizations when converting D into a normalized map or angle. If λ has length units, D and G have length units, T has length⁻², and the double integral has length units as required.

For \(T_1=\tau I+fQ_++gQ_\times\), with \(Q_+=\operatorname{diag}(1,-1)\), \(Q_\times=\left(\begin{smallmatrix}0&1\\1&0\end{smallmatrix}\right)\),

\[
[T_1(s),T_1(t)]=(f(s)g(t)-g(s)f(t))[Q_+,Q_\times].
\]

One fixed shear matrix times one temporal function commutes at every pair of distances and gives zero leading smooth rotation. Independent histories can give nonzero rotation, but independence alone does not guarantee a nonzero integrated coefficient because cancellations are possible.

If \(f(s)=F(s)\cdot a\) and \(g(s)=F(s)\cdot b\) for the same six response functions, define

\[
\Omega_{ij}(L)=\int_0^Lds\int_0^sdt\,G(L,s)G(s,t)d(t)
[F_i(s)F_j(t)-F_j(s)F_i(t)].
\]

Then \(\Omega^T=-\Omega\), the oriented kernel is \(a^T\Omega b\), its rank is even, and every common-profile pair b∝a is null. This finite state-response matrix, evaluated from the declared R1 dynamics and normalization, is the plausible model-specific computational addition. A Euclidean singular-value bound on it is a coordinate bound; call it a physical energy bound only after deriving the positive physical state metric.

### Exact synthetic algebra check

For t₀=0 and \(T_1(s)=sQ_++s^2Q_\times\), exact symbolic integration gives

\[
D_1(L)=L^4Q_+/12+L^5Q_\times/20,
\]

\[
D_2(L)=\left(L^7/504+L^9/1440\right)I
+\frac{L^8}{1680}\begin{pmatrix}0&-1\\1&0\end{pmatrix}.
\]

The ordered scalar integral is −L⁸/1680 and the boxed commutator formula reproduces this antisymmetric part exactly. This is an algebra check in dimensionless test coordinates, not an R1 prediction. Arbitrary T₂ adds a symmetric contribution and leaves this check unchanged.

### Twist, redshift and screen conditions

The conserved Wronskian is \(D^TD'-D'^TD=0\). Hence, where D is invertible, \(D'D^{-1}\) is symmetric: the congruence is twist-free even when D itself has a nonzero antisymmetric part. Do not call the latter a nonzero Sachs twist.

At fixed observed redshift, a shifted endpoint \(L=L_0+\epsilon\delta L_1+\epsilon^2\delta L_2\) adds \(\delta L_1D_1'\), \(\delta L_2d'I\) and \((\delta L_1)^2d''I/2\) at second order, all symmetric. Scalar normalizations likewise do not alter the leading antisymmetric coefficient. An independent rotation of the source endpoint screen does change matrix components; a physical rotation statement must specify the transported source/observer reference or an independently calibrated source orientation.

With a nonperturbative strong lens in the baseline, D₀ is anisotropic. Then \(\operatorname{Asym}(T_2D_0)\) need not vanish. The boxed independence from second-order tides is a statement about smooth propagation on an isotropic baseline, not a proof that the full second-order strong-lens map is known. The leading strong-lens × weak-envelope term of order ε can nevertheless be calculated from the first-order envelope and the fixed local lens.

## Essential observability restriction: common transfers can be symmetrized

Suppress convention-dependent scalar redshift factors by incorporating them consistently in the deflection potential. For physical lens Hessian U_i at image i, the source-plane derivative is

\[
A_i=D_{os}-D_{ls}U_iD_{ol}.
\]

Assume the three Jacobi matrices are common across the image system and are nonsingular where inverted. Define the single common source remapping

\[
B=D_{ol}^TD_{ls}^{-1}.
\]

Then

\[
BA_i=\underbrace{D_{ol}^TD_{ls}^{-1}D_{os}}_{\text{symmetric by reciprocity}}
-D_{ol}^TU_iD_{ol},
\]

which is symmetric for **all** images. Therefore raw image-dependent antisymmetric Jacobians induced by a common tidal environment can still be represented by a potential lens after a common affine source remapping. This is consistent with the equivalent-lens formalism. It is not enough to show that A_i differs from A_iᵀ or that its apparent polar angle differs among images.

An elementary exact check uses \(A_i=I-U_i-V+\beta VU_i\), where V is the same symmetric weak screen at every image. With \(B=(I-\beta V)^{-1}\),

\[
BA_i=(I-\beta V)^{-1}(I-V)-U_i,
\]

and the first term is symmetric because both factors are functions of V. This explicitly retains the weak-screen terms whose omission can obscure a source-remapping cancellation.

An observable claim therefore needs independent restrictions on source shape/orientation, local lens, or environmental transfers, or genuinely ray-dependent transfers across the multiple images. A low angular degree cosmological field varies little over arcsecond image separations; quantify that differential effect before suggesting that it supplies a strong-lens source-independent rotation test.

## Recommended claim and skeptical verdict

The new computation can evaluate an antisymmetric six-state response kernel, classify common-profile null directions, and propagate its independent histories through a fixed physical-source/fixed-lens experiment. This explains a real limitation of the former separable seed. It may be a useful conditional theoretical/computational paper if those calculations are substantial and reproducible.

It does **not** introduce scalar-induced rotation, path-order coupling, curved-background double-distance kernels or independence from unknown second-order tidal fields. All have close existing primary results, including the directly overlapping 2026 Jacobi-map calculation. It also does not uniquely select the environmental state or eliminate the equivalent-lens/source-position freedoms. The manuscript must call its addition the evaluated R1 response family and state-space classification, and identify the microscopic BHSM-to-optical map as unresolved unless recovery has supplied it.
