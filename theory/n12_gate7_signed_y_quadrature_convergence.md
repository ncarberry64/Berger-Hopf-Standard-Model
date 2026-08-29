# Gate-7 signed-`Y` quadrature convergence audit

Status: `CURRENT_GAUSS12_RECENTER_NOT_PROMOTABLE; SIGNED_Y_QUADRATURE_OPEN`.

The selected quarter-step carrier, its 3,009-cell recentered spectral chain,
the 24,072-cell response/reverse-first-variation chain, and the causal Taylor
`Z2` calculation remain valid certificates for the center that they actually
represent.  They do not by themselves prove that this represented center is
within the final history-shadowing halo.

The literal history theorem requires

`Y = ||A(-d)||_P`

in the same common frame.  The source must therefore be integrated as a
signed vector before a norm is taken.  Replaying the same 16-substep Green
operator with Gauss orders 8, 12, 16, and 20 gives maximum successive signed
correction-profile increments

- `3.0654816130078717e-7` for 8 to 12;
- `2.5627317334557724e-7` for 12 to 16;
- `3.4142391285067826e-7` for 16 to 20.

The selected nonlinear action halo is only
`1.243972269022099e-12`.  Thus the 16-to-20 increment alone consumes
`274462.63984572224` halo radii.  It grows rather than decreases, and the
largest 30 local source increments account for only `0.20591605037933117` of
the total local increment.  Ordinary owner-only Gauss refinement is therefore
not available.

The independently refined propagator behaves differently: the summed local
4-to-8, 8-to-16, and 16-to-32 defects decrease at second order, with finest
observed order `2.0000016810116805`.  Its factor-four tail estimate is
`5.709338390227293e-5`, but this remains numerical rather than interval
authority.  Even replacing the stored Gauss-12/one-substep correction by the
same Gauss-12 source with the 16-substep propagator moves the represented
center by `4.100804152831088e-11`, or `32.96539846547204` current halo radii.

Consequently the current Gauss-12 recenter cannot be promoted as the exact
history and the finite radii polynomial must not be assembled from it.  This
does not identify a physical event, branch collision, or action failure.  It
is `NUMERICAL_CONDITIONING + PROOF_CHART_LIMIT` in the signed source and
propagator realization.

The minimum valid next step is to converge the signed Green source with a
high-precision or adaptive correlation-preserving quadrature below the
`1.244e-12` halo, freeze that new recenter, and then rebuild only the
center-dependent recentered cone/response chain.  Gate 7 remains active and
`FULL_BHSM_COMPLETE = FALSE`.
