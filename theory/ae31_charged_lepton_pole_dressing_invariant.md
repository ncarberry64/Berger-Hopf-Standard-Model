# AE3.1 charged-lepton pole-dressing invariant

## Exact consequence of the tree sum rule

The already-derived AE3.1 local-tree relation is

```text
R_tree = log(m_e/m_tau) - 9 log(m_mu/m_tau) - 54/pi = 0.
```

To state the future pole calculation without choosing or fitting a
self-energy, write any three positive dressed pole masses as

```text
M_f = Z_f m_f.
```

Here `Z_f` is only an effective multiplicative description of the pole shift.
It is not an assumed wavefunction renormalization, a new action coefficient,
or a computed radiative correction. Direct substitution gives

```text
R_pole = log(M_e/M_tau) - 9 log(M_mu/M_tau) - 54/pi
       = log(Z_e) - 9 log(Z_mu) + 8 log(Z_tau),
```

and therefore the one multiplicative invariant tested by this sum rule is

```text
D = Z_e Z_tau^8 / Z_mu^9 = exp(R_pole).
```

The coefficient vector is `(8,-9,1)` in heavy--middle--light order.  Its dot
product with the common direction `(1,1,1)` is zero.  Consequently every
common multiplicative pole rescaling, unit conversion, or common
multiplicative wavefunction factor cancels exactly and cannot change a
nonzero sum-rule residual.

This is a restricted no-go, not a claim that every microscopic
family-central self-energy is powerless.  For example, an additive identity
term can generate unequal *fractional* shifts for unequal tree masses, and a
nondiagonal pole operator must first be diagonalized.  Neither possibility is
excluded here.  The result says exactly which effective logarithmic pole
combination their completed action calculation must produce.

## Frozen on-shell target

Using the repository's on-shell ratios only after deriving the invariant gives

```text
R_reference = 0.05880357568422312,
D_required  = exp(R_reference) = 1.0605668991516508.
```

Relative to the currently composed local-tree ratios and choosing the
irrelevant common gauge `Z_tau=1`, the effective ratios are approximately

```text
Z_tau = 1,
Z_mu  = 0.989830,
Z_e   = 0.967353.
```

Only `Z_e Z_tau^8/Z_mu^9` is fixed by this comparison.  The artifact also
records the minimum-Euclidean-log-norm representative of the same affine
constraint as a numerical witness.  That representative is not a physical
ansatz or action solution.

The `1.060566899...` invariant is not inserted into the action.  It is a
post-derivation target for the future action-selected charged-lepton two-point
operator and its family-resolved self-energy or equivalent pole mechanism.

No particle/family spectrum, representation, projector, current, or
topological result is rebuilt.

Promoted:

- `AE31_CHARGED_LEPTON_POLE_DRESSING_INVARIANT_DERIVED = TRUE`;
- `COMMON_MULTIPLICATIVE_POLE_RESCALING_NO_GO_DERIVED = TRUE`;
- the exact required effective dressing combination is quantified.

Open:

- an action-selected Hadamard/Feynman state and dressed two-point operator;
- the microscopic self-energy or renormalization-group evolution;
- global physical electron, muon, and tau poles;
- the physical photon pole, Ward identity, and muon `F2(0)`.

`FULL_BHSM_COMPLETE = FALSE`.
