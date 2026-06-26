# BHSM Gauge Field Target Dictionary v0.5

Machine-readable artifact:

```text
artifacts/BHSM_gauge_field_target_dictionary_v0_5.json
```

The gauge dictionary includes target conventions:

| field entry | target group | status |
| --- | --- | --- |
| `gauge_gluon_target` | `SU(3)_c` | `STANDARD_HEP_TARGET_WITH_BHSM_COUPLING_CANDIDATE` |
| `gauge_weak_target` | `SU(2)_L` | `STANDARD_HEP_TARGET_WITH_BHSM_COUPLING_CANDIDATE` |
| `gauge_hypercharge_target` | `U(1)_Y` | `STANDARD_HEP_TARGET_WITH_BHSM_COUPLING_CANDIDATE` |

These are target conventions with BHSM coupling candidates. They are not a
completed BHSM production gauge theorem and are not UFO-ready.

Phase Three-D treats vector normalization as `Z_A,target = 1` only as a
standard interface convention, not as a BHSM-derived dynamical prediction.

Phase Three-E keeps the same target gauge group convention and exports
scheme-conditional coupling candidates. These candidates require a reference
scale, threshold/running scheme, renormalization scheme, and gauge fixing
convention before production use.
