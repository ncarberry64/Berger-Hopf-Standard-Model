# AE3.1 current-C2 neutral connection Hessian

The intrinsic AE3.1 Higgs action and the already attached same-domain current
pair `(J3,JY)` now determine the broken neutral Hessian in gauge-connection
coordinates. This is independent of the rejected Einstein--Cartan candidate.

For

```text
H_0=(0,v_BH/sqrt(2)),
T3(H_0)=-1/2,
Y_BH(H_0)=+1/2,
```

the selected component is neutral under

```text
Q_em=T3+Y_BH.
```

Write the neutral covariant-derivative coordinates as

```text
W3_hat=g2 W3,
B_hat=g1 B.
```

No numerical `g2` or `g1` is inserted. The Higgs kinetic term gives

```text
H_neutral=(v_BH^2/4) [[1,-1],[-1,1]]
```

in the basis `(W3_hat,B_hat)`. It has exactly one null vector,

```text
v_Q=(1,1)/sqrt(2),
```

and one positive broken vector `(1,-1)/sqrt(2)` with curvature `v_BH^2/2`.
The numerical GeV-squared matrix uses the already inherited conditional
`v_BH`; its absolute unit remains conditional and no measured Higgs VEV is
used.

The fields and currents rotate together:

```text
A_Q=(W3_hat+B_hat)/sqrt(2),
Z_H=(W3_hat-B_hat)/sqrt(2),

J_Q=(J3+JY)/sqrt(2),
J_H=(J3-JY)/sqrt(2),

W3_hat J3+B_hat JY=A_Q J_Q+Z_H J_H.
```

Thus the action discovers the structural `Q_em` null connection and its
current on the actual current-C2 source domain. This is a connection-coordinate
rotation, not yet the canonical Weinberg rotation.

The distinction matters because the same-C2 gauge/ghost frequency Hessian
has already produced an unrenormalized temporal/spatial Maxwell-residue
mismatch. There is no single Lorentzian kinetic metric with which to
canonically normalize `A_Q` and `Z_H`. Therefore this result does not establish
a physical transverse photon, photon pole, Ward identity, Weinberg angle, or
muon magnetic moment.

Promoted:

- the AE3.1 broken neutral connection Hessian;
- its unique structural `Q_em` null direction;
- the simultaneous connection-coordinate field/current rotation;
- the structural current `J3+JY`.

Open:

- one action-owned Lorentzian gauge domain with a common temporal/spatial
  residue for the null connection;
- canonical field normalization and Weinberg rotation;
- photon pole and Ward identity;
- the muon electromagnetic vertex and `F2(0)`.
