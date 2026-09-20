# Interval-14 shared-entry continuation — work in progress

The requested certificate is `sup_D |e_a| < 0.000394150` for the zero-based
right entry `73 <- 14`. It is **not yet certified**. Gate 7 remains open;
no transverse budget debit has been made.

Interval 13 is a frozen input lemma. This continuation does not reevaluate
its certificate. It preserves the original interval-14 physical domains,
including all 249 midpoint parameters.

The exact endpoint-to-midpoint dependency graph, implicit equations,
normalization, and Taylor residual argument are documented in
`theory/n12_gate7_interval14_entry_taylor.md`.

The first endpoint enclosure lost too much correlation in the descriptor
output. Its relaxed tail transport bound was approximately `0.002683`,
above the entry target. This was a failure of that enclosure to certify
the target, not a physical counterexample.

The complete four-block adjoint and the identity `Y = Y - beta G` on the
implicit solution graph reduced the endpoint descriptor derivative tail
from approximately `6.4300521e-9` to `3.9638265e-14`. The resulting combined
endpoint tail transport bound is approximately `3.6340656e-6`.
These are first-run intermediate results, pending the complete independent
reproduction required for the final entry certificate.

The active midpoint calculation shares the endpoint nonlinear remainder
parameters between both occurrences in the transport formula. Its final
scalar contribution will be formed before taking support bounds. The
remaining sequence is the midpoint scalar enclosure, comparison with the
frozen point anchor and first jet, frozen full-history transport, independent
reproduction, and only then a budget-ledger update.

Focused checks of the Taylor arithmetic, original-domain implicit inverse
argument, shared transport cross term, and coupled adjoint passed. Two
isolated scalar-contraction processes also matched an existing serial
Taylor term byte-for-byte. That backend check is not independent
reproduction of the complete entry certificate.

Working evidence is retained under `tmp/gate7_vector_20260919/`, including
`interval14_endpoint_descriptor_refined_first/refinement.json` and
`interval14_endpoint_tail_refined_diagnostic_first.json`. Temporary
checkpoint files are not promoted to published closure certificates.
