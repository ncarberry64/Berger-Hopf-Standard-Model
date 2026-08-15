# BHSM v15.36 — compact momentum constraint and relative Hopf rotor

## Constraint correction

The compact spatial momentum constraint is

\[
 -2D_j\pi^j{}_i=P_i^{\rm matter}.
\]

Contract it with any Killing field \(K^i\) and integrate over closed
\(S^7\). Integration by parts gives

\[
 \int_{S^7}K^iP_i^{\rm matter}=0,
\]

because the boundary term vanishes and
\(\pi^{ij}D_iK_j=0\). Therefore a lone nonzero Hopf rotor is not a
constraint-solved compact state. Event degree cannot replace the compensating
canonical momentum.

This corrects the physical interpretation of v15.34–v15.35 without erasing
their localized-inertia calculation.

## Parent–child relative sector

The admissible nonzero sector has

\[
 J_c=J,
 \qquad J_p=-J,
 \qquad J_{\rm total}=0.
\]

After eliminating the common rotation, the relative inertia is the parallel
sum

\[
 I_{\rm rel}
 =\left(I_c^{-1}+I_p^{-1}\right)^{-1},
\]

and

\[
 E_{\rm rel.rot}
 =\frac{J^2}{2I_{\rm rel}}
 =\frac{J^2}{2I_c}+\frac{J^2}{2I_p}.
\]

The antiperiodic relative coordinate still gives the lowest
\(J^2=1/4\) sector. The parent counterrotor term is finite. The localized
child inertia tends to zero at both collapse limits, so the child term still
diverges and the finite stable Routhian minimum survives. In the deterministic
normalization its \(x<0\) location and positive curvature differ from v15.34
only by the finite parent recoil energy.

## Remaining local momentum constraint

Zero integrated charge is necessary but not sufficient. The full stationary
ansatz requires a Hopf/coexact frame-dragging companion

\[
 \beta=\beta_H(\chi)K_H
\]

and the sourced local momentum-constraint equation. A radial shift alone
cannot solve this block. Eliminating a positive shift operator has the usual
subtractive Schur sign and must be included in the final child Hessian.

## Status

Derived:

- the exact compact zero-total-Killing-momentum theorem;
- the correction from a lone rotor to parent–child relative rotation;
- the parallel-sum inertia and zero-total-charge Routhian;
- survival of a finite stable reduced child minimum.

Open:

- the local Hopf shift/countercurrent profile;
- the off-seam Hamiltonian and spatial Einstein constraints;
- the complete mixed physical Hessian and full Floquet spectrum.

The single-rotor physical-child interpretation is retracted. The corrected
relative reduced child remains conditional, and
`FULL_BHSM_COMPLETE = FALSE`.

Active dependency:

`NONROUND_OFF_SEAM_HOPF_SHIFT_MOMENTUM_CONSTRAINT_WITH_PARENT_CHILD_COUNTERCURRENT_AND_COMPLETE_MIXED_HESSIAN`
