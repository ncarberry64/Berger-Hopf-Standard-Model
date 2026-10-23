# Final skeptical review of the conditional Blackhole Tracker

This is an internal AI-assisted review, not external peer review. The review covers the explicit radial response, local optical derivatives, numerical information experiment and current manuscript. It distinguishes mathematical closure within the declared model from physical horizon matching and observational usefulness.

## Verdict

The narrowed theoretical claim is supported: an explicit conditional R1 exterior maps a supplied worldtube state to one consistently normalized lens potential; separate image, geometric flux and delay data can retain two transverse directions outside the specified finite nuisance space. The action does not select the black-hole flux or deformation amplitude, and the experiment does not establish a horizon, detection, practical observing campaign or general identification against arbitrary ordinary lens structure. The manuscript now states those limits.

No blocking algebraic error remains in the reviewed image-shift, total-Hessian, source-displacement, center-motion or parameter derivatives. The 30-column replay has been inspected. The final all-nine-stage replay has passed and refreshed the numerical artifacts. The earlier harmonic-symbol and section-ownership issues have been corrected, as verified in the current source.

## Resolved findings from the first pass

1. **Unknown scalar monopole flux is now profiled locally.** The nuisance family contains a logarithmic scalar-flux tangent in addition to the physical mass tangent. `parameter_radial` changes the physical scalar monopole at fixed reference Einstein coordinates. At zero quadrupole amplitude, dependence of the quadrupole shape on a nuisance-flux variation is a second-order product, so it is correctly absent from this linear design. A flux/mass sweep additionally tests several specified backgrounds. This resolves the earlier fixed-flux-only inference concern; the physical horizon selection of that flux remains open.

2. **Finite primary roots now have admission checks.** The finite solver checks stationary residual, exterior radius, parity, and bright/early versus faint/late ordering. These checks are more relevant than relying on a nonlinear solver's success flag alone. They define a continued two-primary-image calculation, not an exhaustive image census. Extra roots from singular multipoles near an excluded interior are not ruled out.

3. **Roundoff-zero nuisance columns are no longer blindly normalized.** The current projection admits columns only above `1e-11 * max(maximum raw column norm, 1)`, then normalizes and uses a relative singular-value rank threshold of `1e-9`. Raw admission counts and spectra are saved. All 30 columns survive the main full-data admission. The floor is a numerical convention, not a physical prior or an instrument noise model; the manuscript should state it beside the SVD threshold. Near-null compressed and short-span results remain sensitive to numerical rank conventions and are not forecasts.

4. **Detailed screening curvature is not overclaimed.** The manuscript explains that the strict constant-phase replacement retains nearly the same joint information as the fully matched phase. The main distinction comes from keeping separate image/flux/delay data while comparing the extended response against the declared compact and external quadrupoles. The calculation does not claim that the small transition correction itself has been isolated.

5. **Tiny formal contribution is separated from physical accuracy.** The selected state has dimensionless phase amplitude about `8.89e-13`. Its formal delay contribution is about `5.1e-12 s`, while ordinary weak-field and matching truncation parameters are much larger. The manuscript labels this a contribution of the truncated model, not a physical picosecond prediction, and warns that time-dependent/matching terms need comparison. The same caveat must remain in the lay report and release summary.

## Current inspected numerical evidence

The 30-nuisance result includes 18 independent source coordinates, mass, scalar flux, one axial Y20 boundary mode, two center coordinates, two constant-velocity coordinates, convergence, two external-shear coordinates and two ordinary compact quadrupoles. In 54 data components its projected transverse singular values are

`(3.1347347957, 0.8021997408)`

per unit phase amplitude under the declared equal-dimensionless-error metric. The retained column-norm fractions are

`(0.0421333175, 0.1451210590)`.

Those are local response/conditioning quantities, not instrument-independent detection significance. Profiling scalar flux changes one direction materially compared with the earlier 28-column result, so obsolete 28-column numbers must not remain in the abstract, table, figures, captions or summaries.

The latest finite nonlinear primary-pair derivative comparison ends at an absolute response error about `1.60e-7` for test amplitude `3e-5`; the corresponding stationary residual is about `2.5e-16`. The error decreases quadratically with test amplitude. These deliberately larger lens-potential test amplitudes verify the optical derivative; they do not license an enlarged physical scalar boundary amplitude.

At zero spherical scalar flux, the exact spatial response is harmonic and its projected transverse quadrupole is exactly in the included ordinary compact-quadrupole family. The provider now evaluates this limit analytically rather than interpolating a known power law. The numerical sweep retains at most about `2.21e-15` of the signal norm, consistent with roundoff. The analytic harmonic identity supplies the exact conclusion; the residual is not a measured physical signal.

The ten-year small-span design retains only order `1e-11` projected singular values and has nearly dependent nuisance columns. It is correctly discussed as a conditioning failure, not an observing forecast. A broad `3.6 rE` scan at the illustrative 300 km/s speed takes approximately 5.2 million observer years. Its frozen exterior is therefore a spatial information experiment, not a literal modeled observing history over that interval.

## Remaining manuscript and packaging checks

**Normalization and section structure: resolved.** The STF prefactor is now named N_STF, and the explicit relation N_STF/sqrt(2)=N_2 translates to the unit transverse harmonic. The duplicated section headers and the misplaced appendix wording are corrected. These changes resolve the earlier normalization-communication and hierarchy issues without changing the implemented physical response.

**Axial-mode conditioning and arithmetic: checked.** Adding the physically visible axial Y20 mode is a legitimate enlargement of the nuisance family. It reduces one retained transverse direction to about 4.21% and makes the normalized nuisance matrix nearly masslike, with condition number approximately 3.64e6. The original double least-squares versus SVD residual comparison exceeded the unchanged 2e-11 acceptance bound at about 3.25e-10; the failed diagnostic is preserved. For full-rank admitted columns the revised code projects the same double-precision input matrix with 70-digit normal equations, while retaining the existing SVD rank selection. This is mathematically valid: squared conditioning is comfortably handled at 70 digits, and no null direction is inverted. A separate 70-digit QR calculation checks the projection, and the 121-versus-241-node singular values agree within about 2.62e-9, below the unchanged 1e-6 criterion. This improves arithmetic only, not the derivative inputs, physical model or forecast accuracy.

An independent reviewer calculation first identified a stale saved double-SVD residual at a 1.49e-10 difference. The final nine-stage replay then refreshed the NPZ and JSON. Repeating the independent 70-digit QR projection against the released saved residual now agrees within 1.50e-69; the saved singular values are (3.1347347957119154, 0.8021997408150598). This confirms arithmetic consistency for the same double-precision derivative inputs, not physical accuracy to 69 digits.

**Final numbers and source identity: passed.** The final replay receipt states ALL_NINE_STAGES_PASSED, verifies six pinned provider files from commit 06cf7c1b85d6605bfee0cc0d07fb2af86a66cae9, and records that no observations were used. All stage return codes are zero. The refreshed artifact identities inspected by this reviewer are:

- code/tracker_response.py: d3bbadfc78b4a736ac6262901bb50ab92cc737f90fb4f907bf20c96f10b313d3
- code/radial_response.py: b8787732d3ef63a33f64dcf23ff66497700893ac871447c423be0573a54f9580
- results/tracker_response.json: d3a42b295bfd79c9b7d3f5221ed40882748211594bc16588ebbad3f5f0814430
- results/design_arrays.npz: b52d4cc9a5ddae3d553f3bd1b9bd08aabc347e632d600bcb6f6457083ae85aea

The source-bound package manifest should retain these identities or regenerate them after any subsequent change. Mathematical and numerical checks do not replace the separate rendered-PDF layout review.

## Independent algebraic checks

The review's separate derivation and script verify the generic relations

`delta x = A^-1 (grad p + delta y)`

and

`delta ln|mu| = tr[A^-1 (H p + D(H psi0)[delta x])]`.

The code includes the full evaluation-point derivative. Fermat stationarity gives the potential difference plus `(x_plus-x_minus) dot delta y` in the delay; the common `y dot delta y` drops only after forming the relative delay. Center and velocity tangents translate the same baseline scalar-plus-GR metric rather than inserting another force. The mass tangent changes the scalar monopole along with the ordinary monopole at fixed reference angular units.

For the standard point-mass estimator the independent calculation finds the exact first-order response identities `K_1=K_r2=Kstar`, `K_rminus2=(u^2+1)Kstar`, including the nontrivial all-u null `(r^2-1)cos(2 phi)`. The null is expressly first order; an independent finite perturbation gives a nonzero quadratic departure. Its role is to expose compression of information by the scalar statistic, not to claim a universally admissible compact source for that potential.

The source-action, STF projection and radial equations are mutually consistent in the reviewed text. The rank-three axial projection argument correctly uses `(K_r r^-4 Y')'=6 K_r' r^-5 Y` for `Y=r^3 f`, positivity and the decaying boundary condition. The unscreened harmonic limit has zero axial projection and rank two. The odd xz/yz nulls require the stated symmetric straight-line frozen projection; the text correctly excludes automatic extrapolation to finite endpoints or time-dependent weights.

The external-shear nuisance uses `r^2 cos(2 phi)` and `r^2 sin(2 phi)` as unit basis potentials. Its fit coefficient is half the usual physical shear component under the convention `psi_shear=(gamma/2) r^2 cos(2 phi)`. This changes no nuisance column space but must remain consistent in physical coefficient descriptions.

## Scientific limits that remain essential

An annular distributed ordinary quadrupolar density can reproduce a constant spin-two potential, and a small anisotropy can coexist with a positive monopole. The finite compact/shear nuisance family is useful but cannot establish general separation from all ordinary envelopes or arbitrary line-of-sight potentials. The manuscript now says so. Source-position transformations, uncertain time-distance calibration, arbitrary frame distortions, flux propagation, source structure and additional sources require their own inference model.

The supplied flux and worldtube deformation are not a horizon-regular black-hole solution. A Schwarzschild surface scalar or Brown-York inversion does not determine this scalar charge. The consistent scope is an exterior compact-mass/envelope template conditioned on a stated effective action and boundary datum. Its validity does not depend on acceptance of the whole microscopic BHSM program, and its success does not establish that program.

With the verified notation/hierarchy fixes and passed final replay, this is a defensible conditional theoretical methods result. It does not yet achieve the larger astrophysical ambition of a physically selected, observable black-hole deformation signal. That candid conclusion is scientifically stronger than relabeling the finite information experiment as a detection.
