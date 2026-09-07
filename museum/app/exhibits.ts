export const REPOSITORY =
  'https://github.com/ncarberry64/Berger-Hopf-Standard-Model';
export const SCIENCE = `${REPOSITORY}/blob/main`;
export const CURRENT_SCIENCE = `${REPOSITORY}/blob/d75e77bbdcfba79a83b9c9f9c8c398ae8e7a79d4`;

export type Exhibit = {
  number: string;
  title: string;
  subtitle: string;
  animated: string;
  still: string;
  alt: string;
  lay: string;
  seen: string;
  matters: string;
  dataLabel: string;
  status: 'implemented' | 'provisional' | 'gated';
  statusLabel: string;
  facts?: { label: string; value: string }[];
  links: { label: string; href: string }[];
};

export const exhibits: Exhibit[] = [
  {
    number: '01',
    title: 'CMS Open Data through the BHSM Engine',
    subtitle: '100,000 dimuon events · precision-gated coordinate validation',
    animated: 'pr98_cms_engine_validation_continuous.gif',
    still: 'pr98_cms_engine_validation.png',
    alt: 'Real CMS dimuon four-vectors move from a transverse-momentum view into a boundary-safe angular chart beside validation metrics.',
    lay: 'This display uses a verified sample of real collision data to check that the software can change coordinate descriptions without changing the underlying event.',
    seen: 'Each moving mark is derived from a real muon four-vector in the checked-in CMS sample. The left view encodes transverse momentum; the right view encodes angular coordinates after the BHSM Engine transformation. Color and motion preserve event identity rather than illustrating an invented trajectory.',
    matters:
      'This is coordinate-engine validation, not detector reconstruction, BHSM empirical validation, a physical prediction, or CERN/CMS endorsement. PR #98 processed 200,000 unique four-vectors and a two-million-vector timed workload while keeping scale-aware backward error below 2.4 machine epsilon.',
    dataLabel: 'Real CMS Open Data · BHSM Engine',
    status: 'implemented',
    statusLabel: 'Real-data engine validation',
    facts: [
      { label: 'CMS events', value: '100,000' },
      { label: 'Four-vectors', value: '200,000' },
      { label: 'Timed workload', value: '2,000,000' },
      { label: 'Control speedup', value: '3.225×' },
      { label: 'Maximum delta', value: '5.821×10⁻¹¹' },
      { label: 'License', value: 'CC0' },
    ],
    links: [
      {
        label: 'CMS Open Data Record 303',
        href: 'https://opendata.cern.ch/record/303',
      },
      {
        label: 'Animation data and method',
        href: `${SCIENCE}/docs/pr98_cms_open_data_animation.md`,
      },
      {
        label: 'Pinned source manifest',
        href: `${SCIENCE}/data/manifests/cms_open_data_dimuon_2010.json`,
      },
      {
        label: 'Display sample manifest',
        href: `${SCIENCE}/docs/assets/pr98_cms_open_data_animation/pr98_cms_sample_manifest.json`,
      },
      {
        label: 'Benchmark result',
        href: `${SCIENCE}/artifacts/cern_open_data_benchmark/results.json`,
      },
      {
        label: 'Benchmark tests',
        href: `${SCIENCE}/tests/test_cern_open_data_benchmark.py`,
      },
    ],
  },
  {
    number: '02',
    title: 'From action to calculation',
    subtitle: 'The shared mathematical source',
    animated: 'bhsm_geometry_to_prediction_animated.gif',
    still: 'bhsm_geometry_to_prediction.png',
    alt: 'A simulated sample moves across a normalized action landscape while second-, third-, and fourth-derivative traces update beside it.',
    lay: 'Think of one mathematical landscape examined at different levels of detail: its shape supplies the rules for motion and interaction instead of using a separate formula for each result.',
    seen: 'A simulated sample moves across one normalized action landscape while S², S³, and S⁴ traces update from the same sample position.',
    matters:
      'For a general reader, this is the project’s one-source rule: the displayed observables are meant to share a mathematical origin. Scientifically, it makes each pole, vertex, and amplitude traceable to the same action instead of to separately selected formulas.',
    dataLabel: 'Explanatory simulation · repository-derived structure',
    status: 'implemented',
    statusLabel: 'Implemented machinery',
    links: [
      {
        label: 'Action expansion source',
        href: `${SCIENCE}/src/bhsm/interface/universal_physical_action_expansion.py`,
      },
      {
        label: 'Focused tests',
        href: `${SCIENCE}/tests/test_universal_physical_action_expansion.py`,
      },
      {
        label: 'Current action attachment',
        href: `${SCIENCE}/theory/bhsm_current_full_field_action_attachment.md`,
      },
    ],
  },
  {
    number: '04',
    title: 'Spectral forecast',
    subtitle: 'Animated bands, uncertainty envelopes, and null windows',
    animated: 'bhsm_spectral_forecast_animated.gif',
    still: 'bhsm_spectral_forecast.png',
    alt: 'A scanning cursor reveals admissible bands, null windows, closed regions, and unresolved intervals across a normalized structural spectrum.',
    lay: 'Like scanning radio frequencies, the engine checks each region and records whether a signal is mathematically allowed, absent, blocked, or still uncertain.',
    seen: 'A scan separates admissible intervals, spectral null windows, closed regions, and unresolved regions on a normalized structural coordinate.',
    matters:
      'This view makes uncertainty part of the result rather than hiding it behind a single point. The classifier can distinguish admissible, absent, and unresolved regions without converting a structural interval into a particle mass or discovery claim.',
    dataLabel: 'Explanatory simulation · repository-derived interval classes',
    status: 'provisional',
    statusLabel: 'Structural and provisional',
    links: [
      {
        label: 'Forecast source',
        href: `${SCIENCE}/src/bhsm/interface/universal_spectral_forecast.py`,
      },
      {
        label: 'Focused tests',
        href: `${SCIENCE}/tests/test_universal_spectral_forecast.py`,
      },
      {
        label: 'Claim policy',
        href: `${SCIENCE}/docs/artifact_backed_claim_policy.md`,
      },
    ],
  },
  {
    number: '05',
    title: 'Magnetic-moment projection',
    subtitle: 'Resolving F₁ and F₂',
    animated: 'bhsm_muon_g2_pipeline_animated.gif',
    still: 'bhsm_muon_g2_pipeline.png',
    alt: 'Normalized F1 and F2 curves are sampled by a cursor approaching zero momentum, where the F2 at zero readout remains gated.',
    lay: 'The software separates one electromagnetic calculation into two curves; the second curve at zero momentum is needed for a magnetic-moment calculation, but no BHSM number is claimed yet.',
    seen: 'Normalized F₁(q²) and F₂(q²) curves are sampled as a cursor approaches zero momentum, with the F₂(0) endpoint visibly guarded.',
    matters:
      'In everyday terms, the machinery knows where a magnetic-moment correction would be read. Scientifically, the projection is basis-independent, but no BHSM muon g−2 number is promoted until enclosure, external-state, Ward-identity, and renormalization requirements all pass.',
    dataLabel: 'Explanatory simulation · analytic projection · result gated',
    status: 'gated',
    statusLabel: 'Implemented · numerical output gated',
    links: [
      {
        label: 'Form-factor source',
        href: `${SCIENCE}/src/bhsm/interface/universal_precision_form_factor.py`,
      },
      {
        label: 'Focused tests',
        href: `${SCIENCE}/tests/test_universal_precision_form_factor.py`,
      },
      {
        label: 'Frozen prediction policy',
        href: `${SCIENCE}/docs/frozen_predictions.md`,
      },
    ],
  },
  {
    number: '06',
    title: 'Collision readout',
    subtitle: 'Incoming states to final states',
    animated: 'bhsm_collision_predictor_animated.gif',
    still: 'bhsm_collision_predictor.png',
    alt: 'A simulated event display shows two incoming tracks meeting at a central vertex and two outgoing tracks separating while kinematic checks update.',
    lay: 'Two simulated particles meet, interact, and leave in new directions while the engine checks whether the event bookkeeping is internally consistent.',
    seen: 'Two incoming tracks converge on a shared amplitude vertex and two final-state tracks separate while normalized threshold, balance, average, and symmetry monitors remain visible.',
    matters:
      'This is the familiar collider question—what can go in, what can come out, and with what probability—shown as an implemented calculation path. It does not display a BHSM cross-section value or claim collider readiness.',
    dataLabel: 'Explanatory event simulation · action-derived engine topology',
    status: 'gated',
    statusLabel: 'Implemented · collider claim gated',
    links: [
      {
        label: 'Decay/collision source',
        href: `${SCIENCE}/src/bhsm/interface/universal_decay_collision.py`,
      },
      {
        label: 'Hadronic bridge',
        href: `${SCIENCE}/src/bhsm/interface/universal_hadronic_factorization.py`,
      },
      {
        label: 'Focused tests',
        href: `${SCIENCE}/tests/test_universal_decay_collision.py`,
      },
    ],
  },
  {
    number: '07',
    title: 'Decay and stability',
    subtitle: 'Allowed, forbidden, closed, unresolved',
    animated: 'bhsm_decay_stability_engine_animated.gif',
    still: 'bhsm_decay_stability_engine.png',
    alt: 'A radial channel monitor pulses along allowed decays, crosses forbidden channels, and separately labels closed and unresolved channels.',
    lay: 'The engine checks every way a state might break apart. A bright channel is available, a cross means forbidden, and closed or uncertain channels are kept separate.',
    seen: 'Pulses travel along allowed channels. Exactly forbidden channels remain crossed, while closed and unresolved cases retain distinct colors and ledger entries.',
    matters:
      'A long-lived-looking state is not automatically stable. The scientific claim requires a complete action-derived ledger showing that every possible decay route is either kinematically closed or exactly forbidden.',
    dataLabel: 'Explanatory simulation · repository-derived channel classes',
    status: 'gated',
    statusLabel: 'Implemented · physical instance gated',
    links: [
      {
        label: 'Channel ledger source',
        href: `${SCIENCE}/src/bhsm/interface/universal_channel_ledger.py`,
      },
      {
        label: 'Phase-space source',
        href: `${SCIENCE}/src/bhsm/interface/universal_decay_collision.py`,
      },
      {
        label: 'Focused tests',
        href: `${SCIENCE}/tests/test_universal_channel_ledger.py`,
      },
    ],
  },
  {
    number: '08',
    title: 'The no-fit firewall',
    subtitle: 'Computed BHSM residuals and immutable provenance',
    animated: 'bhsm_no_fit_firewall_animated.gif',
    still: 'bhsm_no_fit_firewall.png',
    alt: 'The existing residual monitor scans 370 certified local numerical residual bounds from BHSM, alongside the source revision, array hash, precision, and open physical-completion status.',
    lay: 'Measurements may grade the finished answer, but they are not allowed to go backward and quietly change the choices that produced it.',
    seen: 'The monitor now reads actual BHSM calculation data: 370 upper bounds on the local projected Hilbert–Schmidt second residual, from the frozen central scalar certificate. The cursor selects saved interval values. These are numerical residual bounds, not differences between predictions and measurements.',
    matters:
      'For any reader, the rule is simple: the answer cannot be adjusted after it is known. Scientifically, immutable provenance separates a frozen prediction from a post-hoc fit and forces incomplete records to fail closed.',
    dataLabel: 'Computed BHSM data · 512-bit scalar certificate',
    status: 'implemented',
    statusLabel: 'Real calculation data installed',
    links: [
      { label: 'Engine input data', href: './data/gate7-scalar-response.json' },
      {
        label: 'Pinned source certificate',
        href: `${CURRENT_SCIENCE}/artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_CAUSAL_COMPOSITION.json`,
      },
      {
        label: 'Prediction-freeze source',
        href: `${SCIENCE}/src/bhsm/interface/universal_prediction_freeze.py`,
      },
      {
        label: 'Integrity audit',
        href: `${SCIENCE}/tools/audit_frozen_prediction_integrity.py`,
      },
      { label: 'Claim boundaries', href: `${SCIENCE}/CLAIMS.md` },
    ],
  },
];

export const cosmologyExhibit: Exhibit = {
  number: 'OW-01',
  title: 'A Hyperspherical Scalar-Topographic Framework',
  subtitle:
    'Other work · late-time cosmological anomalies · January 2026 preprint',
  animated: 'cosmology_hyperspherical_scalar_topography_animated.gif',
  still: 'cosmology_hyperspherical_scalar_topography.png',
  alt: 'A schematic hyperspherical scalar mode changes directional distance rings while a synchronized redshift cursor samples BAO, supernova, and overlap kernels.',
  lay: 'This separate cosmology paper asks whether one very large, smooth variation across a curved Universe could leave related fingerprints in galaxy-distance measurements, supernova directions, and the measured expansion rate.',
  seen: 'The colored hypersphere represents the paper’s proposed long-wavelength scalar mode. Its changing direction slightly stretches and compresses the white distance rings. At right, one moving redshift cursor samples the BAO, supernova, and shared-overlap response curves together.',
  matters:
    'The preprint proposes a common late-time origin for several reported cosmological anomalies and identifies observations that could rule it out. It reports qualitative and order-of-magnitude consistency rather than a full likelihood analysis; the scalar field’s microphysical origin and a full perturbation treatment remain open.',
  dataLabel: 'Schematic preprint model · not observational data',
  status: 'provisional',
  statusLabel: 'Independent preprint · not peer reviewed',
  facts: [
    { label: 'Posted', value: '20 January 2026' },
    { label: 'Geometry', value: 'S³(R_H)' },
    { label: 'Reported bound', value: 'R_H ≳ 24 Gpc' },
    { label: 'Comparison level', value: 'Order of magnitude' },
  ],
  links: [
    {
      label: 'Read the cosmology preprint',
      href: 'https://doi.org/10.20944/preprints202601.1427.v1',
    },
    { label: 'Creator ORCID', href: 'https://orcid.org/0009-0000-6650-3485' },
  ],
};
