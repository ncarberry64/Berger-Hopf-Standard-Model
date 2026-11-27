# Action audit: what lets a massive surface load change the well's shape

The wider susceptibility control showed that a different optical profile can move the held-out image but missed the inner slope. This audit returns to the actual nonlinear action instead of scanning more shell radii, amplitudes or third-source residuals.

## Recovered pieces

- The galaxy v0.5 archives provide the reduced seam equation and a positive complement response, but explicitly leave the resolved loading vector b, direct term A_dir, numerical crossing and slip/readout unevaluated.
- AE4 gives exact derivatives of the constrained Schur solve from supplied physical operator and source derivatives. It is an algorithm, not a physical galaxy loading rule.
- The normalized v5.7 scalar/topographic action supplies a concrete nonlinear derivative. v5.11 explicitly distinguishes this finite homogeneous Hessian from the unresolved mixed collar/Berger trace and metric-stress mixing.
- The R1 angular optical provider computes Phi+Psi on six physical anchor states of the frozen cosmological n=2 harmonic. It is not a galaxy-scale optical readout on the v5.7 fields. Capital Phi in the v5.7 internal profile is not the Newtonian-gauge metric Phi.

## Derived from the existing v5.7 polynomial

Write the fields x=(T,Phi_internal), with V = x^T B x/2 + lambda (x^T x)^2/4, B=[[1,-3],[-3,1]], lambda=8, and equilibrium x0=(1/2)e+, e±=(1,±1)/sqrt(2). Introduce a formal force j through -j^T x to audit the response. This is a probe and not an identified source from nonsingular galactic matter.

The Hessian is H=B+lambda[(x^T x)I+2xx^T], with H0=diag(4,6) in this basis. For j=f n, v=H0^-1 n and
D_f H=2 lambda [(x0·v)I+vx0^T+x0v^T].
An infinitesimal unit probe in the fixed e+ channel has response y=H^-1 e+, so
D_f y=-H0^-1(D_f H)H0^-1 e+.
The derivative is the mixed two-probe response at fixed probe vector, not a result about the physical strength or morphology of the massive surface structures.

| Formal load n | D_f H in the e+,e- basis | D_f y |
|---|---|---|
| e+ | diag(6,2) | -(3/8)e+ |
| -e+ | diag(-6,-2) | +(3/8)e+ |
| e- | off-diagonal 4/3, zero diagonal | -(1/18)e- |

Thus a load parallel to the retained scale mode changes its amplitude (for positive probe sign it hardens the branch, the opposite of the softening used in the shell proxy). A load in the difference mode mixes in a second response at first order, before either eigenvalue shifts at first order. This is an action-derived channel distinction, not a selected galactic load; neither a sign nor directional overlap can be inferred from visible mass alone. The code checks central differences of the equilibrium, Hessian, and independent probe at three decreasing steps, and verifies the positive-branch fold along the opposing formal load only in normalized units.

For any fixed linear optical readout L, the second channel changes the normalized projected shape only if L e- has a component outside the span of L e+; if L e-=0 or proportional, the homogeneous mixing cannot change the optical shape. On the actual spatial domain the same test needs the projected operator/load, constraint and optical variations. The two exact missing objects for applying this calculation to Jackpot are (1) the projection of the independently fixed surface source onto the mixed, spatial Berger/collar problem and (2) a weak-field metric readout of those very modes on the same equilibrium. The archived fixed homogeneous solution or cosmological frozen-n=2 readout cannot be recycled as either. Do not fit either map to image B.

Replay: OPENBLAS_NUM_THREADS=1 python jackpot_archive_action_response.py. No lens rays or data were fit in this audit; no update to manuscript or conclusion on BHSM as a whole.
