# AE3.1 current-C2 lepton/composite mixing structure

The gauge auxiliary action extends to the charged-lepton LR channel because
its exact group weight is `C_e=3/10`.  On the nonzero minimal-SM channels,

```text
K_HS^(-1) = G_C2^(-1) diag(5/14,5/13,5/3)
```

in `(up,down,charged-lepton)` order.  The neutrino gauge weight is zero, so no
inverse neutrino auxiliary block is manufactured.

AE3.1 already owns an intrinsic charged-lepton vertex

```text
V_intrinsic = sigma1_LR tensor Y_l,
```

while the exact gauge HS rewrite supplies

```text
V_HS,e = sigma1_LR tensor I3.
```

Both act on the same `bar(L_L)e_R+h.c.` bilinear and are chirality odd.  The
combined first-order pencil is affine, so its first-order mixed contact is
zero.  Its squared-pencil mixed contact is fixed rather than independent:

```text
Q_intrinsic,HS = V_intrinsic^dagger V_HS
               + V_HS^dagger V_intrinsic
               = 2 I_LR tensor Y_l.
```

## Mixed determinant block

The formal one-loop mixed Hessian is

```text
M_eHS[C] = Tr[G_e[C] V_HS G_e[C] V_intrinsic].
```

Because the current charged-lepton operator preserves the three family
projectors and `Y_l` is diagonal on them,

```text
M_eHS[C] = sum_f y_f chi_f[C] P_f.
```

The state-independent Hadamard pole therefore has the exact action-derived
family direction

```text
M_eHS,sing = chi_Had,sing Y_l.
```

The finite coefficients `chi_f,fin[C]` remain covariance dependent and are not
set equal.  Thus this result attaches the intrinsic lepton hierarchy to the
composite mixing operator, but it does not yet produce its finite physical
normalization.

The intrinsic charged-lepton Higgs shares species only with `H_HS,e`.
Orthogonal quark/lepton projectors make the direct intrinsic--up and
intrinsic--down blocks zero.  More strongly, adding retained vector gauge
vertices cannot repair the block: every scalar insertion flips chirality,
whereas every gauge vertex preserves chirality and species.  Each separate
fermion loop would contain one unpaired chirality flip and therefore cannot
close.  The zero persists to all perturbative orders in vector gauge vertices
about a chirally symmetric quark background.

This scoped result does not exclude a separately derived nonperturbative
chirality-violating topological vertex.  Within the retained action, however,
the first quark link must be a common parent odd endomorphism or an
independently derived nonzero quark gap; a gauge-mediated 2PI term by itself
cannot provide it.

Promoted:

- the charged-lepton gauge auxiliary channel;
- the shared intrinsic/composite lepton vertex and contact jet;
- the universal Hadamard mixing direction proportional to `Y_l`;
- the species/chirality block pattern and its all-orders vector-gauge scope.

Not promoted:

- the finite lepton/composite mixing matrix;
- a common parent odd intrinsic/quark endomorphism or nonzero quark gap;
- a physical normalized Higgs eigenvector;
- canonical quark Yukawas, quark masses, or poles.

The next science calculation returns to the same-current-`C2` action and must
derive the common odd endomorphism on `I_up,I_down`, or independently establish
a nonzero quark gap from the full composite Hessian.  A fitted mixing entry or
a vector-gauge 2PI diagram forbidden by chirality may not replace it.
