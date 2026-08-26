# N12 C2 signed first-coefficient vectors

At the certified C2 node 1214 center, write the desingularized duration
denominator in the retained convention as

\[
  \Delta=c\,b+sR,
  \qquad
  b=\langle\Psi,f\rangle,
  \qquad
  c=D^3S[\Psi,\Psi,\Psi].
\]

The complete second-variation calculation needs signed center values of the
three first coefficient covectors before rowwise mean-value radii are added.
They are assembled directly from the retained action, without a bordered
inverse:

\[
\begin{aligned}
  D\lambda[h] &= D^3S[h,\Psi,\Psi],\\
  Dc[h] &= D^4S[h,\Psi,\Psi,\Psi]
          +3D^3S[h,\Psi,z],\\
  Db[h] &= \langle\Psi,f_h\rangle
          -D^3S[h,\Psi,V_{\rm hard}],
\end{aligned}
\]

where

\[
  z=(\lambda-H)^{-1}_{\Psi^\perp}
    Q\,D^3S[\,\cdot\,,\Psi,\Psi]
\]

is the already certified hard adjoint.  The source differential is evaluated
by its exact retained-action identity

\[
  f_h=D^2S[\,\cdot\,,J\Psi]
      -D^3S[\,\cdot\,,\Psi,\dot Q]
      -D^2S[\Psi,D\dot Q[\,\cdot\,]].
\]

Every vector is assembled componentwise as a directed interval at the exact
stored center.  Signed summation occurs before a Euclidean norm is taken.  The
resulting norms are

\[
\begin{aligned}
  \|Db\|_2 &\le 6.284529154736189,\\
  \|Dc\|_2 &\le 2.2848329733902478\times10^{-6},\\
  \|D\lambda\|_2 &\le 6.165647281722456\times10^{-6}.
\end{aligned}
\]

These are center intervals only.  They do not by themselves certify the
node-tube variation.  Each row of the subsequent complete \(D^2\Delta\)
sweep must add and self-certify its separate mean-value radii for
\(Db_i\), \(Dc_i\), and \(D\lambda_i\).

The older binary64 moving-\(Dc\) and complex-step \(D\lambda\) vectors are
retained solely as cross-method diagnostics.  Their differences from the new
interval midpoints are recorded explicitly and are not used as uncertainty or
fitting freedom.

This theorem changes no action, selector, scale, gate, recurrence rule, or
frozen prediction.  Gate 7 remains open; Gate 8 remains locked; chord 3 remains
unauthorized.
