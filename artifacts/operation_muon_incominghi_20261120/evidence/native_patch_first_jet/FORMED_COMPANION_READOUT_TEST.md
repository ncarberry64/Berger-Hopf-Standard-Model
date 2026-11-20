# Companion axial readout for the conditional incoming-hi wall comparison

Reuse saved n0 wall A, candidate gap differential g, and actual local angular reduced field rows C. In the original unit internal basis, define z to be the unit projection of the central generator onto the complement of the local Higgs-aligned q. Test the companion row w ↦ z·δA_axis3, a fixed-gauge coordinate, and separately the axial variation of the full Higgs-projected nonabelian curvature, including D_H q. No new external loads are assumed.

On the six original central/H-aligned traction coordinates, the three C rows leave 21.98% of the Euclidean response covector norm in their nullspace. Adding the orthogonal axial connection row reduces the relative residual to 7.9e−14. Coefficients in native units are 0.462385799 for the axial reduced field and 0.771820970 for that companion connection. Adding full axial projected curvature instead also reduces the relative residual to 7.5e−14 in this same force span (coefficients 0.431489270 and 0.299518255).

The two extra readouts are NOT interchangeable beyond this span. Across all 16 wall traces, the companion connection leaves a 1.35e−7 relative trace-covector residual, while the projected full curvature still leaves 61.24%, effectively unchanged from using the reduced field alone. A small coefficient residual is not an observable error bound without bounding the omitted physical response in a compatible norm. Norms above refer to declared Euclidean native coordinates only. This identifies a high-priority exterior projection for the finite candidate, not a claim of physical weak-source admission, exact factorization for all traces, field normalization, or g.

Replay with OPENBLAS_NUM_THREADS=1 python formed_companion_readout_test.py.
