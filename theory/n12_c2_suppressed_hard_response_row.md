# N12 C2 suppressed hard-response row

On the fixed positive descriptor fiber, the remaining signed denominator
term is

```text
s R,                 R = D lambda[W],
W = Qdot + E V_hard,
R = D3 S[W,Psi,Psi].
```

Here `E` embeds a raw reduced vector into the action norm, while `Qdot` is
the retained configuration leg already present in the exact C2 field.  The
descriptor `s` is fixed; no state derivative of `s` is introduced.

For the decisive action direction `i=86` and an arbitrary unit action
direction `h`, the complete product rule is

```text
R_ih = D5S[i,h,W,Psi,Psi]
     + D4S[i,W_h,Psi,Psi] + D4S[h,W_i,Psi,Psi]
     + 2 D4S[i,W,Psi_h,Psi] + 2 D4S[h,W,Psi_i,Psi]
     + D3S[W_ih,Psi,Psi]
     + 2 D3S[W_i,Psi_h,Psi] + 2 D3S[W_h,Psi_i,Psi]
     + 2 D3S[W,Psi_ih,Psi] + 2 D3S[W,Psi_i,Psi_h].
```

The whole hard direction obeys

```text
W_h  = DQdot[h] + E (V_hard)_h,
W_ih = E (V_hard)_ih.
```

No ill-conditioned kinetic, Dirac, or bordered block is inverted in this
certificate.  The stored first-response and first-eigenline matrices are
used with their signs intact.  Their motion over the exact node-1214 state
tube is bounded by the mean-value estimates

```text
||DV-DV_0|| <= sup ||D2V|| r,
||DP-DP_0|| <= sup ||D2P|| r.
```

The two second derivatives themselves enter only through contractions with
outward-rounded retained-action tensors.  Expanding the two simultaneous
first-matrix errors includes the bilinear cross term, so every one of the ten
product-rule terms is enclosed.

The resulting raw `R_ih` row bound is multiplied by an upward-rounded copy
of the owner-fixed positive descriptor.  It is then added to the already
certified dominant `D_86h(cb)` row before comparison with the unchanged
resolving ceiling.  This proves only the local signed-duration denominator
data.  It does not by itself supply the transposed segment-map action, the
complete upstream heat-minus-zeta covector, the maximal projected tail, a
Gate-7 closure, a new chord, or a physical-history selector.
