export const REPOSITORY =
  'https://github.com/ncarberry64/Berger-Hopf-Standard-Model';
export const SCIENCE = `${REPOSITORY}/blob/main`;

export type Exhibit = {
  number: string;
  title: string;
  subtitle: string;
  animated: string;
  still: string;
  alt: string;
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
    seen:
      'Each moving mark is derived from a real muon four-vector in the checked-in CMS sample. The left view encodes transverse momentum; the right view encodes angular coordinates after the BHSM Engine transformation. Color and motion preserve event identity rather than illustrating an invented trajectory.',
    matters:
      'This is an engineering validation on public collider data, not a claim that CMS confirms BHSM. PR #98 processed 200,000 unique four-vectors and a two-million-vector timed workload while keeping scale-aware backward error below 2.4 machine epsilon.',
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
      { label: 'CMS Open Data Record 303', href: 'https://opendata.cern.ch/record/303' },
      { label: 'Animation data and method', href: `${SCIENCE}/docs/pr98_cms_open_data_animation.md` },
      { label: 'Pinned source manifest', href: `${SCIENCE}/data/manifests/cms_open_data_dimuon_2010.json` },
    ],
  },
  {
    number: '02',
    title: 'From action to calculation',
    subtitle: 'The shared mathematical source',
    animated: 'bhsm_geometry_to_prediction_animated.gif',
    still: 'bhsm_geometry_to_prediction.png',
    alt: 'A pulse travels from the BHSM action through its second, third, and fourth derivatives toward observable readouts.',
    seen:
      'A single signal leaves the proposed BHSM action and passes through S², S³, and S⁴. These derivatives supply the quadratic propagation terms and the cubic and quartic interaction terms used downstream.',
    matters:
      'For a general reader, this is the project’s one-source rule: the displayed observables are meant to share a mathematical origin. Scientifically, it makes each pole, vertex, and amplitude traceable to the same action instead of to separately selected formulas.',
    dataLabel: 'Repository-derived structural record',
    status: 'implemented',
    statusLabel: 'Implemented machinery',
    links: [
      { label: 'Action expansion source', href: `${SCIENCE}/src/bhsm/interface/universal_physical_action_expansion.py` },
      { label: 'Focused tests', href: `${SCIENCE}/tests/test_universal_physical_action_expansion.py` },
      { label: 'Current action attachment', href: `${SCIENCE}/theory/bhsm_current_full_field_action_attachment.md` },
    ],
  },
  {
    number: '03',
    title: 'Simulated particle spectrum',
    subtitle: 'Temporary museum dataset · dimensionless coordinate',
    animated: 'bhsm_simulated_particle_spectrum_animated.gif',
    still: 'bhsm_simulated_particle_spectrum.png',
    alt: 'Simulated lepton, gauge, and quark-family markers rise from a dimensionless BHSM-style spectrum while a scan line crosses the plot.',
    seen:
      'Lepton, gauge, and quark rows use familiar particle labels as orientation anchors. Marker position and height come from a deterministic museum simulation on a dimensionless display axis; the scan reveals the dataset without assigning a physical mass.',
    matters:
      'The temporary spectrum restores the visual vocabulary needed to discuss families and modes while preserving the scientific boundary. It is not a rebuilt BHSM spectrum, a fit to measured masses, or a prediction of new particles; it can later be replaced by an action-owned physical artifact.',
    dataLabel: 'Simulated display data · not a prediction',
    status: 'provisional',
    statusLabel: 'Simulated spectrum installed',
    facts: [
      { label: 'Display modes', value: '9' },
      { label: 'Families', value: '3' },
      { label: 'Coordinate', value: 'ξ ∈ [0,1]' },
      { label: 'Mass scale', value: 'Not assigned' },
    ],
    links: [
      { label: 'Simulated display dataset', href: `${SCIENCE}/data/museum/bhsm_simulated_particle_spectrum_v1.json` },
      { label: 'Spectrum implementation', href: `${SCIENCE}/src/bhsm/interface/universal_quadratic_spectrum.py` },
      { label: 'Claim policy', href: `${SCIENCE}/docs/artifact_backed_claim_policy.md` },
    ],
  },
  {
    number: '04',
    title: 'Spectral forecast',
    subtitle: 'Animated bands, uncertainty envelopes, and null windows',
    animated: 'bhsm_spectral_forecast_animated.gif',
    still: 'bhsm_spectral_forecast.png',
    alt: 'A scan line moves across normalized spectral bands with uncertainty envelopes, a null window, and an unresolved region.',
    seen:
      'Horizontal bands show interval-valued mode classes on a normalized spectral coordinate. Thin outer envelopes represent uncertainty or incomplete localization, the hatched red interval is a null window, and the moving scan line reads the classification at each coordinate.',
    matters:
      'This view makes uncertainty part of the result rather than hiding it behind a single point. The classifier can distinguish admissible, absent, and unresolved regions without converting a structural interval into a particle mass or discovery claim.',
    dataLabel: 'Repository-derived interval classes',
    status: 'provisional',
    statusLabel: 'Structural and provisional',
    links: [
      { label: 'Forecast source', href: `${SCIENCE}/src/bhsm/interface/universal_spectral_forecast.py` },
      { label: 'Focused tests', href: `${SCIENCE}/tests/test_universal_spectral_forecast.py` },
      { label: 'Claim policy', href: `${SCIENCE}/docs/artifact_backed_claim_policy.md` },
    ],
  },
  {
    number: '05',
    title: 'Magnetic-moment projection',
    subtitle: 'Resolving F₁ and F₂',
    animated: 'bhsm_muon_g2_pipeline_animated.gif',
    still: 'bhsm_muon_g2_pipeline.png',
    alt: 'An electromagnetic vertex is projected into F1 and F2 structures, approaching the F2 at zero-momentum readout behind a gate.',
    seen:
      'The display decomposes a supplied renormalized on-shell electromagnetic vertex into the charge form factor F₁(q²) and magnetic form factor F₂(q²). The animation approaches q² = 0 while leaving the numerical endpoint behind an explicit gate.',
    matters:
      'In everyday terms, the machinery knows where a magnetic-moment correction would be read. Scientifically, the projection is basis-independent, but no BHSM muon g−2 number is promoted until enclosure, external-state, Ward-identity, and renormalization requirements all pass.',
    dataLabel: 'Analytic projection · numerical result gated',
    status: 'gated',
    statusLabel: 'Implemented · numerical output gated',
    links: [
      { label: 'Form-factor source', href: `${SCIENCE}/src/bhsm/interface/universal_precision_form_factor.py` },
      { label: 'Focused tests', href: `${SCIENCE}/tests/test_universal_precision_form_factor.py` },
      { label: 'Frozen prediction policy', href: `${SCIENCE}/docs/frozen_predictions.md` },
    ],
  },
  {
    number: '06',
    title: 'Collision readout',
    subtitle: 'Incoming states to final states',
    animated: 'bhsm_collision_predictor_animated.gif',
    still: 'bhsm_collision_predictor.png',
    alt: 'Two incoming particles converge on a shared amplitude calculation and separate into two outgoing final states.',
    seen:
      'Two incoming states enter the shared interaction calculation and emerge as a two-body final state. The moving marks track the calculation through contact and exchange contributions, squared amplitude, angular distribution, and integrated cross-section readout.',
    matters:
      'This is the familiar collider question—what can go in, what can come out, and with what probability—shown as an implemented calculation path. It does not display a BHSM cross-section value or claim collider readiness.',
    dataLabel: 'Action-derived engine topology',
    status: 'gated',
    statusLabel: 'Implemented · collider claim gated',
    links: [
      { label: 'Decay/collision source', href: `${SCIENCE}/src/bhsm/interface/universal_decay_collision.py` },
      { label: 'Hadronic bridge', href: `${SCIENCE}/src/bhsm/interface/universal_hadronic_factorization.py` },
      { label: 'Focused tests', href: `${SCIENCE}/tests/test_universal_decay_collision.py` },
    ],
  },
  {
    number: '07',
    title: 'Decay and stability',
    subtitle: 'Allowed, forbidden, closed, unresolved',
    animated: 'bhsm_decay_stability_engine_animated.gif',
    still: 'bhsm_decay_stability_engine.png',
    alt: 'Possible decay branches illuminate when allowed and remain distinct when forbidden, closed, or unresolved.',
    seen:
      'The candidate state is tested against four distinct channel outcomes. Allowed branches contribute to the total width; exact selection rules set a branch to zero; thresholds can close it; incomplete interval information keeps it unresolved.',
    matters:
      'A long-lived-looking state is not automatically stable. The scientific claim requires a complete action-derived ledger showing that every possible decay route is either kinematically closed or exactly forbidden.',
    dataLabel: 'Repository-derived channel ledger classes',
    status: 'gated',
    statusLabel: 'Implemented · physical instance gated',
    links: [
      { label: 'Channel ledger source', href: `${SCIENCE}/src/bhsm/interface/universal_channel_ledger.py` },
      { label: 'Phase-space source', href: `${SCIENCE}/src/bhsm/interface/universal_decay_collision.py` },
      { label: 'Focused tests', href: `${SCIENCE}/tests/test_universal_channel_ledger.py` },
    ],
  },
  {
    number: '08',
    title: 'The no-fit firewall',
    subtitle: 'Prediction authority and provenance',
    animated: 'bhsm_no_fit_firewall_animated.gif',
    still: 'bhsm_no_fit_firewall.png',
    alt: 'A firewall prevents measured values from changing upstream branches, coefficients, normalizations, modes, or scales.',
    seen:
      'Measured values remain on the comparison side of the display. The firewall blocks them from choosing the action branch, coefficient, mode, normalization, formula, or scale that generated the candidate prediction.',
    matters:
      'For any reader, the rule is simple: the answer cannot be adjusted after it is known. Scientifically, immutable provenance separates a frozen prediction from a post-hoc fit and forces incomplete records to fail closed.',
    dataLabel: 'Repository policy and provenance checks',
    status: 'implemented',
    statusLabel: 'Implemented policy machinery',
    links: [
      { label: 'Prediction-freeze source', href: `${SCIENCE}/src/bhsm/interface/universal_prediction_freeze.py` },
      { label: 'Integrity audit', href: `${SCIENCE}/tools/audit_frozen_prediction_integrity.py` },
      { label: 'Claim boundaries', href: `${SCIENCE}/CLAIMS.md` },
    ],
  },
  {
    number: '09',
    title: 'The physical identification bridge',
    subtitle: 'Moving state space · six-class AE2 carrier audit',
    animated: 'bhsm_physical_identification_bridge_animated.gif',
    still: 'bhsm_physical_identification_bridge.png',
    alt: 'Three reused BHSM state trajectories move through event-child state space beside a six-by-five audit matrix in which none of the unchanged AE2 candidates qualifies as a local enclosure carrier.',
    seen:
      'Colored trajectories carry a reused BHSM family, mode, and current through the certified event-child state space. The matrix tests six stored AE2 candidates against five carrier requirements: action ownership, local-domain selection, an embedded surface, regularity, and interface variation. Green cells are available properties; no row has all five.',
    matters:
      'For any reader, reaching an event is not the same as forming a place in spacetime. Scientifically, the audit shows that λ₂₄ selects event time but does not define the embedded enclosure surface. An existing family or mode and its reset matching remain reusable, while a future action version would need an owner-approved covariant localization carrier.',
    dataLabel: 'Unchanged AE2 audit · 6 candidates · 0 qualifying carriers',
    status: 'gated',
    statusLabel: 'Carrier audit complete · extension decision open',
    facts: [
      { label: 'Candidates audited', value: '6' },
      { label: 'Carrier requirements', value: '5' },
      { label: 'Qualifying carriers', value: '0' },
      { label: 'Reduced kernels', value: '4' },
      { label: 'Reusable subclosures', value: '2' },
      { label: 'Action change made', value: 'No' },
    ],
    links: [
      { label: 'Full ontology reconstruction', href: `${SCIENCE}/docs/BHSM_NORMAN_SCHOOL_FULL_CORPUS_RECONSTRUCTION.md` },
      { label: 'Localization carrier kill screen', href: `${SCIENCE}/theory/n12_gate7_localization_carrier_kill_screen.md` },
      { label: 'Bridge theorem interface', href: `${SCIENCE}/theory/n12_gate7_physical_encapsulation_identification_bridge.md` },
      { label: 'Future extension acceptance contract', href: `${SCIENCE}/theory/post_ae2_localization_carrier_extension_contract.md` },
    ],
  },
];
