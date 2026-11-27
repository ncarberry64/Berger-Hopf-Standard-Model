# Jackpot: an inter-ring tidal response

Norman proposed a dynamical choke point between the two calibration rings. Test its optical consequence without assuming either the sign or the orientation. This is a projected, static template; it is not evidence that there is a flow bottleneck or a derivation of its dynamics from BHSM.

Hold the prior Chabrier spherical response, aperture masses, ordinary deflectors and lens geometry fixed. Set a smooth signed quadrupole in projected convergence confined to 1.397–2.070 arcseconds (about 5.15–7.63 kpc), with predeclared inner-half and outer-half alternatives. Only the anisotropic term is added: its azimuthal mean vanishes and it changes neither circular aperture mass. The strength/orientation comes from two coefficients estimated with the 14 early-source knots; neither third-source image selects those coefficients or the band boundaries. Compare existing ordinary shear, tide in place of ordinary shear, and tide added alongside ordinary shear, sharing the same S1 deflection nuisance.

For each m=2 convergence component k(r), the decaying projected potential is -[r^-2 integral_0^r s³ k(s)ds + r² integral_r^infinity k(s)/s ds]/2. Thus the tide looks like shear well inside the band, while the potential falls as r^-2 outside (deflection falls as r^-3). It is not a bump in the optical potential forced to vanish at the edges. The two source-3 images lie on opposite sides of the band: A at 3.556 arcseconds and observed B at 1.348. Their different radial weighting supplies a real lever arm even though neither passes through the projected band at closest approach. Analytic derivative verified numerically and zero circular monopole checked.

| Shape model | Early knot RMS | Held-out B position error |
|---|---:|---:|
| Ordinary shear, fixed envelope baseline | 31.4 mas | 346 mas |
| Full inter-ring tide replacing shear | 138.6 mas | 774 mas |
| Full inter-ring tide added to shear | 28.8 mas | 313 mas |
| Inner-half tide added to shear | 29.1 mas | 333 mas |
| Outer-half tide added to shear | 30.1 mas | 309 mas |

The added tide changes the outer forecast without degrading the early nominal RMS, but the change is modest and adds two degrees of freedom. The outer-half test hits a prior coefficient bound; its nominal improvement is not a preferred band or a measured tide. The standard matched Chabrier control with a conventional radial profile has about 38 mas B error, not the 346 mas frozen envelope baseline used in this experiment. Do not assign a physical convergence/energy density to the fitted coefficients without the full normalization and stress map. No significance estimate, actual choke-point mechanism, or HE 0435 transfer. To test dynamics rather than a flexible static tide, source the layer's nonuniform response from the action or independently measured geometry, and require the resulting profile to pass both rings and an untouched outer observable.

Replay: OPENBLAS_NUM_THREADS=1 python jackpot_annular_tide.py.
