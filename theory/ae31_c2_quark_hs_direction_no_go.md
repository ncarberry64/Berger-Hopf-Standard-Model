# AE3.1 current-C2 quark HS channel-direction no-go

The nonzero reduced current-C2 HS vertex and the attached `T_u,T_d` family
operators do not by themselves select the relative up/down Yukawa residue.
The missing information is a channel direction, not merely a kinetic norm.

For any positive diagonal quark-channel kinetic form,

```text
Z(c) = Z_up c_up^2 + Z_down c_down^2,
```

canonical normalization imposes one equation `Z(c)=1` on two positive
components.  Every normalized direction is parameterized by

```text
c_up   = cos(theta)/sqrt(Z_up),
c_down = sin(theta)/sqrt(Z_down),
0 < theta < pi/2.
```

The constraint Jacobian has rank one and the channel-direction nullity is
exactly one.  The ratio

```text
c_up/c_down = sqrt(Z_down/Z_up) cot(theta)
```

varies continuously along the normalized ellipse.

## Historical four-channel trace

The reusable algebraic content of v16.02 is the pairing multiplicity matrix

```text
D = diag(9,9,3,3)
```

in the `(up,down,charged-lepton,neutrino)` basis.  Its numerical periodic-cycle
kinetic residue is not promoted to current C2.  More importantly, equal up and
down multiplicities make the isolated quark quadratic form `O(2)` invariant.
That is a degeneracy: it supplies no preferred angle and does not imply equal
physical components.  The v16.02 artifact itself correctly records that its
physical four-channel direction was not selected.

## Tensoring the family operators

The candidate family pushforward has the form

```text
V_spatial tensor [(c_up T_u)_up + (c_down T_d)_down].
```

Two distinct normalized angles leave all within-sector eigenvalue ratios and
all current-C2 attachment commutators unchanged while changing the heavy
up/down ratio.  Tensoring the already-reused noncentral family shapes therefore
preserves the channel ambiguity; it does not select its angle.

The exact next selector is the same-domain quark-channel Hessian

```text
H_qH^current-C2 =
[[H_uu,H_ud],
 [H_du,H_dd]]
```

derived from one `Gamma_qH` together with the intrinsic `H/H_tilde`
identification, dynamical kinetic residue, family pushforward, and boundary
domain.  A unique physical eigendirection or an action-derived equivalent
source can close the ratio.  A diagonal kinetic trace, equal-component
assumption, copied historical residue, or quark-mass fit cannot.

Promoted:

- `CURRENT_C2_QUARK_HS_KINETIC_NORMALIZATION_NULLITY_DERIVED = TRUE`;
- quark-channel direction nullity is exactly one after canonical kinetic
  normalization;
- historical channel multiplicities are reused without promoting their old
  periodic-cycle residue.

Not promoted:

- a current-C2 quark-channel direction;
- relative or absolute up/down Yukawa residues;
- physical quark poles or CKM mixing.

`FULL_BHSM_COMPLETE = FALSE`.
