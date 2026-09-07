'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline SVG needs image semantics; an HTML img cannot contain this interactive drawing. */
import { useState } from 'react';
import comparison from './sandbox-comparison.json';
import references from './reference-data.json';
import { SCIENCE } from './exhibits';
import { ScienceConsole, useSceneClock } from './science-console';
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

export function ScienceGallery({ motion }: { motion: boolean }) {
  const [baseIndex, setIndex] = useState(0),
    [playing, setPlaying] = useState(true);
  const { ref: stageRef, time } = useSceneClock(motion && playing);
  const [started, setStarted] = useState(0);
  const elapsed = (time - started) % 9;
  const index =
    (baseIndex + Math.floor((time - started) / 9)) % comparison.rows.length;
  const chosen = comparison.rows[index];
  const gallery = galleries.find((g) => g.id === chosen.group)!;
  const ref = references.comparisons.find((r) => r.id === chosen.id)!;
  const residual = (100 * (chosen.bhsm - ref.value)) / ref.value;
  const reveal =
    !motion || !playing ? 1 : Math.min(1, Math.max(0, (elapsed - 1.5) / 2));
  const x = (n: number) => 450 + 17 * n;
  const select = (i: number) => {
    setIndex(i);
    setStarted(time);
    setPlaying(false);
  };
  return (
    <section
      id="comparisons"
      className="console-collection"
      aria-label="BHSM comparisons with published reference data"
    >
      <ScienceConsole
        id="science-test"
        number="04"
        label="The prediction test"
        title="Ask the model. Then ask nature."
        intro="An explanation earns its place by facing a measurement. Watch a retained BHSM calculation meet its published reference—including the differences."
        accent="cyan"
      >
        <div className="console-selector">
          <label htmlFor="prediction-quantity">Choose a test</label>
          <select
            id="prediction-quantity"
            value={index}
            onChange={(e) => select(+e.target.value)}
          >
            {comparison.rows.map((r, i) => (
              <option key={r.id} value={i}>
                {r.label}
              </option>
            ))}
          </select>
          <button onClick={() => setPlaying(!playing)} disabled={!motion}>
            {playing && motion ? 'Ⅱ Pause sequence' : '▶ Cycle tests'}
          </button>
        </div>
        <div ref={stageRef} className="prediction-stage">
          <div className="prediction-heading">
            <span>{gallery.subtitle}</span>
            <h4>{chosen.label}</h4>
            <p>{chosen.explanation}</p>
          </div>
          <div className="comparison-pair">
            <div>
              <span>Historical BHSM calculation</span>
              <strong>{chosen.bhsm}</strong>
              <small>{chosen.unit}</small>
            </div>
            <div
              className="reference-value"
              style={{ opacity: 0.2 + reveal * 0.8 }}
            >
              <span>Published reference</span>
              <strong>{Number(ref.value.toPrecision(7))}</strong>
              <small>{ref.uncertainty_text}</small>
            </div>
          </div>
          <svg
            viewBox="0 0 900 210"
            role="img"
            aria-label={`${chosen.label}: ${residual.toFixed(3)} percent relative difference from reference`}
          >
            <defs>
              <linearGradient id="comparison-beam">
                <stop stopColor="#71e5eb" />
                <stop offset="1" stopColor="#ffbc77" />
              </linearGradient>
            </defs>
            {[-20, -10, 0, 10, 20].map((v) => (
              <g key={v}>
                <line
                  x1={x(v)}
                  x2={x(v)}
                  y1="30"
                  y2="140"
                  stroke={v === 0 ? '#ffbc77' : '#292736'}
                  strokeDasharray={v === 0 ? undefined : '3 7'}
                />
                <text
                  x={x(v)}
                  y="175"
                  textAnchor="middle"
                  fill="#aaa4ba"
                  fontSize="17"
                >
                  {v > 0 ? '+' : ''}
                  {v}%
                </text>
              </g>
            ))}
            <line x1="110" x2="790" y1="85" y2="85" stroke="#393243" />
            <line
              x1={x(residual)}
              x2={x(residual * (1 - reveal))}
              y1="85"
              y2="85"
              stroke="url(#comparison-beam)"
              strokeWidth="12"
              opacity=".2"
            />
            {ref.lower !== null && ref.upper !== null && (
              <line
                x1={x((100 * (ref.lower - ref.value)) / ref.value)}
                x2={x((100 * (ref.upper - ref.value)) / ref.value)}
                y1="85"
                y2="85"
                stroke="#ffbc77"
                strokeWidth="10"
                opacity={reveal}
              />
            )}
            <circle cx={x(residual)} cy="85" r="9" fill="#71e5eb" />
            <circle
              cx={x(residual)}
              cy="85"
              r="20"
              fill="none"
              stroke="#71e5eb"
              opacity=".3"
            />
            <path
              d={`M${x(residual * (1 - reveal))} 68l10 17-10 17-10-17Z`}
              fill="#ffbc77"
              opacity={reveal}
            />
            <text
              x="450"
              y="205"
              fill="#aaa4ba"
              textAnchor="middle"
              fontSize="14"
            >
              Relative difference · cyan: BHSM screen / amber: published
              reference
            </text>
          </svg>
          <div className="prediction-verdict">
            <strong>
              {residual >= 0 ? '+' : ''}
              {residual.toFixed(3)}%
            </strong>
            <p>
              Difference from the reference
              <br />
              <span>{ref.label}</span>
            </p>
          </div>
        </div>
        <p className="console-caption">
          <b>COMPARISON ONLY</b> · Historical BHSM screen + published reference.
          Marker motion reveals the comparison; it is not a live derivation or
          statistical significance.
        </p>
        <details className="console-details">
          <summary>Explore the science · all ten comparisons</summary>
          <p>{gallery.lay}</p>
          <p>{gallery.meaning}</p>
          <p>
            {ref.convention} <a href={ref.source}>Published reference ↗</a>
          </p>
          <p>
            Reference intervals retain the published uncertainty; very narrow
            intervals can be smaller than the marker. The θ23 tension and Higgs
            difference remain visible.
          </p>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Quantity</th>
                  <th>BHSM screen</th>
                  <th>Published reference</th>
                  <th>Original sandbox marker</th>
                </tr>
              </thead>
              <tbody>
                {comparison.rows.map((r) => {
                  const rr = references.comparisons.find((v) => v.id === r.id)!;
                  return (
                    <tr key={r.id}>
                      <th>{r.label}</th>
                      <td>{r.bhsm}</td>
                      <td>
                        {Number(rr.value.toPrecision(7))} {rr.uncertainty_text}
                        <br />
                        <a href={rr.source}>{rr.label} ↗</a>
                      </td>
                      <td>{r.reference}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <a href={`${SCIENCE}/${comparison.source.path}`}>
            Frozen sandbox source ↗
          </a>{' '}
          ·{' '}
          <a href="./data/reference-data.json" download>
            Reference data
          </a>
        </details>
      </ScienceConsole>
    </section>
  );
}
