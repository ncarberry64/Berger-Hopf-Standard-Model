# Final numerical review of the manuscript

Date: 21 October 2026.

**Numerical result: PASS.** The displayed numerical predictions agree with
the new nine-stage replay receipts. No recalculation or change to the
scientific numbers is required. Four notation/label clarifications were
reported to the manuscript owner below. This review inspected the saved
replay, manuscript sources, tables, and implementation; it did not rerun the
expensive propagation stages.

## Replay and tabulated predictions

`artifacts/replay/replay_receipt.json` reports all nine stages executed with
zero return codes and the inherited source inputs verified against their
SHA-256 hashes and lengths. Its source commit and runtime versions agree
with the manuscript provenance statement.

All 24 entries in the response-coefficient table reproduce the receipt's
four-significant-figure rounding. All 24 cells in the delay table reproduce
the stated decimal rounding or the exact first-order zero. The stored
fractional delay rows also independently satisfy
`k=sqrt(2)*(g_os-g_ol)` for every configuration.

| Lens/source redshifts | Baseline delay (days) | Fractional shift at 0 degrees | Delay shift (seconds) |
|---|---:|---:|---:|
| 0.3 / 1.0 | 7.753621449299 | -5.27256743099e-7 | -0.353216090239 |
| 0.3 / 0.6 | 9.268876034614 | -1.53731788248e-7 | -0.123113164710 |
| 0.5 / 1.5 | 11.583862635159 | -1.16241458348e-6 | -1.163397674313 |
| 0.8 / 2.0 | 17.264698901559 | -1.92488731685e-6 | -2.871296635229 |

These fractional shifts include the illustrative coefficient 0.001. They
must not be confused with the unit-anchor derivative, which is larger by
a factor of 1000. The manuscript makes that distinction correctly. The
90-degree sign reversal and the 45-degree first-order null follow from the
same cosine law. Finite-map completion values at the null are explicitly
excluded from the physical first-order prediction.

At (0.3,1.0), the printed distances, source angle, Einstein angle,
background image positions, and 7.75362145-day delay agree with the saved
receipt. The independent SI audit remains a direct check of

    Delta t0 = 2(1+z_l)b*s*(d_ol/d_os)/c,

with physical s=0.8 kpc and b=4*pi*(200 km/s / c)^2. Its maximum relative
discrepancy is 6.24348940397e-16, correctly rounded in the verification table.
The code's c/H0-to-Mpc and length-to-seconds conversions are consistent.

## Seed normalization and smallness

The timing and angular-ray receipts use the same six-component preparation
`(0,0,0.001,0,0,0)`. Its density profile is 0.001 times the unit-L2 normalized
quadrupole; the manuscript correctly rejects interpreting it as a uniform
0.1-percent density perturbation.

For the nodal tensor, the exact angular maxima at a fixed radial position
are `max |Q|=N*sin(chi/R)^2/sqrt(2)` and
`max |grad Q|=sqrt(2)*N*sqrt(K)*|sin(chi/R)|`. Applied to the saved temporal
rows and sampled at 2001 radial points, they reproduce:

| Source redshift | Sampled maximum twice the potential magnitude | Sampled maximum matter speed / c |
|---|---:|---:|
| 1.0 | 3.26781692125e-6 | 4.88719871549e-6 |
| 2.0 | 2.03826385629e-5 | 1.71552366551e-5 |

The manuscript's rounded values and its qualifications about radial
sampling, continuous bounds, and nonlinear truncation errors are accurate.
The corresponding spatial metric maxima agree at the displayed precision.

## Angular Euler equation and normalization

The manuscript's original angular equation has the correct sign and
normalization, provided `w(eta)=sum_j[phi_j(eta)+psi_j(eta)] y_j` and primes
refer to differentiation with respect to chi:

    theta' = L/S_K(chi)^2,
    L' = -w*N*sin(chi/R)^2*h*theta,   h=+/-sqrt(2).

Indeed `D_tilde=S_K(chi)*theta` gives

    D_tilde'' + K*D_tilde = -N*K*w*h*D_tilde,

which independently confirms the sign and curvature factor in the Green
response. For a nonzero vertex chi_a, the code uses theta_a=0 and
L_a=S_K(chi_a), giving unit conformal separation derivative. At the observer,
it uses the regular origin series including the perturbative coefficient.
The h=+/-sqrt(2) values are the eigenvalues of
`H_C=sqrt(2)*diag(1,-1)`, with the same L2 normalization as the angular section.

The complex-step and weak real derivative discrepancies, the Green/forced
Jacobi comparison, temporal refinement, harmonic Gram matrix, anchor
reconstruction, image derivative and effective-potential checks all round
to the values printed in the verification table. Their differing
normalizations are appropriately distinguished from observational errors.

## Shared-state comparison

The reported common-profile determinant maximum is
1.00974195868e-28, consistent with the printed bound of 1.01e-28. The
restricted two-source coefficient is
`R_11=-9.20598661657e-8`, matching the displayed matrix. Its source order is
z_s=1 followed by z_t=0.6, so the sign is consistent. The plotted 33-point
scan, its factor of 1e7 on the vertical axis, and the fixed quadratic
comparison matched at z_s=1 agree with the receipt and figure-generation
code. The text correctly limits this contrast to one fixed physical
main-plane quadratic term.

## Clarifications reported to the manuscript owner

1. Explicitly define the unindexed `w` in the original angular Euler
   equation as the six-state Weyl coefficient and state that its primes
   mean d/dchi. Other equations use derivatives with different parameters.
2. Explicitly call the quoted +0.8331365 and -0.6377768 arcsec positions
   background image positions, and the 7.75362145-day value the baseline
   delay. The numbers are correct; their location under the illustrative
   finite preparation should not suggest they are finite perturbed roots.
3. Specify the action-constraint residual denominator as
   `max(1,||w_canonical||_infinity)` rather than an unspecified state norm.
4. Distinguish the dimensional cubic denominator Lambda^3 in the main
   action from the code parameter lambda=Lambda^3/(M_Pl H0^2), as already
   defined in the appendix; likewise distinguish the dimensional potential
   slope mu^3 from its code value mu^3/(M_Pl H0^2)=3. The numerical action
   and SI conversion themselves agree.

No root manuscript files were edited by this reviewer. The conditional
state, prescribed SIS, fixed physical source, nodal-ray restriction,
paraxial order, and lack of observational inference are consistently
retained throughout the reviewed manuscript.
