'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- SVG contains the accessible computed diagram. */
import { useState } from 'react';
import Image from 'next/image';
import { ScienceConsole, useSceneClock } from './science-console';
import { REPOSITORY } from './exhibits';
import { EinsteinRingTour } from './einstein-ring-tour';
import {
  trackerCenter,
  trackerExample,
  trackerFrame,
  trackerCodeRevision,
  trackerPaperRevision,
  trackerVersion,
  trackerPilot,
  trackerJoint,
  trackerAtlas,
  trackerReviewerRevision,
  trackerTargetProgram,
} from '../lib/blackhole-tracker';

const colors = ['#71e5eb', '#ffbc77', '#bda7f5'];
const source = `${REPOSITORY}/tree/${trackerCodeRevision}/products/blackhole_tracker`;
const productFiles = `${REPOSITORY}/blob/${trackerCodeRevision}/products/blackhole_tracker`;
const reviewerGuide = `${REPOSITORY}/blob/${trackerReviewerRevision}/products/blackhole_tracker/REVIEWER.md`;
const paper = `${REPOSITORY}/blob/${trackerPaperRevision}/papers/bhsm_blackhole_tracker_20261021`;
const assets = './research/blackhole-tracker/';
const pilotAssets = `${assets}pilot-20261022-v1/`;
const jointAssets = `${assets}joint-20261022-v2/`;
const atlasAssets = `${assets}candidate-atlas-20261023-v3/`;
const targetAssets = `${assets}primary-target-20261023-v1/`;
const primaryTarget = trackerTargetProgram.primary_investigation_target;
const envelopmentSource = `${REPOSITORY}/blob/7ebc9f226e0d9abc68e2ec61c90a8b262081c733/docs/BHSM_TRACKER_ENVELOPMENT_SEARCH_CLARIFICATION_20261023.md`;

export function BlackholeTracker({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (value: boolean) => void;
}) {
  const [playing, setPlaying] = useState(true);
  const [anchor, setAnchor] = useState({ epoch: 2015, time: 0 });
  const [massScale, setMassScale] = useState(1);
  const { ref, time } = useSceneClock(motion && playing, Infinity, 0, 'independent');
  // A forward/back presentation loop. The declared trajectory remains linear;
  // the reverse leg is explicitly replay, not reversed physical motion.
  const phase = (anchor.epoch - 2015 + (time - anchor.time) * 0.5) % 20;
  const epoch =
    playing && motion
      ? 2015 + (phase <= 10 ? phase : 20 - phase)
      : anchor.epoch;
  const frame = trackerFrame(epoch, massScale);
  const screen = (p: number[]) => [310 + p[0] * 4, 238 - p[1] * 4];
  const center = screen(frame.center);
  const from = trackerCenter(2015),
    to = trackerCenter(2025);
  const inset = (p: number[]) => [
    42 + ((p[0] - from[0]) / (to[0] - from[0])) * 234,
    64 + ((p[1] - from[1]) / (to[1] - from[1])) * 68,
  ];
  const currentInset = inset(frame.center);
  const pause = () => {
    setAnchor({ epoch, time });
    setPlaying(!playing);
  };
  const chooseEpoch = (value: number) => {
    setAnchor({ epoch: value, time });
    setPlaying(false);
  };
  return (
    <ScienceConsole
      id="blackhole-tracker"
      number="07"
      label="Blackhole Tracker · BHSM lensing"
      title="Follow the lens. Test the interpretation."
      intro="Hunt for gravitational topography on the BHSM hypersurface and ask which kinds of envelopment could produce it. Gaia18ajz is our provisional primary potential black hole, alongside a published black-hole benchmark and a brown-dwarf comparison. Its independent tracker evidence remains open. Explore the historical Candidate Atlas and a separate synthetic lensing animation."
      accent="cyan"
    >
      <EinsteinRingTour motion={motion} setMotion={setMotion} />
      <div className="tracker-theatre" ref={ref}>
        <div className="tracker-scene">
          <div className="tracker-scene-cap">
            <b>INDEPENDENT SYNTHETIC TEACHING MODEL</b>
            <span>{epoch.toFixed(2)} · synthetic observer year</span>
          </div>
          <svg
            viewBox="0 0 620 460"
            role="img"
            aria-labelledby="tracker-map-title tracker-map-desc"
          >
            <title id="tracker-map-title">
              Three synthetic sources and their lensed image pairs
            </title>
            <desc id="tracker-map-desc">
              Computed ordinary point-lens images at the selected synthetic
              observer year. Crosses are declared source positions; colored
              points form independent image pairs. The dashed circle is an
              angular Einstein scale, not a measured surface or horizon. These
              are invented model inputs, separate from Gaia18ajz and the
              historical events.
            </desc>
            {[-40, -20, 0, 20, 40].map((v) => (
              <g key={v} stroke="#272736" strokeWidth="1">
                <path d={`M${310 + v * 4} 54V422M62 ${238 - v * 4}H558`} />
                <text
                  x={310 + v * 4}
                  y="445"
                  textAnchor="middle"
                  fill="#b4a8c1"
                  stroke="none"
                  fontSize="12"
                >
                  {v}
                </text>
              </g>
            ))}
            <circle
              cx={center[0]}
              cy={center[1]}
              r={frame.theta * 4}
              fill="none"
              stroke="#7c6b8c"
              strokeWidth="1.5"
              strokeDasharray="5 6"
            />
            {frame.pairs.map((pair, i) => {
              const s = screen(pair.source),
                p = screen(pair.plus),
                m = screen(pair.minus);
              return (
                <g key={i} stroke={colors[i]}>
                  <path
                    d={`M${s[0] - 5} ${s[1] - 5}l10 10m-10 0l10 -10`}
                    strokeWidth="1.5"
                  />
                  <circle
                    cx={p[0]}
                    cy={p[1]}
                    r="6"
                    fill={colors[i]}
                    stroke="none"
                  />
                  <circle
                    cx={m[0]}
                    cy={m[1]}
                    r="5"
                    fill="#080911"
                    strokeWidth="2.5"
                  />
                  <text
                    x={p[0] + 10}
                    y={p[1] + 4}
                    fill={colors[i]}
                    stroke="none"
                    fontSize="13"
                  >
                    {i + 1}+
                  </text>
                  <text
                    x={m[0] + 10}
                    y={m[1] + 4}
                    fill={colors[i]}
                    stroke="none"
                    fontSize="13"
                  >
                    {i + 1}−
                  </text>
                </g>
              );
            })}
            <path
              d={`M${center[0] - 7} ${center[1]}h14m-7 -7v14`}
              stroke="#fff3de"
              strokeWidth="2"
            />
            <text x="62" y="27" fill="#e6d9ef" fontSize="13">
              Tangent-plane positions · milliarcseconds (mas)
            </text>
            <text x="62" y="416" fill="#b4a8c1" fontSize="12">
              Dashed circle: Einstein angular scale · white cross: lens center
            </text>
          </svg>
          <p className="tracker-legend">
            × declared synthetic source · ● positive image · ○ negative image.
            Each color is a separate source. This teaching model supplies every
            position and mass; no Gaia18ajz lens track is measured here.
          </p>
        </div>
        <aside className="tracker-instruments">
          <div className="tracker-controls">
            <label htmlFor="tracker-epoch">
              Synthetic observer year{' '}
              <output htmlFor="tracker-epoch">{epoch.toFixed(2)}</output>
            </label>
            <input
              id="tracker-epoch"
              type="range"
              min="2015"
              max="2025"
              step="0.01"
              value={epoch}
              onChange={(e) => chooseEpoch(Number(e.target.value))}
            />
            <div className="tracker-epoch-buttons">
              {[2015, 2020, 2025].map((year) => (
                <button key={year} onClick={() => chooseEpoch(year)}>
                  {year}
                </button>
              ))}
            </div>
            <button
              className="tracker-play"
              onClick={() => {
                if (!motion) {
                  setMotion(true);
                  setAnchor({ epoch, time });
                  setPlaying(true);
                } else pause();
              }}
            >
              {playing && motion
                ? 'Pause animation'
                : motion
                  ? 'Play animation'
                  : 'Enable animation'}
            </button>
            <small>
              {!motion
                ? 'Museum motion is off. Step through observer years manually.'
                : 'Playback moves forward, then replays backward. Its speed is illustrative.'}
            </small>
            <label htmlFor="tracker-mass">
              Declared synthetic mass{' '}
              <output htmlFor="tracker-mass">
                {Math.round(frame.mass).toLocaleString('en-US')} M☉
              </output>
            </label>
            <input
              id="tracker-mass"
              type="range"
              min="0.5"
              max="2"
              step="0.05"
              value={massScale}
              onChange={(e) => setMassScale(Number(e.target.value))}
            />
            <small>
              This is a supplied forward-model input, not a fit or mass
              measurement. Default: 100,000 M☉.
            </small>
          </div>
          <div className="tracker-center-inset">
            <h4>The declared synthetic center · enlarged</h4>
            <svg
              viewBox="0 0 320 168"
              role="img"
              aria-label={`Declared center track from 2015 to 2025; selected position ${frame.center.map((v) => v.toFixed(3)).join(', ')} milliarcseconds`}
            >
              <path d="M42 64L276 132" stroke="#71e5eb" strokeWidth="2" />
              <circle
                cx={currentInset[0]}
                cy={currentInset[1]}
                r="6"
                fill="#fff3de"
              />
              <text x="30" y="48" fill="#d6c9e1" fontSize="14">
                2015
              </text>
              <text x="246" y="155" fill="#d6c9e1" fontSize="14">
                2025
              </text>
              <text x="30" y="23" fill="#a69bb5" fontSize="12">
                Displacement: +0.650, −0.380 mas
              </text>
            </svg>
            <p>μ = (+0.065, −0.038) mas / observer year</p>
          </div>
        </aside>
      </div>
      <div
        className="tracker-readouts"
        aria-live={playing && motion ? 'off' : 'polite'}
      >
        <div>
          <small>Einstein angular scale</small>
          <strong>{frame.theta.toFixed(3)} mas</strong>
          <span>An angular lens scale</span>
        </div>
        <div>
          <small>Source 1 image ratio</small>
          <strong>{Math.exp(frame.pairs[0].lnFluxRatio).toFixed(3)}</strong>
          <span>Absolute magnification ratio</span>
        </div>
        <div>
          <small>Source 1 delay</small>
          <strong>{frame.pairs[0].delaySeconds.toFixed(4)} s</strong>
          <span>Ordinary monopole calculation</span>
        </div>
      </div>
      <div className="tracker-meaning">
        <h4>The BHSM hunt: distinguish kinds of envelopment</h4>
        <p>
          Gravity is interpreted as BHSM surface topography. The hunt begins
          with a supported gravitational imprint, constrains its observable
          geometry and asks which envelopments could produce that response. The
          author describes this as a hunt on the hypersphere surface. Lens
          coordinates describe a projected spacetime exterior in a declared
          frame; they do not measure a global hypersphere radius or a
          microscopic core coordinate.
        </p>
        <p>
          Norman calls the spacetime differential at the envelope boundary the{' '}
          <b>BHSM envelope-boundary differential</b>. This author-defined usage
          is broader than conventional rotational frame dragging. Ordinary
          rotating matter can produce conventional frame dragging; that effect
          alone is not a black-hole filter. The current tracker does not measure
          an envelope-boundary jump or a spin signature.
        </p>
        <p>
          The research question includes compact configurations and extended
          gravitational structure, including dark-matter-like interpretations.
          Distinguishing them needs explicit response models and observations
          that probe the difference. Within the scalar weak-field, thin-lens
          model, an exterior point-mass response can also arise outside an
          ordinary finite circular projected mass distribution. Identical
          optical responses remain degenerate. The adopted Einstein/GHY exterior
          and its boundary representation describe one optical response, counted
          once; they add no second force or mass.
        </p>
        <p>
          Passing a conditional light-curve screen alone does not validate a
          gravitational origin or identify a black hole. Physical interface
          shape, a horizon and microscopic core properties need further
          evidence. The optional R1 calculation in the research app tests a
          specified conditional response. The animation supplies its synthetic
          parameters and performs no fit. The present release has no validated
          extended-halo classifier; an unresolved state remains unresolved.
        </p>
        <a href={envelopmentSource}>
          Author-defined envelopment search, terminology and scope ↗
        </a>
      </div>
      <section
        className="tracker-primary-target"
        aria-labelledby="tracker-primary-target-title"
      >
        <p className="eyebrow">
          PRIMARY INVESTIGATION PROGRAM · EVIDENCE REVIEW OPEN
        </p>
        <h4 id="tracker-primary-target-title">
          {primaryTarget.event_id} · {primaryTarget.investigation_category}
        </h4>
        <p>
          Published annual-parallax lensing and lens-light constraints make
          Gaia18ajz a useful lead for deeper investigation. This designation
          prioritizes research; it is a previously published candidate, and the
          tracker has not independently established its lens identity or mass.
          Aliases: {primaryTarget.aliases.join(' · ')}.
        </p>
        <div className="tracker-target-state" role="status">
          <b>Publication held for evidence review.</b> The candidate/evidence
          release is awaiting its final freeze. Engine mass, lens distance,
          angular Einstein scale, absolute lens motion and accepted mass
          interval are all unavailable. No measured Gaia18ajz lens trajectory is
          supplied to this animation.
        </div>
        <div className="tracker-targets tracker-comparisons">
          <article>
            <h5>Primary lead · Gaia18ajz</h5>
            <strong>POTENTIAL BLACK HOLE</strong>
            <p>
              Near/far lens branches and stellar/remnant population priors
              retain lower-mass alternatives. Gaia source astrometry, estimated
              errors, error rescaling and a blending prior require review.
            </p>
          </article>
          <article>
            <h5>Known benchmark · OB110462</h5>
            <strong>PUBLISHED BLACK-HOLE REFERENCE</strong>
            <p>
              OGLE-2011-BLG-0462 / MOA-2011-BLG-191 has published joint
              evidence. Independent tracker recovery is still unaccepted; the
              retained failed model/noise alternatives remain part of the
              record.
            </p>
          </article>
          <article>
            <h5>Comparison · OGLE-2007-BLG-224</h5>
            <strong>PUBLISHED BROWN-DWARF INTERPRETATION</strong>
            <p>
              A nearby, fast lens can be substellar. Published parallax and
              angular-scale evidence identify this comparison as a brown dwarf;
              speed, proximity or short duration alone cannot classify a black
              hole. The tracker has not independently recovered this control.
            </p>
          </article>
        </div>
        <details>
          <summary>All eight published Gaia18ajz alternatives</summary>
          <p>
            These are published posterior summaries under stated priors, not
            engine measurements. Branch weights compare near/far branches within
            the same mode and prior; they are not black-hole probabilities and
            cannot be compared as a global ranking.
          </p>
          <div className="tracker-table-scroll">
            <table>
              <caption>
                Literature-conditional alternatives · Howil et al., Tables 9–10
              </caption>
              <thead>
                <tr>
                  <th scope="col">Mode</th>
                  <th scope="col">Mass prior</th>
                  <th scope="col">Branch</th>
                  <th scope="col">Branch weight</th>
                  <th scope="col">Mass posterior median (M☉)</th>
                </tr>
              </thead>
              <tbody>
                {primaryTarget.literature_alternatives.map((alternative) => (
                  <tr
                    key={`${alternative.photometric_mode}-${alternative.mass_prior}-${alternative.branch}`}
                  >
                    <td>{alternative.photometric_mode}</td>
                    <td>{alternative.mass_prior}</td>
                    <td>{alternative.branch}</td>
                    <td>{alternative.published_branch_weight}</td>
                    <td>{alternative.published_mass_posterior_median_msun}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
        <p>
          Next evidence: {primaryTarget.next_observation} A common moving-lens
          test also needs admitted lens positions, a common angular frame,
          native epoch conventions and covariance. The frozen 1,808-model
          spectrum currently admits zero measured lens tracks. Source/event
          directions alone cannot provide them.
        </p>
        <div className="tracker-actions">
          <a href={`${targetAssets}PRIMARY_TARGET_PROGRAM.json`} download>
            Target program and explicit unknowns ↓
          </a>
          <a href={`${targetAssets}TARGET_EVIDENCE_STATUS.json`}>
            Evidence freeze status and hash ↗
          </a>
          <a href={primaryTarget.source.url}>Primary candidate publication ↗</a>
          <a
            href={
              trackerTargetProgram.known_black_hole_validation_benchmark
                .source_url
            }
          >
            Known black-hole publication ↗
          </a>
          <a href={trackerTargetProgram.non_black_hole_comparison.source_url}>
            Brown-dwarf comparison publication ↗
          </a>
          <a href={reviewerGuide}>
            BHSM researcher installation and replay guide ↗
          </a>
        </div>
        <p className="tracker-local-note">
          This program is separate from the preserved 155-direction atlas and
          1,808-model spectrum. It changes neither frozen dataset nor the
          counts: zero established new black holes and zero accepted independent
          known-black-hole recoveries. The public Museum remains a
          demonstration; the local research app performs inference.
        </p>
      </section>
      <section className="tracker-atlas" aria-labelledby="tracker-atlas-title">
        <p className="eyebrow">CANDIDATE ATLAS · SOURCE / EVENT DIRECTIONS</p>
        <h4 id="tracker-atlas-title">
          155 historical events. Three investigation targets.
        </h4>
        <p>
          The complete inventory combines the frozen 100-event pilot with 59
          published parallax events, removing four verified overlaps: 100 + 59 −
          4 = 155. It retains all 89 inadequate pilot screens and all 33
          unavailable native tables in the older cohort. Review flags remain
          visible. These three targets have different evidence; none is a new
          black-hole identification or a measured black-hole mass.
        </p>
        <figure className="tracker-atlas-map">
          <a href={`${atlasAssets}candidate_inventory_sky.png`}>
            <Image
              src={`${atlasAssets}candidate_inventory_sky.png`}
              width="1800"
              height="1225"
              loading="lazy"
              unoptimized
              alt="Catalog source/event directions for 155 historical events, highlighting three investigation targets; a separate published black-hole benchmark has unresolved engine recovery. No present lens position, depth, motion or error region is shown."
            />
          </a>
          <figcaption>
            Catalog directions locate the source/event on the sky. They do not
            locate the unseen lens today. Lens position, epoch, uncertainty,
            distance, mass and absolute proper motion remain unavailable.
          </figcaption>
        </figure>
        <div className="tracker-targets tracker-atlas-targets">
          {trackerAtlas.targets.map((target) => (
            <article key={target.event_id}>
              <h5>{target.event_id}</h5>
              <strong>
                {target.event_id.endsWith('PAR-13')
                  ? 'DISPUTED, PRIOR-CONDITIONAL POSSIBILITY'
                  : 'PHOTOMETRIC FOLLOW-UP SCREEN ONLY'}
              </strong>
              <p>
                Source/event direction: RA {target.source_direction.ra_hms}, Dec{' '}
                {target.source_direction.dec_dms} · J2000 catalog equatorial.
                Position epoch and angular uncertainty: unavailable.
              </p>
              <p>
                {target.event_id.endsWith('PAR-13')
                  ? 'Published BH-scale possibilities depend on unreliable Gaia source astrometry. An alternative OGLE source-motion estimate supports a lower conditional mass. This event has not been fit with a validated tracker parallax route.'
                  : 'Qualified by the frozen historical photometric screen. Neither the light-curve timescale nor passing that screen discriminates a black hole from other lens or source models.'}
              </p>
              <p className="tracker-local-note">
                {target.event_id.endsWith('3092')
                  ? 'Known aliases include OGLE-2007-BLG-057 / MOA-2007-BLG-027; prior literature is retained.'
                  : target.event_id.endsWith('PAR-13')
                    ? 'Known alias: OGLE-2002-BLG-061. Source-motion, native reduction and calibration checks remain open.'
                    : 'Archival parallax, angular-scale, lens-light and alternative-model checks are needed.'}
              </p>
            </article>
          ))}
        </div>
        <p>
          <b>Separate published benchmark: OGLE-2011-BLG-0462 / OB110462.</b>{' '}
          Published HST astrometry, photometric parallax and lens-light limits
          support its black-hole interpretation. That literature label is
          separate from these 155 events. The tracker has not independently
          established a reliable recovery: its 2025 numerical stage remains
          unresolved, and the frozen 2023 alternatives below fail adequacy.
        </p>
        <p>
          In BHSM, any eventual adequate compact-lens inference describes one
          Einstein/GHY optical exterior, counted once. Conditional gravitational
          geometry has a BHSM surface-topography interpretation; this inventory
          does not establish a microscopic core, horizon or physical interface
          shape.
        </p>
        <div className="tracker-actions">
          <a
            className="tracker-primary"
            href={`${assets}BHSM_Blackhole_Tracker_Product_${trackerVersion}.zip`}
            download
          >
            Download the app with Candidate Atlas ↓
          </a>
          <a href={`${assets}BHSM_Candidate_Atlas_Metadata_v3.zip`} download>
            Complete metadata and offline reconstruction ↓
          </a>
          <a href={`${atlasAssets}ATLAS_PROVENANCE.json`}>
            Atlas counts, directions and provenance ↗
          </a>
          <a href={`${productFiles}/CANDIDATE_ATLAS.md`}>
            Filtering, export and replay guide ↗
          </a>
          <a href="https://doi.org/10.3847/1538-4357/adbe6e">
            Published known-system evidence ↗
          </a>
          <a href="https://arxiv.org/html/2107.13701v1">
            Later conditional parallax reanalysis ↗
          </a>
        </div>
        <p className="tracker-local-note">
          Open <code>Start_Blackhole_Tracker_Atlas.cmd</code> after
          installation, or run{' '}
          <code>python -m bhtracker serve --page atlas --open</code>. The local
          atlas supports search, evidence tiers, quality flags, an optional
          separate benchmark marker, CSV export and a full-inventory JSON
          replay. SHA-256 checks byte consistency; it does not establish source
          authenticity or validate a physical model.
        </p>
      </section>
      <section
        className="tracker-real-data"
        aria-labelledby="tracker-real-data-title"
      >
        <p className="eyebrow">
          REAL OBSERVATION PILOT · FROZEN 22 OCTOBER 2026
        </p>
        <h4 id="tracker-real-data-title">
          100 historical events. Two archival follow-up targets. No new
          black-hole interpretation.
        </h4>
        <p>
          The separate native-magnitude route processed all 76,344 measurements
          from the frozen OGLE-III pilot, including every inadequate or
          unresolved case. Eleven events passed the declared diagonal-noise
          chi-square screen; 89 require a better model or noise description. The
          animation above remains a synthetic resolved-image illustration.
        </p>
        <div className="tracker-targets">
          {trackerPilot.targets.map((target) => (
            <article key={target.event_id}>
              <h5>{target.event_id}</h5>
              <strong>MASS UNRESOLVED</strong>
              <p>
                Fitted timescale {target.fitted_tE_days.toFixed(1)} days; local
                conditional error ±{target.sigma_tE_days.toFixed(1)} days. The
                timescale is not a black-hole mass.
              </p>
              <a href={`${pilotAssets}${target.residual_plot}`}>
                View observed light curve and residuals ↗
              </a>
            </article>
          ))}
        </div>
        <p>
          These already published events merit archival calibration, modeling
          and source-association checks under the frozen ranking rule. No
          ongoing peak is assumed. OGLE3-ULENS-3092 is also OGLE-2007-BLG-057 /
          MOA-2007-BLG-027 and has prior literature. Complete novelty clearance
          remains unresolved. Every pilot lens mass, distance, angular proper
          motion and horizon status is unavailable.
        </p>
        <div className="tracker-actions">
          <a href={`${pilotAssets}all_100_results.csv`} download>
            All 100 results · CSV ↓
          </a>
          <a href={`${pilotAssets}followup_ranking.csv`} download>
            Qualified follow-up ranking · CSV ↓
          </a>
          <a href={`${pilotAssets}protocol_v1.json`}>Frozen protocol ↗</a>
          <a href={`${paper}/real_data_pilot_20261022/README.md`}>
            Research evidence and reproduction ↗
          </a>
        </div>
        <p className="tracker-local-note">
          The separate 2022 known-system benchmark was ingested, but its simple
          photometric model is inadequate. HST timing/frame metadata prevent a
          validated joint mass fit. Neither ordinary lensing agreement nor a
          failed simple fit establishes a BHSM core or envelope mechanism.
        </p>
      </section>
      <section
        className="tracker-real-data"
        aria-labelledby="tracker-joint-title"
      >
        <p className="eyebrow">
          SEPARATE 2023 KNOWN-SYSTEM BENCHMARK · JOINT RESEARCH
        </p>
        <h4 id="tracker-joint-title">
          Three declared models fail adequacy. No supported mass.
        </h4>
        <p>
          The joint route reads 12,500 selected corrected OGLE measurements, 21
          HST magnitudes and 21 two-coordinate angular rows at 11 dated visits
          for OGLE-2011-BLG-0462 / MOA-2011-BLG-191. All original 15,533 OGLE
          rows, declared exclusions and calibrations remain in its source
          record. This 2023 version is separate from the frozen pilot and the
          ambiguous 2022 HST export.
        </p>
        <div className="tracker-targets tracker-models">
          {trackerJoint.candidates.map((candidate) => (
            <article key={candidate.id}>
              <h5>
                {candidate.id} · {candidate.label}
              </h5>
              <strong>ADEQUACY FAILED</strong>
              <p>{candidate.adequacy_reason}</p>
            </article>
          ))}
        </div>
        <p>
          Import, fitting, export and saved-state replay work, but none of these
          candidates supplies an accepted mass interval. A replay verifies a
          recorded calculation; it does not validate its noise model. The
          object’s published black-hole classification is prior literature
          evidence. This run has not independently reproduced a reliable
          known-black-hole mass or established a new black-hole interpretation.
        </p>
        <p>
          Before a supported new target, the next evidence is specific:
          photometric clocks and variance calibration; matched-star, seeing and
          detector controls; angular covariance, frame transformations and
          effective epoch weights; and independent lens/source flux limits.
          Absolute distances and velocities also need an absolute reference
          frame. The calibration-data request below is prepared for author
          review and has not been sent.
        </p>
        <div className="tracker-actions">
          <a href={`${assets}BHSM_OB110462_2023_SourcePack_v1.zip`} download>
            Reviewed 2023 native source pack · ZIP ↓
          </a>
          <a href={`${jointAssets}joint_noise_diagnostics.png`}>
            Known-system residual diagnostics ↗
          </a>
          <a href={`${jointAssets}JOINT_PROVENANCE.json`}>
            Counts, failed statuses and exact evidence hashes ↗
          </a>
          <a href={`${jointAssets}SOURCEPACK_CITATIONS_AND_RIGHTS.md`}>
            Native data attribution and rights ↗
          </a>
          <a href={`${paper}/joint_known_system_20261022/README.md`}>
            All failed alternatives and frozen evidence ↗
          </a>
          <a
            href={`${jointAssets}MANUAL_CALIBRATION_DATA_REQUEST_TEMPLATE.txt`}
            download
          >
            Manual calibration-data request template ↓
          </a>
        </div>
        <p className="tracker-local-note">
          BHSM interpretation stays explicit: one compact-lens optical exterior,
          counted once. No reliable mass, horizon, core state or measured
          membrane deformation follows from these inadequate fits. Native
          source-pack observations retain their original authors’ attribution
          and rights; BHSM licensing does not replace them.
        </p>
      </section>
      <section
        className="tracker-access"
        aria-labelledby="tracker-access-title"
      >
        <div>
          <p className="eyebrow">RESEARCH APP · {trackerVersion}</p>
          <h4 id="tracker-access-title">
            Run a complete analysis on your computer.
          </h4>
          <p>
            The Museum animation runs in your browser. The Python app performs
            inference with uncertainties, diagnostics and a portable replay
            record. The Candidate Atlas adds reviewed historical metadata; the
            resolved-image demonstrations are synthetic. The unresolved
            photometry page accepts native brightness/error rows and preserves
            their provenance; it does not invent resolved images or lens mass.
          </p>
          <div className="tracker-actions">
            <a
              className="tracker-primary"
              href={`${assets}BHSM_Blackhole_Tracker_Product_${trackerVersion}.zip`}
              download
            >
              Download the app · portable source ZIP ↓
            </a>
            <a href={reviewerGuide}>Installation &amp; reviewer guide ↗</a>
            <a href={`${assets}BHSM_Blackhole_Tracker_${trackerVersion}.pdf`}>
              Read the reviewed manuscript ↗
            </a>
          </div>
        </div>
        <ol>
          <li>
            <b>Install.</b> Extract the ZIP. With Python 3.11+, open{' '}
            <code>product/</code> and run{' '}
            <code>Start_Blackhole_Tracker.cmd</code> on Windows. This creates
            its own <code>product/.venv/</code>; the first installation needs
            package-index access. Other systems: use a dedicated Python
            environment, open <code>product/</code>, run{' '}
            <code>python -m pip install .</code>, then{' '}
            <code>python -m bhtracker serve --open</code>. For joint research,
            explicitly choose <code>Start_Blackhole_Tracker_Joint.cmd</code> or
            install <code>&quot;.[astrometry]&quot;</code> in that environment.
            This adds Astropy only when requested. For inventory review without
            fitting, choose <code>Start_Blackhole_Tracker_Atlas.cmd</code> or{' '}
            <code>python -m bhtracker serve --page atlas --open</code>.
          </li>
          <li>
            <b>Validate the synthetic example.</b> Load Nearby compact-mass
            track → Validate dataset → Run fit. Read status, uncertainties,
            residuals and the explicit BHSM interpretation. This supplied
            example tests the software with synthetic measurements; its
            recovered mass and track are not observations of Gaia18ajz.
          </li>
          <li>
            <b>Export and replay.</b> Select Download replay bundle and keep the
            saved ZIP. Use the same installed Python environment and replace the
            input path with that ZIP&apos;s actual location:{' '}
            <code>
              python -m bhtracker replay /path/to/bhsm-analysis-replay.zip
              --output replayed
            </code>
            . If you used the Windows launcher, open a second terminal in{' '}
            <code>product/</code> and use{' '}
            <code>.\.venv\Scripts\python.exe</code> in place of{' '}
            <code>python</code>. Quote paths containing spaces. Inspect{' '}
            <code>replayed/replay_check.json</code>; replay checks the recorded
            calculation, not the physical validity of a model. Candidate Atlas
            exports use their separate JSON workflow:{' '}
            <code>
              python -m bhtracker atlas replay BHSM_candidate_atlas_replay.json
            </code>
            . This preserves every inventory record and flag and does not refit
            data.
          </li>
          <li>
            <b>Move to native observations.</b> Open Unresolved photometry.
            Import the supported OGLE-III <code>.dat</code> files or versioned
            observation JSON described in the{' '}
            <a href={`${productFiles}/README.md`}>native-data guide</a>. Retain
            native time conventions, uncertainties, source-row identities,
            calibration and documented issues; inspect the observations,
            adequacy checks and residuals before export. Do not turn unresolved
            photometry into invented image positions or mass. For the separate
            known-system research route, explicitly install the astrometry
            extra, open Joint astrometry research and import its reviewed
            source-pack ZIP. Its retained failed adequacy checks remain visible.
          </li>
          <li>
            <b>Review the target and angular-track evidence.</b> In the
            installed app, open Primary target, Evidence spectrum or Moving
            lens. The spectrum retains all 1,808 model records and supports
            JSON/CSV view export and replay; those records are not 1,808
            distinct objects. Moving lens requires admitted lens positions,
            epochs, frame and covariance. Its supplied example is synthetic. Use{' '}
            <code>Start_Blackhole_Tracker_Moving_Lens.cmd</code> or{' '}
            <code>python -m bhtracker serve --page skytrack --open</code> and
            follow the{' '}
            <a href={`${productFiles}/SKYTRACK.md`}>measured-track guide</a>.
            Its result JSON has a separate replay command:{' '}
            <code>
              python -m bhtracker skytrack replay BHSM_Moving_Lens_Replay.json
            </code>
            . Source/event directions and duration cannot supply a lens track.
          </li>
        </ol>
        <p className="tracker-target-state">
          Gaia18ajz is the provisional primary research lead. Its independent
          native-data analysis and physical validation remain open, and the
          candidate/evidence freeze is pending. A synthetic validation or
          successful export/replay does not complete those steps. The available
          download is the version shown above; this target program does not
          change its frozen historical results or establish a new discovery.
        </p>
        <p className="tracker-local-note">
          The app opens a loopback address on your own computer after launch.
          The Museum does not upload measurements or provide a hosted fitting
          service. Dependencies install from your configured Python package
          index; fitting needs no API key.
        </p>
        <details>
          <summary>Wheel, hashes and exact source record</summary>
          <p>
            Prefer an existing Python environment?{' '}
            <a
              href={`${assets}bhsm_blackhole_tracker-${trackerVersion}-py3-none-any.whl`}
              download
            >
              Download the reviewed wheel
            </a>
            , install with <code>python -m pip install path/to/the.whl</code>,
            then launch as above. Joint research instead uses the explicit
            extra:{' '}
            <code>
              python -m pip install &quot;path/to/the.whl[astrometry]&quot;
            </code>
            . See{' '}
            <a href={`${productFiles}/JOINT_RESEARCH.md`}>
              joint setup and replay guidance
            </a>
            .
          </p>
          <p>
            <a href={`${assets}DISTRIBUTION.json`}>
              Download hashes and provenance
            </a>{' '}
            · <a href={source}>Pinned product source ↗</a> ·{' '}
            <a href={`${paper}/real_data_pilot_20261022/README.md`}>
              Correction and real-data evidence ↗
            </a>{' '}
            ·{' '}
            <a href={`${productFiles}/bhtracker/examples/nearby_motion.json`}>
              Synthetic measurements with covariance ↗
            </a>{' '}
            ·{' '}
            <a
              href={`${assets}BHSM_Blackhole_Tracker_Source_${trackerVersion}.zip`}
              download
            >
              Complete manuscript, code and pilot source packet ↓
            </a>{' '}
            ·{' '}
            <a href={`${paper}/manuscript/main.tex`}>
              Pinned manuscript source ↗
            </a>
          </p>
          <p>
            Research redistribution is subject to the included{' '}
            <a href={`${assets}LICENSE.md`}>repository license</a> and{' '}
            <a href={`${assets}ACADEMIC_USE.md`}>academic-use notice</a>. Keep
            both notices with either download.{' '}
            <a href={`${assets}history/0.2.0rc2/DISTRIBUTION.json`}>
              Historical 0.2.0rc2 artifacts and hashes
            </a>{' '}
            and the{' '}
            <a href={`${assets}DISTRIBUTION_0.2.0rc3.json`}>
              exact 0.2.0rc3 receipt
            </a>{' '}
            remain preserved. Versioned rc3 artifacts stay at the release root
            beside that versioned receipt. The{' '}
            <a href={`${assets}DISTRIBUTION_0.2.0rc4.json`}>
              exact 0.2.0rc4 receipt
            </a>{' '}
            and the{' '}
            <a href={`${assets}DISTRIBUTION_0.2.0rc5.json`}>
              exact 0.2.0rc5 receipt
            </a>{' '}
            retain their versioned artifacts alongside them.
          </p>
          <p>
            Exhibit constants, geometry and declared truth are copied from the
            pinned product’s nearby-motion example. Only the noise-free ordinary
            monopole is animated; this view has no optimizer, noise, tidal shear
            or R1 response. It has been compared with the product forward
            calculation at all nine source/epoch rows.
          </p>
          <p>
            Geometry: lens{' '}
            {trackerExample.geometry.D_l_pc.toLocaleString('en-US')} pc; source{' '}
            {trackerExample.geometry.D_s_pc.toLocaleString('en-US')} pc; lens
            redshift {trackerExample.geometry.z_l}. Source positions are fixed
            inputs for this illustration; the research fit allows independent
            source positions per measurement row.
          </p>
        </details>
      </section>
    </ScienceConsole>
  );
}
