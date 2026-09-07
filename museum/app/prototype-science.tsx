'use client';
import { useState } from 'react';
import catalog from './science-collection.json';
import { SCIENCE } from './exhibits';
import { CollisionTheatre } from './collision-theatre';
import { MagneticLab } from './magnetic-lab';
import { ForceTree } from './force-tree';
import { GeometryField, ScienceConsole } from './science-console';
type Result = {
  classification: string;
  value: number | number[];
  units: string;
  uncertainty_note: string;
  action_version: string;
  domain: string;
};
type Output = {
  id: string;
  exhibit: string;
  particle?: string;
  observable?: string;
  label: string;
  source_path: string;
  source_pointer: string;
  result: Result;
};
const approved = catalog.approved_outputs as Output[];
function value(v: number | number[] | boolean) {
  return Array.isArray(v)
    ? v
        .map((x) =>
          Array.isArray(x)
            ? x.map((y) => Number(y).toPrecision(5)).join(' · ')
            : Number(x).toPrecision(5),
        )
        .join(' / ')
    : typeof v === 'boolean'
      ? String(v)
      : Number(v).toPrecision(6);
}
function Outputs({
  exhibit,
  particle,
}: {
  exhibit: string;
  particle?: string;
}) {
  const rows = approved.filter(
    (r) => r.exhibit === exhibit && (!particle || r.particle === particle),
  );
  return rows.length ? (
    <div className="approved-outputs">
      {rows.map((r) => (
        <p key={r.id}>
          <strong>
            {r.label}: {value(r.result.value)} {r.result.units}
          </strong>
          <br />
          {r.result.classification} · {r.result.uncertainty_note}
          <br />
          <a href={`${SCIENCE}/${r.source_path}`}>Derived source ↗</a> ·{' '}
          {r.result.action_version} · {r.result.domain}
        </p>
      ))}
    </div>
  ) : null;
}

const generations = [
  {
    name: 'First family',
    lepton: 'e⁻',
    neutrino: 'νe',
    up: 'u',
    down: 'd',
    meaning:
      'The electron and the up and down quarks are the building blocks of ordinary atoms.',
  },
  {
    name: 'Second family',
    lepton: 'μ⁻',
    neutrino: 'νμ',
    up: 'c',
    down: 's',
    meaning:
      'Muon, charm and strange: a second family repeats the charge pattern with heavier charged particles.',
  },
  {
    name: 'Third family',
    lepton: 'τ⁻',
    neutrino: 'ντ',
    up: 't',
    down: 'b',
    meaning:
      'Tau, top and bottom complete the three-family pattern that BHSM seeks to explain.',
  },
];
export function PrototypeScience({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (b: boolean) => void;
}) {
  const [family, setFamily] = useState(0);
  const [sector, setSector] = useState('all');
  const rows = catalog.prediction_ledger.filter(
    (r) => sector === 'all' || r.sector === sector,
  );
  const bundle = catalog.sm_bundle;
  const selected = generations[family];
  return (
    <section
      id="exhibits"
      className="console-collection"
      aria-labelledby="prototype-title"
    >
      <div className="collection-heading">
        <div>
          <p className="eyebrow">Step inside the science</p>
          <h2 id="prototype-title">Nature, through a different lens.</h2>
        </div>
        <button onClick={() => setMotion(!motion)} aria-pressed={!motion}>
          {motion ? 'Ⅱ Pause all' : '▶ Animate exhibits'}
        </button>
      </div>
      <nav className="console-index" aria-label="Science exhibits">
        {[
          ['predictions', '01', 'Matter'],
          ['decays', '02', 'Collisions'],
          ['magnetic', '03', 'Magnetism'],
          ['test', '04', 'Predictions'],
          ['unification', '05', 'Forces'],
        ].map(([id, n, name]) => (
          <a key={id} href={id === 'test' ? '#comparisons' : `#science-${id}`}>
            <b>{n}</b>
            {name}
          </a>
        ))}
      </nav>
      <ScienceConsole
        id="science-predictions"
        number="01"
        label="Matter from geometry"
        title="One geometry. Three families."
        intro="Nature repeats a pattern. BHSM asks whether the repetition comes from different modes of a shared internal geometry."
        accent="lavender"
      >
        <div className="matter-scene">
          <GeometryField motion={motion} family={family} />
          <div className="matter-family" key={family}>
            <p className="eyebrow">{selected.name}</p>
            <div className="particle-quartet">
              {[
                [selected.lepton, 'Charged lepton'],
                [selected.neutrino, 'Neutrino'],
                [selected.up, 'Up-type quark'],
                [selected.down, 'Down-type quark'],
              ].map(([symbol, label]) => (
                <div key={label}>
                  <strong>{symbol}</strong>
                  <span>{label}</span>
                </div>
              ))}
            </div>
            <p>{selected.meaning}</p>
          </div>
        </div>
        <div className="console-selector">
          {generations.map((g, i) => (
            <button
              key={g.name}
              aria-pressed={family === i}
              onClick={() => setFamily(i)}
            >
              {g.name}
            </button>
          ))}
        </div>
        <p className="console-caption">
          <b>Conditional BHSM structure</b> · Mathematical geometry animation;
          particle symbols are a schematic family map.
        </p>
        <details className="console-details">
          <summary>
            Explore the science · Standard Model predictions & equivalence
          </summary>
          <div className="prototype-controls">
            <label htmlFor="prediction-sector">Prediction family</label>
            <select
              id="prediction-sector"
              value={sector}
              onChange={(e) => setSector(e.target.value)}
            >
              <option value="all">
                All {catalog.prediction_ledger.length} entries
              </option>
              {Array.from(
                new Set(catalog.prediction_ledger.map((r) => r.sector)),
              ).map((s) => (
                <option key={s} value={s}>
                  {s.replaceAll('_', ' ')}
                </option>
              ))}
            </select>
          </div>
          <details className="reference-details">
            <summary>Explore all 34 retained BHSM ledger entries</summary>
            <div className="table-scroll">
              <table>
                <caption>
                  BHSM ledger values, with their original authority
                </caption>
                <thead>
                  <tr>
                    <th>Quantity</th>
                    <th>BHSM value</th>
                    <th>Classification</th>
                    <th>Limits / conventions</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.id}>
                      <th>{r.quantity}</th>
                      <td className="numeric-ledger">
                        {value(r.predicted as number)}
                      </td>
                      <td>{r.status.replaceAll('_', ' ')}</td>
                      <td>{r.limitations.join(' ')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
          <Outputs exhibit="predictions" />
          <p>
            Names such as “predicted” in a historical source do not override its
            SCREEN or PROXY classification. Effective neutrino entries extend
            the minimal Standard Model. Physical mass spectra, rates and moment
            predictions remain open where no promoted record exists.
          </p>
          <a href={`${SCIENCE}/theory/bhsm_prediction_ledger.json`}>
            Full ledger, reference values and source conventions ↗
          </a>{' '}
          ·{' '}
          <a href="./data/science-collection.json" download>
            Download the source-bound collection
          </a>
          <div id="science-equivalence" className="sm-equivalence">
            <h4>Standard Model equivalence</h4>
            <h3>
              Recovering the same particles is one part of recovering the same
              physics.
            </h3>
            <p>
              <strong>In plain language.</strong> Matching the particle labels
              and cancelling mathematical inconsistencies are substantial
              structural checks. Full equivalence also requires the right
              interactions, normalization and observable behavior.
            </p>
            <p className="data-label">
              Retained conditional SM-bundle result · full physical equivalence
              remains open
            </p>
            <div className="equivalence-columns">
              <div>
                <h4>Retained representation ledger</h4>
                <table>
                  <caption>
                    {bundle.chiral_bundle.families} families ·{' '}
                    {bundle.chiral_bundle.faithful_gauge_group}
                  </caption>
                  <thead>
                    <tr>
                      <th>Multiplet</th>
                      <th>Representation</th>
                      <th>Hypercharge</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bundle.chiral_bundle.multiplets.map((r) => (
                      <tr key={r.name}>
                        <th>{r.name}</th>
                        <td>{r.representation}</td>
                        <td>{r.Y}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p>
                  The neutral singlet belongs to the stated extension; anomaly
                  cancellation does not determine its mass.
                </p>
              </div>
              <div>
                <h4>Equivalence checks</h4>
                {Object.entries(bundle.validation)
                  .filter(([k]) => k !== 'USB_untouched')
                  .map(([k, v]) => (
                    <p className="equivalence-check" key={k}>
                      <span>{v ? '✓ Retained check' : 'Open'}</span>
                      {k.replaceAll('_', ' ')}
                    </p>
                  ))}
                <p className="pending-output">
                  Physical masses and mixing, renormalized gauge couplings and
                  the complete effective reduction remain open in this source.
                </p>
              </div>
            </div>
            <a
              href={`${SCIENCE}/artifacts/BHSM_aether_hybrid_standard_model_bundle_v15_53.json`}
            >
              Representation and anomaly evidence ↗
            </a>{' '}
            ·{' '}
            <a href={`${SCIENCE}/docs/bhsm_effective_standard_model_v11_0.md`}>
              Full effective-SM equivalence requirements ↗
            </a>
          </div>
        </details>
      </ScienceConsole>
      <ScienceConsole
        id="science-decays"
        number="02"
        label="Collision theatre"
        title="Energy in. New particles out."
        intro="Watch a collision unfold. Click the chamber to freeze the tracks and discover what came out."
        accent="cyan"
      >
        <CollisionTheatre motion={motion} />
        <Outputs exhibit="decays" />
      </ScienceConsole>
      <ScienceConsole
        id="science-magnetic"
        number="03"
        label="Magnetic moments in motion"
        title="Every particle has a magnetic fingerprint."
        intro="Four particles, four measured magnetic moments. Watch each moment precess and see how its direction relates to the particle’s spin."
        accent="lavender"
      >
        <MagneticLab motion={motion} />
        <Outputs exhibit="magnetic" />
      </ScienceConsole>
    </section>
  );
}
export function UnificationConsole({ motion }: { motion: boolean }) {
  return (
    <ScienceConsole
      id="science-unification"
      number="05"
      label="Forces unifying"
      title="Different forces. A shared origin?"
      intro="Follow Norman’s proposed connections: gravity branches from electromagnetism, electromagnetism from weak, then through strong to the luminous aether core."
      accent="amber"
    >
      <ForceTree motion={motion} />
      <Outputs exhibit="forces" />
    </ScienceConsole>
  );
}
