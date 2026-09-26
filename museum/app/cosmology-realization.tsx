'use client';
import { useEffect, useRef, useState } from 'react';
import transfer from './cosmology-transfer.json';
import {
  environment,
  field,
  response,
  spatialRank,
  type Pattern,
} from '../lib/cosmology-realization';
import { useSceneClock } from './science-console';

const epochs = transfer.rows;
const samples = Array.from({ length: 900 }, (_, i) => {
  const y = 1 - (2 * (i + 0.5)) / 900,
    r = Math.sqrt(1 - y * y),
    a = i * Math.PI * (3 - Math.sqrt(5));
  return [r * Math.cos(a), y, r * Math.sin(a)];
});
const number = (v: number) => (v === 0 ? '0' : v.toExponential(3));

function Globe({
  coefficients,
  turn,
  name,
}: {
  coefficients: number[];
  turn: number;
  name: string;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const ctx = canvas.current?.getContext('2d');
    if (!ctx) return;
    const size = 440,
      middle = size / 2,
      radius = 178;
    ctx.clearRect(0, 0, size, size);
    const atmosphere = ctx.createRadialGradient(
      middle,
      middle,
      80,
      middle,
      middle,
      215,
    );
    atmosphere.addColorStop(0, '#123039');
    atmosphere.addColorStop(0.84, '#0b202b');
    atmosphere.addColorStop(1, '#07111500');
    ctx.fillStyle = atmosphere;
    ctx.fillRect(0, 0, size, size);
    ctx.strokeStyle = '#45616c';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(middle, middle, radius, 0, 2 * Math.PI);
    ctx.stroke();
    const c = Math.cos(turn),
      s = Math.sin(turn),
      slice = Math.sqrt(3) / 2;
    const points = samples.map((p) => {
      const value = field(coefficients, [
        slice * p[0],
        slice * p[1],
        slice * p[2],
        0.5,
      ]);
      return {
        x: c * p[0] + s * p[2],
        y: p[1],
        depth: -s * p[0] + c * p[2],
        value,
      };
    });
    const scale = Math.max(...points.map((p) => Math.abs(p.value)), 1e-20);
    points.sort((a, b) => a.depth - b.depth);
    for (const p of points) {
      const signal = Math.abs(p.value) / scale,
        front = (p.depth + 1) / 2;
      ctx.globalAlpha = 0.12 + 0.82 * front;
      ctx.fillStyle =
        signal < 0.005
          ? '#54707e'
          : p.value >= 0
            ? `hsl(183 78% ${28 + signal * 42}%)`
            : `hsl(36 88% ${26 + signal * 43}%)`;
      ctx.beginPath();
      ctx.arc(
        middle + radius * p.x,
        middle - radius * p.y,
        1.2 + front * 1.8 + signal * 1.1,
        0,
        Math.PI * 2,
      );
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }, [coefficients, turn]);
  return (
    <canvas
      ref={canvas}
      width={440}
      height={440}
      role="img"
      aria-label={`${name}: illustrative n=2 field on a fixed slice of the three-sphere. Cyan positive, gold negative; brightness normalized separately.`}
    />
  );
}

export function CosmologyRealization({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (value: boolean) => void;
}) {
  const [pattern, setPattern] = useState<Pattern>('independent');
  const [density, setDensity] = useState(1),
    [velocity, setVelocity] = useState(0.02);
  const [playing, setPlaying] = useState(true),
    [fixed, setFixed] = useState(1),
    [start, setStart] = useState(0);
  const { ref, time } = useSceneClock(motion && playing);
  const frame = Math.min(
    epochs.length - 1,
    fixed + Math.floor((time - start) / 2.2),
  );
  const finished = frame === epochs.length - 1;
  const e = environment(pattern, density, velocity),
    selected = epochs[frame];
  const x = response(selected.matrix, e),
    rank = spatialRank(x);
  const turn = 0.42 + time * 0.1;
  function seek(i: number) {
    setFixed(i);
    setStart(time);
    setPlaying(false);
  }
  function play() {
    if (!motion) {
      setMotion(true);
      setFixed(finished ? 0 : frame);
      setStart(time);
      setPlaying(true);
      return;
    }
    if (playing && !finished) {
      setFixed(frame);
      setStart(time);
      setPlaying(false);
    } else {
      setFixed(finished ? 0 : frame);
      setStart(time);
      setPlaying(true);
    }
  }
  // Freeze at today; replay is an explicit control, not a cyclical cosmology.
  useEffect(() => {
    if (finished && playing) {
      setFixed(epochs.length - 1);
      setStart(time);
      setPlaying(false);
    }
  }, [finished, playing, time]);
  return (
    <article className="r1-realization" ref={ref} aria-labelledby="r1-title">
      <div className="console-cap">
        <span>R1 · coupled environmental response</span>
        <span>Eight audited epochs</span>
      </div>
      <div className="r1-intro">
        <div>
          <p className="eyebrow">Matter → geometric response</p>
          <h3 id="r1-title">Watch the environment shape the response.</h3>
        </div>
        <p>
          Choose the starting patterns. Follow their computed effect on the two
          topographic components as the reference model evolves.
        </p>
      </div>
      <div
        className="console-selector r1-presets"
        aria-label="Environmental pattern"
      >
        {(
          [
            ['independent', 'Independent patterns'],
            ['aligned', 'One aligned pattern'],
            ['zero', 'No n = 2 input'],
          ] as const
        ).map(([key, label]) => (
          <button
            key={key}
            aria-pressed={pattern === key}
            onClick={() => setPattern(key)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="r1-flow">
        <div className="r1-stage">
          <div className="r1-stage-label">
            <span>Supplied environment</span>
            <strong>zᵢ = 2.1</strong>
          </div>
          <div className="r1-pair">
            <figure>
              <Globe
                coefficients={e[0]}
                turn={turn}
                name="Initial matter density"
              />
              <figcaption>
                <strong>Density pattern</strong>
                <span>δₘ · chosen input</span>
              </figcaption>
            </figure>
            <figure>
              <Globe
                coefficients={e[2]}
                turn={turn}
                name="Initial matter velocity potential"
              />
              <figcaption>
                <strong>Velocity-potential pattern</strong>
                <span>vₘ · chosen input</span>
              </figcaption>
            </figure>
          </div>
        </div>
        <div className="r1-transfer" aria-hidden="true">
          <span>
            Saved
            <br />
            R1 transfer
          </span>
          <b>→</b>
        </div>
        <div className="r1-stage r1-output">
          <div className="r1-stage-label">
            <span>Calculated response</span>
            <strong>z = {selected.z.toFixed(2)}</strong>
          </div>
          <div className="r1-pair">
            <figure>
              <Globe
                coefficients={x[0]}
                turn={turn}
                name="Topographic amplitude response"
              />
              <figcaption>
                <strong>Topographic amplitude</strong>
                <span>q₂ · coefficient norm {number(Math.hypot(...x[0]))}</span>
              </figcaption>
            </figure>
            <figure>
              <Globe
                coefficients={x[1]}
                turn={turn}
                name="Reference-normalized momentum response"
              />
              <figcaption>
                <strong>Momentum-like response</strong>
                <span>Π₂ · coefficient norm {number(Math.hypot(...x[1]))}</span>
              </figcaption>
            </figure>
          </div>
        </div>
      </div>
      <p className="r1-legend">
        <span className="r1-positive">● Positive</span>
        <span className="r1-negative">● Negative</span>
        <span>
          Each globe rescales color separately to reveal shape. Rotation changes
          only the view.
        </span>
      </p>
      <div className="r1-transport-controls">
        <button onClick={play}>
          {!motion
            ? 'Enable animation'
            : playing && !finished
              ? 'Pause history'
              : finished
                ? 'Replay history'
                : 'Play history'}
        </button>
        <button
          onClick={() => seek(Math.max(0, frame - 1))}
          disabled={frame === 0}
        >
          ← Earlier
        </button>
        <button
          onClick={() => seek(Math.min(8, frame + 1))}
          disabled={finished}
        >
          Later →
        </button>
        <span>
          {frame === 0 ? 'Initial state' : `Audited epoch ${frame} of 8`} ·{' '}
          {finished ? 'present-day reference' : `z = ${selected.z}`}
        </span>
      </div>
      <label className="r1-timeline">
        Audited epoch · equal playback spacing, not equal cosmic time
        <input
          type="range"
          min={0}
          max={8}
          step={1}
          value={frame}
          onChange={(event) => seek(Number(event.target.value))}
          aria-valuetext={`Redshift ${selected.z}${frame === 0 ? ', initial state' : ', audited epoch'}`}
        />
      </label>
      {!motion && (
        <p className="r1-motion-note">
          Museum motion is off. Step through epochs manually, or choose Enable
          animation to turn museum motion on.
        </p>
      )}
      <div className="r1-results">
        <div>
          <span>Environmental transfer</span>
          <strong>Temporal rank {selected.rank}</strong>
          <p>
            {frame === 0
              ? 'No elapsed response at the anchor.'
              : 'The matter-only transfer spans both temporal components.'}
          </p>
        </div>
        <div>
          <span>This chosen realization</span>
          <strong>Spatial rank {rank}</strong>
          <p>
            {rank === 0
              ? 'No topographic pattern in this frame.'
              : rank === 1
                ? 'Both output rows share one spatial profile (possibly with opposite signs).'
                : 'The output rows require two spatial profiles.'}
          </p>
        </div>
      </div>
      <div className="r1-coefficients">
        <h4>Two response rows across nine spatial coefficients</h4>
        <div className="table-scroll">
          <table>
            <caption>
              Signed coefficients in the explicit illustrative quadratic basis
            </caption>
            <thead>
              <tr>
                <th scope="col">State</th>
                {Array.from({ length: 9 }, (_, i) => (
                  <th scope="col" key={i}>
                    h{i + 1}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {x.map((row, i) => (
                <tr key={i}>
                  <th scope="row">{i === 0 ? 'q₂' : 'Π₂'}</th>
                  {row.map((v, j) => (
                    <td
                      key={j}
                      className={
                        v === 0 ? '' : v > 0 ? 'r1-positive' : 'r1-negative'
                      }
                    >
                      {number(v)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <details className="console-details r1-method">
        <summary>Change the inputs · inspect the calculation</summary>
        <div className="r1-inputs">
          <label>
            Density coefficient: {density.toFixed(2)}
            <input
              type="range"
              min={-1}
              max={1}
              step={0.05}
              value={density}
              disabled={pattern === 'zero'}
              onChange={(ev) => setDensity(Number(ev.target.value))}
            />
          </label>
          <label>
            Velocity-potential coefficient: {velocity.toFixed(3)}
            <input
              type="range"
              min={-0.1}
              max={0.1}
              step={0.002}
              value={velocity}
              disabled={pattern === 'zero'}
              onChange={(ev) => setVelocity(Number(ev.target.value))}
            />
          </label>
        </div>
        <p>
          The initial topographic state and radiation perturbations are set to
          zero. Each frame evaluates X(z) = Uₓₑ(z) Eᵢ using the saved (q₂, Π₂)
          matrix. Only the nine saved frames are shown: the anchor and eight
          later epochs. No interpolated epoch is presented as an audited result.
        </p>
        <p>
          The globes are the fixed X₄ = ½ slice of unit S³, not sky maps. They
          evaluate nine trace-free quadratic polynomials; the examples use h₁ =
          X₁² − X₂² and h₃ = 2X₁X₃. Density and velocity use h₁ together when
          aligned, and h₁/h₃ when independent. Coefficient norms are Euclidean
          basis norms, not physical field norms. These chosen inputs demonstrate
          linear response; they are not a derived cosmic history, calibrated
          amplitude or selected sky axis.
        </p>
        <p>
          Π₂ = 2a³Gₛ,₂ζ̇ is reference-normalized, not identified with the full
          coupled canonical momentum. Rank is evaluated at relative
          singular-value tolerance 10⁻⁸. A rank-one snapshot alone does not
          establish one common profile over an entire history.
        </p>
        <a href={transfer.source}>Saved matrices and provenance ↗</a>
      </details>
    </article>
  );
}
