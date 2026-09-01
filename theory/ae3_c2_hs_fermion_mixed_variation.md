# AE3 current-C2 reduced HS/fermion mixed variation

The current 1,222-segment squared product-Dirac piece has the exact expansion

```text
K(H)=K0+H V+H^2 Q/2.
```

For the reduced bilinear `S=bar(c) K(H) c`, direct differentiation gives

```text
D_H S=bar(c) V c,
D_H^2 S=bar(c) Q c,
D_H D_bar(c) S=V c,
D_H D_bar(c) D_c S=V.
```

The attached current-C2 background has frozen family/mode fibers but no
classical Sobolev fermion coefficient coordinate. On its supported symmetric
slice `c*=0`, the HS source, pure-HS curvature from this reduced piece, and
HS--fermion mixed Hessian therefore vanish exactly. The interaction has not
disappeared: its first background-independent nonzero tensor is the retained
third LR/HS variation `V`, followed by the contact tensor `Q`. Both are
nonzero on both current-C2 chiral pencils.

This closes an algebraic ambiguity. A BHSM family/mode state is valid initial
data in the internal tensor factor; it is not by itself a classical spatial
fermion profile and cannot be substituted for `c*`.

No retained dynamical HS kernel can currently be attached to this result.
The v16.02 and v16.05 kernels live on the historical closed proper cycle and
select no physical four-channel direction. The v15.72 branch has an
unevaluated critical spectral value and relies on the now-failed gauge
residue. The strongest coefficient-free extension candidate is the v15.75
first-order Einstein--Cartan contorsion Schur complement, but that completion
was not part of `BHSM-AE-3.0.0` and has not been evaluated on current C2.

The finite action decision is therefore to derive that first-order completion
as a new action version, derive another parent-owned current-C2 HS kernel, or
retain AE3 without a dynamical broken-LR sector. No option is selected here;
no condensate, mass, spectrum, or Yukawa normalization is inserted.
