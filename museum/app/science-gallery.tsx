'use client';

import { useState } from 'react';
import comparison from './sandbox-comparison.json';
import { SCIENCE } from './exhibits';
import references from './reference-data.json';

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
      'The historical ratio can be compared with a neutral-B mixing extraction. Experimental and theory uncertainties remain separate; this comparison cannot choose a correction to the BHSM result.',
  },
  {
    id: 'neutrinos',
    title: 'Particles that change identity in flight',
    subtitle: 'Neutrino mixing puts several parts of the pattern to the test.',
    lay: 'A neutrino created with one flavor can later be detected with another. BHSM studies whether geometry can organize this mixing and the hierarchy of mass differences.',
    meaning:
      'The same panel shows the closer comparisons and the larger θ23 tension. The reference is an explicitly selected normal-ordering global fit, not the full allowed region. This is an effective neutrino extension, not a claim that the minimal Standard Model contains neutrino masses.',
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
      id="comparisons"
      className="science-hall comparison-collection"
      aria-label="BHSM comparisons with published reference data"
    >
      {galleries.map((gallery, index) => {
        const rows = comparison.rows.filter((r) => r.group === gallery.id);
        const chosen =
          rows.find((r) => r.id === selected[gallery.id]) ?? rows[0];
        const ref = references.comparisons.find((r) => r.id === chosen.id)!;
        const residual = (100 * (chosen.bhsm - ref.value)) / ref.value;
        const x = (n: number) => 260 + 11.5 * Math.max(-20, Math.min(20, n));
        return (
          <article
            className="science-exhibit"
            id={`science-${gallery.id}`}
            key={gallery.id}
          >
            <div className="science-placard">
              <p className="eyebrow">
                {String(index + 7).padStart(2, '0')} · {gallery.subtitle}
              </p>
              <h3>{gallery.title}</h3>
              <p className="lay-copy">{gallery.lay}</p>
              <p>{gallery.meaning}</p>
              <p className="data-label">
                COMPARISON ONLY · historical BHSM screen + published reference
              </p>
              <p className="reference-note">
                Differences test the retained screen. They are not a statistical
                significance or a completed BHSM prediction.
              </p>
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
                {rows.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.label}
                  </option>
                ))}
              </select>
              <p className="quantity-explanation">{chosen.explanation}</p>
              <div className="comparison-pair">
                <div>
                  <span>Historical BHSM screen</span>
                  <strong>{chosen.bhsm}</strong>
                  <small>{chosen.unit}</small>
                </div>
                <div className="reference-value">
                  <span>{ref.label}</span>
                  <strong>{Number(ref.value.toPrecision(7))}</strong>
                  <small>{ref.uncertainty_text}</small>
                </div>
              </div>
              <div className="difference-readout">
                <strong>
                  {residual >= 0 ? '+' : ''}
                  {residual.toFixed(3)}%
                </strong>
                <span>Relative difference from the published reference</span>
              </div>
              <svg
                className="comparison-axis"
                viewBox="0 0 520 95"
                role="img"
                aria-label={`${chosen.label}: ${residual.toFixed(3)} percent difference from published reference`}
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
                      x1={x(v)}
                      x2={x(v)}
                      y1="27"
                      y2="43"
                      stroke="currentColor"
                    />
                    <text
                      x={x(v)}
                      y="76"
                      textAnchor="middle"
                      fill="currentColor"
                      fontSize="19"
                    >
                      {v > 0 ? '+' : ''}
                      {v}%
                    </text>
                  </g>
                ))}
                {ref.lower !== null && ref.upper !== null && (
                  <line
                    x1={x((100 * (ref.lower - ref.value)) / ref.value)}
                    x2={x((100 * (ref.upper - ref.value)) / ref.value)}
                    y1="35"
                    y2="35"
                    stroke="var(--gold)"
                    strokeWidth="10"
                  />
                )}
                <line
                  x1="260"
                  x2={x(residual)}
                  y1="35"
                  y2="35"
                  stroke="var(--cyan)"
                  strokeWidth="3"
                />
                <circle cx={x(residual)} cy="35" r="7" fill="var(--cyan)" />
                <path d="M260 21L267 35L260 49L253 35Z" fill="var(--gold)" />
              </svg>
              <p className="axis-caption">
                Cyan: BHSM screen. Gold: reference and available uncertainty.
                Very narrow intervals may be smaller than the marker.
              </p>
              <p className="reference-note">
                {ref.convention} <a href={ref.source}>Published reference ↗</a>
              </p>
              <details className="reference-details">
                <summary>All comparisons and original sandbox markers</summary>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Quantity</th>
                        <th>BHSM screen</th>
                        <th>Published reference</th>
                        <th>Archived sandbox marker</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((r) => {
                        const rr = references.comparisons.find(
                          (v) => v.id === r.id,
                        )!;
                        return (
                          <tr key={r.id}>
                            <th>{r.label}</th>
                            <td>{r.bhsm}</td>
                            <td>
                              {Number(rr.value.toPrecision(7))}
                              <br />
                              {rr.uncertainty_text}
                              <br />
                              <a href={rr.source}>{rr.label} ↗</a>
                            </td>
                            <td>
                              {r.reference}
                              <br />
                              Original supplied marker
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <p>
                  The September 2 snapshot remains unchanged. Published
                  references were checked September 7; editions, fit assumptions
                  and uncertainties are retained.
                </p>
                <a href={`${SCIENCE}/${comparison.source.path}`}>
                  Original sandbox record ↗
                </a>
              </details>
            </div>
          </article>
        );
      })}
      <p className="collection-source">
        <a href="./data/reference-data.json" download>
          Download published references and provenance
        </a>{' '}
        ·{' '}
        <a href="./data/sandbox-comparison.json" download>
          Original sandbox snapshot
        </a>
      </p>
    </section>
  );
}
