# Historical benchmark metadata and rights review

Checked 22 October 2026. This is a source/metadata review, not a mass fit.

The deposited 2022 observations can support a rectilinear relative-time photometric screening fit with a declared independent Gaussian magnitude-noise model. They do not yet support a certified precision joint/parallax recovery under the information recovered here.

## Timing evidence

The [Zenodo deposit](https://zenodo.org/records/6607578) labels HST t as UTC without stating its numeric epoch origin. A [contemporaneous 2022 BAGLE reader](https://github.com/MovingUniverseLab/BAGLE_Microlensing/blob/51e0f6e7220fc88cf6065ed1672a5db8be2b319e/src/bagle/data.py) reads private HST reduction FITS times as Julian years in UTC and converts them to MJD. That is useful corroboration but does not reconstruct the ASCII export of these exact deposited tables.

An independent public MAST query returned 42 observations of the target. The date/filter/proposal mapping agrees with the original supplement's observing log. Three actual FITS primary-header prefixes were downloaded using HTTP206 byte ranges, preserving source URLs and hashes. They confirm exposure dates/ranges directly. If the native t column is treated as ordinary exposure MJD UTC, every one of the eight shared epochs falls outside its corresponding F606W exposure range:

| Native t, unconverted | Actual MAST F606W exposure window, MJD | Difference from exposure start, days |
|---|---|---|
| 55781.3583048 | 55781.6912507–55781.7427901 | -0.332946 |
| 55865.4158390 | 55865.1737641–55865.2012061 | +0.242075 |
| 56178.9420253 | 56179.1855304–56179.2131113 | -0.243505 |
| 56194.9092384 | 56195.2737831–56195.3012252 | -0.364545 |
| 56586.9096747 | 56587.1453426–56587.1759098 | -0.235668 |
| 56956.1624144 | 56956.0736190–56956.1027969 | +0.088795 |
| 57993.8726884 | 57994.6864033–57994.7565535 | -0.813715 |
| 59487.8952911 | 59488.3598085–59488.3917876 | -0.464517 |

This is a diagnostic comparison, not an accepted epoch transformation. It establishes a concrete mapping gap, not its cause. No blanket day shift, inferred MJD origin, corrected exposure substitution, or modified raw file was used. Original reduction/export code or an author-validated epoch mapping remains needed. The two filters share eight archived epochs; they are not sixteen independent visits.

The OGLE/MOA HJD clock scale remains unspecified in the supplied READMEs. The historical reader labels OGLE numbers UTC and undoes heliocentric timing for another raw six-column MOA format. Neither observation establishes the precise transformation of the released three-column calibrated MOA file. Subtracting a numeric origin alone is not a physical clock or heliocentric conversion.

## Cross-filter calibration

The [published 2022 supplement](https://doi.org/10.3847/1538-4365/ac7441), section4.2.5, derives and applies a constant F606W positional shift of (-0.57,+0.39) mas after the neighbor-bias correction. The released pairs have weighted F814W-minus-F606W differences (-0.00360,+0.02876) mas, with approximately0.178mas formal errors under an explicitly assumed independent diagonal model. Those small differences are consistent with prior alignment. They are not a certificate of which export/bias/reference-frame transformations were applied. Reapplying the historical offsets is unjustified. Exact table provenance and shared-frame/filter covariance remain unresolved.

## Which historical benchmark comparison is valid

The published default-weight likelihood adds ground photometry, HST photometry and HST astrometry log likelihoods. The equal-weight definition divides each group by its point count before adding. They represent different information weighting and can change the answer. The supplement describes a full photometric Gaussian-process covariance, diagonal HST noise and explicit priors; Table19 lists no GP hyperparameters for OB110462. A contemporaneous public weighted-solver implementation also has several weighting options and an additional overall normalization in one mode. No exact deposited run configuration was recovered. Do not identify a new diagonal rectilinear screen with the published joint/parallax posterior or tune it to a preferred mass. The later2023/2025 reductions are distinct datasets and are not mass-recovery targets for these bytes.

## Redistribution

The archived [Zenodo API metadata](https://zenodo.org/api/records/6607578) explicitly records cc-by-4.0 for version1.0.0. Preserve author attribution, DOI, version, README and declared transformations if redistributing those observations. Their license is separate from the BHSM software license.

The [OGLE project page](https://ogle.astrouw.edu.pl/cont/4_main/len/bulge_o3/) requests citation of the catalog paper and offers the observations for analysis. No dataset-wide redistribution license was found in that page or the supplied archive README. Keep OGLE raw bytes in the external reproducibility data store and publish exact-source fetch/hash instructions and derived results unless redistribution permission is clarified. No author or collaboration was contacted.

## Audit files

METADATA_AND_RIGHTS_RESEARCH.json contains exact source URLs/hashes, original reader revisions, FITS-header evidence and scoped findings. HST_NATIVE_TIME_VS_MAST.json contains all eight individual comparisons. The source files and rendering evidence remain in outputs/bhsm_real_data_20261022/metadata_research; the completed F4/F5 receipt remains in outputs/bhsm_real_data_20261022/theory_sources/F4_F5_VERIFICATION.json. No new physical mass, distance, absolute proper motion or horizon identification follows from this metadata review.
