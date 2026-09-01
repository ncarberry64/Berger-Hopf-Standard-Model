# N12 forward BRST heat-tail cancellation audit

Status: `BRST_LONGITUDINAL_GHOST_CANCELLATION_DOES_NOT_CANCEL_PHYSICAL_HEAT_TAIL`.

The retained longitudinal gauge and complex-ghost blocks cancel mode by mode.
The remaining physical graded spatial trace is fixed by the common operator
ledger:

\[
 4\sum_{m\geq1}m^2e^{-am^2}
 +24\sum_{m\geq2}(m^2-1)e^{-am^2}
 -48\sum_{n\geq0}(n+1)(n+2)e^{-a(n+3/2)^2},
 \qquad a=s/R_4^2.
\]

Using

\[
 \sum_{m\geq1}m^2e^{-am^2}
 \sim\frac{\sqrt\pi}{4a^{3/2}},
\]

the leading degeneracy coefficient is
\(4+24-48=-20\). The graded heat trace therefore has the nonzero leading
behavior

\[
 -5\sqrt\pi\,a^{-3/2}.
\]

The half-integer Weyl shift and the transverse `-1` change lower-order terms,
not this coefficient. Direct sums at six decreasing values of `a` converge to
the exact scaled limit.

Thus Ward/BRST removes the longitudinal/ghost pair but does not cancel the
physical transverse-gauge/HS/Weyl heat tail. This does not prove that the
action-owned relative response diverges; it proves that grading alone cannot
serve as the missing angular or infrared relative-trace theorem.

The remaining native routes are an action-owned relative heat reference or
low-energy spectral-measure bound for the noncancelling physical sectors, or
evaluation of the actual finite maximal-endpoint operator. No sector is
removed and no reference, counterterm, or fitted cancellation is added.
