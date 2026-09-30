# Current N12 DOP853 internal bordered response

This calculation consumes the current retained center and the identical
1,395-cell, 185-interval projector-refined cover. It changes neither the
trajectory nor the action. The spectral gap and instantaneous bordered
inverse are inherited from the closed spectrum/projector/inverse records.

With weighted action coordinates, the retained internal source is

`r = W_red ([W_q D_q S, 0] - H_red,q (W_q v))`.

Only the external Cauchy birth source is zero. The internal source is
assembled with its signs before its center norm or center response is
measured. No separate seam force is inserted.

For one cell, let `m=mean(B_i)` be the same Bernstein control mean used by
the spectrum and projector. Write `c=B(1/2)` and `t=B'(1/2)/2`. Integral
Taylor remainder vertices are `R_i in {0,B''_i/8}`. The curve displacement
has the representation

`B(u)-m = (2u-1)t + sum_i theta_i (R_i-(m-c))`,

where the remainder coefficients form a simplex. The residual offset
`m-c` is retained explicitly. The two-block scaling
`1/a^2+1/b^2=1` encloses this product in a unit coefficient ball.

The raw-source driver evaluates the gradient, mixed-Hessian and linear
configuration product-rule terms on that ball. In the retained metric,
`W_red[:37]=1`. Thus the exact action-dual gradient output leg is
`W_q*W_red_v`, once, and the reduced Hessian leg is `W_red`. These dual
pairings are tested against the source formula. The direct driver rebuilds
only geometry and evaluates four majorants; it reuses all existing center
solves and performs no new action-Hessian or directional-Hessian jets.

The initial driver also retains the older preconditioned source diagnostic,
whose gradient leg contains `W_q^2`. This is not identified with the exact
raw gradient dual leg or promoted to a response-level Neumann certificate.
Its conversion to a raw norm remains a conservative fallback: if `A` is
the invertible center spectral preconditioner, multiplication by
`||A^-1||` controls the weighted raw gradient, and `W_q>=1` controls the
unweighted raw gradient. The direct raw calculation is preferred.

The promoted finiteness statement uses only

`sup ||r|| <= ||r_center|| + raw_source_variation_upper`,

`sup ||K_border^-1 (r,0)|| <= instantaneous_inverse_upper * sup ||r||`.

It does not require the separate fixed-center relative-operator diagnostic
to satisfy `eta<1`. Failed diagnostics remain explicit. A partial snapshot
does not certify the entire cover; the report records its included cell
count and complete-cover flag.

The full direct-raw report includes all 1,395 cells and passes validation.
Its maximum source norm cap is `1366.3964864279828`, and its maximum
instantaneous response norm cap is `10298520119.434927`, owned by interval
182, subspan 2 of 4. Every direct raw-source variation bound improves the
initial norm-conversion fallback. All 1,395 fixed-center Neumann diagnostics
remain open; none is used to certify the promoted uniform response cap.

This closes finite internal-source/response bounds on the stored curve
when all cells are included. It does not close the correlated history tube,
transverse nonlinear remainder, reset-to-stop witness, scalar first-hit interval,
or strict earlier domain margins. The sharper uniform response cap still
loses cancellation between the RHS and differentiated bordered operator;
that correlation must be retained where the Green proof requires it.
Gate 7 remains active, and physical prediction values are unchanged.
