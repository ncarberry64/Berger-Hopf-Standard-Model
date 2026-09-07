# AE3.1 current-C2 quark-channel selector domain theorem

The `2 x 2` quark-channel Hessian required after the HS-direction no-go is not
yet an active operator waiting to be diagonalized.

The intrinsic coordinates `H_u,H_d` are absent from the AE3.1 field space.
AE3.1 adds one intrinsic charged-lepton Higgs block but no quark LR--Higgs
trilinears or independent quark-channel scalar coordinates.  Therefore

```text
D_(H_u,H_d)^2 S_AE3.1
```

is undefined on the active field space, not a physical zero matrix.

The current squared product-Dirac reduction does contain auxiliary HS source,
vertex, and contact tensors.  On the only evaluated classical coefficient
background `c*=0`, its pure-HS curvature is the `2 x 2` zero block.  Because
no complete dynamical HS kernel is attached, this is an incomplete probe
curvature and selects no direction.

## Quantum selector and state dependence

For a state-dependent effective functional

```text
Gamma_1loop[C,H] = -Tr log D_C[H],
```

the formal channel Hessian is

```text
D_g D_f Gamma = Tr[G_C V_g G_C V_f] - Tr[G_C Q_fg].
```

It requires action-owned vertices `V_f`, contacts `Q_fg`, and a current-C2
Feynman inverse `G_C`.

The retained action and Hadamard condition do not select the smooth part of
`G_C`.  An explicit finite-rank counterexample uses the previously derived
pure Hadamard covariance family `P_theta` and charge-compatible vertices.
The finite particle-hole response

```text
chi_fg(P) = Tr[P V_f (I-P) V_g]
```

is zero at `theta=0` but nonzero and rank one at `theta=pi/6`, even though the
Dirac operator, causal propagator, classical action, domain, charge grading,
and Hadamard class are unchanged.  This proxy is not claimed as the BHSM
quark Hessian; it proves that state independence cannot be inferred from the
present data.

The dependency order is therefore:

1. derive current-C2 quark Higgs/HS vertices `V_u,V_d,Q_fg`;
2. derive the complete dynamical two-channel kernel on the AE3.1 domain;
3. select a compatible Feynman covariance, or prove the desired Hessian
   combination independent of its smooth bisolution part;
4. evaluate and diagonalize the full renormalized channel Hessian.

No historical periodic determinant, zero probe block, arbitrary state, or
quark-mass fit may replace these steps.

Promoted:

- `CURRENT_AE31_INTRINSIC_QUARK_CHANNEL_HESSIAN_DOMAIN_CLASSIFIED = TRUE`;
- the intrinsic Hessian is undefined on the active field space;
- a same-Hadamard-class state-dependence counterexample for finite channel
  response is derived.

Not promoted:

- a current quark-channel Hessian or direction;
- an action-selected fermion covariance;
- quark poles or CKM mixing.

`FULL_BHSM_COMPLETE = FALSE`.
