# Primary-literature audit and conditional geometrical opportunity

Prepared 2026-10-21. Internal AI-assisted research check, not independent peer review. Scope: the five requested papers, full-sky shear, scalar Berger spectra and source-position degeneracy. The search is directed rather than exhaustive; it cannot establish a first-ever claim.

## What is already established

**Equivalent lens and line-of-sight response.** Peter Schneider, *The cosmological lens equation and the equivalent single-plane gravitational lens*, MNRAS **292**, 673–678 (1997), DOI [10.1093/mnras/292.3.673](https://doi.org/10.1093/mnras/292.3.673), [author preprint](https://arxiv.org/abs/astro-ph/9706185). Main-lens plus tidal cosmological propagation can be represented by an equivalent single-plane lens. Therefore an added envelope potential cannot be counted separately when it represents that same response. A generic quadrupolar line-of-sight correction, or conversion of it to equivalent external shear, is not new.

**Closest lensing result.** Pierre Fleury, Julien Larena and Jean-Philippe Uzan, *Gravitational lenses in arbitrary space-times*, CQG **38**, 085002 (2021), DOI [10.1088/1361-6382/abea2d](https://doi.org/10.1088/1361-6382/abea2d), [full text](https://arxiv.org/html/2011.04440v4). Equations (11)–(14), in their affine-frequency convention and units c=1, give

\[
T(\theta,\beta)=\tfrac12(\theta-\beta)^T\mathcal T(\theta-\beta)
 -(1+z_d)\hat\psi(\omega_o\mathcal D_{od}\theta),\qquad
\mathcal T=\omega_o\mathcal D_{od}^{T}\mathcal D_{ds}^{-1}\mathcal D_{os},\quad \mathcal T^T=\mathcal T.
\]

Their Sections 3.5–3.6 already cover perturbed cosmological and anisotropic reference spacetimes. Section 3.5.4 discusses absorption into source position and a sufficiently flexible lens model. Thus linked incoming/outgoing Jacobi maps and timing responses are inherited formalism. A useful addition must calculate a constrained family of these maps from explicit new input, not claim a new general timing principle.

**Multi-plane freedom.** Peter Schneider, *Generalized multi-plane gravitational lensing: time delays, recursive lens equation, and the mass-sheet transformation*, A&A **624**, A54 (2019), DOI [10.1051/0004-6361/201424881](https://doi.org/10.1051/0004-6361/201424881), [full preprint](https://arxiv.org/html/1409.0015v1). The arXiv submission is from 2014; use 2019 for the journal reference. It treats distance matrices and generalized mass sheets with tidal matrices. Under its generalized transformation all image delays scale by the same parameter. Extra source redshifts or delay ratios do not automatically remove the allowed degeneracy.

**Effective action.** Cédric Deffayet, Oriol Pujolàs, Ignacy Sawicki and Alexander Vikman, *Imperfect Dark Energy from Kinetic Gravity Braiding*, JCAP **10** (2010) 026, DOI [10.1088/1475-7516/2010/10/026](https://doi.org/10.1088/1475-7516/2010/10/026), [full text](https://arxiv.org/html/1008.0048v2). Their convention is \(\mathcal L=K(\phi,X)+G(\phi,X)\Box\phi\), \(X=g^{\mu\nu}\partial_\mu\phi\partial_\nu\phi/2\). The kinetic mixing and imperfect stress tensor are established. Matching a recovered R1 action to this class does not derive its free functions or state from BHSM, and second-order equations alone do not guarantee stability on every background.

**Closed-universe perturbations.** Shingo Akama and Tsutomu Kobayashi, *General theory of cosmological perturbations in open and closed universes from the Horndeski action*, PRD **99**, 043522 (2019), DOI [10.1103/PhysRevD.99.043522](https://doi.org/10.1103/PhysRevD.99.043522), [full text](https://arxiv.org/html/1810.01863v1). Equations (46)–(48) yield

\[
S^{(2)}=\int dt\,d^3x\sqrt\gamma\,a^3
[\mathcal G_S\dot\zeta^2+\zeta\mathcal F_S(\mathcal D^2+3\mathcal K)\zeta/a^2],
\]

with spatial-operator-dependent coefficients involving \((\mathcal D^2+3\mathcal K)/(\mathcal D^2-(\mathcal G_T\Sigma/\Theta^2)\mathcal K)\). Their closed harmonic index begins at n=3, with eigenvalue \(\mathcal K(n^2-1)\); polynomial degree 2 has eigenvalue 8 and corresponds to their n=3. Their short-wave stability conditions do not establish stability of that finite mode. The derivation assumes isotropic constant-curvature slices: replacing the eigenvalue by a Berger value does not itself derive Horndeski perturbations on an anisotropic Berger cosmology.

**Full-sky angular rules.** P. G. Castro, A. F. Heavens and T. D. Kitching, *Weak lensing analysis in three dimensions*, PRD **72**, 023516 (2005), DOI [10.1103/PhysRevD.72.023516](https://doi.org/10.1103/PhysRevD.72.023516), [full text](https://arxiv.org/html/astro-ph/0503479v2). Their spin-harmonic relations include \(\gamma=\eth^2\psi/2\), \(\eth^2Y_{\ell m}=\sqrt{(\ell+2)!/(\ell-2)!}\,{}_2Y_{\ell m}\), and \(\bar\eth^2\eth^2=\nabla^2(\nabla^2+2)\). Monopoles/dipoles are shear-null and a quadrupole produces spin-two shear. None is a BHSM-specific discovery. Earlier full-sky tensor treatment: Albert Stebbins, [*Weak Lensing On the Celestial Sphere*](https://arxiv.org/abs/astro-ph/9609149) (1996 preprint).

**Source-position freedom.** Peter Schneider and Dominique Sluse, *Source-position transformation: an approximate invariance in strong gravitational lensing*, A&A **564**, A103 (2014), DOI [10.1051/0004-6361/201322106](https://doi.org/10.1051/0004-6361/201322106), [full text](https://arxiv.org/html/1306.4675v1). For an invertible source transformation \(\hat\beta=f(\beta)\), set \(\hat\alpha(\theta)=\theta-f[\theta-\alpha(\theta)]\). This preserves mapped image configurations, although a physical curl-free transformed deflection is exact only under additional conditions. The mass-sheet subcase \(f(\beta)=\lambda\beta\) rescales delays. Time-delay changes for broader transformations are studied by Wertz, Orthen and Schneider, [arXiv:1712.05033](https://arxiv.org/abs/1712.05033). A fixed-physical-source calculation must not be advertised as an invariant under arbitrary source remapping.

## Actual Berger input: established spectrum, not a new result

Michela Egidi, Katie Gittins, Georges Habib and Norbert Peyerimhoff, *Eigenvalue estimates for the magnetic Hodge Laplacian on differential forms*, J. Spectr. Theory **13**(4), 1297–1343 (2023 issue; online 2024), DOI [10.4171/JST/480](https://doi.org/10.4171/JST/480), [publisher PDF](https://ems.press/content/serial-article-files/47035?nt=1), Appendix A.3 and Table 1. For a Hopf fibre of relative length b and horizontal curvature normalization giving round unit S³, the positive scalar Laplacian has

\[
\lambda_{k,p}=k(k+2)+(b^{-2}-1)(2p-k)^2,
\qquad k\ge0,\quad0\le p\le k.
\]

An overall radius a supplies a factor a⁻². Thus degree 2 splits into fibre-neutral eigenvalue 8 (real dimension 3) and charged eigenvalue \(4+4b^{-2}\) (real dimension 6). The round limit b=1 restores ninefold degeneracy. This splitting is ordinary Berger spectral geometry. It is useful new input relative to the existing round calculation, but cannot itself establish a BHSM-specific light-transfer law.

## Independently derived conditional response opportunity

The following algebra is a proposed internal derivation, not a result attributed to those papers. It isolates a potentially useful consequence worth computing if the recovered action supports it.

Represent degree-2 real scalar modes by \(F_Q(x)=x^TQx\), \(Q=Q^T\), tr Q=0, on unit S³⊂R⁴. Choose observer e₀ and an orthogonal complex structure J defining the Hopf fibres, with \(Je_0=e_3\), \(Je_1=e_2\). Define

\[
P_0Q=\tfrac12(Q+J^TQJ),\qquad P_2Q=\tfrac12(Q-J^TQJ).
\]

These are orthogonal projectors of dimensions 3 and 6. The Hopf derivative acts as \(A(Q)=[Q,J]\) and \(A^2=-4P_2\), proving the two eigenvalues above directly in this finite space.

For round radial reference rays \(x(\chi,n)=e_0\cos\chi+n\sin\chi\), the angular quadrupole equals \(\sin^2\chi\,n^TR(Q)n\), where \(R(Q)\) is the tracefree spatial 3×3 block. R has rank 5, with kernel

\[
Q=\begin{pmatrix}a&v^T\\v&-aI_3/3\end{pmatrix}.
\]

Suppose the reduced scalar operator yields sector transfers u₀(η),u₂(η), with an explicitly declared scalar-to-Weyl coupling. At a source distance s, round Born shear then has a matrix-valued amplitude

\[
G_s=K_0(s)R(P_0Q)+K_2(s)R(P_2Q),
\]

where the K's are the evaluated line-of-sight integrals including coupling and temporal response. A shared spatial profile requires equal sector responses or a state restricted to one sector. For an illustrative canonical equation \(u_j''+A u_j'+(B+c_s^2\lambda_j)u_j=0\), a common nonzero u solving both equations requires \(c_s^2(\lambda_0-\lambda_2)u=0\); it is impossible on an interval with b≠1 and nonzero sound speed. This is only an example; use the actual recovered operator instead.

If two distances satisfy

\[
K_0(s_1)K_2(s_2)-K_2(s_1)K_0(s_2)\ne0,
\]

they separate \(R(P_0Q)\) and \(R(P_2Q)\). The stacked algebraic map has rank **8**, compared with rank 5 for a single common transfer. To prove the remaining kernel, on ker R above, write v=(x,y,z). Then

\[
R(P_0Q)=\begin{pmatrix}
-2a/9&0&-y/2\\
0&-2a/9&x/2\\
-y/2&x/2&4a/9
\end{pmatrix}.
\]

Its kernel is a=x=y=0, leaving \(Q=z(e_0e_3^T+e_3e_0^T)\): a Hopf-aligned observer dipole. This was checked by exact symbolic elimination. Rank 8 describes full angular shear fields with calibrated transfers; it is not a claim that two observed strong-lens image systems identify eight physical state coordinates.

**Required limits and risks.** A full Berger spacetime changes null rays, screen transport, redshift and background curvature at the same order as its squashing. The round-ray equation above is therefore a declared effective response model, not a complete expansion of Berger-spacetime lensing. If retained as a theorem, state that model explicitly. A physical manuscript must compute the missing effects or establish an approximation suppressing them. Kernel dimensions can also change when the metric/phase projection includes derivative terms or additional matter fields.

## Novelty judgment and manuscript wording

The strongest plausible advance is a computed coupling between **actual** Hopf-sector dynamics and distance-dependent optical response, including an exact visible/null-state classification and quantified failure of the common-profile approximation. The two ingredients individually are known: Berger spectra and general optical-transfer theory. Their conjunction needs concrete calculations, and a broader literature search before submission should test the claimed combination. It does not derive a unique microscopic action, amplitude, vacuum or boundary state.

A defensible result statement, if the calculations verify its premises, is:

> Under an explicitly specified Berger-spectral scalar response operator, common scalar-to-Weyl coupling and round Born optical projection, the degree-2 state separates into two Hopf sectors whose distinct distance kernels increase the algebraically shear-visible state dimension from five to eight. Relative to the general Jacobi/time-delay framework of Fleury, Larena and Uzan, the addition is a calculated finite-dimensional state restriction and null-space theorem for this specified effective model. BHSM motivates the geometric input; the complete microscopic-to-optical identification remains conditional.

This is narrower than a new BHSM gravitational law, but stronger and more checkable than reporting another supplied quadrupole with a familiar cos(2φ) shear or a single seeded delay number.
