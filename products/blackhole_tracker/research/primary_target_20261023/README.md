# Primary investigation target: Gaia18ajz

Gaia18ajz is a **previously published potential black hole** selected for a research programme. The tracker has not established its physical BH identity or independently recovered the known-BH benchmark. Publication remains on HOLD. The pinned investigation programme retains all eight near/far, photometric-mode and mass-prior alternatives, including lower-mass interpretations; see the installed app's Primary target page or `bhtracker/theory/PRIMARY_TARGET_PROGRAM.json`.

The public ZTF file described here is contextual observation intake, not an accepted candidate analysis. No parser, row selection, importer, likelihood or physical fit is supplied by this helper. It cannot be fed into the old resolved-image schema: it supplies no resolved image positions, image flux ratios, interimage delays, lens distance or invented covariance.

## Reproduce the frozen context

From the product folder in a source release, print the exact protocol without making a network request:

```console
python scripts/fetch_primary_target_context.py
```

To verify a native file already acquired, choose a fresh output directory whose parent exists:

```console
python scripts/fetch_primary_target_context.py --verify-existing PATH_TO_NATIVE_FILE --output NEW_CONTEXT_VERIFICATION_DIRECTORY
```

The original file is opened read-only. An input within the fixed byte/time limits is copied completely into the new directory as `native_response.bin`, alongside the exact protocol and `context_verification_receipt.json`. An over-limit or incomplete input retains at most its first 12,000,000 received bytes, marked `RECEIVED_PREFIX_ONLY_NOT_FULL_INPUT` and rejected regardless of its prefix hash. No HTTP request is made. A pre-existing output directory is refused without modification.

To make the fixed public request yourself:

```console
python scripts/fetch_primary_target_context.py --download --output NEW_CONTEXT_DOWNLOAD_DIRECTORY
```

This explicit action uses the named public `ztf_dr21` collection, a one-arcsecond cone around the published source/event direction (277.56025°, −8.22021°), and IPAC-table output. It applies **no time, band, magnitude, NOBS or catalogue-flag cuts**, makes zero retries, and retains received native response bytes and headers. The response cap is 12,000,000 bytes; capped or incomplete responses retain a labelled prefix and are never accepted. The 45-second urllib socket timeout and elapsed checks before and after reads are cooperative limits rather than an OS hard wall-clock guarantee; a read returning after the elapsed deadline is retained but rejected. Local verification uses the same byte/deadline cap. Redirects are refused as HTTP failures. A failed or changed response remains in its new directory with a failure receipt and nonzero exit status.

Frozen version-one byte identity is:

| Item | SHA-256 / size |
| --- | --- |
| `PRIMARY_NATIVE_INTAKE_PROTOCOL_v1.json` | `38d7085b2eeffae5c0e32537c1ca31f7a8cd57f94b153b13d468bc9553a39399` |
| Native public response | `f3fdaebb9a4881213d1db2deb529c2779c9cb5883a089e18c7c8356623c82a84` / 312,255 bytes |

The service can change as observations or processing are updated. A later response may therefore fail the frozen hash gate; it is retained as an **unaccepted new version**, never substituted silently. Matching bytes establish reproduction of this intake, not authenticity, event association, noise calibration or a discovery. The raw observation file is not bundled here; researchers can acquire it directly from the public service under its applicable data terms.

## What the original structural intake establishes

The preserved native response contains 1,032 rows under two returned object IDs: `384212200092273` has 890 `zr` rows and `384312200098636` has 142 `zi` rows. Both include native `catflags` values 0 and 32768. Those IDs are retained as contextual neighbours; neither is automatically adopted as the lensed source or foreground lens. These counts come from the separately saved `NATIVE_ZTF_STRUCTURAL_INTAKE_v1.json`, not from parsing or filtering by this helper.

Keep every calibration field and flag, including magnitude errors, zeropoints, zeropoint scatter, colour terms, exposure identity and catalogue flags. The frozen native response's own header (lines 7–10, under the raw SHA above) explicitly describes `mjd` as the exposure start and `hjd` as its heliocentric midpoint using the input catalogue's mean sky direction. The underlying time scale is unspecified in this intake. Preserve both native columns and their meanings; do not silently call either TDB/TCB/UTC or enable an annual-parallax likelihood from an assumed conversion.

The BHSM interpretation uses ordinary gravitational lensing to constrain an exterior surface-geometric imprint, with one common Einstein/GHY exterior response counted once. This contextual photometry has not yet validated that imprint for Gaia18ajz, measured microscopic interface dynamics, or identified a BH mass. Source direction, foreground-lens location, configuration constraints and BH identity remain separate evidence questions.

Primary paper and service: [Howil et al., Gaia18ajz](https://doi.org/10.1051/0004-6361/202451046), [IRSA ZTF public light-curve service](https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves). Software and reviewer citation: [formal BHSM repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model). The manuscript workspace is not the formal software repository.
