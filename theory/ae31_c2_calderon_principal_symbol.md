# AE3.1 current-C2 Calderon/Hadamard principal boundary symbol

The complete physical outer projector is not yet selected, but its universal
local symbol is.  In an orthonormal current-`C2` tangent frame, the frozen
family Dirac Hamiltonian is

```text
H_l(k)=alpha.k tensor I_3 + beta tensor M_l,
H_l(k)^2=I_4 tensor (|k|^2 I_3+M_l^2).
```

Therefore its exact frozen energy projectors are

```text
P_+^M(k)=1/2 [I+H_l(k)(|k|^2 I_3+M_l^2)^(-1/2)],
P_-^M(k)=I-P_+^M(k).
```

The family mass endomorphism is zero order.  At high momentum every family
therefore has the same homogeneous Hadamard/Calderon principal symbol,

```text
P_+^(0)(k)=1/2 [I+alpha.k/|k|] tensor I_3.
```

On the self-dual CAR doubling this gives

```text
C_Had^(0)=diag(P_+^(0),I-conjugate(P_+^(0))).
```

It is Hermitian, pure, half rank, and satisfies
`C+Gamma conjugate(C) Gamma^dagger=I`.  A nontrivial spatial rotation and its
spin lift verify

```text
C_child^(0)(Rk)=U_R C_event^(0)(k) U_R^dagger,
```

with `U_R` acting as the identity on the three frozen family slots.  Thus AE2
reset transmission and the Hadamard principal polarization are compatible;
they do not compete for the particle labels.

The same local unit retains the already-derived Maxwell--BRST symbol,

```text
H_coexact^(0)=(Z_s |k|^2-Z_t omega^2) Pi_transverse,
H_FP^(0)=Z_t omega^2-Z_s |k|^2.
```

The opposite characteristic scalars certify the BRST matching.  They also
retain the exact `Z_t/Z_s=0.590609601652908` mismatch.  A principal-symbol
construction cannot manufacture the missing noncommon finite boundary
response.

This is a real reduction of the missing owner.  Every admissible physical
outer projector must now be a reset-equivariant smooth completion of this
fixed local gauge--spinor--ghost symbol.  What remains is the smoothing part
of the self-dual CAR covariance and the lower-order outer DtN/boundary or
collar response.  Those data determine the finite determinant and may alter
the gauge residues; the local symbol alone does not.

- `CURRENT_C2_SPINOR_HADAMARD_CALDERON_PRINCIPAL_SYMBOL_DERIVED = TRUE`
- `CURRENT_C2_GAUGE_BRST_CHARACTERISTIC_BOUNDARY_SYMBOL_DERIVED = TRUE`
- `CURRENT_C2_RESET_EQUIVARIANT_FAMILY_PRESERVING_LOCAL_SYMBOL_DERIVED = TRUE`
- `CURRENT_C2_PHYSICAL_GAUGE_SPINOR_GHOST_CALDERON_PROJECTOR_DERIVED = FALSE`
- `CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED = FALSE`
- `CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED = FALSE`
- `MUON_MAGNETIC_MOMENT_DERIVED = FALSE`
