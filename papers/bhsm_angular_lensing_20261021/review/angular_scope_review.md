# Analytic scope review of the standalone angular-lensing section

Reviewed: `theory/angular_transfer_section.tex`, together with the original angular-geodesic audit and the fixed-physical-source SIS implementation.

## Outcome

No algebraic correction to the normalized harmonic family, shear kernel, physical vertex normalization, stationary Fermat derivative, or nodal SIS timing law was identified. The claimed timing derivative is consistent with the declared first-order smooth scalar geometry, a weak-field thin lens capable of multiple imaging, and the paraxial distance-matrix approximation. The conditions below should appear explicitly in the standalone manuscript so that its use of “complete conditional timing response” cannot be read as an exact finite-angle or nonlinear cosmological result.

Three small wording additions are recommended; no change to the numerical prediction follows from them. This review does not edit the root manuscript or the theory section.

## 1. Use one transported screen and a nonconjugate domain

The displayed linear matrix identity omits a transpose on E_ol because the first-order scalar Jacobi perturbations are symmetric in the common parallel-transported screen. In arbitrary independent screen bases that simplification would not be justified. The more general first variation is

    delta T / T0 = E_ol^T - E_ls + E_os.

All background vertex pairs must also avoid conjugate points so that S_K(chi_b-chi_a) and the required distance maps are nonzero/invertible. The numerical redshift range is well inside the first closed-space conjugate point.

Suggested addition before the matrix expansion:

> All maps use one parallel-transported screen. We restrict to nonconjugate background vertex pairs and sufficiently small perturbations; the first-order scalar map perturbations in this screen are symmetric.

The original kernel's lens-to-source normalization is correct: D_ls'=omega_l I in the observer-normalized physical affine parameter becomes a unit initial conformal derivative. Its physical background length is a_s S_K(chi_s-chi_l), with no extra lens scale factor or Doppler multiplier.

## 2. The nodal statement concerns the fiducial ray

For C=diag(1,-1,0)/sqrt(2) and the central direction z, Q and all its first derivatives vanish along the fiducial ray. Its transverse Hessian is tracefree. Thus the first-order frequency, radial-event, matter-velocity, local-scale and Jacobi-trace perturbations along that reference ray vanish, while its infinitesimal-beam shear is nonzero.

The statement must not be extended to every finite-angle image trajectory. The actual lensed rays leave the nodal line. Their leading displacement through the smooth tidal field is precisely what the distance-matrix encounter includes. Nonlinear dependence on transverse separation, finite-angle corrections and higher-order smooth perturbations are outside the calculation; they have not been bounded by the present tests.

Suggested replacement:

> Along this fiducial ray, the first-order frequency, radial-event, velocity, local-scale and Jacobi-trace responses vanish. The infinitesimal physical Jacobi maps are therefore fully specified by their tracefree perturbations for this preparation, within the adopted paraxial approximation.

Fixed measured redshifts specify the reference lens/source events and their clock normalization. The calculation does not separately retune a source endpoint for each deflected image. Cosmological and local lens parameters are held fixed during the short inter-image arrival-time difference, as in the declared thin-encounter approximation.

## 3. The fixed preparation is a conditional encounter, not an equilibrium galaxy calculation

The comparison correctly holds the physical SIS deflection strength b and physical transverse source displacement s fixed. The angular source beta=D_os^{-1}X_s changes. Its contribution and the changing physical impact D_ol theta are both retained in the stationary Fermat derivative. Holding beta fixed would be a different experiment and would invalidate reuse of the present timing coefficient.

The SIS is an explicitly prescribed local weak-field lens. It is singular and not a globally finite-mass, action-derived galaxy solution. Its possible response or deformation under the changed cosmological environment is excluded by the fixed-encounter specification. That is legitimate for a conditional forward response, but it is not a solved microscopic BHSM envelope/body reaction.

Suggested addition after declaring the SIS:

> The SIS is a prescribed local encounter held fixed across preparations; this comparison does not solve the galaxy's structural response to the changed environment or a global finite-mass embedding.

## 4. Branches, finite completions and source orientations

The derivative assumes 0<beta<theta_E, sufficiently small smooth perturbations, and continued noncritical image branches. A finite perturbation near a caustic can change image multiplicity. The two continued numerical roots do not constitute an exhaustive image-count theorem.

The finite linear-map completion is a useful derivative check. It is not a second-order cosmological metric solution. In particular, a small completed response at the 45-degree first-order null cannot be advertised as a physical higher-order prediction.

The cosine-of-twice-angle law compares declared source orientations relative to the chosen quadrupole. Those orientations and amplitudes are not selected by the isotropic dynamics or inferred from data. Rotating the source or the quadrupole is a controlled change of preparation, not the time evolution of one observed source.

## 5. Final claim boundary

The conditional first-order result remains

    delta Delta t / Delta t0
        = e^T (Gamma_os-Gamma_ol) e
        = sqrt(2) [(g_os-g_ol) dot y] cos(2 phi).

Its lens-to-source shear cancellation is valid for the fixed-physical-source SIS comparison. It need not hold for another local lens profile or another matching convention. The result is a deterministic state-to-observable forward relationship. It neither selects the state nor removes source/mass/line-of-sight degeneracies by itself.
