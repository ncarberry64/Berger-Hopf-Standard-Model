# Fully reduced signed C2 row certificate

The decisive component transport inequality at stored proof node 1214 needs
only

```text
sup ||row_86(D2 Delta)||_2 < 14.622464650642785.
```

For the selected-line product `cb`, self-adjointness of the hard resolvent
removes all six nested hard adjoints.  With `P_h=Psi_h`, the two exact rows are

```text
c_ih = D5S[i,h,Psi^3]
     + 3 D4S[h,Psi_i,Psi^2]
     + 3 D4S[i,P_h,Psi^2]
     + 3 D4S[i,h,Psi,z]
     + 3 (D3S[i,P_h,z] - lambda_i <P_h,z>)
     + 3 D3S[h,z,Psi_i]
     - 3 <z,Psi_i> D3S[h,Psi,Psi]
     - 3 c <P_h,Psi_i>
     + 6 D3S[P_h,Psi_i,Psi],

b_ih = -b <P_h,Psi_i>
       - D4S[i,h,Psi,V_hard]
       - D3S[i,P_h,V_hard] + lambda_i <P_h,V_hard>
       - D3S[h,V_hard,Psi_i]
       + <V_hard,Psi_i> D3S[h,Psi,Psi]
       + <Psi_i,f_h> + <P_h,f_i> + <Psi,f_ih>.
```

The source is not differentiated as an external oracle.  In raw reduced
coordinates it is exactly

```text
f = J grad(S_action) - H_RQ u,
```

where `J` identifies the 37 configuration-gradient slots with the velocity
part of the reduced block and `u` is the retained velocity configuration.
Consequently, because decisive action coordinate 86 has no velocity part,

```text
<v,f_h>  = D2S[h,Jv] - D3S[h,v,u] - D2S[v,h_u],
<v,f_i>  = D2S[i,Jv] - D3S[i,v,u],
<v,f_ih> = D3S[i,h,Jv] - D4S[i,h,v,u] - D3S[i,v,h_u].
```

These are local retained-action jets; no external source value or boundary
condition is introduced.

## Interval representation

The certificate evaluates the retained 96-point action expression with a
directed binary64 interval jet.  Every primitive product is rounded outward
before it enters a sum.  Distinct matrix direction legs retain distinct tensor
axes, so signed rows are assembled before a norm is taken.

The state ball is the already certified node-1214 action-coordinate tube.  The
direction balls are deliberately rounded above their local majorants:

```text
||Psi-Psi_0||             <= 6e-9,
||D Psi-D Psi_0||_op      <= 8,
||Psi_i-Psi_i0||          <= 1e-2,
||z-z_0||                 <= 2e-3,
||V_hard-V_hard0||        <= 40.
```

The first two follow from the certified selected-line second-variation
coefficient.  The hard-response radius follows from its certified first and
second variations.  The fixed-complement composed majorants for the decisive
selected column and `z` are rounded upward to derivative bound `2e7`; over the
state tube this is about `1.103e-3`, strictly inside both adopted balls.

The signed row is first evaluated with the center first-Jacobi matrix.  Motion
of that entire matrix is then represented by one arbitrary reduced matrix leg
of operator radius 8 and added as an absolute correction.  This preserves all
signed cancellation not involving the unknown matrix error while remaining
valid for every matrix in its operator ball.

The certificate closes only the dominant `bc` row.  The `s`-suppressed hard
response contribution to `D2 Delta` is a separate remaining row and is not
promoted by smallness of `s` alone.  Gate 7 therefore remains open until that
row is outward-rounded below the remaining budget.  Gate 8 remains locked and
no selector, recurrence, scale, fitted value, stopping locus, gate, or chord is
introduced.
