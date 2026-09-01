# N12 forward fixed-channel transfer reduction

Status: `FIXED_CHANNEL_TRANSFER_REDUCTION_DERIVED`.

In the current retained round forward source representation, every spatial
block has a fixed eigenspace along the history. For `x(tau)=log R4(tau)`,
Dirac and pair-vertex blocks scale as `exp(-x)`, scalar and de Rham Laplacians
scale as `exp(-2x)`, and contact matrices are independent of `x`. Direct
matrix checks through spatial level three and two distinct radii close below
`1e-12`.

For a unit-radius Dirac eigenvalue `lambda`, set

\[
 s_\lambda(\tau)=\pm\lambda e^{-x(\tau)},\qquad
 A_\lambda=\partial_\tau+s_\lambda.
\]

Writing `v=A_lambda u`, the squared-channel resolvent equation becomes the
two-dimensional transfer system

\[
 \frac d{d\tau}\binom uv=
 \begin{pmatrix}-s_\lambda&1\\-z&s_\lambda\end{pmatrix}
 \binom uv.
\]

For a scalar or de Rham unit-radius eigenvalue `c`, the corresponding system
is

\[
 \frac d{d\tau}\binom uv=
 \begin{pmatrix}0&1\\ce^{-2x(\tau)}-z&0\end{pmatrix}
 \binom uv.
\]

Both generators have zero trace. Their transfer matrices therefore preserve
the channel Wronskian. A terminal reset/Friedrichs admittance pulls back to
the birth by the exact Möbius action of the transfer matrix. Exact first and
mixed-second generator jets follow from the already-derived derivatives of
`exp(-x)` and `exp(-2x)`.

Thus Gate 7 does not require a generic matrix-valued coefficient history, a
moving spatial eigenbasis, or independent `D_tau` and `Delta_tau` oracles.
The base resolvent is a finite direct sum of fixed channel transfers; the
retained pair/contact incidence is a finite matrix between those fixed
channels. A pointwise representation of the whole radius history is also not
logically necessary if the resulting channel Weyl functions and their action
variations are enclosed directly.

The remaining dependency is to enclose those finite channel Weyl/transfer
maps for the maximal-forward `x(tau)` flow. Terminal return remains optional,
chord 3 remains unauthorized, Gate 7 remains active, and no momentum-space
label, source profile, endpoint, scale, or new physics has been introduced.
