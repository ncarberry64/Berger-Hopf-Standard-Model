'use client';
import { useState } from 'react';
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
  const [answer, setAnswer] = useState('');
  const [evidence, setEvidence] = useState('');
  const entry = catalog.exhibits.find((item) => item.id === id);
  if (!entry?.question || id === 'details' || id === 'creator') return null;
  const draft = `Exhibit: ${entry.title}\n${entry.url}\n\nReview question: ${entry.question}\n\nReviewer response:\n${answer}\n\nSources, revision, method and evidence:\n${evidence}\n`;
  const url = `${catalog.repository_url}/issues/new?title=${encodeURIComponent(`Museum review: ${entry.title}`)}&body=${encodeURIComponent(draft)}`;
  return (
    <details className="exhibit-review">
      <summary>Review this result · sources, scope &amp; a question</summary>
      <h4>A question for reviewers</h4>
      <p className="review-question">{entry.question}</p>
      <div className="review-response">
        <label htmlFor={`answer-${id}`}>Your answer or question</label>
        <textarea
          id={`answer-${id}`}
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          rows={4}
          maxLength={1400}
          placeholder="Explain your result, challenge an assumption, or ask for clarification."
        />
        <label htmlFor={`evidence-${id}`}>
          Sources and reproduction details
        </label>
        <textarea
          id={`evidence-${id}`}
          value={evidence}
          onChange={(event) => setEvidence(event.target.value)}
          rows={3}
          maxLength={900}
          placeholder="Source revision, calculation steps, links, uncertainties…"
        />
        <a
          className="review-draft-link"
          href={url}
          target="_blank"
          rel="noreferrer"
        >
          Continue to GitHub to submit your answer ↗
        </a>
        <small>
          GitHub is the public response venue. Sign in there, review the draft,
          then select Create. This form does not submit automatically; text
          stays in this tab until you continue. Responses and follow-up
          discussion remain with the public issue.
        </small>
        <a
          download={`BHSM-review-${id}.txt`}
          href={`data:text/plain;charset=utf-8,${encodeURIComponent(draft)}`}
        >
          Save your response as a text file
        </a>
        {' · '}
        <a
          href={`${catalog.repository_url}/issues?q=${encodeURIComponent(`is:issue "Museum review: ${entry.title}"`)}`}
          target="_blank"
          rel="noreferrer"
        >
          Read responses to this exhibit ↗
        </a>
      </div>
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
        Use “Review this result” in the science exhibits and Big Questions to
        find sources and a concrete question. Contributions may reproduce a
        calculation, identify a discrepancy, challenge an assumption or propose
        an independent test.
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
