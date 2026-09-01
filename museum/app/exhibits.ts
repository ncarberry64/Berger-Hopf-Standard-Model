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
    alt: 'A pulse travels from the BHSM action through its second, third, and fourth derivatives toward observable readouts.',
    seen: 'A pulse passes through S², S³, and S⁴: the structures used for propagation and interactions are obtained from one proposed action.',
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
    alt: 'Poles appear on a spectrum and a pulse passes through LSZ normalization into observable channels.',
    seen: 'Poles and residues emerge from the quadratic sector; shared vertices assemble an amplitude; a pulse crosses the inverse-free LSZ normalization step.',
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
    alt: 'A scan crosses a structural spectrum, revealing admissible bands, null windows, closed regions, and unresolved intervals.',
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
    alt: 'An electromagnetic vertex is projected into F1 and F2 structures, approaching the F2 at zero-momentum readout behind a gate.',
    seen: 'A supplied renormalized on-shell electromagnetic vertex resolves into F₁(q²) and F₂(q²), with the F₂(0) endpoint guarded.',
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
    alt: 'Two incoming particles converge on an amplitude block and separate into two outgoing final states.',
    seen: 'Two incoming particles meet at the shared amplitude block and separate into final states while thresholds, averages, and symmetry factors remain visible.',
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
    alt: 'Possible decay branches illuminate when allowed, remain crossed when forbidden, or stay dim when closed or unresolved.',
    seen: 'Allowed decay branches illuminate. Exactly forbidden branches remain crossed. Kinematically closed and unresolved cases retain separate labels.',
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
    alt: 'A firewall prevents measured values from changing upstream branches, coefficients, normalizations, modes, or scales.',
    seen: 'Measured values may enter only on the comparison side. They cannot select an upstream branch, action coefficient, mode, normalization, or scale.',
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
