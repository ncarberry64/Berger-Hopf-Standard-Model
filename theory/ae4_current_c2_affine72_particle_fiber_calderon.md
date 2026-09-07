# AE4 affine-72 particle-fiber Calderón attachment

## Result

The existing nine charged-sector particle/family fibers now carry an
evaluated first-order product-Dirac boundary response on the same
canonical-stop proper-time carrier used by the gauge/BRST calculation.  No
particle identity, representation, projector, or spectrum was rebuilt.

The construction keeps two established BHSM indices separate:

```text
(k,j)  = internal Berger family-mode label,
n      = round-S3 spacetime product-Dirac level.
```

The lowest spatial channel is the already-derived `n=0`, `mu_0=3/2` channel.
For each preserved internal fiber, the evaluated operator is

```text
Calderon_(n=0,chirality) tensor Pi_(sector,slot).
```

Thus all nine family fibers are attached to a genuine dynamic carrier while
their rank-one projectors continue to preserve particle identity.  The
carrier response itself is family-central.  Existing family-noncentral
internal operators are neither erased nor silently inserted into this step.

## Numerical certificate

At spectral parameter `z=-1` on the accepted stopped center path:

```text
plus-chirality Weyl birth value   = 6769.190672162356
minus-chirality Weyl birth value  = 6772.205986753091
plus affine-72 first-jet norm     = 358389.68168654054
minus affine-72 first-jet norm    = 358389.23110670154
```

The moving-duration contribution remains dominant; for the plus block its
norm is about `1.1406015e6` times the log-radius contribution.  Dropping the
moving first-stop term is therefore not an admissible fixed-endpoint
approximation.

## Claim boundary

This closes an affine carrier attachment, not a physical mass or pole:

```text
AE4_CURRENT_C2_AFFINE72_PRODUCT_DIRAC_CARRIER_FIRST_JET_EVALUATED = TRUE
ALL_NINE_EXISTING_CHARGED_PARTICLE_FIBERS_ATTACHED_TO_CARRIER = TRUE
INTERNAL_BERGER_AND_SPATIAL_DIRAC_MODE_INDICES_KEPT_DISTINCT = TRUE
AE4_CURRENT_C2_NONLINEAR72_PARTICLE_FIBER_CALDERON_DERIVED = FALSE
AE4_CURRENT_C2_PHYSICAL_FERMION_POLES_DERIVED = FALSE
CURRENT_C2_PHYSICAL_MASS_OPERATOR_DERIVED = FALSE
PARTICLE_SPECTRUM_REBUILT = FALSE
FULL_BHSM_COMPLETE = FALSE
```

The next physical step is to repeat this contraction on a validated nonlinear
stop family and then compose the existing family-noncentral HS/mixed operator
before searching for fermion poles.
