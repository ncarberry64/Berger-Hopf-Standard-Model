# AE3.1 current-C2 quark parent third-variation evaluation

The two mixed variations named by the quark-normalization theorem have now
been evaluated against the action that is actually active.

`BHSM-AE-3.1.0` is

```text
S_AE3.1 = S_AE3.0 + S_4,lH^BHSM.
```

The added intrinsic-M4 term contains the charged-lepton channel
`bar(L_L) H e_R`, but explicitly adds no up/down Yukawa terms.  The AE3.0
predecessor likewise contains no intrinsic quark LR--Higgs trilinear.
Therefore field incidence gives the exact active-action result

```text
P_u D_bar(Q_L) D_H_tilde D_u_R S_AE3.1 P_u = 0,
P_d D_bar(Q_L) D_H       D_d_R S_AE3.1 P_d = 0.
```

This is a theorem about an absent action term.  It is not a claim that a
physical quark is massless.

## Why the maximal EFT registry does not close the gap

The repository's maximal `S4eff` registry does contain

```text
-bar(Q_L) Y_u H_tilde u_R - bar(Q_L) Y_d H d_R + h.c.
```

and no other registered term contains the three fields in either requested
channel.  Its formal variations are consequently

```text
-sqrt(-h) P_u Y_u P_u,
-sqrt(-h) P_d Y_d P_d,
```

up to the canonical delta and gauge-index contractions.  But the same action
ledger types `Y_u,Y_d` as `INDEPENDENT_THEORY_INPUT`.  Differentiation
therefore recovers the inserted matrices; it does not derive them.  Projection
or a representation trace cannot remove the two sector scalars because

```text
P_f (c_f T_f) P_f = c_f (P_f T_f P_f).
```

## Why the retained current-C2 HS vertex is not the answer

The reduced product-Dirac block has a genuine nonzero third tensor

```text
D_HS D_bar(c) D_c S_reduced = V tensor I3_family.
```

It is an auxiliary-HS derivative, not an intrinsic `H` or `H_tilde`
derivative.  Its family factor is central, and the current action has neither
a dynamical HS kinetic residue nor a selected broken-LR direction.  It cannot
be canonically normalized into either quark Yukawa operator, nor can it attach
the already-reused noncentral `T_u,T_d` operators without an additional
derived pushforward.

The historical event-shell, proper-cycle, quantum-superdeterminant, and
Einstein--Cartan results remain reusable upstream results, but none is the
current AE3.1 intrinsic-quark owner.  Respectively: the v15.73 actual crossing
was not established; v15.91 produced a family-central periodic-cycle residue
with an electric/magnetic mismatch; v15.96 did not solve its interacting
source Hessian or quantum event saddle; and the AE3.2 EC stationary action is
globally divergent on the retained zero mode.

## Exact next owner

The missing object is now narrower than “find two constants.”  It is one
current-C2 functional

```text
Gamma_qH_current_C2[bar(Q_L),u_R,d_R,H]
```

on the AE3.1 domain whose two third derivatives produce the up/down vertices
with their field residues, trace normalization, intrinsic `H/H_tilde`
identification, and the pushforward of the existing `T_u,T_d` family
operators.  A proved mapping from the current HS vertex is admissible only if
it also derives the HS-to-intrinsic-Higgs identification, dynamical residue,
and sector pushforward.  No quark mass or independent `c_u,c_d` may select it.

Promoted:

- `CURRENT_AE31_UP_DOWN_INTRINSIC_HIGGS_THIRD_VARIATIONS_EVALUATED = TRUE`;
- both active-action variations vanish exactly by field incidence;
- the maximal EFT variations are proved to be input-recovery identities.

Not promoted:

- a nonzero current-AE3.1 quark Yukawa vertex;
- `c_u` or `c_d`;
- physical quark poles or CKM mixing.

`FULL_BHSM_COMPLETE = FALSE`.
