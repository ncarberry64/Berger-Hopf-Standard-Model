# Paired uniform trial mean-value integration — 2026-09-13

The complete uniform mixed-variation calculation tightens the actual frozen
trial column 14 at endpoints 13 and 14. The independently paired result is
then carried into interval 13's fixed-frame local HS column using the original
paired midpoint data. These are numerical enclosures, not experimental data.

| Quantity | Previous maximum radius | Selected maximum radius | Coordinates tightened |
| --- | ---: | ---: | ---: |
| Endpoint 13 trial action | 0.600447816 | 0.0931377781 | 99/99 |
| Endpoint 14 trial action | 0.508943341 | 0.0632021946 | 99/99 |
| Local DL column | 71.7877277 | 65.6305918 | 74/74 |
| Local DR column | 70.0433402 | 63.9145489 | 74/74 |

The endpoint calculation retains the original seven bordered solves and all
scalar contractions. It encloses the mixed Hessian against all 75 scaled tube
directions and verifies containment of every corresponding point column.
The same-family smoothness certificates support integration along each segment;
the longitudinal absolute support and transverse Euclidean support give a
uniform mean-value bound, with the complete verified anchor uncertainty.
The original primal families, eigenvalue enclosures, frames and radii are retained.

The local calculation uses the tighter endpoint actions in both the direct
endpoint term and midpoint chain direction. It retains the original verified
midpoint center action, full midpoint derivative, and complete center-shift
remainder. The existing preconditioned split algebra accounts for the shared
endpoint uncertainty. This integration evaluates no new action derivatives.

Each endpoint and the local result were evaluated by two fresh processes with
byte-identical records and data before downstream use. The companion artifact
records source hashes and the exact record/data/reproduction receipt paths.
Per-run endpoint reports retain independent_recomputation=false; paired receipts
supply that separate evidence.

This is one local trial column. The other trial columns, full-path contraction,
physical quotient and moving-frame terms remain open. Gate 7 and full BHSM
completion remain false. The existing Museum's scalar certificate and frozen
physical-prediction files are unchanged.

## Reproduction

Run scripts/certify_n12_gate7_trial_mean_value_derivative.py for interval 13,
column 14, separately for each side. Use the original paired primal roots:
tmp/bhsm_bootstrap_repeat_primal_pair_20260912/mean_value for the left and
tmp/bhsm_endpoint14_primal_first_variation_pair_20260912/value for the right.
Use tmp/bhsm_directed_trial13_pair_20260913 as the directed evidence root.
Run first and repeat in fresh processes and require exact record/data agreement.

Run scripts/certify_n12_gate7_mean_value_trial_local_integration.py with
--interval 13 --column 14, --evidence-root
tmp/bhsm_split_directed_trial13_pair_20260913, --mean-value-root
tmp/bhsm_endpoint_trial_mean_value_pair_20260913, and --previous-pair
tmp/bhsm_preconditioned_split_trial13_pair_20260913/value. Again use distinct
first/repeat output directories and compare bytes before issuing a receipt.

The bound LIVE sources are immutable. Git text normalization can change source
hashes; reproduce with the recorded exact source bytes and prerequisite bindings.
