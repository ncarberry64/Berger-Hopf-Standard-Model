# BHSM v1.3 Formal-Kernel H_T Addendum

BHSM v1.3 closes the current development arc around the corrected formal
sector-labeled Level 2 `(H_T)` scaffold. The corrected reference is
`DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`.

The protected kernel is treated as a coordinate-free subspace:

```text
K_formal = span{|ell,0,0,q=0,chi=-1>, |u,0,0,q=0,chi=-1>, |d,0,0,q=0,chi=-1>}
H_perp = K_formal^perp
```

In the finite sector-major Level 2 basis,

```text
M(k_max)=sum_{k=0}^{k_max}(floor(k/2)+1)
ell=0, u=2M, d=4M
```

so `k_max=4` realizes the formal kernel at `(0,18,36)`. The old
coordinate-first block `(0,1,2)` is superseded wherever prior Level 2 `(H_T)`
claims depended on it.

The current symbolic scaffold is:

```text
D_FK^2 = D_diag^2 + V_Hopf + V_boundary + V_chi + K_sector + P_lift^perp
```

Corrected lower-bound values:

| Quantity | Value |
| --- | --- |
| required Dirac lower bound | `0.8038064161349437` |
| structured relative lower bound | `6.729508865520464` |
| exact finite lower bound | `6.8171156827281205` |
| heat-lift lower bound | `19591.98933512353` |

This addendum does not claim the no-extra-light-state theorem is proven. The
full twisted Dirac operator, topological index theorem, mirror exclusion,
profile positivity, and infinite-basis complement bound remain open proof
obligations. Frozen BHSM v1.0/v1.1 predictions, constants, tolerances, and
branches are unchanged.
