'use client';
import { useEffect, useState } from 'react';
import { SCIENCE } from './exhibits';
import references from './reference-data.json';

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
const xyz = Array.from({ length: 16 }, (_, i) => {
  const y = 1 - (2 * (i + 0.5)) / 16,
    r = Math.sqrt(1 - y * y),
    a = i * 2.399963;
  return [r * Math.cos(a), y, r * Math.sin(a)];
});
const edges = xyz
  .flatMap((a, i) =>
    xyz.map((b, j) => ({ i, j, d: Math.hypot(...a.map((v, k) => v - b[k])) })),
  )
  .filter((e) => e.i < e.j && e.d < 1.14);
function project(v: number[], turn: number) {
  const x = v[0] * Math.cos(turn) + v[2] * Math.sin(turn),
    z = -v[0] * Math.sin(turn) + v[2] * Math.cos(turn);
  return [480 + 260 * x, 310 - 260 * v[1], z];
}
function point(i: number, turn: number) {
  return project(xyz[i], turn);
}
const f = (n: number) => n.toFixed(2);

export function CosmicEnclosure({ motion }: { motion: boolean }) {
  const [phase, setPhase] = useState(0),
    [playing, setPlaying] = useState(true),
    [speed, setSpeed] = useState(1);
  useEffect(() => {
    if (!motion || !playing) return;
    const t = setInterval(() => setPhase((p) => (p + 0.12 * speed) % 100), 60);
    return () => clearInterval(t);
  }, [motion, playing, speed]);
  const active = phases.reduce((a, p, i) => (phase >= p.start ? i : a), 0),
    release = phase < 10,
    smooth = phase >= 96;
  const turn = phase * 0.006,
    web = clamp((phase - 34) / 16) * (1 - clamp((phase - 74) / 22)),
    evap = clamp((phase - 89) / 7),
    collapse = clamp((phase - 68) / 28);
  const shellOpacity = clamp((phase - 10) / 8) * (1 - clamp((phase - 32) / 16));
  const line = (i: number, j: number) => {
    const a = xyz[i],
      b = xyz[j];
    return Array.from({ length: 25 }, (_, k) => {
      const t = k / 24,
        v = a.map((n, l) => n * (1 - t) + b[l] * t),
        r = Math.hypot(...v);
      const p = project(
        v.map((n) => n / r),
        turn,
      );
      return `${k ? 'L' : 'M'}${f(p[0])} ${f(p[1])}`;
    }).join(' ');
  };
  return (
    <article id="cosmic-enclosure-cycle" className="cosmic-cycle">
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
          aria-label={`Cosmic hypersphere: ${phases[active].title}. Stars, acoustic shells and filamentary structures evolve into dark concentrations and finally a smooth surface.`}
        >
          <defs>
            <radialGradient id="cosmic-nebula">
              <stop stopColor={release ? '#fff8cc' : '#25506a'} />
              <stop offset=".48" stopColor={release ? '#edcaff' : '#172846'} />
              <stop offset="1" stopColor="#040a17" />
            </radialGradient>
            <radialGradient id="cosmic-halo">
              <stop stopColor="#fff9cc" />
              <stop offset=".12" stopColor="#f1c078" />
              <stop offset=".36" stopColor="#966ef4" stopOpacity=".55" />
              <stop offset="1" stopColor="#845df0" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="cosmic-release">
              <stop stopColor="#fffef0" />
              <stop offset=".55" stopColor="#fff0c4" />
              <stop offset="1" stopColor="#e2e9ff" stopOpacity=".05" />
            </radialGradient>
            <filter id="cosmic-soft">
              <feGaussianBlur stdDeviation="3" />
            </filter>
            <clipPath id="cosmic-surface-clip">
              <circle cx="480" cy="310" r="261" />
            </clipPath>
          </defs>
          <rect width="960" height="650" fill="#030813" />
          {!smooth &&
            Array.from({ length: 190 }, (_, i) => (
              <circle
                key={i}
                cx={f((i * 137.507) % 960)}
                cy={f((i * i * 19.31) % 650)}
                r={i % 17 === 0 ? 1.5 : 0.65}
                fill={i % 3 === 0 ? '#efd8a6' : '#a2c9e3'}
                opacity={(release ? 0.1 : 0.5) * (1 - evap)}
              />
            ))}
          <circle
            cx="480"
            cy="310"
            r="260"
            fill={smooth ? '#1b3044' : 'url(#cosmic-nebula)'}
            stroke="#7393b0"
            strokeWidth="1"
          />
          {!smooth && (
            <g clipPath="url(#cosmic-surface-clip)">
              {!release &&
                Array.from({ length: 9 }, (_, i) => (
                  <ellipse
                    key={i}
                    cx="480"
                    cy="310"
                    rx={32 + i * 28}
                    ry="260"
                    transform={`rotate(${f(turn * 20)} 480 310)`}
                    fill="none"
                    stroke="#96cde0"
                    opacity=".06"
                  />
                ))}
              {shellOpacity > 0 &&
                [2, 7, 11].map((i, k) => {
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
                {edges.map(({ i, j }, k) => (
                  <g key={k}>
                    <path
                      d={line(i, j)}
                      stroke={k % 3 === 0 ? '#b299ef' : '#66cce6'}
                      strokeWidth="11"
                      opacity=".18"
                      fill="none"
                      filter="url(#cosmic-soft)"
                    />
                    <path
                      d={line(i, j)}
                      stroke="#92ddec"
                      strokeWidth="1.1"
                      fill="none"
                      opacity=".65"
                    />
                  </g>
                ))}
              </g>
              {!release &&
                Array.from({ length: 380 }, (_, i) => {
                  const edge = edges[i % edges.length],
                    t = (i * 0.618 + phase * 0.003) % 1;
                  const a = xyz[edge.i],
                    b = xyz[edge.j];
                  const attract = clamp((phase - 26) / 26);
                  let v = a.map(
                    (n, k) =>
                      n * (1 - t) +
                      b[k] * t +
                      (1 - attract) * 0.26 * Math.sin(i * (k + 1) * 2.17),
                  );
                  const target = xyz[[3, 8, 12][i % 3]];
                  v = v.map(
                    (n, k) => n * (1 - collapse) + target[k] * collapse,
                  );
                  const r = Math.hypot(...v);
                  const p = project(
                    v.map((n) => n / r),
                    turn,
                  );
                  return (
                    <circle
                      key={i}
                      cx={f(p[0])}
                      cy={f(p[1])}
                      r={i % 23 === 0 ? 2.1 : 0.85}
                      fill={i % 7 === 0 ? '#ffd294' : '#b3e7f2'}
                      opacity={(p[2] > 0 ? 0.9 : 0.25) * (1 - evap)}
                    />
                  );
                })}
              {web > 0 &&
                xyz.map((_, i) => {
                  const p = point(i, turn);
                  return (
                    <g key={i} opacity={web * (p[2] > 0 ? 1 : 0.4)}>
                      <circle
                        cx={f(p[0])}
                        cy={f(p[1])}
                        r={i % 3 === 0 ? 37 : 22}
                        fill="url(#cosmic-halo)"
                      />
                      <circle cx={f(p[0])} cy={f(p[1])} r="2" fill="#fff7d0" />
                      {i % 5 === 0 && phase < 76 && (
                        <circle
                          cx={f(p[0])}
                          cy={f(p[1])}
                          r={f(4 + ((phase + i) % 9) * 2)}
                          fill="none"
                          stroke="#ff8b88"
                          opacity=".8"
                        />
                      )}
                    </g>
                  );
                })}
              {phase > 61 &&
                [3, 8, 12].map((i, k) => {
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
              {release && (
                <>
                  <circle
                    cx="480"
                    cy="310"
                    r={f(190 + phase * 12)}
                    fill="url(#cosmic-release)"
                  />
                  {Array.from({ length: 36 }, (_, i) => {
                    const a = (i * Math.PI) / 18;
                    return (
                      <line
                        key={i}
                        x1={f(480 + 40 * Math.cos(a))}
                        y1={f(310 + 40 * Math.sin(a))}
                        x2={f(480 + 280 * Math.cos(a))}
                        y2={f(310 + 280 * Math.sin(a))}
                        stroke="#fff7d5"
                        strokeWidth="2"
                        opacity={0.7 - phase * 0.04}
                      />
                    );
                  })}
                  <circle
                    cx="480"
                    cy="310"
                    r="257"
                    fill="none"
                    stroke="#fff"
                    strokeWidth="5"
                    strokeDasharray="18 10"
                  />
                </>
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
          Cyan: acoustic imprint and filaments · gold: clusters and accretion ·
          coral: energetic bursts · dark cores: black holes · whole-surface
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
