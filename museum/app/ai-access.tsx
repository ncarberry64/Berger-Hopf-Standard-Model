'use client';
/* oxlint-disable next/no-html-link-for-pages -- These links fetch static JSON/text files, not Next pages. */

import { useState } from 'react';
import { aiHandoffJSON } from '../lib/ai-guide.mjs';

export function AIInterfaceButton() {
  const [status, setStatus] = useState('');
  return (
    <div className="ai-copy-control">
      <button
        className="ai-copy-button"
        type="button"
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(aiHandoffJSON);
            setStatus(
              'JSON copied. Paste into your AI, then ask your question.',
            );
          } catch {
            setStatus(
              'Clipboard unavailable. Open AI access in Sources & links to copy the JSON manually.',
            );
          }
        }}
      >
        Copy BHSM for AI
      </button>
      <output>{status}</output>
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
        the scientific record. Then ask your questions.
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
        Your AI needs web or GitHub access to read the sources. This button only
        copies context; it does not send information to an AI service. The
        packet asks your assistant to cite sources and distinguish established
        results, BHSM proposals and open questions.
      </small>
    </section>
  );
}
