# AE4 full finite-core factorized HS Calderon jet

## Result

The current-C2 product-Dirac block is returned to its first-order
factorization

```text
A=d/dtau+W,                 A^*A u=z u,
(u,v)'=[[-W,1],[-z,W]](u,v),       v=A u.
```

For the existing commuting LR/HS source,

```text
W_i(H)=W_i+H p_i,
```

the full 1222-segment Weyl graph is propagated backward with
arbitrary-precision Möbius/Riccati updates.  Differentiating each update and
composing its first and second jets gives

```text
M_birth(z),        D_H M_birth(z),        D_H^2 M_birth(z)
```

without a matrix inverse, dense generalized eigensolve, or subtraction of the
large squared-operator stiffness terms.

This closes the full finite-core HS Calderon-jet calculation on the real
negative spectral axis for both lowest product-Dirac chiralities.  At the
analytic-gap probe, the Dirichlet form-core endpoint gives approximately

```text
D_H M_birth = -1,
D_H^2 M_birth = 6.3426454163e-28,
```

for both chiral second jets.

## Tail-domain result

The zero nonnegative tail-load endpoint gives instead

```text
D_H M_birth = -0.8411684068,
D_H^2 M_birth = 6.9944607732e-28.
```

Thus the downstream domain materially changes the HS Calderon jet.  The
finite-core Dirichlet result cannot be relabeled as the physical maximal
history, and the zero-load endpoint cannot be selected by convenience.

## Claim boundary

The factorized full finite-core negative-axis jet is derived.  The actual N12
continuum-child terminal retarded load and its HS variations have not yet been
attached.  Consequently the maximal-history retarded HS block, integrated
AE4 `E1` Hessian, broken LR saddle, physical scalar residue and physical
encapsulation remain open.

The next calculation is to attach the action-owned N12 child response—or the
first physical domain exit—as the terminal retarded graph with its HS jets,
then integrate the resulting factorized negative-axis resolvent jet into the
AE4 Hessian and event-flux assembly.
