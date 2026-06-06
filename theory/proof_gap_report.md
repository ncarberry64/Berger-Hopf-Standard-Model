# Proof-Gap Report

This report summarizes repository readiness after Phase 17 / Gate 32D. It is
an audit consolidation, not a proof upgrade.

## A. Full Twisted Dirac / H_T Spectrum

- Current status: `DIRAC_PROXY_LEVEL_2 + SPECTRAL_BOUND_SCAFFOLD + BASIS_CONVERGENCE_AUDIT + THEOREM_SCAFFOLD`
- Tests passed: `tests/test_twisted_dirac_level2.py`, `tests/test_spectral_bounds.py`, `tests/test_theorem_scaffold.py`
- Basis size: `54`
- Zero-mode count: `3`
- First complement eigenvalue: `1.4630400252994733`
- H_T gap: `19586.72266333732`
- Margin above `mu_H`: `1.4628370793107024`
- Required Dirac lower bound at natural cutoff: `0.8038064161349437`
- Direct finite-spectrum lower bound: `19586.72266333732`
- Min-max restricted-complement lower bound: `19586.72266333732`
- Gershgorin restricted-complement lower bound: `19586.696449745185`
- Weyl PSD/profile lower bound: `19586.72266333732`
- Gate 32C convergence cases: `18`
- Gate 32C worst direct margin: `1.4628370793070644`
- Gate 32C worst Gershgorin margin: `1.4366234871740744`
- Gate 32C zero-mode counts: `3` in every scanned basis
- Gate 32C pass status: all scanned cases pass the finite-basis proxy bound
- Gate 32C monotonicity: first complement eigenvalue unchanged within tolerance across the requested basis growth
- Gate 32D theorem scaffold: `theorem_complete = False`
- Gate 32D assumptions A1-A7 status counts: `VERIFIED_PROXY = 4`, `OPEN = 2`, `ASSUMED = 1`

The full theorem remains open because the Level 2 operator is a finite-basis,
representation-aware matrix scaffold. It is not the full analytic twisted
Dirac `H_T` spectrum on the complete Hilbert space.

Gate 32B: spectral lower-bound scaffold implemented. The (H_T) theorem
remains open, but the finite-basis proxy is now accompanied by explicit
sufficient lower-bound inequalities and conservative bound checks.

Gate 32C: basis-convergence audit implemented. The Level 2 (H_T) proxy gap
remains finite-basis/proxy evidence; full analytic spectral theorem remains
OPEN.

Gate 32D: formal sufficient theorem scaffold added. The theorem is not
complete; it lists the exact assumptions A1-A7 that must be proven in the full
internal action.

## B. Boundary Operators Omega_f

- Current status: `ACTION_LINKED`

Recovered equations:

```text
Omega_l = -q + 2j = 3
Omega_u =  q - 2j = 6
Omega_d =  q + 4j = 12
```

The coefficients are reproduced by symbolic phase factors tied to Hopf fiber
orientation, base-node phase, chirality, weak component, coframe factor, family
index, and sector winding. What remains is an action-level derivation from
variation or spectrum of the full twisted Dirac/bundle action.

## C. RG Matching

- Current status: one-loop scaffold

Geometric values:

```text
alpha1 = 0.01688686394038963
alpha2 = 0.03377372788077926
alpha3 = 0.1182080475827274
```

One-loop matching scales:

```text
alpha1: 67.282 GeV
alpha2: 95.676 GeV
alpha3: 89.396 GeV
```

Full two-/three-loop threshold matching remains open because threshold
corrections and higher-loop beta functions are explicit placeholders.

## D. Scalar/Topographic Decoupling

- Current status: finite-basis scaffold
- Light Higgs projection count: `1`
- Dangerous light scalar count: `0`
- Conditional filtered/screened modes: `5`

The full action-level proof remains open because the current scalar inventory
is a finite-basis audit. Filtered and screened modes are conditional until
their action-level couplings and spectrum are computed.
