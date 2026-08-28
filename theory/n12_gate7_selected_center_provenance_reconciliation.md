# Gate-7 selected-center provenance reconciliation

The retained proof-center selection names the quarter-step DOP853 history.
Its matched Green correction and terminal crossing use the quarter-step
constraint tangent.  The later exact curvature scripts had instead named the
half-step center/tangent, while the first recentered-cone implementation
inherited the still earlier multiple-shooting center through a default
import.  These are distinct histories, so shape agreement is not a valid
common-frame provenance proof.

The same audit found that the former common-frame data-matching record used
half-step tangent, graph-Jacobian, dense-residual, and first-hit data together
with the quarter-step Green correction.  The 8,692-cell bordered-response
chain itself already names the selected quarter-step center and remains
current; its surrounding common-frame diagnostic and first-hit operands must
be replayed on that center before the three interval adapters are evaluated.

Standalone exact tensors on the half-step history remain mathematically
valid for that history.  Their composition with quarter-step Green data is
invalidated.  Likewise, the earlier recentered cone is not a current
selected-history certificate because it added the quarter-step correction to
the original multiple-shooting center.

The current rebuild names the selected quarter-step center and its matching
tangent explicitly in every exact directional, mixed, transverse, causal,
and budget script.  The retained first-hit polynomial, dense residual, graph
Jacobian, and common-frame matching are likewise replayed on the quarter-step
history.

The selected quarter-step DOP853 chain already supplies the current interval
carrier.  Its exact degree-seven Bernstein cover has certified the selected
line, projector graph, bordered hard inverse, complete internal response, and
a finite response first-variation tube.  This chain is not the invalidated
original-center plus quarter-correction carrier and does not need rebuilding.
Its only open response item is the decorrelated scalar second-variation
denominator.  The exact selected-quarter causal radius must still be attached
to the DOP853 cell carrier to form the nonlinear product tube; that is a
same-center augmentation, not a replay of the legacy cone.  The signed
common-frame curvature must then be contracted on those cells to derive
correlated `Y,Z1,Z2`; the legacy recentered cone remains historical.  No
action, branch, source, selector, scale, gate, or physical endpoint changes
in this reconciliation.

The deterministic replay entry point is
`scripts/replay_n12_gate7_quarter_step_common_frame_operands.py`.  It pins the
quarter-step center for the rational first-hit proof, Gauss-12 dense residual,
and exact graph Jacobian, then rematerializes the common-frame matching audit.
The end-to-end selected-center entry point is
`scripts/replay_n12_gate7_selected_quarter_chain.py`; it rebuilds the exact
curvature, retained response-jet, common-frame, provenance, adapter, and
current-system-map artifacts in dependency order.
