# BHSM v15.29 — compact formed-branch material response

## Result

The inverse material-response calculation is now performed on the actual
compact round-`S7` degree-one eta branch derived in v15.9.  For its normalized
trace

```text
C_q'(chi) = sin(f_q(chi))^2 / integral_0^pi sin(f_q)^2 dchi,
sigma_q = C_q - 1/2,
```

the canonical local scalar Euler equation uniquely requires

```text
a^2 U_q'(sigma_q(chi)) = C_q'''(chi) + 6 cot(chi) C_q''(chi)
                       = w_q'(chi) + 6 cot(chi) w_q(chi).
```

The identity branch has zero force at `sigma=0`.  The action-derived formed
branch does not.  Near the bifurcation,

```text
a^2 U_q'(0) = 20 q/(3 pi) + O(q^2).
```

The reflected internal formation branch has `q -> -q`, `sigma -> -sigma`, and
the source changes sign.  No external rotation frame, empirical input, or new
continuous coefficient enters this calculation.

## Provenance boundary

The eta profile is a retained v15.9 parent-action solution.  The `q`-dependent
material potential is the unique inverse-Euler completion in the declared
canonical local one-field class; it is not silently asserted to have existed
in the historical action.  Nor does the trace construction by itself identify
the historical independent sigma field with `C_eta-1/2`; the branchwise
family `U_q` is not one state-independent local parent potential.  The
calculation does not yet solve the coupled
Einstein–eta–sigma constraints or continue the unstable enclosure into a
regular Hopf child.  `FULL_BHSM_COMPLETE` therefore remains false.

## Exact next dependency

```text
JOINT_PARENT_ACTION_DERIVATION_AND_CONSTRAINT_SOLVED_EINSTEIN_ETA_SIGMA_CONTINUATION_OF_THE_Q_DEPENDENT_MATERIAL_RESPONSE_INTO_A_REGULAR_HOPF_CHILD
```
