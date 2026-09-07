'use client';

import { useState } from 'react';
import comparison from '../public/data/sandbox-comparison.json';
import { SCIENCE } from './exhibits';

const galleries = [
  {
    id: 'families',
    title: 'Why does matter come in families?',
    subtitle: 'The electron has heavier relatives.',
    lay: 'Electrons, muons and tau particles share the same electric charge but have very different masses. BHSM asks whether their hierarchy can follow from different modes of one internal geometry.',
    meaning:
      'A shared geometric origin would explain a pattern rather than assign each mass separately. The historical ratio is encouraging; the electron residual and the unfinished physical mass calculation remain part of the test.',
  },
  {
    id: 'forces',
    title: 'Can interactions share a geometric origin?',
    subtitle: 'Different strengths. One proposed source.',
    lay: 'The electromagnetic, weak and strong interactions behave differently. BHSM explores whether their relative strengths and a common scale can arise within a shared framework.',
    meaning:
      'These historical screens are comparisons, with scale and convention qualifications. A close decimal alone does not derive a coupling or remove the need for a physical normalization.',
  },
  {
    id: 'quarks',
    title: 'The pattern of changing quark flavors',
    subtitle: 'A ratio can reveal what two separate numbers hide.',
    lay: 'The weak interaction can change one kind of quark into another. The mixing pattern tells us how strongly the different possibilities are connected.',
    meaning:
      'The sandbox reports a closer ratio than either individual mixing strength. That is a useful question for the theory, not permission to add a correction chosen from the observed answer.',
  },
  {
    id: 'neutrinos',
    title: 'Particles that change identity in flight',
    subtitle: 'Neutrino mixing puts several parts of the pattern to the test.',
    lay: 'A neutrino created with one flavor can later be detected with another. BHSM studies whether geometry can organize this mixing and the hierarchy of mass differences.',
    meaning:
      'The same panel shows the closer comparisons and the larger θ23 tension. The supplied marker is a normal-ordering best fit, not the full allowed region. This is an effective neutrino extension, not a claim that the minimal Standard Model contains neutrino masses.',
  },
  {
    id: 'higgs',
    title: 'Where the simple Higgs picture falls short',
    subtitle: 'A visible difference is part of the science.',
    lay: 'The Higgs field participates in the Standard Model’s account of particle masses. The sandbox’s simplest BHSM Higgs mass screen lies below its supplied reference.',
    meaning:
      'The difference is retained openly. The action-derived physical mass, including its interactions, remains to be calculated; the reference value cannot choose the correction.',
  },
];

export function ScienceGallery() {
  const [selected, setSelected] = useState<Record<string, string>>({});
  return (
    <section
      id="exhibits"
      className="science-hall"
      aria-labelledby="science-title"
    >
      <div className="section-heading">
        <p className="eyebrow">The BHSM science exhibits</p>
        <h2 id="science-title">Follow the patterns. Keep the differences.</h2>
        <p>
          Explore the September 2 sandbox snapshot. Every number below is a
          historical BHSM screen or a supplied comparison reference. These are
          neither simulated particle masses nor newly certified physical
          predictions.
        </p>
        <div className="evidence-legend" aria-label="Data labels">
          <span className="data-label">Historical BHSM calculation</span>
          <span className="data-label reference-label">
            Sandbox reference · unverified
          </span>
          <span className="data-label simulation-label">
            Simulated imagery is labeled separately
          </span>
        </div>
      </div>
      {galleries.map((gallery, index) => {
        const rows = comparison.rows.filter((row) => row.group === gallery.id);
        const chosen =
          rows.find((row) => row.id === selected[gallery.id]) ?? rows[0];
        const residual =
          (100 * (chosen.bhsm - chosen.reference)) / chosen.reference;
        return (
          <article
            className="science-exhibit"
            id={`science-${gallery.id}`}
            key={gallery.id}
          >
            <div className="science-placard">
              <p className="eyebrow">
                Exhibit {String(index + 1).padStart(2, '0')} ·{' '}
                {gallery.subtitle}
              </p>
              <h3>{gallery.title}</h3>
              <p className="lay-copy">
                <strong>In plain language</strong>
                {gallery.lay}
              </p>
              <p>{gallery.meaning}</p>
              <p className="data-label">
                COMPARISON ONLY · historical screen + sandbox reference
              </p>
              <p className="reference-note">
                Reference markers were supplied with the sandbox report and have
                not been independently verified. No measurement uncertainty or
                statistical significance is assigned.
              </p>
              <a
                className="text-link"
                href={`${SCIENCE}/${comparison.source.path}`}
              >
                Read the complete source and qualifications ↗
              </a>
            </div>
            <div className="comparison-display">
              <label htmlFor={`select-${gallery.id}`}>Explore a quantity</label>
              <select
                id={`select-${gallery.id}`}
                value={chosen.id}
                onChange={(e) =>
                  setSelected({ ...selected, [gallery.id]: e.target.value })
                }
              >
                {rows.map((row) => (
                  <option value={row.id} key={row.id}>
                    {row.label}
                  </option>
                ))}
              </select>
              <p className="quantity-explanation">{chosen.explanation}</p>
              <div className="comparison-pair" aria-live="polite">
                <div>
                  <span>Historical BHSM screen</span>
                  <strong>{chosen.bhsm}</strong>
                  <small>{chosen.unit}</small>
                </div>
                <div className="reference-value">
                  <span>Sandbox reference · unverified</span>
                  <strong>{chosen.reference}</strong>
                  <small>{chosen.unit}</small>
                </div>
              </div>
              <div className="difference-readout">
                <strong>
                  {residual >= 0 ? '+' : ''}
                  {residual.toFixed(3)}%
                </strong>
                <span>Relative difference from the sandbox marker</span>
              </div>
              <svg
                className="comparison-axis"
                viewBox="0 0 520 95"
                role="img"
                aria-label={`${chosen.label}: ${residual.toFixed(3)} percent relative difference; axis from minus 20 to plus 20 percent`}
              >
                <line
                  x1="30"
                  y1="35"
                  x2="490"
                  y2="35"
                  stroke="currentColor"
                  opacity=".35"
                />
                {[-20, -10, 0, 10, 20].map((v) => (
                  <g key={v}>
                    <line
                      x1={260 + v * 11.5}
                      y1="27"
                      x2={260 + v * 11.5}
                      y2="43"
                      stroke="currentColor"
                    />
                    <text
                      x={260 + v * 11.5}
                      y="71"
                      textAnchor="middle"
                      fill="currentColor"
                      fontSize="22"
                    >
                      {v > 0 ? '+' : ''}
                      {v}%
                    </text>
                  </g>
                ))}
                <line
                  x1="260"
                  y1="35"
                  x2={260 + residual * 11.5}
                  y2="35"
                  stroke="var(--cyan)"
                  strokeWidth="5"
                />
                <circle
                  cx={260 + residual * 11.5}
                  cy="35"
                  r="7"
                  fill="var(--cyan)"
                />
                <path
                  d="M260 19 L267 35 L260 51 L253 35 Z"
                  fill="var(--gold)"
                />
              </svg>
              <p className="axis-caption">
                Gold diamond: reference at 0%. Cyan point: BHSM screen. Shared
                ±20% axis; closer is not proof.
              </p>
              <div className="comparison-table-wrap">
                <table className="comparison-table">
                  <caption>Every numerical pair in this exhibit</caption>
                  <thead>
                    <tr>
                      <th>Quantity</th>
                      <th>BHSM screen</th>
                      <th>Reference*</th>
                      <th>Difference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => {
                      const d =
                        (100 * (row.bhsm - row.reference)) / row.reference;
                      return (
                        <tr key={row.id}>
                          <th>
                            {row.label} {row.unit === 'GeV' ? '(GeV)' : ''}
                          </th>
                          <td>{row.bhsm}</td>
                          <td>{row.reference}</td>
                          <td>
                            {d >= 0 ? '+' : ''}
                            {d.toFixed(3)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <p className="reference-note">
                *Supplied sandbox marker, not independently verified
                experimental data. Difference = 100 × (screen − reference) /
                reference.
              </p>
              {comparison.qualitative_sentinels
                .filter((row) => row.group === gallery.id)
                .map((row) => (
                  <p className="sentinel" key={row.text}>
                    {row.text}
                  </p>
                ))}
            </div>
          </article>
        );
      })}
      <p className="collection-source">
        Source snapshot: {comparison.date} ·{' '}
        <a href="./data/sandbox-comparison.json" download>
          Download all numerical pairs and provenance
        </a>{' '}
        · Differences are computed only for this public comparison display.
      </p>
    </section>
  );
}
