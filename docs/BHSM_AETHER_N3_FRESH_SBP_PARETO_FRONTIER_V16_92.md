# BHSM v16.80-v16.92 metric/Pareto N=3 frontier

Fresh Gauss--Newton normal-metric and expanded nonlinear-ray steps reduce the
unchanged exact-SBP N=3 physical KKT residual from `12.853643589435` to
`2.897637137967`. Event-row weights are then used only as preconditioners;
every candidate is accepted using the original complete residual and the
identical ordered Euler--Dirac eigenvalue event. Pareto selection maximizes the
minimum fractional progress of those two mandatory closures.

The current v16.91 state has complete residual `2.486624819288`, event
residual `-0.211419776681`, and `eta_min=0.840494687332`. The terminal soft
eigenpair residual is `1.00e-14`, with lower/upper gaps
`0.170116896187` / `0.007996572397`.

The former `log_scale` norm has fallen from `14.016355587104` to
`0.465980389110` without deleting a variable or equation. The remaining
owners are period stationarity `1.853375463700`, `w_0` stationarity
`1.148018415647`, and `v_0` stationarity `1.074632770789`. Simultaneous saddle
closure is not yet achieved; the next same-action correction must target
these blocks while continuing the same physical event.
