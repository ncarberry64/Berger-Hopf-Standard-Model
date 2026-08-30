# Gate-7 correlated signed-descriptor Newton replay

The desingularized (C^2) state is the 98-dimensional action state together with
an independently carried nonnegative signed descriptor.  Near the retained stop,
the selected eigenvalue is at binary64 noise scale, so reselecting it after each
constraint projection does not define a reproducible Newton map.

For endpoint (i), let (y_i) and (s_i) be the accepted parent state and signed
descriptor, let (g_i=D\lambda(y_i)) in action coordinates, and let the requested
Newton state correction followed by constraint projection produce the actual
action displacement \(\delta y_i\).  This replay transports

\[
  s_i^+ = \max\{0,\;s_i + g_i\,\delta y_i\}.
\]

The exact cancelled field is then evaluated with (s_i^+) supplied explicitly.
The binary64 selected eigenvalue is retained only as a diagnostic fiber residual.
Hermite--Simpson midpoints carry the endpoint descriptors and descriptor rates in
the same 99-dimensional interpolation and likewise evaluate the exact fixed-
descriptor field without numerical re-selection.

This is a numerical nonlinear replay of a first-order correlated descriptor
transport.  It is not interval authority, does not certify continuous shadowing,
and does not by itself close Gate 7 or BHSM.
