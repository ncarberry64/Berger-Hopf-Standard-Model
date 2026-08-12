# BHSM v15.49 — post-cut lapse/shift Dirac reduction

The physical cap flow uses

\[
 N=e^{n_1\cos4\chi+n_2\cos8\chi},\qquad
 \beta^\chi=\sin4\chi\,(b_0+b_1\cos4\chi),
\]

so the shift has zero normal flux at the pole and the physical
\(S^3\times S^3\) boundary. The normal rates are

\[
 H_C=N^{-1}(\dot{\log C}-\beta(\log C)'-\beta'),\quad
 H_A=N^{-1}(\dot{\log A}-\beta(\log A)'),\quad
 H_B=N^{-1}(\dot{\log B}-\beta(\log B)'),
\]

and \(D_\perp f=N^{-1}(\dot f-\beta f')\). Varying the two
lapse-shape and two shift coefficients gives four projected local
constraints; the constant-lapse variation is the canonical-energy
constraint.

Because the reconstructed map is monotone, radial diffeomorphisms admit the
global coordinate gauge

\[
 f=\chi,\qquad q_1=q_2=\dot q_1=\dot q_2=0.
\]

The closest constrained projection on this quotient gives

\[
 (n_1,n_2,b_0,b_1)
 =(-1.4473387,-0.1399055,0.0397674,-0.4350709),
\]

\[
 \max_A|\mathcal C_A|=4.4\times10^{-11},\qquad
 \max_A|\mathcal C_A|_{\rm independent}=5.04\times10^{-4},
 \qquad \dot x=-0.97887<0.
\]

The differentiated Euler--Dirac equations are

\[
 L_{zz}\binom{\ddot q}{\dot m}
 =\binom{L_q-L_{\dot q q}\dot q}{-L_{mq}\dot q},
 \qquad z=(\dot q,m).
\]

After removing the two eta-coordinate gauge modes, \(L_{zz}\) is an
\(11\times11\) full-rank matrix. At the initial slice its condition number is
\(6.77\times10^3\).

A five-step controlled orbit reaches \(t=0.0025\), \(x=-0.00209019\), with
independent-grid constraint residual \(4.27\times10^{-4}\). Extended
continuation has no turning point. Before the first chart fold it reaches

\[
 t=0.24,\qquad x=-0.161681,
 \qquad \min N=0.894,
 \qquad \min(1+X_\eta^3)=2.519.
\]

The Dirac multiplier condition number then rises to \(2.8\times10^6\), and
the scalar velocity projection fails near \(t=0.2655\). A nearest
seven-velocity projection crosses this fold, but its normalized displacement
is order one, so it does not prove continuation of the same numerical branch.
The last regular post-fold state is

\[
 t=0.3095,\quad x=-0.312613,\quad \dot x=-6.19876,
\]

\[
 \min N=0.37335,\quad \max N=4.155,
 \quad \min(1+X_\eta^3)=2.12563,
 \quad \max|\mathcal C_A|_{\rm independent}=6.28\times10^{-4}.
\]

The next Runge--Kutta stage reaches a second eta Legendre singularity. Thus
the Einstein--eta--response--FR block has no relative-periodic return before
the next invariant event. This is a controlled finite-chart branch result,
not a foundational no-go theorem: the complete particle still includes its
action-owned gauge and fermion attachment.
