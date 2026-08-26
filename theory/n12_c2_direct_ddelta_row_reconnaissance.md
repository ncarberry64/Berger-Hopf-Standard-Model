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
