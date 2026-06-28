# Neutral Kernel Positivity

For the artifact-backed finite kernel, the raw eigenspectrum is approximately

```text
(-0.03678592198, 1.64710965221, 3.05634293643).
```

The raw kernel is therefore not positive semidefinite. The existing threshold
map uses `max(0, response-kappa_nu)`, so its reported response is nonnegative by
construction. That is not an admissible-subspace positivity theorem. The
status remains `OPEN_MISSING_ADMISSIBLE_NEUTRAL_POSITIVITY_PROOF`.

