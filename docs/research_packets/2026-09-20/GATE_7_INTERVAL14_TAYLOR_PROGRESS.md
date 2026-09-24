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

The completed first-run midpoint calculation shares endpoint nonlinear
remainder parameters between both occurrences in the transport formula.
Residual cancellation reduces its scalar tail from approximately
`0.0229079431` to `9.0954668e-7`. Comparison with the frozen point anchor
and first jet gives the outward entry-error upper bound approximately
`1.83507737e-5 < 3.94150e-4`. Frozen full-history transport, including the
previously unbooked TT linear piece, gives a transverse contribution at most
approximately `5.51787553e-12`, below the `1.13027823e-10` allocation.
Exact rational bounds are in `interval14_entry_assembly_first.json`.

Independent reproduction is pending. The bounded reproduction driver
regenerates both base enclosures, the endpoint directional and descriptor
enclosures, the shared midpoint chain and scalar refinement, and the final
assembly in fresh processes. It checks numerical artifacts byte-for-byte
and permits only explicitly recorded refinement-location differences in
wrapper provenance. Any mismatch stops the chain. No ledger debit or
Gate-7 closure declaration is made by that driver.

An initial all-parallel base replay failed byte comparison because Arb ball
reloads add outward radius rounding. That diagnostic is retained. The active
reproduction preserves the original serial/cache boundaries: the endpoint
base is serial, and midpoint response rows 8–61 use the original prefetch
path. No mismatch has been waived and no independent certificate is claimed.

Focused checks of the Taylor arithmetic, original-domain implicit inverse
argument, shared transport cross term, and coupled adjoint passed. Two
isolated scalar-contraction processes also matched an existing serial
Taylor term byte-for-byte. That backend check is not independent
reproduction of the complete entry certificate.

Working evidence is retained under `tmp/gate7_vector_20260919/`, including
`interval14_endpoint_descriptor_refined_first/refinement.json` and
`interval14_endpoint_tail_refined_diagnostic_first.json`. Temporary
checkpoint files are not promoted to published closure certificates.
