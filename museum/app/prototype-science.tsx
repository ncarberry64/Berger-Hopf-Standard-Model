'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import catalog from './science-collection.json';
import { exhibits, SCIENCE } from './exhibits';
import { collisionDemo } from '../lib/collision-demo';

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
const particles = catalog.particles;
const sections = [
  ['decays', 'Particle decays & collisions'],
  ['magnetic', 'Full magnetic-moment tracker'],
  ['predictions', 'Standard Model predictions'],
  ['equivalence', 'Standard Model equivalence'],
  ['unification', 'Forces unifying'],
  ['action', 'Geometry to observables'],
  ['spectral', 'Spectral forecasts'],
];
const charge: Record<string, number> = {
  electron: -1,
  muon: -1,
  tau: -1,
  up: 2 / 3,
  charm: 2 / 3,
  top: 2 / 3,
  down: -1 / 3,
  strange: -1 / 3,
  bottom: -1 / 3,
  W: 1,
  proton: 1,
};
const definitions: Record<string, string> = {
  'charged-lepton':
    'The charged-lepton projection separates F₁ and F₂. After the physical gates close, a = F₂(0), g = 2(1 + a), and the physical mass and unit convention determine μ.',
  'neutral-mode':
    'Neutral modes require a specified mass, state identity and diagonal or transition-moment definition. The charged-lepton g−2 formula is not automatically applicable.',
  'confined-mode':
    'A quark is not an isolated asymptotic particle. A magnetic observable needs an explicit scheme and a hadronic or other physical observable map.',
  composite:
    'Proton and neutron moments require the composite-state electromagnetic current and a physical nuclear-magneton convention. A lepton projection alone is insufficient.',
  'boson-specific':
    'A vector or massless gauge field requires its own electromagnetic form-factor definition. Lepton g−2 is not a universal moment formula.',
  'spin-zero':
    'A spin-zero state has no spin magnetic dipole. Other electromagnetic response observables require their own definition; this is not a missing g−2 number.',
};
const channelText: Record<string, string> = {
  allowed:
    'An action-derived amplitude and open phase space would supply a partial width. A nonzero kinematic opening alone does not prove an interaction exists.',
  forbidden:
    'A demonstrated selection rule would exclude the channel. An uncomputed amplitude must not be relabeled forbidden.',
  closed:
    'There is insufficient parent mass or collision energy for the specified final state. This is a kinematic statement.',
  unresolved:
    'The required state, amplitude or classification is missing. This is the current default for an unpromoted physical channel.',
};
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
function ParticleSelect({
  id,
  selected,
  onChange,
  disabled = false,
}: {
  disabled?: boolean;
  id: string;
  selected: string;
  onChange: (s: string) => void;
}) {
  return (
    <select
      disabled={disabled}
      id={id}
      value={selected}
      onChange={(e) => onChange(e.target.value)}
    >
      {particles.map((p) => (
        <option value={p.id} key={p.id}>
          {p.name}
        </option>
      ))}
    </select>
  );
}

function Collider({ onInspect }: { onInspect: (s: string) => void }) {
  const [ids, setIds] = useState(['electron', 'electron', 'muon', 'muon']);
  const [channelMode, setChannelMode] = useState('elastic');
  const elastic = channelMode === 'elastic';
  const [anti, setAnti] = useState([false, true, false, true]);
  const [masses, setMasses] = useState([1, 1, 1, 1]);
  const [energy, setEnergy] = useState(6),
    [angle, setAngle] = useState(55);
  const [run, setRun] = useState<{
    result: ReturnType<typeof collisionDemo>;
    labels: string[];
    ids: string[];
    angle: number;
  } | null>(null);
  const [frame, setFrame] = useState(0),
    [playing, setPlaying] = useState(false);
  const [demoError, setDemoError] = useState('');
  useEffect(() => {
    if (!playing) return;
    const timer = setInterval(
      () =>
        setFrame((f) => {
          if (f >= 100) {
            setPlaying(false);
            return 100;
          }
          return f + 2;
        }),
      35,
    );
    return () => clearInterval(timer);
  }, [playing]);
  const reset = () => {
    setDemoError('');
    setRun(null);
    setPlaying(false);
    setFrame(0);
  };
  function collide() {
    if (!masses.every((m) => Number.isFinite(m) && m >= 0 && m <= 100)) {
      setDemoError('Use finite demonstration masses between 0 and 100.');
      return;
    }
    setDemoError('');
    const eventIds = elastic ? [ids[0], ids[1], ids[0], ids[1]] : ids;
    const eventAnti = elastic ? [anti[0], anti[1], anti[0], anti[1]] : anti;
    const eventMasses = elastic
      ? [masses[0], masses[1], masses[0], masses[1]]
      : masses;
    const q = eventIds.map(
      (id, i) => (charge[id] ?? 0) * (eventAnti[i] ? -1 : 1),
    );
    const actualMasses = eventIds.map((id, i) =>
      ['photon', 'gluon'].includes(id) ? 0 : eventMasses[i],
    );
    const result = collisionDemo(energy, actualMasses, angle, q);
    setRun({
      result,
      angle,
      ids: [...eventIds],
      labels: eventIds.map(
        (id, i) =>
          `${eventAnti[i] ? 'Conjugate ' : ''}${particles.find((p) => p.id === id)!.name}`,
      ),
    });
    const reduced = window.matchMedia(
      '(prefers-reduced-motion: reduce)',
    ).matches;
    setFrame(reduced ? 100 : 0);
    setPlaying(!reduced && result.status === 'kinematics-only');
  }
  const theta = ((run?.angle ?? angle) * Math.PI) / 180,
    f = frame / 100;
  return (
    <div className="collision-workbench">
      <h4>Select particles. Collide. Inspect the output.</h4>
      <p className="data-label">
        SIMULATED KINEMATICS · arbitrary units · no BHSM cross-section or
        branching probability
      </p>
      <p>
        Select the incoming particles and collide: the default elastic prototype
        returns those species in new directions. Switch modes to inspect a
        different candidate outgoing pair. The prototype checks charge balance
        and two-body phase space, then displays energy and momentum. It does not
        predict which channel nature chooses.
      </p>
      <label>
        Collision mode
        <select
          value={channelMode}
          onChange={(e) => {
            setChannelMode(e.target.value);
            reset();
          }}
        >
          <option value="elastic">Automatic elastic prototype</option>
          <option value="candidate">Inspect a selected outgoing channel</option>
        </select>
      </label>
      <div className="beam-grid">
        {['Incoming A', 'Incoming B', 'Outgoing A', 'Outgoing B'].map(
          (label, i) => (
            <div key={label}>
              <label htmlFor={`beam-${i}`}>{label}</label>
              <ParticleSelect
                id={`beam-${i}`}
                selected={ids[elastic && i >= 2 ? i - 2 : i]}
                disabled={elastic && i >= 2}
                onChange={(s) => {
                  setIds(ids.map((x, k) => (k === i ? s : x)));
                  reset();
                }}
              />
              <label className="conjugate">
                <input
                  type="checkbox"
                  checked={anti[elastic && i >= 2 ? i - 2 : i]}
                  disabled={elastic && i >= 2}
                  onChange={(e) => {
                    setAnti(
                      anti.map((x, k) => (k === i ? e.target.checked : x)),
                    );
                    reset();
                  }}
                />{' '}
                Conjugate / antiparticle channel
              </label>
            </div>
          ),
        )}
      </div>
      <div className="prototype-controls">
        <label>
          Collision energy √s: {energy.toFixed(1)} demo units
          <input
            type="range"
            min="0.5"
            max="20"
            step="0.1"
            value={energy}
            onChange={(e) => {
              setEnergy(+e.target.value);
              reset();
            }}
          />
        </label>
        <label>
          Outgoing angle: {angle}°
          <input
            type="range"
            min="5"
            max="175"
            value={angle}
            onChange={(e) => {
              setAngle(+e.target.value);
              reset();
            }}
          />
        </label>
      </div>
      <details>
        <summary>Demonstration mass settings</summary>
        <p>
          These are user-controlled rest-mass inputs, not a BHSM or measured
          particle spectrum. Defaults use equal unit masses; photon and gluon
          labels use zero. Neutral-mode conjugacy is a bookkeeping choice, not a
          Dirac/Majorana determination.
        </p>
        <div className="beam-grid">
          {masses.map((m, i) => (
            <label key={i}>
              Slot {i + 1} mass
              <input
                aria-label={`Slot ${i + 1} demonstration mass`}
                type="number"
                min="0"
                max="10"
                step="0.1"
                value={elastic && i >= 2 ? masses[i - 2] : m}
                disabled={
                  (elastic && i >= 2) || ['photon', 'gluon'].includes(ids[i])
                }
                onChange={(e) => {
                  setMasses(
                    masses.map((x, k) =>
                      k === i ? Math.max(0, Number(e.target.value)) : x,
                    ),
                  );
                  reset();
                }}
              />
            </label>
          ))}
        </div>
      </details>
      <button className="science-action" onClick={collide}>
        Collide selected particles
      </button>
      <div aria-live="polite">
        {demoError && <p>{demoError}</p>}
        {run && run.result.status !== 'kinematics-only' && (
          <p className="pending-output">
            {run.result.status === 'charge-blocked'
              ? 'No event generated: the selected channel fails charge conservation.'
              : 'No event generated: the selected energy is at or below a two-body threshold.'}
          </p>
        )}
      </div>
      {run?.result.status === 'kinematics-only' && (
        <>
          <div className="diagram-scroll">
            <svg
              className="collision-view"
              viewBox="0 0 800 360"
              role="img"
              aria-label="Illustrative collision with two incoming and two outgoing tracks"
            >
              <line
                x1="50"
                y1="180"
                x2="750"
                y2="180"
                stroke="#406078"
                strokeDasharray="8 8"
              />
              <path
                d={`M400 180 l${250 * Math.cos(theta)} ${-130 * Math.sin(theta)} M400 180 l${-250 * Math.cos(theta)} ${130 * Math.sin(theta)}`}
                stroke="#7cdfd2"
                fill="none"
                strokeDasharray="6 6"
              />
              <circle
                cx="400"
                cy="180"
                r={f > 0.4 && f < 0.6 ? 18 : 7}
                fill="#efc374"
              />
              {[0, 1].map((i) => {
                const sign = i ? 1 : -1;
                const x = 400 + sign * 310 * (1 - Math.min(1, f / 0.45));
                return (
                  f < 0.5 && (
                    <g key={i}>
                      <circle cx={x} cy="180" r="12" fill="#efc374" />
                      <text
                        x={i ? 750 : 50}
                        y="140"
                        textAnchor={i ? 'end' : 'start'}
                        fill="currentColor"
                      >
                        {run.labels[i]}
                      </text>
                    </g>
                  )
                );
              })}
              {[0, 1].map((i) => {
                const sign = i ? -1 : 1,
                  d = Math.max(0, (f - 0.5) / 0.5);
                return (
                  f >= 0.5 && (
                    <g key={i}>
                      <circle
                        cx={400 + sign * 250 * Math.cos(theta) * d}
                        cy={180 - sign * 130 * Math.sin(theta) * d}
                        r="12"
                        fill="#7cdfd2"
                      />
                      <text
                        x="400"
                        y={i ? 320 : 35}
                        textAnchor="middle"
                        fill="currentColor"
                      >
                        {run.labels[i + 2]}
                      </text>
                    </g>
                  )
                );
              })}
              <text x="400" y="350" textAnchor="middle" fill="currentColor">
                Illustrative trajectories · not detector data
              </text>
            </svg>
          </div>
          <div className="prototype-controls">
            <button
              onClick={() => {
                setFrame(0);
                setPlaying(true);
              }}
            >
              Replay
            </button>
            <button onClick={() => setPlaying(!playing)}>
              {playing ? 'Pause' : 'Play'}
            </button>
            <label>
              Event frame
              <input
                type="range"
                min="0"
                max="100"
                value={frame}
                onChange={(e) => {
                  setPlaying(false);
                  setFrame(+e.target.value);
                }}
              />
            </label>
          </div>
          <p className="data-label">
            KINEMATICALLY OPEN · dynamical amplitude and physical rate
            uncomputed
          </p>
          <div className="table-scroll">
            <table>
              <caption>
                Generated prototype output · E and momentum in demo units
              </caption>
              <thead>
                <tr>
                  <th>State</th>
                  <th>E</th>
                  <th>pₓ</th>
                  <th>pᵧ</th>
                  <th>p_z</th>
                  <th>Decay follow-up</th>
                </tr>
              </thead>
              <tbody>
                {[...run.result.incoming, ...run.result.outgoing].map(
                  (v, i) => (
                    <tr key={i}>
                      <th>
                        {i < 2 ? 'In' : 'Out'} · {run.labels[i]}
                      </th>
                      {[v.E, v.px, v.py, v.pz].map((n, j) => (
                        <td key={j}>{n.toFixed(4)}</td>
                      ))}
                      <td>
                        {i >= 2 ? (
                          <button onClick={() => onInspect(run.ids[i])}>
                            Inspect decay record
                          </button>
                        ) : (
                          '—'
                        )}
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
          <p>
            Energy–momentum balance residual:{' '}
            {run.result.residual!.toExponential(2)}. Physical channel
            probabilities and subsequent decays await the action-derived
            amplitudes.
          </p>
        </>
      )}
    </div>
  );
}

export function PrototypeScience({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (b: boolean) => void;
}) {
  const [particle, setParticle] = useState('muon'),
    [channel, setChannel] = useState('unresolved');
  const [magnetic, setMagnetic] = useState('muon'),
    [sector, setSector] = useState('all');
  const [forceFrame, setForceFrame] = useState(0),
    [forcePlaying, setForcePlaying] = useState(true);
  useEffect(() => {
    if (!forcePlaying || !motion) return;
    const timer = setInterval(() => setForceFrame((f) => (f + 1) % 101), 70);
    return () => clearInterval(timer);
  }, [forcePlaying, motion]);
  const selected = particles.find((p) => p.id === magnetic)!;
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
        <p className="eyebrow">The permanent BHSM science collection</p>
        <h2 id="prototype-title">
          From geometric structure to physical predictions.
        </h2>
        <p>
          Explore the full particle and interaction program. The prototype
          exhibits stay here as BHSM develops; reviewed derived data will fill
          their pending outputs. The sandbox comparisons below are additional
          evidence views.
        </p>
        <p className="data-label">
          Living research collection · schematic simulations, retained results
          and derived outputs are labeled separately
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
        <p className="eyebrow">01 · Particle decays and collisions</p>
        <h3>What can a particle become?</h3>
        <p>
          <strong>In plain language.</strong> Particles may scatter into new
          directions or transform into other particles. BHSM must supply the
          states, permitted channels and probabilities from the same physical
          action.
        </p>
        <Collider
          onInspect={(id) => {
            setParticle(id);
            document
              .getElementById('decay-record')
              ?.scrollIntoView({ behavior: 'auto', block: 'center' });
          }}
        />
        <div id="decay-record" className="prototype-controls">
          <label htmlFor="decay-particle">Particle decay record</label>
          <ParticleSelect
            id="decay-particle"
            selected={particle}
            onChange={setParticle}
          />
          <label htmlFor="channel-state">
            Explore a channel classification
          </label>
          <select
            id="channel-state"
            value={channel}
            onChange={(e) => setChannel(e.target.value)}
          >
            {Object.keys(channelText).map((k) => (
              <option key={k}>{k}</option>
            ))}
          </select>
        </div>
        <p>{channelText[channel]}</p>
        <p className="data-label">
          Classification demonstration · this selection does not classify{' '}
          {particles.find((p) => p.id === particle)!.name} as stable or unstable
        </p>
        <Outputs exhibit="decays" particle={particle} />
        <div className="table-scroll">
          <table>
            <caption>Full decay readout contract</caption>
            <thead>
              <tr>
                <th>Output</th>
                <th>Existing calculation path</th>
                <th>Physical result</th>
              </tr>
            </thead>
            <tbody>
              {[
                [
                  'Partial widths',
                  'Two-, three- and general multi-body phase space',
                ],
                ['Total width', 'Sum over the complete channel inventory'],
                ['Lifetime', 'Inverse width, followed by fixed physical units'],
                [
                  'Branching fractions',
                  'Each partial width divided by total width',
                ],
                [
                  'Stability / exclusions',
                  'Action-owned selection rules and channel closure',
                ],
              ].map(([a, b]) => (
                <tr key={a}>
                  <th>{a}</th>
                  <td>{b}</td>
                  <td>
                    {approved.some(
                      (r) =>
                        r.exhibit === 'decays' &&
                        r.particle === particle &&
                        r.label === a,
                    )
                      ? 'See reviewed result above'
                      : 'Awaiting reviewed particle-level result'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <PrototypeImage number="07" motion={motion} />
        <a href={`${SCIENCE}/src/bhsm/interface/universal_decay_collision.py`}>
          Decay and collision calculation source ↗
        </a>
      </article>
      <article id="science-magnetic" className="primary-exhibit">
        <p className="eyebrow">02 · Full magnetic-moment tracker</p>
        <h3>How does each state respond to a magnetic field?</h3>
        <p>
          <strong>In plain language.</strong> Magnetic moments probe how a
          particle’s spin and electromagnetic interactions fit together. This
          tracker covers all listed SM particle families and proton/neutron
          benchmarks, with a separate definition requirement for each kind of
          state.
        </p>
        <div className="prototype-controls">
          <label htmlFor="magnetic-particle">Inspect a state</label>
          <ParticleSelect
            id="magnetic-particle"
            selected={magnetic}
            onChange={setMagnetic}
          />
        </div>
        <p>{definitions[selected.moment_basis]}</p>
        <Outputs exhibit="magnetic" particle={magnetic} />
        <div className="table-scroll">
          <table>
            <caption>All-state magnetic tracker · pending is not zero</caption>
            <thead>
              <tr>
                <th>State</th>
                <th>Definition</th>
                <th>g</th>
                <th>Anomaly a</th>
                <th>Moment μ / form factors</th>
              </tr>
            </thead>
            <tbody>
              {particles.map((p) => (
                <tr key={p.id}>
                  <th>
                    <button onClick={() => setMagnetic(p.id)}>{p.name}</button>
                  </th>
                  <td>{p.moment_basis.replaceAll('-', ' ')}</td>
                  {['g', 'a', 'mu'].map((k) => {
                    const row = approved.find(
                      (r) =>
                        r.exhibit === 'magnetic' &&
                        r.particle === p.id &&
                        r.observable === k,
                    );
                    return (
                      <td key={k}>
                        {row
                          ? `${value(row.result.value)} ${row.result.units}`
                          : p.moment_basis === 'spin-zero'
                            ? 'Not a spin-dipole observable'
                            : p.moment_basis !== 'charged-lepton'
                              ? 'Definition / derivation pending'
                              : 'Derivation pending'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="data-label">
          No physical magnetic-moment numbers are fabricated. Particle/conjugate
          relations and transition moments require explicit source records.
        </p>
        <PrototypeImage number="05" motion={motion} />
        <a
          href={`${SCIENCE}/src/bhsm/interface/universal_precision_form_factor.py`}
        >
          Electromagnetic form-factor and lepton promotion gates ↗
        </a>
      </article>
      <article id="science-predictions" className="primary-exhibit">
        <p className="eyebrow">03 · Standard Model predictions</p>
        <h3>The complete retained prediction ledger.</h3>
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
        <div className="table-scroll">
          <table>
            <caption>BHSM ledger values, with their original authority</caption>
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
      </article>
      <article id="science-equivalence" className="primary-exhibit">
        <p className="eyebrow">04 · Standard Model equivalence</p>
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
      </article>
      <article id="science-unification" className="primary-exhibit">
        <p className="eyebrow">05 · Forces unifying</p>
        <h3>Different interactions. A proposed common origin.</h3>
        <p>
          <strong>In plain language.</strong> Watch electromagnetic, weak,
          strong and gravitational descriptions come together in the proposed
          geometric action. This illustrates BHSM’s ambition; it is not a
          measured running-coupling plot or a proof of quantum-gravity
          unification.
        </p>
        <p className="data-label">
          ANIMATED CONCEPTUAL MODEL · no physical energy axis, meeting scale or
          coupling equality is claimed
        </p>
        <div className="diagram-scroll">
          <svg
            className="force-view"
            viewBox="0 0 900 400"
            role="img"
            aria-label="Four labeled interactions converge toward a shared geometric-action node as the conceptual animation progresses"
          >
            {['Electromagnetic', 'Weak', 'Strong', 'Gravity'].map((name, i) => {
              const y = 55 + i * 95,
                t = forceFrame / 100,
                x = 270 + 360 * t,
                cy = y + (200 - y) * t;
              return (
                <g key={name}>
                  <path
                    d={`M260 ${y} C420 ${y} 470 200 650 200`}
                    stroke={['#efc374', '#85ceff', '#7cdfd2', '#ceafff'][i]}
                    strokeWidth="4"
                    fill="none"
                  />
                  <circle
                    cx={x}
                    cy={cy}
                    r="10"
                    fill={['#efc374', '#85ceff', '#7cdfd2', '#ceafff'][i]}
                  />
                  <text x="240" y={y + 7} textAnchor="end" fill="currentColor">
                    {name}
                  </text>
                </g>
              );
            })}
            <rect
              x="650"
              y="140"
              width="225"
              height="120"
              rx="16"
              fill="#132d3d"
              stroke="#efc374"
            />
            <text x="762" y="185" textAnchor="middle" fill="currentColor">
              Shared geometric
            </text>
            <text x="762" y="215" textAnchor="middle" fill="currentColor">
              action · proposed
            </text>
            <text x="450" y="395" textAnchor="middle" fill="currentColor">
              Conceptual connection, not numerical convergence
            </text>
          </svg>
        </div>
        <div className="prototype-controls">
          <button
            onClick={() => {
              setMotion(true);
              setForcePlaying(!forcePlaying);
            }}
          >
            {forcePlaying && motion ? 'Pause unification' : 'Play unification'}
          </button>
          <label>
            Explore the connection
            <input
              type="range"
              min="0"
              max="100"
              value={forceFrame}
              onChange={(e) => {
                setForcePlaying(false);
                setForceFrame(+e.target.value);
              }}
            />
          </label>
        </div>
        <div className="table-scroll">
          <table>
            <caption>
              Retained gauge-coupling screens · not running curves
            </caption>
            <thead>
              <tr>
                <th>Quantity</th>
                <th>Historical value</th>
                <th>Authority</th>
              </tr>
            </thead>
            <tbody>
              {catalog.prediction_ledger
                .filter((r) => r.sector === 'gauge_couplings')
                .map((r) => (
                  <tr key={r.id}>
                    <th>{r.quantity}</th>
                    <td>{value(r.predicted as number)}</td>
                    <td>{r.status}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        <Outputs exhibit="forces" />
        <p>
          A future quantitative animation needs source-owned scale dependence,
          normalization, uncertainty and a specified common domain. The
          schematic will remain identified separately from those data.
        </p>
        <a
          href={`${SCIENCE}/src/bhsm/interface/bhsm_standard_model_gauge_vertices.py`}
        >
          Shared gauge structure and coupling requirements ↗
        </a>
      </article>
      {[
        ['action', '02', 'Geometry to observables'],
        ['spectral', '04', 'Spectral forecasts'],
      ].map(([id, number, title]) => {
        const row = exhibits.find((r) => r.number === number)!;
        return (
          <article id={`science-${id}`} className="primary-exhibit" key={id}>
            <p className="eyebrow">Retained BHSM science prototype</p>
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
      <p className="collection-update">
        As BHSM closes its physical gates, reviewed source artifacts update
        these same exhibits. New comparison panels do not replace them.{' '}
        <a href={`${SCIENCE}/docs/MUSEUM_SCIENCE_UPDATE.md`}>
          Academic data-update contract ↗
        </a>
      </p>
    </section>
  );
}
