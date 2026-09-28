import { slides } from './museum-slides.mjs';

export const museumUrl =
  'https://ncarberry64.github.io/Berger-Hopf-Standard-Model/';
const repository = 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model';
const raw =
  'https://raw.githubusercontent.com/ncarberry64/Berger-Hopf-Standard-Model/main/';
const local = (path) => new URL(path, museumUrl).href;
const source = (title, path) => ({ title, url: local(path) });
const repoSource = (title, path) => ({ title, url: raw + path });

export const readingRules = [
  'This is a navigation index, not a new scientific result or a live computation service.',
  'Read the linked source before answering; cite its URL, revision or snapshot date and scope. If it cannot be read, say so.',
  'Separate established reference physics, BHSM propositions, conditional results, historical numerical screens and action-derived physical predictions. A visual analogy or numerical match is not a physical derivation.',
  'Museum downloads are dated snapshots. Check the current repository status for later work; do not silently combine results from different revisions.',
  'Preserve open dependencies and missing values. Kinematic admissibility does not supply a transition probability, cross section or lifetime.',
  'Use the existing definition of done and gate ledger for completion questions. Do not invent additional completion gates.',
];
export const currentSources = [
  repoSource(
    'Current research status (main; may change)',
    'docs/current_bhsm_status.md',
  ),
  repoSource('Claim boundaries', 'CLAIMS.md'),
  repoSource(
    'Existing definition of done',
    'docs/BHSM_1_0_DEFINITION_OF_DONE.md',
  ),
  repoSource('Existing gate ledger', 'theory/gate_ledger.md'),
];

// Curated retrieval descriptions, not automatically generated scientific answers.
const topics = {
  potential: {
    keywords:
      'welcome children hypersphere topology modes harmonics moire geometry standard model particles quarks leptons bosons atoms hydrogen carbon molecules structures scales',
    summary:
      'Children of BHSM connects proposed core/topology, modes and geometry to established particle families and larger structures. Selectable illustrations include orbital densities, molecules, matter phases and cosmic structures.',
    scope:
      'The foundational connections are BHSM propositions. Animations are schematic; established categories do not validate those connections.',
    sources: [
      source('Established science collection', 'data/science-collection.json'),
      currentSources[1],
    ],
  },
  'berger-hopf': {
    keywords:
      'berger hopf sphere squashing fibers fibration geometry spectrum charge unification',
    summary:
      'The Berger & Hopf animation introduces deformation of the sphere and linked Hopf fibers, then places their combination within the proposed BHSM framework.',
    scope:
      'Mathematical geometry is distinguished from the open physical identification of the model.',
    sources: [currentSources[1], repoSource('Framework overview', 'README.md')],
  },
  'science-unification': {
    keywords:
      'forces strong weak electromagnetic electromagnetism gravity aether spacetime fine structure constant fsc origin',
    summary:
      'Five geometric force studies and the force-line diagram illustrate the supplied BHSM interpretation of strong cohesion, limited electromagnetic surface availability, weak decay, gravity and a common hyperspherical origin. The core describes Aether as a lack of spacetime support.',
    scope:
      'Qualitative BHSM interpretation, without calibrated force strengths or action-derived interaction rates.',
    sources: [
      currentSources[1],
      source(
        'Exhibit scope and provenance',
        'research/museum-update-record.json',
      ),
    ],
  },
  'science-predictions': {
    keywords:
      'matter particles mass masses spectrum standard model generations yukawa mixing neutrino ledger',
    summary:
      'Explore the particle ledger, conditional structural framework and the distinction between reference properties and proposed BHSM calculations.',
    scope:
      'Conditional structural results and historical screens do not establish physical masses or mixing predictions.',
    sources: [
      source('Science collection', 'data/science-collection.json'),
      repoSource(
        'Mass and mixing dependency audit',
        'docs/BHSM_MASS_MIXING_DEPENDENCY_AUDIT_2026_09_07.md',
      ),
      currentSources[0],
    ],
  },
  'science-magnetic': {
    keywords: 'magnetism magnetic moments muon electron g2 g-2 anomaly',
    summary:
      'Magnetic-moment animations accompany conventional reference measurements and the proposed route to BHSM calculations.',
    scope:
      'Reference values are edition-labeled measurements; BHSM magnetic predictions remain gated in the displayed record.',
    sources: [
      source('Experimental references', 'data/reference-data.json'),
      currentSources[0],
    ],
  },
  'science-decays': {
    keywords:
      'collision collisions decay decays transition incoming envelopes boundary imbalance admissible branches observables cross sections lifetime scattering',
    summary:
      'Collision theatre provides kinematic scenarios and a BHSM Transition Diagram: incoming envelopes, active boundary imbalance, admissible-branch screens and observable slots. The interactive exhibit can export its selected transition record.',
    scope:
      'Kinematic screens are necessary checks, not a complete dynamics calculation. Missing boundary inputs, rates and probabilities remain explicitly uncomputed.',
    sources: [
      repoSource(
        'Transition record implementation and source references',
        'museum/lib/bhsm-transition.ts',
      ),
      source('CMS sample four-vectors', 'data/cms-four-vector-sample.json'),
      currentSources[0],
    ],
  },
  'cosmology-original': {
    keywords:
      'cosmology original january cosmic cycle hypersphere light proposal universe expansion',
    summary:
      'The original cosmology exhibit animates the January geometric proposal, from light and cosmic structure to a proposed cosmic cycle.',
    scope:
      'Historical conceptual illustration, not a sky map, current numerical fit or demonstrated physical cosmic cycle.',
    sources: [
      {
        title: 'Original January preprint',
        url: 'https://doi.org/10.20944/preprints202601.1427.v1',
      },
      source('Snapshot provenance', 'research/museum-update-record.json'),
    ],
  },
  'other-work': {
    keywords:
      'cosmology testable response r1 environment topography supernova sightline bao laniakea great attractor cosmic web',
    summary:
      'The later cosmology exhibit presents the R1 environment-to-topography response, numerical replay, sightline study and observational-test prerequisites.',
    scope:
      'Read the integration receipt and limitations with the replay. Missing profile selection, normalization and observational prerequisites are not closed by an animation.',
    sources: [
      source(
        'R1 numerical replay',
        'research/r1-coupled-environment-replay.json',
      ),
      source('R1 validation snapshot', 'research/r1-integration-receipt.json'),
      source(
        'Sightline results and limitations',
        'research/sn-sightline-report.md',
      ),
      source(
        'Observational prerequisites',
        'research/cosmology-test-prerequisites.md',
      ),
    ],
  },
  'science-test': {
    keywords:
      'comparisons reference data historical screens mass coupling error codata pdg sandbox',
    summary:
      'Compare historical BHSM screens with published reference data, retaining assumptions, editions and qualifications.',
    scope:
      'COMPARISON_ONLY. Matching a reference number does not turn a historical screen into an independently selected prediction.',
    sources: [
      source('Historical comparison snapshot', 'data/sandbox-comparison.json'),
      source(
        'Edition-labeled experimental references',
        'data/reference-data.json',
      ),
    ],
  },
  'research-exhibit': {
    keywords:
      'cms data research gate7 gate-7 force root hessian persistence certificate tube remainder numerical incoming history',
    summary:
      'CMS visualization and the numerical research displays provide measured four-vector samples, scoped engine validation and dated Gate-7 numerical certificates.',
    scope:
      'Engine validation and local numerical certificates do not close all Gate-7 obligations or establish physical observables. Consult the existing obligations and current status.',
    sources: [
      source('CMS sample', 'data/cms-four-vector-sample.json'),
      source(
        'Certificate provenance and hashes',
        'research/museum-update-record.json',
      ),
      source('Physical-tube scope', 'research/bhsm-physical-tube.md'),
      currentSources[0],
      currentSources[2],
      currentSources[3],
    ],
  },
  details: {
    keywords:
      'evidence predictive predictions completion obligations open questions derivation falsifiability tests assumptions status',
    summary:
      'The evidence exhibit describes the path from geometry through calculations to predictive tests, with links to assumptions, current status and reproducible institutional setup.',
    scope:
      'Use the current claim boundaries and existing completion obligations; museum summaries do not supersede the scientific record.',
    sources: [
      ...currentSources,
      repoSource(
        'Institutional reproduction guide',
        'docs/INSTITUTIONAL_START.md',
      ),
    ],
  },
  creator: {
    keywords:
      'citation author creator carberry berger hopf scientific record archive preprint orcid credit doi',
    summary:
      'Find citation metadata, archival records and the frozen preprint.',
    scope:
      'Archive versions preserve their historical scope; consult current status before describing a result as complete.',
    sources: [
      repoSource('Citation metadata', 'CITATION.cff'),
      { title: 'Archival DOI', url: 'https://doi.org/10.5281/zenodo.20663419' },
    ],
  },
  'museum-exit': {
    keywords:
      'sources links ai assistant access guide json download license music soundtrack',
    summary:
      'Sources, soundtrack controls and AI access. Visitors can copy a JSON context packet linking their own AI assistant to the BHSM GitHub scientific record.',
    scope:
      'Read-only static retrieval. No hosted language model, API key, account or server-side question processing.',
    sources: [
      source('AI-readable guide', 'llms.txt'),
      source('Structured exhibit index', 'ai/index.json'),
      repoSource('License', 'LICENSE.md'),
    ],
  },
};

export const catalog = {
  schema_version: '1.0',
  title: 'BHSM Museum AI navigation index',
  updated: '2026-09-28',
  museum_url: museumUrl,
  repository_url: repository,
  guide_url: local('llms.txt'),
  access: {
    method: 'GET',
    authentication: 'none',
    format: 'static JSON and Markdown',
    javascript_required: false,
  },
  reading_rules: readingRules,
  current_sources: currentSources,
  exhibits: slides.map(([id, title]) => {
    if (!topics[id]) throw new Error(`Missing AI guide entry: ${id}`);
    return { id, title, url: `${museumUrl}#${id}`, ...topics[id] };
  }),
};

// A compact, provider-neutral context packet copied by the public AI button.
export const aiHandoff = {
  schema: 'bhsm-ai-handoff/v1',
  purpose:
    'Use the public BHSM GitHub scientific record to answer my questions about the Berger–Hopf Standard Model.',
  repository: {
    url: repository,
    branch: 'main',
    raw_base_url: raw,
    freshness:
      'Read the current files when answering. Record the revision or access date; do not assume the museum snapshot is the newest research.',
  },
  start_here: currentSources,
  navigation: {
    overview: raw + 'README.md',
    reproduction: raw + 'docs/INSTITUTIONAL_START.md',
    citation: raw + 'CITATION.cff',
    museum: museumUrl,
    exhibit_index: local('ai/index.json'),
    readable_guide: local('llms.txt'),
  },
  answer_guidance: readingRules,
  capability_note:
    'Requires an assistant able to read public web or GitHub links. If unavailable, ask the user for the relevant source text instead of claiming to have read it.',
};
export const aiHandoffJSON = JSON.stringify(aiHandoff, null, 2);
