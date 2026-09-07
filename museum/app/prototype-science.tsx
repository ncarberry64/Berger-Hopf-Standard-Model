'use client';
import { useState } from 'react';
import Image from 'next/image';
import catalog from './science-collection.json';
import { exhibits, SCIENCE } from './exhibits';
import { CollisionTheatre } from './collision-theatre';
import { MagneticLab } from './magnetic-lab';
import { ForceTree } from './force-tree';
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
const sections = [
  ['decays', 'Collision theatre'],
  ['magnetic', 'Magnetic moments in motion'],
  ['predictions', 'SM predictions & equivalence'],
  ['unification', 'Forces unifying'],
  ['action', 'Geometry to observables'],
  ['spectral', 'Spectral forecasts'],
];
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
  ) : (
    <p className="pending-output">
      BHSM physical outputs: awaiting reviewed derivation. Missing values are
      not zero.
    </p>
  );
}
function PrototypeImage({
  number,
  motion,
}: {
  number: string;
  motion: boolean;
}) {
  const row = exhibits.find((e) => e.number === number)!;
  const desired = motion ? row.animated : row.still;
  const [failed, setFailed] = useState('');
  return (
    <figure className="prototype-image">
      <Image
        src={`./exhibits/${failed === desired ? row.still : desired}`}
        width={1600}
        height={900}
        alt={row.alt}
        loading="lazy"
        unoptimized
        onError={() => setFailed(desired)}
      />
      <figcaption>{row.dataLabel}</figcaption>
    </figure>
  );
}

export function PrototypeScience({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (b: boolean) => void;
}) {
  const [sector, setSector] = useState('all');
  const rows = catalog.prediction_ledger.filter(
    (r) => sector === 'all' || r.sector === sector,
  );
  const bundle = catalog.sm_bundle;
  return (
    <section
      id="exhibits"
      className="prototype-hall"
      aria-labelledby="prototype-title"
    >
      <div className="section-heading">
        <p className="eyebrow">Explore BHSM</p>
        <h2 id="prototype-title">Matter, motion and a common origin.</h2>
        <p>
          Follow a collision, move a magnetic field, and explore what a
          geometric account of particle physics must explain.
        </p>
        <button onClick={() => setMotion(!motion)} aria-pressed={!motion}>
          {motion ? 'Pause exhibit animations' : 'Enable exhibit animations'}
        </button>
      </div>
      <nav className="science-index" aria-label="Science exhibits">
        {sections.map(([id, title], i) => (
          <a href={`#science-${id}`} key={id}>
            <span>{String(i + 1).padStart(2, '0')}</span>
            {title}
          </a>
        ))}
      </nav>
      <article id="science-decays" className="primary-exhibit">
        <p className="eyebrow">01 · Collision theatre</p>
        <h3>Read the traces particles leave behind.</h3>
        <p>
          Charged particles bend in a magnetic field. Their energy, momentum and
          charge help us work backward from the outgoing tracks to the
          interaction.
        </p>
        <CollisionTheatre motion={motion} />
        <Outputs exhibit="decays" />
      </article>
      <article id="science-magnetic" className="primary-exhibit">
        <p className="eyebrow">02 · Magnetic moments in motion</p>
        <h3>Bring a magnet close. Watch the spin respond.</h3>
        <MagneticLab motion={motion} />
        <Outputs exhibit="magnetic" />
      </article>
      <article id="science-predictions" className="primary-exhibit">
        <p className="eyebrow">03 · Standard Model predictions & equivalence</p>
        <h3>One particle model. Many measurable tests.</h3>
        <p>
          <strong>In plain language.</strong> A theory has to account for
          masses, mixing and interaction strengths together. Every retained
          ledger entry is available here, including imperfect screens, proxy
          audits and the neutrino extension.
        </p>
        <p className="data-label">
          Actual retained BHSM calculations · historical screens / conditional
          results · not measurements or newly derived physical predictions
        </p>
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
          SCREEN or PROXY classification. Effective neutrino entries extend the
          minimal Standard Model. Physical mass spectra, rates and moment
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
            <strong>In plain language.</strong> Matching the particle labels and
            cancelling mathematical inconsistencies are substantial structural
            checks. Full equivalence also requires the right interactions,
            normalization and observable behavior.
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
                Physical masses and mixing, renormalized gauge couplings and the
                complete effective reduction remain open in this source.
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
      </article>

      <article id="science-unification" className="primary-exhibit">
        <p className="eyebrow">04 · Forces unifying</p>
        <h3>Follow the branches toward the core.</h3>
        <p>
          In Norman’s picture, gravity branches from electromagnetism,
          electromagnetism from the weak interaction, and the connections lead
          through strong interaction to a shared aether core.
        </p>
        <ForceTree motion={motion} />
        <Outputs exhibit="forces" />
      </article>
      {[
        ['action', '02', 'Geometry to observables'],
        ['spectral', '04', 'Spectral forecasts'],
      ].map(([id, number, title], index) => {
        const row = exhibits.find((r) => r.number === number)!;
        return (
          <article id={`science-${id}`} className="primary-exhibit" key={id}>
            <p className="eyebrow">
              {String(index + 5).padStart(2, '0')} · BHSM science
            </p>
            <h3>{title}</h3>
            <p>
              <strong>In plain language.</strong> {row.lay}
            </p>
            <PrototypeImage number={number} motion={motion} />
            <p>{row.matters}</p>
            <div className="record-links">
              {row.links.map((l) => (
                <a key={l.href} href={l.href}>
                  {l.label} ↗
                </a>
              ))}
            </div>
          </article>
        );
      })}
    </section>
  );
}
