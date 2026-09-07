# AE3.1 current-C2 LR susceptibility factorization

The historical round-child susceptibility can be transported to the spatial
operator on every certified finite-core current-`C2` Cauchy slice without
assuming a stationary spacetime.  For

```text
h = -d tau^2 + R4(tau)^2 dOmega3^2,
```

the round-`S3` Weyl eigenvalues and multiplicities at `tau=tau0` remain

```text
E_n = (n+3/2)/R4(tau0),       d_n = (n+1)(n+2).
```

Thus the regulated spatial LR sum per left-right pair is

```text
chi_N(tau0) = S_N/[2 pi^2 R4(tau0)^2],
S_N = (N+1)(N+3)/2 - [psi(N+5/2)-psi(3/2)]/4.
```

This is a slice-local spatial spectral result, not a global-frequency
Feynman loop.  The latter still requires a current-`C2` covariance.

## Universal pole and channel factorization

The historical Laurent expansion

```text
S(s;q) = -1/(8s) + 1/24 - gamma_E/4 - log(2)/2 - log(q)/4 + O(s)
```

therefore gives the local pole

```text
-1/[16 pi^2 R4(tau0)^2 s]
```

per unit LR pair.  All Hadamard states have the same local singularity; their
two-point functions differ only by a smooth bisolution.  The pole is therefore
state independent, while the renormalized finite response is not.

In the unit-vertex auxiliary Hubbard--Stratonovich coordinates, the transported
incidences satisfy

```text
Tr(I_up^dagger I_up) = Tr(I_down^dagger I_down),
Tr(I_up^dagger I_down) = 0.
```

The reusable four-channel trace also assigns equal up/down multiplicity
`diag(9,9)`.  Consequently the normalized Hadamard pole matrix is exactly
proportional to `I2`.  This statement concerns unit-vertex composite channel
coordinates; it does not insert or derive intrinsic Higgs residues `c_u,c_d`.

## Composite Hessian

Combining the common pole with the current-`C2` gauge ray gives

```text
H_C = K_LR^(-1) - Pi_Had,sing I2 - Pi_fin[C],

K_LR^(-1)
  = G_C2^(-1) diag(5/14,5/13)
  = 135/(364 G_C2) I2 - 5/(364 G_C2) sigma3.
```

The universal pole has zero traceless projection.  It cannot erase or reverse
the exact gauge-induced relative curvature splitting.  For positive `G_C2`,
the unit-vertex up channel has lower inverse curvature than the down channel.

This does not yet select the physical Higgs direction.  An explicit
same-Hadamard-class covariance witness changes the finite response by a matrix
with a nonzero traceless off-diagonal part.  Hence `Pi_fin[C]` can rotate the
channel eigenvectors even though it cannot change the universal pole.

Promoted:

- the current-`C2` round-slice LR spectral sum;
- the state-independent local Hadamard pole factor;
- the unit-vertex composite trace/traceless Hessian decomposition;
- cancellation of the common ultraviolet pole from the traceless channel.

Not promoted:

- a finite renormalized LR susceptibility;
- an action-selected covariance;
- intrinsic-Higgs/composite mixing;
- a physical Higgs direction, gap, Yukawa residue, or quark pole.

The next operator is the block Hessian

```text
H_mix = [[H_intrinsic, M_HS],
         [M_HS^dagger, K_LR^(-1)-Pi_Had,sing I2-Pi_fin[C]]].
```

Its finite covariance and mixing blocks must come from the same action and
current-`C2` domain.  No cutoff, fitted subtraction, or arbitrary vacuum is
admitted.
