# Prediction validation partition v2.1

The scientific likelihood, source pin5bb94198565fb25414f1f05908c00d49838c4b73,
baseline fits and mass profiles remain unchanged. Before any held-out outcome,
the study corrected the validation partition at2026-10-22T20:49:25Z.

The original protocolv2 floor(JD_TDB-.5) rule split Chile observing nights at
approximately00UT. Its planned conditional score is retained as a disclosed
diagnostic and does not establish prediction on independent nights.

The corrected rule is floor(JD_TDB+longitude_east/360), holding out bins with
integer mod5=0, using LasCampanas approximate longitude−70.692degrees. The day
boundary is local mean solar noon, in daylight. This fixes2464 held-outOGLE
rows. Minimum adjacent cross-partition gap is.606267day; none is below.1day.
Independent checks found the nearest observation5.9955hours from this boundary;
±120seconds clock and±.1degree longitude do not change any held-out identity.

Both train and full likelihoods are evaluated at the SAME training-only fitted
mean and calibration state. Conditional photometric Q=Qall-Qtrain and
relative logdet=logdetCall/Dall-logdetCtrain/Dtrain; no angular objective is
subtracted. This includes cross-night GP covariance. Plug-in chi-square screens
and20local parametric controls remain limited diagnostics, not coverage proof.

The exact original driver files/hashes are archived under
product/research/joint_campaign_drivers. The study's authoritative freeze,
independent partition and Schur-complement checks accompany the public audit
and full external campaign artifacts. This correction was prospective to all
prediction outcomes and did not select a partition by mass or prediction score.

Site references: [official LCO calendar](https://csp2.lco.cl/csp2/calendar/)
and [OGLE telescope information](https://ogle.astrouw.edu.pl/main/tel.html).
The official LCO west-longitude4h42m48s(-70.7degrees) gives the identical
held-out row set to the declared approximate coordinate; no score was used to
choose or adjust the boundary.
