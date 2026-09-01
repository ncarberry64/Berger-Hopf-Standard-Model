# Direct signed-denominator row theorem and reconnaissance

On the fixed signed-descriptor fiber, let the bordered complement solve return
the selected-line coefficient `b`, selected vector `Psi`, and hard response
`V_hard`.  Define the signed numerator

```text
N = b Psi + s V_hard.
```

Linearity of the selected-eigenvalue differential gives the exact identity

```text
Delta = c b + s R = D lambda[N],
c = D lambda[Psi],
R = D lambda[V_hard].
```

The selected-line coefficient itself is inverse-free.  If

```text
(H-lambda) V_hard + b Psi = f,   <Psi,V_hard>=0,
```

then multiplication by `Psi^dagger` gives

```text
b = <Psi,f>.
```

The hard response is evaluated on the spectral complement,

```text
V_hard = sum_(a != selected) Psi_a <Psi_a,f>/(lambda_a-lambda),
```

so a binary eigensystem residual multiplied by the large hard vector cannot
contaminate `b`.  This is an algebraic identity, not an extra inverse or a new
physical choice.

This identity is evaluated before any absolute value or operator norm.  It
therefore preserves the cancellation between the selected-line and hard
complement contributions that is lost in the earlier product majorant.

To exclude zero from the transported `D Delta` ball it is unnecessary to
enclose the complete Hessian.  If `i_*` is any action coordinate for which the
reference-center component is nonzero, then

```text
|D_i* Delta(Y_exact)|
>= |D_i* Delta(Y_1214)| - r_seed
   - sup_t ||row_i*(D2 Delta)(Y(t))||_2 ||Y_exact-Y_1214||_2.
```

Thus one rigorously enclosed Hessian row below

```text
(|D_i* Delta(Y_1214)| - r_seed) / r_tube
```

is sufficient.  No full `98 x 98` Hessian norm is required.

The accompanying two-mesh computation is explicitly reconnaissance.  It
evaluates `Delta=D lambda[N]` directly from the retained action Hessian,
selected eigenspace, and bordered solve, and then measures the decisive row by
centered mixed differences in action coordinates.  Agreement of two meshes is
a conditioning diagnostic, not an interval remainder theorem.  Promotion to a
certificate requires a cancellation-preserving interval/analytic remainder
bound for this one row on the node-1214 exact-state tube.

This reduction introduces no selector, recurrence, scale, fitted value,
physical stopping locus, gate, or chord.

## Hard-adjoint removal of the mixed second eigenline

Let `Q=I-Psi Psi^dagger` and let

```text
S = (lambda-H)_hard^{-1} Q.
```

For two state directions `u,h`, differentiated eigenline normalization and
the twice-differentiated eigenvalue equation give

```text
Psi_uh = S Q G_uh - <Psi_u,Psi_h> Psi,
G_uh = H_uh Psi + (H_u-lambda_u)Psi_h
                    + (H_h-lambda_h)Psi_u.
```

Define the raw reduced covector `g` by

```text
<g,v> = D3 S_action[v,Psi,Psi]
```

and solve only the hard adjoint

```text
z = S Q g.
```

Self-adjointness of the hard resolvent then gives the exact contraction

```text
D3 S_action[Psi_uh,Psi,Psi]
  = <z,G_uh> - c <Psi_u,Psi_h>,
c = <g,Psi>.
```

Consequently the large vector `Psi_uh` never needs to be enclosed.  The
decisive row requires one local mixed source paired with one hard adjoint.
At the reference center the structured adjoint is orders of magnitude below
the gap-only estimate.  That center replay validates the algebra and exposes
the right proof variable; it does not replace the still-required outward-
rounded tube enclosure.

## Complete local-adjoint assembly of the `bc` row

The same self-adjoint hard-resolvent identity removes every moving
`Psi_h` occurrence, not only `Psi_ih`.  Write `A_u=D_u H`, fix the decisive
direction `i`, and define

```text
Psi_i = S Q A_i Psi,
k_i(v) = D4 S_action[i,v,Psi,Psi],
w3  = S Q k_i,
w5  = S Q A_(Psi_i) Psi,
wI  = S Q (A_i-lambda_i) z,
wN  = S Psi_i.
```

Then the complete cubic Hessian row is

```text
c_ih = D5S[i,h,Psi^3]
     + 3 D4S[h,Psi_i,Psi^2]
     + 3 D3S[h,Psi,w3]
     + 3 D4S[i,h,Psi,z]
     + 3 D3S[h,Psi,wI]
     + 3 D3S[h,z,Psi_i]
     - 3 <z,Psi_i> D3S[h,Psi,Psi]
     - 3 c D3S[h,Psi,wN]
     + 6 D3S[h,Psi,w5].
```

For the inverse-free coefficient, use

```text
(H-lambda)V_hard + b Psi = f,
wVI = S Q (A_i-lambda_i)V_hard,
wfi = S Q f_i.
```

Differentiating `b=<Psi,f>` and eliminating `Psi_h` and `Psi_ih` gives

```text
b_ih = -b D3S[h,Psi,wN]
       -D4S[i,h,Psi,V_hard]
       -D3S[h,Psi,wVI]
       -D3S[h,V_hard,Psi_i]
       +<V_hard,Psi_i>D3S[h,Psi,Psi]
       +<Psi_i,f_h>
       +D3S[h,Psi,wfi]
       +<Psi,f_ih>.
```

The first rows have the corresponding local forms

```text
c_h = D4S[h,Psi^3] + 3 D3S[h,Psi,z],
b_h = <Psi,f_h> - D3S[h,Psi,V_hard].
```

Consequently

```text
D_ih(cb) = b c_ih + b_i c_h + c_i b_h + c b_ih
```

contains only finite local action/source jets and a finite list of hard
adjoints.  Neither the full moving first-eigenline matrix nor any mixed
second-eigenline vector is an input to the interval proof.  This is an exact
same-action recombination; it adds no inverse, selector, or physical datum.

## Elimination of every nested hard adjoint

The finite list of nested adjoints is itself unnecessary.  Self-adjointness
of the same hard resolvent gives, for every hard source `r`,

```text
D3 S_action[h,Psi,S Q r] = <Psi_h,r>,
Psi_h = S Q A_h Psi.
```

Applying this identity to `w3`, `wI`, `wN`, `w5`, `wVI`, and `wfi` reduces
the two second rows to

```text
c_ih = D5S[i,h,Psi^3]
     + 3 D4S[h,Psi_i,Psi^2]
     + 3 D4S[i,Psi_h,Psi^2]
     + 3 D4S[i,h,Psi,z]
     + 3 (D3S[i,Psi_h,z] - lambda_i <Psi_h,z>)
     + 3 D3S[h,z,Psi_i]
     - 3 <z,Psi_i> D3S[h,Psi,Psi]
     - 3 c <Psi_h,Psi_i>
     + 6 D3S[Psi_h,Psi_i,Psi],

b_ih = -b <Psi_h,Psi_i>
       - D4S[i,h,Psi,V_hard]
       - D3S[i,Psi_h,V_hard]
       + lambda_i <Psi_h,V_hard>
       - D3S[h,V_hard,Psi_i]
       + <V_hard,Psi_i> D3S[h,Psi,Psi]
       + <Psi_i,f_h> + <Psi_h,f_i> + <Psi,f_ih>.
```

For example,

```text
D3S[h,Psi,w5]  = D3S[Psi_h,Psi_i,Psi],
D3S[h,Psi,wVI] = D3S[i,Psi_h,V_hard]
                  - lambda_i <Psi_h,V_hard>.
```

Thus the cancellation-preserving interval representation needs only the
selected line, its existing first Jacobi matrix, the fixed decisive column
`Psi_i`, the single small adjoint `z`, the hard response, and local action and
source jets.  No tube for any of `w3,w5,wI,wN,wVI,wfi` is required.  The
fully reduced center replay has the same `cb` row norm as the nine/eight-term
representation, approximately `1.68954153e-5`; this remains a binary64 center
replay rather than the required outward-rounded tube enclosure.
