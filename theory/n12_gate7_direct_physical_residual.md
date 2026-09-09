# Full direct residual on the selected finite-history branch

The direct-value producer evaluates the original rate at each fixed raw
endpoint and at the actual Arb Hermite–Simpson midpoint. The residual
consumer requires all 371 endpoint and 370 midpoint records, their source
bindings, and their independent reproduction receipt. Missing points are
an error. This calculation uses neither the old stored-midpoint rate nor
the linearized midpoint-displacement diagnostic.

For exact stored binary64 step h, exact weighted endpoint z=(W x,s), and
the direct rate enclosures f, assemble

```
r_i = z_(i+1) - z_i - h_i (f_i + 4 f_mid_i + f_(i+1))/6
b_i = -R_i^-1 T_i r_i.
```

All products, rates, and the inverse above are enclosed in Arb. The input
R and T are the unchanged stored reduced right block and test frame.
Extract each local source's exact Arb midpoint c_i and bound the Euclidean
radius of b_i-c_i. Propagate the signed c_i through the stored causal maps
P_i. The signed computation's own Arb rounding radii remain in its bounds.
Independently transport the local source radii through those same maps
with the existing block-product method, then apply the verified frozen-map
perturbation bound once to the complete response. This retains cancellation
while avoiding interval wrapping of independent source uncertainty across
the entire history. Source/map cross terms are included.

Longitudinal and transverse projections are e^T z and (I-e e^T)z for the
unchanged stored axes. Exact unit norm is not assumed. Hashes of the maps,
axes, right blocks, test-frame operands, and endpoint states must agree with
the complete stored arithmetic foundation; the direct-value source bindings
must agree with those same operands.

This is a finite-history residual bound conditional on identification of
the selected eigenpair branch. Local inclusion and fixed-reference
orientation do not establish global branch continuation, the physical
quotient, the continuum oracle, or a physical root. No physical Y or
contraction claim is enabled until these remaining identifications and
the required derivative/neighborhood bounds are established. Historical
coefficients and physical prediction files are not changed.

```
python scripts/certify_n12_gate7_direct_physical_residual.py --preflight-foundation
python scripts/certify_n12_gate7_direct_physical_residual.py
```

The first command checks only the existing foundation. It does not assert
direct-value coverage. Independently run the second command twice and
compare the resulting JSON byte for byte before consuming it downstream.
