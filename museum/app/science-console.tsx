'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline SVG needs image semantics; an HTML img cannot contain this interactive drawing. */
import { useEffect, useRef, useState, type ReactNode } from 'react';

// A shared scene clock stops outside the viewport and while the tab is hidden.
export function useSceneClock(running: boolean) {
  const ref = useRef<HTMLDivElement>(null);
  const [time, setTime] = useState(0);
  useEffect(() => {
    if (!running) return;
    let visible = false;
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
    });
    if (ref.current) observer.observe(ref.current);
    const timer = setInterval(() => {
      if (visible && !document.hidden) setTime((t) => t + 0.05);
    }, 50);
    return () => {
      observer.disconnect();
      clearInterval(timer);
    };
  }, [running]);
  return { ref, time };
}

export function ScienceConsole({
  id,
  number,
  label,
  title,
  intro,
  children,
  accent = 'amber',
}: {
  id: string;
  number: string;
  label: string;
  title: string;
  intro: string;
  children: ReactNode;
  accent?: string;
}) {
  return (
    <article id={id} className={`science-console console-${accent}`}>
      <div className="console-cap">
        <span>{label}</span>
        <span>BHSM / {number}</span>
      </div>
      <div className="console-body">
        <aside className="console-rail" aria-hidden="true">
          <b>{number}</b>
          <span>{label}</span>
          <i />
          <i />
          <i />
        </aside>
        <div className="console-content">
          <header className="console-intro">
            <h3>{title}</h3>
            <p>{intro}</p>
          </header>
          {children}
        </div>
      </div>
      <div className="console-foot">
        <span>{label}</span>
        <a href="#exhibits">Explore the collection ↑</a>
      </div>
    </article>
  );
}

export function GeometryField({
  motion,
  compact = false,
  family = 0,
}: {
  motion: boolean;
  compact?: boolean;
  family?: number;
}) {
  const { ref, time } = useSceneClock(motion);
  const colors = ['#ffbc77', '#bda7f5', '#71e5eb'];
  const paths = Array.from({ length: 24 }, (_, f) => {
    const phi = (f * Math.PI * 2) / 24;
    const points = Array.from({ length: 100 }, (_, i) => {
      const t = (i * Math.PI * 2) / 99;
      // Linked circles on S3, stereographically projected to R3, then to the screen.
      const eta = 0.48 + family * 0.16;
      const d = 1 - Math.sin(eta) * Math.sin(t + phi);
      const x = (Math.cos(eta) * Math.cos(t)) / d;
      const y = (Math.cos(eta) * Math.sin(t)) / d;
      const z = (Math.sin(eta) * Math.cos(t + phi)) / d;
      const a = time * 0.18;
      const xx = x * Math.cos(a) - z * Math.sin(a);
      const zz = x * Math.sin(a) + z * Math.cos(a);
      return `${i ? 'L' : 'M'}${(420 + xx * 112).toFixed(2)},${(235 + (y * 0.78 + zz * 0.38) * 112).toFixed(2)}`;
    });
    return (
      <path
        key={f}
        d={points.join(' ')}
        fill="none"
        stroke={colors[f % 3]}
        strokeWidth={f % 3 === family ? 1.7 : 0.8}
        opacity={f % 3 === family ? 0.8 : 0.24}
      />
    );
  });
  return (
    <div
      ref={ref}
      className={`geometry-field ${compact ? 'geometry-compact' : ''}`}
    >
      <svg
        viewBox="0 0 840 480"
        role="img"
        aria-label="Rotating linked Hopf fibers: a mathematical geometry illustration, not a particle simulation"
      >
        <defs>
          <radialGradient id={compact ? 'hero-halo' : 'mode-halo'}>
            <stop stopColor="#2d294f" stopOpacity=".6" />
            <stop offset="1" stopColor="#030406" stopOpacity="0" />
          </radialGradient>
        </defs>
        <ellipse
          cx="420"
          cy="245"
          rx="330"
          ry="220"
          fill={`url(#${compact ? 'hero-halo' : 'mode-halo'})`}
        />
        <ellipse
          cx="420"
          cy="400"
          rx="205"
          ry="25"
          fill="none"
          stroke="#403443"
        />
        {paths}
        <path
          d="M70 170H150M70 170V330H150M770 170H690M770 170V330H690"
          stroke="#a18ccb"
          strokeWidth="2"
          fill="none"
        />
        <text x="70" y="150" fill="#bda7f5" fontSize="14">
          HOPF FIBERS
        </text>
        <text x="770" y="150" fill="#ffbc77" textAnchor="end" fontSize="14">
          S³ → R³
        </text>
        <text x="420" y="450" fill="#b5afbe" textAnchor="middle" fontSize="14">
          Linked geometry · mathematical visualization
        </text>
      </svg>
    </div>
  );
}

export function EngineHero({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (b: boolean) => void;
}) {
  return (
    <section
      id="potential"
      className="engine-hero"
      aria-labelledby="potential-title"
    >
      <div className="hero-overline">
        <span>BERGER–HOPF STANDARD MODEL</span>
        <button onClick={() => setMotion(!motion)} aria-pressed={!motion}>
          {motion ? 'Ⅱ Pause motion' : '▶ Enable motion'}
        </button>
      </div>
      <div className="hero-layout">
        <div className="hero-copy">
          <p className="eyebrow">
            A prediction engine. A historic possibility.
          </p>
          <h1 id="potential-title">
            What if geometry
            <br />
            could <em>predict matter?</em>
          </h1>
          <p>
            One geometric origin for the particles and forces of nature. BHSM
            pursues that possibility with historic stakes: explaining the
            pattern of matter from a common foundation.
          </p>
          <a className="enter-museum" href="#exhibits">
            Enter the science ↓
          </a>
          <small>
            If established and tested, this could reshape our understanding of
            matter. Full physical derivation remains open.
          </small>
        </div>
        <div className="hero-engine">
          <GeometryField motion={motion} compact />
          <div className="engine-sequence">
            <span>
              01 <b>Geometry</b>
            </span>
            <i>→</i>
            <span>
              02 <b>Calculation</b>
            </span>
            <i>→</i>
            <span>
              03 <b>Test</b>
            </span>
          </div>
        </div>
      </div>
      <div className="hero-baseline">
        <span>THE SCIENCE MUSEUM OF NORMAN P. CARBERRY</span>
        <span>Explore. Interact. Question.</span>
      </div>
    </section>
  );
}
