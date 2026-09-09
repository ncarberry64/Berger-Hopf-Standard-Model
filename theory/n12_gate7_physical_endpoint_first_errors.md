# Physical endpoint first derivatives at a common normalized projector

For the exact stored endpoint frame F and supplied axis a, the physical
direction matrix is F(I-aa^T/(a^T a)), formed in Arb. Pass those Arb directions
directly to the retained physical rate derivative. This avoids the alternative
binary64 direction/weight division path in the parent API and uses one common
projector for the frame and physical derivative.

Subtract the stored first_mid matrix in Arb and export a verified error ball.
Thus the old first derivative is treated as a numerical center, without
assuming that its original projector or direction rounding was already exact.
The frozen action, endpoint state, descriptor, selected eigenline, weights,
frame and Green-axis selection are unchanged. Physical identification of the
stored frame is still a separate obligation.

The parent rate function is pinned to
0DC531574372EAA6C69AFAD3B4790A1C7EF52C18E7BA52B6C8FAAA1D442BFC2C.
Original base action jets and the eigenline are cached before the factored
contraction context is entered. The contraction adapter accepts only mutually
independent, correctly ordered broadcast axes. Shared axes, multidimensional
legs or reordered axes fail closed because flattening them would change
the derivative pairing.

    python scripts/derive_n12_gate7_physical_endpoint_first_errors.py --all-endpoints --workers 6 --worker-hour-cap 3

The 370 noninitial endpoints are required for all midpoint kinematics. The
initial endpoint is fixed, so it contributes zero rather than requiring an
unevaluated derivative. Each endpoint cache binds every numerical operand,
stored first-derivative source, producer/helper source and physical provenance.
Outward containment is checked before writing, and a missing or changed cache
pair is rejected. The bounded campaign preserves failures and supports reuse
of complete verified endpoint files.

The endpoint1 pilot evaluated all74 physical columns, compared its first two
columns with the original Arb evaluation, and verified outward export. It does
not establish all-endpoint coverage. After completion, compose these errors
through the actual midpoint construction and full physical Hessian pullback;
neighborhood variation, physical frame authority and Gate7 remain open.

The midpoint coordinate consumer forms h/8 [E_left,-E_right] from the two
endpoint DF error balls, applies the signed inverse of the stored full basis,
and adds the existing construction/solve error ball. Retained/complement
operator bounds remain separate. It checks the endpoint frame, axis and
stored first derivative against the exact operands of each midpoint.

    python scripts/certify_n12_gate7_physical_first_midpoint_coordinates.py --all-midpoints

Each midpoint requires both noninitial endpoint caches; the fixed initial
endpoint contributes an exact zero ball. Materialize the deterministic
coordinate artifacts twice from the same physical row evidence and require
byte identity. This closes the common-projector/first-derivative discrepancy
at the stored frames, without identifying those frames as exact physical
constraint charts or closing the remaining Hessian/neighborhood obligations.
