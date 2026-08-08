# BHSM v11.5 Conditional Flavor-Action Assembly

## Result

V11.5 turns the reviewed manual equations into executable action components.
It preserves the v11.3 reciprocal attachment and resolves the packet's mixed
normalization by retaining the v11.3 action-whitened coordinates. One shared
map transforms both quadratic forms, `K_white=W^T K_action W` and
`H_white=W^T H_action W`; the canonical retained map is `W=I3`. The kinetic,
core, wall, depth, and constraint sources are recorded in the artifact ledger.

The common-domain quadratic data are

```text
K = I3
B = (-1,1,1)
N = [[1,1],[1,0],[0,1]]
K_parallel = [[2,1],[1,2]]
H(K_octave) = diag(h_C,0,1+K_octave)
```

with `h_C=0.181391690148362` from the stored finite-radius core representative.
The reduced Hessian is positive for every `h_C>0` and nonnegative octave.

The charged-lepton action uses the frozen family projectors, Berger spectral
generator, one uniform trace-normalized source, and one universal scale
calibration. Its displayed absolute mass triplet is therefore a calibrated
conditional output, not a parameter-free prediction.

The quark action candidate contains the frozen up/down spectral operators. The
charged-current kernel is selected by the coefficient-free internal rule

```text
s12 = sqrt(T_down,light/T_down,middle)
s23 = 2 T_down,middle
s13 = sqrt(T_up,light)
delta = 2/sqrt(pi)
```

and defines a proposed insertion into the intrinsic M4 weak covariant
derivative. It is unitary, full rank, CP-odd, and closes SU(2) exactly. The
neutral current stays family central. These checks establish mathematical
viability only. The coefficient-free kernel is an author-selected, no-fit
action candidate; it has not been recovered from a parent-action charged-current
term and no BHSM-axiom uniqueness theorem selecting it is presently supplied.

## Status

Verdict:
`BHSM_FLAVOR_ACTION_CANDIDATES_ASSEMBLED_WITH_CHARGED_CURRENT_PROVENANCE_GATE_OPEN`.

- Mark I: reached.
- Mark II: reached on the selected finite-radius core branch.
- Mark III: not reached.
- Mark IV: not reached.
- BHSM 1.0 release complete: no.

Exact next object:
`PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL`.

The provenance gate closes only if the kernel is recovered from an existing
parent-action charged-current term by explicit mixed second variation/current
pairing, or a stated uniqueness theorem proves that the declared BHSM axioms
select it. Up/down normalization, RG transport, and the frozen empirical
benchmark may proceed as downstream conditional evaluations, but they cannot
substitute for this gate.

## Reproduction

```text
python scripts/materialize_completion_v11_4.py
python scripts/materialize_completion_v11_5.py
python -m pytest -q tests/test_bhsm_completion_v11_4.py tests/test_bhsm_completion_v11_5.py
```
