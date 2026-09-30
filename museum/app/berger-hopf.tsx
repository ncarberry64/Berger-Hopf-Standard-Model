'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- SVG carries the accessible diagram description. */
import { useState } from 'react';
import { ScienceConsole, useSceneClock } from './science-console';
import {
  bergerLevel,
  hopfBase,
  hopfPoint,
  projectFiber,
} from '../lib/berger-hopf';
import { SCIENCE } from './exhibits';

const chapters = [
  {
    name: 'Hopf',
    title: 'A sphere woven from circles.',
    tag: 'THE STRUCTURE',
    copy: 'The three-sphere S³ consists of points (x₁,x₂,x₃,x₄) in four-dimensional Euclidean space with x₁²+x₂²+x₃²+x₄² = 1. Hopf’s map provides an interface to this geometry: one circle of S³ becomes one point of an ordinary S². Follow the single selected fiber here.',
    prompt:
      'Follow a moving light around a fiber. Its matching point on the base sphere stays fixed.',
  },
  {
    name: 'Berger',
    title: 'Change the distances. Keep the links.',
    tag: 'THE GEOMETRY',
    copy: 'Berger’s construction changes the metric of that same S³ hypersphere in R⁴: distances along its Hopf fibers change relative to distances across them. The hypersphere has three intrinsic dimensions; a genuinely four-dimensional sphere is S⁴ in R⁵, a different object. These embedding coordinates are not automatically physical spacetime.',
    prompt:
      'Move the fiber-scale slider. The ruler changes; the circles remain linked. This is a change of metric, not a squeezed drawing.',
  },
  {
    name: 'BHSM',
    title: 'From geometry toward predictions.',
    tag: 'THE RESEARCH PROPOSAL',
    copy: 'BHSM combines this fiber structure and geometry with modes, fields and a proposed action. It asks whether particle patterns and interactions can follow from a shared mathematical foundation.',
    prompt:
      'Watch two model levels respond differently. Turning geometric structure into physical predictions also needs independently derived dynamics and experimental tests.',
  },
];
const fibers = Array.from({ length: 18 }, (_, i) => ({
  eta: [0.36, 0.58, 0.8][Math.floor(i / 6)],
  phi: ((i % 6) * Math.PI) / 3,
}));
const colors = ['#ffbc77', '#bda7f5', '#71e5eb'];

export function BergerHopf({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (value: boolean) => void;
}) {
  const [playing, setPlaying] = useState(true);
  const [selected, setSelected] = useState(0);
  const [auto, setAuto] = useState(true);
  const [started, setStarted] = useState(0);
  const [scale, setScale] = useState(1);
  const [manualScale, setManualScale] = useState(false);
  const { ref, time } = useSceneClock(motion && playing);
  const elapsed = Math.max(0, time - started);
  const stage = auto ? (selected + Math.floor(elapsed / 10)) % 3 : selected;
  const fiberScale =
    stage === 0 ? 1 : manualScale ? scale : 1 + 0.3 * Math.sin(elapsed * 0.65);
  const chapter = chapters[stage];
  const angle = time * 0.12 + 0.55;
  const focus = 9;
  const base = hopfBase(hopfPoint(fibers[focus].eta, fibers[focus].phi, 0));
  const level = bergerLevel(2, 0, fiberScale);
  const choose = (i: number) => {
    setSelected(i);
    setAuto(false);
  };
  return (
    <ScienceConsole
      id="berger-hopf"
      number="02"
      label="Berger & Hopf · foundations"
      title="Two mathematical ideas. One deeper question."
      intro="Meet the geometry behind the name: Hopf gives the linked fibers, Berger changes their metric, and BHSM investigates what that structure could explain."
      accent="lavender"
      introAfter={2}
    >
      <div className="bh-chapters" aria-label="Animation chapters">
        {chapters.map((item, i) => (
          <button
            key={item.name}
            onClick={() => choose(i)}
            aria-pressed={stage === i}
          >
            <small>
              0{i + 1} · {item.tag}
            </small>
            <strong>{item.name}</strong>
            <span>
              {i === 0
                ? 'Linked circles'
                : i === 1
                  ? 'Relative distances'
                  : 'Modes → tests'}
            </span>
          </button>
        ))}
      </div>
      <div className="bh-theatre" ref={ref}>
        <div className="bh-projection">
          <svg
            viewBox="0 0 700 480"
            role="img"
            aria-label="Linked Hopf fibers projected from S3, their base sphere, and a Berger fiber-length ruler"
          >
            <defs>
              <radialGradient id="bh-halo">
                <stop stopColor="#342b50" stopOpacity=".65" />
                <stop offset="1" stopColor="#050608" stopOpacity="0" />
              </radialGradient>
            </defs>
            <ellipse cx="260" cy="230" rx="238" ry="205" fill="url(#bh-halo)" />
            <text x="28" y="32" fill="#bda7f5" fontSize="15">
              S³ · PROJECTED FIBERS
            </text>
            {fibers.map(({ eta, phi }, i) => {
              if (stage === 0 && i !== focus) return null;
              const points = Array.from({ length: 97 }, (_, n) =>
                projectFiber(hopfPoint(eta, phi, (n * Math.PI) / 48), angle),
              );
              const d = points
                .map(
                  ([x, y], n) =>
                    `${n ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`,
                )
                .join(' ');
              const dot = projectFiber(
                hopfPoint(eta, phi, time * (stage === 2 ? 1.1 : 0.65)),
                angle,
              );
              return (
                <g key={i}>
                  <path
                    d={d}
                    fill="none"
                    stroke={colors[Math.floor(i / 6)]}
                    strokeWidth={i === focus ? 2.7 : 1.1}
                    opacity={i === focus ? 1 : stage === 0 ? 0.28 : 0.58}
                  />
                  {(stage === 2 || i === focus) && (
                    <circle
                      cx={dot[0]}
                      cy={dot[1]}
                      r={i === focus ? 4.5 : 2.5}
                      fill={colors[Math.floor(i / 6)]}
                    />
                  )}
                </g>
              );
            })}
            <path
              d="M418 130Q475 80 528 126"
              fill="none"
              stroke="#bda7f5"
              strokeDasharray="4 7"
              strokeDashoffset={-time * 12}
            />
            <circle cx="587" cy="151" r="60" fill="#101321" stroke="#75628f" />
            <ellipse
              cx="587"
              cy="151"
              rx="26"
              ry="60"
              fill="none"
              stroke="#453a56"
            />
            <ellipse
              cx="587"
              cy="151"
              rx="60"
              ry="20"
              fill="none"
              stroke="#453a56"
            />
            <circle
              cx={587 + base[0] * 60}
              cy={151 - base[2] * 60}
              r="5"
              fill="#bda7f5"
            />
            <text
              x="587"
              y="57"
              textAnchor="middle"
              fill="#bda7f5"
              fontSize="15"
            >
              HOPF MAP
            </text>
            <text
              x="587"
              y="242"
              textAnchor="middle"
              fill="#c7c1d2"
              fontSize="14"
            >
              S² · ONE POINT PER FIBER
            </text>
            <g opacity={stage === 0 ? 0.4 : 1}>
              <text x="484" y="309" fill="#ffbc77" fontSize="14">
                BERGER METRIC
              </text>
              <path
                d={`M485 341H${485 + 105 * fiberScale}`}
                stroke="#ffbc77"
                strokeWidth="5"
              />
              <path d="M485 385H590" stroke="#71e5eb" strokeWidth="3" />
              <text x="485" y="366" fill="#ffbc77" fontSize="14">
                Along fibers × {fiberScale.toFixed(2)}
              </text>
              <text x="485" y="413" fill="#71e5eb" fontSize="14">
                Across fibers × 1.00
              </text>
            </g>
            <text x="28" y="459" fill="#aaa4b5" fontSize="13">
              Projection of selected fibers · lights are visual guides
            </text>
          </svg>
        </div>
        <div className="bh-story">
          <p className="eyebrow">{chapter.tag}</p>
          <h4>{chapter.title}</h4>
          <p>{chapter.copy}</p>
          <p className="bh-invitation">{chapter.prompt}</p>
          {stage === 2 && (
            <div className="bh-levels">
              <strong>Geometry changes the mode spectrum</strong>
              <div>
                <span>Fiber-sensitive · q = 2</span>
                <b>{level.toFixed(2)}</b>
                <i
                  style={{
                    width: `${(level / 15) * 100}%`,
                    background: '#ffbc77',
                  }}
                />
              </div>
              <div>
                <span>Fiber-neutral · q = 0</span>
                <b>8.00</b>
                <i
                  style={{ width: `${(8 / 15) * 100}%`, background: '#71e5eb' }}
                />
              </div>
              <small>
                Dimensionless scalar proxy · k = 2 · illustrative levels, not
                particle masses.
              </small>
            </div>
          )}
        </div>
      </div>
      <div className="bh-controls">
        <button
          onClick={() => {
            if (!motion) {
              setMotion(true);
              setPlaying(true);
            } else setPlaying(!playing);
          }}
          aria-pressed={motion && playing}
        >
          {motion && playing ? 'Ⅱ Pause animation' : '▶ Play animation'}
        </button>
        <button
          onClick={() => {
            setSelected(0);
            setStarted(time);
            setAuto(true);
            setManualScale(false);
            setPlaying(true);
            setMotion(true);
          }}
        >
          Replay the story ↺
        </button>
        <label>
          Fiber scale <output aria-live="off">{fiberScale.toFixed(2)}</output>
          <input
            aria-label="Berger fiber scale"
            type="range"
            min="0.7"
            max="1.3"
            step="0.01"
            value={fiberScale}
            onChange={(e) => {
              setScale(+e.target.value);
              setManualScale(true);
              choose(stage === 0 ? 1 : stage);
            }}
          />
        </label>
        <button
          onClick={() => {
            setScale(1);
            setManualScale(true);
            choose(1);
          }}
        >
          Round sphere · 1.00
        </button>
      </div>
      <div
        className="bh-pathway"
        aria-label="The path from geometry to predictive tests"
      >
        {[
          'Geometry',
          'Modes & fields',
          'Dynamics',
          'Observables',
          'Independent tests',
        ].map((name, i) => (
          <span
            key={name}
            className={stage === 2 && Math.floor(time) % 5 === i ? 'lit' : ''}
          >
            <small>0{i + 1}</small>
            {name}
          </span>
        ))}
      </div>
      <p className="console-caption">
        <b>Established mathematical construction → BHSM research proposal.</b>{' '}
        The animation explains a starting point. Deriving physical masses,
        interactions and cosmic observables requires further action,
        normalization and testing. Full physical derivation remains open.
      </p>
      <details className="console-details">
        <summary>
          Explore the mathematics · names, metric and model limits
        </summary>
        <p>
          Heinz Hopf and Marcel Berger are the mathematicians behind these
          constructions; this exhibit does not attribute BHSM to them. S³ is a
          three-dimensional sphere in four-dimensional space. The drawing is a
          projection of selected circle fibers, not a literal picture of the
          universe.
        </p>
        <p>
          A Berger metric rescales the fiber direction while retaining the
          horizontal metric: g = gₕ + s²gᵥ. Changing s changes intrinsic
          distances without changing the Hopf map or the linked topology.
        </p>
        <p>
          The two readouts use the repository’s scalar proxy λ(k,j) = a²(k −
          2j)² + 2[(2j + 1)k − 2j²], with a = 1/s in this unit-base
          illustration. They show (k,j) = (2,0) and (2,1). No measured particle
          data choose the slider value. The moving lights do not represent
          solved BHSM eigenfunctions.
        </p>
        <div className="record-links">
          <a href="https://www.maths.tcd.ie/pub/ims/bull51/M5102.pdf">
            Kerin & Wraith · homogeneous sphere metrics ↗
          </a>
          <a
            href={`${SCIENCE}/theory/berger_base_action_coupling_normalization.md`}
          >
            BHSM metric and open action coupling ↗
          </a>
          <a href={`${SCIENCE}/AGENTS.md`}>
            Repository scalar-proxy convention ↗
          </a>
        </div>
      </details>
      <a className="bh-next" href="#science-unification">
        Follow the idea into the forces →
      </a>
    </ScienceConsole>
  );
}
