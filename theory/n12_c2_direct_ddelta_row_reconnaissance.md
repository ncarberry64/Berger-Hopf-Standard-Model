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
