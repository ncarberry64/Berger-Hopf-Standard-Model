'use client';
import { useEffect, useState } from 'react';
import { SCIENCE } from './exhibits';

const phases = [
  {
    start: 0,
    title: 'White-hole surface release',
    text: 'In Norman’s proposed cycle, cohesion is lost across the whole cosmic spatial surface. The white-hole event is represented as a global release, not an object opening at one point.',
  },
  {
    start: 12,
    title: 'Cooling, flows and active topology',
    text: 'As the surface cools, structure and motion return. Body markers and transient explosive events follow surface flows toward black-hole concentrations.',
  },
  {
    start: 72,
    title: 'Concentration, evaporation and smoothing',
    text: 'In the author’s Bubble/Wave picture, black holes process the remaining structure and release bound spacetime back to the surface. As the black holes evaporate, surface tension is restored and the displayed topography smooths.',
  },
  {
    start: 94,
    title: 'Smooth surface / heat death',
    text: 'The entire displayed surface becomes smooth. In this speculative cycle, this is followed immediately by another global loss of cohesion and white-hole release.',
  },
];
const sinks = [
  [0.65, -0.3, 0.7],
  [-0.6, 0.4, 0.7],
  [0.1, 0.7, 0.7],
];
function normalize(v: number[]) {
  const r = Math.hypot(...v);
  return v.map((x) => x / r);
}
function point(theta: number, phi: number, turn: number, rough: number) {
  const t = phi + turn;
  const radius =
    1 +
    rough *
      0.075 *
      (Math.sin(5 * theta + t * 3) + 0.5 * Math.cos(7 * t - theta));
  return [
    Math.sin(theta) * Math.cos(t) * radius,
    Math.cos(theta) * radius,
    Math.sin(theta) * Math.sin(t) * radius,
  ];
}
function project(p: number[]) {
  return [430 + 220 * p[0], 270 - 220 * p[1]];
}

export function CosmicEnclosure({ motion }: { motion: boolean }) {
  const [phase, setPhase] = useState(0),
    [playing, setPlaying] = useState(true),
    [speed, setSpeed] = useState(1);
  useEffect(() => {
    if (!motion || !playing) return;
    const timer = setInterval(
      () => setPhase((p) => (p + 0.25 * speed) % 100),
      75,
    );
    return () => clearInterval(timer);
  }, [motion, playing, speed]);
  const active = phase < 12 ? 0 : phase < 72 ? 1 : phase < 94 ? 2 : 3;
  const release = phase < 12,
    smooth = phase >= 94;
  const rough = release ? 0.35 : Math.max(0, 1 - Math.max(0, phase - 50) / 44);
  const turn = phase * 0.018;
  const evaporation = Math.max(0, Math.min(1, (phase - 80) / 14));
  const line = (kind: string, fixed: number) =>
    Array.from({ length: 91 }, (_, i) => {
      const p =
        kind === 'latitude'
          ? point(fixed, (i * Math.PI) / 45, turn, rough)
          : point((i * Math.PI) / 90, fixed, turn, rough);
      const xy = project(p);
      return `${i ? 'L' : 'M'}${xy[0].toFixed(2)} ${xy[1].toFixed(2)}`;
    }).join(' ');
  return (
    <article id="cosmic-enclosure-cycle" className="cosmic-cycle">
      <p className="eyebrow">
        Additional other work · Norman’s cosmic enclosure cycle
      </p>
      <h3>A surface that releases, flows, smooths—and begins again.</h3>
      <p>
        <strong>In plain language.</strong> This exhibit animates Norman’s
        proposed cyclic picture: a whole-surface white-hole event, renewed
        surface dynamics as it cools, concentration into black holes and their
        evaporation, a completely smooth heat-death state, and another release.
      </p>
      <p className="data-label">
        SPECULATIVE CONCEPTUAL SIMULATION · author-described cycle · not
        observational data, established cosmology or a BHSM closure result
      </p>
      <div className="cycle-phase-buttons">
        {phases.map((p, i) => (
          <button
            key={p.title}
            aria-pressed={active === i}
            onClick={() => {
              setPhase(p.start);
              setPlaying(false);
            }}
          >
            {i + 1}. {p.title}
          </button>
        ))}
      </div>
      <div className="diagram-scroll">
        <svg
          className="cosmic-view"
          viewBox="0 0 860 560"
          role="img"
          aria-label={`Schematic hypersphere cycle: ${phases[active].title}. Surface-flow markers concentrate into black-hole markers, disappear into a smooth state, then the whole surface releases.`}
        >
          <defs>
            <radialGradient id="cycle-surface">
              <stop offset="0" stopColor={release ? '#fffbe5' : '#183d55'} />
              <stop offset="1" stopColor={release ? '#d7f6ff' : '#091c2b'} />
            </radialGradient>
          </defs>
          <circle
            cx="430"
            cy="270"
            r="220"
            fill="url(#cycle-surface)"
            stroke={release ? '#ffffff' : '#739db5'}
            strokeWidth={release ? 5 : 1}
          />
          {Array.from({ length: 11 }, (_, i) => (
            <path
              key={`l${i}`}
              d={line('latitude', ((i + 1) * Math.PI) / 12)}
              fill="none"
              stroke={release ? '#fff' : '#69b8c6'}
              opacity={release ? 0.65 : 0.38}
              strokeDasharray={release ? '6 9' : undefined}
            />
          ))}
          {Array.from({ length: 14 }, (_, i) => (
            <path
              key={`m${i}`}
              d={line('meridian', (i * Math.PI) / 7)}
              fill="none"
              stroke={release ? '#fff' : '#8cced3'}
              opacity={release ? 0.7 : 0.32}
              strokeDasharray={release ? '6 9' : undefined}
            />
          ))}
          {!release &&
            !smooth &&
            sinks.map((s, i) => {
              const xy = project(normalize(s));
              return (
                <g key={i} opacity={Math.min(1, (94 - phase) / 8)}>
                  <circle
                    cx={xy[0]}
                    cy={xy[1]}
                    r={(12 + 6 * (phase / 94)) * (1 - evaporation)}
                    fill="#01030a"
                    stroke="#cb9f64"
                    strokeWidth="3"
                  />
                  <circle
                    cx={xy[0]}
                    cy={xy[1]}
                    r={25 + 45 * evaporation}
                    fill="none"
                    stroke="#cb9f64"
                    opacity={0.35 + 0.35 * evaporation}
                  />
                </g>
              );
            })}
          {!release &&
            !smooth &&
            Array.from({ length: 72 }, (_, i) => {
              const seed = normalize([
                Math.sin(i * 2.399),
                Math.cos(i * 1.71),
                0.5 + Math.sin(i * 0.7),
              ]);
              const sink = normalize(sinks[i % 3]);
              const travel =
                phase >= 72
                  ? Math.min(1, (phase - 72) / 22)
                  : (phase * 0.017 + i * 0.037) % 1;
              const twist = Math.sin(travel * Math.PI) * 0.25;
              const p = normalize(
                seed.map(
                  (n, k) =>
                    (1 - travel) * n + travel * sink[k] + (k === 0 ? twist : 0),
                ),
              );
              const xy = project(p);
              const opacity =
                (p[2] > 0.05 ? 1 : 0.22) *
                (1 - travel) *
                (phase > 85 ? (94 - phase) / 9 : 1);
              return (
                <g key={i} opacity={opacity}>
                  <circle
                    cx={xy[0]}
                    cy={xy[1]}
                    r={i % 8 === 0 ? 4 : 2}
                    fill={i % 8 === 0 ? '#efc374' : '#8fe7e6'}
                  />
                  {i % 17 === 0 && phase < 72 && (
                    <circle
                      cx={xy[0]}
                      cy={xy[1]}
                      r={5 + 12 * ((phase * 0.06 + i) % 1)}
                      fill="none"
                      stroke="#ff947d"
                      strokeWidth="2"
                    />
                  )}
                </g>
              );
            })}
          {release &&
            Array.from({ length: 32 }, (_, i) => {
              const a = (i * Math.PI) / 16,
                r = 220 + phase * 2.5;
              return (
                <line
                  key={i}
                  x1={430 + 215 * Math.cos(a)}
                  y1={270 + 215 * Math.sin(a)}
                  x2={430 + r * Math.cos(a)}
                  y2={270 + r * Math.sin(a)}
                  stroke="#ffffff"
                  strokeWidth="3"
                  opacity={1 - phase / 12}
                />
              );
            })}
          <text x="430" y="535" textAnchor="middle" fill="#dfedf5">
            {release
              ? 'Global loss of surface cohesion'
              : smooth
                ? 'Entire displayed surface smooth · restart follows'
                : 'Surface-flow and concentration schematic'}
          </text>
        </svg>
      </div>
      <div className="prototype-controls">
        <button onClick={() => setPlaying(!playing)} disabled={!motion}>
          {playing && motion ? 'Pause cycle' : 'Play cycle'}
        </button>
        <button
          onClick={() => {
            setPhase(0);
            setPlaying(false);
          }}
        >
          Restart at white-hole event
        </button>
        <label>
          Cycle position
          <input
            type="range"
            min="0"
            max="99.9"
            step=".1"
            value={phase}
            onChange={(e) => {
              setPlaying(false);
              setPhase(+e.target.value);
            }}
          />
        </label>
        <label>
          Playback speed
          <select value={speed} onChange={(e) => setSpeed(+e.target.value)}>
            <option value=".5">½ speed</option>
            <option value="1">Normal</option>
            <option value="2">2× speed</option>
          </select>
        </label>
      </div>
      {!motion && (
        <p>
          Animations are paused by the Museum motion control. The phase buttons
          and slider still work.
        </p>
      )}
      <h4>{phases[active].title}</h4>
      <p>{phases[active].text}</p>
      <p className="cycle-legend">
        Cyan: schematic flows · gold: celestial-body markers · dark circles:
        black-hole concentrations · coral rings: explosive-event markers ·
        expanding gold rings with shrinking centers: proposed evaporation and
        surface restoration · whole-surface white flash: proposed white-hole
        release.
      </p>
      <p>
        <strong>From Norman’s original Bubble/Wave picture.</strong> The
        author’s deck <em>The Prints</em> describes particles as nonlinear
        surface modes and forces as surface harmonics. Its black-hole sketches
        link evaporation with restoring surface tension. These are conceptual
        origins of this other-work exhibit; the September 7 brief supplies the
        complete heat-death-to-white-hole sequence shown here.
      </p>
      <p>
        The drawn sphere is an illustrative cross-sectional view of a
        three-dimensional S³ spatial hypersurface, not a literal outer wall or a
        full embedding of S³. Geometry, timing, surface roughness and flow paths
        are chosen for explanation. No evolution equation or thermodynamic proof
        establishes the proposed heat-death-to-white-hole transition here.
      </p>
      <a href={`${SCIENCE}/docs/museum/norman_cosmic_enclosure_cycle.md`}>
        Author brief, context and simulation limits ↗
      </a>
    </article>
  );
}
