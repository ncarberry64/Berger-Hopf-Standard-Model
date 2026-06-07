# BHSM v1.3O Symbolic Formal-Kernel Operator Note

BHSM v1.3O closes the Level 2 formal-kernel scaffold at the symbolic level.
The protected subspace is stated coordinate-free as

[
K_{\rm formal}
= \mathrm{span}\{
|\ell,0,0,q=0,\chi=-1\rangle,
|u,0,0,q=0,\chi=-1\rangle,
|d,0,0,q=0,\chi=-1\rangle
\}.
]

The complement is

[
\mathcal H_\perp = K_{\rm formal}^{\perp}.
]

The current corrected Level 2 operator scaffold is

[
D_{\rm FK}^2
=
D_{\rm diag}^2
+V_{\rm Hopf}
+V_{\rm boundary}
+V_\chi
+K_{\rm sector}
+P_{\rm lift}^{\perp}.
]

The finite basis realization is sector-major. With

[
M(k_{\max})=\sum_{k=0}^{k_{\max}}\left(\lfloor k/2\rfloor+1\right),
]

the protected coordinates are

[
\ell=0,\qquad u=2M,\qquad d=4M.
]

For `k_max=4`, this gives `(0,18,36)`. This is the corrected formal sector-labeled kernel and not the legacy coordinate-first block `(0,1,2)`.

## Term Classification

| Term | Classification | Kernel action | Bound role |
| --- | --- | --- | --- |
| `D_diag^2` | `DIAGONAL_EXACT` | vanishes on and preserves `K_formal` | diagonal complement minimum |
| `V_Hopf` | `SIGN_INDEFINITE_BOUNDED` | vanishes on and preserves `K_formal` | semi-analytic/Gershgorin row |
| `V_boundary` | `SIGN_INDEFINITE_BOUNDED` | vanishes on and preserves `K_formal` | semi-analytic/Gershgorin row |
| `V_chi` | `SIGN_INDEFINITE_BOUNDED` | vanishes on and preserves `K_formal` | semi-analytic/Gershgorin row |
| `K_sector` | `OFF_DIAGONAL_BOUNDED` | vanishes on `K_formal`; acts on complement | structured relative-bound candidate |
| `P_lift^perp` | `PSD_EXACT` | acts only on `H_perp` | monotone heat-lift lower bound |
| `V_profile` | `PSD_EXACT` if assumed nonnegative | acts on `H_perp` | nonnegative Weyl contribution |

## Complement Bound

The v1.3O scaffold uses the v1.3N semi-analytic complement bound under
`DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`:

| Quantity | Value |
| --- | --- |
| Required Dirac lower bound | `0.8038064161349437` |
| Diagonal complement lower bound | `6.833527254265818` |
| Structured relative lower bound | `6.729508865520464` |
| Exact finite lower bound | `6.8171156827281205` |
| Heat-lift lower bound | `19591.98933512353` |
| Clears `mu_H` after heat lift | `True` |

Conditional implication:

If the coordinate-free `K_formal` split, the semi-analytic complement lower
bound, the sector-coupling relative bound, and the positive-semidefinite
profile condition hold for the full operator, then

[
H_T|_{\mathcal H_\perp}\ge \mu_H.
]

## What v1.3O Does Not Prove

BHSM v1.3O does not prove the full no-extra-light-state theorem. It does not
complete the full twisted Dirac spectrum, the topological index theorem, the
mirror-mode exclusion theorem, or the infinite-basis complement split. It also
does not change frozen BHSM v1.0/v1.1 predictions, constants, tolerances, or
branch outputs.
