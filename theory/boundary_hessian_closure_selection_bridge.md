# Boundary Hessian Closure Selection Bridge

Bridge:

```text
P_ref     -> d=1 -> End(C^1)=C
P_orient  -> d=2 -> End(C^2)=M2(C)
P_cyclic  -> d=3 -> End(C^3)=M3(C)
P_excess  -> d>=4 -> higher/composite/unsupported low-energy closures
```

Recover:

```text
A_channel = C_ell direct_sum M3(C)_C
A_weak = M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}
```

This bridge supports the finite algebra source diagnostically, but does not uniquely derive it.
