import { catalog } from '../lib/ai-guide.mjs';

export function ExhibitStatement({ id }: { id: string }) {
  const entry = catalog.exhibits.find((item) => item.id === id);
  if (!entry?.statement) return null;
  return (
    <div className="exhibit-statement">
      <p className="eyebrow">{entry.classification}</p>
      <p>{entry.statement}</p>
    </div>
  );
}

export function ExhibitReview({ id }: { id: string }) {
  const entry = catalog.exhibits.find((item) => item.id === id);
  if (!entry?.question) return null;
  const draft = `Exhibit: ${entry.title}\n${entry.url}\n\nReview question: ${entry.question}\n\nSource revision and exact claim:\n\nInputs, method and reproduction steps:\n\nResult, discrepancy or proposed test:\n\nEvidence and limitations:\n`;
  const url = `${catalog.repository_url}/issues/new?title=${encodeURIComponent(`Museum review: ${entry.title}`)}&body=${encodeURIComponent(draft)}`;
  return (
    <details className="exhibit-review">
      <summary>Review this result · sources, scope &amp; a question</summary>
      <h4>A question for reviewers</h4>
      <p className="review-question">{entry.question}</p>
      <h4>Inspect the evidence</h4>
      <ul>
        {entry.sources.map(
          (source: { title: string; url: string; github_url?: string }) => (
            <li key={source.url}>
              <a href={source.github_url ?? source.url}>{source.title} ↗</a>
            </li>
          ),
        )}
      </ul>
      <h4>Scope of this exhibit</h4>
      <p>{entry.scope}</p>
      <p>
        Identify the source revision, state the assumptions, and include
        reproducible steps or a specific test. Separate the calculation from its
        physical interpretation.
      </p>
      <a
        className="review-draft-link"
        href={url}
        target="_blank"
        rel="noreferrer"
      >
        Open a review draft on GitHub ↗
      </a>
      <small>
        You review and submit the draft on GitHub. Existing reviews are public
        in the repository.
      </small>
    </details>
  );
}

export function OpenReviewInvitation() {
  return (
    <section
      className="open-review-invitation"
      aria-labelledby="open-review-title"
    >
      <p className="eyebrow">A living, open scientific review forum</p>
      <h2 id="open-review-title">
        Explore BHSM’s claims. Inspect the calculations. Help test what follows.
      </h2>
      <p>
        The museum presents BHSM proposals, numerical results and the route to
        physical predictions. Follow an animation, inspect the numbers, open the
        evidence and challenge the reasoning.
      </p>
      <p>
        Use “Review this result” in each exhibit to find its sources and a
        concrete question. Contributions may reproduce a calculation, identify a
        discrepancy, challenge an assumption or propose an independent test.
      </p>
      <p>
        Open review here invites scientific scrutiny; it does not certify
        journal peer review. A formal manuscript is planned for submission to a
        journal for independent scientific review.
      </p>
      <a href={`${catalog.repository_url}/issues`}>
        Read and contribute public reviews ↗
      </a>
    </section>
  );
}
