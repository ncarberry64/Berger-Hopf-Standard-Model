# BHSM parent-action spectral-current completion v11.6

## Outcome

Both legitimate routes requested by the v11.5 gate were evaluated. Neither
derives or uniquely selects the v11.5 spectral charged-current kernel from the
live theory.

The direct mixed variation of the effective SU(2)L Dirac term is

```text
delta^3 S4 / (delta W+_mu delta bar(u_L,i) delta d_L,j)
  = (g2/sqrt(2)) gamma^mu delta_ij.
```

Thus the action-owned family kernel is `I3`. The v11.5 candidate has nonzero
off-diagonal magnitudes, so it cannot be obtained from `I3` by independent
diagonal rephasings of up- and down-quark mass eigenstates.

## Provenance result

The effective action owns the SU(2)L current form, its adjoint pairing, and the
family-universal identity factor. The frozen three-slot up/down modules and
the diagonal v11.4 spectral responses are conditional geometric structures.
The four angle/phase rules in v11.5 are author-selected relations using those
frozen weights. No live action term supplies the common-domain up/down family
wavefunctions, their relative complex orientation, or the projector/current
pairing that would evaluate
`K_ud[i,j]=<u_i,J_plus_action d_j>_common`.

## Uniqueness result

For every unitary `U`, the block generators
`T+=[[0,U],[0,0]]`, `T-=T+^dagger`, and
`T3=diag(I3,-I3)/2` close the same SU(2) algebra. Requiring nonzero CP removes
special lower-dimensional subsets but leaves a continuous family. The v11.6
tests exhibit two full-rank, unitary, CP-odd, SU(2)-closing candidates with
different entry magnitudes, hence not related by quark rephasing.

The commuting diagonal v11.4 operators do not repair this: every ordinary
joint polynomial or functional calculus of them is diagonal, and so is its
polar factor. Adding the v11.5 angle equations as axioms would select the
matrix by declaration, not derive those equations from prior BHSM axioms.

## Completion boundary

The exact v11.5 disjunction was attacked and replaced by the narrower missing
action object:

```text
ACTION_OWNED_COMMON_DOMAIN_UP_DOWN_FAMILY_WAVEFUNCTION_ORIENTATION_AND_CURRENT_PAIRING_MAP
```

Verdict:

```text
BHSM_PARENT_ACTION_CURRENT_REDUCTION_BLOCKED_BY_UNFIXED_COMMON_DOMAIN_FAMILY_WAVEFUNCTION_MAP
```

Mark III is not reached. Its authoritative definition also requires the
gauge-dressed charged timelike relative-periodic orbit, reduced Floquet
stability, a color-neutral hadron orbit, neutrino current/monodromy closure,
the absolute unit bridge, full-rank physical mixing, and a canonically
normalized four-dimensional theory. Mark IV and BHSM 1.0 consequently remain
open. No measured CKM values were used and frozen predictions were not changed.

Machine-readable sources are the five `BHSM_*_v11_6.json` artifacts and the
rolling `BHSM_1_0_completion_gate.json`.
