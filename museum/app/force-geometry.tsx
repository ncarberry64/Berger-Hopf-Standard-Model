'use client';

import { useEffect, useRef, useState } from 'react';
import { useSceneClock } from './science-console';
import {
  coneRadius,
  electromagneticCloud,
  originCloud,
  weakCollision,
  surfaceCollision,
  type Dot,
} from '../lib/force-particles';

const studies = [
  {
    name: 'Strong force',
    motif: 'Binding & cohesion',
    color: '#72d9ff',
    text: 'A coherent surface pulses around a concentrated core.',
    meaning:
      'BHSM pictures strong interaction as cohesion in the underlying Aether geometry. The breathing mesh is a visual analogy for binding.',
    boundary:
      'Established strong interactions are described by QCD. This display does not calculate confinement or a binding energy.',
  },
  {
    name: 'Electromagnetic',
    motif: 'Limited surface availability',
    color: '#f2c774',
    text: 'A limited electromagnetic component is freely available at the surface.',
    meaning:
      'In this BHSM interpretation, only a limited electromagnetic component is freely available on the surface, corresponding to the fine-structure constant (FSC, α). The circulating interior and narrow release illustrate that proposed relationship.',
    boundary:
      'The fine-structure constant measures electromagnetic coupling. The proposed surface interpretation is qualitative here; the animation does not calculate α or calibrate surface availability.',
  },
  {
    name: 'Weak force',
    motif: 'Decay & transformation',
    color: '#fc9171',
    text: 'An unstable configuration transforms into decay products.',
    meaning:
      'The weak-force study illustrates decay: an unstable configuration transforms and releases daughter products. The spinning paths in the right cone provide a visual language for that transition, rather than a simulated collision process.',
    boundary:
      'Weak interactions mediate particle transformations. This geometric analogy does not compute a decay channel, lifetime or interaction range.',
  },
  {
    name: 'Gravity',
    motif: 'Large-scale geometry',
    color: '#b99bff',
    text: 'A broad curvature pattern moves across the support.',
    meaning:
      'A slowly changing surface shows the extended geometric response in the BHSM interpretation. Its shape is a diagram of curvature, not a material sheet.',
    boundary:
      'Gravity is distinct from electromagnetism. No electromagnetic frequency, metric solution or gravitational-wave prediction is assigned here.',
  },
  {
    name: 'One geometric origin',
    motif: 'The hypersphere',
    color: '#67e8ef',
    text: 'A shared interior and interacting surface modes connect the four studies.',
    meaning:
      'The sphere brings the interior and surface modes into one geometric picture. Surface interactions release daughter modes. The globe is a lower-dimensional visualization of BHSM’s proposed S³ support.',
    boundary:
      'A common picture is not a completed unification. Physical mode identification, normalized couplings and quantitative predictions remain open.',
  },
];

type Point = [number, number, number];
const TAU = Math.PI * 2;

function ForceField({ kind, phase }: { kind: number; phase: number }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const ctx = ref.current?.getContext('2d');
    if (!ctx) return;
    const W = 600,
      H = 470,
      t = phase * TAU;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#050c14';
    ctx.fillRect(0, 0, W, H);
    const project = ([x, y, z]: Point): [number, number] => {
      const a = kind === 4 || kind === 0 ? t : 0.24;
      const rx = x * Math.cos(a) + z * Math.sin(a);
      const rz = z * Math.cos(a) - x * Math.sin(a);
      const scale = 1 + rz * 0.001;
      return [W / 2 + rx * scale, H / 2 - (y * 0.92 + rz * 0.3) * scale];
    };
    const glow = (
      x: number,
      y: number,
      r: number,
      color: string,
      opacity = 1,
    ) => {
      const g = ctx.createRadialGradient(x, y, 0, x, y, r);
      g.addColorStop(0, color);
      g.addColorStop(0.18, color + 'b0');
      g.addColorStop(1, color + '00');
      ctx.globalAlpha = opacity;
      ctx.fillStyle = g;
      ctx.fillRect(x - r, y - r, r * 2, r * 2);
      ctx.globalAlpha = 1;
    };
    const dot = ({ point, radius, color }: Dot) => {
      const [x, y] = project(point);
      ctx.globalAlpha = 0.5 + (0.4 * (point[2] + 180)) / 360;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, TAU);
      ctx.fill();
      ctx.globalAlpha = 1;
    };
    // Deterministic background points; geometry, not a measured sky map.
    for (let j = 0; j < 42; j++) {
      ctx.fillStyle = `rgba(145,185,215,${0.12 + (j % 4) * 0.06})`;
      ctx.fillRect((j * 137.3) % W, (j * 79.7) % H, 1.4, 1.4);
    }
    glow(300, 235, 220, '#183d69', 0.65);
    const line = (
      points: Point[],
      color: string,
      alpha = 0.45,
      width = 1.3,
    ) => {
      ctx.beginPath();
      points.forEach((point, n) => {
        const p = project(point);
        if (n) ctx.lineTo(...p);
        else ctx.moveTo(...p);
      });
      ctx.strokeStyle = color;
      ctx.globalAlpha = alpha;
      ctx.lineWidth = width;
      ctx.stroke();
      ctx.globalAlpha = 1;
    };
    const surface = (u: number, v: number): Point => {
      if (kind === 0 || kind === 4) {
        const lat = (u - 0.5) * Math.PI,
          lon = v * TAU;
        const wave = kind === 0 ? 1 + 0.035 * Math.sin(t * 2 + lat * 5) : 1;
        const r = (kind === 0 ? 183 : 168) * wave;
        return [
          r * Math.cos(lat) * Math.cos(lon),
          r * Math.sin(lat) * (kind === 0 ? 0.72 : 1),
          r * Math.cos(lat) * Math.sin(lon),
        ];
      }
      if (kind === 3) {
        const x = (u - 0.5) * 400,
          z = (v - 0.5) * 340;
        const r = Math.hypot(x, z);
        return [
          x,
          88 * Math.exp((-r * r) / 15000) + 9 * Math.cos(r / 32 - t) - 45,
          z,
        ];
      }
      const x = (u - 0.5) * 425;
      const r = coneRadius(u, kind, phase);
      return [x, r * Math.cos(v * TAU), r * Math.sin(v * TAU)];
    };
    for (let j = 0; j <= 18; j++) {
      const color = kind === 2 && j > 10 ? '#fc9171' : '#72d9ff';
      line(
        Array.from({ length: 65 }, (_, i) => surface(j / 18, i / 64)),
        color,
        j % 3 === 0 ? 0.65 : 0.28,
      );
      line(
        Array.from({ length: 65 }, (_, i) => surface(i / 64, j / 18)),
        color,
        0.34,
      );
    }
    if (kind === 0) {
      glow(300, 235, 45 + 12 * Math.sin(t * 2), '#72d9ff', 0.85);
      for (let j = 0; j < 3; j++) {
        const q = (phase * 2 + j / 3) % 1;
        line(
          Array.from(
            { length: 81 },
            (_, i): Point => [
              Math.cos((i / 80) * TAU) * 180 * q,
              Math.sin((i / 80) * TAU) * 130 * q,
              0,
            ],
          ),
          '#a7eaff',
          (1 - q) * 0.7,
          2,
        );
      }
    } else if (kind === 1) {
      electromagneticCloud(phase)
        .sort((a, b) => a.point[2] - b.point[2])
        .forEach(dot);
      glow(...project([55, 0, 0]), 36, '#ffe073', 0.65);
      for (let j = 0; j < 5; j++) {
        const q = (phase * 2 + j / 5) % 1;
        dot({
          point: [-15 + q * 210, 5 * Math.sin(q * TAU), 0],
          radius: 4,
          color: '#ffe073',
        });
      }
      glow(...project([198, 0, 0]), 25, '#72d9ff', 0.8);
    } else if (kind === 2) {
      for (let lane = 0; lane < 8; lane++) {
        const current = weakCollision(phase, lane);
        line(
          Array.from(
            { length: 25 },
            (_, j) => weakCollision(phase - (24 - j) / 900, lane).point,
          ),
          current.color,
          0.55,
          2,
        );
        dot(current);
        const q = (((phase * 2 + Math.floor(lane / 2) / 4) % 1) + 1) % 1;
        if (Math.abs(q - 0.5) < 0.035)
          glow(
            ...project([(0.77 - 0.5) * 425, 0, 0]),
            22,
            '#ffe073',
            1 - Math.abs(q - 0.5) / 0.035,
          );
      }
    } else if (kind === 3) {
      line(
        Array.from({ length: 81 }, (_, i): Point => {
          const x = (i / 80 - 0.5) * 400;
          return [
            x,
            88 * Math.exp((-x * x) / 15000) +
              9 * Math.cos(Math.abs(x) / 32 - t) -
              45,
            0,
          ];
        }),
        '#c6b3ff',
        0.9,
        2.8,
      );
    } else {
      originCloud()
        .sort((a, b) => a.point[2] - b.point[2])
        .forEach(dot);
      for (let lane = 0; lane < 3; lane++) {
        const dots = surfaceCollision(phase, lane);
        dots.forEach(dot);
        for (let j = 0; j < dots.length; j++) {
          const trail = Array.from(
            { length: 16 },
            (_, k) => surfaceCollision(phase - (15 - k) / 1000, lane)[j]?.point,
          ).filter((p): p is Point => Boolean(p));
          if (trail.length > 1) line(trail, dots[j].color, 0.65, 1.8);
        }
      }
    }
  }, [kind, phase]);
  return (
    <canvas
      ref={ref}
      width={600}
      height={470}
      // Canvas draws the moving study; an image role exposes its description.
      // oxlint-disable-next-line jsx-a11y/prefer-tag-over-role
      role="img"
      aria-label={`${studies[kind].name}: ${studies[kind].text}`}
    />
  );
}

export function ForceGeometry({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (value: boolean) => void;
}) {
  const [playing, setPlaying] = useState(true);
  const [offset, setOffset] = useState(0);
  const [chosen, setChosen] = useState(0);
  const { ref, time } = useSceneClock(motion && playing);
  const phase = (((time / 12 + offset) % 1) + 1) % 1;
  const study = studies[chosen];
  return (
    <div ref={ref} className="force-atlas">
      <div className="force-atlas-heading">
        <span className="data-label">
          BHSM interpretation · animated geometric studies
        </span>
        <span className="force-atlas-key">
          Illustrative motion · no physical scale
        </span>
      </div>
      <div className="force-studies" aria-label="Five geometric studies">
        {studies.map((item, i) => (
          <button
            key={item.name}
            type="button"
            className="force-study"
            aria-pressed={chosen === i}
            aria-controls="force-study-reading"
            onClick={() => setChosen(i)}
            style={{ '--study-color': item.color } as React.CSSProperties}
          >
            <span className="force-study-number">0{i + 1}</span>
            <h4>{item.name}</h4>
            <span className="force-study-motif">{item.motif}</span>
            <ForceField kind={i} phase={phase} />
            <span className="force-study-caption">{item.text}</span>
            <span className="force-study-explore">
              {chosen === i ? 'Selected study' : 'Explore study'}{' '}
              <span aria-hidden="true">↗</span>
            </span>
          </button>
        ))}
      </div>
      <div className="force-atlas-controls">
        <button
          type="button"
          onClick={() => {
            if (!motion) {
              setMotion(true);
              setPlaying(true);
            } else setPlaying(!playing);
          }}
        >
          {!motion
            ? 'Enable animation'
            : playing
              ? 'Pause animation'
              : 'Play animation'}
        </button>
        <button type="button" onClick={() => setOffset(-time / 12)}>
          Restart
        </button>
        <label>
          Animation phase
          <input
            type="range"
            min="0"
            max="100"
            step="0.1"
            value={phase * 100}
            aria-valuetext={`${Math.round(phase * 100)} percent of illustrative cycle`}
            onChange={(e) => {
              setPlaying(false);
              setOffset(Number(e.target.value) / 100 - time / 12);
            }}
          />
        </label>
        <span>12-second illustrative loop</span>
      </div>
      <div
        className="force-study-reading"
        id="force-study-reading"
        aria-live="polite"
        style={{ '--study-color': study.color } as React.CSSProperties}
      >
        <div>
          <p className="eyebrow">
            Study 0{chosen + 1} · {study.motif}
          </p>
          <h4>{study.name}</h4>
          <p>{study.meaning}</p>
        </div>
        <div>
          <p className="eyebrow">What this shows</p>
          <p>{study.boundary}</p>
        </div>
      </div>
      <p className="force-atlas-closing">
        One proposed geometric origin. Four interaction stories.
      </p>
    </div>
  );
}
