'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline SVG needs image semantics; an HTML img cannot contain this interactive drawing. */
import { useEffect, useRef, useState } from 'react';
import { SCIENCE } from './exhibits';
import references from './reference-data.json';
import {
  cosmicProjection as project,
  filamentPoint,
  mix,
  webEdges as edges,
  webNodes as xyz,
  webParticles,
  webHubs,
} from '../lib/cosmic-web';

const phases = [
  {
    start: 0,
    title: 'White-hole surface release',
    text: 'The proposed cycle begins with a global loss of cohesion: the whole cosmic surface releases, rather than one white hole opening at a point.',
  },
  {
    start: 10,
    title: 'Cooling, flows and active topology',
    text: 'A luminous plasma cools. Ripples spread across the surface while density variations seed the next generation of structure.',
  },
  {
    start: 26,
    title: 'Acoustic imprint',
    text: 'The expanding acoustic shells stop propagating in this illustration, leaving a preferred separation. Observed BAO is a statistical fossil of early sound waves; these visible rings are explanatory symbols.',
  },
  {
    start: 43,
    title: 'Cosmic filaments and bright clusters',
    text: 'Matter collects along a web of filaments. Bright nodes stand for galaxy groups and clusters; coral bursts mark energetic events. The web illustrates gravitational structure growth, not literal BAO shells shrinking into filaments.',
  },
  {
    start: 68,
    title: 'Accretion and concentration',
    text: 'In Norman’s proposed enclosure cycle, structure and surface flows concentrate toward black holes. Streams spiral inward as the surrounding web thins.',
  },
  {
    start: 89,
    title: 'Evaporation and surface restoration',
    text: 'The author’s Bubble/Wave picture links black-hole evaporation with restoring surface tension. Dark cores shrink, their halos expand and remaining topography relaxes.',
  },
  {
    start: 96,
    title: 'Smooth surface / heat death',
    text: 'The displayed surface is completely smooth. The proposed cycle then passes directly into another global release; that transition has not been derived.',
  },
];
const clamp = (v: number) => Math.max(0, Math.min(1, v));
function point(i: number, turn: number) {
  return project(xyz[i], turn);
}
const f = (n: number) => n.toFixed(2);

export function CosmicEnclosure({ motion }: { motion: boolean }) {
  const sceneRef = useRef<HTMLElement>(null);
  const [phase, setPhase] = useState(0),
    [playing, setPlaying] = useState(true),
    [speed, setSpeed] = useState(1);
  useEffect(() => {
    if (!motion || !playing) return;
    let visible = false;
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
    });
    if (sceneRef.current) observer.observe(sceneRef.current);
    const t = setInterval(() => {
      if (visible && !document.hidden)
        setPhase((p) => (p + 0.12 * speed) % 100);
    }, 60);
    return () => {
      clearInterval(t);
      observer.disconnect();
    };
  }, [motion, playing, speed]);
  const active = phases.reduce((a, p, i) => (phase >= p.start ? i : a), 0),
    release = phase < 10,
    smooth = phase >= 96;
  const turn = phase * 0.006,
    web = clamp((phase - 34) / 16) * (1 - clamp((phase - 74) / 22)),
    evap = clamp((phase - 89) / 7),
    collapse = clamp((phase - 68) / 28),
    plasma = 1 - clamp((phase - 4) / 18);
  const shellOpacity = clamp((phase - 10) / 8) * (1 - clamp((phase - 32) / 16));
  const line = (edge: (typeof edges)[number], offset = 0) => {
    let visible = false;
    return Array.from({ length: 25 }, (_, k) => {
      const p = project(filamentPoint(edge, k / 24, offset), turn);
      if (p[2] < -0.025) {
        visible = false;
        return '';
      }
      const prefix = visible ? 'L' : 'M';
      visible = true;
      return `${prefix}${f(p[0])} ${f(p[1])}`;
    }).join(' ');
  };
  return (
    <article
      id="cosmic-enclosure-cycle"
      className="cosmic-cycle"
      ref={sceneRef}
    >
      <p className="eyebrow">Cosmic enclosure · other work</p>
      <h3>From a sea of light to the cosmic web.</h3>
      <p>
        A proposed hyperspherical cycle: release, cooling, acoustic structure,
        filaments, black-hole concentration, complete smoothing—and renewal.
      </p>
      <p className="data-label">
        SPECULATIVE CONCEPTUAL SIMULATION · not observational data or a BHSM
        closure result
      </p>
      <button
        className="event-stage cosmic-stage"
        aria-label={
          playing && motion ? 'Pause cosmic cycle' : 'Play cosmic cycle'
        }
        aria-pressed={!playing}
        onClick={() => setPlaying((p) => !p)}
      >
        <svg
          viewBox="0 0 960 650"
          role="img"
          aria-label={`Cosmic hypersphere: ${phases[active].title}. Irregular filaments, broad voids and dense cluster knots evolve into dark concentrations and finally a smooth surface.`}
        >
          <defs>
            <radialGradient id="cosmic-nebula">
              <stop stopColor="#07101b" />
              <stop offset=".48" stopColor="#060b14" />
              <stop offset="1" stopColor="#020408" />
            </radialGradient>
            <radialGradient id="cosmic-halo">
              <stop stopColor="#fff9cc" />
              <stop offset=".12" stopColor="#e5d9c2" />
              <stop offset=".36" stopColor="#97aaca" stopOpacity=".2" />
              <stop offset="1" stopColor="#637a99" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="cosmic-release">
              <stop stopColor="#fffef0" />
              <stop offset=".55" stopColor="#fff0c4" />
              <stop offset="1" stopColor="#e2e9ff" stopOpacity=".05" />
            </radialGradient>
            <filter
              id="cosmic-soft"
              filterUnits="userSpaceOnUse"
              x="180"
              y="10"
              width="600"
              height="600"
            >
              <feGaussianBlur stdDeviation="3" />
            </filter>
            <radialGradient id="cosmic-plasma">
              <stop stopColor="#fffef0" stopOpacity=".65" />
              <stop offset=".38" stopColor="#e8edff" stopOpacity=".22" />
              <stop offset="1" stopColor="#b0bded" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="cosmic-limb">
              <stop offset=".72" stopColor="#000" stopOpacity="0" />
              <stop offset="1" stopColor="#010309" stopOpacity=".82" />
            </radialGradient>
            <clipPath id="cosmic-surface-clip">
              <circle cx="480" cy="310" r="261" />
            </clipPath>
          </defs>
          <rect width="960" height="650" fill="#030813" />
          <circle
            cx="480"
            cy="310"
            r="260"
            fill={smooth ? '#1b3044' : 'url(#cosmic-nebula)'}
            stroke="#25313f"
            strokeWidth="1"
          />
          {!smooth && (
            <g clipPath="url(#cosmic-surface-clip)">
              {shellOpacity > 0 &&
                webHubs.map((i) => {
                  const p = point(i, turn),
                    r = 35 + clamp((phase - 10) / 16) * 105;
                  return (
                    <g key={i} opacity={shellOpacity * 0.7}>
                      <circle
                        cx={f(p[0])}
                        cy={f(p[1])}
                        r={f(r)}
                        fill="none"
                        stroke="#76dce2"
                        strokeWidth="3"
                      />
                      <circle
                        cx={f(p[0])}
                        cy={f(p[1])}
                        r={f(r - 7)}
                        fill="none"
                        stroke="#bcf4ec"
                        opacity=".3"
                      />
                      <circle cx={f(p[0])} cy={f(p[1])} r="6" fill="#fff0bd" />
                    </g>
                  );
                })}
              <g opacity={web}>
                {edges.map((edge, k) => (
                  <g key={k}>
                    <path
                      d={line(edge)}
                      stroke="#9eafc8"
                      strokeWidth={5 * edge.weight}
                      opacity=".11"
                      fill="none"
                      strokeLinecap="round"
                      filter="url(#cosmic-soft)"
                    />
                    {[-0.012, 0, 0.012].map((offset, j) => (
                      <path
                        key={j}
                        d={line(edge, offset)}
                        stroke={j === 1 ? '#c2cfdf' : '#728aa7'}
                        strokeWidth={j === 1 ? 0.55 : 0.35}
                        fill="none"
                        opacity={0.1 * edge.weight}
                        strokeLinecap="round"
                      />
                    ))}
                  </g>
                ))}
              </g>
              {!release &&
                webParticles.map((particle, i) => {
                  const attract = clamp((phase - 20) / 34);
                  let v = mix(particle.diffuse, particle.position, attract);
                  v = mix(v, xyz[webHubs[particle.target]], collapse);
                  const p = project(v, turn),
                    depth = clamp((p[2] + 0.015) / 0.18);
                  if (depth === 0) return null;
                  return (
                    <circle
                      key={i}
                      cx={f(p[0])}
                      cy={f(p[1])}
                      r={particle.size}
                      fill={particle.warm ? '#e9d4b8' : '#bacddd'}
                      opacity={
                        particle.brightness *
                        depth *
                        (1 - evap) *
                        (0.24 + 0.76 * attract)
                      }
                    />
                  );
                })}
              {web > 0 &&
                xyz.map((_, i) => {
                  const p = point(i, turn),
                    depth = clamp(p[2] / 0.2);
                  if (!depth) return null;
                  return (
                    <g key={i} opacity={web * depth}>
                      <circle
                        cx={f(p[0])}
                        cy={f(p[1])}
                        r={i % 5 === 0 ? 14 : 7}
                        fill="url(#cosmic-halo)"
                      />
                      <circle
                        cx={f(p[0])}
                        cy={f(p[1])}
                        r={i % 5 === 0 ? 0.95 : 0.5}
                        fill="#f3e5cf"
                        opacity=".8"
                      />
                      {i % 19 === 0 && phase < 76 && (
                        <circle
                          cx={f(p[0])}
                          cy={f(p[1])}
                          r={f(3 + ((phase + i) % 9) * 0.8)}
                          fill="url(#cosmic-halo)"
                          opacity={1 - ((phase + i) % 9) / 9}
                        />
                      )}
                    </g>
                  );
                })}
              {phase > 61 &&
                webHubs.map((i, k) => {
                  const p = point(i, turn),
                    size = (10 + 18 * clamp((phase - 61) / 25)) * (1 - evap);
                  return (
                    <g key={i} opacity={clamp((phase - 61) / 10) * (1 - evap)}>
                      <circle
                        cx={f(p[0])}
                        cy={f(p[1])}
                        r={f(50 + 90 * evap)}
                        fill="url(#cosmic-halo)"
                      />
                      <ellipse
                        cx={f(p[0])}
                        cy={f(p[1])}
                        rx={f(size * 2.1 + evap * 45)}
                        ry={f(size * 0.8 + evap * 18)}
                        transform={`rotate(${-25 + k * 29} ${f(p[0])} ${f(p[1])})`}
                        fill="none"
                        stroke="#f8cb82"
                        strokeWidth="2"
                      />
                      <circle
                        cx={f(p[0])}
                        cy={f(p[1])}
                        r={f(size)}
                        fill="#01030a"
                        stroke="#ffe2a6"
                      />
                      {Array.from({ length: 3 }, (_, j) => {
                        const d = Array.from({ length: 40 }, (_, z) => {
                          const q = z / 39,
                            ang = q * 6 + phase * 0.1 + j * 2.094,
                            rad = size + 70 * (1 - q);
                          return `${z ? 'L' : 'M'}${f(p[0] + rad * Math.cos(ang))} ${f(p[1] + rad * 0.6 * Math.sin(ang))}`;
                        }).join(' ');
                        return (
                          <path
                            key={j}
                            d={d}
                            fill="none"
                            stroke="#e7b574"
                            opacity=".4"
                          />
                        );
                      })}
                    </g>
                  );
                })}
              {plasma > 0 && (
                <g opacity={plasma}>
                  <circle
                    cx="480"
                    cy="310"
                    r="260"
                    fill="#dbe4f4"
                    opacity=".48"
                  />
                  <circle
                    cx="480"
                    cy="310"
                    r="260"
                    fill="url(#cosmic-release)"
                    opacity=".68"
                  />
                  {Array.from({ length: 46 }, (_, i) => {
                    const a = i * 2.399963 + phase * 0.035,
                      r = Math.sqrt((i + 0.5) / 46) * 258;
                    return (
                      <circle
                        key={i}
                        cx={f(480 + r * Math.cos(a))}
                        cy={f(310 + r * Math.sin(a))}
                        r={f(44 + 19 * Math.sin(i * 1.7 + phase * 0.3))}
                        fill="url(#cosmic-plasma)"
                        opacity={0.46 + 0.14 * Math.sin(i + phase * 0.2)}
                      />
                    );
                  })}
                  {[0, 1, 2].map((i) => (
                    <circle
                      key={i}
                      cx="480"
                      cy="310"
                      r={f(235 + 12 * Math.sin(phase * 0.18 + i * 0.9))}
                      fill="none"
                      stroke="#e8eeff"
                      strokeWidth={9 + i * 4}
                      opacity={0.025 + 0.01 * Math.sin(phase * 0.3 + i)}
                      filter="url(#cosmic-soft)"
                    />
                  ))}
                </g>
              )}
              {!release && (
                <circle
                  cx="480"
                  cy="310"
                  r="260"
                  fill="url(#cosmic-limb)"
                  opacity={1 - plasma}
                />
              )}
            </g>
          )}
          <text
            x="480"
            y="615"
            textAnchor="middle"
            fill="#d2e5f1"
            fontSize="19"
          >
            {phases[active].title}
          </text>
        </svg>
      </button>
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
      <div className="media-toolbar">
        <button disabled={!motion} onClick={() => setPlaying((p) => !p)}>
          {playing && motion ? 'Pause cycle' : 'Play cycle'}
        </button>
        <label>
          Speed{' '}
          <select value={speed} onChange={(e) => setSpeed(+e.target.value)}>
            <option value=".5">½×</option>
            <option value="1">1×</option>
            <option value="2">2×</option>
          </select>
        </label>
      </div>
      <label className="media-slider">
        Cycle position
        <input
          type="range"
          min="0"
          max="99.9"
          step=".1"
          value={phase}
          onChange={(e) => {
            setPhase(+e.target.value);
            setPlaying(false);
          }}
        />
      </label>
      <div className="event-story">
        <h4>{phases[active].title}</h4>
        <p>{phases[active].text}</p>
        <p className="cycle-legend">
          Pale filaments: matter density · warm knots: galaxy groups and
          clusters · dark cores: enlarged black-hole symbols · diffuse surface
          light: proposed white-hole release.
        </p>
      </div>
      <div className="cosmic-context">
        <div>
          <h4>What the sky measures</h4>
          <p>{references.bao_note}</p>
          <p>
            The reference separation is roughly <strong>150 Mpc</strong>. The
            animation has no distance or time calibration.
          </p>
          <a href={references.bao_source}>DESI: the observed BAO signal ↗</a>
          <p>
            The web’s appearance is informed by galaxy-survey maps: irregular
            filaments, bright intersections and large voids. Density is enhanced
            for visibility; individual stars and black-hole horizons would not
            be resolved at this scale. This is a synthetic illustration, not a
            photograph or survey reconstruction.
          </p>
          <a href="https://www.desi.lbl.gov/2026/07/03/exploring-what-desi-measures-an-interactive-cosmic-web-in-your-browser/">
            DESI: mapped filaments and voids ↗
          </a>{' '}
          ·{' '}
          <a href="https://eso.org/public/images/potw2504a/">
            ESO: an observed cosmic filament ↗
          </a>
        </div>
        <div>
          <h4>Norman’s enclosure picture</h4>
          <p>
            <em>The Prints</em> describes surface modes, harmonics and
            black-hole evaporation restoring surface tension. The whole-surface
            white-hole cycle is the author’s proposed extension. The
            smooth-to-release transition remains unproved.
          </p>
          <p>
            The sphere is an illustrative cross-sectional view of an S³ spatial
            hypersurface. It is not a literal outer wall or a complete embedding
            of the three-sphere.
          </p>
          <a href={`${SCIENCE}/docs/museum/norman_cosmic_enclosure_cycle.md`}>
            Concept, context and limits ↗
          </a>
        </div>
      </div>
    </article>
  );
}
