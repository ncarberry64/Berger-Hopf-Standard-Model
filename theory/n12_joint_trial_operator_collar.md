# Current-reset coupled trial operator collar

This calculation serves the existing same-action force/root obligation in
`docs/GATE7_CURRENT_CALCULATION_SCOPE.md`. Its consumer is the C2 Weyl/load
factor in the common joint heat operator, including the amplitude boundary
spectral contraction. No completion condition is added.

The saved `gate7_current_history_20260927/core` begins at a different
endpoint from `gate7_current_reset_connection_20260927/reset_match_complete`.
Their outgoing log-radii differ by about `1.33997e-7`. That finite prefix
and its jets remain evidence for their original base, not same-base
operands for the current joint force. Even the zero-order coefficient
mismatch is much larger than its stored rounding radii. A change of name
or reuse of relative mesh weights cannot remove it.

The smaller replacement is one evaluated outgoing coefficient collar,
with a proper-duration enclosure, at the actual saved reset member. It
does not rebuild the old 1,222-cell history or compute new launch columns.
An endpoint point alone cannot enclose the proper-duration integral or
the boundary spectral response; one local field domain suffices for this
collar. Further operator contractions must retain the unresolved tail.

## Off-root coordinates, not a relabelled signed eigenvalue

The frozen current outgoing branch-24 selected eigenvalue is negative and
excludes zero. The coupled event formulation already contains the selected
descriptor event equation. For a trial evaluation, set its **independent
event descriptor coordinate** to zero and retain

```
E_event = lambda_selected(Y_event)-s_event
```

with its actual nonzero value. This does not replace the certified signed
eigenvalue by zero and does not certify the trial point as a physical
event. It is an off-root argument of the existing augmented KKT problem.
An eventual normal/root solve must eliminate the defect before this
collar can be promoted as physical history. The incoming amplitude remains
another unsolved coordinate of that same saddle, not a selected number.

The existing rate owner separates the independent descriptor s from the
selected eigenvalue in its common eigenline/hard-response solve. With

```
G_raw=(s*v,b*psi+s*hard),
s'=(c*b+s*R)/||G||,
```

its selected-line derivative satisfies
`lambda_selected'=(c*b+s*R)/||G||` as well. This follows by contracting
`D L_zz` with the same normalized eigenline twice and the actual state
direction. Thus `lambda_selected-s` is conserved along this augmented
trial field. The off-root defect is explicit; it is not lost during
propagation or equated to physical failure.

## One-domain enclosure

Evaluate this unchanged action-owned field on a new small weighted-state
box about the current outgoing reset state and on `0<=s<=s_max`. The
indexed normalized eigenline inclusion and common bordered solve prove
that the branch field is analytic there with positive arc norm. The
strict first-exit bounds

```
h*sup |Y_i'| < state_radius_i,
h*sup s' < s_max,
inf s' > 0
```

give existence in that box over the proof collar `0<=r<=h`. Local
uniqueness follows from analyticity of this regular branch. No bound on
a full 99-column Jacobi matrix is needed for this value-only calculation.

The initial coordinate is `s(0)=0`; hence `s(r)` is enclosed by the
positive interval `r*[inf s',sup s']`. Since proper clock is
`d tau/dr=N*s/||G||`,

```
T_collar in (N/||G||) * [inf s',sup s'] * h^2/2 > 0.
```

All factors on the right are uniform field-box enclosures. A symmetric
descriptor interval containing negative values is not substituted for
this directed clock argument. Radius, lapse, proper radius rate, scalar
potential and both Dirac superpotentials are enclosed directly by the
existing coefficient map over the same box, without midpoint
interpolation or a continuum error inferred from a discrete mesh.

The collar horizon is a proof-domain parameter. It is not a physical
terminal stop, formation amplitude, decay time, or change to the joint
operator's far endpoint class. Subsequent Weyl/heat bounds must account
for the remainder of the retained child domain.

## Complete-domain fixed-channel boundary heat bound

Let `M(-u)` be the C2 inward Dirichlet-to-Neumann value at its initial
seam for a retained nonnegative scalar or factorized Dirac channel. The
complete exterior remains active. A linear trial field, falling from
one to zero within the current collar and extended by zero afterwards,
gives the existing variational estimates

```
0 <= M(-u) <= 1/T + (V_max+u)*T/3                    (scalar),
0 <= M(-u) <= 1/T + W_max + (W_max^2+u)*T/3           (Dirac).
```

The exact lower endpoint of the duration enclosure is used as T. These
are full-domain comparison bounds, not a Dirichlet condition imposed at
the collar's far edge. The unknown exterior minimizes the full energy;
the zero-extended trial is only an admissible upper comparison.

For the positive Dirichlet spectral measure `rho` of the same complete
operator at this seam, the subtracted Weyl representation reads

```
M(-u)-M(0) = u * integral d rho(lambda)/(lambda*(lambda+u)).
```

The second-order scalar/factorized operator has no affine spectral term
in this identity. At zero threshold the expression is the monotone
limit; positivity and the collar trial keep M(0) finite and nonnegative.
For `u*ell^2>=1`,

```
exp(-ell^2*lambda) <= u/(lambda+u),
H(ell) = 1/2 integral exp(-ell^2*lambda)/lambda d rho(lambda)
       <= (M(-u)-M(0))/2 <= M(-u)/2.
```

This yields a numerical **complete-domain fixed-channel** boundary heat
moment from the new collar, even without a positive global spectral gap
or a far-tail trajectory. It includes interior spectral contributions.
Continuous spectrum approaching zero is covered; a free half-line test
checks that case. The four current channel results are bounds at the
C2 seam reference. The incoming transfer and physical contacts must be
composed before interpreting them at the moving birth endpoint. Their
signs and angular weights have not yet been combined into the joint
force. In particular, a single negative-axis Weyl value is not being
reported as the heat functional.

The bound is deliberately a first variational enclosure. Its large width
measures unresolved operator response, not a physical decay or failure.
It cannot certify q66, amplitude stationarity, or a root. The next smaller
improvement is a correlated subtracted Weyl/heat contraction in the
incoming-plus-C2 system; summing these coarse bounds sector by sector is
not a substitute for that signed composition.

`Gate7_closed=False`. `FULL_BHSM_COMPLETE=False`.
