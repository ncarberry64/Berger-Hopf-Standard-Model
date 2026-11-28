const repository = 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model';

export function MuseumEvidenceGuide() {
  return (
    <section
      id="museum-evidence-guide"
      className="museum-evidence-guide"
      aria-labelledby="museum-evidence-title"
    >
      <div className="museum-evidence-heading">
        <div>
          <p className="eyebrow">Inspect the evidence</p>
          <h2 id="museum-evidence-title">
            An idea is the beginning. A test is the next step.
          </h2>
        </div>
        <p className="museum-edition">
          Visitor edition <time dateTime="2026-11-28">28 November 2026</time>
        </p>
      </div>
      <p className="museum-evidence-intro">
        Read each exhibit’s status before interpreting its result. A visual
        analogy, a calculation under assumptions and an experimentally tested
        description answer different questions.
      </p>
      <dl className="museum-status-key">
        <div>
          <dt>
            <span className="museum-status-dot status-reference" />
            Established reference
          </dt>
          <dd>
            Conventional particle physics and observed structures used for
            context. Their success does not by itself validate the BHSM
            connection.
          </dd>
        </div>
        <div>
          <dt>
            <span className="museum-status-dot status-conditional" />
            Conditional or computed result
          </dt>
          <dd>
            A result for the stated assumptions, action, background or numerical
            domain. Follow its source to see where it applies.
          </dd>
        </div>
        <div>
          <dt>
            <span className="museum-status-dot status-screen" />
            Historical screen
          </dt>
          <dd>
            A numerical comparison with measured values. Agreement becomes a
            prediction only after independent selection rules and the physical
            calculation are established.
          </dd>
        </div>
        <div>
          <dt>
            <span className="museum-status-dot status-proposal" />
            Proposal or open question
          </dt>
          <dd>
            A BHSM interpretation or unfinished link that still needs a
            derivation, calculation or distinguishing observation.
          </dd>
        </div>
      </dl>

      <div className="museum-evidence-routes">
        <a href="#science-test">
          <span>01 / Reproduce</span>
          <strong>Check a numerical comparison →</strong>
          <small>Inputs, reference values and differences.</small>
        </a>
        <a href="#research-exhibit">
          <span>02 / Inspect</span>
          <strong>Open a calculation and its scope →</strong>
          <small>Recorded data and local numerical certificates.</small>
        </a>
        <a href={`${repository}/blob/main/docs/OPEN_RESEARCH.md`}>
          <span>03 / Investigate</span>
          <strong>Follow the open research register ↗</strong>
          <small>Unfinished objects, source links and next tests.</small>
        </a>
      </div>

      <details className="museum-reading-desk">
        <summary>Research reading desk · dates, sources and open tests</summary>
        <p>
          The date above identifies this visitor guide. Scientific claims retain
          their own source dates, assumptions and revisions. BHSM remains an
          unfinished research programme; a museum update does not close a
          scientific gate.
        </p>
        <ol>
          <li>
            <strong>Trace the claim.</strong> Open the{' '}
            <a href={`${repository}/blob/main/docs/current_bhsm_status.md`}>
              dated scientific status record
            </a>{' '}
            and identify the result’s domain and revision.
          </li>
          <li>
            <strong>Find the missing link.</strong> Ask whether mode selection,
            physical normalization, a decay channel or an observable has
            actually been calculated for that claim.
          </li>
          <li>
            <strong>Try to reproduce or challenge it.</strong> Use the{' '}
            <a
              href={`${repository}/blob/main/docs/reviewer_30min_quickstart.md`}
            >
              reviewer quickstart
            </a>
            , then the exhibit’s “Review this result” panel to prepare a sourced
            question.
          </li>
        </ol>
        <p>
          <a href="./research/animation-evidence.md">
            Animation methods and limitations ↗
          </a>
          {' · '}
          <a href={`${repository}/commits/main/museum/`}>
            Museum update history ↗
          </a>
        </p>
      </details>

      <div className="museum-learning-kit">
        <div>
          <p className="eyebrow">Take the museum with you</p>
          <h3>A poster, a conversation, a classroom.</h3>
          <p>
            Print the seven-scale atlas or use a 20-minute activity to
            distinguish observations, models and open tests. The guide includes
            a narration transcript, worksheet and teacher notes.
          </p>
        </div>
        <div className="museum-learning-links">
          <a
            href="./learn/bhsm-scale-atlas.svg"
            download="BHSM-seven-scale-atlas.svg"
          >
            Download the scale poster ↓{' '}
            <small>SVG · scalable for printing</small>
          </a>
          <a
            href="./learn/bhsm-visitor-guide.html"
            target="_blank"
            rel="noreferrer"
          >
            Open the classroom guide ↗{' '}
            <small>Printable · works offline when saved</small>
          </a>
          <a
            href="./learn/bhsm-visitor-guide.html"
            download="BHSM-visitor-guide.html"
          >
            Save the classroom guide ↓
          </a>
        </div>
      </div>
    </section>
  );
}
