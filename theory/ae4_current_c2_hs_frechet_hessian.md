# AE4 current-C2 HS Fréchet Hessian

## Derived owner formula

For one positive generalized current-C2 form block

```text
K(H)=K+H V+(H^2/2)Q,          K x=lambda M x,
Gamma(H)=-(w/2) Tr E1(ell_star^2 P(H)),
```

let `X` be the `M`-orthonormal generalized eigenbasis and define

```text
r(lambda)=exp(-ell_star^2 lambda)/lambda.
```

The exact AE4 source and curvature are

```text
Gamma_H=(w/2) sum_i r_i (X^dagger V X)_ii,

Gamma_HH=(w/2) [
    sum_i r_i (X^dagger Q X)_ii
  + sum_ij r[1](lambda_i,lambda_j)
           (X^dagger V X)_ij (X^dagger V X)_ji
].
```

Here `r[1]` is the first divided difference, with its derivative on a
repeated eigenvalue.  The result is the exact Duhamel/Fréchet second variation
of the AE4 `E1` owner.  It includes the contact and two-vertex terms together;
neither may be independently normalized or dropped.

## Current-C2 evaluation

The formula is evaluated on the birth-local 128-segment Galerkin prefixes of
both lowest product-Dirac chiral form pencils in the reset-generated
1222-segment current-C2 descriptor.  The already-derived unit LR/HS vertex and
contact forms are used directly.  The generalized solve forms the spectral
Hilbert-space operator without constructing `M^(-1)`.

This is the first AE4 evaluation of a pure HS curvature on an actual
current-C2 birth-local form-core prefix.  It does not transplant the
historical periodic proper-cycle HS kinetic matrix.

At the conditioned witness scale, both chiral blocks give the same source and
curvature, and the curvature is positive.  The contact contribution is
positive while the two-vertex Fréchet contribution is negative and larger in
magnitude; the fermionic supertrace sign turns their sum into positive HS
curvature.  This is a birth-local conditioned result, not yet a physical Higgs
mass or residue.

## Claim boundary

The current evaluation uses
`ell_witness=lambda_min(prefix)^(-1/2)` only to condition the owner witness.
It is not the physical `ell_star`, whose collapse-surface value remains
unknown.  The descriptor path consists of proof centers, and the 128th-node
edge is a Galerkin Dirichlet truncation rather than a physical endpoint.

Therefore the result is not yet the full 1222-segment convergence limit, the
maximal-history retarded HS Calderon block, a selected four-channel Higgs
direction, or a broken LR saddle.  It cannot yet be inserted as a physical
coefficient in the event-flux assembly.

The next calculation is to establish prefix convergence to the full finite
core, extend the same Fréchet block to the reset-glued maximal-history
retarded resolvent, assemble all four existing HS channels and the noncentral
fermion operator, then test the broken saddle and event balance without
fitting a Yukawa or scalar normalization.
