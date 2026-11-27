# HE 0435−1223: single-domain nonlinear R1 galaxy plus group

For the first time in this exercise, the stellar galaxy and its same-redshift group are unified as inputs to **one nonlinear scalar solve**, on a connected axisymmetric grid with no artificial interface or separately stacked interior solutions. Inputs are the frozen R1 coefficients at redshift .4546; the main [Zahedy et al.](https://arxiv.org/pdf/1510.04307) photometrically fixed (M_*=10^{11.1} M_\odot), (n=3.51), area-equivalent projected effective radius 3.984 kpc prior to core regularization; and the [Sluse et al.](https://doi.org/10.1093/mnras/stx1484) spectroscopic group at 67.1″ and dispersion (470\) km/s. The offset is put in the sky plane (projected separation 398.91 kpc). The spherical group is modeled by the difference of two softened isothermal densities, unmeasured core 25 kpc and velocity-dispersion-motivated outer soft scale 761 kpc. This prescription has a decaying tail, not a hard radius. The main density is softened inside a 0.5-kpc radial scale and then normalized to the same stellar total. Without normalization this softening retains 91.9% of the total; it is a material modeling choice, not a measurement. All known profile simplifications remain explicit.

The finite cylindrical domain has one prescribed approximate common screened monopole outer value, and no free boundary seam or fitted group potential. The solver instead varies the full interior field using the actual static nonlinear Hessian invariant and tracks pointwise sampled principal-operator positivity on a nonuniform grid. The retained weak-field no-slip branch gives the scalar part of the metric as (-b_T\pi/(2M_{\rm Pl}^{2})). No delay, lens-fitted mass, or lens-fitted outer boundary is used.

| Radial × axial grid | Half-box length | Discrete max scaled residual | Sampled minimum principal eigenvalue | Pairwise joint-minus-isolated scalar deflection on fixed ±800 kpc paths |
| --- | ---: | ---: | ---: | ---: |
| 68 × 135 | 1.5 Mpc | 8.14e−8 | 4.017 | .004812 mas |
| 90 × 179 | 1.5 Mpc | 1.55e−7 | 4.022 | .004711 mas |
| 90 × 179 | 2.25 Mpc | 1.77e−7 | 4.018 | .004745 mas |
| 115 × 229 | 1.5 Mpc | 1.56e−7 | 4.025 | .004659 mas |

The independent one-source spherical control reproduces the analytic radial gradient to .19–.63% at 3–24 kpc. A coarse Plummer test was also performed; its original stricter requested numerical tolerance and flags are preserved in `he0435_nonlinear_joint_axis.json`. The table's rerun uses a gauge-offset subtraction and separately specified 2e−7 discrete target. Residual, positivity and sensitivities here are numerical properties, not validated continuum or observational error bounds.

On the finest Sérsic grid, the same statistic is .003275/.004505/.004659 mas on half-path widths 80/300/800 kpc, so the outer integration tail is explicitly tested rather than silently discarded. The number is the maximum **pairwise differential between two calculations** (nonlinear joint scalar vs isolated scalar sum) at actual observed ray positions. It is not the full predicted lens astrometry, a complete two-plane source map, or a measurement. Ordinary group convergence, rear G1, unknown mass distribution and the independent constitutive BHSM environment term are not solved in this comparison. The actual two-center PDE can be solved under declared inputs; this does not establish that the inputs predict the entire observed field.

Replay, in this directory:
```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python he0435_nonlinear_joint_axis.py --main-profile sersic --runs main:68:1.5 joint:68:1.5 joint:90:1.5 joint:90:2.25 joint:115:1.5
```
