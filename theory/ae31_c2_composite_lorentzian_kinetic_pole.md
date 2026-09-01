# AE3.1 current-C2 composite Lorentzian kinetic pole

The gauge-derived Hubbard--Stratonovich fields now have a genuine local
derivative principal part.  This is derived from the external-momentum second
variation of the same current-`C2` fermion determinant, not from the old
static susceptibility's mass derivative.

For one unit complex left-right vertex,

```text
Gamma_f = -Tr log(D_C2 + H P_R + Hdagger P_L),
```

the chiral Clifford trace and numerator identity are

```text
tr[P_L slash(q) P_R slash(q+p)] = 2 q.(q+p),
2 q.(q+p) = q^2 + (q+p)^2 - p^2.
```

The first two terms are scaleless tadpoles in dimensional regularization.  The
universal one-pair Euclidean pole is therefore

```text
Gamma_HdaggerH,sing^(2)(p)
  = p_E^2/[16 pi^2 epsilon_UV].
```

On a frozen current-`C2` slice with

```text
h = -d tau^2 + R4(tau)^2 dOmega3^2,
```

the Lorentzian three-channel principal symbol is

```text
H_HS,sing(omega,lambda)
 = diag(9,9,3)*(-omega^2+lambda)/[16 pi^2 epsilon_UV]
```

in the `(up,down,charged-lepton)` unit-vertex basis.  The multiplicities reuse
the valid v16.02 rank-16 pairing trace.  The neutrino is absent from this
matrix because the current gauge kernel has zero neutrino LR attraction and
does not define an invertible neutrino HS coordinate.

This pole is local and fixed by the Hadamard singularity.  It uses continuous
external frequency, carries the current-`C2` Dirac cone, and has one matching
temporal/spatial residue in each channel.  A finite Hadamard-state difference
can change the finite derivative term but not this pole.

## Correcting the historical residue label

The v15.77 quantity

```text
-partial chi_LR/partial(m^2)
```

is a derivative of a static susceptibility with respect to a mass parameter.
It is not

```text
partial_(external p^2) Gamma_HdaggerH^(2)(p)|p=0.
```

The two objects have different functional variations.  Consequently the old
heat-regulated number is not promoted as a current-`C2` wavefunction residue,
and its EC-driven gap branch is not revived.  Only its valid pairing
multiplicities are reused.

## Combined Hessian and claim boundary

The low-momentum structure is now

```text
H_HS = G_C2^(-1) diag(5/14,5/13,5/3)
       - Pi_0,ren[C]
       + diag(9,9,3)(-omega^2+lambda)/[16 pi^2 epsilon_UV]
       + ... .
```

This proves that the auxiliary fields are locally dynamical at the universal
principal pole.  It does not provide the finite renormalized kinetic residue.
It also does not select a broken direction: the up/down derivative pole is
degenerate, while the finite zero-momentum Hessian remains state- and
subtraction-dependent.

Promoted:

- `CURRENT_C2_COMPOSITE_LORENTZIAN_PRINCIPAL_POLE_DERIVED = TRUE`;
- `CURRENT_C2_COMPOSITE_TEMPORAL_SPATIAL_POLE_RESIDUE_MATCH_DERIVED = TRUE`;
- a local derivative term is induced for the three nonzero gauge-HS channels.

Not promoted:

- a finite composite kinetic residue;
- a renormalized zero-momentum Hessian or nonzero gap;
- a physical one-Higgs direction or canonical Yukawa residues;
- physical quark poles.

The next operator is the renormalized full three-channel Lorentzian HS Hessian
with its finite `Pi_0` and `Pi_p2` derived from one selected current-`C2`
action domain.  No cutoff, fitted residue, or old EC number may fill it.

`FULL_BHSM_COMPLETE = FALSE`.
