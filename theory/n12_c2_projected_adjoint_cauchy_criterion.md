# C2 projected maximal-adjoint Cauchy criterion

Let `T` index the nested finite form cores on the unique maximal C2 history and
let

`p_T(0)=integral_0^T U(t,0)^dagger q_rep(t) dt`,

where `q_rep=q_heat-q_zeta`.  The Gate-7 observable is not the whole ambient
adjoint.  On the retained reset quotient it is

`F_T=N_phys^dagger(B_reset^dagger p_T(0)+q_direct,T)`.

Because the physical reset quotient is finite dimensional, `F_T` has a unique
maximal-core limit if and only if it is Cauchy in the quotient dual.  Equivalently,
for every `epsilon>0` there is a core time `T0` such that for all `S,T>T0`,

`||N_phys^dagger[B_reset^dagger integral_S^T U(t,0)^dagger q_rep(t)dt
  +(q_direct,T-q_direct,S)]|| < epsilon`.

This is the exact weakest convergence requirement for the projected Gate-7
force.  The previously derived absolute estimate

`integral ||U(t,0)|| ||q_rep(t)|| dt < infinity`

together with convergence of `q_direct,T` is sufficient, but is not necessary:
ambient divergent loads may lie entirely in constraint-normal, exact-time, or
other directions annihilated by the retained physical pullback.  Any such
cancellation must be proved from the BHSM projection and graded action; it may
not be inserted as a selector.

The C2 enclosure-class theorem fixes the class, history domain, channel set,
and endpoint dichotomy.  It does not fix the continuous propagator or the
graded cotangent.  The 1,222-segment parametric-family certificate and its
complete interval transposed-duration action cover therefore bound a finite prefix
only.  Fixed-channel source-Dini and compact-source high-energy smoothing close
two spectral slots, but neither is a temporal estimate for the product above,
and the infinite-route angular contraction and direct zeta tail remain open.

On a certified finite later-event or canonical-stop stratum, the retained
finite-endpoint operator/adjoint theorem supplies the criterion automatically.
On an infinite Friedrichs route, the next action theorem may prove the quotient
Cauchy tail directly; it need not prove the stronger ambient absolute norm
bound.  Until one of those alternatives is certified, the numerical C2 force,
same-action saddle, and physical Hessian remain open.
