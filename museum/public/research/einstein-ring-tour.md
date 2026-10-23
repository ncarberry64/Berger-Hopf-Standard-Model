# Einstein ring tour: visual method and measurement scope

This not-to-scale illustration uses ordinary geometric-optics gravitational
lensing by an isolated point mass. It is not an observed star field, a black-hole
detection, a BHSM prediction, or a fit to the product's synthetic dataset.
The stationary decorative stars represent foreground reference light; the
finite distant source moves relative to the marked foreground lens.

## How the light is drawn

The source is a uniform-brightness circular disk of radius 0.14 times the
Einstein angle. Every displayed image boundary is calculated from the inverse
point-lens map, in dimensionless angular coordinates:

`beta = theta - theta / |theta|^2`.

For each image-plane direction, the disk intersection determines a radial
interval. These intervals form two arcs when the disk is off-axis and an
annulus when the disk covers alignment. At exact alignment the annulus is
circular. Surface brightness is not multiplied by a divergent point-source
magnification. The finite image area produces finite integrated brightness.
The inferred lens-center marker has an arbitrary visible size; it does not
depict a resolved object, horizon, orbit, material shell or lens radius.
Source-position guides are model geometry, not an additional observed image.

## Reading the pause

The marked Einstein angle is a fitted lens scale through the ring's width,
not its outer edge. For a point mass,

`theta_E^2 = (4 G M / c^2) D_LS / (D_L D_S)`.

Independent distance information is needed to convert this scale to mass.
For cosmological lenses these are angular-diameter distances; `D_LS` is not
generally `D_S - D_L`. For nonspherical or extended lenses, the interpretation
requires the appropriate lens model and enclosed projected mass.

The optional offset snapshot marks the compact-source limit's two image
positions and total-flux ratio. The extended arcs are calculated from the
finite disk; their centroids and photometry require an extended-source fit.
They should not be identified exactly with compact-source marker positions.
Lensing preserves surface brightness, so compare integrated fluxes of the
images rather than the intensity of one pixel.

Repeated positions relative to reference stars constrain angular motion.
Separating lens, source and observer contributions, and converting angular
motion to physical speed, requires additional information. The tour's seconds
and slider positions are presentation controls, not measured epochs or speeds.
The animation stops for study at alignment. Resume continues the relative
crossing; replay restarts it. It never claims that a static snapshot measures
a time delay; that requires identifiable variable source light seen at
different times in the resolved images.

## Primary sources

- [ESA: Einstein ring explained](https://www.esa.int/ESA_Multimedia/Images/2025/02/Einstein_ring_explained)
- [Narayan and Bartelmann, Lectures on Gravitational Lensing](https://pages.astro.umd.edu/~rmushotz/ASTRO620/Naryan_Bartlemann_Lensing.pdf), lens equation, Einstein radius, image positions, magnification, and surface-brightness conservation.
- [Sahu et al., An Isolated Stellar-Mass Black Hole Detected Through Astrometric Microlensing](https://arxiv.org/abs/2201.13296), combining astrometry, photometry and parallax.
- [COSMOGRAIL XIX](https://doi.org/10.1051/0004-6361/202037740), time-delay measurement from variable lensed images.
