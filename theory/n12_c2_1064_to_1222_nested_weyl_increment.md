# N12 C2 1064-to-1222 nested Weyl increment

Status: `C2_NESTED_CORE_SEMIGROUP_CERTIFIED_CURRENT_WEYL_NET_NOT_CONVERGED`.

The 1222-segment coefficient path contains the 1064-segment path exactly,
including every stored node log-radius and proper-duration interval.  Split
the longer path at node 1064.  For each retained scalar or factorized
product-Dirac channel and every real `z<0`, let

`L_1064_to_1222(z)`

be the positive birth impedance of the added 158-segment tail with a
Dirichlet far form-core edge.  If `Phi_0_1064(z;L)` denotes the inverse-free
Möbius transfer of a nonnegative load `L` through the old prefix, exact
associativity gives

`M_1222^D(z)=Phi_0_1064(z;L_1064_to_1222(z))`.

Differentiating this identity gives the exact backward-cotangent split

`D_prefix M_1222^D=D_prefix Phi_0_1064`,

`D_tail M_1222^D=(D_L Phi_0_1064) D_tail L_1064_to_1222`.

Thus the inverse-free operator adjoint composes across the stored core split
without a forward column solve.  This closes the finite-core transfer
cotangent algebra; it does not supply the still-missing action-owned map from
reset-quotient directions to coefficient and duration histories.

Positivity of every local impedance map and its strictly positive Möbius
determinant gives the strict bracket

`Phi_0_1064(z;0)<M_1222^D(z)<M_1064^D(z)`.

This statement is parametric for the whole negative real resolvent axis; the
stored probes are reproducibility crosschecks only.  The current low-axis
Dirichlet Weyl value changes by almost its full 1064-core magnitude when the
158 certified segments are appended.  Thus the two available truncations
are not yet a numerically converged finite-core value net.  This does not
contradict the abstract Friedrichs exhaustion theorem, which is an
asymptotic existence and uniqueness statement.

The nesting replay also exposes a numerical artifact in the earlier engine:
an arbitrary-precision downstream load was converted to binary64 before
composition.  The inverse-free interface now accepts a decimal load without
that conversion, so split-core composition replays to the declared decimal
precision.  The same arbitrary-precision replay is applied componentwise to
the coefficient and duration cotangents; the stored crosschecks retain more
than 25 relative decimal digits across the full probe range.  No kinetic or
Dirac block inverse is formed.

Neither the Dirichlet truncation increment nor its sample grid is the
physical heat-minus-zeta force.  The far edge remains a form-core
truncation, not an event, stop, or boundary choice.  Gate 7 still requires
the source-contracted physical reset-quotient Cauchy tail (or an actual
later event/canonical stop), with the incoming compact arm assembled in the
same joint operator.

`FULL_BHSM_COMPLETE=false`.
