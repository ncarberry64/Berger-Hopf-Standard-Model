# Outgoing sphere versus native moving-wall action conormal

## Exact flat-sphere reference
Take one unit-normalized transverse electric S2 vector spherical harmonic, and let A(r) denote the amplitude in the physical orthonormal angular frame. The covariant angular trace variable is u=r A. The usual Maxwell action for this mode, with unit overall coupling, is
  S_L=1/2 ∫dt dr [u_t²-u_r²-l(l+1)u²/r²].
For the exterior r>=R the lower-face **outward Lorentzian action** variation is f_u δu with f_u=+u_r(R). It is not the Euclidean outward normal derivative −u_r. In the A coordinate f_A=R f_u, i.e. f_A/A=R²(A'/A+1/R). Using A'/A alone would omit the geometric contact. Equivalent reduced actions obtained by integration by parts must retain the corresponding boundary term.

For exp(−iωt), outgoing h1^(1)(kr)=−exp(ikr)(kr+i)/(kr)², x=kR:
  R f_u/u = 1+x h1'/h1 = ix−i/(x+i)
          = (−1+i x³)/(1+x²) for real x
          = −1+x²/(1−ix).
The rational expression with 1+x² cancels its apparent upper-half-plane x=+i singularity, and the quotient has no x=0 pole despite the individual Hankel divergence. Its actual simple exterior-only Dirichlet DtN pole is x=−i. It is not a zero of the matched interior+exterior action pencil and not evidence of a particle pole. Static return is −1/R in the u chart, −R in the orthonormal A chart. Positive real-frequency sign Im(f_u/u)=x³/[R(1+x²)] is consistent with outgoing radiation for this action/time convention. Conservatively, |R f_u/u+1| ≤ |x|²/(1−η) when |x|≤η<1. Useful unit test, not a BHSM analytic-domain claim.

## Native chart check
From source_integrated_source.py weighted_curvature and the retained n0 central radial action, let b be the raw covariant angular connection coefficient, rho the material radial coordinate with wall at pi/2, t the saved coordinate clock, and e,r,d,s the exact central weights. Its sector has density
  C_M/2 [e(b_t−s b_rho)²−r b_rho²−4d b²],
  C_M=0.0003208119454588855 in the original cap action.
With pi=e(b_t−s b_rho) (factor C_M excluded intentionally), lower-face exterior action conormal is f_b=C_M(s pi+r b_rho). Interior upper-face conormal is the opposite. The BHSM b is already a covariant one-form coefficient in the right unit-S3 coframe: orthonormal component b/R4. No flat +1/R contact is to be added to its native traction. If changing the native field variable to A_orth, rewrite the entire action, derivative and boundary pairing together, including R4 derivative. The S2 l(l+1)=2 geometry in the reference is not the S3 n0 curl²=4 angular operator, and neither pi/2 nor R4 is by itself a flat exterior radius calibration.

Exact incoming-hi wall values evaluated with exact_radial_known_blocks.py:
  e=4198.4562263622265, r=5921.340578763061, d=5581.932384919164,
  s=.0779237798365626, R4=.9633777962755173, wall proper lapse Nw=1.108427234091954.
Central principal check: for frozen local outgoing plane wave exp(i k_rho rho−iω_t t), ω_t=(sqrt(r/e)−s)k_rho and
  f_b/b=+i ω_t C_M sqrt(er).
The shift cancels from the impedance, NOT from speed. C_M sqrt(er)=1.5995777933336193 on this exact wall for unit internal/Haar channel. This is the principal high-frequency coefficient. It is not the static load and excludes coupling, derivative / curvature subprincipal pieces and global backscatter. The expression compares only the declared exterior outgoing side, not the already-signed opposite conormal.

Clock and numerical rescaling: proper wall interval dτ_w=Nw dt gives f_per_proper=f_b/Nw and ω_t=Nw ω_proper for frozen Nw. If numerical t=t0+T θ and b=B0 a, then action variation ∫dt f_b δb=∫dθ (T B0 f_b)δa. Hence frequency return f_a/a=T B0²(f_b/b) at ω_t=Ω/T; the principal slope is iΩ B0² C_M sqrt(er). In the existing collar diagnostic rho=pi/2+T x, b=T a, this action-level coefficient carries T². If instead dividing the entire action by T² as a declared common convention, it cancels. Do not compare the diagnostic's unweighted characteristic fields directly with original K84 conormal. A transfer from an external normalized mode requires its separate channel/trace scale and congruence before combination.

Actionable checks for a future native receiver: validate signed high-frequency iω coefficient after undoing all time, amplitude, and cap-weight changes; check flux orientation by power and a smooth two-sided collar; then compute static limit and poles separately. A flat h1 formula passes the reference test but does not define the physical BHSM exterior.
