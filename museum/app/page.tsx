'use client';

import { ArrowRight, Code2, Pause, Play, ShieldCheck } from 'lucide-react';
import Image from 'next/image';
import { useEffect, useMemo, useState } from 'react';
import { Button } from '@/components/ui/button';
import { exhibits, REPOSITORY, SCIENCE, type Exhibit } from './exhibits';

const ASSET_REVISION = 'simulation-engines-2026-09-01b';

const creatorLinks = [
  { label: 'ORCID record', href: 'https://orcid.org/0009-0000-6650-3485' },
  { label: 'Citation metadata', href: `${SCIENCE}/CITATION.cff` },
  { label: 'Frozen preprint PDF', href: `${SCIENCE}/manuscript/BHSM_final_paper.pdf` },
  { label: 'Archival DOI', href: 'https://doi.org/10.5281/zenodo.20663419' },
];

type CMSVector = {
  event_index: number;
  run: number;
  event: number;
  muon: number;
  E: number;
  px: number;
  py: number;
  pz: number;
  pt: number;
  eta: number;
  phi: number;
  charge: number;
};

function CMSExplorer() {
  const [vectors, setVectors] = useState<CMSVector[]>([]);
  const [selected, setSelected] = useState(0);

  useEffect(() => {
    fetch('./data/cms-four-vector-sample.json')
      .then(async (response) => {
        const payload = (await response.json()) as { vectors: CMSVector[] };
        setVectors(payload.vectors);
      })
      .catch(() => setVectors([]));
  }, []);

  const eventIndices = useMemo(
    () => [...new Set(vectors.map((vector) => vector.event_index))],
    [vectors],
  );
  const selectedEventIndex = eventIndices[selected];
  const eventVectors = useMemo(
    () => vectors.filter((vector) => vector.event_index === selectedEventIndex),
    [selectedEventIndex, vectors],
  );
  const event = eventVectors[0];
  const maxPt = Math.max(...eventVectors.map((vector) => vector.pt), 1);

  return (
    <section className="cms-explorer" id="cms-data" aria-labelledby="cms-explorer-title">
      <div className="cms-explorer-copy">
        <p className="eyebrow">BHSM Engine instrument · real CMS Open Data</p>
        <h2 id="cms-explorer-title">Inspect 64 dimuon events.</h2>
        <p>
          Choose one checked-in event and inspect both measured muon
          four-vectors. The circular instrument maps azimuth to angle, transverse
          momentum to radius, and charge to color. It is a BHSM-style rendering
          of CMS data—not a detector photograph, detector reconstruction,
          BHSM empirical validation, or CERN/CMS endorsement.
        </p>
        <label htmlFor="cms-event-selector">
          Sample event <strong>{selected + 1} / {eventIndices.length || 64}</strong>
        </label>
        <input
          id="cms-event-selector"
          type="range"
          min="0"
          max={Math.max(eventIndices.length - 1, 0)}
          value={selected}
          onChange={(eventChange) => setSelected(Number(eventChange.target.value))}
        />
        <div className="cms-event-identity">
          <span>Source row {event?.event_index ?? '—'}</span>
          <span>Run {event?.run ?? '—'}</span>
          <span>Event {event?.event ?? '—'}</span>
        </div>
        <div className="cms-field-links">
          <a href="https://opendata.cern.ch/record/303">CMS record ↗</a>
          <a href={`${SCIENCE}/docs/pr98_cms_open_data_animation.md`}>Method ↗</a>
        </div>
      </div>

      <div className="cms-event-instrument">
        <svg viewBox="0 0 320 320" aria-labelledby="cms-event-plot-title">
          <title id="cms-event-plot-title">Selected dimuon event in a polar momentum display</title>
          {[55, 95, 135].map((radius) => (
            <circle className="instrument-ring" cx="160" cy="160" r={radius} key={radius} />
          ))}
          <line className="instrument-axis" x1="20" x2="300" y1="160" y2="160" />
          <line className="instrument-axis" x1="160" x2="160" y1="20" y2="300" />
          {eventVectors.map((vector) => {
            const radius = 42 + (vector.pt / maxPt) * 92;
            const x = 160 + Math.cos(vector.phi) * radius;
            const y = 160 - Math.sin(vector.phi) * radius;
            return (
              <g className={vector.charge > 0 ? 'track-positive' : 'track-negative'} key={vector.muon}>
                <line x1="160" y1="160" x2={x} y2={y} />
                <circle cx={x} cy={y} r="8" />
                <text x={x + 12} y={y - 10}>μ{vector.charge > 0 ? '+' : '−'}</text>
              </g>
            );
          })}
          <circle className="instrument-origin" cx="160" cy="160" r="5" />
        </svg>
        <table className="cms-vector-table">
          <caption>Selected CMS muon four-vectors</caption>
          <thead>
            <tr className="cms-vector-row cms-vector-head">
              <th>Muon</th><th>E</th><th>pT</th><th>η</th><th>φ</th>
            </tr>
          </thead>
          <tbody>
            {eventVectors.map((vector) => (
              <tr className="cms-vector-row" key={vector.muon}>
                <th>μ{vector.charge > 0 ? '+' : '−'}</th>
                <td>{vector.E.toFixed(3)}</td>
                <td>{vector.pt.toFixed(3)}</td>
                <td>{vector.eta.toFixed(3)}</td>
                <td>{vector.phi.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="instrument-caption">Energy and momentum in GeV · η and φ dimensionless/radians · two source vectors per event</p>
      </div>
    </section>
  );
}

function StatusBadge({ exhibit }: { exhibit: Exhibit }) {
  return (
    <span className={`status status-${exhibit.status}`}>
      <ShieldCheck aria-hidden="true" size={15} /> {exhibit.statusLabel}
    </span>
  );
}

function MotionImage({
  motion,
  exhibit,
  priority = false,
  loading,
}: {
  motion: boolean;
  exhibit: Exhibit;
  priority?: boolean;
  loading?: 'eager' | 'lazy';
}) {
  const desired = motion ? exhibit.animated : exhibit.still;
  const [failedSource, setFailedSource] = useState<string | null>(null);
  const source = failedSource === desired ? exhibit.still : desired;

  return (
    <Image
      src={`./exhibits/${source}?v=${ASSET_REVISION}`}
      alt={exhibit.alt}
      width={1600}
      height={900}
      priority={priority}
      loading={priority ? undefined : loading}
      onError={() => setFailedSource(desired)}
      unoptimized
    />
  );
}

export default function Home() {
  const [motion, setMotion] = useState(() =>
    typeof window === 'undefined'
      ? true
      : !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  );

  const hero = exhibits[0];
  const exhibitCount = String(exhibits.length).padStart(2, '0');

  return (
    <main id="top">
      <a className="skip-link" href="#exhibits">
        Skip to the exhibits
      </a>
      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="BHSM Museum home">
          <Image
            className="wordmark-image"
            src="./bhsm-symbol.svg"
            alt=""
            width={40}
            height={40}
            unoptimized
          />
          <span>
            <strong>BHSM Museum</strong>
            <small>Scientific research archive</small>
          </span>
        </a>
        <nav aria-label="Museum navigation">
          <a href="#exhibits">Exhibits</a>
          <a href="#cms-data">CMS data</a>
          <a href="#reconstruction">Research</a>
          <a href="#professionals">For reviewers</a>
          <a href="#creator">Creator</a>
          <a className="nav-repository" href={REPOSITORY}>
            Repository <Code2 aria-hidden="true" size={16} />
          </a>
        </nav>
      </header>

      <section
        className="exhibition-hall exhibition-hall-first"
        id="exhibits"
        aria-labelledby="exhibit-title"
      >
        <div className="section-heading hall-heading">
          <p className="eyebrow">
            Main exhibition hall · {exhibits.length} animated data engines
          </p>
          <h1 id="exhibit-title">Look first. Then go backstage.</h1>
          <p>
            The CMS exhibit uses real public data. The remaining rooms use
            normalized simulations or audited records to show calculations
            happening—never flow charts.
          </p>
          <Button
            className="hall-motion-toggle"
            onClick={() => setMotion((value) => !value)}
            aria-pressed={!motion}
            variant="outline"
            size="sm"
          >
            {motion ? <Pause aria-hidden="true" /> : <Play aria-hidden="true" />}
            {motion ? 'Pause all motion' : 'Play all motion'}
          </Button>
        </div>

        <div className="exhibit-list">
          {exhibits.map((exhibit, index) => (
            <article
              className="exhibit"
              id={`exhibit-${exhibit.number}`}
              key={exhibit.number}
            >
              <div className="exhibit-visual">
                <div className="display-label">
                  <span>Exhibit {exhibit.number} / {exhibitCount}</span>
                  <span>
                    {exhibit.number === '01'
                      ? 'Real-data engine'
                      : 'Simulation / audit engine'}{' '}
                    · {motion ? 'motion on' : 'static view'}
                  </span>
                </div>
                <MotionImage
                  motion={motion}
                  exhibit={exhibit}
                  priority={index === 0}
                  loading={index === 0 ? undefined : 'lazy'}
                />
              </div>
              <div className="exhibit-placard">
                <p className="exhibit-index">Gallery {exhibit.number}</p>
                <h2>{exhibit.title}</h2>
                <p className="exhibit-subtitle">{exhibit.subtitle}</p>
                <p className="data-label">{exhibit.dataLabel}</p>
                <StatusBadge exhibit={exhibit} />
                {exhibit.facts ? (
                  <dl className="exhibit-facts">
                    {exhibit.facts.map((fact) => (
                      <div key={fact.label}>
                        <dt>{fact.label}</dt>
                        <dd>{fact.value}</dd>
                      </div>
                    ))}
                  </dl>
                ) : null}
                <dl>
                  <div>
                    <dt>Lay description</dt>
                    <dd>{exhibit.lay}</dd>
                  </div>
                  <div>
                    <dt>What you are seeing</dt>
                    <dd>{exhibit.seen}</dd>
                  </div>
                  <div>
                    <dt>Scientific caption</dt>
                    <dd>{exhibit.matters}</dd>
                  </div>
                </dl>
                <div
                  className="record-links"
                  aria-label={`Scientific record for ${exhibit.title}`}
                >
                  <span>Open scientific record</span>
                  {exhibit.links.map((link) => (
                    <a href={link.href} key={link.label}>
                      {link.label} <span aria-hidden="true">↗</span>
                    </a>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="atrium" aria-labelledby="atrium-title">
        <div className="atrium-copy">
          <p className="eyebrow">Berger–Hopf Standard Model</p>
          <h2 id="atrium-title" className="atrium-title">
            Geometry, particles, and the record <span>in motion.</span>
          </h2>
          <p className="lede">
            The reconstructed BHSM archive begins with real CMS Open Data, then
            moves through the action, spectrum, observables, and the open
            physical-identification bridge.
          </p>
          <div className="atrium-actions">
            <a className="button button-primary" href="#cms-data">
              Open the CMS record <ArrowRight aria-hidden="true" size={18} />
            </a>
            <a className="button button-secondary" href={REPOSITORY}>
              Enter the scientific repository
            </a>
          </div>
          <div className="hero-release" aria-label="BHSM archival identifiers">
            <span>Release v1.1.0</span>
            <span>Research head v15.7</span>
            <span>DOI 10.5281/zenodo.20663419</span>
          </div>
        </div>

        <div className="atrium-display" aria-label="Featured animated exhibit">
          <div className="display-label">
            <span>Exhibit {hero.number} / {exhibitCount}</span>
            <Button
              onClick={() => setMotion((value) => !value)}
              aria-pressed={!motion}
              variant="ghost"
              size="sm"
            >
              {motion ? (
                <Pause aria-hidden="true" />
              ) : (
                <Play aria-hidden="true" />
              )}
              {motion ? 'Pause all motion' : 'Play all motion'}
            </Button>
          </div>
          <div className="display-frame">
            <MotionImage motion={motion} exhibit={hero} priority />
          </div>
          <div className="display-caption">
            <p>
              <strong>Lay description</strong>
              {hero.lay}
            </p>
            <StatusBadge exhibit={hero} />
          </div>
          {hero.facts ? (
            <dl className="hero-facts">
              {hero.facts.map((fact) => (
                <div key={fact.label}>
                  <dt>{fact.label}</dt>
                  <dd>{fact.value}</dd>
                </div>
              ))}
            </dl>
          ) : null}
        </div>
      </section>

      <CMSExplorer />

      <section
        className="reconstruction-room"
        id="reconstruction"
        aria-labelledby="reconstruction-title"
      >
        <div className="section-heading reconstruction-heading">
          <p className="eyebrow">Reconstruction room · integrated BHSM corpus</p>
          <h2 id="reconstruction-title">
            One program, recovered across an evolving research record.
          </h2>
          <p>
            Every BHSM lineage is now integrated on main. The reconstruction
            preserves its calculations while separating an existing particle
            ontology from the later AE2 stop and event-child dynamics and from
            the audited but still-missing local-enclosure carrier.
          </p>
        </div>

        <div className="bridge-map" aria-label="Physical identification bridge">
          <article className="bridge-stage bridge-stage-upstream">
            <span>01 · Reused upstream state</span>
            <h3>BHSM family or mode</h3>
            <p>
              Representation, projector, current, topology, and existing SM
              manifestation class retain their historical provenance.
            </p>
            <strong>Historical registry retained</strong>
          </article>
          <div className="bridge-arrow" aria-hidden="true">→</div>
          <article className="bridge-stage bridge-stage-dynamics">
            <span>02 · Derived AE2 dynamics</span>
            <h3>Selected stop → event child</h3>
            <p>
              The canonical stop is the reduced Euler–Dirac Hessian stop
              λ₂₄ = 0. Its geometric event child is carried forward.
            </p>
            <strong>Real dynamics · not yet enclosure</strong>
          </article>
          <div className="bridge-arrow" aria-hidden="true">→</div>
          <article className="bridge-stage bridge-stage-open">
            <span>03 · Open typed interface</span>
            <h3>Local enclosure → SM manifestation</h3>
            <p>
              Six stored AE2 candidate classes have now been tested. None
              supplies the full action-owned localization type needed to carry
              the frozen state into its existing manifestation class.
            </p>
            <strong>6 audited · 0 qualify</strong>
          </article>
        </div>

        <div className="reconstruction-ledger">
          <article>
            <span className="ledger-label ledger-proved">Recovered</span>
            <h3>Preserved BHSM assets</h3>
            <p>Particle families, modes, representations, projectors, currents, topology, selected stop, and event child.</p>
          </article>
          <article>
            <span className="ledger-label ledger-open">Still required</span>
            <h3>Four proof kernels</h3>
            <p>Localization carrier, physical interface variation, child inheritance, and actual C2 family/mode instantiation.</p>
          </article>
          <article>
            <span className="ledger-label ledger-forbidden">Not equivalent</span>
            <h3>Interpretive guardrails</h3>
            <p>λ₂₄ = 0 is not 2π; a stop is not automatically a spacetime edge; positive duration is not particle stability.</p>
          </article>
        </div>

        <div className="reconstruction-records">
          <a href={`${SCIENCE}/docs/BHSM_NORMAN_SCHOOL_FULL_CORPUS_RECONSTRUCTION.md`}>Full ontology reconstruction ↗</a>
          <a href={`${SCIENCE}/theory/n12_gate7_localization_carrier_kill_screen.md`}>Carrier kill screen ↗</a>
          <a href={`${SCIENCE}/theory/n12_gate7_physical_encapsulation_identification_bridge.md`}>Typed enclosure bridge ↗</a>
          <a href={`${SCIENCE}/theory/post_ae2_localization_carrier_extension_contract.md`}>Extension acceptance contract ↗</a>
        </div>
        <dl className="corpus-facts" aria-label="Integrated BHSM corpus figures">
          <div>
            <dt>Lineage refs examined</dt>
            <dd>426</dd>
          </div>
          <div>
            <dt>Lineage refs integrated</dt>
            <dd>426</dd>
          </div>
          <div>
            <dt>Unmerged refs</dt>
            <dd>0</dd>
          </div>
          <div>
            <dt>Files after reduction</dt>
            <dd>17,630</dd>
          </div>
        </dl>
      </section>

      <section
        className="claim-key"
        id="claim-key"
        aria-labelledby="claim-title"
      >
        <div className="section-heading">
          <p className="eyebrow">Museum legend</p>
          <h2 id="claim-title">Read every claim by its evidence level</h2>
        </div>
        <div className="claim-grid">
          <article>
            <span className="claim-number">01</span>
            <h3>Implemented machinery</h3>
            <p>
              Code, interfaces, tests, and artifacts exist in the repository.
            </p>
          </article>
          <article>
            <span className="claim-number">02</span>
            <h3>Numerically demonstrated</h3>
            <p>
              Behavior is shown with its interval, resolution, and provisional
              or benchmark qualifier.
            </p>
          </article>
          <article>
            <span className="claim-number">03</span>
            <h3>Physical prediction</h3>
            <p>
              This label is reserved for results frozen behind the no-fit
              firewall. Promotion is otherwise explicitly gated.
            </p>
          </article>
        </div>
        <div className="status-ribbon" role="note">
          <strong>Current research state</strong>
          <span>
            AE2 stop and event child are derived · 6 carrier classes audited,
            0 qualify · owner-authorized action-version decision remains open ·
            FULL_BHSM_COMPLETE = FALSE
          </span>
          <a href={`${SCIENCE}/docs/current_bhsm_status.md`}>
            Read current status <ArrowRight aria-hidden="true" size={15} />
          </a>
        </div>
      </section>

      <section
        className="professional-wing"
        id="professionals"
        aria-labelledby="professional-title"
      >
        <div className="section-heading professional-heading">
          <p className="eyebrow">The reading room · professional review</p>
          <h2 id="professional-title">The back of every story is open.</h2>
          <p>
            For institutional reviewers, every path below enters the
            repository’s scientific record—not a marketing summary.
          </p>
        </div>
        <div className="review-grid">
          {[
            [
              '01',
              'Current authority',
              'Live status, completion boundary, and blocker.',
              `${SCIENCE}/docs/current_bhsm_status.md`,
            ],
            [
              '02',
              'Claim-to-evidence matrix',
              'Claim class, action owner, artifact, benchmark, and falsifier.',
              `${SCIENCE}/docs/BHSM_1_0_CLAIM_TO_EVIDENCE_MATRIX.md`,
            ],
            [
              '03',
              'Action provenance',
              'Attachment audit for the retained action and missing physical blocks.',
              `${SCIENCE}/theory/bhsm_current_full_field_action_attachment.md`,
            ],
            [
              '04',
              'Reviewer reproduction',
              'Environment, commands, expected outputs, and audit route.',
              `${SCIENCE}/docs/reviewer_reproduction_guide.md`,
            ],
            [
              '05',
              'Frozen records',
              'The no-retuning prediction layer and its stated authority.',
              `${SCIENCE}/docs/frozen_predictions.md`,
            ],
            [
              '06',
              'Public-language guardrails',
              'Allowed statements, forbidden claims, and institutional boundaries.',
              `${SCIENCE}/docs/allowed_public_language.md`,
            ],
            [
              '07',
              'Ontology reconstruction',
              'Recovered meanings, provenance, vocabulary drift, and current authority.',
              `${SCIENCE}/docs/BHSM_NORMAN_SCHOOL_FULL_CORPUS_RECONSTRUCTION.md`,
            ],
            [
              '08',
              'Physical enclosure bridge',
              'Typed transport from existing BHSM states through the AE2 event child.',
              `${SCIENCE}/theory/n12_gate7_physical_encapsulation_identification_bridge.md`,
            ],
            [
              '09',
              'Integrated validation',
              'Current-authority checks and the retained historical N=3 replay boundary.',
              `${SCIENCE}/docs/BHSM_INTEGRATED_VALIDATION_REPORT.md`,
            ],
          ].map(([number, title, copy, href]) => (
            <a className="review-card" href={href} key={number}>
              <span>{number}</span>
              <h3>{title}</h3>
              <p>{copy}</p>
              <strong>Open record ↗</strong>
            </a>
          ))}
        </div>
      </section>

      <section
        className="reproduction-lab"
        id="reproduce"
        aria-labelledby="reproduce-title"
      >
        <div className="lab-copy">
          <p className="eyebrow">Reproduction lab</p>
          <h2 id="reproduce-title">Clone. Inspect. Test. Audit.</h2>
          <p>
            The primary implementation is Python 3.10+. These commands enter the
            same public interface used by the focused invariant and
            claim-separation tests.
          </p>
          <a className="text-link" href={`${SCIENCE}/QUICKSTART.md`}>
            Open the complete quickstart{' '}
            <ArrowRight aria-hidden="true" size={16} />
          </a>
        </div>
        <pre aria-label="BHSM quickstart commands">
          <code>{`git clone https://github.com/ncarberry64/\
Berger-Hopf-Standard-Model.git
cd Berger-Hopf-Standard-Model
python -m venv .venv
python -m pip install -e .
python -m pytest -q \
  tests/test_engine_invariant_preservation.py \
  tests/test_engine_physics_status_separation.py
python -m bhsm.interface physics-status --format markdown`}</code>
        </pre>
      </section>

      <section className="language-gallery" aria-labelledby="language-title">
        <div className="section-heading">
          <p className="eyebrow">Software and integration surface</p>
          <h2 id="language-title">
            Plug in at the level the evidence supports.
          </h2>
        </div>
        <div className="language-grid">
          {[
            [
              'Python',
              'Primary computational engine, CLI, tests, and audits',
              'Core',
            ],
            [
              'JSON / NPZ',
              'Machine-readable artifacts, ledgers, and numerical records',
              'Evidence',
            ],
            [
              'Markdown / LaTeX',
              'Derivations, reviewer guides, and policy',
              'Review',
            ],
            [
              'Jupyter',
              'Inspectable notebooks and research demonstrations',
              'Analysis',
            ],
            [
              'C++ / ROOT',
              'Optional experimental-data adapter surface',
              'Runtime-gated',
            ],
            [
              'Wolfram / FeynRules',
              'Optional symbolic and model-export adapters',
              'Runtime-gated',
            ],
            [
              'TypeScript',
              'This museum façade and its accessible motion controls',
              'Presentation',
            ],
          ].map(([language, role, status]) => (
            <article key={language}>
              <span>{status}</span>
              <h3>{language}</h3>
              <p>{role}</p>
            </article>
          ))}
        </div>
        <p className="integration-boundary">
          Optional adapters do not establish collider readiness, detector
          compatibility, or institutional endorsement. New language bindings
          should follow a reviewed scientific interface contract rather than
          duplicate physics logic.
        </p>
      </section>

      <section
        className="creator-alcove"
        id="creator"
        aria-labelledby="creator-title"
      >
        <div className="creator-mark" aria-hidden="true">
          <span>NPC</span>
          <small>Primary author</small>
        </div>
        <div className="creator-copy">
          <p className="eyebrow">Creator’s alcove</p>
          <h2 id="creator-title">Norman P. Carberry</h2>
          <p className="creator-role">
            Independent Researcher · Oconomowoc, Wisconsin, USA
          </p>
          <p>
            Norman P. Carberry is the primary author of the Berger–Hopf Standard
            Model research framework. From Oconomowoc, Wisconsin, he has built
            BHSM as a public, artifact-backed program spanning differential
            geometry, particle-physics interfaces, numerical certification, and
            reproducible scientific software.
          </p>
          <p className="creator-release">
            Citation release v1.1.0 · released 26 June 2026 · ORCID
            0009-0000-6650-3485 · Zenodo 10.5281/zenodo.20663419
          </p>
          <div className="creator-links">
            {creatorLinks.map((link) => (
              <a href={link.href} key={link.label}>
                {link.label} ↗
              </a>
            ))}
          </div>
        </div>
      </section>

      <footer>
        <div>
          <Image
            src="./bhsm-symbol.svg"
            alt=""
            width={48}
            height={48}
            unoptimized
          />
          <p>
            <strong>BHSM Museum</strong>
            <br />The research archive of Norman P. Carberry.
          </p>
        </div>
        <div className="footer-links">
          <a href={REPOSITORY}>GitHub repository</a>
          <a href={`${SCIENCE}/LICENSE.md`}>License</a>
          <a href="https://doi.org/10.5281/zenodo.20663419">DOI</a>
          <a href="#top">Back to top ↑</a>
        </div>
        <p className="footer-boundary">
          Reconstructed corpus · CMS Open Data Record 303 · nine animated
          exhibits · current authority synchronized with GitHub main
        </p>
      </footer>
    </main>
  );
}
