# Nonlinear Threshold Law Candidates

Status: `NONLINEAR_THRESHOLD_SIGNAL_INDICATED`

Threshold laws may replace a simple heat-kernel exponential if the existing engine effectively saturates or branches response by mode role. These are candidate diagnostics only.

| Family | Parameters | RMS to existing bare | Official | Overfit risk |
| --- | --- | ---: | --- | --- |
| `exponential_action_control` | `single_universal_parameter` | `2.714934256444424` | `False` | `False` |
| `bounded_threshold` | `single_universal_parameter` | `2.6026920512069673` | `False` | `False` |
| `logarithmic_threshold` | `single_universal_parameter` | `1.8076741338301048` | `False` | `False` |
| `branch_rank_threshold` | `single_universal_parameter` | `1.4880093492548556` | `False` | `False` |
| `branch_type_weighted_threshold` | `universal_a_b_c_not_sector_specific` | `None` | `False` | `True` |

Forbidden tuning rules: no sector-specific parameters, no per-particle response factors, and no retrofitting frozen predictions.
