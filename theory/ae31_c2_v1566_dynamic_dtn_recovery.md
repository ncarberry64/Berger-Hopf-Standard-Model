# AE3.1 recovery of the v15.66 dynamic round-cap DtN

The v15.65--v15.66 construction is a genuine upstream asset. It fixes the
static order-one full-gauge DtN kernel, the parent coefficient, the
`5/3:1:1` gauge ray, and the LR group factors. It was not a local Maxwell
boundary term.

Restoring continuous Lorentzian frequency gives

```text
-d_rho(sin(rho) d_rho u)+m^2 u/sin(rho)-q^2 sin(rho)u=0,
q=omega R4.
```

At `q=0`, `u_m=tan(rho/2)^m` and `N_m(0)=m`. The envelope derivative is

```text
-dN_m/d(q^2)|0 = integral_0^(pi/2) sin(rho) u_m(rho)^2 d rho.
```

For the lowest coexact mode `m=2`,

```text
I_t=3-4 log(2),
Z_t/Z_s=2 I_t=6-8 log(2)=0.4548225555204377.
```

Thus the recovered round-cap completion also fails the single Lorentzian
Maxwell-residue test. It cannot be added to the current AE3 weighted trace:
both are bulk pushforwards using the same parent connection coefficient, so
addition would double count rather than derive a new contact field.

What survives is the static full-gauge kernel provenance and group ray. What
does not survive is a physical photon residue. The constructive historical
owner remains the v15.69 common parent regulator/subtraction, which was
formulated but not derived.

- `V1566_ROUND_CAP_CONTINUOUS_FREQUENCY_DTN_DERIVED = TRUE`
- `V1566_STATIC_FULL_GAUGE_KERNEL_PROVENANCE_REUSABLE = TRUE`
- `V1566_ROUND_CAP_ONE_LORENTZIAN_MAXWELL_RESIDUE_DERIVED = FALSE`
- `V1566_ADDITIVE_CURRENT_C2_BOUNDARY_CORRECTION_AUTHORIZED = FALSE`
