# Matching countercheck using the actual central wall coefficients

This is an artificial single-channel exterior calibration against the saved K84 incoming-hi interior with the wall temporal trace held. It does not select a BHSM exterior or solve for a physical muon.

Freeze e,r,d,s and the cap factor C at the saved wall for the entire half-line x≥0. For the central coframe trace b and exp(−iωt), set a=r−es². The bulk equation is
  a b'' + 2iωes b' + (eω²−4d)b = 0.
Writing b=exp(−iωesx/a)v gives v''=(4da−erω²)v/a². The original outward exterior action force is f=C(a b'+iωes b). Thus the exact retarded/scattered force per trace is −C√(4da−er(ω+i0)²), choosing the root positive at zero and analytically continued from Im ω>0. This recovers the earlier high-frequency slope +iω C√(er) and is real below the artificial channel threshold 2.30112680275 in the saved coordinate units.

Static return is −3.68083133332, not the required −4.12221888503 for zero composition force. Compared with the rank-one central target calculated from original K84/M84/B84, the uniform extension instead has an additional finite numerical null at ω=.236801683063; its original free-row residual is 1.16e−14, and one numerical null already existed in the interior. This is an artificial matched mode below its propagation threshold, neither a measured frequency nor a physical spin resonance. No incident drive was applied.

Nonlocality check: leave the entire first .2 radial-coordinate units unchanged and vary only the positive angular coefficient d in the tail by factors .5, 1, 2. Match the shifted phase-removed field and its conormal at the distant interface by exact hyperbolic transfer. The static returns become −3.14326276, −3.68083133, −4.31033622 even though wall coefficients and all wall jets are the same. With factor .5 a bracketed real null moves to .39096553. With factor 2 the test has no sign bracket at the endpoints, not a no-root proof. The far tails are intentionally declared comparison profiles, not BHSM solutions. This establishes why an outgoing prescription and locally correct wall data alone do not supply the weak-field boundary amplitude.

Replay: OPENBLAS_NUM_THREADS=1 python frozen_native_central_halfline.py.
