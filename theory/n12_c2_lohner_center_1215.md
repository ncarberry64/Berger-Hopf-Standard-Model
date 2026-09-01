# N12 C2 bordered and fixed-descriptor center at 1215

At the recentered segment-1215 predictor, the hard response and selected
coefficient are assembled through the bordered equation

`[D-lambda I,Psi;Psi^dagger,0](V_h,b_psi)=(rhs,0)`.

The 98 action-coordinate derivatives are computed by differentiating the
whole bordered system.  The exact fixed-descriptor field then combines
`Psi`, `c`, `b_psi`, `V_h`, `R`, and `Delta` before projection to
`ker D lambda`.  Its intrinsic identity `D lambda[F_s]=1` is checked.

The tensor `K^-1 DK` is projected to the physical tangent quotient and stored
for the second-variation fixed point.  These are exact-center objects; their
interval remainder is certified separately before any new segment is taken.
