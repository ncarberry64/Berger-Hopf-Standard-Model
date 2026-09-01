# Gate-7 direct Hermite--Simpson multiple-shooting source

The second interpolation halving increases the maximum exact flow defect, and
the third signed-Green Newton replay also increases it after rebuilding both
the graph Jacobian and constraint tangents.  These two routes are therefore
retired as center solvers.

On the best second-Newton endpoint center, recover the exact retained field at
every Gauss-3 midpoint from `path_rate - measured_defect`.  For each interval
materialize the augmented Hermite--Simpson block residual

`x_(i+1)-x_i-h_i (f_i+4 f_mid+f_(i+1))/6`.

This supplies the explicit `370 x 99` source for a direct block Newton or
Krawczyk solve.  It is not the solution of that system and is not interval or
physical operator authority.

`FULL_BHSM_COMPLETE = FALSE`.
