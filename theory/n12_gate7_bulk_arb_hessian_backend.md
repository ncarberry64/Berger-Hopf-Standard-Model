# Bulk Arb matrix transfers in physical Hessian evaluation

The retained physical Hessian graph repeatedly transfers rectangular arrays
of Arb entries into and out of Arb matrices. The bulk adapter replaces only
these two transfers, retaining C row-major order, exact binary64 input
conversion, and every Arb midpoint and radius. A vector remains a column
matrix. Empty and higher-rank layouts are rejected.

The source-guarded context substitutes a flattened `arb_mat` constructor and
`numpy.fromiter(matrix.entries())` conversion. It changes no arithmetic or
contraction order and restores both parent functions even after an exception.
Base action jets and the eigenline are prepared before installing the adapter.

The backend uses its own algorithm identifier, row directory, input/source
fingerprint, and physical DF/output integration directory. The parent factored
and original campaigns and certificates are preserved. Worker count remains
at most six and each invocation retains the twelve-worker-hour upper cap.

Synthetic transfer timings are not full-kernel speed measurements. Adoption
for the next numerical campaign requires a bounded comparison against the
unchanged factored physical graph. No speed improvement closes a scientific
gate, identifies a physical quotient, or supplies missing predictions.
