'use client';

import { ArrowRight, Code2, Pause, Play, ShieldCheck } from 'lucide-react';
import Image from 'next/image';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { exhibits, REPOSITORY, SCIENCE, type Exhibit } from './exhibits';

const creatorLinks = [
  { label: 'ORCID record', href: 'https://orcid.org/0009-0000-6650-3485' },
  { label: 'Citation metadata', href: `${SCIENCE}/CITATION.cff` },
  { label: 'Archival DOI', href: 'https://doi.org/10.5281/zenodo.20663419' },
];

function StatusBadge({ exhibit }: { exhibit: Exhibit }) {
  return (
    <span className={`status status-${exhibit.status}`}>
      <ShieldCheck aria-hidden="true" size={15} /> {exhibit.statusLabel}
    </span>
  );
}

export default function Home() {
  const [motion, setMotion] = useState(() =>
    typeof window === 'undefined'
      ? true
      : !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  );

  const hero = exhibits[0];

  return (
    <main>
      <a className="skip-link" href="#museum-start">
        Skip to the exhibition
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
            <small>Public exhibition · Scientific archive</small>
          </span>
        </a>
        <nav aria-label="Museum navigation">
          <a href="#exhibits">Exhibits</a>
          <a href="#professionals">For reviewers</a>
          <a href="#creator">Creator</a>
          <a className="nav-repository" href={REPOSITORY}>
            Repository <Code2 aria-hidden="true" size={16} />
          </a>
        </nav>
      </header>

      <section className="atrium" id="top" aria-labelledby="atrium-title">
        <div className="atrium-copy">
          <p className="eyebrow">Berger–Hopf Standard Model</p>
          <h1 id="atrium-title">
            One Action <span>·</span> One Scale <span>·</span> One Observable
            Pipeline
          </h1>
          <p className="lede">
            A visual entrance to an artifact-backed mathematical physics
            program. Watch each calculation move, then open the scientific
            record behind it.
          </p>
          <div className="atrium-actions">
            <a className="button button-primary" href="#museum-start">
              Begin the guided tour <ArrowRight aria-hidden="true" size={18} />
            </a>
            <a className="button button-secondary" href={REPOSITORY}>
              Enter the scientific repository
            </a>
          </div>
          <p className="institution-note">
            Built for public understanding and professional inspection. No CERN,
            Fermilab, or institutional endorsement is implied.
          </p>
        </div>

        <div className="atrium-display" aria-label="Featured animated exhibit">
          <div className="display-label">
            <span>Exhibit {hero.number} / 07</span>
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
            <Image
              src={`./exhibits/${motion ? hero.animated : hero.still}`}
              alt={hero.alt}
              width={1600}
              height={900}
              priority
              unoptimized
            />
          </div>
          <div className="display-caption">
            <p>
              <strong>What you are seeing</strong>
              {hero.seen}
            </p>
            <StatusBadge exhibit={hero} />
          </div>
        </div>
      </section>

      <section className="orientation" id="museum-start">
        <div>
          <p className="eyebrow">Orientation wall · 60 seconds</p>
          <h2>
            The displays are the invitation. The records are the evidence.
          </h2>
        </div>
        <p>
          BHSM investigates whether Berger–Hopf geometry can organize a
          reproducible path from a parent action to particle-physics
          calculations. Every animation has a backstage door to source,
          derivation, tests, artifacts, and stated limits.
        </p>
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
          <strong>Current public boundary</strong>
          <span>
            Gate 7 remains ACTIVE_NOT_CLOSED · physical readout is gated ·
            FULL_BHSM_COMPLETE = FALSE
          </span>
          <a href={`${SCIENCE}/docs/current_bhsm_status.md`}>
            Read current status <ArrowRight aria-hidden="true" size={15} />
          </a>
        </div>
      </section>

      <section
        className="exhibition-hall"
        id="exhibits"
        aria-labelledby="exhibit-title"
      >
        <div className="section-heading hall-heading">
          <p className="eyebrow">
            Main exhibition hall · seven animated calculations
          </p>
          <h2 id="exhibit-title">Look first. Then go backstage.</h2>
          <p>
            Each display starts with plain language. The scientific-record links
            lead directly to the implementation, test, derivation, or policy
            that supports the placard.
          </p>
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
                  <span>Exhibit {exhibit.number} / 07</span>
                  <span>{motion ? 'Motion on' : 'Static view'}</span>
                </div>
                <Image
                  src={`./exhibits/${motion ? exhibit.animated : exhibit.still}`}
                  alt={exhibit.alt}
                  width={1600}
                  height={900}
                  loading={index === 0 ? 'eager' : 'lazy'}
                  unoptimized
                />
              </div>
              <div className="exhibit-placard">
                <p className="exhibit-index">Gallery {exhibit.number}</p>
                <h3>{exhibit.title}</h3>
                <p className="exhibit-subtitle">{exhibit.subtitle}</p>
                <StatusBadge exhibit={exhibit} />
                <dl>
                  <div>
                    <dt>What you are seeing</dt>
                    <dd>{exhibit.seen}</dd>
                  </div>
                  <div>
                    <dt>Why it matters</dt>
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
            The repository record identifies Norman P. Carberry as the primary
            author of BHSM. The work is presented as an independent,
            artifact-backed mathematical-physics research framework built for
            inspection, reproducibility, and explicit claim boundaries.
          </p>
          <p className="creator-boundary">
            No invented biography or portrait is used here. A first-person
            creator’s statement can be added when supplied or approved by the
            creator.
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
            <br />A public door to a scientific repository.
          </p>
        </div>
        <div className="footer-links">
          <a href={REPOSITORY}>GitHub repository</a>
          <a href={`${SCIENCE}/LICENSE.md`}>License</a>
          <a href="https://doi.org/10.5281/zenodo.20663419">DOI</a>
          <a href="#top">Back to top ↑</a>
        </div>
        <p className="footer-boundary">
          BHSM does not claim empirical establishment, completed physical
          promotion, collider-production readiness, or institutional
          endorsement.
        </p>
      </footer>
    </main>
  );
}
