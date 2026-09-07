# AE3.1 current-C2 color-singlet residual-response bridge

The historical BHSM record already supplies normalized meson and baryon
Wilson singlets, the closed-`S3` global color-Gauss condition, and the current
quark color representations.  It does not supply a solved hadron or a
confining potential.  The missing identification bridge can nevertheless be
narrowed exactly.

Let `P1` project onto a normalized color singlet and `Q=I-P1`.  For any
constituent-resolved exterior color probe `V_a`, tracelessness gives

```text
P1 V_a P1 = 0.
```

Thus the completed color-neutral object has no linear exterior color charge.
For a uniform long-wavelength probe the total generator itself annihilates
the singlet, so even `Q V_a P1` vanishes.  This is the precise no-leakage
statement.

A finite-size probe weights different constituents differently.  It still
has zero direct singlet charge, but it can connect the singlet to internal
colored states.  With `Tr(T_a T_b)=delta_ab/2`, the exact contracted
transition numerators are

```text
meson:  N_M = sum_a ||Q V_a P1||_HS^2 = (4/3)(f_q-f_qbar)^2,
baryon: N_B = sum_a ||Q V_a P1||_HS^2 = 2 sum_i(f_i-f_bar)^2.
```

The first possible singlet exterior response is therefore not a free gluon
field and not a one-color exchange.  It is the Schur/polarizability operator

```text
H_eff^(2) = -sum_a P1 V_a Q [Q(H_hadron-E1)Q]^-1 Q V_a P1.
```

Whenever the colored excitation resolvent is positive, this operator is
negative semidefinite.  Its numerator is now derived and is nonzero exactly
for a constituent-resolving probe.  Its magnitude is not yet a BHSM
prediction because the current action has not produced the returned hadron
Hamiltonian, its colored excitation gaps, or the two-hadron exchange kernel.

This also resolves the intended ontology:

```text
internal quark/gluon dynamics -> color-singlet enclosure
                              -> zero linear exterior color charge
                              -> possible finite-size singlet polarizability
```

The v14.28 Gaussian-collar zero-string-tension no-go remains binding.  The
Wilson operator remains an exact source/observable insertion, not an added
action term.  The later v16.36 boundary is also preserved: closed-child
singlet kinematics do not by themselves prove a global asymptotic
confinement theorem.

Promoted:

- exact vanishing of the direct singlet exterior color charge;
- exact meson and baryon finite-size transition numerators;
- the sign and nonzero criterion of the singlet Schur polarizability.

Not promoted:

- a returned hadron excitation resolvent;
- a physical residual nuclear force or inter-hadron potential;
- an area law, Yang--Mills mass gap, hadron spectrum, or hadron mass.

`FULL_BHSM_COMPLETE = FALSE`.
