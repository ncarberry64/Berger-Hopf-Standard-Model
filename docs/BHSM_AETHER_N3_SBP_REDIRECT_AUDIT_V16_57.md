# BHSM N=3 endpoint-plateau SBP redirect audit v16.57

After correcting the normalized soft-mode curvature and continuing through
v16.55, the remaining parent-geometry residual is still concentrated at the
first and last collocation layers. The retained centered/second-order endpoint
derivative has a large exact summation-by-parts defect with trapezoidal
quadrature.

The minimal trapezoid-SBP derivative changes only the two endpoint derivative
rows and satisfies the discrete integration-by-parts identity exactly. This
new evidence activates a fresh canonical-reset N=3 solve with that pair. The
v16.55 state will not be transplanted into it.
