# RC6 implementation and usability evidence

The final wheel is `01463e3a0de90cef7e2b9e9ac325ce2cf3e438f94b0ccb3316a76dc7ae434195`.
The complete product source and isolated installed-product suites each passed
318 tests and 66 subtests. Two wheel builds were byte-identical. The separate
base-only wheel probe installed current runtime dependencies in another fresh
environment, outside the checkout, with optional astrometry absent.

The actual Windows source launcher also passes missing-Python, dependency repair,
explicit optional astrometry installation, occupied-port and HTTP startup checks
in a fresh source directory with spaces.

Actual final-wheel browser checks cover qualified benchmark aliases, JSON/CSV
view export and replay after clearing, retained hidden inadequate/unresolved
cases, and primary-program export. The moving-lens control preserves the exact
synthetic UTF-8 BOM/CRLF input, fits, exports and replays; an altered probability
is refused. Downloaded examples and screenshots are under `browser/`.

These checks establish implementation and workflow consistency. They do not
establish a native Gaia18ajz fit, a new black hole, independent recovery of a
known black hole, universal uncertainty coverage or publication readiness.
Gaia18ajz is a previously published provisional investigation target, with all
eight alternatives retained and the scientific publication gate held.

The first five notebook runs and all previous release receipts remain
historical. The sixth notebook's current installed run is bound separately in
`../notebook06_rc6_receipt_v2.json`. Hosted CI is a separate exact-commit check.
