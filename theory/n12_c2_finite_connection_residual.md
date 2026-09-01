# C2 finite later-event/canonical-stop connection residual

Hold the certified event member of the AE2 reset fixed.  The retained full
reset has 57 rows: 25 event constraints, one ordered-event row, four interface
trace rows, 25 child constraints, and two momentum rows.  The first 26 rows
belong to the fixed event.  The remaining 31 rows define the child reset fiber
inside the 98-dimensional child state, hence its raw tangent dimension is
`98-31=67`.

Let `Y_0` be a child reset state, let `Y_j` be nodes on normalized forward time
`s in [0,1]`, and parameterize physical duration by `T=exp(theta)>0`.  The
inverse-free trapezoidal connection residual is

`C_reset,child(Y_0)=0`,

`Y_0,path-Y_0=0`,

`Y_{j+1}-Y_j-(T Delta s/2)(V_AE2(Y_j)+V_AE2(Y_{j+1}))=0`,

and either the first transverse retained event equation
`e_ord(Y_N)=0` or one already-retained canonical-stop graph.  Lapse, spatial
metric, Legendre, inertia, trace/gauge, Euler--Dirac invertibility, and selected
eigenline simplicity remain strict inequalities at every path node.  They are
audited as margins and are not converted into fitted residual penalties.

After eliminating the path equations, the raw reset fiber contributes 67
parameters, duration contributes one, and the endpoint equation removes one.
The one exact whole-history time orbit is then quotiented intrinsically,
leaving the retained 66-dimensional physical endpoint stratum.  Common scale
is not removed.

The repository now contains an executable residual assembler with this exact
partition and a reproducible algebraic witness.  Every production callback is
type-locked to a BHSM object.  The actual fixed-event child reset rows exist,
and the 98-segment C2 prefix supplies certified local flow boxes and margins.
However, no repository object currently supplies a certified continuous
Euler--Dirac flow callback beyond that prefix together with a later retained
event or canonical-stop graph hit.  The prefix ends on branch 24 with positive
signed eigenvalue and is not a physical endpoint.

Thus the finite connection problem is now executable as a residual once the
actual continuation and endpoint callback are supplied, but no later endpoint
solution or stratum is claimed.  No recurrence, periodic boundary condition,
validation cutoff, QFT boundary condition, selector, scale, or chord is added.
