# Current-Green signed transverse tensor recovery

The complete 740-center transverse campaign evaluated the signed tensors

\[
 B_{aij}=D^2F_a[EV_i,EV_j]
\]

on the 73-dimensional complement of the current Green axis, but persisted
only basis-invariant total and output-row Frobenius norms.  That was sufficient
for a center unit-sphere majorant.  It is not sufficient for the present
causal representation: applying componentwise absolute values before the
frozen test-frame, reduced-inverse, and Green products discards the signed
output correlations and fails even in an optimistic center-only two-radius
screen.

The recovery campaign therefore reruns the unchanged signed center kernel and
persists its in-memory `99 x 73 x 73` tensor.  No derivative is recomputed by a
different formula.  A lossless return option exposes the same local array from
which the published norms are computed; the default norm-only campaign path is
unchanged.  A shard is admitted only when
both

\[
 \|B\|_{\rm F}
 \quad\hbox{and}\quad
 \bigl(\|B_a\|_{\rm F}\bigr)_{a=1}^{99}
\]

agree with the previously published shard to a relative tolerance of
`5e-13`.  The exact orthonormal complement basis used to evaluate `B` is
persisted with it and is checked against the corresponding Green axis.  This
prevents a later null-space recomputation from silently rotating tensor input
coordinates.  The published shard hash, algorithm fingerprint, worker
identity, and elapsed time are retained with every recovered tensor.

The recovered tensors allow the Hermite--Simpson second variation, midpoint
incidence, reduced solve, and causal transport to be composed while signs are
still present.  Norms are taken only after that composition.  This is a
representation recovery, not a change of action, trajectory, mesh, selected
eigenline, Green axis, preconditioner, precision contract, or two-radius norm.

The recovery remains center data.  It does not supply the transverse outward
neighborhood remainder, a two-radius self-map, Gate-7 closure, physical
background authority, or `FULL_BHSM_COMPLETE`.
