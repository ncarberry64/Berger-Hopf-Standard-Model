import { SCIENCE } from './exhibits';

export function MuonResult() {
  return (
    <section
      className="muon-result evidence-feature"
      aria-labelledby="muon-result-title"
    >
      <p className="eyebrow">
        BHSM deliverable · local electromagnetic vertex and charge identity
      </p>
      <h4 id="muon-result-title">
        From BHSM’s lepton action to the muon’s magnetic response.
      </h4>
      <p>
        A muon behaves like a tiny magnet. BHSM first builds the charged-lepton
        interaction from its action, then checks that the interaction conserves
        electric charge. Its current calculation establishes this local charge
        identity for all three lepton families without inserting measured lepton
        masses.
      </p>
      <ol>
        <li>
          <strong>Build the vertex:</strong> the retained local interaction is
          Γμ = Qℓγμ, with Qℓ = −1 for each charged lepton.
        </li>
        <li>
          <strong>Separate the response:</strong> F₁ describes the charge term;
          F₂ describes the additional magnetic response. The minimal tree vertex
          has no Pauli term, so F₂ = 0 at this order.
        </li>
        <li>
          <strong>Read the magnetic anomaly:</strong> after charge
          normalization, aμ = (gμ − 2)/2 = F₂(0). The tree result corresponds to
          g = 2 in the positive-magnitude convention.
        </li>
      </ol>
      <div className="muon-readouts">
        <p>
          <small>Derived local tree result</small>
          <strong>F₂ = 0</strong>
          <span>Before quantum corrections</span>
        </p>
        <p>
          <small>Physical quantum anomaly</small>
          <strong>Not yet evaluated</strong>
          <span>An open calculation, not a failed prediction</span>
        </p>
      </div>
      <p>
        The next number must come from the same-action, renormalized quantum
        vertex with the normalized photon and physical muon state. Charge
        conservation alone cannot determine it: qμσμνqν = 0, so any transverse
        Pauli coefficient leaves that charge identity unchanged. This is why
        completing the identity is an achievement, but is not yet a numerical
        prediction of the observed anomaly.
      </p>
      <p className="console-caption">
        The muon card below shows the edition-labeled CODATA measurement, not a
        BHSM output. The 2025 Fermilab anomaly measurement is a separate
        experimental result and does not replace that magnetic-moment reference
        silently.
      </p>
      <div className="record-links">
        <a href={`${SCIENCE}/theory/ae31_c2_local_em_ward_identity.md`}>
          BHSM derivation and scope ↗
        </a>
        <a href={`${SCIENCE}/theory/muon_minimum_pauli_readout_20260930.md`}>
          Minimum Pauli projection: derivation and tests ↗
        </a>
        <a
          href={`${SCIENCE}/src/bhsm/interface/universal_precision_form_factor.py`}
        >
          Executable F₁/F₂ readout ↗
        </a>
        <a href="https://news.fnal.gov/2025/06/muon-g-2-most-precise-measurement-of-muon-magnetic-anomaly/">
          Fermilab’s 2025 measurement ↗
        </a>
      </div>
    </section>
  );
}
