# AE3.1 current-C2 full scalar derivative pole

The universal external-momentum calculation now includes the intrinsic
charged-lepton Higgs field and all three nonzero gauge-HS channels.  In the
basis

```text
(H_intrinsic,H_HS_e,H_HS_up,H_HS_down),
```

the scalar vertex vectors are

```text
(Y_l,I3,I9_up,I9_down).
```

The one-pair Lorentzian pole derived in the preceding unit therefore gives
the trace Gram matrix

```text
G_V = [[Tr(Y_l^2), Tr(Y_l), 0, 0],
       [Tr(Y_l),          3, 0, 0],
       [0,                0, 9, 0],
       [0,                0, 0, 9]].
```

The full derivative principal symbol is

```text
H_derivative(omega,lambda)
 = [diag(1,0,0,0)+G_V/(16 pi^2 epsilon_UV)]
   (-omega^2+lambda).
```

The finite tree entry is the canonical intrinsic `|D H|^2` term already
owned by `BHSM-AE-3.1.0`.  The Laurent pole is the universal current-`C2`
fermion bubble.  No periodic frequency or finite state covariance is used.

## Family noncentrality removes the lepton null direction

The charged-lepton intrinsic/auxiliary block has determinant numerator

```text
3 Tr(Y_l^2)-Tr(Y_l)^2
  = sum_(i<j) (y_i-y_j)^2.
```

This would vanish for a family-central `Y_l=y I3`.  The already-derived BHSM
charged-lepton family operator has three distinct eigenvalues, so the value is
strictly positive.  The lepton block has rank two, and the complete four-field
pole Gram matrix has rank four and is positive definite.

This is a direct place where the preserved family hierarchy changes the
current-`C2` dynamics: it makes the intrinsic and charged-lepton composite
directions kinetically independent at the universal pole.  No family spectrum
or mass input is rebuilt.

## Claim boundary

The universal pole kinetic eigendirections are action derived.  They are not
physical Higgs mass eigenvectors.  A physical generalized eigenproblem needs
both finite matrices:

```text
H_0,ren v = m_scalar^2 Z_ren v.
```

The action still supplies neither the finite current-`C2` derivative matching
condition nor the renormalized zero-momentum four-field Hessian.  Therefore no
broken direction, canonical Yukawa residue, or physical scalar pole is
promoted.

Promoted:

- `CURRENT_C2_FULL_FOUR_FIELD_DERIVATIVE_PRINCIPAL_POLE_DERIVED = TRUE`;
- the intrinsic/charged-lepton-HS cross derivative pole;
- strict rank two of the lepton block from family noncentrality;
- positivity and full rank of the four-field UV kinetic form.

Not promoted:

- a finite full scalar kinetic matrix;
- a renormalized zero-momentum Hessian;
- a physical one-Higgs direction or canonical Yukawa residues;
- scalar or quark pole masses.

`FULL_BHSM_COMPLETE = FALSE`.
