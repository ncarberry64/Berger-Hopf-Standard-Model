# Full-vector equal-local-field native comparison

On the actual incoming-hi frozen n0 chart, reuse the original 16-wall action A and corresponding same-state spin-gap covector g. Hold geometry, temporal wall trace and finite spin pair fixed. Compare two independent three-axis force families: central U(1) or unit Higgs-aligned angular charge. No retarded domain, physical far-field incident amplitude, or native normalized muon pole is added.

Because H is homogeneous on the angular S3 slice, its local reduced connection has coframe components a_i=A_i·Qhat(H); the angular Higgs reframe has no tangential derivative. In the signed native curl+2 coframe, B_i=2 a_i/R4². With geometry fixed, the actual three-component derivative is
  C δw = (2/R4²)[δA_i·Qhat + A_i·(D_H Qhat)δH].
The second term uses actual background connection and induced scalar readout, not a fixed-H assumption. Complex-step derivative of normalized charge uses its exactly constant norm sqrt(16/3); independent real centered finite difference verifies the full B map. This is reduced local angular curvature, not an identification with the complete physical incident electromagnetic field.

For each force family P (16×3), solve
  X=A^-1 P, s=(C X)^-1 (0,0,1)^T, δw=X s.
Both three-axis response matrices are nonsingular (smallest singular values .42090442 and .52979830). Both give the SAME full local reduced angular derivative (0,0,1) to2.3e−16. Independent nonlinear field finite difference agrees within1.23e−12. Original interior residuals ≤3.36e−14 and wall-force residuals ≤5.1e−16.

| Force family | Coordinate spin-gap response | Wall-proper spin-gap response |
|---|---:|---:|
| Central | .726417973549738 | .655359189315512 |
| Higgs-aligned | .464662259811661 | .419208627792624 |

Their response difference lies in the nullspace of all THREE local curvature rows (norm2.22e−16), yet changes the spin gap by .261755713738077 coordinate or .236150561522888 proper. Thus even matched local amplitude and direction do not by themselves determine the finite BHSM spin response when the sourced scalar/gauge profile is unresolved. The missing ingredient is the actual retarded exterior and affine incident force, or a proof their unresolved differences lie in the spin-gap covector's nullspace. This comparison does not assert either abstract force is an allowed physical incident Maxwell solution, that the complete local electric/weak data match, or that physical g is ambiguous.

Replay formed_n0_equal_local_field_test.py, full solver checks .json, saved field-flat difference and covectors .npz. No formation restart or repo edits.
