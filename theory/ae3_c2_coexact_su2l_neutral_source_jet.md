# AE3 current-C2 neutral SU(2)L source jet

The current-C2 lowest-Weyl coexact source construction used for `J_Y` now
also carries the neutral weak generator `T3`. On one rank-16 left-Weyl family,
`T3` has eigenvalues `(+1/2,-1/2)` on each of the three colored `Q_L`
doublets and on `L_L`, and vanishes on `u_c,d_c,e_c,nu_c`. Therefore

```text
tr_16(T3)=0,  tr_16(T3^2)=2,  tr_48(T3^2)=6,  tr_16(Y T3)=0.
```

Both chiral current-C2 product-Dirac pencils receive exact Hermitian first and
second/contact source derivatives on the same birth-retained Friedrichs core
as `J_Y`. Thus the pair `(J_Y,J_3)` is attached before mixing, and the
structural generator `Q_em=T3+Y_BH` is available.

This does not rotate currents or fields, discover a neutral null direction,
or promote a photon. The Lorentz-residue mismatch from the preceding gauge/
ghost Hessian remains active.

`CURRENT_C2_COEXACT_SU2L_J3_SOURCE_JET_DERIVED=TRUE` and
`CURRENT_C2_PHYSICAL_PHOTON_VERTEX_DERIVED=FALSE`.
