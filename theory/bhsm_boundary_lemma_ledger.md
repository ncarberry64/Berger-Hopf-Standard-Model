# BHSM Boundary Lemma Ledger

| code | name | status | statement | proof sketch | dependencies | linked prior gate |
| --- | --- | --- | --- | --- | --- | --- |
| LEM-BH-1 | Phase second-variation lemma | DERIVED_CONDITIONAL | S_phase(d,2pi/d+epsilon)=d^2 epsilon^2 + O(epsilon^4). | Expand 2-2cos(d epsilon) at epsilon=0. | AX-BH-2 | phase_closure_second_variation.md |
| LEM-BH-2 | Orientation quadratic lemma | DERIVED_CONDITIONAL | For R=diag(s_i+epsilon_i), s_i^2=1, the finite orientation surrogate has quadratic part 4 sum epsilon_i^2 + lambda_trace (sum epsilon_i)^2. | Taylor expand (r_i^2-1)^2 around s_i=+/-1. | AX-BH-3 | orientation_involution_second_variation.md |
| LEM-BH-3 | Cyclic phase lemma | DERIVED_CONDITIONAL | For order n cyclic closure, |exp(i n epsilon)-1|^2 = n^2 epsilon^2 + O(epsilon^4). | Apply the phase expansion with d replaced by n. | AX-BH-4 | cyclic_channel_second_variation.md |
| LEM-BH-4 | Endomorphism block lemma | DERIVED_CONDITIONAL | End(C^d)=M_d(C), with d=1 giving C. | Use the standard finite-dimensional complex endomorphism algebra identity. | AX-BH-7 | finite_boundary_algebra_source_gate.md |
| LEM-BH-5 | Projector-to-primitive lemma | DIAGNOSTIC_SUPPORTED | The previously audited finite boundary algebra supplies central projectors and orientation grading that map into C, ell, sigma, w. | Use the existing projector/integer primitive bridge. | AX-BH-7, AX-BH-8 | boundary_integer_charge_hypercharge_bridge.md |
| LEM-BH-6 | Charge formula lemma | DIAGNOSTIC_SUPPORTED | The existing bridge maps C, ell, sigma, w to T3, Y, Q. | Apply the audited integer primitive formulas. | AX-BH-8 | boundary_integer_charge_hypercharge_bridge.md |
| LEM-BH-7 | Anomaly diagnostic lemma | DIAGNOSTIC_SUPPORTED | The existing one-generation diagnostic anomaly sums vanish under the audited charge/hypercharge assignment. | Use the already audited anomaly sums and Witten parity check. | AX-BH-9, LEM-BH-6 | boundary_integer_anomaly_closure_gate.md |
