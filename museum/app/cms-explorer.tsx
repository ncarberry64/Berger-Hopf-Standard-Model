'use client';
import { useEffect, useMemo, useState } from 'react';
import { SCIENCE } from './exhibits';
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

export function CMSExplorer() {
  const [vectors, setVectors] = useState<CMSVector[]>([]);
  const [selected, setSelected] = useState(0);
  const [loadState, setLoadState] = useState('loading');

  useEffect(() => {
    fetch('./data/cms-four-vector-sample.json')
      .then(async (response) => {
        if (!response.ok) throw new Error('CMS sample unavailable');
        const payload = (await response.json()) as { vectors: CMSVector[] };
        setVectors(payload.vectors);
        setLoadState('ready');
      })
      .catch(() => {
        setVectors([]);
        setLoadState('error');
      });
  }, []);

  const eventIndices = useMemo(
    () => [...new Set(vectors.map((vector) => vector.event_index))],
    [vectors],
  );
  const selectedEventIndex = eventIndices[selected];
  const eventVectors = useMemo(
    () => vectors.filter((vector) => vector.event_index === selectedEventIndex),
    [selectedEventIndex, vectors],
  );
  const event = eventVectors[0];
  const maxPt = Math.max(...eventVectors.map((vector) => vector.pt), 1);

  return (
    <section
      className="cms-explorer"
      id="cms-data"
      aria-labelledby="cms-explorer-title"
    >
      <div className="cms-explorer-copy">
        <p className="eyebrow">BHSM Engine instrument · real CMS Open Data</p>
        <h2 id="cms-explorer-title">Inspect 64 dimuon events.</h2>
        <p>
          Choose one checked-in event and inspect both measured muon
          four-vectors. The circular instrument maps azimuth to angle,
          transverse momentum to radius, and charge to color. It is a BHSM-style
          rendering of CMS data—not a detector photograph, detector
          reconstruction, BHSM empirical validation, or CERN/CMS endorsement.
        </p>
        <label htmlFor="cms-event-selector">
          Sample event{' '}
          <strong>
            {eventIndices.length ? selected + 1 : 0} / {eventIndices.length}
          </strong>
        </label>
        <input
          id="cms-event-selector"
          type="range"
          min="0"
          max={Math.max(eventIndices.length - 1, 0)}
          value={selected}
          disabled={loadState !== 'ready'}
          onChange={(eventChange) =>
            setSelected(Number(eventChange.target.value))
          }
        />
        {loadState !== 'ready' ? (
          <p role="status">
            {loadState === 'loading'
              ? 'Loading the checked-in CMS sample…'
              : 'The CMS sample could not be loaded. The source record remains available below.'}
          </p>
        ) : null}
        <div className="cms-event-identity">
          <span>Source row {event?.event_index ?? '—'}</span>
          <span>Run {event?.run ?? '—'}</span>
          <span>Event {event?.event ?? '—'}</span>
        </div>
        <div className="cms-field-links">
          <a href="https://opendata.cern.ch/record/303">CMS record ↗</a>
          <a href={`${SCIENCE}/docs/pr98_cms_open_data_animation.md`}>
            Method ↗
          </a>
        </div>
      </div>

      <div className="cms-event-instrument">
        <svg viewBox="0 0 320 320" aria-labelledby="cms-event-plot-title">
          <title id="cms-event-plot-title">
            Selected dimuon event in a polar momentum display
          </title>
          {[55, 95, 135].map((radius) => (
            <circle
              className="instrument-ring"
              cx="160"
              cy="160"
              r={radius}
              key={radius}
            />
          ))}
          <line
            className="instrument-axis"
            x1="20"
            x2="300"
            y1="160"
            y2="160"
          />
          <line
            className="instrument-axis"
            x1="160"
            x2="160"
            y1="20"
            y2="300"
          />
          {eventVectors.map((vector) => {
            const radius = 42 + (vector.pt / maxPt) * 92;
            const x = 160 + Math.cos(vector.phi) * radius;
            const y = 160 - Math.sin(vector.phi) * radius;
            return (
              <g
                className={
                  vector.charge > 0 ? 'track-positive' : 'track-negative'
                }
                key={vector.muon}
              >
                <line x1="160" y1="160" x2={x} y2={y} />
                <circle cx={x} cy={y} r="8" />
                <text x={x + 12} y={y - 10}>
                  μ{vector.charge > 0 ? '+' : '−'}
                </text>
              </g>
            );
          })}
          <circle className="instrument-origin" cx="160" cy="160" r="5" />
        </svg>
        <table className="cms-vector-table">
          <caption>Selected CMS muon four-vectors</caption>
          <thead>
            <tr className="cms-vector-row cms-vector-head">
              <th>Muon</th>
              <th>E</th>
              <th>pT</th>
              <th>η</th>
              <th>φ</th>
            </tr>
          </thead>
          <tbody>
            {eventVectors.map((vector) => (
              <tr className="cms-vector-row" key={vector.muon}>
                <th>μ{vector.charge > 0 ? '+' : '−'}</th>
                <td>{vector.E.toFixed(3)}</td>
                <td>{vector.pt.toFixed(3)}</td>
                <td>{vector.eta.toFixed(3)}</td>
                <td>{vector.phi.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="instrument-caption">
          Energy and momentum in GeV · η and φ dimensionless/radians · two
          source vectors per event
        </p>
      </div>
    </section>
  );
}
