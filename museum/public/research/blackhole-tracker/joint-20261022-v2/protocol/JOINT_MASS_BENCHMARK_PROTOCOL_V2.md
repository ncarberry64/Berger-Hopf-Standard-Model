# Joint mass protocol v2: exploratory continuation, internally frozen

Date2026-10-22. This is a prospective internal freeze AFTER the exploratory v1
results, not an external preregistration or independent discovery. No v2 measured
fit precedes the final freeze receipt. Original v1 source, data, failed noise
checks, numerical-step study, profiles and20 controls remain intact.

## Why this version exists

V1M0 has residual time correlation. V1 additiveOU has substantially too-small
innovation variance relative to20 parametric/refitted controls; native reported
errors were empirically calibrated to observed scatter (Mróz2022 sectionII),
not supplied independent white variances. V1 default finite-difference time step
(.035day) also caused a small optimization error. These motivate explicit new
hypotheses and stable computational coordinates, never tuning toward any mass.

## Fixed data and physical model

Use exactly protocolv1 native bytes, identities, calibration and time assumptions:
15533 correctedOGLE author rows preserved; publishedHJD2455376..2457700 primary
window gives12500OGLE+21HST photometric rows;21 relativeNE angular rows from11
visits mapped to82 actual exposure headers. Exact native input hash and source
hashes are in freeze receipt. Native errors are NEVER edited in stored/exported
data. No fabricated images,fluxratios,delays,covariance,distances or precise HST
combined epochs. Native HJDclock assumption and fullHSTexposure-window uncertainty
remain explicit. V2 importer uses platform-independent Windows-provenance basename.

Retain v1 one-potential BHSM interpretation, point lens flux/centroid equations,
source-minus-lens NE sign, heliocentric Earth vectors, free source position and
relative-frame motion/apparent parallax, optional filter offsets, no absolute
Gaia zero-point or distance inferred. Mass=thetaE/(kappa*piE); tE alone is notmass.
Calibrated noise is an instrumental hypothesis, never a BHSM extra potential.

Stable computational t0 is days from the declared physical time-bound midpoint
(2455765JD_TDB for this benchmark). Physical t0 bounds stay2455700..2455830.
Changing only the numerical center must preserve predictions exactly. For future
targets require explicit analysis.bounds for t0JD,tE,u0,piE,thetaE,relative-frame
sourceparallax and initial guesses t0JD,tE,absu0,piE. No2011default is silently
assigned to a new object. Benchmark other bounds/seeds/modes are v1 unchanged.

## Complete candidate set, fixed before v2 outcomes

G0: centered native-diagonal check.
G1 PRIMARY: C=S R S, S=diag(native reported sigma),
Rij=(1-f)deltaij+f exp(-|ti-tj|/tau), f:[0,.95],tau:[.05,100]day.
This preserves every supplied marginal sigma and explicitly hypothesizes a
correlation; no full covariance is claimed supplied.
G2 COMPETITOR: sameR, but effective sigma_i=sqrt(k²sigma_native_i²+s²),
k:[.5,2],s:[0,.02]mag. Native sigma remains unchanged. k/s are calibration
nuisances to be jointly fitted/profiled, not an author-provided correction.

For both OU candidates minimize the FULL Gaussian objective Q+logdet(C/Dnative),
including negative determinant terms. For G1 reuse exactOU innovations on
r/native_sigma with whiteerror sqrt(1-f), latentamp sqrt(f), addingNlog(1-f)
to the returned determinant. G2 adds sumlog(sigma_eff²/sigma_native²).
A fixed offset makes a least-squares residual representation real:
B=-Nlog(.05) forG1; B=-N[log(.05)+2log(.5)] forG2. Report objective minusB;
B is never chi-square or evidence. Dense independent checks cover complete
objective, duplicate epochs,f0identity,k1/s0identity and worst bounded offset.
F0 leaves tau unidentified; zeroextra-floor and zeroblend are admissible physical
nuisance boundaries, with nonregular support-level qualification.

Initial f=.1,tau2days,k1,s.003mag.16 angular/sign starts unchanged.600evaluations
perstart; declared continuation to1800 for unresolved states. Keep every start,
failed case, distinct mode and lower-objective discovery. No prefit mass value,
literature mass prior or source absolute parallax prior. Scalar/fixed-mass exact
Gaussian scores are comparable only under the same likelihood and fixed data.

## Controls before measured v2 fits

Independent image-summed centroid/parallax tests inherited; fresh dense G1/G2
Gaussian objective checks; computational-center invariance; all actual-cadence
geometry injection and zero-parallax mass-null control. Predeclared noisy truth:
thetaE4.8mas,piE.12 (mass4.91168Msun),f.2,tau1.4day,k.9,s.003mag and seed20261022;
this differs from published target. Preserve noisy-injection output regardless
of outcome. No repeated seeds or noise choices to obtain a desired answer.

## Adequacy and out-of-sample structure

Numerical convergence, likelihood adequacy, parameter identification and physical
classification are separate. Both upper AND lower chi-square tails are screened
at.01. Innovation lag1 and LjungBox10 are recorded; approximate LjungBox df8 for
OU,10 forG0, screen.01. Parametric controls/refits calibrate rather than treating
these post-estimation screens as exact.

Before outcomes fix residual tables by native sigma,noise-free predicted model magnitude,seeing quartiles,
Julian365.25-day season, and fixed nativeHJD event2455400..2456400 versus
complement. Bin count>=30; conservative approximate two-tail probability is the
maximum using dfN and dfN-minus-totalparametercount. Bonferroni .01 across all
eligible bins screens heteroscedastic/season/seeing failures. Observed-magnitude
quartiles must not gate with naive chi-square because they select residual tails;
use noise-free predictions for brightness bins; these are approximate
postfit diagnostics, not exact coverage. Do not discard a failed bin or row.

BLOCKED PREDICTION for G1 andG2: assign entire observer-TDB night bins
floor(JD_TDB-.5), hold out nights with integer mod5=0 (about20%). Keep HST rows
and remainingOGLE nights in training; retain all heldout IDs/native values.
Refit training using all retained baseline modes. At training-fitted parameters,
compute heldout conditional Gaussian Q=Qall-Qtrain and logdet contribution
logdetCall-logdetCtrain-logdetDheldout using the same stationary model; GP
cross-night correlations are included. Native constants are common between
candidates. Report heldout count,two-sided Qscreen and conditional relative
Gaussian deviance. No randomperrow split that leaks intranight correlation.
Mean/calibration parameter uncertainty limits naive chi-square interpretation;
compare identical procedures in parametric controls where computationally feasible.

At least20 full-cadence parametric controls/refits per OU candidate; record
innovation/global/bin/lag statistics and known-generating-mass profile deviance.
Use independent fixed seeds2026102200+i forG1 and2026102300+i forG2.20controls
only provide coarse MC tail resolution1/21; report this limit and binomial
uncertainty, never precise calibrated coverage. Fitted noise is not certified
because of small in-sample residuals or a mass near the published value.

## Profiles, sensitivities and stopping

Both OU models retain conditional mass profiles over31 logspaced0.1..100Msun
including all retained modes. Refine genuine eligible delta1 and3.841459 brackets
to<.5% relativewidth. These are local likelihood support levels; physicalnuisance
boundaries make nominalWilks coverage unavailable. Artificial caps, failed points
and a lower constrained minimum break interval eligibility. No endpoint becomes
a claimed observational limit. Preserve all competing modes and unresolved points.

For each OU candidate that passes baseline adequacy, run the full v1 mandatory
sensitivities: all15533OGLErows; clock±120sec; fullHSTwindow endpoints;
duration-weightedHSTtime; same-visit/filter rho.4,.8; extraangularjitter.10,.25mas;
no filteroffset; hypothetical RELATIVE sourceparallax0±.2mas; allHSTnon-source
flux assigned to lens as limiting blend-location sensitivity; JPLDE432svectors.
Keep failures and conditionally fitted masses; these are not new measurements.
Profile/retain k,s,f,tau along with all physical/angular/flux nuisance parameters.

If G1 fails but G2 passes independent predictive/structure checks, G2 can support
conditional mass inference as an explicit estimated calibration hypothesis.
If both pass report both; prefer simplerG1 unless predictive evidence favorsG2,
never choose by closeness to literature. If all fixed candidates fail, STOP this
campaign and report mass CONDITIONAL/INADEQUATE with exact required calibration
or observation. No further model iteration is an acceptance criterion.

Mass support requires interior finite competing-mode support, adequate noise and
predictive checks, resolved numerical minima and stability across mandatory
sensitivities. A mass above3Msun identifies a high compact-mass candidate only.
A BH interpretation also needs independent darkness/lensflux evidence and
single-lens compatibility. Existing peer-reviewed darkness evidence for this
KNOWN object may be cited separately; this engine does not manufacture a new
flux limit. The2023published6.03(+1.19/-1.04)Msun is only a comparison target.
Unknown-object claims additionally require catalogalias/literature checks and
new adequate measured astrometry/parallax; frozen100 photometry does not supply
those measurements. No discovery is an acceptance requirement.

## Audit/export

Export native inputs/bytehashes, model/options/analysis bounds, software/source
and protocol pins, all states/modes, likelihood/offset/calibration/profile outputs,
residuals, diagnostic failures, sensitivity and predictive/MC receipts. V1 schema
and replay remain intact; v2 result/profile/replay use explicit v2 schemas.
An independent versioned acceptance receipt interprets gates; a raw numerical
solver status never automatically becomes a BH identification.

V2 input hashing canonicalizes whole finite floats to integers recursively
(excluding booleans) before deterministic JSON serialization. This preserves
numeric meaning across browserJSON parse/stringify while exact native byte
hashes remain unchanged. Hash algorithm is explicitly versioned in results.
