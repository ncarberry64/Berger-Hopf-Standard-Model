# Final theory consistency review

Reviewed `manuscript/main.tex`, `manuscript/angular_transfer_section.tex`, and `manuscript/action_provider_appendix.tex` against the finite action in `code/vendor_original/code/action_native_matter_n2.py`, its background and closed-Horndeski providers, and the previously checked harmonic and stationary-image identities.

## Outcome

**No algebraic or theoretical blocker was identified within the explicitly declared conditional R1, first-order smooth-field, paraxial thin-lens experiment.** The manuscript now distinguishes that calculation from a unique microscopic BHSM preparation, a nonlinear finite-body solution, an exact finite-angle calculation, or observational validation. The numerical timing law does not need to change as a result of this review.

The action-derived description is warranted in a qualified sense: the temporal responses are obtained from the declared conditional effective action and its specified finite quadratic reduction, rather than assigned phenomenologically as independent optical coefficients. It does not follow that the effective action, its normalization, or the initial state has been uniquely derived from microscopic BHSM. The main text and appendix state this distinction explicitly.

## 1. Finite action and temporal dynamics

The appendix polynomial matches every term of the vendored `unreduced_lagrangian`. In particular, the gravitational terms contain the same lapse coefficient Sigma, lapse-shift coefficient 2 b2 Theta, shift-square coefficient -b2 kappa, mixed kinetic terms, and curvature coefficient s2. The fluid polynomials produce the same auxiliary, derivative, and density blocks, including the zero dust sound speed.

The displayed Schur reduction has the correct signs:

\[
M=M_0-B^TA^{-1}B,\qquad L=-B^TA^{-1}D,\qquad
V_2=E-D^TA^{-1}D.
\]

The canonical momentum and equations are consistent with the reduced Lagrangian, including the time-dependent background through the momentum definition. The full six-dimensional fundamental matrix is retained. The reference momentum Pi_2,ref is explicitly distinguished from the coupled canonical momentum, avoiding an incorrect identification with the old two-coordinate gravity-scalar subsystem.

The Newtonian reconstruction is consistent with the stated covariant ADM shift and uniform-field convention: Phi = alpha + dot(chi), Psi = -zeta - H chi. The derivative includes both row evolution and state evolution, as required. This review checks the finite reduction against its implementation; it is not an independent derivation of the full microscopic theory or a general stability proof.

## 2. Harmonic counting and normalization

The degree-two real scalar eigenspace on S3 has dimension nine. Representing it by a symmetric tracefree 4 by 4 matrix gives the stated 1 + 3 + 5 decomposition about the observer. The normalization

\[
\mathcal N=\sqrt{6/(\pi^2R^3)},\qquad
\int Q_AQ_B\,dV=\operatorname{Tr}(AB)
\]

follows from the S3 fourth moment and is consistent with the finite action's unit harmonic normalization.

Six independent initial coordinates for each of the nine real harmonics give 54 retained coefficients. The smooth first-order shear annihilates the four monopole/dipole directions for every temporal coordinate, leaving at most 30 quadrupole coefficients. A common spatial quadrupole shared by all six state coordinates is an additional preparation restriction; the manuscript correctly does not impose it on the generic 54-coordinate family. Deterministic alignment is correctly distinguished from a stochastic covariance model.

All field lengths and normalized harmonic coefficients use the same c/H0 coordinate unit. The numerical density seed is a coefficient multiplying a normalized nonconstant spatial harmonic, not a uniform fractional density change. Changing normalization would require transforming the seed and response row together; no normalization-free physical amplitude is claimed.

## 3. Jacobi maps and the nodal ray

The screen Hessian and Green kernel are consistent with linearized curvature propagation. Each of the observer-lens, observer-source, and lens-source maps has its own vertex initialization. The physical lens-source normalization is a_s S_K(chi_s-chi_l); no additional a_l factor or redshift multiplier belongs in the fractional-shear kernel.

The common parallel-transported screen and nonconjugate domain are now explicit. First-order scalar Jacobi perturbations in this screen are symmetric, justifying the use of E_ol rather than E_ol transposed in the displayed first variation. In arbitrary independently chosen screens, the unsimplified identity would be

\[
\delta T/T_0=E_{ol}^T-E_{ls}+E_{os}.
\]

For C = diag(1,-1,0)/sqrt(2) and n = z, the harmonic and its full first gradient vanish along the fiducial ray, while the transverse Hessian is nonzero and tracefree. Therefore the first-order central frequency, radial-event, velocity, local-scale, and trace perturbations vanish. The remaining tracefree perturbations supply the full infinitesimal Jacobi maps of that nodal preparation.

The manuscript correctly limits this statement to the fiducial ray and the retained paraxial construction. Actual finite-angle images leave the nodal line. Their leading tidal separation is included by the distance matrices; higher finite-angle terms are neither computed nor bounded. A generic direction still needs the uncomputed trace and endpoint terms for a complete timing response.

## 4. Fixed physical source, local body, and timing

The stationary-image derivative includes all three required changes: the time-delay matrix, the angular source beta = D_os^{-1} X_s, and the local physical impact D_ol theta. Omitting either of the latter two terms would give a different and incorrect derivative for the declared experiment.

For the fixed physical SIS strength b and physical source displacement s, the two continued noncritical branches have v_plus/minus = plus/minus theta_E e. The quadratic stationary variation cancels in their relative delay, leaving

\[
\frac{\delta\Delta t}{\Delta t_0}
=e^T(\Gamma_{os}-\Gamma_{ol})e
=\sqrt2[(g_{os}-g_{ol})\cdot y]\cos(2\varphi).
\]

The lens-source shear cancellation is specific to this source/body comparison. It is not a generic lens theorem or a fixed-angular-source result. The stated SIS is a prescribed local weak-field encounter capable of multiple imaging; no global finite-mass galaxy construction or environmental structural reaction is solved. The reference measured redshifts and common clock normalization are held fixed; image-specific endpoint retuning is not part of the experiment.

The finite-map image calculations check this derivative. They do not supply second-order cosmological dynamics. The manuscript now correctly excludes a physical interpretation of tiny completed residuals at the first-order 45-degree null, and distinguishes rotating the declared source configuration from temporal evolution of an observed source.

## 5. Two small clarity edits recommended before finalizing

These do not change the calculation and do not constitute unresolved scientific blockers.

1. **Distinguish the dimensional cubic scale from its code value.** The main action writes its cubic denominator as lambda while the appendix defines the dimensionless code lambda = Lambda^3/(M_Pl H0^2). To avoid one symbol carrying two dimensional meanings, write the dimensional main-action denominator as Lambda^3 and state that the numerical values use lambda = Lambda^3/(M_Pl H0^2) = 1 and q_T = mu^3/(M_Pl H0^2) = 3. Alternatively, declare the entire main action to be in the appendix's dimensionless code variables and remove its isolated dimensional M_Pl factor. The appendix's rescaling itself is correct.

2. **Name the angular phase explicitly.** In the interpretation paragraph, replace “A state-dependent phase, a timing amplitude and a shear pattern” with “The angular orientation of the quadrupole, its timing amplitude and its shear pattern.” The computed phase is the orientation of the cosine-of-twice-angle law. No separate electromagnetic phase or additional topographic-to-phase coupling has been calculated.

The phrase “action-derived temporal propagator” may remain, because the surrounding text consistently restricts it to the declared conditional R1 effective action. Adding “conditional R1” directly before it in the abstract would make the scope even easier to read, but is not required to repair an error.
