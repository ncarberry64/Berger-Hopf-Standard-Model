'use client';

import { useEffect, useId, useState, type ReactNode } from 'react';
import { useSceneClock } from './use-scene-clock';
import { ExhibitReview } from './exhibit-review';
import { MuseumVisitorGuide } from './museum-visitor-guide';
import { MuseumEvidenceGuide } from './museum-evidence-guide';
import { followExhibit } from '../lib/exhibit-navigation';
import {
  PARTICLE_CYCLE_SECONDS,
  PARTICLE_SURFACE_Y,
  particleCyclePhases,
  particleCycleFrame,
  particleSurfaceHeight,
  bubbleOutline,
  cycleSmooth,
} from '../lib/particle-cycle';

type BubbleProps = {
  id: string;
  x: number;
  y: number;
  r: number;
  opacity: number;
  time: number;
  color: string;
  wobble?: number;
  seed?: number;
  squeeze?: number;
  pilot?: boolean;
};

/** A refractive membrane with moving wave fronts visible through its interior. */
function Bubble({
  id,
  x,
  y,
  r,
  opacity,
  time,
  color,
  wobble = 0.018,
  seed = 0,
  squeeze = 0,
  pilot = false,
}: BubbleProps) {
  const outline = bubbleOutline(r, wobble, time, seed, squeeze);
  if (opacity <= 0.001) return null;
  return (
    <g transform={`translate(${x} ${y})`} opacity={opacity}>
      <defs>
        <clipPath id={`${id}-clip`}>
          <path d={outline} />
        </clipPath>
        <radialGradient id={`${id}-glass`} cx="33%" cy="26%" r="74%">
          <stop stopColor="#f2fbff" stopOpacity=".38" />
          <stop offset=".2" stopColor={color} stopOpacity=".14" />
          <stop offset=".6" stopColor="#142c48" stopOpacity=".2" />
          <stop offset=".89" stopColor={color} stopOpacity=".21" />
          <stop offset="1" stopColor={color} stopOpacity=".65" />
        </radialGradient>
      </defs>
      <path
        d={outline}
        fill={`url(#${id}-glass)`}
        stroke={color}
        strokeWidth="1.7"
      />
      <g clipPath={`url(#${id}-clip)`} fill="none">
        {Array.from({ length: pilot ? 5 : 3 }, (_, row) => {
          const points = Array.from({ length: 41 }, (_, point) => {
            const px = -r * 1.2 + (point / 40) * r * 2.4;
            const py =
              (row - (pilot ? 2 : 1)) * r * 0.28 +
              Math.sin(px * 0.085 - time * 2.7 + seed + row * 0.9) * r * 0.16;
            return `${point ? 'L' : 'M'}${px.toFixed(2)} ${py.toFixed(2)}`;
          }).join(' ');
          return (
            <path
              key={row}
              d={points}
              stroke={row % 2 ? '#f4d6ff' : '#b8f6ff'}
              strokeWidth={pilot ? 1.5 : 0.9}
              opacity={pilot ? 0.7 : 0.28}
            />
          );
        })}
        <ellipse
          cx={-r * 0.18}
          cy={r * 0.5}
          rx={r * 0.72}
          ry={r * 0.15}
          stroke={color}
          opacity=".32"
        />
      </g>
      <path
        d={`M${-r * 0.7} ${-r * 0.16} Q${-r * 0.63} ${-r * 0.7} ${-r * 0.08} ${-r * 0.79}`}
        fill="none"
        stroke="#f5fbff"
        strokeWidth="3"
        strokeLinecap="round"
        opacity=".77"
      />
      <path
        d={`M${r * 0.69} ${r * 0.16} Q${r * 0.65} ${r * 0.65} ${r * 0.22} ${r * 0.82}`}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        opacity=".66"
      />
      <ellipse
        cx={-r * 0.36}
        cy={-r * 0.55}
        rx={r * 0.1}
        ry={r * 0.06}
        fill="#fff"
        opacity=".8"
        transform="rotate(-30)"
      />
    </g>
  );
}

function LifecycleDrawing({
  seconds,
  prefix,
}: {
  seconds: number;
  prefix: string;
}) {
  const f = particleCycleFrame(seconds);
  const y = PARTICLE_SURFACE_Y;
  const wavePath = (baseY: number) =>
    Array.from({ length: 151 }, (_, i) => {
      const x = 20 + i * 6.4;
      return `${i ? 'L' : 'M'}${x.toFixed(1)} ${(baseY - particleSurfaceHeight(x, baseY, f)).toFixed(1)}`;
    }).join(' ');
  const waveFace = wavePath(y);
  const neckHalf = 25 * (1 - f.detach) ** 1.8 + 0.2;
  const neckTop = f.parent.y + f.parent.r * 0.72;
  const mergeOutline = bubbleOutline(49, 0.13, f.t, 4, -0.25);
  const ruptureAngles = [-2.75, -1.9, -0.9, 0.15, 1.1, 2.05];

  return (
    <svg
      viewBox="0 0 1000 500"
      role="img"
      aria-labelledby={`${prefix}-title ${prefix}-description`}
    >
      <title
        id={`${prefix}-title`}
      >{`Particle lifecycle: ${f.phase.name.toLowerCase()}`}</title>
      <desc id={`${prefix}-description`}>
        A continuous conceptual BHSM cycle: converging ripples construct a rogue
        wave; its crest pinches off into a transparent bubble. Pilot waves pass
        through the traveling bubble. It collides with another bubble and forms
        three independently wobbling daughter bubbles. The daughters rupture in
        sequence, returning disturbances to the surface until the starting
        ripple pattern returns. The scene illustrates the proposed return of
        residual inertia without calculating a decay channel or transfer law.
      </desc>
      <defs>
        <radialGradient id={`${prefix}-atmosphere`}>
          <stop stopColor="#20475b" stopOpacity=".58" />
          <stop offset="1" stopColor="#08101d" stopOpacity="0" />
        </radialGradient>
        <linearGradient id={`${prefix}-surface`} x1="0" y1="0" x2="0" y2="1">
          <stop stopColor="#4ccbd3" stopOpacity=".2" />
          <stop offset=".58" stopColor="#152e48" stopOpacity=".34" />
          <stop offset="1" stopColor="#0c1526" stopOpacity="0" />
        </linearGradient>
        <linearGradient id={`${prefix}-crest`}>
          <stop stopColor="#74eced" stopOpacity=".12" />
          <stop offset=".46" stopColor="#d3ffff" stopOpacity=".58" />
          <stop offset="1" stopColor="#9f96fb" stopOpacity=".14" />
        </linearGradient>
        <radialGradient id={`${prefix}-impact`}>
          <stop stopColor="#fff6d8" stopOpacity=".65" />
          <stop offset=".2" stopColor="#ffb3b0" stopOpacity=".25" />
          <stop offset="1" stopColor="#a88cf3" stopOpacity="0" />
        </radialGradient>
        <linearGradient id={`${prefix}-membrane`} x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="#8ff3ee" stopOpacity=".28" />
          <stop offset=".5" stopColor="#ffb6cd" stopOpacity=".38" />
          <stop offset="1" stopColor="#c0a3ff" stopOpacity=".2" />
        </linearGradient>
      </defs>
      <ellipse
        cx="500"
        cy="260"
        rx="480"
        ry="230"
        fill={`url(#${prefix}-atmosphere)`}
      />
      <g className="particle-scene-label">
        <text x="30" y="35">
          A CONTINUOUS FIELD–BUBBLE CYCLE
        </text>
        <text x="970" y="35" textAnchor="end">
          {String(f.phaseIndex + 1).padStart(2, '0')} / 07
        </text>
        <text x="30" y="478">
          CONCEPTUAL BHSM INTERPRETATION · NO PHYSICAL SIZE OR TIME SCALE
        </text>
      </g>

      <path d={`${waveFace} L980 462H20Z`} fill={`url(#${prefix}-surface)`} />
      <g fill="none" strokeWidth=".9">
        {Array.from({ length: 20 }, (_, row) => (
          <path
            key={row}
            d={wavePath(294 + row * 8.2)}
            stroke={row % 4 === 0 ? '#8cebf0' : '#5b91ae'}
            opacity={row % 4 === 0 ? 0.42 : 0.2}
          />
        ))}
        {Array.from({ length: 31 }, (_, column) => {
          const points = Array.from({ length: 34 }, (_, row) => {
            const baseY = 292 + row * 4.9;
            const x = 500 + (column - 15) * (19 + row * 0.38);
            return `${row ? 'L' : 'M'}${x.toFixed(1)} ${(baseY - particleSurfaceHeight(x, baseY, f)).toFixed(1)}`;
          }).join(' ');
          return (
            <path key={column} d={points} stroke="#75b8c9" opacity=".13" />
          );
        })}
      </g>
      <path
        d={waveFace}
        fill="none"
        stroke="#a2f5ec"
        strokeWidth="1.9"
        opacity=".75"
      />

      {f.crest > 0.01 && (
        <>
          <path
            d={`${waveFace} L980 458H20Z`}
            fill={`url(#${prefix}-crest)`}
            opacity={f.crest * 0.3}
          />
          <g
            className="particle-scene-annotation"
            opacity={cycleSmooth((f.t - 4) / 2) * (1 - f.detach)}
          >
            <path
              d={`M300 ${y - f.crest * 156 - 12}V88H365`}
              stroke="#9ae9ea"
              fill="none"
              opacity=".55"
            />
            <text x="376" y="93" fill="#b9f8f1">
              Constructive interference
            </text>
          </g>
        </>
      )}

      {f.neck > 0.001 && (
        <path
          d={`M${300 - neckHalf * 2.5} ${y} C${300 - neckHalf} ${y - 20} ${300 - neckHalf * 0.28} ${neckTop + 24} ${300 - neckHalf} ${neckTop} Q300 ${neckTop - 20} ${300 + neckHalf} ${neckTop} C${300 + neckHalf * 0.28} ${neckTop + 24} ${300 + neckHalf} ${y - 20} ${300 + neckHalf * 2.5} ${y}`}
          fill={`url(#${prefix}-crest)`}
          stroke="#b9f7ec"
          strokeWidth="1.2"
          opacity={f.neck}
        />
      )}

      {f.parent.opacity > 0.001 && (
        <>
          <ellipse
            cx={f.parent.x}
            cy={y + 3}
            rx={f.parent.r * 1.6}
            ry="13"
            fill="#98d8fa"
            opacity={f.parent.opacity * 0.065}
          />
          {f.travel > 0 && (
            <g
              fill="none"
              stroke="#f3ca8c"
              strokeWidth="1.3"
              opacity={f.parent.opacity * 0.6}
            >
              {[0, 1, 2, 3].map((ring) => {
                const ripple = (f.t * 0.7 + ring / 4) % 1;
                return (
                  <ellipse
                    key={ring}
                    cx={f.parent.x - ripple * 28}
                    cy={y}
                    rx={12 + ripple * 100}
                    ry={4 + ripple * 23}
                    opacity={(1 - ripple) * 0.65}
                  />
                );
              })}
              <path
                d={`M${f.parent.x} ${f.parent.y + f.parent.r + 3}Q${f.parent.x - 15} 280 ${f.parent.x} ${y - 6}`}
                strokeDasharray="2 7"
                opacity=".35"
              />
            </g>
          )}
          <Bubble
            id={`${prefix}-parent`}
            {...f.parent}
            time={f.t}
            color="#a4eef1"
            pilot
          />
        </>
      )}
      <Bubble
        id={`${prefix}-incoming`}
        {...f.incoming}
        time={f.t}
        color="#ffbc91"
        seed={2}
        pilot
      />

      {f.merge > 0.001 && (
        <g transform="translate(590 190)" opacity={f.merge}>
          <circle r="105" fill={`url(#${prefix}-impact)`} />
          <path
            d={mergeOutline}
            fill={`url(#${prefix}-membrane)`}
            stroke="#f7cfed"
            strokeWidth="2"
          />
          {[0, 1, 2].map((i) => (
            <path
              key={i}
              d={`M-52 ${-25 + i * 25} Q0 ${Math.sin(f.t * 3 + i) * 45} 53 ${24 - i * 24}`}
              fill="none"
              stroke={['#8cf2ea', '#ffcd98', '#ceb2ff'][i]}
              strokeWidth="2"
              opacity=".6"
            />
          ))}
        </g>
      )}

      {f.daughters.map((daughter, index) => (
        <g key={index}>
          <Bubble
            id={`${prefix}-daughter-${index}`}
            x={daughter.x}
            y={daughter.y}
            r={daughter.r}
            opacity={daughter.opacity}
            wobble={daughter.wobble}
            time={f.t}
            color={daughter.color}
            seed={index + 3}
          />
          {daughter.ruptureOpacity > 0 && (
            <g
              transform={`translate(${daughter.x} ${daughter.y})`}
              fill="none"
              stroke={daughter.color}
              opacity={daughter.ruptureOpacity}
              strokeWidth="1.6"
            >
              {ruptureAngles.map((angle, piece) => {
                const radius = daughter.r * (1 + daughter.pop * 0.65);
                const ax = Math.cos(angle) * radius;
                const ay = Math.sin(angle) * radius;
                return (
                  <path
                    key={piece}
                    d={`M${ax} ${ay} Q${Math.cos(angle + 0.18) * radius * 1.1} ${Math.sin(angle + 0.18) * radius * 1.1} ${Math.cos(angle + 0.42) * radius} ${Math.sin(angle + 0.42) * radius}`}
                  />
                );
              })}
            </g>
          )}
          {daughter.returnOpacity > 0.001 && (
            <g
              fill="none"
              stroke={daughter.color}
              opacity={daughter.returnOpacity}
            >
              {[0, 1, 2].map((stream) => {
                const streamX = daughter.x + (stream - 1) * 16;
                const endY =
                  daughter.y + (y - daughter.y) * daughter.returnProgress;
                return (
                  <g key={stream}>
                    <path
                      d={`M${streamX} ${daughter.y + 8} Q${streamX + 25 * Math.sin(index + stream)} ${(daughter.y + endY) / 2} ${daughter.x + (stream - 1) * 10} ${endY}`}
                      strokeWidth="1.4"
                      opacity=".55"
                    />
                    <circle
                      cx={daughter.x + (stream - 1) * 10}
                      cy={endY}
                      r={2.5 + stream * 0.5}
                      fill={daughter.color}
                      stroke="none"
                    />
                  </g>
                );
              })}
            </g>
          )}
          {daughter.ringOpacity > 0.001 && (
            <g
              fill="none"
              stroke={daughter.color}
              opacity={daughter.ringOpacity}
              strokeWidth="1.6"
            >
              {[0, 1, 2].map((ring) => (
                <ellipse
                  key={ring}
                  cx={daughter.x}
                  cy={y}
                  rx={Math.max(1, daughter.ringRadius - ring * 17)}
                  ry={Math.max(1, daughter.ringRadius - ring * 17) * 0.25}
                  opacity={1 - ring * 0.22}
                />
              ))}
            </g>
          )}
        </g>
      ))}

      <g className="particle-scene-annotation">
        {f.phaseIndex === 0 && (
          <>
            <text x="100" y="246" fill="#9ee9ec">
              Converging ripples
            </text>
            <path
              d="M175 258L250 300M760 260L665 300"
              fill="none"
              stroke="#91dbe2"
              opacity=".45"
            />
          </>
        )}
        {f.phaseIndex === 2 && (
          <>
            <text x="395" y="160" fill="#d6c4fb">
              A crest becomes a bubble
            </text>
            <path
              d={`M382 169L${f.parent.x + 44} ${f.parent.y}`}
              fill="none"
              stroke="#cbb8f4"
              opacity=".5"
            />
          </>
        )}
        {f.phaseIndex === 3 && (
          <>
            <text x="365" y="90" fill="#f5d5a5">
              Pilot waves through the bubble
            </text>
            <text x="750" y="130" fill="#e8c5b2">
              Incoming bubble
            </text>
          </>
        )}
        {f.phaseIndex === 4 && (
          <text x="590" y="85" textAnchor="middle" fill="#ffd1c9">
            Collision → decay event
          </text>
        )}
        {f.phaseIndex === 5 && (
          <text x="80" y="110" fill="#ddc8ff">
            Independent, unstable daughters
          </text>
        )}
        {f.phaseIndex === 6 && (
          <text x="500" y="105" textAnchor="middle" fill="#afece8">
            Rupture → return to surface ripples
          </text>
        )}
      </g>
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
  const [playing, setPlaying] = useState(false);
  const running = playing && motion;
  const { ref, time } = useSceneClock(running, Infinity, 0.05, 'independent');
  const [offset, setOffset] = useState(0);
  const frame = particleCycleFrame(time + offset);

  useEffect(() => {
    const pauseWhenAway = () => {
      setPlaying(false);
      window.dispatchEvent(new Event('bhsm:lifecycle-pause'));
    };
    const visibility = () => {
      if (document.hidden) pauseWhenAway();
    };
    const stopFollowing = followExhibit(window, (slideId) => {
      // The destination exhibit owns its soundtrack; only reset this scene's
      // button so returning to it requires one explicit Play gesture.
      if (slideId !== 'potential') setPlaying(false);
    });
    window.addEventListener('blur', pauseWhenAway);
    document.addEventListener('visibilitychange', visibility);
    return () => {
      window.removeEventListener('blur', pauseWhenAway);
      document.removeEventListener('visibilitychange', visibility);
      stopFollowing();
    };
  }, []);

  function pause() {
    setPlaying(false);
    setMotion(false);
    window.dispatchEvent(new Event('bhsm:lifecycle-pause'));
  }
  function seek(next: number) {
    pause();
    setOffset(next - time);
  }
  function togglePlayback() {
    if (running) pause();
    else {
      setPlaying(true);
      setMotion(true);
      // Dispatch inside the visitor gesture so music can begin on mobile.
      window.dispatchEvent(new Event('bhsm:lifecycle-play'));
    }
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
            BHSM proposes geometric organization across scales. Follow one
            excitation from overlapping ripples to a bubble, a collision and a
            return to the surface.
          </p>
          <div className="particle-home-links">
            <a href="#museum-visitor-guide">Take the three-minute tour ↓</a>
            <a href="#bhsm-scale-map">Explore the scales ↓</a>
            <a href="#bhsm-lifecycle">Enter the exhibits →</a>
          </div>
        </div>
      </div>

      <div
        id="particle-lifecycle-theatre"
        ref={ref}
        className="particle-theatre"
        data-lifecycle-phase={frame.phaseIndex}
        data-lifecycle-playing={running ? 'true' : 'false'}
      >
        <div className="particle-theatre-heading">
          <div>
            <span className="particle-label">THE LIFE OF AN EXCITATION</span>
            <h2>From a ripple. Back to ripples.</h2>
          </div>
          <button
            className="particle-play"
            type="button"
            onClick={togglePlayback}
            aria-label={
              running
                ? 'Pause particle lifecycle and music'
                : 'Play particle lifecycle with music'
            }
          >
            {running ? 'Pause' : 'Play'}
          </button>
        </div>
        <LifecycleDrawing seconds={frame.t} prefix={prefix} />
        <div
          className="particle-phase-buttons"
          aria-label="Particle lifecycle phases"
        >
          {particleCyclePhases.map((phase, index) => (
            <button
              key={phase.name}
              type="button"
              aria-pressed={index === frame.phaseIndex}
              onClick={() =>
                seek(phase.start + (phase.end - phase.start) * 0.55)
              }
            >
              <span>{String(index + 1).padStart(2, '0')}</span>
              {phase.name}
            </button>
          ))}
        </div>
        <div className="particle-phase-copy">
          <h3>{frame.phase.title}</h3>
          <p>{frame.phase.copy}</p>
        </div>
        <div className="particle-transport">
          <label htmlFor={`${prefix}-progress`}>Explore the cycle</label>
          <input
            id={`${prefix}-progress`}
            type="range"
            min="0"
            max={PARTICLE_CYCLE_SECONDS - 0.01}
            step=".05"
            value={frame.t}
            aria-valuetext={`${frame.phase.name}, ${Math.round((frame.t / PARTICLE_CYCLE_SECONDS) * 100)} percent of the conceptual cycle`}
            onChange={(event) => seek(Number(event.target.value))}
          />
          <button type="button" onClick={() => seek(0)}>
            Restart
          </button>
        </div>
        <p className="particle-science-note">
          Conceptual BHSM cycle · The return to ripples depicts the proposed
          transfer of residual inertia to the surface. Wave heights, timing,
          decay channels and inertia transfer are illustrative; no quantitative
          law is calculated.
        </p>
      </div>
      <MuseumVisitorGuide />
      {children}
      <MuseumEvidenceGuide />
      <ExhibitReview id="potential" />
    </section>
  );
}
