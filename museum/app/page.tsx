'use client';

import { Pause, Play } from 'lucide-react';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  cosmologyExhibit,
  exhibits,
  REPOSITORY,
  SCIENCE,
  type Exhibit,
} from './exhibits';
import { ScienceGallery } from './science-gallery';
import { PrototypeScience } from './prototype-science';
import { CosmicEnclosure } from './cosmic-enclosure';
import { CMSExplorer } from './cms-explorer';

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

export default function Home() {
  const [motion, setMotion] = useState(false);
  const [displayId, setDisplayId] = useState('08');
  useEffect(() => {
    setMotion(!window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }, []);
  const display =
    researchDisplays.find((row) => row.number === displayId) ??
    researchDisplays[0];
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
            <small>Geometry and the pattern of matter</small>
          </span>
        </a>
        <nav aria-label="Museum navigation">
          <a href="#potential">The possibility</a>
          <a href="#exhibits">Science exhibits</a>
          <a href="#comparisons">Additional data</a>
          <a href="#details">Details</a>
          <a href="#creator">Author</a>
          <a href="#other-work">Cosmology</a>
          <a href={REPOSITORY}>Academic repository ↗</a>
        </nav>
      </header>
      <section
        id="potential"
        className="potential"
        aria-labelledby="potential-title"
      >
        <div className="potential-copy">
          <p className="eyebrow">
            Berger–Hopf Standard Model · an open scientific proposal
          </p>
          <h1 id="potential-title">
            Could geometry explain <em>the pattern of matter?</em>
          </h1>
          <p className="potential-lede">
            BHSM explores a possibility with historic stakes: that particle
            families, their mass hierarchies and their interactions could share
            a geometric origin.
          </p>
          <p>
            If established and tested, that would be a major step toward
            explaining why nature has this pattern of particles and forces. The
            proposal is still being developed; a complete physical derivation
            and experimental validation remain open.
          </p>
          <a className="button button-primary" href="#exhibits">
            Explore the scientific comparisons ↓
          </a>
        </div>
        <aside className="potential-panel" aria-label="The scientific idea">
          <p className="eyebrow">The question behind the equations</p>
          <h2>
            One geometry.
            <br />A connected account of matter.
          </h2>
          <ol>
            <li>
              <strong>Shape</strong>
              <span>A curved internal geometry supplies possible modes.</span>
            </li>
            <li>
              <strong>Families</strong>
              <span>
                Different modes could organize repeated particle patterns.
              </span>
            </li>
            <li>
              <strong>Tests</strong>
              <span>
                Mass ratios and mixing patterns give the proposal something
                concrete to answer.
              </span>
            </li>
          </ol>
          <p className="data-label">
            Conceptual explanation · not experimental evidence
          </p>
        </aside>
      </section>
      <PrototypeScience motion={motion} setMotion={setMotion} />
      <ScienceGallery />
      <section
        id="research-exhibit"
        className="research-exhibit"
        aria-labelledby="research-title"
      >
        <div className="section-heading">
          <p className="eyebrow">Computation and research achievements</p>
          <h2 id="research-title">How the scientific record is checked.</h2>
          <p>
            This single exhibit gathers software demonstrations, real-data
            coordinate checks and mathematical certification work. These support
            scrutiny of the proposal; they do not replace its physics tests.
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
            onClick={() => setMotion((value) => !value)}
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
            <p>{display.seen}</p>
            <p>{display.matters}</p>
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
        <p className="research-boundary">
          The local enclosure and its family-state transport have been derived
          within their stated scope. The complete interacting physical solution
          remains open. New derivative handoffs reuse these results while Gate 7
          certification continues.
        </p>
        <a
          className="text-link"
          href={`${SCIENCE}/theory/ae4_event_response_jet_integration.md`}
        >
          Read the integrated response work and its limits ↗
        </a>
      </section>
      <section
        id="details"
        className="museum-details"
        aria-labelledby="details-title"
      >
        <div className="section-heading">
          <p className="eyebrow">The details behind the exhibits</p>
          <h2 id="details-title">What the evidence can—and cannot—say.</h2>
        </div>
        <div className="claim-grid">
          <article>
            <h3>Historical calculations</h3>
            <p>
              Actual recorded BHSM screens and conditional model results. They
              are not generated display positions, but they are also not newly
              established physical predictions.
            </p>
          </article>
          <article>
            <h3>Comparison references</h3>
            <p>
              The sandbox supplied the reference markers used above. They are
              labeled unverified throughout. The real CMS sample has its own
              experimental source and serves a separate software check.
            </p>
          </article>
          <article>
            <h3>Explanatory simulations</h3>
            <p>
              Animated illustrations help explain an idea or calculation. A
              simulated trajectory or spectrum is never labeled as a
              measurement.
            </p>
          </article>
        </div>
        <div className="details-copy">
          <h3>One rule: comparisons must not choose the answer.</h3>
          <p>
            BHSM’s action, modes and coefficients must be established
            independently. A measurement may test a frozen result; it may not
            quietly choose a branch, repair a mass or set a separate
            normalization for each observable.
          </p>
          <p>
            Gate 7 is active. The physical background, interacting observables
            and full completion remain unresolved.{' '}
            <code>FULL_BHSM_COMPLETE = FALSE</code>.
          </p>
        </div>
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
          <p className="eyebrow">Final wing · other work · cosmology</p>
          <h2 id="other-work-title">
            Could a large-scale pattern connect cosmic anomalies?
          </h2>
          <p>
            This separate cosmology preprint explores another geometric
            question. It is presented last and retains its own scientific scope.
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
