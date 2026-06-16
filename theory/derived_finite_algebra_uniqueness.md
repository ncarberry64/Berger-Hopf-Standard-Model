# Derived Finite Algebra Uniqueness

The primitive closure spectrum is

```text
D_primitive_low = {1,2,3}
```

Closure spaces:

```text
V_1 = C
V_2 = C^2
V_3 = C^3
```

Endomorphism blocks:

```text
End(V_1)=C
End(V_2)=M2(C)
End(V_3)=M3(C)
```

The minimal channel algebra is

```text
A_channel = C_ref direct_sum M3(C)_cyc
```

because the boundary has one reference/single channel and one primitive cyclic three-channel sector.

The minimal orientation algebra is

```text
A_orientation = M2(C)_active direct_sum C_+ direct_sum C_-
```

because the boundary has one active orientation-pair sector and two inactive resolved orientation signs.

The total boundary algebra is represented in this repo convention by

```text
A_boundary = A_channel tensor A_orientation
```

or an isomorphism-class equivalent.

Theorem statement: Under the conditionally derived primitive closure spectrum `{1,2,3}` and the requirement that boundary sectors act by finite endomorphisms on their closure spaces, the minimal semisimple complex boundary algebra containing the reference, active orientation, cyclic channel, and inactive resolved orientation sectors is unique modulo finite-dimensional *-algebra isomorphism.

Guardrail: this does not yet derive full gauge dynamics. It derives the finite boundary algebra skeleton.

Status: `PO_BH_9_FINITE_ALGEBRA_UNIQUENESS_DERIVED_CONDITIONAL`.
