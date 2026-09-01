# Gate-7 refined within-seam Hermite collocation

The second current-linearization Newton step reduces the dense defect only
weakly, suggesting that the quarter-cell cubic interpolant itself is the
remaining numerical floor.  Insert the already-evaluated exact field at the
midpoint of each of the 370 fine spans, producing 741 nodes and 740 half-spans.
This is refinement inside the retained quarter-step proof center, not a return
to a historical half-step center.

Join adjacent refined nodes by endpoint-field-matched cubics and replay the
direct action at three Gauss nodes on every half-span.  The observed reduction
decides whether further owner-only refinement can reach the existing
Taylor--Volterra/Krawczyk enclosure budget.

`FULL_BHSM_COMPLETE = FALSE`.
