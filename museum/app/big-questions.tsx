'use client';

import { useState } from 'react';
import { physicsQuestions, questionTopics } from '../lib/physics-questions.mjs';
import {
  BigQuestionVisual,
  type BigQuestionVisualKind,
} from './big-question-visual';
import { ExhibitReview } from './exhibit-review';

const sourceBase =
  'https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/main/';

export function BigQuestions({ motion }: { motion: boolean }) {
  const [topic, setTopic] = useState(questionTopics[0].id);
  const [questionId, setQuestionId] = useState(physicsQuestions[0].id);
  const [query, setQuery] = useState('');
  const [playing, setPlaying] = useState(true);
  const term = query.trim().toLocaleLowerCase();
  const visible = physicsQuestions.filter((question) =>
    term
      ? `${question.title} ${question.answer} ${question.detail}`
          .toLocaleLowerCase()
          .includes(term)
      : question.topic === topic,
  );
  const selected =
    visible.find((question) => question.id === questionId) ?? visible[0];
  const currentTopic = questionTopics.find((item) => item.id === topic)!;

  return (
    <section
      id="big-questions"
      className="big-questions"
      aria-labelledby="big-questions-title"
    >
      <header className="questions-heading">
        <p className="eyebrow">Exhibit 13 · Big Questions</p>
        <h2 id="big-questions-title">The questions that keep us curious.</h2>
        <p>
          {physicsQuestions.length} questions about reality, matter and the
          cosmos. Explore a short BHSM explanation, watch its illustration, then
          open the reasoning and sources.
        </p>
      </header>
      <nav className="question-topics" aria-label="Physics question topics">
        {questionTopics.map((item) => (
          <button
            type="button"
            key={item.id}
            aria-pressed={!term && topic === item.id}
            onClick={() => {
              setTopic(item.id);
              setQuery('');
              setQuestionId(
                physicsQuestions.find((question) => question.topic === item.id)!
                  .id,
              );
            }}
          >
            {item.title}
          </button>
        ))}
      </nav>
      <div className="question-browser">
        <aside
          className="question-picker"
          aria-label="Choose a physics question"
        >
          <label htmlFor="physics-question-search">Find a question</label>
          <input
            id="physics-question-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try mass, time, neutrinos…"
          />
          <p className="question-list-label" aria-live="polite">
            {term
              ? `${visible.length} search ${visible.length === 1 ? 'result' : 'results'}`
              : currentTopic.description}
          </p>
          <div className="question-list">
            {visible.map((question) => (
              <button
                type="button"
                key={question.id}
                aria-pressed={selected?.id === question.id}
                aria-controls="physics-question-answer"
                onClick={() => setQuestionId(question.id)}
              >
                <span>{question.title}</span>
                <span aria-hidden="true">↗</span>
              </button>
            ))}
            {!visible.length && (
              <p>No matching questions. Try another word or choose a topic.</p>
            )}
          </div>
        </aside>
        {selected ? (
          <article
            id="physics-question-answer"
            className="question-answer"
            aria-labelledby="physics-question-title"
            key={selected.id}
          >
            <p className="question-status">{selected.status}</p>
            <h3 id="physics-question-title">{selected.title}</h3>
            <p className="question-short-answer">{selected.answer}</p>
            <figure className="question-figure">
              <BigQuestionVisual
                motion={motion && playing}
                kind={selected.visual as BigQuestionVisualKind}
                variant={selected.id}
              />
              <figcaption>{selected.caption}</figcaption>
            </figure>
            <div className="question-animation-controls">
              <button
                type="button"
                onClick={() => setPlaying(!playing)}
                disabled={!motion}
                aria-pressed={motion && playing}
              >
                {!motion
                  ? 'Animation off'
                  : playing
                    ? 'Pause animation'
                    : 'Play animation'}
              </button>
              <span>Conceptual illustration</span>
            </div>
            <details className="question-details">
              <summary>
                Go deeper · reasoning, open questions &amp; sources
              </summary>
              <h4>The BHSM explanation</h4>
              <p>{selected.detail}</p>
              {selected.formula && (
                <code className="question-formula">{selected.formula}</code>
              )}
              <h4>What remains to be established</h4>
              <p>{selected.boundary}</p>
              <h4>Read the supporting record</h4>
              <ul>
                {selected.sources.map((source) => (
                  <li key={source.path}>
                    <a
                      href={`${sourceBase}${source.path}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {source.title} ↗
                    </a>
                  </li>
                ))}
              </ul>
            </details>
          </article>
        ) : (
          <div id="physics-question-answer" className="question-empty">
            Choose a topic to keep exploring.
          </div>
        )}
      </div>
      <div className="questions-evidence">
        <p>
          These answers describe BHSM’s framework positions, geometric proposals
          and scoped results. The linked record explains which physical
          derivations and observational tests remain open.
        </p>
        <a href="#science-test">Explore the numerical comparisons ↗</a>
        <a href="./data/physics-questions.json" download>
          Download all questions &amp; sources ↓
        </a>
      </div>
      <ExhibitReview id="big-questions" />
    </section>
  );
}
