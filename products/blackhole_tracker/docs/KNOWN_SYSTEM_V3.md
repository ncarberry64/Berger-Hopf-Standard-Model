# Versioned known-system Gaussian research engine

The explicit `bhtracker.known_system_v3` API packages the reviewed Gaussian
model v4 and spectral trust solver v6. The existing `joint` v1/v2 interfaces
retain their separate methods. There is no fallback between these engines.

This engine currently accepts the exact 2023 benchmark document or an explicitly
registered wholly invented/actual-cadence simulation. It is **not an adapter for
general user joint observations**. It does not attach the benchmark's metadata,
time convention, exposure samples or uncertainty corrections to another dataset.
The missing 2025 uncertainties remain missing. Registration of a simulation hash
is an identity declaration, not independent validation or calibration evidence.

The native document is kept external. Its SHA256 is
`d2409db410e113872781494ca4d73db57d2a44fd65146c4e7ec2f40828448428`;
the data version is
`OGLE-Mroz2022-corrected_LamLu2023v2-HST21-MAST82.v1`.
Use the existing documented sourcepack/reproduction workflow. No automatic data
download, implicit JSON reserialization or newline normalization occurs here.

## Model and interpretation

The photometric covariance is the unchanged supplied diagonal plus the reviewed
variance-normalized F10-type two-real-exponential Matérn 3/2 approximation
(`epsilon=0.01`) and SHO (`Q=1/sqrt(2)`) components. The model retains exact zero
amplitude faces; coherence at a zero amplitude is unidentified. It does not add a
variance floor. This is a declared Gaussian working hypothesis, not a claim to
reproduce the complete published posterior or its photometry-to-astrometry prior.

The angular data remain relative HST positions with the explicit diagonal
working-independence assumption. The supplied errors already include their
documented corrections; they are not applied again. Actual exposure samples are
averaged with the same declared equal sample weights. Numerical origin plus raw
time offset, angular reference, row identities and first-occurrence instrument
order are retained. The private data-adapter class retains its historical
Student-related name, but this public engine never calls its Student evaluator.

In [BHSM](https://github.com/ncarberry64/Berger-Hopf-Standard-Model), the supported
gravitational exterior is interpreted as surface topography. One Einstein/GHY
response is counted once. No additional potential, microscopic core/interface
law or horizon identification is introduced. A conditional numerical mass at a
working state is not a black-hole classifier or accepted mass interval. Relative
source parallax is not silently converted into an absolute source distance.

Every public result preserves `publication_hold="HOLD"`,
`scientific_acceptance=false`, `known_black_hole_recovery_accepted=false` and
`accepted_mass_interval=null`. Stationarity is not a local/global minimum,
predictive adequacy, calibrated coverage or known-black-hole recovery certificate.
The trust multiplier is a quadratic trust-constraint multiplier; the original
Hessian and covariance are not ridged. Promotion tolerances are algorithmic
progress policies, not statistical acceptance or numerical-error bounds.

## Researcher workflow

The optional `joint-research` environment needs Astropy and the reviewed
`celerite2` API in addition to the normal numerical dependencies. Inspection is
available without those optional imports:

```text
python -m bhtracker.known_system_v3 inspect
python -m bhtracker.known_system_v3 validate INPUT.json --purpose AUTHENTIC2023
```

Python APIs are `availability`, `validate_benchmark`, `evaluate_saved_state`,
`plan_run`, `run_plan`, `export_workspace`, `verify_replay` and `replay_export`.
They require explicit data purpose, exact bytes, chosen states and resource
limits. They do not require internal author/Codex permission JSON files or claims
that a scientific gate has passed. Running a user-selected plan is an explicit
action; simply inspecting or planning runs no optical model or optimizer.

An evaluation state contains the five centered geometry coordinates, source
fractions in declared instrument order and four logarithmic covariance
coordinates. Each case specifies `state` and `zero_components` (an explicit
subset of `matern`, `sho`). Full parameter names and active-coordinate maps are
exported. Even inactive covariance coordinates remain stored as computational
representations; they do not become measured coherence values.

```text
python -m bhtracker.known_system_v3 evaluate INPUT.json --purpose AUTHENTIC2023 --state STATE.json --output SAVED.json
python -m bhtracker.known_system_v3 plan INPUT.json --purpose AUTHENTIC2023 --cases CASES.json --output PLAN.json
python -m bhtracker.known_system_v3 run PLAN.json --workspace NEW_DIRECTORY
python -m bhtracker.known_system_v3 export NEW_DIRECTORY --output AUDIT.zip
python -m bhtracker.known_system_v3 replay SAVED.json --mode integrity
python -m bhtracker.known_system_v3 replay AUDIT.zip --mode numerical
```

`STATE.json` is `{"state":[...],"zero_components":[]}`. `CASES.json` is a list
of such objects; there is no implicit published-mass seed. Do not select branches
or covariance hypotheses by agreement with a published or generating mass.
Imported development endpoints are finite continuations, not independent searches.

Plans expose every method/resource setting. The current engineering limits admit
at most 128 explicit cases, 2,002 full evaluations per case, 16,016 full attempts
and 144,144 internal covariance attempts overall. Users can reduce these limits.
All internal trials, lower values, failures, unknown/unattempted cases and own
replays are retained. The source spectrum/domain is unchanged. The numerical
worker uses a fresh exclusive directory and a separate installed subprocess;
it never retries automatically. A cancelled process or resource stop is not a
zero likelihood or a scientific exclusion.

Ctrl+C terminates and waits for the owned child, then writes a cancelled terminal
with every missing case retained as unknown. Durable computed prefixes remain
available. A computation or final verification that finishes after its declared
deadline cannot be promoted to a successful case/replay; its computed evidence
is retained with the deadline qualification.

Original input is bounded at 32,000,000 bytes; this adapter supports its three
named instrument groups, at most 25,000 photometric rows and 128 angular rows.
An input exceeding this engineering domain is refused as a whole, without
dropping observations. Expanded JSON reads are bounded separately. The working
audit/result storage budget is at most 1 GiB, plus bounded terminal summaries
and process logs; preserving a stopped workspace is important.

## Export and replay

Integrity verification checks declared bytes/structure/source identities. It is
not authentication of an observation, scientific result or caller's hash registry.
Numerical replay recomputes saved-state objectives/gradients and observer-array
identities, without optimizing or generating new simulations. It requires the
recorded numerical runtime; exact represented disagreement is retained as a
failed comparison, not relaxed until a desired physical answer appears. Runtime
versions alone do not prove identical BLAS/platform arithmetic.

ZIP exports are allowlisted, bounded to 512 MiB and read without extraction or
executing archive code. Numerical ZIP replay defaults to at most 16 saved-state
attempts and a cooperative 120-second limit. Unattempted states are explicitly
unknown and prevent a claim of complete numerical verification. Large exports,
time limits and numerical differences preserve the original workspace/results.
Each saved state must match its enclosing plan's exact input, settings, runtime
and case face. Export preflight applies the same expanded/structured read limits
as replay before creating an archive.

Mass profiles, independent search, systematic sensitivities, refit prediction and
coverage require their separate validation protocols. This packaging layer does
not release those gates or the scientific hold.
