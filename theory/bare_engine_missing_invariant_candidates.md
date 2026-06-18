# Bare Engine Missing Invariant Candidates

Status: `MISSING_INVARIANT_DIAGNOSTIC_CANDIDATE`

This note lists shape-only invariant candidates. None is official.

| Family | Formula | Status | Official | Control | Diagnostic correlation |
| --- | --- | --- | --- | --- | ---: |
| `sector_operator_weighted_action` | `lambda_O=(O_q*q)^2+(O_j*j)^2` | `SECTOR_OPERATOR_WEIGHTING_DIAGNOSTIC` | `False` | `False` | `-0.0017541003202771167` |
| `signed_boundary_action_magnitude` | `lambda_signed=abs(O_q*q+O_j*j)` | `DIAGNOSTIC_CONSTANT_ON_TARGET_SECTORS` | `False` | `False` | `0.10470261497845296` |
| `cross_coupled_berger_action` | `lambda_cross=q^2+j^2+rho*q*j` | `ORIENTATION_CROSS_TERM_DIAGNOSTIC` | `False` | `False` | `-0.8830559119992455` |
| `branch_gap_action` | `lambda_branch_gap=N-N_min_nonzero_sector` | `BRANCH_ASSIGNMENT_DIAGNOSTIC` | `False` | `True` | `-0.9722593540454771` |
| `sector_response_weighted_action` | `lambda_response=N/(Omega_star^2-1)` | `CHANNEL_DIMENSION_NORMALIZATION_ALREADY_WEAK` | `False` | `False` | `-0.6887205114247605` |
| `orientation_sensitive_action` | `lambda_orientation=N+gamma*(O_q*q)*(O_j*j)` | `ORIENTATION_CROSS_TERM_DIAGNOSTIC` | `False` | `False` | `0.29430559870696604` |

Simple degree/channel normalization already failed in the residual-autopsy sprint. Branch-gap subtraction is marked control/candidate because sector-relative subtraction needs derivation. Cross/orientation terms and nonlinear threshold laws remain diagnostic targets only.

Guardrail: `NO_NEW_OFFICIAL_MASS_FORMULA_GUARDRAIL`.
