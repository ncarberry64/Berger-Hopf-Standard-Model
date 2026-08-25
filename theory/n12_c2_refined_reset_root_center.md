# N12 C2 refined reset-root proof center

The original terminal radii theorem certifies a unique root in the fixed
58-dimensional normal section, but its center residual leaves an enclosure of
order `6e-13`.  This is adequate for existence and reset semantics, yet too
coarse for efficient outgoing-flow recentering.

Let `A` be the already certified normal preconditioner, `F` the augmented
reset-plus-event map, and `Y=||A F(0)||`.  The proof-coordinate Newton point is
`a1=-A F(0)`.  It introduces no tangent displacement and hence selects no
member of the physical reset family.

The existing directed defect `Z0` and Hessian bound `Z2` give, without a new
action estimate,

`Y1 <= Z0 Y + Z2 Y^2/2`,

`Z01 <= Z0 + Z2 Y`.

The recentered radii polynomial

`p1(r)=Y1+Z01 r+Z2 r^2/2-r`

is negative at the derived radius `r=2 r_minus`, where `r_minus` is its small
root and is below `5e-15`.  The new ball and Newton displacement lie strictly inside the old
certified normal ball, so contraction uniqueness identifies the enclosed root
with the already certified terminal reset root.

The materialized state is a numerical proof center only.  The reset tangent
family, action, forward chronology, and all physical readouts are unchanged.
