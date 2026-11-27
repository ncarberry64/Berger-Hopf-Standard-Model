# HE 0435−1223 finite local galaxy–group mixed R1 calculation

This advances the earlier separate thin-lens group control. It is still not the globally matched HE 0435−1223 field. An independently derived stellar main profile is perturbed by the measured main-redshift group, idealized as an isothermal sphere. Use [Sluse et al., Table 4](https://doi.org/10.1093/mnras/stx1484) velocity dispersion 470±100 km/s, offset 67.1″, and the observed sky direction (east/north unit vector −0.57961,+0.81489). At the frozen distance the group is at projected separation 398.91 kpc; adopt zero additional group depth uncertainty as an approximation for the nominal control.

## What is solved

In natural units, subtract the exact spherical screened stellar equation before expanding. The linear scalar operator is in divergence form with (a_r=CS), (a_t=a_r+r a_r'/2). The leading local SIS density produces the monopole source (J_g); the group's isolated radial R1 Hessian fixes a quadrupole Dirichlet value at a matching sphere rather than being added as an interior solution. Constant potential/gradient are excluded from this relative, centered response. The regular (l=2) mode follows ((r^2a_rf')'=6a_tf). One explicit residual correction with fixed Dirichlet data inserts the full omitted scalar quadratic source, with Legendre degrees 0, 2, and 4, through the same variable-coefficient operator.

## Numerical control, nominal group

| Trial matching radius | Sampled linear principal perturbation / minimum base ellipticity | Residual relative to local (J_g), before → after correction | Corrected inner joint-vs-isolated pair difference |
| --- | ---: | ---: | ---: |
| 20 kpc | 0.357 | 7.856 → 0.190 | 0.0007152 mas |
| 40 kpc | 1.211 | 11.799 → 1.037 | 0.0016706 mas |
| 80 kpc | 4.016 | 18.080 → 6.574 | 0.0028695 mas |

The 20-kpc finite problem is numerically useful: the nonlinear correction changes the relative ray contribution by (1.295\times10^{-5}) mas; the corrected group scalar *interior* signal itself is (8.4480\times10^{-4}) mas. The denominator (J_g) is the small local group density source, not an estimate of the overall forcing scale. Neither residual sampling nor correction size certifies an observational precision or global error. For 40/80 kpc, this low-order truncation does not certify a result. No artificial free surface layer is inserted. Exterior conormal matching has not been solved, the 20-kpc quadrupole logarithmic derivative 1.588 differs from the imposed far Taylor profile's value 2, and the finite line-of-sight integral is not closed at large distance. The rear G1 coupling is not rerun in this interior diagnostic.

Replay: `PYTHONDONTWRITEBYTECODE=1 python he0435_local_group_joint_response.py`. Result: `he0435_local_group_joint_response.json`; primary direction receipt `he0435_group_direction.json`.
