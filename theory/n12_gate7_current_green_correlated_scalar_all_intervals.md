# Correlated central Green scalar on all retained intervals

The normalized midpoint of each certified Green-image enclosure defines one
central longitudinal scalar direction.  Endpoint first and second variations
are derived in that direction and transported through the Hermite--Simpson
midpoint with its induced second incidence.  The intrinsic midpoint Hessian,
incidence response, total midpoint curvature, and local second residual are
then evaluated with 384-bit Arb on all 370 intervals.

The endpoint directions and their first and second rate variations are carried
between resumable stages as exact Arb decimal intervals.  Binary64 midpoint and
radius exports are retained for reporting only; they are not fed back into the
scientific transport.  This prevents persistence rounding from being
misinterpreted as 99 independent perturbation directions.

The resulting global norm bounds are

```text
maximum intrinsic midpoint curvature upper = 0.34991350135064914   (interval 8)
maximum midpoint incidence upper           = 0.0017528985596774965 (interval 9)
maximum total midpoint curvature upper     = 0.3491272055507006    (interval 8)
maximum local HS second residual upper     = 0.08778063910324282   (interval 8)
minimum selected-line gap lower            = 1.7343288725995338e-7
```

At interval 355 the intrinsic upper is `0.012206040568731967`, with
maximum exported component radius `3.7443732407358826e-19`; this sharply
encloses the independent interval-355 reconciliation.  The maximum certified
central-axis neighborhood error is `5.5312200553564e-6` at node 370.

This preserves the normalization/transport correlation that was destroyed by
the independent 74-component interval box.  The exact Green axis remains in a
certified neighborhood of the central direction at every node.  Those
neighborhood radii are persisted rather than discarded and must enter the
mixed Green/transverse and transverse-transverse remainder bounds.

Consequently this artifact closes the global central-scalar operand only.  It
does not yet close the axis-neighborhood remainder, frozen causal
preconditioning, longitudinal/transverse radii polynomial, or Gate 7.
