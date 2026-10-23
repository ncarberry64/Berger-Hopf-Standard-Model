// Focused, dependency-free execution of the shipped renderer in a small DOM.
// This is not a layout/browser test; the installed-app review covers pixels.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

class Element {
  constructor(tag = 'div') { this.tagName = tag; this.children = []; this.parentElement = null; this.attributes = {}; this._text = ''; this.className = ''; this.id = ''; this.hidden = false; this.open = false; this.listeners = {}; this.classList = { toggle() {} }; }
  get childElementCount() { return this.children.filter(child => child.tagName !== '#text').length; }
  get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
  set textContent(value) { this.replaceChildren(); this._text = String(value); }
  append(...children) {
    for (let child of children) {
      if (typeof child === 'string') { const text = new Element('#text'); text.textContent = child; child = text; }
      child.remove(); child.parentElement = this; this.children.push(child);
    }
  }
  insertBefore(child, before) {
    if (before == null) { this.append(child); return; }
    assert.ok(this.children.includes(before), 'DOM insertion anchor must belong to the parent');
    child.remove(); child.parentElement = this; this.children.splice(this.children.indexOf(before), 0, child);
  }
  replaceChildren(...children) { for (const child of this.children) child.parentElement = null; this.children = []; this._text = ''; this.append(...children); }
  remove() { if (this.parentElement) { const siblings = this.parentElement.children; siblings.splice(siblings.indexOf(this), 1); this.parentElement = null; } }
  setAttribute(key, value) { this.attributes[key] = String(value); if (key === 'id') this.id = String(value); if (key === 'class') this.className = String(value); }
  matches(selector) { return selector.startsWith('#') ? this.id === selector.slice(1) : selector.startsWith('.') ? this.className.split(/\s+/).includes(selector.slice(1)) : this.tagName === selector; }
  querySelectorAll(selector) { return this.children.flatMap(child => [...(child.matches(selector) ? [child] : []), ...child.querySelectorAll(selector)]); }
  querySelector(selector) { return selector === 'span:last-child' ? this.children.filter(child => child.tagName === 'span').at(-1) || null : this.querySelectorAll(selector)[0] || null; }
  closest(selector) { for (let node = this; node; node = node.parentElement) if (node.matches(selector)) return node; return null; }
  addEventListener(name, handler) { this.listeners[name] = handler; }
}
const body = new Element('body');
const document = {
  getElementById: id => body.querySelector(`#${id}`),
  createElement: tag => new Element(tag),
  createElementNS: (_namespace, tag) => new Element(tag),
  createTextNode: text => { const node = new Element('#text'); node.textContent = text; return node; },
  querySelectorAll: selector => body.querySelectorAll(selector),
  querySelector: selector => selector === 'input[name="family"]:checked' ? { value: 'gr' } : body.querySelector(selector)
};
const web = new URL('../bhtracker/web/', import.meta.url);
const html = readFileSync(new URL('index.html', web), 'utf8');
for (const [, id] of html.matchAll(/\bid="([^"]+)"/g)) { const node = new Element(); node.id = id; body.append(node); }
const get = document.getElementById;
get('run-fit').append(new Element('span'));
const emptyTitle = new Element('h2'), emptyNote = new Element(); emptyNote.className = 'empty-footnote';
get('empty-results').append(emptyTitle, emptyNote);
for (const className of ['status-mark', 'status-copy']) { const node = new Element('span'); node.className = className; get('validation-state').append(node); }
get('nuisance-select').value = 'shear'; get('fit-starts').value = '2';
const interpretationPanel = new Element('section'); interpretationPanel.className = 'bhsm-interpretation'; body.append(interpretationPanel);
for (const id of ['bhsm-interpretation-title', 'boundary-choice-summary', 'bhsm-dictionary-details']) interpretationPanel.append(get(id));
const chartPanel = new Element('section'); chartPanel.className = 'chart-panel';
const legend = new Element(); legend.className = 'plot-legend'; chartPanel.append(legend, get('track-chart')); body.append(chartPanel);

const appPath = fileURLToPath(new URL('app.js', web));
const source = readFileSync(appPath, 'utf8');
// Replace only bootstrapping; exercise production functions, not copies.
const boot = '  syncControls(); loadExamples();';
assert.equal(source.split(boot).length, 2, 'expected one application bootstrap');
const instrumented = source.replace(boot, '  globalThis.ui = { renderBHSMInterpretation, renderTrack, renderSeries, pollJob, state };');
let validationSource, fetchMode = 'duplicate', requestedPaths = [];
const runtime = { document, window: { addEventListener() {} }, setTimeout, clearTimeout, setInterval, clearInterval, Intl, TextEncoder, AbortController,
  fetch: async (path, options) => {
    requestedPaths.push(path);
    if (fetchMode === 'network') throw new Error('Test network interruption');
    if (fetchMode === 'missing') return { ok: false, status: 404, json: async () => ({ error: 'Unknown job' }) };
    if (fetchMode === 'server') return { ok: false, status: 500, json: async () => ({ error: 'Temporary server error' }) };
    validationSource = JSON.parse(options.body).dataset_json;
    return { ok: false, status: 400, json: async () => ({ error: 'Duplicate JSON key: schema_version' }) };
  } };
vm.createContext(runtime); vm.runInContext(instrumented, runtime, { filename: appPath });
const { ui } = runtime;

// Execute the actual upload and validation handlers. The raw uploaded text must
// reach strict server validation intact; JSON.parse/stringify would erase keys.
const duplicateInput = '{"schema_version":0,"schema_version":1,"geometry":{},"provenance":{"kind":"synthetic"}}';
const uploadEvent = { target: { files: [{ name: 'duplicate.json', size: duplicateInput.length, text: async () => duplicateInput }], value: 'duplicate.json' } };
await get('file-input').listeners.change(uploadEvent);
assert.equal(get('source-json').value, duplicateInput);
assert.equal(get('run-fit').disabled, true, 'unvalidated uploads cannot run');
await get('validate-data').listeners.click();
assert.equal(validationSource, duplicateInput, 'strict validation receives both duplicate keys');
assert.ok(get('validation-state').textContent.includes('Duplicate JSON key'));
assert.equal(ui.state.validated, false);
assert.equal(get('run-fit').disabled, true, 'rejected uploads cannot run');
assert.ok(html.includes('name="repository" content="https://github.com/ncarberry64/Berger-Hopf-Standard-Model"'));
assert.ok(html.includes('href="https://github.com/ncarberry64/Berger-Hopf-Standard-Model"'));

// A definitive missing job allows recovery; uncertain transport/server failures
// retain the active-job guard rather than accidentally submit another fit.
for (const mode of ['missing', 'network', 'server']) {
  fetchMode = mode; requestedPaths = [];
  ui.state.jobId = 'prior-job'; ui.state.busy = true; ui.state.validated = true;
  ui.state.examples = [{ id: 'nearby_motion' }]; ui.state.result = null;
  await ui.pollJob();
  assert.deepEqual(requestedPaths, ['/api/jobs/prior-job']);
  assert.equal(ui.state.result, null);
  if (mode === 'missing') {
    assert.equal(ui.state.busy, false); assert.equal(ui.state.jobId, null);
    assert.equal(get('retry-job').hidden, true);
    assert.equal(get('load-example').disabled, false); assert.equal(get('clear-data').disabled, false);
    assert.equal(get('result-content').hidden, true);
    assert.ok(get('global-message').textContent.includes('no longer has this job'));
  } else {
    assert.equal(ui.state.busy, true); assert.equal(ui.state.jobId, 'prior-job');
    assert.equal(get('retry-job').hidden, false);
    assert.ok(get('global-message').textContent.includes('may still be running'));
  }
}
ui.state.busy = false;

const model = { family: 'gr', r0_pc: .0001, worldtube_policy: 'supplied' };
const context = { schema_version: 1, status: 'PROPOSED_NOT_INFERRED', attribution: 'Dated proposal attribution',
  surface_summary: 'Surface statement supplied by the shared contract.', core_summary: 'Abstract core statement supplied by the shared contract.',
  matching_summary: 'Matching scope supplied by the shared contract.', inference_scope: 'Inference limit supplied by the shared contract.',
  claim_ledger: [{ label: 'One scoped claim', status: 'CONDITIONAL_DEDUCTION', statement: '<script>not markup</script>', source_refs: ['source:equation-1'] }] };
const metadata = { core_surface: context, source_provenance: { revision: 'source-revision', sources: [{ path: 'pinned.md', sha256: 'abc' }] } };
const before = JSON.stringify(metadata);
ui.renderBHSMInterpretation(metadata, model);
const primary = get('bhsm-core-surface-summary'), advanced = get('bhsm-core-surface-details');
assert.ok(primary && advanced);
assert.equal(advanced.open, false, 'theory details must start closed');
assert.ok(primary.textContent.includes(context.surface_summary) && primary.textContent.includes(context.core_summary));
assert.ok(!primary.textContent.includes(context.matching_summary), 'matching detail stays advanced');
assert.ok(advanced.textContent.includes(context.attribution) && advanced.textContent.includes(context.matching_summary) && advanced.textContent.includes(context.inference_scope));
assert.ok(advanced.textContent.includes(context.claim_ledger[0].statement));
assert.equal(advanced.querySelector('script'), null, 'metadata is rendered as text, never executable HTML');
assert.equal(advanced.querySelector('pre').textContent, JSON.stringify(metadata.source_provenance, null, 2));
assert.equal(JSON.stringify(metadata), before, 'rendering must not mutate interpretation/provenance');

// Replacing a new result with an older one must remove stale new claims.
ui.renderBHSMInterpretation({ parameter_meanings: [] }, model);
assert.equal(get('bhsm-core-surface-summary'), null);
assert.equal(get('bhsm-core-surface-details'), null);
assert.equal(get('bhsm-dictionary-details').hidden, false);
ui.renderBHSMInterpretation(null, model);
assert.equal(get('bhsm-dictionary-details').hidden, true);

// New metadata never turns unavailable boundary output into numeric cards.
for (const status of ['NOT_REPORTED_FOR_REJECTED_FIT', 'NOT_REPORTED_FOR_UNRESOLVED_MASS', 'NOT_ASSUMED_FOR_R1_METRIC']) {
  ui.renderBHSMInterpretation({ ...metadata, spherical_boundary: { status, reason: status } }, model);
  assert.equal(get('bhsm-spherical-boundary').querySelector('.boundary-measures'), null);
}

// Actual SVG endpoint labels preserve complete years and fractional epochs.
for (const epochs of [[2015, 2025], [2015.123456789, 2025.987654321], [2025, 2015]]) {
  ui.state.result = { epochs_yr: epochs, center_track_mas: [[.4587597211, -.4061374376], [1.125435447, -.7869648776]], observations: [] };
  const saved = JSON.stringify(ui.state.result); ui.renderTrack();
  const labels = get('track-chart').querySelectorAll('text').map(element => element.textContent).filter(text => text.startsWith('t='));
  assert.deepEqual(labels, [...epochs].sort((a, b) => a - b).map(epoch => `t=${String(epoch)}`));
  assert.equal(JSON.stringify(ui.state.result), saved, 'trajectory rendering preserves exported data');
}
get('series-select').value = '5';
ui.state.result = { epochs_yr: [2015, 2015, 2025], observations: [[1,2,3,4,0,10],[2,3,4,5,0,30],[1,2,3,4,0,12]], predictions: [[1,2,3,4,0,11],[2,3,4,5,0,29],[1,2,3,4,0,13]] };
ui.renderSeries();
assert.equal(get('series-chart').querySelectorAll('path').length, 0, 'independent source predictions are not joined into a trajectory');
assert.equal(get('series-chart').querySelectorAll('circle').length, 6);
assert.ok(get('series-caption').textContent.includes('No continuous source trajectory'));

// Also consume the actual versioned contract (or an explicitly supplied file).
const contractPath = process.argv[2] || fileURLToPath(new URL('../bhtracker/theory/BHSM_CORE_SURFACE_CONTRACT.json', import.meta.url));
const real = JSON.parse(readFileSync(contractPath, 'utf8'));
const provenance = JSON.parse(readFileSync(new URL('../bhtracker/theory/BHSM_INTERPRETATION_MANIFEST.json', import.meta.url), 'utf8'));
get('result-status-label').textContent = 'fit-status-sentinel';
ui.renderBHSMInterpretation({ core_surface: real, source_provenance: provenance }, model);
const actualPrimary = get('bhsm-core-surface-summary'), actualAdvanced = get('bhsm-core-surface-details');
assert.ok(actualPrimary.textContent.includes(real.surface_summary) && actualPrimary.textContent.includes(real.core_summary));
for (const value of [real.attribution, real.matching_summary, real.inference_scope, ...real.claim_ledger.map(entry => entry.statement)]) assert.ok(actualAdvanced.textContent.includes(value));
assert.equal(actualAdvanced.querySelector('pre').textContent, JSON.stringify(provenance, null, 2));
assert.equal(actualAdvanced.querySelectorAll('input').length + actualPrimary.querySelectorAll('input').length, 0, 'interpretation does not create fitted core controls');
assert.equal(get('result-status-label').textContent, 'fit-status-sentinel', 'theory metadata does not reclassify the fit');
console.log(`PASS: uploaded JSON integrity, missing-job recovery and interruption guards, independent-source plotting, canonical BHSM links, shared metadata (${real.claim_ledger.length} statements), legacy/suppression/safe text, and chronological lossless epoch labels.`);
