# Direct physical-point quadratic source integration

The complete ambient Hessian campaign provides upper-input-triangle rows of
the normalized physical rate at each actual endpoint and Hermite-Simpson
midpoint. Local C2 Hessian symmetry reconstructs the lower triangle. Every
row is required; an absent contraction is never supplied as zero.

For Cartesian families of endpoint directions U=(U0,U1), V=(V0,V1), form
Um=(I/2+h DF0/8)U0+(I/2-h DF1/8)U1 and the analogous Vm. Contract H0[U0,V0],
Hm[Um,Vm], H1[U1,V1] through the retained second chain rule:

    D2M = h (H0[U0,V0]-H1[U1,V1])/8
    D2r = -h (H0[U0,V0]+4 Hm[Um,Vm]+H1[U1,V1])/6 - 2h DFm D2M/3
    Q = -R_frozen^-1 T D2r / 2

The frozen trial frames are included in U and V. T and R are the same test
frame and right block used by the frozen inverse. Both endpoint slots are
explicit. The fixed initial endpoint has zero directions. Contractions and
solves use 512-bit Arb, preserve signs, and export rational centers/radii.

For each interval the consumer stores four endpoint-pair blocks (00,01,10,11)
for each input family LL, LT and TT. L is the existing stored axis, without
silently assuming exact unit norm. T uses the full 74-coordinate identity:
this supplies a superset of transverse inputs, not a fabricated quotient.
Columns have first-direction-major order. Symmetry supplies the TL family
by swapping both endpoints and direction arguments of the LT family; later
two-radius estimates must retain 2*LT*rL*rT. The Taylor half is already in Q.

The producer verifies all three full Hessian manifests, fresh independent
reproduction receipts, their exact physical value-point dependencies and
matching paired derivative data. The full DF workspace may add a wrapper
binding; it must still use precisely the same value campaign and point files.
Raw file fingerprints are retained alongside the foundation's normalized
text fingerprints and rechecked after assembly. Source bytes are captured
before computation. Repeat invocations recompute every block, preserving
originals and uniquely named mismatches. Completed blocks permit first-run
resumption; an old successful repeat receipt is archived before a new repeat.

Example after the three complete physical Hessians and full DF are paired:

    python scripts/certify_n12_gate7_direct_physical_quadratic_sources.py --interval 13 --full-derivatives
    python scripts/certify_n12_gate7_direct_physical_quadratic_sources.py --interval 13 --full-derivatives --recompute

These are local signed source tensors at the supplied physical points. They
do not enclose a neighborhood remainder, transport the sources through the
full causal inverse, differentiate moving frames, identify the physical
quotient, or close the physical radii inequalities. No new physical Hessian
data or Gate-7 completion is asserted by implementing the adapter.
