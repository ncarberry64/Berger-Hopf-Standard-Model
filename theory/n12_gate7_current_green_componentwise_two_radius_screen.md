# Current-Green componentwise two-radius screen

This screen asks whether the stored componentwise transverse center norms can
be inserted directly into the frozen Hermite--Simpson causal proof.  It uses
the current Green partition, the certified block `Z1`, central and mixed
causal operands, the full endpoint/midpoint transverse center majorants, and
the reconstructed ambient midpoint `DF` for the exact second-incidence slot.

For an endpoint transverse pair, the Hermite--Simpson midpoint first
variation is decomposed into its midpoint longitudinal and transverse tangent
coordinates.  The stored full transverse Frobenius norm bounds the latter;
the certified central and mixed maps bound the other two terms.  Endpoint
quadratic component bounds form the second incidence, and the reconstructed
ambient `DF` maps it into the midpoint rate.  Component boxes are then passed
through the unchanged test frame, reduced inverse, and causal step maps.

The screen is intentionally optimistic: it omits both the small normal
midpoint remainder and every outward tube addition.  Therefore failure means
that outwardizing this component-box representation cannot repair it.  The
scientifically valid next representation retains the signed transverse
Hermite--Simpson tensor through causal transport before taking norms.

This is not a root-nonexistence theorem, a physical instability statement, a
full transverse outward bound, or Gate-7 closure.
