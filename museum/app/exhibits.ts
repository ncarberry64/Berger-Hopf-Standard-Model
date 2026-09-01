export const REPOSITORY =
  'https://github.com/ncarberry64/Berger-Hopf-Standard-Model';
export const SCIENCE = `${REPOSITORY}/blob/main`;
export const MUSEUM =
  'https://ncarberry64.github.io/Berger-Hopf-Standard-Model/';

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
  status: 'implemented' | 'provisional' | 'gated';
  statusLabel: string;
  links: { label: string; href: string }[];
};

export const cmsValidation = {
  title: 'Coordinate-engine validation—not a BHSM physics test',
  animated: 'pr98_cms_engine_validation_continuous.gif',
  still: 'pr98_cms_engine_validation.svg',
  alt: 'Checksum-pinned CMS Open Data dimuon four-vectors continuously transform between coordinate representations while invariant checks remain fixed.',
  lay: 'This display uses a small, verified sample of real collision data to check that the software can change coordinate descriptions without changing the underlying event.',
  seen: 'Real, checksum-pinned four-vectors from a compact CMS Open Data dimuon sample move through BHSM coordinate transformations. The motion shows the data representation changing while the engine checks invariants.',
  proves:
    'The tested software can ingest the pinned four-vectors and preserve the declared coordinate and invariant relationships at the documented benchmark scope.',
  doesNotProve:
    'It does not perform detector reconstruction, validate BHSM as particle physics, produce a BHSM prediction, or imply CERN/CMS endorsement.',
  links: [
    {
      label: 'CERN Open Data record 303',
      href: 'https://opendata.cern.ch/record/303',
    },
    {
      label: 'Generator source',
      href: `${SCIENCE}/docs/assets/pr98_cms_open_data_animation/generate_pr98_cms_animation.py`,
    },
    {
      label: 'Pinned sample manifest',
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
};

export const exhibits: Exhibit[] = [
  {
    number: '01',
    title: 'From action to calculation',
    subtitle: 'The shared mathematical source',
    animated: 'bhsm_geometry_to_prediction_animated.gif',
    still: 'bhsm_geometry_to_prediction.png',
    alt: 'A simulated sample moves across a normalized action landscape while second-, third-, and fourth-derivative traces update beside it.',
    lay: 'Think of one mathematical landscape being examined at different levels of detail: its shape supplies the rules for motion and interaction instead of using a separate formula for each result.',
    seen: 'A simulated sample moves across one normalized action landscape while S², S³, and S⁴ traces update from the same sample position.',
    matters:
      'The architecture is designed to prevent unrelated formulas from being chosen separately for each observable.',
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
    number: '02',
    title: 'The observable pipeline',
    subtitle: 'Poles, residues, vertices, and LSZ',
    animated: 'bhsm_universal_predictive_engine_animated.gif',
    still: 'bhsm_universal_predictive_engine.png',
    alt: 'A normalized response spectrum reveals four pole markers while an amplitude waveform runs through an inverse-free LSZ monitor.',
    lay: 'The peaks mark places where the mathematics can support a mode; the lower trace shows how those ingredients are prepared for a calculation that could later connect to an observable.',
    seen: 'Pole markers and residue strengths appear on a normalized response spectrum while a moving cursor samples the amplitude after the inverse-free LSZ step.',
    matters:
      'It exposes a reviewable chain from action-derived inputs to decay, collision, form-factor, and spectral readouts.',
    status: 'gated',
    statusLabel: 'Implemented · physical promotion gated',
    links: [
      {
        label: 'Spectrum source',
        href: `${SCIENCE}/src/bhsm/interface/universal_quadratic_spectrum.py`,
      },
      {
        label: 'Amplitude source',
        href: `${SCIENCE}/src/bhsm/interface/universal_vertex_amplitude.py`,
      },
      {
        label: 'LSZ source',
        href: `${SCIENCE}/src/bhsm/interface/universal_lsz.py`,
      },
    ],
  },
  {
    number: '03',
    title: 'Spectral forecast',
    subtitle: 'Allowed bands and null windows',
    animated: 'bhsm_spectral_forecast_animated.gif',
    still: 'bhsm_spectral_forecast.png',
    alt: 'A scanning cursor reveals admissible bands, null windows, closed regions, and unresolved intervals across a normalized structural spectrum.',
    lay: 'Like scanning radio frequencies, the engine checks each region and records whether a signal is mathematically allowed, absent, blocked, or still uncertain.',
    seen: 'A scan separates action-derived modes, admissible intervals, spectral null windows, closed channels, and unresolved regions.',
    matters:
      'The classifier can say “allowed,” “absent,” or “not resolved” without turning a structural calculation into a particle claim.',
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
    number: '04',
    title: 'Magnetic-moment projection',
    subtitle: 'Resolving F₁ and F₂',
    animated: 'bhsm_muon_g2_pipeline_animated.gif',
    still: 'bhsm_muon_g2_pipeline.png',
    alt: 'Normalized F1 and F2 curves are sampled by a cursor approaching zero momentum, where the F2 at zero readout remains gated.',
    lay: 'The software separates one electromagnetic calculation into two curves; the second curve at zero momentum is the piece needed for a magnetic-moment calculation, but no BHSM number is claimed yet.',
    seen: 'Normalized F₁(q²) and F₂(q²) curves are sampled as a cursor approaches zero momentum, with the F₂(0) endpoint visibly guarded.',
    matters:
      'The projection machinery exists, but no numerical BHSM muon g−2 value is displayed before all physical gates pass.',
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
    number: '05',
    title: 'Collision readout',
    subtitle: 'Incoming states to final states',
    animated: 'bhsm_collision_predictor_animated.gif',
    still: 'bhsm_collision_predictor.png',
    alt: 'A simulated event display shows two incoming tracks meeting at a central vertex and two outgoing tracks separating while kinematic checks update.',
    lay: 'Two simulated particles meet, interact, and leave in new directions while the engine checks whether the event bookkeeping is internally consistent.',
    seen: 'Two incoming tracks converge on a shared amplitude vertex and two final-state tracks separate while normalized threshold, balance, average, and symmetry monitors remain visible.',
    matters:
      'The animation shows an engine topology, not a cross-section value or a claim of collider readiness.',
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
    number: '06',
    title: 'Decay and stability',
    subtitle: 'Allowed, forbidden, closed, unresolved',
    animated: 'bhsm_decay_stability_engine_animated.gif',
    still: 'bhsm_decay_stability_engine.png',
    alt: 'A radial channel monitor pulses along allowed decays, crosses forbidden channels, and separately labels closed and unresolved channels.',
    lay: 'The engine checks every way a state might break apart. A bright channel is available, a cross means forbidden, and dim or uncertain channels are kept separate.',
    seen: 'Pulses travel along allowed channels. Exactly forbidden channels remain crossed, while closed and unresolved cases retain distinct colors and ledger entries.',
    matters:
      'A state is called stable only when a complete ledger proves that every decay route is closed or exactly forbidden.',
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
    number: '07',
    title: 'The no-fit firewall',
    subtitle: 'Prediction authority and provenance',
    animated: 'bhsm_no_fit_firewall_animated.gif',
    still: 'bhsm_no_fit_firewall.png',
    alt: 'A residual plot compares a frozen calculation with measurements while an immutable provenance monitor keeps branch, coefficients, normalization, and scale locked.',
    lay: 'Measurements may grade the finished answer, but they are not allowed to go backward and quietly change the choices that produced it.',
    seen: 'A comparison residual is scanned above a live provenance ledger. Branch, action coefficients, normalization, and scale remain locked while measurements enter only at comparison.',
    matters:
      'The firewall keeps a frozen prediction distinct from a post-hoc fit and fails closed when provenance is incomplete.',
    status: 'implemented',
    statusLabel: 'Implemented policy machinery',
    links: [
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
