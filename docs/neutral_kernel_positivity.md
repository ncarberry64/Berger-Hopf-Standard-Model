# Neutral Kernel Positivity

Status: `CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE`; raw neutral-kernel PSD is not claimed and complete-action derivation of the cone remains open.

For the artifact-backed finite kernel, the raw eigenspectrum is approximately

```text
(-0.03678592198, 1.64710965221, 3.05634293643).
```

The raw kernel is therefore not positive semidefinite. The v1.4 audit proves
exact copositivity on the conditional measurement-supported response cone,
without using the existing threshold clipping. The status is
`CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE`; complete-action
derivation of the cone remains open.

The v1.5 action audit does not change the raw eigenspectrum or the exact cone
proof.
