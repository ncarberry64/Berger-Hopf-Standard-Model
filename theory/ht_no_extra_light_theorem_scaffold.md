# H_T No-Extra-Light-State Theorem Scaffold

Gate 32D: formal sufficient theorem scaffold added. The theorem is not complete; it lists the exact assumptions A1-A7 that must be proven in the full internal action.

Title: Conditional H_T No-Extra-Light-State Theorem Scaffold
Theorem complete: `False`

## Assumptions

| ID | Status | Statement | Evidence | Limitations |
| --- | --- | --- | --- | --- |
| `A1` | `VERIFIED_PROXY` | dim ker D_twist = 3. | Level 2 finite-basis proxy inserts and audits three protected zero modes.<br>Gate 32C convergence scan kept zero_mode_count = 3 across requested bases. | The full twisted Dirac kernel has not been computed in the complete internal action. |
| `A2` | `OPEN` | No opposite-chirality mirror zero modes. | Current finite-basis scaffolds track chirality labels. | Absence of mirror zero modes has not been proven for the full twisted Dirac spectrum. |
| `A3` | `ASSUMED` | The physical light subspace is exactly ker D_twist. | The audit projects a protected kernel before testing H_perp. | Identification of the physical light subspace remains an action-level assumption. |
| `A4` | `VERIFIED_PROXY` | The complement satisfies d_lower >= 0.8038064161349437 for Lambda^2 = 1/(4 pi). | Gate 32B computed the required finite-basis Dirac lower bound at natural cutoff.<br>Gate 32C found worst direct margin 1.4628370793070644 and worst Gershgorin margin 1.4366234871740744 in the requested convergence scan. | This is finite-basis proxy evidence, not a complete Hilbert-space lower bound. |
| `A5` | `VERIFIED_PROXY` | V_profile restricted to H_perp is positive semidefinite: V_profile|H_perp >= 0. | Gate 28D and positivity tests verify PSD profile terms preserve proxy complement gaps. | The full curvature/profile operator has not been derived and proven PSD on H_perp. |
| `A6` | `OPEN` | The trace U(1) is topological/nondynamical. | Tracked as an open claim in the claims ledger. | No independent topological proof is implemented. |
| `A7` | `VERIFIED_PROXY` | Scalar orthogonal modes are lifted or screened separately. | Gate 30B scalar/topographic decoupling scaffold audits one light Higgs projection and no dangerous light direct-coupled scalar in the proxy inventory. | Full action-level scalar/topographic decoupling remains open. |

## Implication Steps

| ID | Depends On | Statement | Conclusion |
| --- | --- | --- | --- |
| `S1` | A4, A5 | Heat-lift inequality: d + mu_H(1 - exp(-d/Lambda^2)) + V_min >= mu_H. | A sufficient dimensionless H_T lower bound follows from the Dirac lower bound and nonnegative profile term. |
| `S2` | A4, A5, S1 | If A4 and A5 hold, then H_T|H_perp >= mu_H. | The complement clears the dimensionless Hopf-gap target. |
| `S3` | S2 | Since mu_H = (4 pi^2 v)^2 r_int^2 in dimensionless units, complement modes are heavier than 4 pi^2 v. | The complement lies above the Hopf lift scale under the stated unit matching. |
| `S4` | A1, A2, A3 | A1-A3 leave exactly three protected chiral families light. | The protected light fermion family count is three if the kernel assumptions are proven. |
| `S5` | A6, A7 | A6-A7 remove extra gauge/scalar light states. | No additional trace-U(1) or scalar/topographic light state remains under those assumptions. |

## Required Equations

```text
d + mu_H(1 - exp(-d/Lambda^2)) + V_min >= mu_H
H_T|H_perp >= mu_H
mu_H = (4 pi^2 v)^2 r_int^2
m_complement >= 4 pi^2 v
```

## Conclusion

If A1-A7 are proven in the full internal action, then the no-extra-light-state theorem follows.

This is a sufficient theorem scaffold only. It does not prove A1-A7.
