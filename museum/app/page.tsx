'use client';

import { Pause, Play } from 'lucide-react';
import Image from 'next/image';
import { useState, useSyncExternalStore } from 'react';
import { Button } from '@/components/ui/button';
import {
  cosmologyExhibit,
  exhibits,
  REPOSITORY,
  SCIENCE,
  type Exhibit,
} from './exhibits';
import { ScienceGallery } from './science-gallery';
import { PrototypeScience, UnificationConsole } from './prototype-science';
import { CosmicEnclosure } from './cosmic-enclosure';
import { CMSExplorer } from './cms-explorer';
import { EngineHero } from './science-console';

const ASSET_REVISION = 'science-first-2026-09-07';
const researchDisplays = exhibits.filter((row) =>
  ['01', '08'].includes(row.number),
);

function MotionImage({
  motion,
  exhibit,
}: {
  motion: boolean;
  exhibit: Exhibit;
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
      loading="lazy"
      onError={() => setFailedSource(desired)}
      unoptimized
    />
  );
}

function subscribeMotionPreference(onChange: () => void) {
  const query = window.matchMedia('(prefers-reduced-motion: reduce)');
  query.addEventListener('change', onChange);
  return () => query.removeEventListener('change', onChange);
}
export default function Home() {
  const reducedMotion = useSyncExternalStore(
    subscribeMotionPreference,
    () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    () => true,
  );
  const [motionOverride, setMotion] = useState<boolean | null>(null);
  const motion = motionOverride ?? !reducedMotion;
  const [displayId, setDisplayId] = useState('01');
  const display =
    researchDisplays.find((row) => row.number === displayId) ??
    researchDisplays[0];
  return (
    <main
      id="top"
      className="prediction-museum"
      data-motion={motion ? 'on' : 'off'}
    >
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
            <small>The prediction engine museum</small>
          </span>
        </a>
        <nav aria-label="Museum navigation">
          <a href="#potential">The possibility</a>
          <a href="#exhibits">Science exhibits</a>
          <a href="#comparisons">Comparisons</a>
          <a href="#details">Details</a>
          <a href="#creator">Author</a>
          <a href="#other-work">Cosmology</a>
          <a href={REPOSITORY}>Academic repository ↗</a>
        </nav>
      </header>
      <EngineHero motion={motion} setMotion={setMotion} />
      <PrototypeScience motion={motion} setMotion={setMotion} />
      <ScienceGallery motion={motion} />
      <UnificationConsole motion={motion} />
      <section
        id="research-exhibit"
        className="research-exhibit"
        aria-labelledby="research-title"
      >
        <div className="section-heading">
          <p className="eyebrow">06 · Data, computation & research</p>
          <h2 id="research-title">Inside the real data.</h2>
          <p>
            Explore recorded CMS collisions and the numerical checks behind the
            research. Experimental data and mathematical certification answer
            different questions about the scientific record.
          </p>
        </div>
        <div className="research-controls">
          <label htmlFor="research-display">Choose a research display</label>
          <select
            id="research-display"
            value={displayId}
            onChange={(e) => setDisplayId(e.target.value)}
          >
            {researchDisplays.map((row) => (
              <option value={row.number} key={row.number}>
                {row.title}
              </option>
            ))}
          </select>
          <Button
            onClick={() => setMotion(!motion)}
            aria-pressed={!motion}
            variant="outline"
          >
            {motion ? (
              <Pause aria-hidden="true" />
            ) : (
              <Play aria-hidden="true" />
            )}
            {motion ? 'Pause animations' : 'Play animations'}
          </Button>
        </div>
        <div className="research-display">
          <div className="research-visual">
            <p className="data-label">{display.dataLabel}</p>
            <MotionImage motion={motion} exhibit={display} />
          </div>
          <div className="research-copy">
            <h3>{display.title}</h3>
            <p>
              <strong>In plain language</strong> {display.lay}
            </p>
            <details className="console-details">
              <summary>Explore the science · this data display</summary>
              <p>{display.seen}</p>
              <p>{display.matters}</p>
            </details>
            <p className="data-label">{display.statusLabel}</p>
            <div className="record-links">
              {display.links.map((link) => (
                <a href={link.href} key={link.label}>
                  {link.label} ↗
                </a>
              ))}
            </div>
          </div>
        </div>
        <details className="research-detail">
          <summary>Explore the real CMS data sample</summary>
          <p className="data-label">
            Real experimental data · CMS Open Data Record 303 · CC0
          </p>
          <CMSExplorer />
        </details>
      </section>
      <section
        id="details"
        className="museum-details"
        aria-labelledby="details-title"
      >
        <div className="section-heading">
          <p className="eyebrow">The details behind the exhibits</p>
          <h2 id="details-title">Follow the science further.</h2>
        </div>
        <p className="method-intro">
          BHSM is being developed as a prediction engine: derive an answer from
          the model, then test it against nature. Today’s exhibits distinguish
          historical calculations, experimental references and explanatory
          simulations.
        </p>
        <details className="console-details">
          <summary>How to read the evidence</summary>
          <p>
            Measurements test the result; they do not choose the model’s answer.
            Historical screens and conditional structural results are not
            completed physical predictions. Full physical closure remains open:{' '}
            <code>FULL_BHSM_COMPLETE = FALSE</code>.
          </p>
          <p>
            Published CODATA, PDG and neutrino-fit references retain their
            editions, assumptions and uncertainties. Reviewed BHSM outputs can
            enter the exhibits as the derivations are completed.
          </p>
        </details>
        <div className="review-grid">
          {[
            [
              'The scientific framework',
              'The hypotheses, equations and claim boundaries.',
              `${SCIENCE}/CLAIMS.md`,
            ],
            [
              'Current research status',
              'Established results and the remaining physical questions.',
              `${SCIENCE}/docs/current_bhsm_status.md`,
            ],
            [
              'For institutions',
              'Portable setup, offline checks, reusable artifacts and optional adapters.',
              `${SCIENCE}/docs/INSTITUTIONAL_START.md`,
            ],
            [
              'Complete comparison source',
              'The sandbox snapshot, qualifications and adverse criteria.',
              `${SCIENCE}/docs/museum/sandbox_comparison_source_2026-09-02.md`,
            ],
          ].map(([title, copy, href]) => (
            <a className="review-card" href={href} key={title}>
              <h3>{title}</h3>
              <p>{copy}</p>
              <strong>Open the academic record ↗</strong>
            </a>
          ))}
        </div>
      </section>
      <section
        id="creator"
        className="creator-alcove"
        aria-labelledby="creator-title"
      >
        <div className="creator-mark" aria-hidden="true">
          <span>NPC</span>
          <small>Primary author</small>
        </div>
        <div className="creator-copy">
          <p className="eyebrow">The author</p>
          <h2 id="creator-title">Norman P. Carberry</h2>
          <p>
            Independent researcher and author of the Berger–Hopf Standard Model
            program. The public record connects the proposal, its derivations,
            its evolving tests and the questions still to be resolved.
          </p>
          <div className="creator-links">
            <a href="https://orcid.org/0009-0000-6650-3485">
              ORCID 0009-0000-6650-3485 ↗
            </a>
            <a href={`${SCIENCE}/CITATION.cff`}>Citation metadata ↗</a>
            <a href="https://doi.org/10.5281/zenodo.20663419">Archival DOI ↗</a>
            <a href={`${SCIENCE}/manuscript/BHSM_final_paper.pdf`}>
              Frozen preprint PDF ↗
            </a>
          </div>
        </div>
      </section>
      <section
        id="other-work"
        className="other-work-wing"
        aria-labelledby="other-work-title"
      >
        <div className="section-heading">
          <p className="eyebrow">Other work · cosmology</p>
          <h2 id="other-work-title">
            Could a large-scale pattern connect cosmic anomalies?
          </h2>
          <p>
            A hyperspherical cosmology proposal explores whether spatial
            topography could connect several large-scale anomalies.
          </p>
        </div>
        <article className="other-work-card">
          <div className="other-work-visual">
            <p className="data-label">
              Simulated schematic · not observational data
            </p>
            <MotionImage motion={motion} exhibit={cosmologyExhibit} />
          </div>
          <div className="other-work-copy">
            <h3>{cosmologyExhibit.title}</h3>
            <p className="data-label">{cosmologyExhibit.dataLabel}</p>
            <p>
              <strong>In plain language</strong> {cosmologyExhibit.lay}
            </p>
            <p>{cosmologyExhibit.seen}</p>
            <p>{cosmologyExhibit.matters}</p>
            <p className="data-label">
              Independent preprint · not peer reviewed
            </p>
            <div className="record-links">
              {cosmologyExhibit.links.map((link) => (
                <a href={link.href} key={link.label}>
                  {link.label} ↗
                </a>
              ))}
            </div>
          </div>
        </article>
        <p className="other-work-boundary">
          Posted 20 January 2026. This is a schematic model, not a sky map or
          confirmation from a survey. Comparison level: order of magnitude; a
          full likelihood analysis remains open.
        </p>
        <CosmicEnclosure motion={motion} />
      </section>
      <footer>
        <p>
          <strong>BHSM Museum</strong>
          <br />
          The public science collection of Norman P. Carberry.
        </p>
        <div className="footer-links">
          <a href={REPOSITORY}>Academic repository</a>
          <a href={`${SCIENCE}/LICENSE.md`}>License</a>
          <a href="#top">Back to top ↑</a>
        </div>
      </footer>
    </main>
  );
}
