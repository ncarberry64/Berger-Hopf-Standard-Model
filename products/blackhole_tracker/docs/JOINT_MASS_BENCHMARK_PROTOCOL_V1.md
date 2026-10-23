# Native joint mass benchmark protocol v1 (2026-10-22)

This protocol is frozen before the first measured joint fit. It is a separately
versioned research route; the rc3 frozen100 and original2022 benchmark do not
change. The known object is OGLE-2011-BLG-0462 = MOA-2011-BLG-191. It is not a
new discovery. Published mass estimates are comparison outcomes, never inputs.

## Observations and clocks

Use exact Mróz2022 corrected OGLE author file (15533 rows; Zenodo20056044) and
Lam & Lu2023v2 HST Table2 (21 filter rows,11 dated visits). Preserve every native
byte, row identity, magnitude/error, seeing, calibration note, exclusion reason,
and hash. Primary OGLE window is the paper's HJD2455376..2457700; the all15533
row sensitivity is mandatory. No clipping, rescaling native uncertainties,
substituting fitted values, fabricated images/delays/distances/covariance.

OGLE's underlying HJD clock is unspecified by this deposit. Conditional main
route assumes HJD_UTC, inverts heliocentric correction at geocentre, and converts
to JD_TDB; omission of terrestrial displacement is at most0.0213sec. Mandatory
clock shifts ±120sec cover UTC/TDB-like differences under this assumption;
other undocumented clocks remain a limitation, not certified metadata.

HST82 complete primary headers match all21 date/filter groups by program,
exposure counts and durations. UTC EXPSTART/EXPEND produce actual exposure
midpoints. Main angular prediction averages all actual midpoints equally.
Photometry uses their derived unweighted mean as an approximation. Original
centroid/flux combination weights are unavailable: mandatory endpoints use the
full exposure START..END windows, with duration-weighted average also reported.
None of these derived means is labeled an author-supplied exact epoch.

RA means east tangent alpha*cos(delta), inherited from Lam2022 section5. The
published2023 bias corrections and added errors are already applied. Do not
reapply the old filter correction or added error. Table errors omit the global
Gaia absolute-motion transformation. Fit relative-frame source position,
motion and apparent parallax; do not report absolute source/lens PM or distance.

## Derived likelihood and physical model

One compact-lens optical potential counted once, interpreted in BHSM. No second
core/envelope deflection. With n=(cos(alpha),sin(alpha)) in NE and b=(-nE,nN),
source-minus-lens separation in Einstein units is
q=u0*b+(t-t0)/tE*n+piE*Earth_heliocentric_NE(t)/AU. t0/u0 are heliocentric
rectilinear coordinates, not apparent peak coordinates. Alpha remains free at
piE=0. Astropy Earth barycentric minus Sun barycentric is used; builtin vectors
are independently checked against JPLDE432s over the full baseline.

Native magnitude model is mbase-2.5log10[1+fs(A(u)-1)] per instrument with
0<fs<=1 (nonnegative source/blend flux). Image-centroid shift is thetaE*q/(u²+2).
Linear GLS profiles thetaE, source NE position/motion/apparent parallax and
constant nonreference-filter offsets. Lens-light sensitivity assigns ALL HST
non-source flux to lens; it is a limiting assumption about blend location,
not a measured location/flux constraint. Mass=thetaE/(kappa*piE), where kappa
uses IAU2015 nominal solarGM, exact c/AU and mas/radian. Absolute distance,
horizon, core state and membrane radius remain unavailable.

M0: native diagonal errors. M1: same physical model with an optional stationary
OGLE magnitude OU covariance Kij=sigmaGP² exp(-|ti-tj|/tau), diagonal native
variance retained. Its exact Gaussian objective is r'C^-1r + logdet(C/D),
not just whitened chi2. Hyperparameters sigmaGP:[1e-5,.3]mag and tau:[.05,100]d.
This derived O(N) tridiagonal evaluation must match independent dense covariance.
No fitted covariance is presented as covariance supplied by observers.

## Bounds, search and controls

Frozen nonlinear bounds: t0JD-2450000:[5700,5830], tE:[20,2000]d,
signedu0:[-1,1], alpha periodic[-pi,pi], piE:[0,1], instrument baseline native
median±5mag, fs:[1e-5,1]. Angular thetaE:[.01,40]mas and relative-frame source
parallax:[-1,1]mas. These are model/search bounds, never evidence or intervals.
Main16 starts cover8 angles and bothu0 signs, piE=.1,tE250d,t0relative5765,
OGLEfs.05,HSTfs.98. Keep every start, failure and distinct converged mode.
3point finite differences; max600 evaluations, objective/step tol1e-10,
gradient1e-7. An unresolved run may be extended with identical predeclared
starts to max1800, but no data-dependent new priors/selection. Retain all modes.

Before measured fits: independent image-position/flux centroid, parallax-sign
and finite-difference Jacobian, dense GP covariance/logdet/conditional mean,
noiseless recovery at ALL actual retained cadences, zero-parallax null control
(mass unavailable), and nonzero injected truth distinct from published mass.

Profile mass at31 logspaced masses0.1..100Msun, retaining up to8 converged
modes, max600 perpoint/start (1800 continuation if unresolved). Refine genuine
bracketed delta-deviance1 and3.841459 crossings by interpolation plus additional
fits until relative width<.5%, provided every bracket row is interior/converged
and reference minimum valid. A source-fraction1 state is an admissible physical
zero-blend boundary, recorded as nonregular: profile support levels remain valid
objective comparisons but nominal Wilks confidence coverage is unavailable.
Artificial caps, unresolved points or a lower constrained
minimum interrupt eligibility. Report intervals as LOCAL asymptotic likelihood
support, never calibrated coverage. Parameter uncertainty must retain degeneracy;
no mass inference solely from duration. No finite crossing means unavailable.

## Mandatory sensitivity and acceptance

For M1 refit the following using all baseline modes (minimum4 angular seeds as
fallback), same bounds: all OGLErows; OGLEclock±120sec; earliest/latest fullHST
window; duration-weighted HSTtime; cross-filter same-visit same-axis rho=.4,.8;
additional astrometric jitter.10,.25mas; nofilter offsets; relative-frame source
parallax prior0±.2mas (explicit hypothetical frame sensitivity, NOT the published
absolute-source prior); limiting allblendislens light; JPLDE432s vectors. Native
errors and calibration remain unchanged in every sensitivity.

Numerical convergence, model/noise adequacy, parameter identification and
physical interpretation are separate. Diagonal chi2 tail below.01 rejectsM0.
For M1 approximate innovation/astrometric chi2 and innovation lag are screens;
perform at least20 parametric simulated/refitted Gaussian OU controls to assess
fit and lag statistics. With few simulations report MonteCarlo uncertainty and
inability to resolve p<.01; do not claim precise calibrated confidence.

Mass support requires interior competing-mode profile crossings, independently
identified thetaE and piE, no untested lower-deviance mode, adequate residuals,
and stability across mandatory assumptions. A mass above3Msun is a compact-mass
candidate criterion only. A black-hole interpretation additionally requires
independent lens flux limits/darkness and single-lens compatibility; magnitude
blend fractions alone do not supply that evidence. This known system must be
compared with published2023 mass6.03(+1.19/-1.04)Msun without tuning toward it.
If any condition fails, report the point fit and reason it is conditional,
unresolved or inadequate. No new object/discovery claim is an acceptance test.

## Provenance and replay

Export full input, source hashes, scientific source hashes, environment versions,
all start/mode/likelihood/nuisance/profile outcomes and residuals. Replay must
validate input/source/protocol hashes and reproduce predictions/objective, not
silently change data or normalize a failed profile. Every method or bound change
after first measured fit increments protocol version and preserves this record.
Sources: https://arxiv.org/abs/2308.03302 ;
https://doi.org/10.5281/zenodo.20056044 ;
https://docs.astropy.org/en/stable/coordinates/solarsystem.html .
