# BHSM complex-profile isospectral attachment v8.6

## Result

This sprint directly attacks the two objects left open by v8.5:

1. a coefficient-free rule attaching the full-S3 profile to the frozen mass spectrum without changing its eigenvalues;
2. a complex current profile capable of producing a nonzero CKM Jarlskog invariant.

The strongest positive result is

`BHSM_LINEAR_ISOSPECTRAL_SLOT_ATTACHMENT_AND_POLAR_CURRENT_FUNCTORS_CONSTRUCTED_CONDITIONALLY`.

The final fail-closed verdict is

`BHSM_FULL_FLAVOR_COMPLETION_REMAINS_BLOCKED_BY_NO_ACTION_DERIVED_ORIENTED_TRANSFER_WEIGHT_AND_NO_ACTION_OWNED_G2_C3_PROFILE_NORMALIZATION`.

No measured CKM input, fitted continuous phase, new field, frozen-prediction change, or physical CKM claim is introduced.

## 1. Linear f(X)=X isospectral attachment

Let the frozen heavy-to-light transfer spectrum in sector `f` be

```text
D_f=diag(d_f,0,d_f,1,d_f,2),  d_f,0>d_f,1>d_f,2>0.
```

Let `H_f` be a Hermitian full-S3 profile-response matrix with simple spectrum

```text
h_f,0<h_f,1<h_f,2.
```

Consider the unitary orbit of the frozen spectrum,

```text
O(D_f)={U D_f U^dagger : U in U(3)},
```

and the strictly linear alignment functional

```text
E_align(M;H_f)=Tr(M H_f).
```

Von Neumann's trace inequality gives

```text
min_(M in O(D_f)) Tr(M H_f)=sum_i d_f,i h_f,i,
```

where descending frozen eigenvalues are paired with ascending profile eigenvalues. If both spectra are simple, the minimizer is unique modulo phases of its eigenvectors.

Therefore

```text
M_f^*=U_f D_f U_f^dagger,
```

where the columns of `U_f` are the eigenvectors of `H_f`, ordered by ascending profile eigenvalue.

This proves:

- the frozen mass spectrum is preserved exactly;
- the `3!` assignment ambiguity in each sector is removed;
- the joint `3! x 3!` ambiguity is removed;
- only column phases remain, and those are ordinary mass-eigenstate rephasings;
- the construction uses the core rule `f(X)=X` rather than an arbitrary nonlinear response.

Status:

`BHSM_ISOSPECTRAL_SLOT_ATTACHMENT_FUNCTOR_CONSTRUCTED_CONDITIONALLY`.

The condition is that the current action does not yet contain the linear profile-alignment functional or prove that it is the physical energy minimized by the flavor state.

For the real v8.5 heat-profile matrices, the resulting overlap is

```text
|V_align|=
[0.9199403772,0.3869423255,0.0631295427]
[0.2760716958,0.7536635711,0.5964693121]
[0.2783776593,0.5312879240,0.8001493739].
```

It is real and has `J=0`; therefore the slot theorem closes an ambiguity but does not complete CKM.

## 2. Canonical polar-current functor

For any full-rank square transfer matrix `T`, define

```text
U(T)=T(T^dagger T)^(-1/2).
```

This is the unique unitary polar factor. It is also the unique closest unitary matrix to `T` in Frobenius norm.

Thus the v8.5 full-rank profile transfer has a coefficient-free unitary extraction with no eigenvector assignment:

`BHSM_POLAR_CURRENT_FUNCTOR_CONSTRUCTED_CONDITIONALLY`.

This is not automatically the physical CKM matrix. The action must still prove that the positive polar factor

```text
P=(T^dagger T)^(1/2)
```

belongs to wavefunction/current normalization rather than representing physical nonuniversal vertex singular values.

## 3. Single Hopf-phase no-go for the polar cross current

A single right-Hopf translation gives

```text
T_ij(theta)=exp(i m_u,i theta) T_ij(0) exp(-i m_d,j theta).
```

In matrix form,

```text
T(theta)=D_u(theta) T(0) D_d(theta)^dagger.
```

Polar decomposition is covariant under unitary left/right multiplication:

```text
U[T(theta)]=D_u(theta) U[T(0)] D_d(theta)^dagger.
```

Therefore the magnitudes are unchanged and the phase is only row/column rephasing. If the unshifted polar matrix is real, its Jarlskog invariant remains zero.

Result:

`SINGLE_HOPF_U1_TRANSLATION_CANNOT_GENERATE_CP_IN_THE_CROSS_POLAR_CURRENT`.

A physical CP phase requires at least two non-equivalent harmonic channels or noncommuting profile/holonomy data.

## 4. Oriented lower-partner incidence candidate

The strongest discrete weighted transfer found in the existing architecture is

```text
T_or=Theta_u^(-1/2) H_ud Theta_d,
U_or=polar(T_or).
```

The interpretation is:

- inverse square-root normalization on the outgoing up-sector carrier;
- full forward transfer on the colored lower weak partner;
- the down/up incidence distinction is motivated by `Omega_up=6`, `Omega_down=12`.

The exponent map itself is not derived by the action.

The candidate gives

```text
|U_or|=
[0.9725017465,0.2328930238,0.0010919842]
[0.2326746481,0.9713643228,0.0481026039]
[0.0101420464,0.0470339433,0.9988418028].
```

Compared with the frozen internal-rule screen:

```text
sin(theta12): +3.22 percent
sin(theta23): +9.65 percent
sin(theta13): -69.35 percent
J:             zero
```

It reconstructs the Cabibbo and 2-3 hierarchy surprisingly closely without fitting, but it fails the 1-3 channel and CP.

Result:

`ORIENTED_INCIDENCE_POLAR_CANDIDATE_APPROXIMATES_THETA12_AND_THETA23_BUT_FAILS_THETA13_AND_HAS_ZERO_CP`.

## 5. G2-complex and C3-triality profile

BHSM already contains two discrete complex structures:

```text
Pi_10=(Q-iJ_u)/2
```

from the G2 polarization, and the nontrivial `chi=1` character of the triality `C3` Fourier decomposition.

This motivates a no-continuous-parameter complex current with the fixed phase `-i`.

### Optimistic mixed-normalization candidate

Using

```text
T_complex=T_point-i T_chi1
```

and the oriented polar map gives

```text
|U_complex|=
[0.9671319919,0.2542566904,0.0030406706]
[0.2539756032,0.9660008366,0.0483609010]
[0.0123330147,0.0468606357,0.9988252988],
```

with

```text
J=3.5910408199e-5.
```

The frozen internal-rule value is

```text
J_frozen=3.1011702945e-5.
```

Relative errors are

```text
sin(theta12): +12.69 percent
sin(theta23): +10.24 percent
sin(theta13): -14.64 percent
J:             +15.80 percent.
```

This is a notable near miss obtained without a fitted continuous phase. It cannot be promoted because `T_point` and `T_chi1` use inequivalent single-center and normalized-orbit conventions. Their relative norm is not fixed by the action.

### Character-normalized candidate

The representation-consistent normalized combination is

```text
T_complex,norm=T_chi0-i T_chi1.
```

It generates nonzero CP, but gives

```text
sin(theta12): -55.22 percent
sin(theta23): +45.05 percent
sin(theta13): +36.09 percent
J:             -23.04 percent.
```

Thus the coefficient-free normalized construction fails the frozen hierarchy.

Result:

`G2_C3_COMPLEX_PROFILE_CAN_GENERATE_CP_WITHOUT_A_CONTINUOUS_PHASE_BUT_NO_ACTION_OWNED_NORMALIZATION_PASSES_THE_FROZEN_SCREEN`.

## 6. Hindsight result

The v8.5 blocker has split into two sharply different pieces.

### Closed conditionally

- Unique isospectral slot attachment through a linear trace minimum.
- Unique full-rank polar-current unitary.
- A discrete source of complex phase from G2 polarization and triality character.
- Nonzero Jarlskog generation without fitting a continuous phase.

### Invalidated

- The old `3! x 3!` ambiguity as unavoidable; it is removed by the linear trace theorem.
- A single Hopf translation as physical CP in the polar cross-current route.
- The real oriented transfer as complete CKM.
- The normalized G2-C3 character profile as the frozen CKM solution.
- Promotion of the visually close mixed-normalization candidate.

### Still open

- Derive `Theta_u^(-1/2) ... Theta_d` or another transfer weighting from the oriented two-cap charged-current action.
- Dynamically select the G2 unit section and orientation.
- Derive a map from the triality character carrier to the Berger profile harmonics.
- Fix the singlet/complex-character relative normalization from one action term.
- Prove that the positive polar factor is absorbed by canonical field/current normalization.

## Exact next object

`ACTION_DERIVED_ORIENTED_CHIRAL_TRANSFER_AND_NORMALIZED_G2_C3_COMPLEX_CURRENT_PROFILE`.

This is now the smallest remaining flavor object. The mathematical attachment and CP-capable representation content exist. What remains is one action theorem fixing their incidence powers and channel normalization.

