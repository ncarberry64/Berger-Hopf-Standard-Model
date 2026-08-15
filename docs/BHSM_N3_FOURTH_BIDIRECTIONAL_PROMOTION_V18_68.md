# BHSM N=3 fourth bidirectional promotion v18.68

Status: **VALIDATED / PROMOTED.**

- exact `||F_376||`: `0.811248056430707` (reduction `0.000254622030594`);
- event magnitude: `0.083931074020022`;
- global eta minimum: `0.774255587310955`;
- fresh child: 26 variables, 14 rows, rank 14;
- trace / constraint / momentum: `3.5e-14 / 2.04417e-10 / 2.0990091e-8`;
- independent two-scale flux envelope: `9.668406268e-6 < 2e-5`;
- child eta: `0.99997781808237`;
- persistence: duration `1e-4`, maximum constraint residual `5.9162e-11`, minimum eta `0.999972991535512`;
- nonzero relative evolution retained.

The physical solve remains the unchanged square 376-variable KKT system with explicit event multiplier. The invalidated solver interpretation is not physics and is not reasserted. `FULL_BHSM_COMPLETE = FALSE` because `F_376` remains nonzero.

Active dependency: `CONTINUE_PHYSICALLY_ADMISSIBLE_EXACT_376_ROW_DESCENT_FROM_THE_LATEST_ACCEPTED_FRONTIER_TO_F376_ZERO`.
