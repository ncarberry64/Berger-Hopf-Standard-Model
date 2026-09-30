'use client';
import { useState } from 'react';
import catalog from './science-collection.json';
import { SCIENCE } from './exhibits';
import { CollisionTheatre } from './collision-theatre';
import { MagneticLab } from './magnetic-lab';
import { MassStudy } from './mass-study';
import { MuonResult } from './muon-result';
import { ForceTree } from './force-tree';
import { ScienceConsole } from './science-console';
import { FamilyStudy } from './family-study';
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
          ['unification', '03', 'Forces'],
          ['predictions', '04', 'Matter'],
          ['magnetic', '05', 'Magnetism'],
          ['decays', '06', 'Collisions'],
          ['test', '09', 'Comparisons'],
        ].map(([id, n, name]) => (
          <a key={id} href={id === 'test' ? '#comparisons' : `#science-${id}`}>
            <b>{n}</b>
            {name}
          </a>
        ))}
      </nav>
      <ScienceConsole
        id="science-predictions"
        number="04"
        label="Matter from geometry"
        title="Three families in the BHSM framework."
        introAfter={2}
        intro="The repeating pattern is three particle families: each contains a charged lepton, a neutrino, an up-type quark and a down-type quark. The electric charges repeat across families, while the charged particles have different masses. Select a family to explore the pattern."
        accent="lavender"
      >
        <FamilyStudy motion={motion} />
        <MassStudy motion={motion} />
        <p className="console-caption">
          <b>Conditional BHSM structure</b> · The family selector shows the
          established charge pattern. The mass study pairs the displaced-energy
          picture with BHSM’s relative-energy definition; neither display
          assigns a measured particle to an arbitrary animated fiber.
        </p>
        <details className="console-details">
          <summary>
            Explore the science · historical ledger & conditional SM structure
          </summary>
          <div className="prototype-controls">
            <label htmlFor="prediction-sector">Ledger sector</label>
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
        id="science-magnetic"
        number="05"
        label="Magnetic moments in motion"
        title="The muon: from charge to magnetic response."
        intro="Explore conventional measured moments for four spin-½ particles. Watch their precession in a shared demonstration field, then inspect the values and conventions below."
        accent="lavender"
      >
        <MagneticLab motion={motion} />
        <MuonResult />
        <Outputs exhibit="magnetic" />
      </ScienceConsole>
      <ScienceConsole
        id="science-decays"
        number="06"
        label="Collision theatre"
        title="Energy in. New particles out."
        intro="Watch a collision unfold. Click the chamber to freeze the tracks and discover what came out."
        accent="cyan"
      >
        <CollisionTheatre motion={motion} />
        <Outputs exhibit="decays" />
      </ScienceConsole>
    </section>
  );
}
export function UnificationConsole({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (value: boolean) => void;
}) {
  return (
    <ScienceConsole
      id="science-unification"
      number="03"
      label="Forces · one geometric origin"
      title="One geometry. Four interaction regimes."
      intro="Explore four interactions and the geometric origin proposed by BHSM. Five studies connect known reference mechanisms and mathematical geometry to the proposed interpretation."
      accent="amber"
    >
      <ForceTree motion={motion} setMotion={setMotion} />
      <Outputs exhibit="forces" />
    </ScienceConsole>
  );
}
