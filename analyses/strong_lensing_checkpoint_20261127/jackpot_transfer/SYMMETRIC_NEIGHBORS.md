# Two-neighbor control: route versus terrain

Same frozen spherical stellar profiles and R1 cosmological coefficients as
the previous controlled tide test. Put equal positive point masses at
opposite physical offsets 400 kpc from each primary, on an axis tilted 45
degrees to the line of sight. Each has mass 7.4403e9 solar masses, so the
local Newtonian quadrupole is q r^2 P2 with q = -0.001 (km/s)^2/kpc^2.
The center's direct acceleration vanishes, but the tidal tensor does not.

## Route

Propagate in ordinary weak-field multi-plane optics twice: first with
each ray passed forward from plane to plane, then with each deflection
evaluated at the same unperturbed viewing angle. For both, subtract
the star-only and neighbors-only deflection. The latter subtraction
includes any neighbor-neighbor propagation already present. Unshifted
rays give zero mixed deflection to floating-point precision. These
controls use all Newtonian point-mass multipoles. No actual galaxy
peculiar velocity or measured neighbor positions are inferred here.

## Terrain

For the R1 deformation retain the leading l=2 term only (its radial
potential everywhere, not just its local Taylor form), projecting along
unchanged rays. A constant-potential interior l=0 for the external
spherical shell is not a description of its exterior, so this explicitly
does not include the pair's l=0 or higher multipoles in the R1 response.
Subtract the isolated scalar tide. The first-order l=2 term can have a
nonzero sky-ring mean because a tilted 3D quadrupole does not average away
along those sightlines. It has zero *3D* spherical mean.

Let u=f(r) P2 be the first-order scalar response in physical scalar
units. The quadratic mean radial flux is
Q=(2 f'^2/r - 12 f f'/r^2 + 6 f^2/r^3)/5.
This follows by averaging ((Delta u) grad u - Hess(u) grad u) in the
radial direction. Regularity and absence of second-order matter drive
give v0'=2 Q/(lambda A), using the same radial principal coefficient A
as the first-order solve. Subtract the isolated quadratic scalar tide
(A=C and its own f) before projecting. The quadratic entry is just the
l=0 contribution, not the full second-order projected correction.
These are perturbation coefficients, not a finite-amplitude fit.

At 1 arcsec, in microarcseconds (inward radial is positive):

| Lens | Route residual range | Terrain axis minus cross-axis, linear | Terrain sky mean, linear | Terrain true monopole, quadratic contribution |
|---|---:|---:|---:|---:|
| HE 0435 | -0.0333 to 0.0350 | -0.00766 | 0.00260 | -0.0000164 |
| Jackpot | -0.244 to 0.252 | -0.0137 | 0.00463 | -0.0000517 |

The Cartesian interior flux identity, independent angular quadrature,
two resolutions and tails, ray-order null, and linear/quadratic
amplitude scalings were checked. No mass, halo, source, or coupling was
fitted. This is an action-fixed R1 Galileon test, not a derivation or
validation of the full BHSM interface/environment law. It is not the
real environment of either system and does not close the lensing gap.

Replay: OPENBLAS_NUM_THREADS=1 python symmetric_neighbors.py
