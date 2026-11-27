# Multi-dataset gravity-topology test

Use different sightlines and independent measurements, not duplicate images
in different filters as independent paths. Keep PR #23's HE 0435 time-delay
question and Jackpot transfer as the main targets. Keep larger systems as
controls unless the same source-to-field law transfers without recalibration.

1. **CSWA 31: group-scale bridge.** Wang et al. 2022,
   https://doi.org/10.1051/0004-6361/202243600, Table 1 and Sect. 2.
   HST WFC3 F160W/F438W resolves arcs and foreground starlight; ESO/MUSE
   program 0104.A-0830(A) supplies source and group-member spectroscopy
   (46 selected member redshifts) and central stellar kinematics. The
   measured positions give 18 images in 6 feature families across 5
   physical sources. S0/S1 are distinct features of the same spiral.
   S2 is another source at very nearly the same redshift. There are
   effectively four well-separated source distances. The minimum and
   maximum projected radii are 2.95 and 23.63 arcsec (21–171 kpc in
   frozen R1 geometry). First development split: S0–S3; keep S4 and
   S5 for comparison without adjusting the map to them. S4 has a
   single emission line and model-supported association; S5(d) is
   a lower-S/N member with model corroboration. Test robustly with
   and without those assignments, and treat existing published models
   trained on these points as benchmarks, not blind comparisons.
   All four S5 paths lie outside the development images' sky convex
   hull. Their use tests extrapolation, not interpolation. Without
   independent group outskirts/gas data cannot supply a complete 3D
   matter map. See `cswa31_paths.py` and `cswa31_paths.json`.
2. **SL2S J02140-0535: galaxy-group cross-check.** Verdugo et al.
   https://arxiv.org/abs/1608.03687. Spectroscopy of two background
   sources and group members, shallow XMM, and wide-field information
   are complementary; do not assume both sources furnish multiple
   secure images without verifying the individual IDs.
3. **Abell 2744: larger-scale map stress test.** Bergamini et al.
   https://doi.org/10.1051/0004-6361/202244575 Table A.1 offers a
   clean starter catalog of 90 multiple images from 30 spectroscopic
   backgrounds. The more extensive JWST GLASS/UNCOVER catalogs overlap
   this sample, so they should be reconciled family by family, not
   summed. Gas imaging and more widely separated rays can address
   broader-scale topology; the mass scale is unlike the main paper.
4. **Timing control if needed:** MACS J1149 and SN Refsdal
   https://doi.org/10.1051/0004-6361/202449528, or SDSS J1004+4112
   https://arxiv.org/abs/2206.08597 with the positions in
   https://arxiv.org/abs/1005.3103. Keep timing and unseen-region
   prediction separate; do not use fits to the same delays as blind
   tests.

For real comparisons: map a shared physical field from independently
specified galaxy/group inputs; propagate individual light paths, including
intermediate source-plane deflectors; calibrate the conventional comparator
with exactly the same development constraints. Reserve whole source families
and sky regions, and predict image positions and morphology, then timing
where a common source is recovered. Sky projection still does not uniquely
recover a three-dimensional mass distribution. The current replay establishes
coverage and rank in a simple projected basis only; it is not a model fit.
