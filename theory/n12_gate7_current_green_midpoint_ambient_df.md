# Current-Green midpoint ambient first variation

The accepted outward campaign already certified, at every midpoint, the two
74-column derivatives obtained from the exact Hermite--Simpson left and right
direction maps.  Their combined 99 by 148 direction matrix has row rank 99.
Therefore the complete ambient midpoint derivative is determined without a
new action evaluation.

For the certified direction matrix `K` and its certified derivative image
`G = DF K`, column-pivoted QR selects a nonsingular 99-column submatrix
`K_S`.  The identity

```text
DF = G_S K_S^{-1}
```

is evaluated in 384-bit Arb arithmetic.  The unused 49 columns are then
checked by requiring every component of `DF K - G` to contain zero.  The
pivoting is only an algebraic choice of an already-certified spanning set; it
does not change the action, center, branch, scale, partition, or proof norm.

This reconstruction supplies the missing first variation needed for the
Hermite--Simpson transverse second-incidence term.  It is not itself the
transverse causal majorant or the two-radius theorem.
