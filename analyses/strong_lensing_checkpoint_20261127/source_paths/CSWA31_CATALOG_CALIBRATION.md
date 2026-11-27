# CSWA 31 catalog-plane calibration

Fixed observed positions from Wang et al. Table B.1, archived CDS
catalog DOI 10.26093/cds/vizier.36680162. The archive copy is
`cswa31_muse_raw.tsv` (121 rows); group-selection/mapping script
`cswa31_catalog_planes.py`, machine results `cswa31_catalog_planes.json`.
All seven QF 3 entries near z=1.36 were recovered. The two within 15
arcsec are 677 and 766. A simple ±3000 km/s rest-frame window on this
download selects 44 catalog entries near the primary including the
brightest galaxy (hence 43 additional positions), not exactly the 46
selected in the paper. Do not equate the cohorts. Use one redshift
plane at the median of the seven, ray trace their apparent positions
to their own plane, and then propagate through the S0 deflector.
S4/S5 are excluded from every shared-amplitude and geometry fit.
The tests use a kinematics-motivated S0 proxy, not a recalibration of
observed galaxy masses. Only catalog angles and redshifts are directly
measured inputs for the two new populations: the catalog has no masses
or luminosities, so equal soft-isothermal member weights within each
population are a deliberately minimal calibration.

- Middle plane only: fitted nonnegative normalization lands at zero
  with two or seven members, unchanged at a doubled ceiling, without
  any claim that the galaxies are massless. Forced positive when the
  total angular normalization is 0.60 arcsec, using seven equal weights;
  development RMS goes from 0.3800 to 0.3835 arcsec. S5 remains wrong
  by 3.29–4.99 arcsec, vs. 3.33–4.83 for the original.
- Primary-plane catalog satellites added: at a total normalization cap
  of 10 arcsec, the coefficient hits that cap. S5 misses fall to
  1.04–3.89 arcsec, but S4 is still wrong and the preferred primary
  amplitude is cap-sensitive. At a 20-arcsec cap, it fits 16.50 arcsec;
  the S5 errors are 1.26–3.12 arcsec. The S5 trend is not a calibrated
  mass inference; the fit has no independently normalized per-member
  mass. The central-star-only R1 overlay at the 10-arcsec cap changes
  none of this at the reported precision; no native group deformation
  is simulated.
- Conventional published multi-plane fits use substantially more
  modeling and arc data and include S4/S5 constraints; they are not
  held-out tests. Do not claim this replay falsifies conventional
  gravitation or the presence of foreground deflectors.
- Next: ingest independent F160W luminosity/size weights and image
  morphology, or a preselected stellar mass proxy for each foreground
  member. Refit on the same nearer families and rescore the same
  held-out images, then compare the native shared-field law only if
  physically normalized. Keep population equal-weight results as controls.

Verification: catalog counts, exact zero-added-plane numerical limit,
and perturbing held-out coordinates without affecting the fit.
