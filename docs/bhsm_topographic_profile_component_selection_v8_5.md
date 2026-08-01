# BHSM topographic-profile component selection v8.5

## Result

This sprint tests whether the existing scalar/topographic-profile idea can
supply the two objects left open by v8.4:

1. one normalized state inside each degenerate Berger block;
2. the coefficients multiplying the normalized weak-current intertwiners.

The strongest supported positive result is

`BHSM_TOPOGRAPHIC_REPRODUCING_KERNEL_COMPONENT_SELECTOR_CONSTRUCTED_CONDITIONALLY`.

The final fail-closed verdict is

`BHSM_MASS_AND_CKM_REMAIN_BLOCKED_BY_NO_ACTION_SELECTED_FULL_S3_COMPLEX_PROFILE_AND_NO_ACTION_DERIVED_PROFILE_TO_ISOSPECTRAL_FLAVOR_ORIENTATION_FUNCTOR`.

No measured mass, fitted matrix, new continuous parameter, physical CKM
matrix, or frozen-prediction change is introduced.

## 1. A point and frame select one state in every Berger block

Use normalized Haar measure on `SU(2)` and

```text
Y^J_(n,m)(g)=sqrt(2J+1) D^J_(n,m)(g).
```

For a fixed associated block `H_(J,m)`, its reproducing kernel is

```text
K_(J,m)(g,h)=sum_(n=-J)^J Y^J_(n,m)(g) conjugate(Y^J_(n,m)(h)).
```

Unitarity of the Wigner matrix gives

```text
K_(J,m)(h,h)=2J+1.
```

Therefore the normalized Riesz representative of point evaluation at `h` is

```text
|J,m;h> = sum_n conjugate(D^J_(n,m)(h)) |J,n,m>.
```

At the identity frame,

```text
|J,m;e>=|J,n=m,m>.
```

This is an exact rank-one selector inside every frozen block. It solves the
v8.4 component-selection problem **conditional on a selected full-S3 point
and frame**.

It does not prove that the current BHSM action selects that point or frame.
The stored scalar/topographic peak `y0` is not yet an action-derived Wigner
axis, and the solved v5.7 profile is the homogeneous reduced profile rather
than a nonhomogeneous full-Berger profile.

## 2. Complete scalar-profile moment functional

Expand a scalar profile as

```text
Phi(g)=sum_(L,p,r) phi_(L,p,r) Y^L_(p,r)(g).
```

For identity-frame coherent states, the up/down matrix element is

```text
M_ij[Phi]
 = sum_L phi_(L,r_ij,r_ij)
   sqrt((2L+1)(2J_d,j+1)/(2J_u,i+1))
   CG(J_d,j m_d,j,L r_ij|J_u,i m_u,i)^2,
```

where

```text
r_ij=m_u,i-m_d,j,
max(|J_u,i-J_d,j|,|r_ij|)<=L<=J_u,i+J_d,j.
```

The sum is finite. This is the explicit profile-to-current coefficient
functional sought after v8.4. Once the action supplies the profile moments
`phi_(L,p,r)`, every frozen current entry is fixed without fitting a 3 by 3
matrix.

## 3. Homogeneous/Hopf-neutral profile no-go

The frozen quark right-weight matrix is

```text
r = [ [0,0,-2],
      [3,3, 1],
      [4,4, 2] ].
```

If the scalar profile is invariant under the right Hopf `U(1)`, then

```text
Phi(g exp(theta T3))=Phi(g)
```

forces

```text
phi_(L,p,r)=0 for r!=0.
```

Only the entries `(U0,D0)` and `(U0,D1)` survive:

```text
support = [ [1,1,0],
            [0,0,0],
            [0,0,0] ].
```

Hence

```text
rank M <= 1.
```

Therefore

`HOPF_PHASE_NEUTRAL_SCALAR_PROFILE_CANNOT_GENERATE_FULL_RANK_FROZEN_QUARK_MIXING`.

This rules out the existing homogeneous scalar/topographic profile as the
complete weak-current mechanism.

## 4. Minimum full-rank profile content

Each determinant term selects one entry in every row and every column. The
six corresponding right-weight triples are

```text
(0,3,2), (0,1,4), (0,3,2),
(0,1,4), (-2,3,4), (-2,3,4).
```

Every possible determinant term therefore requires **three distinct Hopf
weights**.

Thus a full-rank scalar-profile current needs at least three independent
nonzero right-weight moments. A point delta profile is also insufficient,
because

```text
V_ij=u_i(h0)^* d_j(h0)
```

is one outer product and has rank at most one.

Finite width is not cosmetic: it is required to support independent harmonic
moments.

## 5. Full point-centered Berger heat-kernel candidate

The natural no-fit nonhomogeneous candidate is the point-centered Berger heat
kernel

```text
Phi_s(g)=K_s(g,e).
```

Its normalized harmonic coefficients are

```text
phi_(L,p,r)=sqrt(2L+1) exp[-s lambda_(L,r)] delta_(p,r).
```

Using the frozen values

```text
a=1.157054135733433,
s=1/(4pi),
```

produces the cross-sector transfer matrix

```text
H_ud =
[ 1.0000000000, 0.05803183384, 0.003349560164 ]
[ 0.02198751774,0.01162371324, 0.2046645093   ]
[ 0.00004208950,0.000948669389,0.2216320255  ].
```

Its determinant is approximately

```text
0.00209979914246,
```

so it has rank three. This proves that a full-S3 finite-width profile can, in
principle, resolve all quark channels without nine independent current
parameters.

However `H_ud` is not unitary. It is a multiplication/transfer matrix, not an
action-derived isometry between normalized quark mass eigenbases. It is not
promoted to CKM.

## 6. Direct profile dressing kill screen

The most direct positive Hermitian attachment is

```text
M_f = D_f^(1/2) H_f D_f^(1/2),
```

where

```text
D_f=diag(exp[-s lambda_f,i])
```

is the frozen hierarchy and `H_f` is the same-sector heat-profile matrix.

The resulting heavy-normalized eigenvalue ratios are

```text
charged leptons: (1, 0.07378361092, 0.0003623356502)
up:              (1, 0.02098242048, 0.00002398917897)
down:            (1, 0.02628315333, 0.001509904423)
```

The frozen ratios are

```text
charged leptons: (1, 0.06007447093, 0.0002972910646)
up:              (1, 0.008310500554,0.00001269046302)
down:            (1, 0.02193397150, 0.001116520055).
```

The direct attachment shifts every nonbase ratio. The middle-up ratio changes
by a factor about `2.525`.

Therefore

`DIRECT_HEAT_PROFILE_DRESSING_REJECTED_BY_FROZEN_RATIO_LOCK`.

## 7. Isospectral orientation route

One can preserve the exact frozen ratios by using the profile only to orient
the mass operator:

```text
H_f U_f=U_f h_f,
M_f=U_f D_f U_f^T.
```

This introduces no continuous parameter and preserves the eigenvalues of
`D_f` exactly.

But it does not close BHSM:

- each sector has `3!` eigenvector-to-frozen-slot assignments;
- the up/down pair has `3! times 3! = 36` assignments;
- all 36 give different absolute overlap matrices;
- the real heat profile gives real orthogonal overlaps;
- every candidate has Jarlskog invariant exactly zero;
- the action does not state that profile eigenvectors orient the frozen mass
  spectrum.

A representative ascending-eigenvalue assignment gives

```text
|V| =
[0.91994038,0.38694233,0.06312954]
[0.27607170,0.75366357,0.59646931]
[0.27837766,0.53128792,0.80014937].
```

This is a diagnostic consequence of one unselected assignment, not a CKM
prediction.

The result is

`ISOSPECTRAL_HEAT_PROFILE_ORIENTATION_PRESERVES_FROZEN_RATIOS_BUT_LEAVES_DISCRETE_SLOT_ASSIGNMENT_AND_CP_OPEN`.

## 8. Sprint verdict

### Validated

- A selected full-S3 point/frame uniquely selects one normalized state inside
  every Berger block.
- The complete finite scalar-profile harmonic-moment functional is explicit.
- A Hopf-neutral profile has rank at most one on the frozen quark ledger.
- Every nonzero determinant requires three distinct Hopf-weight moments.
- A full point-centered Berger heat kernel produces a full-rank no-fit
  transfer candidate.

### Invalidated

- The homogeneous scalar/topographic profile as the complete CKM source.
- A point delta profile as a full-rank current.
- Direct heat-profile dressing under the strict frozen-ratio lock.
- A real isospectral heat-profile orientation as a complete CKM-plus-CP
  theorem.

### Still open

- An action-selected full-S3 point/frame or equivalent orientation.
- A derived nonhomogeneous complex Berger profile with at least three Hopf
  moments.
- A complex phase or holonomy producing a nonzero Jarlskog invariant.
- An action-derived rule attaching profile eigenvectors to the frozen
  isospectral mass hierarchy.
- An action-selected eigenvector-to-slot assignment.

## Exact next object

`ACTION_DERIVED_NONHOMOGENEOUS_BERGER_WEAK_CURRENT_PROFILE_WITH_COMPLEX_HOPF_MOMENTS_AND_ISOSPECTRAL_SLOT_ATTACHMENT`.

This is narrower than the v8.4 blocker. Component selection and the complete
moment map are now constructed conditionally. The remaining work is to make
the profile, its complex Hopf moments, and its isospectral attachment actual
outputs of the existing BHSM action.

