# Literature and claim review for a new BHSM angular-lensing paper

Date: 21 October 2026. This is a new theoretical and computational paper. The HE 0435 photometry, image calibration, detector repairs and their failure chronology are outside this paper's evidentiary basis. Relevant inherited ingredients are the declared effective action, its six-state temporal response, the closed-background geometry, and the physical angle-to-separation convention.

## Recommended title and scientific question

**Angular selection rules and linked shear--time-delay responses in a Berger--Hopf cosmological realization**

A shorter alternative is **Quadrupolar light transfer and time delays in the Berger--Hopf framework**. The abstract must make explicit that the calculation is an effective, conditional realization. A title promising microscopic BHSM closure, an observed signal, or a unique reconstruction would not describe the present task.

The scientific question is: given one specified spatial and environmental preparation in the retained closed cosmology, which angular optical responses follow, and how does that same preparation constrain strong-lensing time delays? Recovery of an ordinary effective gravitational description is a constructive correspondence result. A departure from general relativity is not a prerequisite for this calculation's value.

## Primary literature and the novelty boundary

1. **Lindblom, Taylor and Zhang (2017), scalar/vector/tensor harmonics on the three-sphere.** This supplies the standard harmonic setting and numerical identities. The n=2 scalar eigenspace, its nine-dimensional degeneracy and decomposition into angular ell=0,1,2 sectors are mathematical infrastructure, not a novel BHSM result. Primary article: https://doi.org/10.1007/s10714-017-2303-y ; preprint: https://arxiv.org/abs/1709.08020 . The official publisher identifies volume 49, article 139. An author-hosted PDF has conflicting article-number/DOI metadata; use the official publisher and arXiv identifiers in the bibliography.

2. **Bernardeau, Bonvin and Vernizzi (2010), full-sky shear.** First-order scalar shear is a spin-two response, while higher-order lens--lens, deflection and redshift couplings are distinct terms. The vanishing tracefree angular Hessian of ell=0,1 is standard geometry. The paper's contribution can be its explicit application to the retained BHSM mode family and the action-derived temporal coefficients. Primary full text: https://arxiv.org/html/0911.2244v2 . Relevant first-order equations are (39)--(45); the curved-background check is in section 4.2.1.

3. **Schneider (2019), generalized multi-plane theory.** Distance matrices, Fermat propagation and the generalized mass-sheet transformation already exist. In particular, all delays can scale together under the generalized transformation, so ratios do not automatically remove it. Primary full text: https://arxiv.org/html/1409.0015v1 ; published DOI: https://doi.org/10.1051/0004-6361/201424881 .

4. **Fleury, Larena and Uzan (2021), arbitrary-space-time lenses.** The exact three-map time-delay matrix and its symmetry are established, with physical frame/redshift normalizations. Their notation for Jacobi maps uses vertex frequency factors differently from physical angle-to-separation maps; convert explicitly. Primary full text: https://arxiv.org/html/2011.04440v4 . Equations (11)--(14), section 3.5 and Appendix B are particularly relevant.

5. **Schneider and Sluse (2014), source-position transformations.** Permitted changes to the source and lens can preserve the same optical observables. Computing a nonzero background shear or timing derivative does not establish observational identifiability. Primary preprint: https://arxiv.org/abs/1306.4675 ; published DOI: https://doi.org/10.1051/0004-6361/201322106 .

The plausible new contribution is the reproducible composition of the retained six-state BHSM/R1 dynamics with the full n=2 angular geometry, the resulting redshift-dependent coefficients, and a linked shear--delay prediction for an explicitly stated preparation. The angular identities and generic Fermat machinery should be derived for transparency and credited as established tools. A literature search does not certify that the final application is unprecedented.

## Independent time-delay derivation

### Map and clock conventions

Let D_ab map a unit physical angle at event a to a transverse physical separation at b. Express all maps in compatible parallel screen bases and fix the measured lens redshift z_l. With a transverse physical source position X_s,

    beta = D_os^{-1} X_s,
    T = (1+z_l) D_ol^T D_ls^{-1} D_os.

The corresponding single thin-lens arrival-time function, in length units, is

    c t(theta) = 1/2 (theta-beta)^T T (theta-beta)
                 - (1+z_l) psi_hat(D_ol theta) + f(beta).

Here grad psi_hat = alpha_hat is the physical lens-frame deflection. The source-only function f cancels between images. The local physical potential and the source preparation must be declared when differentiating. The time-delay matrix is symmetric for compatible physical maps; arbitrary input matrices need not satisfy the geometrical constraints.

### First variation of the delay matrix

Around an isotropic background write

    D_ab = d_ab (I + E_ab) + O(q^2),
    T0 = (1+z_l) d_ol d_os/d_ls.

Direct differentiation gives

    delta T/T0 = E_ol^T - E_ls + E_os.

This identity is valid at fixed measured z_l. If the chosen comparison changes z_l, its clock variation must be added. For symmetric first-order maps,

    (delta T/T0)_TF = E_ol,TF - E_ls,TF + E_os,TF.

With the usual convention D_ab=d_ab[(1-kappa_ab)I-Gamma_ab], the tracefree result is

    (delta T/T0)_TF = -Gamma_ol + Gamma_ls - Gamma_os.

This is an algebraic consistency identity, not an additional independent data point and not a new BHSM theorem.

### The delay matrix alone is not the full time-delay prediction

At a stationary unperturbed image theta_i, put v_i=theta_i-beta. Fermat stationarity eliminates the first-order image-position variation from the variation of the arrival value. Keeping X_s and the physical lens potential fixed gives

    delta beta = -E_os beta,
    c delta t_i = 1/2 v_i^T delta T v_i
                 - v_i^T T0 delta beta
                 - (1+z_l) alpha_hat_i^T delta D_ol theta_i
                 + delta f.

The last physical-impact term must be retained. Using the background lens equation alpha_hat_i=(d_os/d_ls)v_i, the symmetric-map expression simplifies to

    c delta t_i/T0
       = 1/2 v_i^T(E_os-E_ol-E_ls)v_i
         + v_i^T(E_os-E_ol)beta + delta f/T0.

Subtract this expression between images. The formula requires noncaustic branches so that the stationary images vary smoothly. It does not assume that image shifts themselves vanish.

## A tractable nonzero timing example: the nodal quadrupole

Choose the fixed normalized spatial quadrupole tensor

    C = diag(1,-1,0)/sqrt(2),
    n = (0,0,1),
    Q_C = N sin^2(chi/R) n^T C n.

The central ray is along the zero eigenvector of C. On that ray Q_C and all its first derivatives vanish. The screen Hessian has zero trace and nonzero tracefree part. Consequently the first-order smooth perturbation does not shift the central ray's frequency, radial path or fixed-redshift endpoints, while the tidal beam deformation survives. Observer velocity corrections from this scalar profile also vanish at the origin. This is a designed conditional preparation, not a claim that an observed sightline occupies such a node.

Write H_C=sqrt(2) diag(1,-1) in the chosen screen and

    E_ab = -[g_ab dot y] H_C,

where y is the common six-component physical initial state and g_ab its action-derived response row. A generic sightline outside this nodal setting can have additional trace/frequency terms; those must not be silently omitted.

For a singular isothermal sphere with fixed physical deflection strength b, fix X_s=s e and use the noncaustic two-image branch. On the background

    theta_E = b d_ls/d_os,
    beta = (s/d_os)e,
    v_+ = theta_E e,  v_- = -theta_E e,
    Delta t_(minus-plus) = 2 T0 theta_E |beta|/c.

The quadratic terms in the stationary-image first variation cancel between these two images. The positive relative delay therefore obeys

    delta ln Delta t = e^T(E_ol-E_os)e
                     = [(g_os-g_ol) dot y] e^T H_C e.

For e=(cos alpha,sin alpha),

    delta ln Delta t
       = sqrt(2) [(g_os-g_ol) dot y] cos(2 alpha).

The lens-to-source coefficient cancels in this particular fixed-physical-source SIS comparison. The cancellation is not a general statement about arbitrary lenses, angular-source-fixed comparisons or multiple planes. For sources on either principal axis, the exact diagonal-map SIS expression is proportional to D_ol,axis/D_os,axis, providing an independent sign and normalization check. For a rotated source, numerical solutions of the matrix lens equation should recover the first variation as the amplitude tends to zero.

This result is a conditional timing prediction. A numerical value per unit state is a response coefficient. An illustrative finite amplitude should be labeled as specified, with its metric perturbation size and truncation error reported; it is not an inferred physical amplitude.

## Exact effective-potential correspondence for one source plane

The propagation response has an exact conventional representation within the single-plane, constant-Jacobi-map approximation. This is constructive correspondence, consistent with the BHSM interpretation of the same underlying surface contributions.

Choose a scalar reference T0>0 and let M=T/T0. For the symmetric physical time-delay matrix, define

    beta_eff = M beta,
    psi_eff(theta) = [(1+z_l)/T0] psi_hat(D_ol theta)
                     + 1/2 theta^T(I-M)theta.

Expanding the ordinary-form Fermat function gives

    1/2 |theta-beta_eff|^2 - psi_eff(theta)
      = 1/2 theta^T M theta - theta^T M beta
        + 1/2 beta^T M^2 beta - [(1+z_l)/T0]psi_hat(D_ol theta).

Consequently

    c t(theta)/T0
      = 1/2 |theta-beta_eff|^2 - psi_eff(theta)
        + 1/2 beta^T(M-M^2)beta + f(beta)/T0.

The final two terms are source-only constants. The image stationarity equations and relative arrival times therefore agree exactly between the two representations. No separate metric response is to be added again after this absorption.

The effective deflection is

    grad psi_eff = [(1+z_l)/T0] D_ol^T alpha_hat(D_ol theta)
                   + (I-M)theta.

For a local SIS, psi_hat(x)=b|x|, the first term in psi_eff is an elliptical potential when D_ol is anisotropic. The quadratic term supplies the ordinary uniform-convergence and shear contributions. In the nodal quadrupole example the linear correction is tracefree, so its quadratic term is shear at first order. A finite-amplitude matrix completion can also produce higher-order isotropic terms; those are properties of the chosen completion and should not be presented as an action-derived second-order metric result.

This identity does not prove that every resulting effective potential satisfies all global nonnegative-density, finite-mass, dynamical or environmental constraints. The norm term for a nonsingular SIS map is convex and has nonnegative two-dimensional Laplacian away from its singular center, but the added uniform-convergence term can have either sign. External physical constraints can therefore restrict the allowed equivalence class. It also does not guarantee that a single shared effective physical mass distribution reproduces all source redshifts or all dynamical observations; each must be included explicitly.

Within its scope, the identity shows why full image and delay agreement alone need not identify the BHSM preparation if the conventional lens potential and source position remain sufficiently free. It is not a failure of the BHSM forward calculation. The positive result is that its calculated response can be represented in the familiar lens variables, with the cross-redshift and cross-observable restrictions then supplied by the common physical state.

### A restricted source-redshift contrast

For sources s and t behind the same main lens, use the same D_ol, screen frame, physical lens potential, small angular patch and background distance prescription. Define

    p_s = d_ls/d_os,
    T0_s = (1+z_l) d_ol/p_s,
    a_s = (1+z_l)/T0_s = p_s/d_ol,
    B_s = I-M_s.

The exact effective potential is

    psi_eff,s(theta) = a_s psi_hat(D_ol theta) + 1/2 theta^T B_s theta.

A single additional physical quadratic deflector at the main lens would have

    delta psi_hat(x) = 1/2 x^T A_lens x,

with the same symmetric A_lens for all sources. It absorbs the propagation quadratic term if and only if

    B_s/a_s = D_ol^T A_lens D_ol

is independent of source redshift. Because D_ol is common and nonsingular, this is equivalent to B_s/p_s being source-independent. At first order about the isotropic background it reads B_s=p_s d_ol A_lens.

For the nodal quadrupole,

    B_s = [(g_ol-g_ls+g_os) dot y] H_C + O(y^2).

The matrix contrast

    R_st = B_s/p_s - B_t/p_t

therefore vanishes for a single fixed physical quadratic term at the main plane but can be nonzero for the distributed mode. Its common-profile scalar coefficient is

    r_st = [(g_ol-g_ls+g_os)/p_s
            -(g_ol-g_lt+g_ot)/p_t] dot y.

The first-order tracefree contrast is the appropriate quantity if only tracefree propagation has been calculated. It must not be called a constraint on an uncomputed generic convergence response.

This is an exact absorption criterion and a conditional decomposition-level prediction. The reduced quadratic coefficients B_s are not directly measured from raw images. Source structure, lens shape and distance uncertainties enter their inference. A nonzero R_st excludes only absorption into the stated one-plane quadratic term; it does not exclude a conventional distributed/multi-plane gravitational representation, arbitrary nonquadratic mass adjustments, source-position transformations, or a generalized mass-sheet construction. No independent amplitudes may be assigned to s and t when computing the shared-state contrast.

The distinction between physical and source-dependent reduced lens strengths, and the redshift dependence of distributed tidal perturbations, are established lensing physics. The paper-specific content would be the evaluated r_st supplied by the retained BHSM/R1 temporal state and spatial mode, plus its explicit relation to the other optical response rows.

## Shared spatial profile and what its alignment implies

For one common real quadrupolar shape C and six temporal initial amplitudes y, each map has

    Gamma_ab(n) = [g_ab dot y] H_C(n).

Thus, at the same line of sight and in a common screen, the two shear components of the three propagation maps are collinear. Every pairwise determinant of their two-component shear vectors vanishes. The tracefree time-delay matrix has that same screen tensor. A coefficient may change sign, interchanging the stretching/compression axes; this is still collinearity, not a universal positive ratio.

This statement does not require the temporal state to be two-dimensional. It does require one spatial shape shared by the six initial coordinates throughout their coupled evolution. With general independent quadrupole tensors C_j for the six temporal coordinates, Gamma_ab is a sum over j and collinearity need not hold. With the entire n=2 sector there are six temporal amplitudes for each of nine spatial harmonics. The isotropic dynamics act identically on the harmonic labels, but do not choose their values or a preferred axis.

The amplitude-independent collinearity is a deterministic structural prediction of the restricted common-profile realization. It is not a statement that all observed image ellipticities align, since the strong lens, intrinsic source, measurement response and other line-of-sight structure contribute. Nor does it imply a rank-one stochastic covariance for arbitrary local noise along a path.

## Identifiability and a concrete observation design

In a local response calculation let

    delta O = B q + N eta + epsilon,
    W^T W = C^{-1},
    B_perp = (I-P_WN) W B,

where q contains the specified physical state coordinates, eta includes the permitted lens/source/environment nuisance parameters, and P_WN projects onto the columns of WN. Only rank(B_perp) counts the locally identifiable state directions in this observable set. This linear criterion is a local diagnostic; nonlinear searches, boundaries and estimated covariance need their own calibration.

The present SIS derivative holds the physical lens and source preparation fixed. It establishes a forward response. If the source scale, lens strength, external convergence/shear or cosmological distance scale are allowed to vary in an observational inference, some or all of that response may be absorbed. Do not convert the forward derivative into a detection forecast without applying the corresponding nuisance analysis.

A concrete future test should freeze one of the following fully specified designs:

1. A lens with independent constraints on its mass structure and environment, with a declared source model and multiple timing/image constraints.
2. Several sources or lenses for which a physically justified common state and independently constrained nuisance model predict a linked redshift/angular response.
3. A joint geometrical/dynamical observation set that constrains the same state through a second physically derived response.

Multiple source redshifts or delay ratios alone are not a guarantee. Under generalized mass-sheet transformations, the delays can all acquire the same scale factor. Likewise, assigning a new independently chosen state to every measurement removes the claimed shared-state restriction.

The first numerical paper can present the forward response and a clearly separated identifiability calculation without claiming that a suitable real-data inference has already been performed. This is a complete conditional theory calculation if its preparation, approximation and error controls are explicit.

## Suggested article structure

1. Introduction: envelope/environment-to-light-transfer question, strong-lensing relevance, existing theory and the precise contribution.
2. Declared effective realization: action, background, six physical initial coordinates, normalization and scope of the microscopic correspondence.
3. Full n=2 angular geometry: STF embedding representation, 1+3+5 decomposition, screen Hessian and selection rules.
4. Optical transfer: three map kernels, reciprocity, fixed-redshift treatment, generic tracefree results and nodal-ray simplification.
5. Shared-state relations: common-profile collinearity, delay tensor, full stationary-image variation and the SIS nodal benchmark.
6. Computation: actual action-derived kernel values, numerical refinement and independent analytic/numerical comparisons. Populate only with executed results.
7. Interpretation and identifiability: what the fixed-preparation calculation predicts, what nuisance freedom can absorb, and the observational requirements.
8. Conclusion: completed conditional results and the specific remaining physical/observational tasks.

## Executed independent geometry audit

`review/check_geometry_identities.py` imports no BHSM temporal provider or new optical-kernel implementation. It solves the two-image SIS lens equation directly for five source orientations in a commuting anisotropic matrix family, then differentiates the arrival values with a four-point formula. The largest error relative to the analytic fractional-delay derivative is 2.691e-12; the largest dimensionless lens-equation residual is 1.058e-15. It also evaluates the original and effective-potential Fermat functions and gradients at nonstationary positions. The largest differences, scaled by the Einstein angle squared and the Einstein angle respectively, are 2.532e-16 and 1.690e-16. The full receipt is `review/geometry_identity_audit.json`.

This verifies the calculus and exact representation identities. The input matrix coefficients are chosen numerical controls, not the BHSM temporal response, so these numbers are neither cosmological predictions nor physical-validation statistics. The actual action-derived optical coefficients must be tested separately.

## Claim checks for the final manuscript

- Do not call the full n=2 sector a two-parameter cosmology.
- Distinguish scalar-harmonic degree n=2 on S3 from angular ell=2 on the observer's S2.
- Do not call dipole shear absence a proof of zero full strong-lensing response.
- Do not treat shear-only kernels as generic complete distance maps.
- Do not call the time-delay tensor perturbation a total arrival-time prediction without the physical-source and impact terms.
- Do not promote an exact conditional consistency relation to an observed relation.
- Do not identify ordinary effective-gravity agreement as failure.
- Do not equate code tests or integration convergence with empirical validation.
- Preserve the state/source normalization qualification, without importing unrelated detector or muon work into the new paper.
- Cite the standard harmonic, Sachs and Fermat machinery. Attribute the new work to the specified BHSM/R1 realization and its executed response composition.
