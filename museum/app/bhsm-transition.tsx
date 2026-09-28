'use client';
import type { TransitionRecord } from '../lib/bhsm-transition';
import { REPOSITORY } from './exhibits';

const number = (value: number | null, digits = 2) =>
  value === null ? 'Not evaluated' : value.toFixed(digits);
const screens: Record<string, string> = {
  'kinematic-pass': 'Screen passes',
  'charge-blocked': 'Charge blocked',
  'threshold-closed': 'Threshold closed',
  'not-evaluated': 'Not evaluated',
};

export function BHSMTransition({
  record,
  approach,
  reveal,
}: {
  record: TransitionRecord;
  approach: number;
  reveal: number;
}) {
  const real = record.classification === 'RECONSTRUCTED_CMS_SUBSYSTEM';
  const science = `${REPOSITORY}/blob/${record.sources.theory_revision}`;
  const encounter = Math.max(0, approach * (1 - reveal));
  const stage = approach < 1 ? 0 : reveal < 0.2 ? 1 : reveal < 0.75 ? 2 : 3;
  return (
    <section className="bhsm-transition" aria-labelledby="transition-title">
      <header>
        <div>
          <p className="eyebrow">THE BHSM VIEW OF A TRANSITION</p>
          <h4 id="transition-title">BHSM Transition Diagram</h4>
        </div>
        <span className="transition-status">
          {real
            ? 'CMS subsystem · boundary unresolved'
            : 'Computed kinematics · boundary unresolved'}
        </span>
      </header>
      <p className="transition-intro">
        BHSM treats a particle as a dynamically maintained geometric
        envelopment. This diagram connects the displayed event to the incoming
        states, boundary question, candidate outcomes and quantities that can be
        tested.
      </p>
      <ol className="transition-stages">
        <li className={stage === 0 ? 'active' : ''}>
          <small>01 · INPUT</small>
          <h5>Incoming envelopes</h5>
          <svg viewBox="0 0 210 82" aria-hidden="true">
            <g
              fill="none"
              strokeWidth="1.5"
              strokeDasharray={real ? '4 4' : undefined}
            >
              {[0, 1].map((i) => (
                <g
                  key={i}
                  transform={`translate(${i ? 163 - approach * 20 : 47 + approach * 20} 41)`}
                  stroke={i ? '#ffbc77' : '#71e5eb'}
                >
                  <ellipse rx="29" ry="24" />
                  <ellipse rx="12" ry="24" />
                  <ellipse rx="29" ry="9" />
                </g>
              ))}
              <path
                d="M86 41H124M95 36L102 41L95 46M115 36L108 41L115 46"
                stroke="#a38fbd"
              />
            </g>
          </svg>
          <strong>
            {real
              ? 'Initial subprocess unknown'
              : record.incoming.labels.join(' + ')}
          </strong>
          <p>
            {real
              ? 'The sample contains outgoing muons, not the incoming partons or their envelopes.'
              : `√s = ${number(record.incoming.cm_energy_GeV)} GeV · Q = ${record.incoming.total_charge_e} e`}
          </p>
          <em>Envelope fields: not evaluated</em>
        </li>
        <li className={stage === 1 ? 'active' : ''}>
          <small>02 · ENCOUNTER</small>
          <h5>Active boundary imbalance</h5>
          <svg viewBox="0 0 210 82" aria-hidden="true">
            <ellipse
              cx="90"
              cy="41"
              rx="32"
              ry="28"
              fill="none"
              stroke="#71e5eb"
              opacity=".6"
            />
            <ellipse
              cx="120"
              cy="41"
              rx="32"
              ry="28"
              fill="none"
              stroke="#ffbc77"
              opacity=".6"
            />
            <circle
              cx="105"
              cy="41"
              r={14 + encounter * 8}
              fill="#bda7f5"
              opacity={0.12 + encounter * 0.3}
            />
            <path
              d="M105 11Q85 26 105 41T105 71"
              fill="none"
              stroke="#bda7f5"
              strokeDasharray="3 4"
            />
          </svg>
          <strong>Open BHSM calculation</strong>
          <p>
            The event-specific boundary response and transfer map have not been
            solved.
          </p>
          <em>Glow marks the encounter, not an imbalance measurement.</em>
        </li>
        <li className={stage === 2 ? 'active' : ''}>
          <small>03 · POSSIBLE OUTCOMES</small>
          <h5>Admissible branches</h5>
          <p className="transition-small">
            Necessary charge + threshold checks
          </p>
          <ul className="transition-branches">
            {record.branches.map((branch) => (
              <li key={branch.id} data-state={branch.screen}>
                <div>
                  <b>{branch.label}</b>
                  {branch.displayed && <small>DISPLAYED</small>}
                </div>
                <span>{screens[branch.screen]}</span>
                <small>
                  Threshold &gt; {branch.threshold_GeV.toFixed(3)} GeV
                </small>
              </li>
            ))}
          </ul>
          <em>
            BHSM branch selection and probabilities remain open. Candidate list
            is not exhaustive.
          </em>
        </li>
        <li className={stage === 3 ? 'active' : ''}>
          <small>04 · TESTABLE OUTPUT</small>
          <h5>{real ? 'Observed quantities' : 'Predicted observables'}</h5>
          <p className="transition-small">
            {real
              ? 'Measured subsystem readout'
              : 'Conditional kinematics for the chosen branch'}
          </p>
          <strong className="transition-mass">
            {number(record.observables.invariant_mass_GeV, 3)}{' '}
            <small>GeV</small>
          </strong>
          <p>
            {real
              ? 'Dimuon invariant mass only'
              : 'Selected final-state invariant mass'}
          </p>
          {record.observables.particles.map((p, i) => (
            <div className="transition-particle" key={i}>
              <b>{p.label}</b>
              <span>
                E {p.four_vector.E.toFixed(2)} · pT {p.pt_GeV.toFixed(2)} GeV
              </span>
            </div>
          ))}
          <em>BHSM rates and observable predictions: not yet evaluated.</em>
        </li>
      </ol>
      <div className="transition-footer">
        <p>
          {real
            ? 'A dimuon sample cannot determine the complete incoming collision or verify its full conservation balance.'
            : `Four-momentum conservation residual: ${record.observables.conservation_residual_GeV?.toExponential(1) ?? 'not evaluated'} GeV. The displayed channel and angle are chosen inputs.`}
        </p>
        <a
          download={`bhsm-transition-${record.event.id}.json`}
          href={`data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(record, null, 2))}`}
        >
          Download transition record ↓
        </a>
      </div>
      <details className="console-details">
        <summary>How to read this BHSM computation object</summary>
        <p>
          The envelope drawings express BHSM’s structural postulate, not
          reconstructed surfaces. The boundary stage identifies the physical
          calculation needed to explain a transition; it does not assign an
          imbalance or reinterpret a conservation residual as a force.
        </p>
        <p>
          For demonstrations, energy, reference masses, charges and the chosen
          angle determine two-body four-vectors. The branch screen checks only
          total electric charge and nonzero phase space above threshold.
          Additional conserved quantities, an action-derived transition
          amplitude and a probability law are needed to determine physical
          admissibility and rates. For CMS data, all incoming-state and branch
          checks remain unevaluated.
        </p>
        <p>
          The downloadable record contains the current event inputs, branch
          tests, outgoing four-vectors, units and source paths. Missing boundary
          fields, amplitudes and BHSM predictions are stored as null. Animation
          phase does not change the scientific record.
        </p>
        <div className="record-links">
          <a href={`${science}/${record.sources.envelopment}`}>
            BHSM envelopment foundation ↗
          </a>
          <a href={`${science}/${record.sources.boundary}`}>
            Boundary charge-map audit ↗
          </a>
          <a href={`${science}/${record.sources.transition}`}>
            Quantum transition gate ↗
          </a>
        </div>
      </details>
    </section>
  );
}
