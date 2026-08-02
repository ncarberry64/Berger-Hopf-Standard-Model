# BHSM v11.2 Linear and Quadratic Connection Couplings

For a real scalar and `D=nabla-wA_D`,

```text
|D phi|^2 = |nabla phi|^2 - 2w A_D.phi nabla phi
             + w^2 A_D^2 phi^2.
```

The linear term integrates to a bulk `div(A_D)phi^2` term plus
`-w n.A_D phi^2` on the boundary. It cannot be retained without the quadratic
term. Complex Hermitian and contragredient-dual pairings give different
currents, and the parent action declares neither as a `G_D` pairing.

A first-order Dirac operator generates a linear connection term but no
primitive scalar-like seagull; quadratic terms may arise only after squaring
or reduction. The tested non-Abelian gauge connection has support weight zero.
All coefficients return to the parent kinetic terms when `A_D=0`.

