# AE3.1 current-C2 quark--Higgs contact closure

On the real neutral up/down scalar-source coordinates, the transported
quark--Higgs incidence is the renormalizable first-order Dirac pencil

```text
D(h_u,h_d)=D_0+h_u V_u+h_d V_d.
```

It is affine-linear in the scalar directions. Therefore

```text
d_f D=V_f,
d_f d_g D=0
```

for every `f,g` in `{up,down}`. No higher-dimension scalar--fermion contact is
inserted. In the first-order determinant convention,

```text
Gamma=-Tr log D,
d_g d_f Gamma=Tr[G V_g G V_f].
```

The separate `-Tr[G Q_fg]` term vanishes because the first-order Dirac
contact is zero.

The retained product-Dirac descriptor uses a squared pencil. For

```text
P(h)=D(h)^dagger D(h),
```

the corresponding contact is not zero, but it is not independent:

```text
d_f d_g P=V_f^dagger V_g+V_g^dagger V_f,
Q_ff=2 V_f^dagger V_f.
```

On the transported binary supports, `I_up I_down=0`, so

```text
Q_ud=Q_du=0.
```

The diagonal contacts are positive semidefinite and reproduce the existing
unit-probe quadratic scaling `Q(q)=q^2 Q(1)` and the retained one-channel
factor `Q=2 p^2 M`.

This closes the contact structure while preserving the real obstruction.
Once `V_u,V_d` are fixed, the complete squared-pencil contact jet follows
algebraically. There is no third independent quark contact coefficient.

Promoted conditionally:

- zero first-order Dirac contact for the recovered renormalizable incidence;
- squared-pencil contact closure in terms of `V_u,V_d`;
- zero mixed up/down contact on the transported disjoint supports.

Not promoted:

- the action-owned residues multiplying `V_u,V_d`;
- an action-selected Feynman inverse or quantum channel Hessian;
- quark poles, masses, or CKM mixing.

The remaining common functional must derive the two first vertices with the
same current-C2 action, trace, field normalization, boundary domain, and
reused family shapes `T_u,T_d`. Independent Yukawa, contact, or mass fitting
remains forbidden.

`FULL_BHSM_COMPLETE = FALSE`.
