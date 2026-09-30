'use client';
/* oxlint-disable next/no-html-link-for-pages -- These links fetch static JSON/text files, not Next pages. */

import { useRef, useState } from 'react';
import { aiHandoffJSON } from '../lib/ai-guide.mjs';

export function AIInterfaceButton() {
  const [status, setStatus] = useState('');
  const [manualCopy, setManualCopy] = useState(false);
  const text = useRef<HTMLTextAreaElement>(null);
  return (
    <div className="ai-copy-control">
      <button
        className="ai-copy-button"
        type="button"
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(aiHandoffJSON);
            setManualCopy(false);
            setStatus(
              'JSON copied. Paste into your AI, then ask your question.',
            );
          } catch {
            setManualCopy(true);
            setStatus(
              'Automatic copy is unavailable in this browser. Select and copy the JSON below, then paste it into your AI.',
            );
          }
        }}
      >
        Copy BHSM for AI
      </button>
      <output>{status}</output>
      {manualCopy && (
        <div className="ai-manual-copy">
          <textarea
            ref={text}
            aria-label="JSON for manual copy"
            readOnly
            value={aiHandoffJSON}
            rows={6}
          />
          <button
            className="ai-copy-button"
            type="button"
            onClick={() => {
              text.current?.focus();
              text.current?.select();
            }}
          >
            Select JSON
          </button>
          <a href="./ai/handoff.json" download>
            Download JSON instead
          </a>
        </div>
      )}
    </div>
  );
}

export function AIAccess() {
  return (
    <section className="ai-access" aria-labelledby="ai-access-title">
      <p className="eyebrow">
        AI interface · your assistant, the scientific record
      </p>
      <h2 id="ai-access-title">Bring your questions to BHSM.</h2>
      <p>
        Copy the JSON below and paste it into your preferred AI. It provides the
        BHSM GitHub repository, key source files and guidance for answering from
        the scientific record. It asks your AI to search BHSM using its
        available tools if direct file access is blocked. Then ask your
        questions.
      </p>
      <AIInterfaceButton />
      <div className="ai-access-actions">
        <a href="./ai/handoff.json" download>
          Download JSON
        </a>
        <a href="./llms.txt">AI-readable guide ↗</a>
        <a href="./ai/index.json">Exhibit index ↗</a>
      </div>
      <details>
        <summary>View or manually copy the JSON</summary>
        <textarea
          aria-label="BHSM AI interface JSON"
          readOnly
          value={aiHandoffJSON}
          rows={10}
        />
      </details>
      <small>
        Your AI can use web search, ordinary GitHub pages or a repository
        connector, depending on its capabilities. This button only copies
        context; it does not send information to an AI service. The packet asks
        your assistant to cite sources and distinguish established results, BHSM
        proposals and open questions.
      </small>
    </section>
  );
}
