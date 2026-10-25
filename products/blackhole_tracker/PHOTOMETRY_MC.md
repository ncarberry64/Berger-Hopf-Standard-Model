# Fixed-grid photometry inference

This researcher workspace uses the original apparent-magnitude observations and
reported errors with the unchanged rectilinear PSPL optical model. It replaces
additive Wald or a presumed Wilks threshold with an approximate, constrained-null
nuisance bootstrap at explicitly requested `tE_days` and `u0` values. General
user-input calibration is **PENDING**. The replacement procedure passed all four
predeclared confirmation gates at **two fixed cadence/error/truth designs**:
4,096 independently drawn datasets, 8,192 pointwise tests and 326,304 retained
bootstrap fits. Seven unavailable tests stayed in the denominators as misses.
This result supports those designs only; fitted-nuisance inference remains
approximate and no continuous endpoints were validated. The three old local and
reference-threshold calibration failures remain preserved. The
[versioned evidence guide](docs/PHOTOMETRY_POINTWISE_EVIDENCE_20261025_V1.md)
records all four counts, criteria and source receipt hashes.

In BHSM, a supported gravitational exterior is interpreted as hypersurface
topography. This calculation counts one optical exterior once. A conditional
photometric fit alone does not establish gravitational origin or a black-hole
identity. Mass, lens distance, angular Einstein scale, parallax, absolute lens
motion, horizon and core state remain unavailable.

## Start and retain a run

Open `blackhole-tracker serve --open --page photometry-mc`, upload the versioned
unresolved-observations JSON, enter increasing grid values and explicit seed
components, and validate the plan before starting. Native files can first be
imported through the existing Native photometry workspace. The original JSON
bytes, including a BOM or CRLF line endings, are retained separately from their
canonical observation hash.

The fixed procedure uses 199 predetermined slots, 12 null starts, the reviewed
RAW peak/width starter policy and one unrestricted refinement from the null fit.
The same procedure is used for observed and simulated data. No truth nuisance or
published black-hole mass is supplied to fitting. Fitted-nuisance bootstrap
probabilities remain approximate; the exact simple-null rank argument does not
automatically make this composite-null procedure exact.

The GUI retains every planned node, including failures, cancellations and
unattempted slots. It shows requested-node decisions and probability bounds,
without connecting points into a continuous confidence interval or excluding
unmeasured gaps. Numerical search caps are not physical confidence limits.

The CLI uses the same orchestration:

```text
blackhole-tracker mc-photometry run observations.json --timescales 100 200 400 --impacts 0.1 0.3 0.6 --entropy 20261025 4242 --output NEW_AUDIT_DIRECTORY --wall-seconds 600
blackhole-tracker mc-photometry status NEW_AUDIT_DIRECTORY
```

The output directory must be new. Audit requests and all seed slots are durable
before simulation, generated observations before fitting, and fitted results
before rank comparisons. The isolated worker is supervised for time, storage and
cancellation. Ctrl+C retains a cancelled terminal where possible. A killed or
failed writer's original SQLite bytes and journal are retained; recovery uses a
fresh copy. There is no automatic retry or refit. The GUI displays the durable
workspace path; these directories persist after the server stops.

## Export and replay

Export after a terminal status. Browser ZIP transfers stream unchanged bytes and
are limited to 128 MiB. A 256 MiB workspace budget does not guarantee that its ZIP
fits the browser limit. Larger retained audits use the file route:

```text
blackhole-tracker mc-photometry export NEW_AUDIT_DIRECTORY --output audit.zip --max-archive-bytes 536870912
blackhole-tracker mc-photometry replay audit.zip --mode integrity --output integrity.json
blackhole-tracker mc-photometry replay audit.zip --mode numerical --wall-seconds 120 --output numerical.json
```

`--mode integrity` verifies archive bytes, observation/request identities, durable
records and saved rank arithmetic. It is not scientific numerical reproduction.
`--mode numerical` additionally reconstructs each stored synthetic observation
set and directly re-evaluates every stored finite objective and profile contrast
at its exact saved transformed vector. It does not re-encode rounded physical
parameters, optimize, profile or draw noise. It refuses changed method or observer
sources, missing state/data pairs, ambiguous trace associations or exhausted
budgets. Neither replay mode validates statistical coverage or global optimality.

File export accepts an explicit cap up to 2 GiB; replay has a 2 GiB archive cap,
bounded expansion, time and state counts. Exceeding a cap preserves the original
workspace and any incomplete file; use a fresh destination on the next manual
export. Hashes establish consistency, not authenticity or scientific acceptance.

## Python and local API

`bhtracker.photometry_mc.plan(body)` performs input and request validation without
fitting or RNG. `MCWorkspace(original_bytes, grids, entropy, fresh_directory)`
followed by `.run()` uses the supervised worker. The companion
`photometry_mc_replay.export_workspace` and `replay_bundle` accept file paths for
large audits. Keep private tracing instrumentation inside the isolated worker.

The loopback app exposes `/api/photometry-mc/plan`, `/start`, `/jobs/<id>`,
`/jobs/<id>/cancel`, `/jobs/<id>/export` and `/replay-file?mode=integrity|numerical`.
The last endpoint takes the raw ZIP body as `application/zip`; it uses an owned,
bounded temporary file. The older `/replay` JSON/base64 route remains available
for bounded API clients. The server admits only its local origin.

The formal citation and reviewer repository is
[Berger–Hopf Standard Model](https://github.com/ncarberry64/Berger-Hopf-Standard-Model),
under `products/blackhole_tracker`. The fixed-design confirmation and independent
saved-evidence audit support the limited claim above. They do not establish
general composite-null coverage, calibration at other truths/noise designs,
continuous intervals, lensing origin, known-black-hole recovery or publication
readiness.
