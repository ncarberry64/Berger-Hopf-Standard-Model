# Candidate atlas

Candidate selection is useful even when the observations do not identify a precise mass. The atlas records evidence and where to investigate; a lensing event alone does not identify a black hole.

Open **Candidate sky atlas** in the local app, use `Start_Blackhole_Tracker_Atlas.cmd`, or run:

```text
blackhole-tracker serve --open --page atlas
blackhole-tracker atlas list --tier BLACK_HOLE_SEARCH_TARGET --output targets.json
blackhole-tracker atlas export --tier BLACK_HOLE_SEARCH_TARGET --output targets-replay.json
blackhole-tracker atlas replay targets-replay.json --output restored-targets
```

Existing output files/directories are refused. `atlas validate inventory.json` checks an external versioned inventory. `atlas list` also accepts `--query`, `--cohort`, `--flag`, and `--sort event_id|ra_deg|tier`. Python users can call `bhtracker.candidate_atlas.load_inventory`, `filter_events`, `create_replay` and `validate_replay`. The library returns the original inventory text separately from parsed records so replay can preserve its exact UTF-8 bytes.

The reviewed v3 inventory combines the frozen 100-event pilot with all 59 Wyrzykowski et al. (2016) parallax events. Four independently checked shared catalog identities yield 155 distinct cohort records. All 89 inadequate pilot fits, eleven scalar nonrejections and two qualified pilot followups remain present. Scalar nonrejection is not a comparison against intrinsic variability or proof of black-hole lensing. All 142 published parallax model modes are retained as model metadata. Twenty-six older public tables were located and hash-verified (19,068 rows); 33 remain unavailable. The older 2015 data are not asserted to equal the 2016 reduction, calibration or outlier masks. No new parallax fit is performed by this atlas.

| Stage | Meaning |
|---|---|
| Review required | Preserve the catalog entry and its failed, flagged or unassessed tracker model. |
| Supported lensing event | Attributed literature supports a lensing interpretation; this is not an engine black-hole identification. |
| Black-hole search target | Specific screening or literature evidence warrants investigation, with alternatives retained. |
| Black-hole candidate | Would require discriminating evidence beyond generic lensing; no cohort entry currently receives this stage. |
| Strongly supported identification | Would require sufficient evidence against relevant alternatives; none is independently established by this engine. |

The three search targets have different bases. OGLE3-ULENS-0585 and OGLE3-ULENS-3092 passed the frozen photometric followup screen. Their fitted durations do not supply a mass. PAR-13 has a disputed, prior-dependent literature interpretation: unreliable Gaia source astrometry and an alternative lower-mass inference are explicit. The historical thirteen dark-remnant-consistent events are not thirteen black holes. The 2021 reanalysis revises several historical interpretations, including PAR-02 toward a roughly 0.9-solar-mass star under its adopted population/source-motion assumptions. These conditional literature values are not supplied as observations to the tracker likelihood.

The separate benchmark record, OGLE-2011-BLG-0462/MOA-2011-BLG-191, has strong published black-hole support. Its label comes from the literature. The engine's independent recovery remains unresolved. It is outside the 155-event cohort and outside candidate ranking.

Markers show source/event catalog directions. J2000 is the catalog equinox, not a supplied observation epoch. Lens position, position uncertainty, distance, mass, absolute proper motion and radial velocity remain null. The atlas supplies no three-dimensional or propagated lens positions. Blank sky is not evidence that black holes are absent; survey selection and alignment govern which events enter the catalogs.

JSON replay retains the entire inventory, including unselected records and the separate benchmark, plus the chosen filters and exact selected records. SHA-256 checks both exact text layers and their consistency. It is not an authenticity signature, a new fit or an uncertainty-calibration certificate. CSV contains the filtered records, source roles, null policy, metadata and provenance; use JSON replay to retain the complete inventory. Large numeric identifiers must be strings to preserve browser/Python precision.

The paper's `candidate_atlas_20261023` metadata package contains the portable builder, factual metadata snapshots, source hashes, tests and reviewer instructions. It rebuilds offline without native photometry, article HTML, the full catalog or the full 2025 observed input. Optional original-source verification remains separate from the offline metadata rebuild. The bundled runtime inventory has SHA-256 `4a76300f0e0e3883a0c9c343e1e0c5fbead595c9b4f333aaa01ec05c9ec9debc`.

BHSM interpretation: one ordinary compact-lens Einstein/GHY exterior optical response is counted once. No extra core/envelope lensing potential is added. These observations do not identify a membrane deformation, nongeometric core state or horizon.

The formal software, metadata and reviewer repository is [BHSM GitHub](https://github.com/ncarberry64/Berger-Hopf-Standard-Model). Primary cohort/revision sources: [Wyrzykowski et al. 2016](https://arxiv.org/html/1509.04899v2), [Mróz and Wyrzykowski 2021](https://arxiv.org/html/2107.13701v1), and the separate [2025 known-system analysis](https://doi.org/10.3847/1538-4357/adbe6e).
