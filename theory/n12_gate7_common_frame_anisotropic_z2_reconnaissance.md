# Gate-7 anisotropic common-frame Z2 reconnaissance

The full 73-direction constraint-tangent `D2f` norm is not the correct first
nonlinear test.  The fixed-reset shadow equation is driven by the signed
minus-defect Green image, and its correction occupies a narrow anisotropic
cone.  The retained common-scale direction stays physical; no multiplier or
hybrid time direction is removed by hand.

At each of the 48 retained macro seams this reconnaissance calibrates the JAX
action value, gradient, and Hessian to the authoritative exact action center,
replays the projected exact Jacobian, forms the physical constraint tangent,
removes only the local history-flow direction, and evaluates

`D2f[.,e_hat]` and `D2f[e_hat,e_hat]`,

where `e_hat` is the signed Green correction direction.  These are the
correct center quantities for an anisotropic radii enclosure.  The complete
tensor Frobenius norm is retained as a diagnostic comparison, not used as the
`Z2` coefficient.

The result remains reconnaissance because the JAX higher derivatives and
between-seam interpolation have not yet received an outward retained-action
remainder.  It cannot certify `Z2`, the exact history, or Gate 7 by itself.
