'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline SVG graphics use named image semantics. */
import { useEffect, useState } from 'react';
import { useSceneClock } from './science-console';
import { invariantMass } from '../lib/science-media';

type CMSVector = {
  event_index: number;
  run: number;
  event: number;
  muon: number;
  E: number;
  px: number;
  py: number;
  pz: number;
  pt: number;
  eta: number;
  phi: number;
  charge: number;
};

export function CMSExplorer({ motion }: { motion: boolean }) {
  const [vectors, setVectors] = useState<CMSVector[]>([]);
  const [selected, setSelected] = useState(0),
    [error, setError] = useState(false);
  const [playing, setPlaying] = useState(true),
    [fixed, setFixed] = useState(0),
    [start, setStart] = useState(0);
  const { ref, time } = useSceneClock(motion && playing);
  const phase = playing ? ((time - start) / 10) % 1 : fixed;
  const blend = 0.5 - 0.5 * Math.cos(2 * Math.PI * phase);
  useEffect(() => {
    const controller = new AbortController();
    fetch('./data/cms-four-vector-sample.json', { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw Error('Unavailable');
        return r.json();
      })
      .then((d) => setVectors((d as { vectors: CMSVector[] }).vectors))
      .catch((e) => {
        if (e.name !== 'AbortError') setError(true);
      });
    return () => controller.abort();
  }, []);
  const ids = [...new Set(vectors.map((v) => v.event_index))];
  const pair = vectors.filter((v) => v.event_index === ids[selected]);
  const event = pair[0];
  const scale = Math.max(
    1,
    ...vectors.flatMap((v) => [
      Math.asinh(Math.abs(v.px)),
      Math.asinh(Math.abs(v.pz)),
    ]),
  );
  // Exactly the normalized display mapping in the retained PR98 GIF generator.
  const raw = (v: CMSVector) => [
    (Math.asinh(v.px) / scale + 1) / 2,
    (Math.asinh(v.pz) / scale + 1) / 2,
  ];
  const mapped = (v: CMSVector) => [
    (v.phi + Math.PI) / (2 * Math.PI),
    (Math.tanh(v.eta / 3) + 1) / 2,
  ];
  const point = (v: CMSVector, b: number) => {
    const a = raw(v),
      z = mapped(v);
    return [
      58 + 484 * (a[0] + b * (z[0] - a[0])),
      342 - 274 * (a[1] + b * (z[1] - a[1])),
    ];
  };
  const toggle = () => {
    if (playing) setFixed(phase);
    else setStart(time - fixed * 10);
    setPlaying(!playing);
  };
  return (
    <div className="cms-console" ref={ref} id="cms-data">
      <div className="cms-instrument-top">
        <span>128 MUONS / 64 RECORDED EVENTS</span>
        <button
          disabled={!motion || !vectors.length}
          onClick={toggle}
          aria-pressed={!playing}
        >
          {playing && motion ? 'Ⅱ Pause mapping' : '▶ Animate mapping'}
        </button>
      </div>
      {!vectors.length ? (
        <output className="cms-loading">
          {error
            ? 'The CMS sample could not be loaded. Open the original animation or source record below.'
            : 'Loading the recorded CMS sample…'}
        </output>
      ) : (
        <>
          <div className="cms-station-grid">
            <button
              className="event-stage cms-coordinate-stage"
              onClick={toggle}
              aria-pressed={!playing}
              aria-label="Pause or resume the CMS coordinate animation"
            >
              <svg
                viewBox="0 0 600 405"
                role="img"
                aria-label="128 real CMS muon records continuously map from compressed px and pz coordinates into a compressed phi and eta chart. The selected event is highlighted."
              >
                <defs>
                  <radialGradient id="cms-field-light">
                    <stop stopColor="#221932" />
                    <stop offset="1" stopColor="#050509" />
                  </radialGradient>
                </defs>
                <rect width="600" height="405" fill="url(#cms-field-light)" />
                <text x="28" y="30" fill="#bda7f5" fontSize="12">
                  CMS / COORDINATE MAPPING
                </text>
                <text
                  x="572"
                  y="30"
                  fill="#ffbc77"
                  textAnchor="end"
                  fontSize="12"
                >
                  {!playing || !motion
                    ? blend === 0
                      ? 'MOMENTUM CHART'
                      : blend === 1
                        ? 'ANGULAR CHART'
                        : 'PAUSED / COORDINATE BLEND'
                    : phase < 0.5
                      ? 'MOMENTUM → ANGLES'
                      : 'ANGLES → MOMENTUM'}
                </text>
                {[0, 0.25, 0.5, 0.75, 1].map((f) => (
                  <g key={f}>
                    <line
                      x1={58 + 484 * f}
                      x2={58 + 484 * f}
                      y1="68"
                      y2="342"
                      stroke="#44314f"
                      strokeDasharray={f === 0.5 ? undefined : '2 6'}
                    />
                    <line
                      x1="58"
                      x2="542"
                      y1={342 - 274 * f}
                      y2={342 - 274 * f}
                      stroke="#44314f"
                      strokeDasharray={f === 0.5 ? undefined : '2 6'}
                    />
                  </g>
                ))}
                <path
                  d="M28 88V50H85M515 50H572V88M28 322V360H85M515 360H572V322"
                  fill="none"
                  stroke="#bda7f5"
                  strokeWidth="3"
                />
                {vectors.map((v) => {
                  const [x, y] = point(v, blend),
                    color = v.charge < 0 ? '#71e5eb' : '#ffbc77';
                  const chosen = v.event_index === ids[selected];
                  const [ax, ay] = point(v, 0),
                    [bx, by] = point(v, 1);
                  return (
                    <g key={`${v.event_index}-${v.muon}`}>
                      {chosen && (
                        <path
                          d={`M${ax} ${ay}L${bx} ${by}`}
                          stroke={color}
                          opacity=".35"
                          strokeDasharray="3 5"
                        />
                      )}
                      <circle
                        cx={x}
                        cy={y}
                        r={chosen ? 6 : 2.7}
                        fill={color}
                        opacity={chosen ? 1 : 0.6}
                      />
                      {chosen && (
                        <>
                          <circle
                            cx={x}
                            cy={y}
                            r="12"
                            fill="none"
                            stroke={color}
                          />
                          <text
                            x={Math.min(520, x + 17)}
                            y={Math.max(80, y - 13)}
                            fill={color}
                            fontSize="16"
                          >
                            μ{v.charge > 0 ? '+' : '−'}
                          </text>
                        </>
                      )}
                    </g>
                  );
                })}
                <text
                  x="300"
                  y="389"
                  fill="#b7a2c8"
                  textAnchor="middle"
                  fontSize="12"
                >
                  Normalized coordinates · motion shows a change of chart
                </text>
              </svg>
            </button>
            <div className="cms-selected-event">
              <p className="eyebrow">Selected collision</p>
              <h4>
                Event {selected + 1}
                <span> / {ids.length}</span>
              </h4>
              <dl className="cms-record-id">
                <div>
                  <dt>Run</dt>
                  <dd>{event.run}</dd>
                </div>
                <div>
                  <dt>CMS event</dt>
                  <dd>{event.event}</dd>
                </div>
              </dl>
              <div className="cms-mass">
                <span>Dimuon invariant mass</span>
                <strong>
                  {invariantMass(pair).toFixed(4)}
                  <small> GeV</small>
                </strong>
              </div>
              {pair.map((v) => (
                <div
                  className="cms-muon-readout"
                  key={v.muon}
                  style={{ borderColor: v.charge < 0 ? '#71e5eb' : '#ffbc77' }}
                >
                  <b style={{ color: v.charge < 0 ? '#71e5eb' : '#ffbc77' }}>
                    μ{v.charge > 0 ? '+' : '−'}
                  </b>
                  <div>
                    <span>Energy</span>
                    <strong>{v.E.toFixed(3)} GeV</strong>
                  </div>
                  <div>
                    <span>Transverse momentum</span>
                    <strong>{v.pt.toFixed(3)} GeV</strong>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="cms-mapping-controls">
            <button
              aria-pressed={!playing && fixed === 0}
              onClick={() => {
                setFixed(0);
                setPlaying(false);
              }}
            >
              pₓ / pz · momentum
            </button>
            <div
              className="cms-mapping-meter"
              role="img"
              aria-label={`${Math.round(blend * 100)} percent blend toward the angular chart`}
            >
              <span style={{ width: `${blend * 100}%` }} />
            </div>
            <button
              aria-pressed={!playing && fixed === 0.5}
              onClick={() => {
                setFixed(0.5);
                setPlaying(false);
              }}
            >
              φ / η · angles
            </button>
          </div>
          <div className="cms-event-controls">
            <label htmlFor="cms-event-selector">
              Inspect a recorded collision{' '}
              <strong>
                {selected + 1} / {ids.length}
              </strong>
            </label>
            <input
              id="cms-event-selector"
              type="range"
              min="0"
              max={ids.length - 1}
              value={selected}
              onChange={(e) => setSelected(+e.target.value)}
            />
            <div className="track-key">
              <span>
                <i style={{ background: '#71e5eb' }} />
                Negative muon
              </span>
              <span>
                <i style={{ background: '#ffbc77' }} />
                Positive muon
              </span>
            </div>
          </div>
        </>
      )}
      <p className="console-caption">
        <b>Real CMS measurements · animated coordinate mapping</b> · Each point
        is a muon record. Movement changes its display coordinates; it is not a
        particle trajectory or a new BHSM prediction.
      </p>
      <details className="console-details">
        <summary>
          Read the event · four-vectors and coordinate definitions
        </summary>
        <p>
          The animation uses the same 128 records and display mapping as the
          original CMS animation. Momentum coordinates use signed asinh
          compression; the angular chart uses (φ + π)/(2π) and (tanh(η/3) +
          1)/2. Interpolation between those endpoints is illustrative. It is not
          a new run of the validated BHSM Engine.
        </p>
        <div className="table-scroll">
          <table>
            <caption>
              Selected CMS muons · energy and momentum in GeV, natural units c =
              1
            </caption>
            <thead>
              <tr>
                <th>Muon</th>
                <th>E</th>
                <th>pₓ</th>
                <th>py</th>
                <th>pz</th>
                <th>η</th>
                <th>φ · radians</th>
              </tr>
            </thead>
            <tbody>
              {pair.map((v) => (
                <tr key={v.muon}>
                  <th>μ{v.charge > 0 ? '+' : '−'}</th>
                  {[v.E, v.px, v.py, v.pz, v.eta, v.phi].map((n, i) => (
                    <td key={i}>{n.toFixed(5)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <a href="https://opendata.cern.ch/record/303">
          CMS Open Data Record 303 ↗
        </a>{' '}
        ·{' '}
        <a href="./data/cms-four-vector-sample.json" download>
          Download the 64-event sample
        </a>
      </details>
    </div>
  );
}
