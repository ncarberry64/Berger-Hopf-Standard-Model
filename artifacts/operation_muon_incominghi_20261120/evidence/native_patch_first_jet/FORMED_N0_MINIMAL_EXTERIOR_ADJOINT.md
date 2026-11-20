# Minimal exterior force datum for the saved formed n0 spin gap

Reused only same incoming-hi K84, its original 84×20 lift, the held-temporal 16×16 boundary form A, actual spin readout g, and the prior full three-vector field map C. No physical outer boundary was assigned. Let f=A w be the signed canonical RHS force needed to drive the interior with wall state w. One adjoint solve gives t=A^-T g; three dual solves give F=C A^-1. Then field=F f and signed gap=g^T w=t^T f. This avoids a time/space full inverse for the scalar once actual matched force is available. It is not the physical matched full operator.

Decompose t=F^T λ+t_perp by orthogonal projection in the saved canonical force coordinate norm. For a specified field, gap=λ^T field+t_perp^T f. There are 13 formally undetermined force directions from curvature alone, but only ONE additional scalar t_perp^T f affects this fixed finite linear gap. The exposed scalar is nonzero; a physical uncertainty model can bound it directly instead of supplying every exterior component. For a Euclidean admitted force error δ, its curvature-null contribution is bounded by ||t_perp|| δ; the norm is not physical units and no actual δ is available.

| Rows fixed in addition to interior constraints/held temporal trace | Rank out of 16 | Visible force-null dual norm |
|---|---:|---:|
| Three local curvature components | 3 | .332700197230 |
| Curvature, zero scalar RHS | 7 | .282585990372 |
| Curvature, zero temporal wall reaction | 7 | .332700111528 |
| Curvature, zero scalar RHS and temporal wall reaction | 11 | .178860416742 |

The final case uses the weak singular direction1.43368e−10 (rank threshold1e−14 relative to maximum). At looser1e−11 cutoff its numerical rank is10; the still-visible relaxed dual norm is .28258599. Already retaining the stricter row produces a legitimate finite witness: constraint residual1.81e−15, max original interior action force1.03e−14. Directions primarily A3 SU2_3 (.6883), A3 central (.5808), A1 SU2_1 and A2 SU2_2 (each −.3074) in signed unit force coordinates. All interior Gauss rows are part of those original residuals. The zero-load rows are stronger test conditions, not a claimed exterior boundary prescription. No exact continuum or gauge admissibility is inferred.

Actual difference from the two earlier carrier forces: norm1.45492606438, projected curvature residual1.83e−16. Pairing it against t_perp exactly replays the coordinate gap difference .261755713738 to displayed precision. The two individual chosen three-axis force families each have invertible F P, so selecting EITHER one alone would remove the ambiguity. No checked native matched source selects one exclusively. The stricter witness further shows that a ban on externally supplied scalar load and zero temporal wall load would not suffice on their own.

Evidence: formed_n0_minimal_exterior_adjoint.py/.json/.npz. Starting point is the existing finite field trial, not a physical uncertainty estimate, physical pole, or g.
