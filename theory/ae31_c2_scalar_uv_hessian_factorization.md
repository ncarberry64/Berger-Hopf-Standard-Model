# AE3.1 current-C2 scalar UV Hessian factorization

The complete zero-momentum Hadamard pole and the complete Lorentzian
derivative pole carry the same four-field channel matrix.

Let

```text
V=(Y_l,I3,I9_up,I9_down)
```

in the scalar basis

```text
(H_intrinsic,H_HS_e,H_HS_up,H_HS_down).
```

The vertex Gram matrix is

```text
G_V = [[Tr(Y_l^2),Tr(Y_l),0,0],
       [Tr(Y_l),3,0,0],
       [0,0,9,0],
       [0,0,0,9]].
```

On a finite-core current-`C2` slice, the static susceptibility pole is

```text
Pi_0,sing = -G_V/[16 pi^2 R4(tau0)^2 s_mass].
```

The continuous-frequency derivative pole is

```text
Z_sing = G_V/[16 pi^2 epsilon_derivative].
```

The two Laurent coordinates are not identified: they arise in different
dimensionful coefficient extractions.  The theorem is about their exact
channel shape.  After removal of their scalar prefactors, both matrices are
the same normalized `G_V`.

Because the existing family-noncentral charged-lepton operator makes `G_V`
positive definite, the singular generalized channel operator is

```text
G_V^(-1) G_V = I4.
```

All four generalized eigenvalues are equal.  Thus family noncentrality makes
the UV kinetic form full rank, but the universal UV poles still select no
physical scalar direction.

## Finite physical problem

After local pole subtraction, the required matrices have the structure

```text
Z_ren  = Z_tree + z_log(mu) G_V + Z_fin[C,mu],
H0_ren = H0_intrinsic+gauge-HS + H0_fin[C,mu].
```

The physical problem is

```text
H0_ren v = m_scalar^2 Z_ren v,
```

resolved further into neutral radial, Goldstone, and charged weak components.
Neither `Z_fin` nor `H0_fin` is selected by the current action/state data.
Minimal subtraction, a cutoff, the old EC residue, or a UV kinetic eigenvector
cannot be declared the physical Higgs direction.

Promoted:

- the complete four-field zero-momentum Hadamard pole shape;
- common Gram factorization of masslike and derivative UV poles;
- fourfold degeneracy of the singular generalized direction problem.

Not promoted:

- finite renormalized scalar matrices;
- a physical scalar direction or mass;
- canonical Yukawa residues or quark poles.

`FULL_BHSM_COMPLETE = FALSE`.
