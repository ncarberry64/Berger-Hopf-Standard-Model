# Physical field on the actual Hermite–Simpson midpoint domain

The input is the independently reproduced coupled midpoint eigenpair and its
independently reproduced actual HS outer domain. This includes both endpoint
longitudinal directions, both complete transverse balls, and all 99 independent
field-remainder directions. No physical trial radius is reduced.

Use the signed response proof in `n12_gate7_affine_response_enclosure.md`, with
each single-tube row bound replaced by the complete product-domain support
function in `n12_gate7_affine_hs_midpoint_domain.md`. All 249 signed derivative
columns enter the bound; complete action contractions are formed before absolute
values. In particular, the derivative of the configuration leg is retained.

The exact 99-coordinate midpoint-domain anchor supplies the point descriptor.
The uniform descriptor is coordinate 98 of that domain's segment hull. An
endpoint descriptor or a center-only HS image cannot replace either operand.

The paired midpoint eigenpair proves normalization and the uniform contraction
needed for the same bordered physical response. Since K=J diag(I,-1), the
weighted Neumann response enclosure applies. Its last equation proves
psi^T hard=0 for this same response. Together with psi^T psi=1, these identities
permit the normalization in `n12_gate7_coupled_physical_normalization.md`.
Both complete third-action descriptor contractions are recomputed. The original
physical field enclosure is retained and must overlap the coupled enclosure.
A nonzero border sign and a positive original field norm are required.

This establishes only a uniform value on the selected actual midpoint outer
domain. Uniform physical derivatives, higher remainders, the physical quotient,
Gate 7, and full BHSM completion remain open. Each successful numerical artifact
requires a separate full invocation producing byte-identical evidence.
