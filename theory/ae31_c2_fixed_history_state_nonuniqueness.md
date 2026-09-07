# AE3.1 fixed-history fermion-state nonuniqueness

## Result

Fix any certified finite-core current-`C2` history and one pure Hadamard
covariance `P` for the assembled AE3.1 Dirac operator.  Choose two smooth
orthonormal Cauchy modes `e1,e2` in opposite charge sectors inside one frozen
family sector and write `fi=Gamma ei`.  On

```text
span(e1,e2,f1,f2)
```

replace the positive subspace `span(e1,e2)` by

```text
u1(theta) = cos(theta)e1 + sin(theta)f2,
u2(theta) = cos(theta)e2 - sin(theta)f1.
```

Let `P_theta` be the corresponding projection and leave `P` unchanged on the
orthogonal complement.  Direct calculation gives

```text
P_theta^dagger = P_theta,
P_theta^2 = P_theta,
P_theta + Gamma P_theta Gamma = I,
0 <= P_theta <= I.
```

For generic nonzero `theta`, `P_theta != P`.  The difference has finite rank,
so it is a smoothing change of the Cauchy covariance and does not change the
Hadamard wavefront set or polarization.  Thus a fixed current-`C2` history
admits a continuous family of distinct pure quasifree Hadamard states with
the same Dirac operator, causal propagator, CAR pairing, family projectors,
charge grading, and local singularity class.  The opposite-charge choice
makes each rotated mode charge-homogeneous, so the covariance continues to
commute with the gauge-charge grading.

This is a theorem about the present action data, not a proposed physical
Bogoliubov angle.  No value of `theta` is inserted into BHSM.

## Reset and family transport

The AE2 reset acts as `U_R tensor I_F`.  Hence

```text
P_theta,child = U_R P_theta,event U_R^dagger
```

preserves purity, self-dual CAR reality, Hadamard polarization, and every
frozen family projector.  Because unitary conjugation is bijective, reset
transport carries the whole continuum into the child and cannot collapse it
to one state.

This sharpens the identification bridge: the already-defined family/mode
particle labels and every admissible upstream Hadamard state reach the local
child trace, but the reset and the selected history do not decide which
smooth state-dependent two-point function is physical.

## Current action-owned selector screen

The latest Gate-7 authority still leaves the continuous action-constrained
history open and classifies the stored quarter-step/DOP853 center as a proof
candidate, not a physical trajectory.  Even closing that history would not
remove the covariance family above.

The analytic `R4 -> infinity` branch is also unavailable as an in/out vacuum
selector: it is owner-classified as a nonrealized mathematical branch and
has `H4 -> H0 > 0`, rather than an action-realized asymptotically stationary
end.

The child-boundary Hamiltonian route is not executable either.  The current
ledger lacks the complete covariant symplectic potential/current, complete
`Q_xi`, selected boundary ensemble, and matched-parent subtraction.  Its
constraint-reduced canonical Legendre energy is identically zero and cannot
be relabelled as a state-selecting Hamiltonian.

## Scientific consequence

The exact separation is

```text
history selection -> fixes coefficients of the Dirac operator,
state selection   -> fixes the smooth CAR covariance/bisolution part.
```

The first does not imply the second.  Therefore the present action cannot
promote a unique Feynman two-point function, dressed charged-lepton pole,
physical muon pole, or `F2(0)` by history selection alone.

The next positive object must be an action-owned boundary covariance or an
equivalent spectral, Euclidean, or realized asymptotic condition that fixes
the smooth bisolution part.  Only then should BHSM transport the selected
covariance and assemble the dressed charged-lepton two-point operator.

No particle spectrum, family assignment, mass ledger, current, projector, or
topological label is rebuilt.

`FULL_BHSM_COMPLETE = FALSE`.
