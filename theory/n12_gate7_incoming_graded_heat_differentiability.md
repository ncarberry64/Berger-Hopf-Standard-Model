# Gate-7 incoming graded heat differentiability

Status: `INCOMING_SHRINKING_ARM_GRADED_HEAT_DIFFERENTIABILITY_CERTIFIED`.

The incoming compliance theorem removes the short-arm Laurent pole in every
fixed channel.  It remains to justify differentiating before the retained
infinite angular supertrace.

The scalar and factorized product-Dirac transfer generators depend at most
quadratically on the unit-radius angular level, and one first geometry jet
adds only a fixed polynomial loss.  On the certified compact coefficient
tube, the regular compliance transfer therefore has a majorant of the form

`K*(1+mu)^4*exp(c*T_form*mu)`

after division by the formation amplitude.  Here `K` is finite and
independent of the angular level and positive amplitude.  The power four is
a conservative common envelope for the scalar, gauge, HS, and paired-Weyl
first-jet generators; it is not a fitted exponent.

The already-certified one-seam heat estimate supplies the angular weights

`exp(-a*m^2)`

in the scalar/gauge/HS sectors and

`exp(-a*(n+3/2)^2+b*(n+3/2))`

in the Weyl sector, with `a>0`.  The extra compliance-transfer factor changes
only the linear coefficient.  Thus the absolute derivative majorants are

`4*m^2*(1+m)^4*exp(-a*m^2+c*T_form*m)`,

`24*(m^2-1)*(1+m)^4*exp(-a*m^2+c*T_form*m)`,

and

`48*(n+1)*(n+2)*(1+n+3/2)^4`
`*exp(-a*(n+3/2)^2+(b+c*T_form)*(n+3/2))`.

All three sums converge by the root test, uniformly on the entire certified
positive-amplitude box.  Dominated differentiation is therefore valid and

`D_lambda Gamma_heat=lambda*H_heat(lambda)`

with `H_heat` uniformly finite.  The heat term is not set to zero.  This
theorem closes the derivative/supertrace interchange, but does not evaluate
or sharply enclose `H_heat`; consequently it does not yet compare the heat
coefficient with the strictly signed zeta coefficient and does not decide the
joint KKT equation.

No internal response is zeroed and no source, selector, cutoff, endpoint,
recurrence condition, scale, gate, or chord is introduced.
