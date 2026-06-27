# Theorem Closure Sprint A

Sprint A implements executable closure attempts for `X_ch`, the neutrino
physical basis/scale/Dirac-Majorana theorem, and standalone CP `O_int`.
Seventeen proof gates cover formal statements, domains, actions, callables,
artifacts, provenance, admissibility, units, calibration, tests, and failure
modes.

No theorem is promoted in this sprint. The attempts identify existing local
source artifacts and return exact missing objects while preserving production
and runtime gates.

| Theorem | Result | Promotion |
| --- | --- | --- |
| `X_ch` | `OPEN_EXACT_MISSING_THEOREM` | no |
| neutrino basis/scale | `OPEN_EXACT_MISSING_THEOREM` | no |
| standalone CP `O_int` | `OPEN_MISSING_INTERACTION_ATTACHMENT` | no |

Theorem closure requires executable artifact-backed support; narrative plausibility is not enough.

Reference values, including PDG values, are comparison inputs only and are never theorem inputs.

A partial localization is not a production prediction.

Runtime-disabled software gates remain disabled until live external validation passes.

The neutral operator kernel is not promoted to a physical neutrino mass matrix without a physical basis, dimensional scale, and Dirac/Majorana convention.

Sprint B now provides the focused CP `O_int` stage decomposition without
changing Sprint A's non-promotion result. See `docs/cp_o_int_sprint_b.md`.
