'use client';

import { useId, useState, type ReactNode } from 'react';
import { useSceneClock } from './use-scene-clock';
import { ExhibitReview } from './exhibit-review';

const phases = [
  {
    name: 'Excitation',
    title: 'A field is disturbed.',
    copy: 'Begin with an excitation: a change in a field. The drawing gives that disturbance a visible shape.',
    start: 0,
    end: 4,
    color: '#71e5eb',
  },
  {
    name: 'Organization',
    title: 'A localized mode takes shape.',
    copy: 'BHSM interprets particle structure through organized modes and their geometric support. Here an illustrative unstable excitation becomes localized.',
    start: 4,
    end: 9,
    color: '#bda7f5',
  },
  {
    name: 'Propagation',
    title: 'The excitation carries its history.',
    copy: 'Follow the organized excitation across the field. The moving pattern represents a continuing state, with no physical speed assigned.',
    start: 9,
    end: 14,
    color: '#ffbc77',
  },
  {
    name: 'Decay event',
    title: 'One parent becomes outgoing excitations.',
    copy: 'The parent transforms into daughter excitations. A physical decay must obey the available interaction channels and conservation laws; this scene illustrates the event.',
    start: 14,
    end: 20,
    color: '#ff9c91',
  },
] as const;

const duration = 20;
const clamp = (value: number) => Math.max(0, Math.min(1, value));
const smooth = (value: number) => {
  const t = clamp(value);
  return t * t * (3 - 2 * t);
};

/** A visual sequence, not a numerical model or physical particle trajectory. */
function LifecycleDrawing({
  seconds,
  prefix,
}: {
  seconds: number;
  prefix: string;
}) {
  const phaseIndex = phases.findIndex((phase) => seconds < phase.end);
  const phase = phases[Math.max(0, phaseIndex)];
  const organization = smooth((seconds - 3) / 3);
  const propagation = smooth((seconds - 9) / 5);
  const decay = smooth((seconds - 14) / 4.4);
  const parentX = 260 + propagation * 320;
  const parentY = 215;
  const amplitude = (0.28 + 0.72 * smooth(seconds / 3)) * (1 - decay);
  const parentOpacity = 1 - smooth((seconds - 14) / 1.6);
  const daughterOpacity = smooth((seconds - 14.15) / 1.4);
  const daughterDistance = 215 * decay;
  const fieldLines = Array.from({ length: 15 }, (_, row) => {
    const baseY = 132 + row * 13;
    const points = Array.from({ length: 111 }, (_, i) => {
      const x = 30 + i * 8;
      const envelope = Math.exp(-(((x - parentX) / 85) ** 2));
      const depth = Math.exp(-(((baseY - parentY) / 80) ** 2));
      const wave = Math.sin((x - parentX) * 0.075 - seconds * 1.9 + row * 0.3);
      const y =
        baseY + wave * envelope * depth * amplitude * (30 - organization * 12);
      return `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`;
    });
    return (
      <path
        key={row}
        d={points.join(' ')}
        stroke={row % 3 === 0 ? '#71e5eb' : '#667c9e'}
        opacity={row % 3 === 0 ? 0.35 : 0.16}
      />
    );
  });

  return (
    <svg
      viewBox="0 0 940 410"
      role="img"
      aria-labelledby={`${prefix}-title ${prefix}-description`}
    >
      <title
        id={`${prefix}-title`}
      >{`Particle lifecycle: ${phase.name.toLowerCase()}`}</title>
      <desc id={`${prefix}-description`}>
        A conceptual BHSM illustration moves from a cyan field disturbance to a
        localized mode, then propagation and a decay event with three symbolic
        outgoing excitations. Positions, sizes, paths and durations are
        schematic, not calculated particle properties.
      </desc>
      <defs>
        <radialGradient id={`${prefix}-atmosphere`}>
          <stop stopColor="#244956" stopOpacity=".55" />
          <stop offset="1" stopColor="#0b121d" stopOpacity="0" />
        </radialGradient>
        <radialGradient id={`${prefix}-particle`} cx="35%" cy="30%">
          <stop stopColor="#fffdf5" />
          <stop offset=".22" stopColor="#e3d6ff" />
          <stop offset=".7" stopColor="#a49adf" />
          <stop offset="1" stopColor="#4c467a" stopOpacity=".25" />
        </radialGradient>
        <radialGradient id={`${prefix}-halo`}>
          <stop stopColor={phase.color} stopOpacity=".42" />
          <stop offset=".35" stopColor={phase.color} stopOpacity=".12" />
          <stop offset="1" stopColor={phase.color} stopOpacity="0" />
        </radialGradient>
        <linearGradient id={`${prefix}-path`}>
          <stop stopColor="#71e5eb" stopOpacity="0" />
          <stop offset="1" stopColor="#ffbc77" stopOpacity=".8" />
        </linearGradient>
      </defs>

      <ellipse
        cx="460"
        cy="215"
        rx="450"
        ry="195"
        fill={`url(#${prefix}-atmosphere)`}
      />
      <g fill="none" strokeWidth="1">
        {fieldLines}
      </g>
      <g fill="none" stroke="#667c9e" strokeWidth=".7" opacity=".15">
        {Array.from({ length: 24 }, (_, index) => (
          <path
            key={index}
            d={`M${95 + index * 32} 132L${20 + index * 39} 314`}
          />
        ))}
      </g>

      <g className="particle-scene-label">
        <text x="36" y="42">
          FIELD → LOCALIZED MODE → OUTGOING STATES
        </text>
        <text x="36" y="376">
          BHSM INTERPRETATION · CONCEPTUAL SEQUENCE
        </text>
        <text x="904" y="376" textAnchor="end">
          {String(Math.max(0, phaseIndex) + 1).padStart(2, '0')} / 04
        </text>
      </g>
      <path
        d={`M260 215H${parentX}`}
        fill="none"
        stroke={`url(#${prefix}-path)`}
        strokeWidth="2"
        opacity={organization * (1 - decay * 0.7)}
      />

      <g opacity={parentOpacity}>
        <circle
          cx={parentX}
          cy={parentY}
          r={100 + organization * 20}
          fill={`url(#${prefix}-halo)`}
        />
        <g
          transform={`translate(${parentX} ${parentY})`}
          fill="none"
          stroke={phase.color}
        >
          {[0, 1, 2].map((ring) => (
            <ellipse
              key={ring}
              rx={17 + organization * 29}
              ry={9 + organization * 8}
              transform={`rotate(${ring * 60 + seconds * 13})`}
              opacity={0.35 + organization * 0.5}
              strokeWidth="1.5"
            />
          ))}
          <circle
            r={4 + organization * 12}
            fill={`url(#${prefix}-particle)`}
            stroke="none"
          />
          <circle
            r={48 + organization * 10}
            strokeDasharray="2 8"
            opacity={organization * 0.35}
          />
        </g>
        <g
          className="particle-scene-annotation"
          opacity={smooth(seconds / 1.5)}
        >
          <path
            d={`M${parentX} ${parentY - 63}V88H${parentX + 64}`}
            fill="none"
            stroke={phase.color}
            opacity=".55"
          />
          <text x={parentX + 72} y="93" fill={phase.color}>
            {seconds < 4 ? 'Field excitation' : 'Organized parent'}
          </text>
        </g>
      </g>

      {seconds >= 14 && (
        <>
          <circle
            cx="580"
            cy="215"
            r={22 + decay * 70}
            fill={`url(#${prefix}-halo)`}
            opacity={1 - decay * 0.8}
          />
          <circle
            cx="580"
            cy="215"
            r={8 + decay * 60}
            fill="none"
            stroke="#ff9c91"
            strokeWidth="1.5"
            opacity={(1 - decay) * 0.7}
          />
          <g opacity={daughterOpacity}>
            {[-0.62, 0.04, 0.65].map((angle, index) => {
              const x = 580 + Math.cos(angle) * daughterDistance;
              const y = 215 + Math.sin(angle) * daughterDistance;
              const colors = ['#71e5eb', '#ffbc77', '#bda7f5'];
              return (
                <g key={angle}>
                  <path
                    d={`M580 215L${x} ${y}`}
                    fill="none"
                    stroke={colors[index]}
                    strokeWidth="1.3"
                    strokeDasharray="4 6"
                    opacity=".6"
                  />
                  <circle cx={x} cy={y} r="24" fill={`url(#${prefix}-halo)`} />
                  <ellipse
                    cx={x}
                    cy={y}
                    rx="14"
                    ry="7"
                    fill="none"
                    stroke={colors[index]}
                    transform={`rotate(${(angle * 180) / Math.PI} ${x} ${y})`}
                  />
                  <circle cx={x} cy={y} r="4.5" fill={colors[index]} />
                </g>
              );
            })}
          </g>
          <g className="particle-scene-annotation" opacity={daughterOpacity}>
            <path
              d="M580 197V80H514"
              fill="none"
              stroke="#ff9c91"
              opacity=".6"
            />
            <text x="506" y="85" textAnchor="end" fill="#ff9c91">
              Decay event
            </text>
            <text x="743" y="75" fill="#dcd5e9">
              Daughter excitations
            </text>
          </g>
        </>
      )}
    </svg>
  );
}

export function ParticleLifecycle({
  motion,
  setMotion,
  children,
}: {
  motion: boolean;
  setMotion: (enabled: boolean) => void;
  children?: ReactNode;
}) {
  const prefix = useId().replace(/:/g, '');
  const { ref, time } = useSceneClock(motion, Infinity, 0.05, 'independent');
  // Begin with excitation; reduced-motion visitors can inspect every later
  // phase with the buttons or scrubber without enabling animation.
  const [offset, setOffset] = useState(0);
  const seconds = (((time + offset) % duration) + duration) % duration;
  const phaseIndex = phases.findIndex((phase) => seconds < phase.end);
  const phase = phases[phaseIndex];

  function seek(next: number) {
    setMotion(false);
    setOffset(next - time);
  }

  return (
    <section
      id="potential"
      className="engine-hero particle-home"
      aria-labelledby="potential-title"
    >
      <div className="particle-home-overline">
        <span>BERGER–HOPF STANDARD MODEL</span>
        <span>THE MUSEUM / BEGIN HERE</span>
      </div>
      <div className="particle-home-intro">
        <div>
          <p className="eyebrow">A journey through scale</p>
          <h1 id="potential-title">
            One framework.
            <br />
            <em>Many forms of matter.</em>
          </h1>
        </div>
        <div className="particle-home-invitation">
          <p>
            From a field excitation to a decay event, follow the idea at the
            heart of BHSM: geometric organization connecting particles, matter
            and the cosmos.
          </p>
          <div className="particle-home-links">
            <a href="#bhsm-scale-map">Explore the scales ↓</a>
            <a href="#bhsm-lifecycle">Enter the exhibits →</a>
          </div>
        </div>
      </div>

      <div
        ref={ref}
        className="particle-theatre"
        data-lifecycle-phase={phaseIndex}
      >
        <div className="particle-theatre-heading">
          <div>
            <span className="particle-label">THE LIFE OF AN EXCITATION</span>
            <h2>Formation. Motion. Transformation.</h2>
          </div>
          <button
            className="particle-play"
            type="button"
            onClick={() => setMotion(!motion)}
            aria-label={
              motion
                ? 'Pause particle lifecycle animation'
                : 'Play particle lifecycle animation'
            }
          >
            {motion ? 'Ⅱ Pause' : '▶ Play'}
          </button>
        </div>
        <LifecycleDrawing seconds={seconds} prefix={prefix} />
        <div
          className="particle-phase-buttons"
          aria-label="Particle lifecycle phases"
        >
          {phases.map((item, index) => (
            <button
              key={item.name}
              type="button"
              aria-pressed={index === phaseIndex}
              onClick={() => seek(item.start + (item.end - item.start) * 0.55)}
            >
              <span>{String(index + 1).padStart(2, '0')}</span>
              {item.name}
            </button>
          ))}
        </div>
        <div className="particle-phase-copy">
          <h3>{phase.title}</h3>
          <p>{phase.copy}</p>
        </div>
        <div className="particle-transport">
          <label htmlFor={`${prefix}-progress`}>Explore the sequence</label>
          <input
            id={`${prefix}-progress`}
            type="range"
            min="0"
            max="19.99"
            step=".05"
            value={seconds}
            aria-valuetext={`${phase.name}, ${Math.round((seconds / duration) * 100)} percent of the conceptual sequence`}
            onChange={(event) => seek(Number(event.target.value))}
          />
          <button type="button" onClick={() => seek(0)}>
            Restart
          </button>
        </div>
        <p className="particle-science-note">
          Conceptual BHSM interpretation · An illustrative unstable excitation.
          Paths, durations and outgoing modes are schematic; no decay rate or
          branching ratio is calculated.
        </p>
      </div>

      {children}

      <div className="particle-home-record">
        <p className="eyebrow">An open scientific collection</p>
        <h2>Follow the idea. Inspect the evidence.</h2>
        <p>
          BHSM proposes a common geometric foundation across scales. The museum
          connects that proposal with conditional Standard Model structure,
          calculations on specified backgrounds and experimental reference
          science. Each exhibit identifies its assumptions, results and open
          questions.
        </p>
        <div className="particle-home-links">
          <a href="https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/main/docs/current_bhsm_status.md">
            Current research status ↗
          </a>
          <a href="./research/mass-and-hypersphere-context.md">
            Hypersphere, core and mass ↗
          </a>
          <a href="./research/animation-evidence.md">
            What drives the animations ↗
          </a>
        </div>
      </div>
      <ExhibitReview id="potential" />
    </section>
  );
}
