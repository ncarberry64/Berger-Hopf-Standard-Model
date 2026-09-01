# AE3.1 current-C2 quark projector-overlap bridge

The preserved BHSM quark ledgers identify the family subspaces

```text
up:   (k,j)=(0,0),(6,0),(10,1),
down: (k,j)=(0,0),(6,3),(8,2),
```

through `k=q+2j`. They do not select the remaining Wigner/base orientation
label `m`. Consequently, one matrix element

```text
<psi_A,kjm, M_H psi_S,kjm'>
```

cannot be used as a physical residue by choosing `m,m'` after the fact.

There is, however, a canonical object already determined once the spectral
subspaces and scalar multiplication operator are attached. If `P_A,f` and
`P_S,f` are the orthogonal projectors onto the active and singlet retained
subspaces, define

```text
R_f(M_H)=Tr(P_A,f M_H P_S,f M_H^dagger)
        =||P_A,f M_H P_S,f||_HS^2 >= 0.
```

This response is invariant under arbitrary unitary changes of basis inside
either retained subspace. Thus the unresolved `m` label is not needed when
the parent action traces the complete retained multiplets. This replaces an
arbitrary vector overlap with a spectral-projector invariant; it does not
rebuild or alter the historical particle spectrum.

The distinction in the action domain is decisive:

- If the current-C2 parent trace includes each complete retained `(k,j)`
  subspace, `R_f` is the unique basis-independent quadratic overlap readout.
- If the action selects a vector or proper density inside a degenerate
  subspace, the correct object is
  `Tr(rho_A M_H rho_S M_H^dagger)`, and an action-derived `m` or density
  selection is still required. The full projector trace cannot make that
  selection.

Conditionally, under one common action normalization,

```text
|c_f|^2=C_common R_f,
|c_u/c_d|^2=R_u/R_d.
```

Neither relation is numerically evaluated here. The current repository does
not yet provide the normalized current-C2 internal scalar multiplication
operator, prove that the parent trace runs over the complete retained
subspaces, or close the common trace/field normalization. The old symbolic
boundary target amplitudes are not substituted for any of these data.

This changes the next calculation. Explicit harmonic-vector values are not
the first requirement. First derive the current-C2 action trace domain and
the normalized `M_H`. If the trace is the full multiplet trace, the `m`
ambiguity drops out and the two sector responses follow directly from the
existing projectors. Only if the action chooses a proper state does the
orientation-selection problem remain upstream.

Promoted:

- the nonnegative projector-overlap functional;
- its exact basis-invariance theorem;
- reuse of the historical up/down family subspaces without a spectrum rebuild;
- the full-trace versus selected-state decision criterion.

Not promoted:

- a current-C2 action trace domain;
- a normalized internal Higgs multiplication operator;
- numerical `c_u,c_d`, quark poles, masses, or CKM mixing.

`FULL_BHSM_COMPLETE = FALSE`.
