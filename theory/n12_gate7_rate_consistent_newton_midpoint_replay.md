# Rate-consistent Newton midpoint replay

All 370 Hermite--Simpson midpoint augmented states are rebuilt from endpoints
whose state, selected descriptor, and endpoint rate are mutually consistent.
The retained exact field is evaluated directly at every midpoint.  Strict
reduction relative to the repaired `1.800590017529095e-6` source is the sole
acceptance criterion for this Newton step.
