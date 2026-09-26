const sources = './research/';

export function CosmologyUpdate() {
  return (
    <div className="cosmology-update">
      <article className="cosmology-panel">
        <p className="eyebrow">September 2026 · what changed</p>
        <h3>A cosmic pattern can respond to its surroundings.</h3>
        <p>
          In the frozen R1 reference model, matter and radiation are coupled to
          the large-scale geometric response. Specified density and velocity
          patterns can drive both parts of its temporal state: its amplitude
          and a momentum-like response coordinate. The matter-only inputs
          already span both parts at the eight tested epochs.
        </p>
        <div className="cosmology-equation" aria-label="Later topographic state equals transported initial state plus environmental response">
          X₂(z) = UXX(z) X₂(zᵢ) + UXE(z) Eᵢ
        </div>
        <p>
          <strong>Numerical result: rank UXE = 2</strong> at redshifts 1.5, 1,
          0.8, 0.5, 0.3, 0.1, 0.02 and 0. The environmental transfer is zero
          at the starting point, zᵢ = 2.1. This sampled result is not a proof
          for every intervening time.
        </p>
        <p>
          The initial environment is supplied, not inferred by this calculation.
          An isolated one-dimensional attractor is not required for this
          coupled realization. Earlier cosmic initial conditions and the
          absolute BHSM-to-R1 normalization remain open.
        </p>
        <details className="console-details">
          <summary>Two temporal components, nine spatial coefficients</summary>
          <p>
            The scalar n = 2 harmonic sector on the three-sphere has nine
            spatial coefficients. The same isotropic temporal transfer acts
            on each. It can carry an existing orientation but cannot create
            a preferred axis from an isotropic state.
          </p>
          <p>
            A single spatial profile requires rank X(z) ≤ 1 at each epoch
            and one common profile throughout the history. Aligned initial
            topographic and environmental patterns are sufficient; aligning
            the environment alone is not sufficient if the initial
            topographic pattern is independent. Generic inputs can give
            spatial rank two. This spatial condition is distinct from the
            temporal transfer rank and the covariance test below.
          </p>
          <p>
            X₂ = (q₂, Π₂), with q₂ = ζ and Π₂ = 2a³Gₛ,₂ζ̇. This
            reference-normalized Π₂ is not identified with the full coupled
            canonical momentum. The numerical audit checks both declared
            output bases without changing the frozen reference kernels.
          </p>
          <p>
            Research update as of 24 September: 11 focused tests passed;
            the manuscript integration’s full validation suite was still
            pending at this snapshot.
          </p>
          <div className="record-links">
            <a href={`${sources}r1-coupled-environment-section.tex`}>Corrected manuscript section ↗</a>
            <a href={`${sources}r1-coupled-environment-replay.json`}>Numerical replay ↗</a>
            <a href={`${sources}r1-integration-receipt.json`}>Validation snapshot ↗</a>
          </div>
        </details>
      </article>

      <article className="cosmology-panel">
        <p className="eyebrow">Observations · frozen sightline tests</p>
        <h3>A coherent supernova residual is not established.</h3>
        <p>
          With the axis, amplitude and transfer law held fixed, the primary
          Pantheon held-out test gives a small preference for the template.
          The separate DES transfer favors the null. These conditional
          comparisons do not establish a common physical signal.
        </p>
        <div className="table-scroll">
          <table className="cosmology-table">
            <caption>Source/environment comparison · original released covariance</caption>
            <thead><tr><th scope="col">Test</th><th scope="col">Rows</th><th scope="col">Δχ²</th><th scope="col">Conditional mock p</th></tr></thead>
            <tbody>
              <tr><th scope="row">Pantheon · held out</th><td>1,208</td><td>−0.883</td><td>0.0725</td></tr>
              <tr><th scope="row">DES · nuisance transfer</th><td>1,467</td><td>+1.321</td><td>0.5897</td></tr>
            </tbody>
          </table>
        </div>
        <p>
          Δχ² = χ²(template) − χ²(null); negative favors the template.
          The p-values are one-sided Gaussian-mock diagnostics conditional
          on the specified covariance and nuisance features, not model probabilities.
        </p>
        <p>
          A fixed external peculiar-velocity correction gives a stronger
          sensitivity result, but missing field-error and source cross-covariance
          prevent treating it as a discovery likelihood. Local-shell tomography
          does not identify a common foreground cause. Earlier unsuccessful
          foreground-transfer tests remain part of the record.
        </p>
        <div className="record-links">
          <a href={`${sources}sn-sightline-report.md`}>Full results and limitations ↗</a>
          <a href="https://github.com/ncarberry64/Manuscript-Generation">Cosmology research repository ↗</a>
        </div>
      </article>

      <article className="cosmology-panel">
        <p className="eyebrow">What could rule out the proposed realization?</p>
        <h3>One shared state must survive two different tests.</h3>
        <p>
          <strong>Gate A · shared response.</strong> The deterministic observables
          must be compatible with one common two-component state. A properly
          calibrated residual test with p &lt; 0.01 rejects that realization.
        </p>
        <p>
          <strong>Gate B · coherent covariance.</strong> The minimal contribution
          from one coherent random amplitude must have covariance rank at most
          one after independently specified standard and noise treatment.
          A predeclared finite-sample test with p &lt; 0.01 rejects that realization.
          One local stochastic field need not retain rank one after path integration.
        </p>
        <p>
          These are prospective tests with separate null hypotheses, not two
          independent detections. Survey nuisance calibration remains to be
          completed. The retrospective supernova tests above do not replace
          these gates; adding channels or retuning after seeing the result
          would change the tested model.
        </p>
        <div className="record-links">
          <a href={`${sources}cosmology-two-gate-protocol.json`}>Frozen structural protocol ↗</a>
          <a href={`${sources}cosmology-test-prerequisites.md`}>Survey prerequisites ↗</a>
        </div>
      </article>
    </div>
  );
}
