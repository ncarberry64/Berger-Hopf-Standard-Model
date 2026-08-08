# BHSM v14.90 intrinsic full-preimage dynamical momentum gate

## Verdict

The retained Lorentzian P1 action owns genuine time-dependent canonical
metric momentum. This is a bounded positive result: the v14.41 stationary
ADM-shift theorem does not imply that every gravitational momentum vanishes.

The only explicit constraint-reduced P1 dynamical solutions are nevertheless
homogeneous round and Jensen trajectories. Their momentum is common to both
reflection-related caps, so its reflection-relative part vanishes. The
archive does not contain the nonhomogeneous degree-one full-preimage phase
space, moving-seam symplectic reduction, cap inertia operators or coexact L2
momentum--shape vertex. General intrinsic relative tensor modes are therefore
open, not ruled out, and no physical softening correction can yet be inserted.

## Recovered canonical action

The action-owned P1 Lorentzian term is

```text
S_P1=(1/2) integral_M8 sqrt(-G)(kappa1 R-kappa0)
     +kappa1 integral_boundary epsilon K.
```

For an ADM split it gives

```text
S_P1=(1/2) integral dt d7x N sqrt(h)
     [kappa1(R7+KijKij-K^2)-kappa0],
pi^ij=(kappa1/2)sqrt(h)(K^ij-Kh^ij).
```

Lapse and shift are multipliers with vanishing primary canonical momenta.
Metric velocity in `K_ij` is not a freely chosen shift. The repository derives
the lapse-preserving homogeneous reduction on `M8=I_t x S7`, but not the
coupled nonhomogeneous full-preimage phase space.

The intrinsic M4 B1 action remains a provisional boundary axiom, not a parent
P1 derivation. Eta has the v14.87 momentum on its positive Legendre branch;
gauge and adopted Dirac sectors have their standard canonical structures only
conditionally, without the required coupled degree-one common domain. The
seam embedding and global enclosure scale are not retained canonical fields.

## Two-cap theorem

For a reflection identification `R`, define

```text
DeltaPi=Pi_plus-R^dagger Pi_minus R.
```

On either explicit homogeneous P1 trajectory, `K_ij=H h_ij` and the two caps
are restrictions of the same invariant slice. Hence their nonzero common
expansion momentum is reflection identified and

```text
DeltaPi=0,
Delta sigma=0.
```

This does not prove that a nonhomogeneous counterpropagating physical solution
cannot exist. It proves that the implemented P1 solution sector does not
supply one. A kinematic assignment with opposite cap momenta is not a solution
or state-selection theorem.

## Dynamical spectrum and representation screen

The round P1 branch has two homogeneous constraint-reduced shape masses
`4/a^2`; the Jensen branch has `52/(5a^2)` and `-4/a^2`. These modes are
cap-common. The associated tower has only an instantaneous/adiabatic operator
description. No nonhomogeneous gravitational vector/tensor spectrum has been
derived on the compact degree-one full-preimage background.

The v14.88 rigid-L1 times scalar-ell2 representation no-go remains exact. A
rank-two traceless shear has different representation content and is not
excluded by that theorem. This is a possibility statement only: without the
nonhomogeneous operator, projectors and common domain, its coexact L2 content
and mixed vertex are undefined.

## Inertias, current and response

The physical reduced `Pi_plus`, `Pi_minus`, `M_plus`, and `M_minus` are not
defined. Pure cap repartition cannot supply them because v14.85 proves its
total-action Hessian is zero. Reflection equal inertia and `nu=1/4` remain
conditional operator theorems.

The formal candidate is

```text
J_dyn=P_coex,L2 J[DeltaPi,DeltaSigma],
B_dyn,L2=P_L2 D_Q J_dyn.
```

It is undefined on the absent physical common domain and zero in the explicit
homogeneous truncation. For a future positive dynamical block the static
formula is conditionally

```text
DeltaH=-B^dagger K_dyn^-1 B <= 0.
```

At finite frequency it becomes

```text
DeltaH(omega)=-B^dagger[K_dyn-omega^2 M_dyn]^-1B,
```

away from poles, and cannot generally be collapsed to a static Hessian.

## State-selection firewall

A stable oscillator admits nonzero momentum when populated, has zero
cycle-mean momentum, and has zero classical amplitude in its ground state.
Existence does not select a coherent amplitude. A vacuum one-loop route
requires the coupled operator, gauge/ghost cancellation, common domain and a
fixed renormalization prescription; none is presently available.

## Hindsight 20/20

Validated: P1 owns metric momentum; stationary shift is distinct from metric
velocity; explicit homogeneous momentum is cap-common; and a future positive
momentum block has the conditional Schur-softening sign.

Invalidated: treating v14.41 as an all-dynamical-momentum no-go; treating
homogeneous expansion as relative shear; treating the moving-seam contract as
an active canonical field; and treating an allowed oscillator as populated.

Reclassified: intrinsic dynamics remains a nonhomogeneous tensor-mode route,
not an external-driver route.

Open, exactly:

`LORENTZIAN_DEGREE_ONE_FULL_PREIMAGE_BACKGROUND_AND_GAUGE_REDUCED_COUPLED_METRIC_ETA_GAUGE_DIRAC_LINEARIZED_SYMPLECTIC_BOUNDARY_VALUE_PROBLEM_WITH_REFLECTION_ODD_CAP_RELATIVE_TENSOR_MODES_AND_EXPLICIT_COEXACT_L2_MIXED_VARIATION`

The complete L2 Hessian, locking, alpha crossing, Floquet system and flavor
gates are not reached. Frozen predictions are unchanged. USB access is
excluded.
