'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline SVG needs image semantics; an HTML img cannot contain this interactive drawing. */
import { useEffect, useState } from 'react';
import { useSceneClock } from './science-console';
import { collisionDemo } from '../lib/collision-demo';
import {
  invariantMass,
  trackPoints,
  type FourVector,
} from '../lib/science-media';

type Track = FourVector & { label: string; charge: number; color: string };
type CMSVector = FourVector & {
  event_index: number;
  run: number;
  event: number;
  charge: number;
  pt: number;
  phi: number;
};
const demos = [
  {
    title: 'Electron + positron → muon pair',
    input: 'e⁻ + e⁺',
    energy: 10,
    masses: [0.00051099895069, 0.00051099895069, 0.1056583755, 0.1056583755],
    charges: [-1, 1, -1, 1],
    labels: ['μ⁻', 'μ⁺'],
    colors: ['#65e6ef', '#f6c46f'],
    angle: 58,
    text: 'An electron and its antiparticle can annihilate into a heavier muon pair. This selected channel illustrates two-body energy and momentum conservation; its frequency of occurrence is not simulated.',
  },
  {
    title: 'Electron + positron → two photons',
    input: 'e⁻ + e⁺',
    energy: 4,
    masses: [0.00051099895069, 0.00051099895069, 0, 0],
    charges: [-1, 1, 0, 0],
    labels: ['γ₁', 'γ₂'],
    colors: ['#f296d9', '#f296d9'],
    angle: 112,
    text: 'The incoming electric charges cancel. Two neutral photons carry away the energy and momentum. Neutral tracks are drawn straight; visible photon lines are an explanatory convention.',
  },
  {
    title: 'Proton + proton → elastic scattering',
    input: 'p + p',
    energy: 10,
    masses: [0.93827208943, 0.93827208943, 0.93827208943, 0.93827208943],
    charges: [1, 1, 1, 1],
    labels: ['p₁', 'p₂'],
    colors: ['#b99cff', '#b99cff'],
    angle: 39,
    text: 'In this elastic example the outgoing particles remain protons. The scattering angle is selected for the demonstration, not sampled from a physical differential cross-section.',
  },
];

export function CollisionTheatre({ motion }: { motion: boolean }) {
  const [cms, setCms] = useState<CMSVector[]>([]),
    [failed, setFailed] = useState(false);
  const [baseIndex, setIndex] = useState(0),
    [started, setStarted] = useState(0),
    [playing, setPlaying] = useState(true),
    [mode, setMode] = useState('all');
  const { ref: sceneRef, time } = useSceneClock(motion && playing);
  const clock = (time - started) % 8;
  useEffect(() => {
    fetch('./data/cms-four-vector-sample.json')
      .then((r) => {
        if (!r.ok) throw Error();
        return r.json();
      })
      .then((d) => setCms((d as { vectors: CMSVector[] }).vectors))
      .catch(() => setFailed(true));
  }, []);
  const eventIds = [...new Set(cms.map((v) => v.event_index))];
  const playlist =
    mode === 'real'
      ? eventIds.map((id) => ({ real: true, id }))
      : mode === 'demo'
        ? demos.map((_, id) => ({ real: false, id }))
        : demos.flatMap((_, id) => [
            { real: false, id },
            ...(eventIds[id] !== undefined
              ? [{ real: true, id: eventIds[id] }]
              : []),
          ]);
  const index =
    (baseIndex + Math.floor((time - started) / 8)) %
    Math.max(1, playlist.length);
  const item = playlist[index % Math.max(1, playlist.length)];
  const current = item?.real
    ? cms.filter((v) => v.event_index === item.id)
    : [];
  const demo = demos[item && !item.real ? item.id : 0];
  const result = collisionDemo(
    demo.energy,
    demo.masses,
    demo.angle,
    demo.charges,
  );
  const tracks: Track[] = item?.real
    ? current.map((v) => ({
        ...v,
        label: v.charge > 0 ? 'μ⁺' : 'μ⁻',
        color: v.charge > 0 ? '#f6c46f' : '#65e6ef',
      }))
    : result.outgoing!.map((v, i) => ({
        ...v,
        label: demo.labels[i],
        charge: demo.charges[i + 2],
        color: demo.colors[i],
      }));
  const reveal =
    !motion || (!playing && clock === 0)
      ? 1
      : Math.min(1, Math.max(0, (clock - 1.4) / 2.2));
  const approach =
    !motion || (!playing && clock === 0) ? 1 : Math.min(1, clock / 1.4);
  const step = (delta: number) => {
    setIndex((index + delta + playlist.length) % Math.max(1, playlist.length));
    setStarted(time);
  };
  return (
    <div className="collision-theatre" ref={sceneRef}>
      <div className="media-toolbar">
        <span className="data-label">
          {item?.real
            ? 'REAL CMS EVENT · schematic tracks'
            : 'SIMULATED COLLISION · physical reference masses'}
        </span>
        <label>
          Event collection{' '}
          <select
            value={mode}
            onChange={(e) => {
              setMode(e.target.value);
              setIndex(0);
              setStarted(time);
            }}
          >
            <option value="all">Guided tour · data + demonstrations</option>
            <option value="real">64 recorded CMS events</option>
            <option value="demo">Three collision demonstrations</option>
          </select>
        </label>
      </div>
      {failed && (
        <output>
          Recorded events are unavailable. Demonstrations remain available.
        </output>
      )}
      {mode === 'real' && !cms.length ? (
        <output>
          {failed
            ? 'Choose a demonstration above.'
            : 'Loading the recorded event sample…'}
        </output>
      ) : (
        <>
          <button
            type="button"
            className="event-stage"
            onClick={() => setPlaying((p) => !p)}
            aria-label={
              playing && motion
                ? 'Pause collision and read event'
                : 'Resume collision tour'
            }
            aria-pressed={!playing}
          >
            <svg
              viewBox="70 0 660 570"
              role="img"
              aria-label="Detector-inspired transverse event display, with charged paths curling and neutral paths straight"
            >
              <defs>
                <radialGradient id="collision-space">
                  <stop stopColor="#1f1835" />
                  <stop offset="1" stopColor="#050509" />
                </radialGradient>
                <filter id="track-glow">
                  <feGaussianBlur stdDeviation="2" />
                </filter>
              </defs>
              <rect width="800" height="570" fill="url(#collision-space)" />
              {[65, 115, 165, 220].map((r) => (
                <circle
                  key={r}
                  cx="400"
                  cy="270"
                  r={r}
                  fill="none"
                  stroke="#365369"
                  strokeDasharray={r === 220 ? '3 7' : undefined}
                />
              ))}
              {Array.from({ length: 24 }, (_, i) => (
                <line
                  key={i}
                  x1={(400 + 224 * Math.cos((i * Math.PI) / 12)).toFixed(2)}
                  y1={(270 + 224 * Math.sin((i * Math.PI) / 12)).toFixed(2)}
                  x2={(400 + 235 * Math.cos((i * Math.PI) / 12)).toFixed(2)}
                  y2={(270 + 235 * Math.sin((i * Math.PI) / 12)).toFixed(2)}
                  stroke="#7993a7"
                />
              ))}
              <text x="95" y="35" fill="#b9ccdb" fontSize="15">
                COLLISION / TRANSVERSE VIEW
              </text>
              <text
                x="705"
                y="35"
                textAnchor="end"
                fill="#b9ccdb"
                fontSize="15"
              >
                {item?.real ? 'CMS · 2010' : 'TWO-BODY KINEMATICS'}
              </text>
              {[0, 1].map((side) => (
                <g key={`beam-${side}`} opacity={1 - Math.min(1, reveal * 3)}>
                  <line
                    x1="400"
                    y1={side ? 500 : 45}
                    x2="400"
                    y2={side ? 500 - 230 * approach : 45 + 225 * approach}
                    stroke={side ? '#ffbc77' : '#71e5eb'}
                    strokeWidth="3"
                  />
                  <circle
                    cx="400"
                    cy={side ? 500 - 230 * approach : 45 + 225 * approach}
                    r="6"
                    fill={side ? '#ffbc77' : '#71e5eb'}
                  />
                </g>
              ))}
              <circle
                cx="400"
                cy="270"
                r={8 + Math.sin(Math.min(1, reveal) * Math.PI) * 70}
                fill="#fff"
                opacity={Math.max(0, 0.3 - reveal * 0.7)}
              />
              {Array.from({ length: 32 }, (_, i) => (
                <path
                  key={`module-${i}`}
                  d={`M${400 + 205 * Math.cos((i * Math.PI) / 16)} ${270 + 205 * Math.sin((i * Math.PI) / 16)}L${400 + 220 * Math.cos((i * Math.PI) / 16)} ${270 + 220 * Math.sin((i * Math.PI) / 16)}`}
                  stroke={i % 2 ? '#8d729c' : '#c09a74'}
                  strokeWidth="5"
                  opacity=".6"
                />
              ))}
              {tracks.map((v, i) => {
                const pt = Math.hypot(v.px, v.py);
                const pts = trackPoints(
                  Math.atan2(v.py, v.px),
                  v.charge,
                  pt,
                  reveal,
                );
                const d = pts
                  .map(
                    (p, j) =>
                      `${j ? 'L' : 'M'}${p[0].toFixed(2)} ${p[1].toFixed(2)}`,
                  )
                  .join(' ');
                const end = pts.at(-1)!;
                return (
                  <g key={i}>
                    <path
                      d={d}
                      stroke={v.color}
                      fill="none"
                      strokeWidth="9"
                      opacity=".22"
                      filter="url(#track-glow)"
                    />
                    <path d={d} stroke={v.color} fill="none" strokeWidth="3" />
                    <circle
                      cx={end[0].toFixed(2)}
                      cy={end[1].toFixed(2)}
                      r="5"
                      fill={v.color}
                    />
                    <text
                      x={end[0].toFixed(2)}
                      y={(end[1] - 17 - i * 4).toFixed(2)}
                      textAnchor="middle"
                      fill={v.color}
                      fontSize="23"
                    >
                      {v.label}
                    </text>
                  </g>
                );
              })}
              <circle cx="400" cy="270" r={reveal > 0 ? 7 : 2} fill="#fff6df" />
              <text
                x="400"
                y="530"
                fill="#e8f0f5"
                textAnchor="middle"
                fontSize="18"
              >
                {playing && motion
                  ? 'Click to pause and inspect this collision'
                  : 'Paused · click to continue'}
              </text>
            </svg>
          </button>
          <div className="track-key">
            {tracks.map((v, i) => (
              <span key={i}>
                <i style={{ background: v.color }} />
                {v.label} ·{' '}
                {v.charge === 0
                  ? 'neutral'
                  : v.charge > 0
                    ? 'positive'
                    : 'negative'}
              </span>
            ))}
          </div>
          <div className="media-toolbar">
            <button onClick={() => step(-1)}>← Previous</button>
            <button onClick={() => setPlaying((p) => !p)} disabled={!motion}>
              {playing && motion ? 'Pause tour' : 'Play tour'}
            </button>
            <button onClick={() => step(1)}>Next collision →</button>
            <span>
              {(index % Math.max(1, playlist.length)) + 1} / {playlist.length}
            </span>
          </div>
          <div
            className="event-story"
            aria-live={playing && motion ? 'off' : 'polite'}
          >
            <p className="eyebrow">
              {item?.real
                ? `Run ${current[0]?.run} · event ${current[0]?.event}`
                : demo.input}
            </p>
            <h4>
              {item?.real
                ? 'A recorded proton-collision dimuon event'
                : demo.title}
            </h4>
            <p>
              {item?.real
                ? 'These two reconstructed muon four-vectors come from CMS Open Data. Other collision products are not included in this sample. The curved paths visualize momentum and charge; they are not reconstructed detector hits or a BHSM-generated event.'
                : demo.text}
            </p>
            <div className="science-readout">
              <div>
                <small>
                  {item?.real
                    ? 'Measured dimuon subsystem mass'
                    : 'Selected center-of-mass energy'}
                </small>
                <strong>
                  {(item?.real ? invariantMass(current) : demo.energy).toFixed(
                    4,
                  )}{' '}
                  GeV
                </strong>
              </div>
              <div>
                <small>
                  {item?.real ? 'Data comparison' : 'Conservation check'}
                </small>
                <strong>
                  {item?.real
                    ? `${tracks.length} reconstructed muons`
                    : `${result.residual!.toExponential(1)} residual`}
                </strong>
              </div>
            </div>
            <details className="console-details">
              <summary>Explore the science · particle energies</summary>
              <div className="table-scroll">
                <table>
                  <caption>
                    {item?.real
                      ? 'CMS reconstructed values'
                      : 'Calculated demonstration values'}{' '}
                    · natural units c = 1
                  </caption>
                  <thead>
                    <tr>
                      <th>Particle</th>
                      <th>E · GeV</th>
                      <th>pT · GeV</th>
                      <th>pz · GeV</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tracks.map((v, i) => (
                      <tr key={i}>
                        <th>{v.label}</th>
                        <td>{v.E.toFixed(4)}</td>
                        <td>{Math.hypot(v.px, v.py).toFixed(4)}</td>
                        <td>{v.pz.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="media-note">
                Incoming beams are shown schematically in the screen plane; real
                collider beams run along the detector axis. Track lengths and
                curvature are scaled for visibility. No event rates, branching
                probabilities or BHSM amplitudes are inferred.{' '}
                <a href="https://opendata.cern.ch/record/303">CMS source ↗</a> ·{' '}
                <a href="https://physics.nist.gov/cuu/Constants/Table/allascii.txt">
                  CODATA reference masses ↗
                </a>
              </p>
            </details>
          </div>
        </>
      )}
    </div>
  );
}
