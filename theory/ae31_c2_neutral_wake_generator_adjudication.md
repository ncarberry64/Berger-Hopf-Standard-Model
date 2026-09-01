# AE3.1 neutral stiffness versus wake-generator adjudication

The historical `K_nu` cannot be a positive mass-squared or stiffness operator
as written. A positive-semidefinite matrix with `H_00=0` must have
`H_0j=0` for every `j`, because each leading two-state principal minor gives

```text
0 <= det [[0,b],[b*,c]] = -|b|^2.
```

Here `b=1/3`, so the minor is `-1/9`. This obstruction persists for any
nonzero first-slot mixing while the reference diagonal remains exactly zero.

That does not make the seed unusable as a first-order wake Hamiltonian. v14.56
already defines the coherent action term

```text
i z^dagger D_tau z - z^dagger H_wake z,
```

and v14.57 defines `U(T)=exp(-i T H_wake)`. A Hermitian first-order generator
need not be positive. Removing the common trace `14/9` from `K_nu` leaves a
traceless Hermitian generator with two nonzero eigenvalue gaps and exactly
unitary norm-preserving evolution. The negative shifted eigenvalue is only a
choice of common energy origin.

This is an ontology correction, not a physical promotion. The v14.57 owner is

```text
H_wake = traceless Hermitian part of
  P(N_child-N_parent-J_interface)P
  + sum_A partial_A zeta_rel'(0) G_A.
```

The stored v14.57 matrices are explicitly diagnostic. The physical current-C2
DtN/interface block and relative-zeta shape derivatives have not been
evaluated on the identified neutral modes, so the historical `K_nu` cannot be
substituted for that result.

Promoted:

- the zero-reference positive-stiffness mixing no-go;
- the traceless two-gap unitary-generator shape of historical `K_nu`;
- algebraic eligibility of `K_nu` as a wake Hamiltonian candidate.

Not promoted:

- equality to the action-evaluated current-C2 `H_wake`;
- a physical monodromy, PMNS matrix, or neutrino mass splitting.

The next calculation is now exact: evaluate the v14.57 wake formula with the
physical current-C2 DtN/interface operator and relative-zeta shape jets.

`FULL_BHSM_COMPLETE = FALSE`.
