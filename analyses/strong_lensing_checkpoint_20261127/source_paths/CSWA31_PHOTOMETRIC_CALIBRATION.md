# CASSOWARY 31 F160W aperture-weight calibration

Source: HST GO-15253, MAST WFC3/IR drizzled science image
`hst_15253_04_wfc3_ir_f160w_idki04_drz.fits` (MAST CAOM 26693200),
used alongside VizieR DOI 10.26093/cds/vizier.36680162.
Fetch via https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:HST/product/hst_15253_04_wfc3_ir_f160w_idki04_drz.fits
and verify the SHA-256 recorded in `cswa31_hst_photometry.json`.
This is the archive pipeline mosaic at 0.12825 arcsec/pixel,
not the Wang et al. custom higher-sampling mosaic. The measured
aperture fluxes/size proxies are not total or deconvolved photometry.
The foreground-only spectroscopic mask does not use the held-out
S4/S5 positions. Uncataloged light can still contaminate apertures.

Photometry: robust local plane subtraction and neighbor-masked
0.64/0.84/1.04 arcsec apertures, HST AB zero point 25.9348.
Quality screens retained 42/43 primary candidates and 5/7 intermediate
candidates. The measured F160W 0.84-arcsec aperture AB values of
the two inner intermediate objects are 21.35 (677) and 21.36 (766).
The normalized soft-isothermal strengths within each population
scale as sqrt(aperture flux); the assumed core proxy is 0.6 times
the aperture half-light radius bounded to 0.10–0.42 arcsec.
These are assumptions, not measured masses or core radii.
Intermediate flux is apparent, not demagnified. A missing object is
excluded nominally, and given median flux as a sensitivity control.

At identical total primary amplitude cap 20 arcsec, S5 counterimage
RMS changes from 2.43 arcsec with equal weights to 2.226 arcsec with
photometry, with similar 2.197–2.251 arcsec across aperture/missing
object controls. Without primary satellites it is 4.335 arcsec.
Equal and light-weighted main-group results are both joint development
fits on S0–S3; S4/S5 are not used for normalization. S4 RMS changes
from 2.859 arcsec to 2.890 at nominal aperture, so there is no uniform
improvement. The intermediate-plane amplitude again goes to zero
within this particular cored isothermal family, not evidence of
zero physical mass. Central-star-only R1 remains effectively unchanged.
The native BHSM group source-to-field response is not inferred here.

Reproduce in this order:
1. `python cswa31_hst_photometry.py /path/to/HST/file.fits` (Astropy)
2. `OPENBLAS_NUM_THREADS=1 python -W error cswa31_light_weighted.py`
