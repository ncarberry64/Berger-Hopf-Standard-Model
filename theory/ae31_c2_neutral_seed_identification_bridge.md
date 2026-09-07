# AE3.1 historical-neutral-seed identification bridge

The old and current neutral ledgers are the same modes written in different
coordinates. Current BHSM stores `(k,j)` modes

```text
(0,0), (3,0), (3,1).
```

The historical neutral Hessian uses `(q,j)` with `q=k-2j`, giving exactly

```text
(0,0), (3,0), (1,1).
```

Its candidate positive mode metric `H_nu=[[1,1],[1,2]]` therefore yields the
stored costs `(0,9,5)` on the current three slots. This closes the algebraic
mode-identification bridge without rebuilding any particle or family ledger.

The historical boundary seed

```text
K_nu = [[0,   1/3, 0  ],
        [1/3, 3,   1/6],
        [0,   1/6, 5/3]]
```

does contain the missing kind of family shape: it fails to commute with the
current diagonal neutral semigroup response and, under a conditional
first-slot/`nu_e` identification, has source-projector commutator norm
`sqrt(2)/3`. It therefore passes the algebraic necessary noncommutation screen.

The off-diagonal part also decomposes exactly on the already-predeclared
v14.55 shape channels:

```text
K_nu = diag(0,3,5/3)
     + (sqrt(2)/3) M_(3,0)
     + (sqrt(2)/6) M_(1,1).
```

Those channel matrices have normalized off-diagonal entries `1/sqrt(2)` and
are precisely the `0<->1` and `1<->2` directions. Thus the old neutral seed,
the old pair-wake channel basis, and the current neutral mode ledger are now
one algebraic object. v14.55 explicitly left the channel amplitudes and phases
unselected, so this identity does not supply their action ownership.

It is not yet a physical propagation operator. As written, its determinant is
`-5/27`, its leading `2x2` principal minor is `-1/9`, and it has one negative
eigenvalue. More decisively, the historical repository already records
`eta_nu`, `beta_nu`, and `kappa_nu` as strong candidates whose action/source
derivation is open. A positive common shift, physical scale, weak-flavor basis
map, or Lorentzian interpretation cannot be inserted by hand.

Promoted:

- exact historical/current neutral mode-coordinate identification;
- the historical seed's noncommuting family shape on those slots;
- its exact decomposition on the v14.55 noncommuting shape-channel basis;
- the exact indefiniteness no-go for treating it as a positive stiffness.

Not promoted:

- the seed as an AE3.1 action term;
- a Lorentzian propagation Hamiltonian, PMNS matrix, or neutrino splitting.

The next owner is the returned neutral action Hessian on these identified
slots. It must derive `eta`, `beta`, and `kappa` or replace them.

`FULL_BHSM_COMPLETE = FALSE`.
