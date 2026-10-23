'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- SVG contains the accessible computed diagram. */
import { useState } from 'react';
import { ScienceConsole, useSceneClock } from './science-console';
import { REPOSITORY } from './exhibits';
import { EinsteinRingTour } from './einstein-ring-tour';
import {
  trackerCenter,
  trackerExample,
  trackerFrame,
  trackerCodeRevision,
  trackerPaperRevision,
} from '../lib/blackhole-tracker';

const colors = ['#71e5eb', '#ffbc77', '#bda7f5'];
const source = `${REPOSITORY}/tree/${trackerCodeRevision}/products/blackhole_tracker`;
const productFiles = `${REPOSITORY}/blob/${trackerCodeRevision}/products/blackhole_tracker`;
const paper = `${REPOSITORY}/blob/${trackerPaperRevision}/papers/bhsm_blackhole_tracker_20261021`;
const assets = './research/blackhole-tracker/';

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
  const { ref, time } = useSceneClock(
    motion && playing,
    Infinity,
    0,
    'musical',
  );
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
      intro="Blackhole Tracker reconstructs a compact configuration’s effective mass, position and motion from resolved image pairs, magnification ratios and time delays, with the supplied full measurement covariance. Its BHSM description interprets this same exterior response once."
      accent="cyan"
    >
      <EinsteinRingTour motion={motion} setMotion={setMotion} />
      <div className="tracker-theatre" ref={ref}>
        <div className="tracker-scene">
          <div className="tracker-scene-cap">
            <b>SYNTHETIC FORWARD VIEW</b>
            <span>{epoch.toFixed(2)} · observer year</span>
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
              Computed ordinary point-lens images at the selected observer year.
              Crosses are declared source positions; colored points form
              independent image pairs. The dashed circle is an angular Einstein
              scale, not a measured surface or horizon.
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
            × declared source · ● positive image · ○ negative image. Each color
            is a separate source; no source trajectory is inferred here.
          </p>
        </div>
        <aside className="tracker-instruments">
          <div className="tracker-controls">
            <label htmlFor="tracker-epoch">
              Observer year{' '}
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
                : 'Playback follows the music’s swells, then replays backward. Observer-year positions stay calculated; playback speed is illustrative.'}
            </small>
            <label htmlFor="tracker-mass">
              Declared mass{' '}
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
            <h4>The same moving center · enlarged</h4>
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
        <h4>The BHSM interpretation</h4>
        <p>
          The fitted monopole is the effective gravitational mass of a
          BHSM-described compact configuration. Its center and proper motion
          track that same optical configuration in the supplied frame. The
          adopted Einstein/GHY exterior and its boundary representation describe
          one optical potential, counted once.
        </p>
        <p>
          A supplied boundary radius is a declared modeling surface. This
          animation does not measure a hard surface, horizon, core motion or
          envelope deformation. The optional R1 calculation in the research app
          tests a specified conditional response; an unresolved state remains
          unresolved.
        </p>
      </div>
      <section
        className="tracker-access"
        aria-labelledby="tracker-access-title"
      >
        <div>
          <p className="eyebrow">RESEARCH APP · 0.2.0rc2</p>
          <h4 id="tracker-access-title">
            Run a complete analysis on your computer.
          </h4>
          <p>
            The Museum animation runs in your browser. The Python app performs
            inference with uncertainties, diagnostics and a portable replay
            record. All bundled examples are synthetic; new compact-lens
            candidates require observational evidence and independent follow-up.
          </p>
          <div className="tracker-actions">
            <a
              className="tracker-primary"
              href={`${assets}BHSM_Blackhole_Tracker_Product.zip`}
              download
            >
              Download the app · portable source ZIP ↓
            </a>
            <a href={`${productFiles}/REVIEWER.md`}>
              Installation &amp; reviewer guide ↗
            </a>
            <a href={`${paper}/manuscript/main.pdf`}>
              Read the reviewed manuscript ↗
            </a>
          </div>
        </div>
        <ol>
          <li>
            <b>Install.</b> Extract the ZIP. With Python 3.11+, open{' '}
            <code>product/</code> and run{' '}
            <code>Start_Blackhole_Tracker.cmd</code> on Windows. Other systems:{' '}
            <code>python -m pip install .</code>, then{' '}
            <code>python -m bhtracker serve --open</code>.
          </li>
          <li>
            <b>Fit.</b> Load Nearby compact-mass track → Validate dataset → Run
            fit. Read status, uncertainties and the explicit BHSM
            interpretation.
          </li>
          <li>
            <b>Export and replay.</b> Download replay bundle. In the installed
            Python environment run{' '}
            <code>
              python -m bhtracker replay bhsm-analysis-replay.zip --output
              replayed
            </code>
            . Inspect <code>replayed/replay_check.json</code>.
          </li>
        </ol>
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
              href={`${assets}bhsm_blackhole_tracker-0.2.0rc2-py3-none-any.whl`}
              download
            >
              Download the reviewed wheel
            </a>
            , install with <code>python -m pip install path/to/the.whl</code>,
            then launch as above.
          </p>
          <p>
            <a href={`${assets}DISTRIBUTION.json`}>
              Download hashes and provenance
            </a>{' '}
            · <a href={source}>Pinned product source ↗</a> ·{' '}
            <a
              href={`${paper}/review/RC2_SCIENTIFIC_EDITORIAL_REVIEW_20261022.md`}
            >
              Scientific review ↗
            </a>{' '}
            ·{' '}
            <a href={`${productFiles}/bhtracker/examples/nearby_motion.json`}>
              Synthetic measurements with covariance ↗
            </a>
          </p>
          <p>
            Research redistribution is subject to the included{' '}
            <a href={`${assets}LICENSE.md`}>repository license</a> and{' '}
            <a href={`${assets}ACADEMIC_USE.md`}>academic-use notice</a>. Keep
            both notices with either download.
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
