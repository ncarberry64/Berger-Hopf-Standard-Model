'use client';

import Image from 'next/image';
import { useState, useSyncExternalStore } from 'react';
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
import { EngineHero, ScienceConsole } from './science-console';
import { MuseumSoundtrack } from './museum-soundtrack';
import { CosmologyUpdate } from './cosmology-update';
import { CosmologyRealization } from './cosmology-realization';
import { BHSMResearchUpdate } from './research-update';
import { ComputeAchievement } from './compute-achievement';
import { MuseumDeck } from './museum-deck';
import { BergerHopf } from './berger-hopf';
import { AIAccess } from './ai-access';
import { freshShareURL } from '../lib/social-preview.mjs';
import {
  ExhibitStatement,
  ExhibitReview,
  OpenReviewInvitation,
} from './exhibit-review';

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
            <small>Geometry, evidence and open questions</small>
          </span>
        </a>
        <nav aria-label="Museum navigation">
          <a href="#berger-hopf">Berger &amp; Hopf</a>
          <a href="#exhibits">Science exhibits</a>
          <a href="#comparisons">Comparisons</a>
          <a href="#details">Details</a>
          <a href="#creator">Scientific record</a>
          <a href="#other-work">Cosmology</a>
          <a href="#museum-exit">AI access</a>
          <a href={REPOSITORY}>Academic repository ↗</a>
        </nav>
      </header>
      <MuseumDeck>
        <EngineHero motion={motion} setMotion={setMotion} />
        <BergerHopf motion={motion} setMotion={setMotion} />
        <UnificationConsole motion={motion} setMotion={setMotion} />
        <PrototypeScience motion={motion} setMotion={setMotion} />
        <section
          id="cosmology-original"
          className="other-work-wing"
          aria-labelledby="cosmology-original-title"
        >
          <div className="section-heading">
            <p className="eyebrow">Cosmology · original exhibit</p>
            <h2 id="cosmology-original-title">
              Geometry, light and the cosmic cycle.
            </h2>
            <p>
              Explore the original geometric proposal and its selectable
              storyboard from a sea of light through the cosmic web to a
              proposed cycle.
            </p>
          </div>
          <CosmicEnclosure motion={motion} />
          <ExhibitStatement id="cosmology-original" />
          <p className="other-work-boundary">
            Historical conceptual storyboard · BHSM cosmology proposal
          </p>
          <div className="creator-links">
            <a href="#other-work">
              Follow the proposal into testable responses →
            </a>
          </div>
          <details className="original-proposal-details">
            <summary>
              The January proposal · original illustration and source
            </summary>
            <article className="other-work-card">
              <div className="other-work-visual">
                <MotionImage motion={false} exhibit={cosmologyExhibit} />
              </div>
              <div className="other-work-copy">
                <h3>The January proposal</h3>
                <p>{cosmologyExhibit.seen}</p>
                <a href="https://doi.org/10.20944/preprints202601.1427.v1">
                  Original preprint ↗
                </a>
              </div>
            </article>
          </details>
          <ExhibitReview id="cosmology-original" />
        </section>
        <section
          id="other-work"
          className="other-work-wing"
          aria-labelledby="other-work-title"
        >
          <div className="section-heading">
            <p className="eyebrow">Cosmology · updated 24 September 2026</p>
            <h2 id="other-work-title">
              From a cosmic pattern to a testable response.
            </h2>
            <p>
              Geometry Before Fields connects a proposed geometric framework
              with matter, light propagation and observational tests. Explore
              the computed environmental response, then inspect the numerical
              replay and the supernova comparisons below.
            </p>
          </div>
          <div className="creator-links">
            <a href="#cosmology-original">
              Revisit the original cosmology proposal ←
            </a>
          </div>
          <ExhibitStatement id="other-work" />
          <CosmologyRealization motion={motion} setMotion={setMotion} />
          <details className="console-details cosmology-evidence">
            <summary>Evidence and open questions · cosmology results</summary>
            <CosmologyUpdate />
          </details>
          <ExhibitReview id="other-work" />
        </section>
        <ScienceGallery motion={motion} />
        <ScienceConsole
          id="research-exhibit"
          number="10"
          label="CMS · Data & discovery"
          title="More computation from a better coordinate map."
          intro="Follow real muons through two coordinate descriptions. The picture changes; the recorded event stays the same."
          accent="amber"
        >
          <ComputeAchievement motion={motion} />
          <div
            className="console-selector cms-display-selector"
            aria-label="Data exhibit displays"
          >
            {researchDisplays.map((row) => (
              <button
                key={row.number}
                aria-pressed={displayId === row.number}
                onClick={() => setDisplayId(row.number)}
              >
                {row.number === '01'
                  ? 'CMS collision data'
                  : 'Numerical research'}
              </button>
            ))}
          </div>
          {displayId === '01' ? (
            <>
              <p className="console-caption">
                <b>Real experimental data · CMS Open Data Record 303 · CC0</b>
              </p>
              <CMSExplorer motion={motion} />
              <details className="console-details cms-original">
                <summary>Original CMS animation · source record</summary>
                <MotionImage motion={motion} exhibit={display} />
              </details>
            </>
          ) : (
            <div className="cms-original">
              <p className="console-caption">{display.dataLabel}</p>
              <MotionImage motion={motion} exhibit={display} />
              <p>{display.lay}</p>
              <BHSMResearchUpdate />
            </div>
          )}
          <details className="console-details">
            <summary>Explore the science · data, method and research</summary>
            <p>{display.seen}</p>
            <p>{display.matters}</p>
            <p className="console-caption">{display.statusLabel}</p>
            <div className="record-links">
              {display.links.map((link) => (
                <a key={link.href} href={link.href}>
                  {link.label} ↗
                </a>
              ))}
            </div>
          </details>
        </ScienceConsole>
        <section
          id="details"
          className="museum-details"
          aria-labelledby="details-title"
        >
          <div className="section-heading">
            <p className="eyebrow">From explanation to prediction</p>
            <h2 id="details-title">What makes it predictive?</h2>
          </div>
          <ExhibitStatement id="details" />
          <p className="method-intro">
            A shared geometric description could connect questions about
            particles and the cosmos. Predictive power comes when independently
            specified assumptions produce a quantitative answer before the
            experimental comparison. Follow the chain: derive the dynamics, fix
            the units and scope, freeze the result, then test it against
            observations that did not choose the answer.
          </p>
          <p className="method-intro">
            Collection reviewed 24 September 2026. Local BHSM certificates have
            advanced; no new physical particle observable has passed the
            museum’s reviewed-output requirements. Historical values retain
            their original classifications and experimental reference editions.{' '}
            {/* oxlint-disable-next-line next/no-html-link-for-pages -- This opens a static JSON source record, not an application route. */}
            <a href="./research/museum-update-record.json">
              Update sources and exhibit coverage ↗
            </a>
          </p>
          <p className="method-intro">
            BHSM organizes one universal action, many environment-conditioned
            realizations. Universality does not mean one trajectory, scale or
            boundary condition for every particle and environment. The retained
            Gate-7 background is one proof carrier, not a universal particle
            history.
          </p>
          <p className="method-intro">
            The collection distinguishes action-derived results within their
            certified scope, historical BHSM screens and ontology, conceptual
            interpretations, and conventional experimental references. A
            geometric interpretation does not by itself establish a physical
            prediction.{' '}
            <a href={`${SCIENCE}/docs/BHSM_CURRENT_ENCAPSULATION_SCOPE.md`}>
              Action and realization scope ↗
            </a>
          </p>
          <details className="console-details">
            <summary>How to read the evidence</summary>
            <p>
              Measurements test the result; they do not choose the model’s
              answer. Historical screens and conditional structural results are
              not completed physical predictions. Full physical closure remains
              open: <code>FULL_BHSM_COMPLETE = FALSE</code> and{' '}
              <code>GATE7_CLOSED = FALSE</code>.
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
            <span>BHSM</span>
            <small>Research record</small>
          </div>
          <div className="creator-copy">
            <p className="eyebrow">Scientific record</p>
            <h2 id="creator-title">Sources, citations and archival records</h2>
            <ExhibitStatement id="creator" />
            <p>
              The Berger–Hopf Standard Model record connects model assumptions,
              scoped derivations, reproducible tests and unresolved physical
              questions. Citation metadata preserves research credit; current
              claim boundaries determine how each result may be used.
            </p>
            <div className="creator-links">
              <a href="https://orcid.org/0009-0000-6650-3485">
                ORCID 0009-0000-6650-3485 ↗
              </a>
              <a href={`${SCIENCE}/CITATION.cff`}>Citation metadata ↗</a>
              <a href="https://doi.org/10.5281/zenodo.20663419">
                Archival DOI ↗
              </a>
              <a href={`${SCIENCE}/manuscript/BHSM_final_paper.pdf`}>
                Frozen preprint PDF ↗
              </a>
            </div>
          </div>
        </section>
        <footer id="museum-exit">
          <p>
            <strong>BHSM Museum</strong>
            <br />
            The Berger–Hopf Standard Model scientific collection.
          </p>
          <div className="footer-links">
            <a href={REPOSITORY}>Academic repository</a>
            <a href={`${SCIENCE}/LICENSE.md`}>License</a>
            <a href="#top">Back to the future ↑</a>
            <a href={freshShareURL}>Fresh Facebook sharing link ↗</a>
          </div>
          <MuseumSoundtrack />
          <OpenReviewInvitation />
          <AIAccess />
        </footer>
      </MuseumDeck>
    </main>
  );
}
