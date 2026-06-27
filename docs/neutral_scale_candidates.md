# BHSM Neutral Scale Candidates

The v1.0 offline inventory classifies possible scale sources before any unit
conversion is attempted.

| Candidate | Classification | Unit eligibility |
| --- | --- | --- |
| `tau` | `DIMENSIONLESS_ARTIFACT` | no |
| `sigma` | `DIMENSIONLESS_ARTIFACT` | no |
| `kappa_H`, `mu_H` | `DIMENSIONLESS_ARTIFACT` in their local action context | no |
| overlap width and Berger anisotropy | `DIMENSIONLESS_ARTIFACT` | no |
| `dmu_boundary dt` | `AUTHOR_ONTOLOGY_CONDITIONAL` symbolic measure | no physical normalization |
| neutral background energy density | `MISSING` | unavailable |
| W calibration | `EMPIRICAL_FORBIDDEN` as theorem input | comparison/calibration only |
| electron-neutrino upper limit | `EMPIRICAL_FORBIDDEN` as theorem input | comparison only |

No candidate is promoted from a dimensionless internal constant to an eV/GeV
scale by notation alone.

