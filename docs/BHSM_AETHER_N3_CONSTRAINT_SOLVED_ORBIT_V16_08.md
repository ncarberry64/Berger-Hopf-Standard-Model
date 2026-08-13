# BHSM independent (N=3) constrained orbit v16.08

This calculation closes the first dependency after rejecting the static event
embedding: it constructs an executable higher-order orbit from the canonical
reset itself.

At order (N=3),

\[
 \dim q=1+3N=10,\qquad \dim m=2N=6,
\]

and all six lapse/shift equations plus the Hamiltonian equation are imposed.
The round reset geometry has zero new harmonic amplitudes, while its rates and
multipliers are selected by the minimum (H^5\times H^6) correction satisfying
those seven constraints.  No (N=2) event state enters.

For (z=(\dot q,m)), the exact order-two jet supplies

\[
 D_{zz}^2L_N
 \begin{pmatrix}\ddot q\\ \dot m\end{pmatrix}
 =
 \begin{pmatrix}
 D_qL_N-D_{\dot q q}^2L_N\dot q\\
 -D_{mq}^2L_N\dot q
 \end{pmatrix}.
\]

Each Runge--Kutta step is returned to the seven-constraint surface by the
Sobolev minimum-norm projection.  The Euler--Dirac event is detected from the
generalized pencil

\[
 D_{zz}^2L_N u=\lambda\,G_su,
\]

where (G_s) is the (H^5\times H^6) product metric.  All eigenbranches are
matched between adjacent steps by maximum total Sobolev overlap; the event is
the first matched branch crossing zero.  The next calculation runs this
independent orbit to that event and evaluates the rank-16 spin-stress and gauge
DtN residues on the identical layer.

The v16.09 continuation adds the missing pointwise continuum-domain check.
It finds that the independently solved orbit exits the eta-Legendre domain at
approximately (t=0.04410714), before any Euler--Dirac zero. Consequently the
post-exit soft layer described above is not promoted to a physical event.
