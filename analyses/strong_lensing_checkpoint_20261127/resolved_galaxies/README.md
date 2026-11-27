# HE 0435−1223: individual galaxies inside the total lensing field

This is a fixed-observed-ray diagnostic for PR #23, not a fit. In weak-field lensing, light responds to the transverse gradient of the combined optical potential throughout its path. Nearby sources make that gradient vary across the four image rays. Where deflectors are at different redshifts, a deflection also changes where the ray samples a later lens plane. No ray needs to pass through a galaxy's visible body.

## Controls

1. **Mass redistribution (one budget).** Fix the nominal 1.385 Mpc aperture budget at 10^13.72 solar masses. In both cases reserve the main galaxy's stellar profile. Compare a resolved, compact G4 (10^10.399 solar masses from the stellar catalog) with its catalog stellar mass returned to the same off-center diffuse group profile. The group parameters (25 kpc core, 761 kpc softening scale of the outer subtraction) are fixed sensitivity assumptions, not measured. G4 is put in the main group plane; its small observed redshift difference is not treated as distance. The compact G4 is fully within the group sphere. The spherical main Sérsic profile is budgeted by its full stellar mass; the omitted Sérsic tail outside the budget sphere is negligible at this precision. Rear galaxies and foreground G3 are kept on their separate measured-redshift planes, not charged to the main group. This comparison changes both the linear tide and the higher-order field.
2. **Local tidal approximation.** Keep each mass model fixed. Replace only the designated object's exact bending function by its first-order Taylor approximation about the central ray *on that object's own plane*. This keeps the central bending and local convergence/shear while removing higher-order angular variation in those coordinates. Later planes still propagate in order. The four reported differences are vectors in the inferred source plane, not measured position shifts or a published flexion-shift statistic. The summary reports the largest pairwise norm of those vectors, which cancels a common translation.
3. **Ray ordering.** Compare ordered tracing with evaluating all deflectors on undeflected angular trajectories. Deflector light centroids in the ordered case are back-traced through the preceding planes. This is a method sensitivity, not a direct measurement.

Two independently specified distance prescriptions (the paper's frozen R1 background and a conventional flat LCDM control), two candidate group centers, and 1×/3× versions of the main Sérsic amplitude were checked. The 3× version is a sensitivity, not a new kinematic posterior. The 5, 15 and 65 kpc compact-member radii are modeling controls. R1 distances do not by themselves implement a BHSM perturbation to optical gravity. None of the paths is refitted to a common quasar source, there is no time-delay inference, and the positive effective mass of the diffuse component is an input proxy, not a derived BHSM output.

## Suggested manuscript wording

“For light traversing the HE 0435−1223 environment, a diffuse group contribution and localized galaxy contributions belong to the same optical field. We retain resolved members where a local convergence/shear approximation changes the ray mapping, and propagate rays in redshift order so that foreground deflections change later impact parameters. For G4 we compare explicit placement with redistribution into the group at fixed mass budget. These controls isolate sensitivity to source placement and field gradients; they do not constitute an independent recovery of the group profile, a time-delay measurement, or a departure from standard weak-field lensing.”

## Sources and replay

- [Courbin et al., Table 2](https://arxiv.org/pdf/1009.1473): four ray positions and lens center.
- [Morgan et al., Table 3](https://arxiv.org/pdf/astro-ph/0410614#page=7): galaxy astrometry re-centered on the main lens.
- [Sluse et al., Fig. 5, Table 4, Table C1](https://esahubble.org/static/archives/releases/science_papers/heic1702b.pdf): perturber redshifts, group candidates and nominal virial mass/radius.
- [H0LiCOW Rusu catalog](https://shsuyu.github.io/H0LiCOW/site/data/PaperIII_complete_catalogue.txt): stellar mass inputs; these are not total halo masses.
- [Wong et al.](https://doi.org/10.1093/mnras/stw3077): precedent for treating G1 explicitly at its own redshift; G1 circularized bulge/disk proxy adopts common mass-to-light ratio.
- [McCully et al.](https://arxiv.org/abs/1401.0197): mixed exact and tidal multi-plane methodology.

Run with Python, NumPy, and SciPy: `python resolved_control.py`. Checks include exact undeflected identity, independent cylindrical group-mass quadrature, and consistency of each local derivative on two step sizes. `RESULTS.txt` is a compact replay log and `resolved_control.json` retains all four signed vector differences and impact parameters for each configuration.
