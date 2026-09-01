# AE3.1 charged-lepton scale-free mode sum rule

## Exact derivation

The composed AE3.1 charged-lepton operator has one common prefactor and the
three frozen family weights

```text
m_f = M_common exp[-(K_f+(a^2-1)q_f^2)/(4 pi)].
```

For the already-defined charged-lepton slots

```text
tau slot:      (k,j)=(0,0),  (K,q^2)=(0,0),
muon slot:     (k,j)=(5,2),  (K,q^2)=(35,1),
electron slot: (k,j)=(9,3),  (K,q^2)=(99,9),
```

write

```text
L_mu = log(m_mu/m_tau) = -(35+(a^2-1))/(4 pi),
L_e  = log(m_e/m_tau)  = -(99+9(a^2-1))/(4 pi).
```

Nine times the first equation has exactly the same squashing term as the
second.  Subtraction gives

```text
L_e - 9 L_mu = (9*35-99)/(4 pi) = 54/pi.
```

Therefore

```text
log(m_e/m_tau) = 9 log(m_mu/m_tau) + 54/pi,
```

or equivalently

```text
m_e/m_tau = exp(54/pi) (m_mu/m_tau)^9.
```

This is an exact consequence of the discrete mode ledger and the already
composed semigroup action.  The common Higgs saddle, the universal energy
calibration, the trace-normalized Yukawa prefactor, and the Berger squashing
all cancel.  In particular, the numerical low-energy fine-structure anchor
historically used to screen the squashing does not enter this relation.

## Meaning of the result

The result is a genuine no-lepton-input, scale-free constraint among the
three AE3.1 local tree mass shells.  It is stronger than quoting three
numbers from one selected squashing because the identity holds for every
positive squashing.

It is not yet a theorem about the globally dressed physical electron, muon,
and tau poles.  That promotion still requires either action-selected global
charged-lepton poles or matched-parent relative energies and proof that their
readout preserves this local mode relation.  Curvature dressing,
renormalization-group transport, and radiative self-energies are not assumed
to vanish.

As a post-derivation diagnostic, the repository's frozen on-shell ratios give

```text
tree sum-rule light/heavy from the reference middle/heavy = 0.00027116194,
frozen on-shell light/heavy reference                         = 0.00028758538,
required multiplicative dressing                             = 1.06056690.
```

The reference values do not enter the derivation and the `1.06056690` factor
is not inserted into the action.  It is the quantitative target that a future
global pole, renormalization-group, and radiative calculation must explain.

No particle spectrum, family assignment, projector, current, or topological
label is rebuilt.  No measured lepton mass is used to derive the sum rule.

Promoted:

- `AE31_CHARGED_LEPTON_SCALE_FREE_MODE_SUM_RULE_DERIVED = TRUE`;
- exact cancellation of the absolute unit and Berger squashing;
- verification on the composed AE3.1 family-noncentral Yukawa operator.

Open:

- global physical charged-lepton poles;
- the physical muon pole and electromagnetic vertex;
- muon `F2(0)`.

`FULL_BHSM_COMPLETE = FALSE`.
