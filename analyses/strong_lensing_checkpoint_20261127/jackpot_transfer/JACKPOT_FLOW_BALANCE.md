# Steady flow and buildup between Jackpot's two inner rings

Take flow as the working cause, not a measurement. On the regular surface side of the model, for a radially inward steady transported quantity with no sources in the band and no imposed azimuthal velocity, the flux per unit azimuth is F=r q |v_R|. Slowing the flow at fixed F raises stored quantity q locally; it does not make total stock grow in time unless influx exceeds outflux. Finite throughflow and large stored response are different observables. For a numerical test only, take projected optical storage as proportional to q, without identifying the moving quantity as stars or particle mass.

Freeze ordinary masses and the earlier Chabrier circular excess. In the layer, use reference stock per radial angle and radius proportional to its mass-profile derivative M0'(r), and set inward speed inversely to the stock so every comparison satisfies the same fixed steady flux. Multiply the reference stock by
1+d[h(r)+epsilon f(r) cos 2(theta-theta0)].
Here f is the prior smooth annular bump and h=f-C f(2z-1)^2, with z the fractional radius and C fixed once by integral M0'h=0. This makes a slowdown in the middle and compensation in the shoulders, without moving either calibrated circular aperture mass. The compensation is imposed for the experiment, not inferred from observations. The model remains strictly positive for all sampled settings. Choose d=.25,.50,.75 and epsilon=0,+.5,-.5 in advance. The axis theta0 is the one inferred from the previous whole-annulus fit to the **same early data** only; the negative option rotates the quadrupole by 90 degrees. It is not an independently measured flow direction. All strengths are sensitivity choices, not derived couplings or inferred velocities.

Solve the radial deflection and the m=2 Green response separately, adding them once to the existing map. The symmetric compensated arm has zero direct correction at both observed S3 ray coordinates; its forecast changes only through the early-ring nuisance recalibration. The angular part changes their direct bending. Fit only the same shear and S1 coefficients using first-two-source knots. A then anchors the source-3 counterimage solution; observed B only scores it.

| Trial | Early RMS, mas | Held-out B error, mas |
|---|---:|---:|
| No choke perturbation | 31.4 | 346 |
| d=.75, radial only | 24.2 | 316 |
| d=.75, coherent anisotropy | 20.5 | 279 |
| d=.75, 90-degree rotated anisotropy | 32.3 | 367 |

For the d=.75 coherent arm the center's assumed speed falls to 47% or 73% of the reference along the two principal directions. Neither number is a measured speed. The earlier conventional Chabrier comparator has 38 mas B error. The coherent trial improves both ring geometry and the outer forecast compared with the frozen shape-only baseline without moving either circular aperture mass, but still falls short of the conventional check. The remaining physical need is an independently specified flow law and a light-deflecting metric response, not selection of the sign, amplitude or angular direction from B. No HE 0435 transfer.

Replay: OPENBLAS_NUM_THREADS=1 python jackpot_flow_balance.py.
