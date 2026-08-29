# Gate-7 causal Y/Z1/Z2 margin budget

The frozen Decimal Gauss-8, PROP16 correction is compared with two independent
cross-discretization profiles on the same retained quarter-step history:

\[
 r_Y(t_i)=\max_{k\leq i}\|c^{(8,32)}_k-c^{(6,32)}_k\|_2,
 \qquad
 r_{Z1}(t_i)=\max_{k\leq i}\|c^{(8,32)}_k-c^{(8,16)}_k\|_2.
\]

The retained certified Taylor--Volterra Z2 macro radius is interpolated onto
the fine grid and added to these two bookkeeping radii.  Every term is zero at
the reset.  Thus the construction respects the causal initial condition and
does not replace it with a uniform halo that would obscure the tiny positive
birth descriptor.

For the explicit stored-profile proxy, every binary64 dense descriptor
coefficient is replayed as an exact rational number.  The frozen descriptor
correction and proxy radius are linear on each fine segment.  Exact Bernstein
range checks prove positivity through the old stored hit.  The unit proxy has
strict margin, and the same exact replay remains positive under more than
211-fold uniform inflation of the combined proxy radius.

This is a budget and routing result, not an outward interval theorem.  Neither
Gauss-6/8 nor PROP16/32 cross-discretization is promoted to a truncation-error
bound.  The remaining theorem is now quantitatively localized: construct a
causal outward signed-Y plus PROP16-Z1 radius below the reported inflation
headroom, rebuild the center-dependent Z2 cone on that radius, and apply scalar
interval Newton on the later shifted terminal segment.

No action term, source, selector, scale, recurrence, event, gate, or chord is
added or changed.
