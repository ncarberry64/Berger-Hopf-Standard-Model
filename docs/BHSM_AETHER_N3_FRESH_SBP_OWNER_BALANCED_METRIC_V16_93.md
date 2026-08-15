# BHSM v16.93 owner-balanced normal-metric audit

Identity weights, measured period/`w_0`/`v_0` equilibration, and stronger
event emphasis were tested only as normal-equation preconditioners. All trials
were evaluated using the unchanged physical KKT and identical soft event.

Identity wins the Pareto criterion. It reduces the residual from
`2.486624819288` to `2.437270312411` and the event magnitude from
`0.211419776681` to `0.208275968279`, with `eta_min=0.840365825398`.
Simple diagonal owner equilibration is not promoted.
