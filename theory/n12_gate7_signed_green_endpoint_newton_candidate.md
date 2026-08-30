# Gate-7 signed Green endpoint Newton candidate

For the measured Hermite collocation defect

`d = y_hat_prime - F(y_hat)`,

apply the retained reduced graph equation

`e_prime = J e - d`

with the defect sign preserved.  The three retained Gauss samples in each fine
cell are propagated to the right endpoint using the existing linearly varying
371-node graph Jacobian and sixteen substeps per quarter cell, matching the
partition used by the frozen Taylor26 carrier.  Projection occurs only at the
complete retained two-action-unit macro seams.

This materializes one causal endpoint Newton correction.  It is not promoted
until the direct action constraints and selected descriptor are replayed on
the corrected endpoints and the resulting dense flow defect is reduced.

`FULL_BHSM_COMPLETE = FALSE`.
