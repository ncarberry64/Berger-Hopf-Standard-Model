# AGENTS.md

## Project
Berger-Hopf Standard Model Completion Program

## Mission
Build a reproducible research repository that formalizes, audits, and
numerically tests a conditional Berger-Hopf topographic framework for
reinterpreting Standard Model flavor, couplings, generations, and the
electroweak scale.

Do not invent new theory. Implement, audit, test, and document the framework
supplied here.

## Scientific Boundaries
Use conservative claim discipline.

Forbidden claims:
- Do not claim a rigorous first-principles derivation of the Standard Model
  from pure geometry alone.
- Do not claim a proof of Yang-Mills confinement.
- Do not claim the no-extra-light-state theorem is complete until the spectrum
  of H_T is computed.
- Do not claim neutrino masses are part of the minimal Standard Model; treat
  them as an effective extension.
- Do not claim numerical matches are predictions until mode-selection rules are
  derived independently.

Allowed claims:
- The framework conditionally reproduces the anomaly-free Standard Model gauge
  and matter ledger.
- Hypercharges follow from Yukawa invariance and anomaly cancellation once the
  chiral representation pattern and Higgs-selected U(1) are admitted.
- Three generations are reduced to an index-three twisted Dirac kernel.
- Yukawa matrices are reinterpreted as internal overlap integrals with a
  universal Higgs/topographic profile.
- CKM mixing is interpreted as left-handed up/down internal-basis misalignment.
- Gauge coupling relations are electroweak-scale matching screens.
- The no-extra-light-state theorem is reduced to a computable spectral bound on
  H_T.

## Core Equations

Berger scalar spectrum proxy:

```text
lambda_{k,j}(a) = a^2 (k - 2j)^2 + 2((2j + 1)k - 2j^2)
```

Hopf charge:

```text
q = k - 2j
```

Universal overlap rule:

```text
m_i / m_3 = exp[-S lambda_{k,j}]
S = 1 / (4 pi)
```

Gauge coupling screens:

```text
alpha_1 = 1 / (6 pi^2)
alpha_2 = 2 / (6 pi^2)
alpha_3 approx 7 / (6 pi^2)
sin^2(theta_W) = 3 / 13
alpha_EM^{-1}(M_EW) = 13 pi^2
```

Electroweak scale candidate:

```text
epsilon_alpha = alpha^{-1}/(12 pi^2) - 1
v = 2 sqrt(2) E_P exp[-4 pi^2 - epsilon_alpha/(4 pi^2)]
```

Hopf gap:

```text
M_lift = 4 pi^2 v
dimensionless target:
mu_H = 64 pi^5
```

Topographic stability operator:

```text
H_T = -Delta_I + beta Delta_I^2 + gamma K[rho] + V_T(y)
```

No-extra-light-state target:

```text
H_T restricted to H_perp >= (4 pi^2 v)^2
```

## Mode Ledger to Test

Heavy generation in each charged sector:

```text
(0,0)
```

Charged leptons:

```text
middle = (5,2)
light = (9,3)
```

Up-type quarks:

```text
middle = (6,0)
light = (10,1)
```

Down-type quarks:

```text
middle = (6,3)
light = (8,2)
```

Boundary operators to document/test:

```text
Omega_l = 2j - q
Omega_u = q - 2j
Omega_d = q + 4j
```

## Engineering Instructions

- Use Python.
- Use numpy and scipy where useful.
- Use pytest for tests.
- Keep functions small and documented.
- Every numerical screen must report input assumptions, output values,
  empirical comparison values if provided, relative error, and whether the
  result is derived, conditional, screened, or open.
- Do not hide failures. If a test fails, report the failure clearly.
- Do not tune parameters silently.
- Separate constants, assumptions, and empirical reference values.

## First Priority

Implement tests for:

1. hypercharge derivation;
2. anomaly cancellation;
3. Berger-spectrum mass hierarchy screens;
4. gauge coupling screens;
5. electroweak-scale calculation;
6. proxy spectral-gap test for H_T.

Do not proceed to manuscript polishing until the tests run.

