# Correlated Green scalar reconciliation at interval 355

The componentwise midpoint enclosure failed first at interval 355 because the
small uncertainty in each normalized Green-axis component was propagated as 74
independent directions through an increasingly stiff first variation.  That
box discards the common normalization correlation.

The present calculation selects the normalized midpoint of each certified
Green-axis enclosure as one central scalar proof direction.  It then derives
the endpoint first and second variations, Hermite--Simpson midpoint direction,
second incidence, intrinsic midpoint curvature, incidence response, and local
second residual together at 384-bit Arb precision.  Every operand is finite at
interval 355.  In particular,

```text
||D2F_m[u_m,u_m]|| < 0.012206040568749032,
||DF_m w_m||       < 3.4730963028548466e-7,
||R_HS''||         < 0.0030515998355270598.
```

The exact interval Green axis is not silently replaced.  Its certified
distance from the selected central axis is recorded and must be charged to the
mixed/transverse remainder in the eventual two-radius proof.  Thus the result
reconciles the nonfinite interval-355 box as correlation loss without claiming
global longitudinal, causal, or physical closure.
