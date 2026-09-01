# AE3 current-C2 coexact hypercharge source jet

## Same-domain transfer

The historical rank-16 source calculation derives the spatial coexact
`U(1)_Y` insertion in the product-Dirac operator. Its old dense closed-cycle
response value is not promoted to the current child. Only the local operator
algebra is reused.

At homogeneous spinor level `n=0`, the round Berger block on every current C2
element is exactly

```text
D_0,e = (3/2) R4,e^-1 I2.
```

The unit spatial coexact generator is

```text
G = sigma_z, tr(G)=0, G^2=I2.
```

For chirality `s=+/-1` and a real source profile `p_e`, define the source
family of first-order factors

```text
W_s,e(epsilon) = s [D_0,e + epsilon p_e G].
```

On the nonuniform C2 element, the retained form is

```text
K_e(epsilon)
  = S/h_e tensor I2
  + M_e tensor W_s,e(epsilon)^2
  + C tensor W_s,e(epsilon),

M_e=h_e A/6.
```

Therefore

```text
V_e = dK_e/d epsilon |0
    = M_e tensor (W_s,e dW_s,e + dW_s,e W_s,e)
      + C tensor dW_s,e,

Q_e = d2K_e/d epsilon2 |0
    = 2 M_e tensor dW_s,e^2.
```

The materializer uses `p_e=1`, retains the C2 birth node, and eliminates the
last node only as the existing Friedrichs form-core truncation. For both
chiralities, its background diagonal and off-diagonal blocks equal the exact
`I2` lift of every stored 1,222-segment product-Dirac coefficient, with zero
stored relative residual. No inverse is formed and no proof center is selected
as a physical history.

## Rank-16 attachment

The existing representation trace supplies

```text
sum over three families and rank-16 chiral states of Y^2 = 10,
family factor = I3.
```

These are reused without a new gauge coupling or scale. The result is a
current-domain fermionic first and second derivative with respect to a unit
spatial coexact hypercharge source.

This advances the full-field, muon, and collision puzzle sections, but it is
not yet an electromagnetic observable. The missing joins are:

- a dynamical current-C2 `U(1)_Y` gauge/ghost kinetic block;
- the corresponding `SU(2)_L` block;
- an action-selected broken electroweak saddle and neutral mixing map;
- a simple physical muon pole, Ward identity, renormalization scheme, and
  complete loop amplitude;
- the maximal-history exterior vertex or a genuine later stop.

Until those joins exist, calling this source the photon or evaluating
`F2(0)` would overstate the result.

`CURRENT_C2_COEXACT_U1Y_SOURCE_JET_DERIVED=TRUE`,
`CURRENT_C2_PHYSICAL_PHOTON_VERTEX_DERIVED=FALSE`,
`MUON_MAGNETIC_MOMENT_DERIVED=FALSE`, and `FULL_BHSM_COMPLETE=FALSE`.

## Reproduction

```bash
python scripts/materialize_ae3_c2_coexact_hypercharge.py
python -m pytest tests/test_ae3_c2_coexact_hypercharge.py -q
```

The machine-readable result is
`artifacts/action_extension/BHSM_AE3_C2_COEXACT_HYPERCHARGE_SOURCE_JET.json`.
