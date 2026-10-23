'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- The computed SVG diagram needs its own accessible description. */

import { useMemo, useState } from 'react';
import { useSceneClock } from './science-console';
import {
  EINSTEIN_CROSSING_SECONDS,
  EINSTEIN_SOURCE_RADIUS,
  einsteinRingFrame,
  einsteinSourceOffset,
} from '../lib/einstein-ring';

const center = { x: 340, y: 250 };
const angularScale = 106;
const stars = Array.from({ length: 142 }, (_, index) => ({
  x: (index * 137.508 + 19) % 680,
  y: (index * index * 17.31 + index * 63.7 + 11) % 520,
  radius: index % 13 === 0 ? 1.7 : index % 4 === 0 ? 1 : 0.65,
  opacity: 0.25 + ((index * 7) % 10) / 15,
}));

function signed(value: number) {
  return `${value > 0 ? '+' : ''}${value.toFixed(2)}`;
}

export function EinsteinRingTour({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (value: boolean) => void;
}) {
  const [journey, setJourney] = useState({
    progress: 0,
    time: 0,
    target: 0.5,
    playing: true,
    touched: false,
  });
  const [sourceGuide, setSourceGuide] = useState(true);
  const stopAt =
    journey.time +
    (journey.target - journey.progress) * EINSTEIN_CROSSING_SECONDS;
  // Let visitors reach the sky before spending the nine-second approach.
  const { ref, time } = useSceneClock(motion && journey.playing, stopAt, 0.6);
  const elapsedProgress = journey.playing
    ? (time - journey.time) / EINSTEIN_CROSSING_SECONDS
    : 0;
  const advanced = journey.progress + elapsedProgress;
  // Reduced-motion visitors start with the annotated ring. A visitor who turns
  // motion off during a crossing keeps the clock's current, frozen position.
  const progress =
    !motion && time === 0 && !journey.touched
      ? 0.5
      : journey.target - advanced < 0.000000001
        ? journey.target
        : advanced;
  const offset = einsteinSourceOffset(progress);
  const frame = useMemo(() => einsteinRingFrame(offset), [offset]);
  const ringImage = frame.images.length === 1;
  const running = motion && journey.playing && progress < journey.target;
  const aligned = Math.abs(offset) < 0.000001;
  const complete = progress >= 1;
  const annotations = !running;
  const sourceX = center.x + offset * angularScale;

  const showSky = () => {
    ref.current?.scrollIntoView({
      block: 'center',
      inline: 'nearest',
      behavior: motion ? 'smooth' : 'instant',
    });
  };
  const chooseOffset = (value: number, revealSky = false) => {
    const next = (value + 2.4) / 4.8;
    setJourney({
      progress: next,
      time,
      target: next < 0.5 ? 0.5 : 1,
      playing: false,
      touched: true,
    });
    if (revealSky) showSky();
  };
  const togglePlayback = () => {
    setJourney({
      progress,
      time,
      target: progress < 0.5 ? 0.5 : 1,
      playing: !running && !complete,
      touched: true,
    });
    if (!running && !complete) showSky();
  };
  const replay = () => {
    setJourney({
      progress: 0,
      time,
      target: 0.5,
      playing: true,
      touched: true,
    });
    showSky();
  };
  const phase = running
    ? offset < 0
      ? 'Approaching alignment'
      : 'Continuing the crossing'
    : aligned
      ? 'Paused at alignment · measure the ring'
      : complete
        ? 'Crossing complete'
        : 'Paused · inspect the images';

  return (
    <section className="einstein-tour" aria-labelledby="einstein-tour-title">
      <div className="einstein-tour-heading">
        <div>
          <p className="eyebrow">
            A moving source. A hidden lens. A circle of light.
          </p>
          <h4 id="einstein-tour-title">Watch an Einstein ring take shape.</h4>
          <p>
            A distant object passes behind a foreground lens. Follow its lensed
            images as they stretch into a ring, then stop to read the geometry.
          </p>
        </div>
        <span className="einstein-scale-notice">NOT TO SCALE</span>
      </div>

      <div className="einstein-theatre">
        <div className="einstein-sky-panel" ref={ref}>
          <div className="einstein-scene-cap">
            <span role="status">
              <i data-running={running} /> {phase}
            </span>
            <b>POINT-LENS SIMULATION</b>
          </div>
          <svg
            className="einstein-sky"
            viewBox="0 0 680 520"
            role="img"
            aria-labelledby="einstein-sky-title einstein-sky-description"
          >
            <title id="einstein-sky-title">
              {aligned
                ? 'An Einstein ring at perfect alignment'
                : 'The extended images of a moving background source'}
            </title>
            <desc id="einstein-sky-description">
              Illustrative view of a finite circular source behind a spherical
              point lens. The lens center is fixed. The source moves relative to
              it; decorative foreground stars remain unchanged. At alignment the
              images join into a ring. The reference scale through its thickness
              is one Einstein angle. The ring is an image of background light,
              not a physical surface or horizon. All displayed angular positions
              are normalized.
            </desc>
            <defs>
              <radialGradient id="einstein-nebula">
                <stop stopColor="#242749" stopOpacity="0.74" />
                <stop offset="0.55" stopColor="#10232f" stopOpacity="0.4" />
                <stop offset="1" stopColor="#060911" stopOpacity="0" />
              </radialGradient>
              <filter
                id="einstein-image-glow"
                x="-4"
                y="-3"
                width="8"
                height="6"
                filterUnits="userSpaceOnUse"
              >
                <feGaussianBlur stdDeviation="0.045" />
              </filter>
              <marker
                id="einstein-cyan-arrow"
                viewBox="0 0 8 8"
                refX="7"
                refY="4"
                markerWidth="7"
                markerHeight="7"
                orient="auto-start-reverse"
              >
                <path d="M0 0L8 4L0 8Z" fill="#71e5eb" />
              </marker>
              <marker
                id="einstein-amber-arrow"
                viewBox="0 0 8 8"
                refX="7"
                refY="4"
                markerWidth="7"
                markerHeight="7"
                orient="auto"
              >
                <path d="M0 0L8 4L0 8Z" fill="#ffbc77" />
              </marker>
              <marker
                id="einstein-lavender-arrow"
                viewBox="0 0 8 8"
                refX="7"
                refY="4"
                markerWidth="7"
                markerHeight="7"
                orient="auto-start-reverse"
              >
                <path d="M0 0L8 4L0 8Z" fill="#bda7f5" />
              </marker>
            </defs>
            <rect width="680" height="520" fill="#060911" />
            <ellipse
              cx="340"
              cy="250"
              rx="330"
              ry="260"
              fill="url(#einstein-nebula)"
            />
            <g aria-hidden="true">
              {stars.map((star, index) => (
                <circle
                  key={index}
                  cx={star.x}
                  cy={star.y}
                  r={star.radius}
                  opacity={star.opacity}
                  fill={index % 9 === 0 ? '#bda7f5' : '#e5e9f2'}
                />
              ))}
              <path
                d="M115 90h12m-6 -6v12M560 382h12m-6 -6v12M508 114h8m-4 -4v8"
                stroke="#e7e4f5"
                strokeWidth="1"
                opacity="0.6"
              />
            </g>

            <g
              transform={`translate(${center.x} ${center.y}) scale(${angularScale} ${-angularScale})`}
            >
              <g
                filter="url(#einstein-image-glow)"
                opacity="0.8"
                aria-hidden="true"
              >
                {frame.images.map((image) => (
                  <path key={image.kind} d={image.path} fill="#71e5eb" />
                ))}
              </g>
              {frame.images.map((image) => (
                <path key={image.kind} d={image.path} fill="#d1fff2" />
              ))}
            </g>

            {sourceGuide && (
              <g className="einstein-source-guide" aria-hidden="true">
                <circle
                  cx={sourceX}
                  cy={center.y}
                  r={EINSTEIN_SOURCE_RADIUS * angularScale}
                  fill="none"
                  stroke="#bda7f5"
                  strokeWidth="1.7"
                  strokeDasharray="4 4"
                />
                <path
                  d={`M${sourceX - 5} ${center.y}h10m-5 -5v10`}
                  fill="none"
                  stroke="#bda7f5"
                  strokeWidth="1.4"
                />
              </g>
            )}

            <g aria-hidden="true">
              <path
                d={`M${center.x - 7} ${center.y}h14m-7 -7v14`}
                stroke="#ffbc77"
                strokeWidth="2.5"
              />
              <circle cx={center.x} cy={center.y} r="2.5" fill="#fff0cf" />
            </g>

            {annotations && (
              <g className="einstein-annotations" aria-hidden="true">
                {aligned && (
                  <>
                    <circle
                      cx={center.x}
                      cy={center.y}
                      r={angularScale}
                      fill="none"
                      stroke="#71e5eb"
                      strokeWidth="1.1"
                      strokeDasharray="4 5"
                    />
                    <line
                      x1={center.x}
                      y1={center.y}
                      x2={center.x + angularScale}
                      y2={center.y}
                      stroke="#71e5eb"
                      strokeWidth="2"
                      markerStart="url(#einstein-cyan-arrow)"
                      markerEnd="url(#einstein-cyan-arrow)"
                    />
                    <text
                      x={center.x + angularScale / 2}
                      y={center.y + 32}
                      textAnchor="middle"
                      className="einstein-angle-label"
                    >
                      θ_E
                    </text>
                    <g
                      transform={`translate(${center.x + angularScale / 2} ${center.y - 26})`}
                      className="einstein-badge einstein-badge-cyan"
                    >
                      <circle r="17" />
                      <text y="7" textAnchor="middle">
                        1
                      </text>
                    </g>
                  </>
                )}
                <path
                  d={`M${center.x - 120} ${center.y + 95}h38L${center.x - 5} ${center.y + 5}`}
                  fill="none"
                  stroke="#ffbc77"
                  strokeWidth="1.7"
                  markerEnd="url(#einstein-amber-arrow)"
                />
                <g
                  transform={`translate(${center.x - 138} ${center.y + 95})`}
                  className="einstein-badge einstein-badge-amber"
                >
                  <circle r="17" />
                  <text y="7" textAnchor="middle">
                    2
                  </text>
                </g>
                {ringImage ? (
                  <path
                    d={`M${center.x - 151} ${center.y - 118}h40L${center.x - angularScale * 0.71} ${center.y - angularScale * 0.71}`}
                    fill="none"
                    stroke="#bda7f5"
                    strokeWidth="1.7"
                    markerEnd="url(#einstein-lavender-arrow)"
                  />
                ) : frame.pointImages ? (
                  <>
                    <line
                      x1={center.x + frame.pointImages.minus[0] * angularScale}
                      y1={center.y + 49}
                      x2={center.x + frame.pointImages.plus[0] * angularScale}
                      y2={center.y + 49}
                      stroke="#bda7f5"
                      strokeWidth="1.6"
                      strokeDasharray="5 4"
                      markerStart="url(#einstein-lavender-arrow)"
                      markerEnd="url(#einstein-lavender-arrow)"
                    />
                    {[frame.pointImages.plus, frame.pointImages.minus].map(
                      (point, index) => (
                        <path
                          key={index}
                          d={`M${center.x + point[0] * angularScale} ${center.y + 12}v30`}
                          stroke="#bda7f5"
                          strokeWidth="1.2"
                          strokeDasharray="3 4"
                        />
                      ),
                    )}
                  </>
                ) : null}
                <g
                  transform={
                    ringImage
                      ? `translate(${center.x - 169} ${center.y - 118})`
                      : `translate(${center.x} ${center.y + 76})`
                  }
                  className="einstein-badge einstein-badge-lavender"
                >
                  <circle r="17" />
                  <text y="7" textAnchor="middle">
                    3
                  </text>
                </g>
                <path
                  d="M126 437H554"
                  stroke="#bda7f5"
                  strokeWidth="1.4"
                  strokeDasharray="4 6"
                  markerEnd="url(#einstein-lavender-arrow)"
                  opacity="0.7"
                />
                <g
                  transform="translate(106 437)"
                  className="einstein-badge einstein-badge-lavender"
                >
                  <circle r="17" />
                  <text y="7" textAnchor="middle">
                    4
                  </text>
                </g>
                <text
                  x="340"
                  y="469"
                  textAnchor="middle"
                  className="einstein-crossing-label"
                >
                  Relative crossing · illustrative guide
                </text>
              </g>
            )}
          </svg>
          <div className="einstein-sky-key">
            <span>
              <i className="einstein-key-image" /> Lensed background light
            </span>
            <span>
              <i className="einstein-key-lens" /> Fixed foreground lens center
            </span>
            {sourceGuide && (
              <span>
                <i className="einstein-key-source" /> Unlensed source position ·
                guide
              </span>
            )}
          </div>
          <p className="einstein-scene-note">
            Illustrative sky, not an observation. Foreground stars are
            decorative. The bright ring is background light, not a surface or
            horizon.
          </p>
        </div>

        <aside
          className="einstein-instruments"
          aria-label="Einstein ring controls and measurements"
        >
          <div className="einstein-controls">
            <p className="einstein-control-intro">
              {running
                ? 'The crossing pauses automatically at perfect alignment.'
                : aligned
                  ? 'The ring is paused. Follow the numbered arrows below.'
                  : 'Move the source, inspect the split images, or replay the crossing.'}
            </p>
            <div className="einstein-playback">
              <button type="button" onClick={replay} disabled={!motion}>
                Replay crossing
              </button>
              <button
                type="button"
                onClick={togglePlayback}
                disabled={!motion || complete}
                aria-pressed={running}
              >
                {running ? 'Pause' : complete ? 'Crossing complete' : 'Resume'}
              </button>
            </div>
            {!motion && (
              <p className="einstein-motion-note">
                Museum motion is off. Explore with the slider, or{' '}
                <button type="button" onClick={() => setMotion(true)}>
                  enable museum motion
                </button>
                .
              </p>
            )}
            <div className="einstein-presets">
              <button
                type="button"
                onClick={() => chooseOffset(0, true)}
                aria-pressed={aligned && !running}
              >
                Measure ring
              </button>
              <button
                type="button"
                onClick={() => chooseOffset(0.7, true)}
                aria-pressed={Math.abs(offset - 0.7) < 0.001 && !running}
              >
                Inspect two images
              </button>
            </div>
            <label
              className="einstein-offset-label"
              htmlFor="einstein-source-offset"
            >
              Source offset{' '}
              <span>
                β / θ_E ={' '}
                <output htmlFor="einstein-source-offset" aria-live="off">
                  {signed(offset)}
                </output>
              </span>
            </label>
            <input
              id="einstein-source-offset"
              type="range"
              min="-2.4"
              max="2.4"
              step="0.02"
              value={offset}
              onChange={(event) => chooseOffset(Number(event.target.value))}
              aria-valuetext={`${signed(offset)} Einstein-angle units`}
            />
            <div className="einstein-slider-key" aria-hidden="true">
              <span>Left</span>
              <span>Alignment</span>
              <span>Right</span>
            </div>
            <label className="einstein-guide-toggle">
              <input
                type="checkbox"
                checked={sourceGuide}
                onChange={(event) => setSourceGuide(event.target.checked)}
              />
              Show unlensed source guide
            </label>
          </div>

          <ol
            className="einstein-measurements"
            aria-label="What the image can tell us"
          >
            <li className="einstein-measure-cyan">
              <span className="einstein-card-number">1</span>
              <div>
                <h5>Measure the angular radius</h5>
                <strong>
                  {aligned
                    ? 'θ_E = 1 normalized unit'
                    : 'Return to alignment to measure'}
                </strong>
                <p>
                  Fit the Einstein angular scale through the ring’s thickness.
                  With independently supplied lens and source distances, this
                  angular scale constrains effective mass.
                </p>
              </div>
            </li>
            <li className="einstein-measure-amber">
              <span className="einstein-card-number">2</span>
              <div>
                <h5>Locate the center</h5>
                <p>
                  In this spherical model, the ring’s symmetry locates the lens
                  center on the sky. The cross marks that angular position.
                </p>
              </div>
            </li>
            <li className="einstein-measure-lavender">
              <span className="einstein-card-number">3</span>
              <div>
                <h5>
                  {aligned
                    ? 'Watch a source become a ring'
                    : ringImage
                      ? 'Near alignment: an uneven ring'
                      : 'Compare the two images'}
                </h5>
                {frame.pointImages && !ringImage && (
                  <strong>
                    Point-source limit: separation{' '}
                    {frame.pointImages.separation.toFixed(3)} θ_E · flux ratio{' '}
                    {frame.pointImages.fluxRatio.toFixed(3)}
                  </strong>
                )}
                <p>
                  {aligned
                    ? 'At perfect alignment, a circular source produces a circular ring. Farther off axis, the light separates into two extended images.'
                    : ringImage
                      ? 'This finite source still overlaps the optical axis, forming an uneven ring. Move farther off axis to see the two images separate.'
                      : 'The dashed separation guide and brightness ratio use the ideal point-source limit, not measured centroids or photometry of these finite arcs.'}
                </p>
              </div>
            </li>
            <li className="einstein-measure-lavender">
              <span className="einstein-card-number">4</span>
              <div>
                <h5>Compare more than one epoch</h5>
                <p>
                  Changes in the image pattern across repeated observations
                  constrain relative angular motion. This animation’s playback
                  speed has no physical time scale.
                </p>
              </div>
            </li>
          </ol>
        </aside>
      </div>
      <div className="einstein-model-note">
        <p>
          <b>Model:</b> ordinary spherical thin-lens geometry, a finite circular
          background source, and a fixed point lens. Angles are shown in θ_E
          units; geometry and brightness are illustrative.
        </p>
        <p className="einstein-mass-relation">
          θ_E² = (4GM / c²) D_ls / (D_l D_s)
        </p>
        <p>
          The image alone does not supply the distances or a unique mass. This
          ring animation does not identify a black hole or measure a physical
          boundary.
        </p>
        <p>
          {/* oxlint-disable-next-line next/no-html-link-for-pages -- Static scientific source record. */}
          <a href="./research/einstein-ring-tour.md">
            Model, equations and sources ↗
          </a>
        </p>
      </div>
    </section>
  );
}
