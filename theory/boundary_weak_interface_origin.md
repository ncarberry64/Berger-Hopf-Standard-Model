# Boundary Weak-Interface Origin

Candidate weak-interface origin logic:

```text
active weak-interface orientation space:
  V_w = C^2
  End(V_w) = M2(C)_{w=1}

inactive resolved orientation spaces:
  V_+ = C
  V_- = C
  End(V_+) direct_sum End(V_-) = C_{sigma=+} direct_sum C_{sigma=-}
```

Candidate weak algebra:

```text
A_weak = M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}
```

Candidate central projection:

```text
P_w = projection onto M2(C)_{w=1}
```

Candidate orientation grading:

```text
S_sigma |upper> = + |upper>
S_sigma |lower> = - |lower>
S_sigma^2 = I
```

| block | algebra | algebra dimension | interpretation |
| --- | --- | --- | --- |
| M2_active | M2(C) | 4 | weak-interface active two-orientation block |
| C_sigma_plus | C | 1 | inactive upper orientation singlet |
| C_sigma_minus | C | 1 | inactive lower orientation singlet |

Guardrail:
This is not yet a derivation of SU(2)_L. It is a candidate source of weak-interface activity and orientation.

## Related Closure Spectrum Gate

- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
