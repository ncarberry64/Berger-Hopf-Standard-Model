(function (root) {
  'use strict';
  const INPUT_LIMIT = 32_000_000;
  const ZIP_LIMIT = 128 * 1024 * 1024;
  const ACTIVE = new Set(['pending', 'running']);
  const TERMINAL = new Set(['complete', 'cancelled', 'failed']);
  const DECIMAL = /^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i;

  function numbers(text, name, minimum, maximum) {
    const tokens = String(text).trim().split(/[\s,]+/).filter(Boolean);
    const values = tokens.map(token => {
      if (!DECIMAL.test(token)) throw new Error(name + ' contains an invalid decimal number.');
      const value = Number(token);
      if (!Number.isFinite(value) || value < minimum || value > maximum) {
        throw new Error(name + ' must stay between ' + minimum + ' and ' + maximum + '.');
      }
      return value;
    });
    if (values.some((value, index) => index > 0 && value <= values[index - 1])) {
      throw new Error(name + ' must be strictly increasing, with no duplicates.');
    }
    return values;
  }

  function configuration(te, u0, entropyText, wallText) {
    const supplied = {tE_days: numbers(te, 'tE grid', 0.1, 10000), u0: numbers(u0, 'u0 grid', 0.0001, 10)};
    const grids = Object.fromEntries(Object.entries(supplied).filter(([, values]) => values.length));
    const count = Object.values(grids).reduce((total, values) => total + values.length, 0);
    if (count < 1 || count > 17) throw new Error('Request 1–17 grid points in total.');
    const seedTokens = String(entropyText).trim().split(/[\s,]+/).filter(Boolean);
    if (!seedTokens.length || seedTokens.length > 16) throw new Error('Supply 1–16 explicit uint32 random seed components.');
    const entropy = seedTokens.map(token => {
      if (!/^\d+$/.test(token)) throw new Error('Seed components must be uint32 integers.');
      const value = Number(token);
      if (!Number.isSafeInteger(value) || value > 4294967295) throw new Error('A seed component exceeds uint32.');
      return value;
    });
    if (!/^\d+$/.test(String(wallText).trim())) throw new Error('Wall budget must be a whole number of seconds.');
    const wall = Number(wallText);
    if (!Number.isSafeInteger(wall) || wall < 1 || wall > 3600) throw new Error('Wall budget must be 1–3600 seconds.');
    return {grids, entropy, wall_seconds: wall, max_saved_bytes: 268435456};
  }

  function bytesToBase64(value, encoder) {
    const bytes = value instanceof Uint8Array ? value : new Uint8Array(value);
    let binary = '';
    for (let at = 0; at < bytes.length; at += 0x8000) {
      binary += String.fromCharCode.apply(null, bytes.subarray(at, at + 0x8000));
    }
    return (encoder || root.btoa.bind(root))(binary);
  }

  function mergeNodes(planned, received) {
    const plan = Array.isArray(planned) ? planned : [];
    const incoming = Array.isArray(received) ? received : [];
    const used = new Set();
    const result = plan.map(point => {
      const index = incoming.findIndex((node, at) => !used.has(at) && node && node.node_id === point.node_id);
      if (index < 0) return {...point, decision: 'UNKNOWN_NOT_RETURNED', unknown: 'No committed result returned for this planned node.'};
      used.add(index);
      return {...point, ...incoming[index]};
    });
    incoming.forEach((node, index) => {
      if (!used.has(index)) result.push(node && typeof node === 'object' ? {...node} : {node_id: 'Unparsed row ' + index, unknown: String(node)});
    });
    return result;
  }

  function text(value) {
    if (value === null || value === undefined) return 'Unavailable';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }

  function probability(value) {
    return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1 ? String(value) : 'Unavailable';
  }

  function safeJobId(value) {
    if (typeof value !== 'string' || !/^[A-Za-z0-9_-]{1,128}$/.test(value)) throw new Error('The server returned an invalid job identifier.');
    return value;
  }

  function createApp(dependencies) {
    const deps = dependencies || {};
    const doc = deps.document || root.document;
    const fetcher = deps.fetch || root.fetch.bind(root);
    const later = deps.setTimeout || root.setTimeout.bind(root);
    const clear = deps.clearTimeout || root.clearTimeout.bind(root);
    const names = ['form', 'input-file', 'input-note', 'te-grid', 'u0-grid', 'entropy', 'wall', 'plan', 'plan-status', 'plan-details', 'plan-json', 'start', 'message', 'job-title', 'job-status', 'progress-bar', 'node-progress', 'fit-progress', 'stage', 'workspace', 'cancel', 'refresh', 'job-history', 'export', 'result-scope', 'node-rows', 'result-json', 'replay-file', 'replay-file-note', 'integrity', 'numerical', 'replay-status', 'return-job'];
    const el = Object.fromEntries(names.map(name => [name, doc.getElementById('mc-' + name)]));
    if (names.some(name => !el[name])) throw new Error('The calibration page is missing a required control.');
    const state = {input: null, inputRevision: 0, replay: null, plan: null, busy: false, pollBusy: false,
      jobId: null, jobStatus: null, snapshot: null, history: new Map(), view: 'empty', viewNodes: [],
      pollTimer: null, watch: 0, cancelRequested: false, lastError: null, disposed: false};

    function clearError() { state.lastError = null; el.message.hidden = true; el.message.textContent = ''; }
    function showError(error) {
      state.lastError = error && error.message ? error.message : String(error);
      el.message.textContent = state.lastError; el.message.hidden = false;
    }
    function config() { return configuration(el['te-grid'].value, el['u0-grid'].value, el.entropy.value, el.wall.value); }
    function signature(value) { return state.inputRevision + ':' + JSON.stringify(value); }
    function active() { return ACTIVE.has(state.jobStatus); }
    function updateButtons() {
      const locked = state.busy || state.pollBusy || active();
      let freshPlan = false;
      try { freshPlan = !!state.plan && state.plan.signature === signature(config()); } catch (_) { freshPlan = false; }
      ['input-file', 'te-grid', 'u0-grid', 'entropy', 'wall'].forEach(name => { el[name].disabled = locked; });
      el.plan.disabled = locked || !state.input;
      el.start.disabled = locked || !freshPlan;
      el.cancel.disabled = state.busy || !state.jobId || !active() || state.cancelRequested;
      el.refresh.disabled = state.busy || state.pollBusy || !state.jobId;
      el.export.disabled = state.busy || state.pollBusy || state.view !== 'job' || !state.jobId || !TERMINAL.has(state.jobStatus);
      el['job-history'].disabled = locked || state.history.size === 0;
      el['replay-file'].disabled = locked;
      el.integrity.disabled = locked || !state.replay;
      el.numerical.disabled = locked || !state.replay;
      el['return-job'].hidden = !state.jobId || state.view === 'job';
      el['return-job'].disabled = state.busy || state.pollBusy;
    }
    function stopPoll() { if (state.pollTimer !== null) clear(state.pollTimer); state.pollTimer = null; }
    function dropPlan() {
      state.plan = null; el['plan-status'].textContent = 'Input or configuration changed. Validate a new plan before starting.';
      el['plan-details'].hidden = true; updateButtons();
    }
    function history() {
      el['job-history'].replaceChildren();
      if (!state.history.size) {
        const option = doc.createElement('option'); option.value = ''; option.textContent = 'No recorded jobs'; el['job-history'].append(option);
      } else {
        state.history.forEach((item, id) => {
          const option = doc.createElement('option'); option.value = id; option.textContent = id + ' · ' + item.status;
          el['job-history'].append(option);
        });
        el['job-history'].value = state.jobId || '';
      }
    }
    function renderNodes(planned, received) {
      const nodes = mergeNodes(planned, received); state.viewNodes = nodes; el['node-rows'].replaceChildren();
      if (!nodes.length) {
        const row = doc.createElement('tr'); const cell = doc.createElement('td'); cell.colSpan = 6;
        cell.textContent = 'No planned nodes yet.'; row.append(cell); el['node-rows'].append(row); return;
      }
      nodes.forEach(node => {
        const row = doc.createElement('tr');
        const labels = {tE_days: 'tE (days)', u0: 'u0 (dimensionless)'};
        const cells = [text(node.node_id), (labels[node.parameter] || text(node.parameter)) + ': ' + text(node.value),
          text(node.decision === undefined ? 'UNKNOWN' : node.decision), probability(node.p_lower), probability(node.p_upper), text(node.unknown)];
        cells.forEach((value, index) => {
          const cell = doc.createElement('td'); cell.textContent = value;
          if (index === 0) cell.className = 'mc-node-id';
          if (index === 2) cell.className = 'mc-decision';
          if (index === 5) cell.className = 'mc-unknown';
          row.append(cell);
        });
        el['node-rows'].append(row);
      });
    }
    async function responseError(response) {
      let value;
      try { value = await response.json(); } catch (_) { value = {error: 'Request failed (HTTP ' + response.status + ').'}; }
      return new Error(text(value.error || value.message || value));
    }
    async function request(path, body, binary, uploadType) {
      const controller = typeof root.AbortController === 'function' ? new root.AbortController() : null;
      const timer = controller ? later(() => controller.abort(), 180000) : null;
      try {
        const options = {method: body === undefined ? 'GET' : 'POST', credentials: 'same-origin', cache: 'no-store', redirect: 'error'};
        if (controller) options.signal = controller.signal;
        if (body !== undefined) {
          options.headers = {'Content-Type': uploadType || 'application/json'};
          options.body = uploadType ? body : JSON.stringify(body);
        }
        const response = await fetcher(path, options);
        if (!response.ok) throw await responseError(response);
        if (binary) {
          const mime = response.headers && response.headers.get ? response.headers.get('Content-Type') : null;
          if (mime && !/^(application\/zip|application\/octet-stream|application\/x-zip-compressed)(?:;|$)/i.test(mime)) {
            throw new Error('The server did not return a ZIP. The durable workspace and prior records remain retained.');
          }
          return response.blob();
        }
        return await response.json();
      } catch (error) {
        if (error && error.name === 'AbortError') throw new Error('Request timed out. Its outcome is unavailable; existing job records remain retained.');
        throw error;
      } finally { if (timer !== null) clear(timer); }
    }
    async function operation(fn, allowStatusOverlap) {
      if (state.busy || state.disposed || (state.pollBusy && !allowStatusOverlap)) return false;
      state.busy = true; clearError(); updateButtons();
      try { await fn(); return true; } catch (error) { showError(error); return false; }
      finally { state.busy = false; updateButtons(); }
    }
    async function readFile(file, limit) {
      if (!file || !Number.isSafeInteger(file.size) || file.size < 1 || file.size > limit) throw new Error('Choose a nonempty file within the declared byte limit.');
      const bytes = new Uint8Array(await file.arrayBuffer());
      if (bytes.length !== file.size || bytes.length > limit) throw new Error('The selected file byte count changed or exceeds the limit.');
      return {name: String(file.name || 'input'), bytes: bytes.length, base64: bytesToBase64(bytes, deps.btoa)};
    }
    async function loadInput(file) {
      if (active()) { showError(new Error('Wait for the active job to stop before changing input.')); return false; }
      return operation(async () => {
        dropPlan(); state.input = null; state.inputRevision++; el['input-note'].textContent = 'No valid input loaded.';
        if (!file) { el['input-note'].textContent = 'No file selected.'; return; }
        const value = await readFile(file, INPUT_LIMIT); state.input = value;
        el['input-note'].textContent = value.name + ' · ' + value.bytes + ' original bytes retained. JSON has not been reserialized.';
      });
    }
    async function loadReplay(file) {
      if (active()) { showError(new Error('Wait for the active job to stop before replay verification.')); return false; }
      return operation(async () => {
        state.replay = null; el['replay-file-note'].textContent = 'No valid ZIP loaded.';
        el['replay-status'].textContent = 'No verification for the current file selection.';
        if (state.view === 'replay' || state.view === 'replay_unverified') {
          state.view = 'replay_unverified'; renderNodes([], []);
          el['result-scope'].textContent = 'Replay file selection changed. No verification result applies to this selection.';
          el['result-json'].textContent = 'No verification for the current file selection.';
        }
        if (!file) { el['replay-file-note'].textContent = 'No ZIP selected.'; return; }
        if (!Number.isSafeInteger(file.size) || file.size < 1 || file.size > ZIP_LIMIT) throw new Error('Choose a nonempty ZIP within the 128 MiB browser limit.');
        state.replay = {name: String(file.name || 'audit.zip'), bytes: file.size, file};
        el['replay-file-note'].textContent = state.replay.name + ' · ' + state.replay.bytes + ' ZIP bytes selected for direct upload.';
        el['replay-status'].textContent = 'ZIP selected. Choose integrity-only or saved-state numerical verification.';
      });
    }
    async function plan() {
      if (active()) return false;
      return operation(async () => {
        if (!state.input) throw new Error('Choose the original observation JSON first.');
        const settings = config(); const key = signature(settings);
        state.plan = null;
        const body = {input_base64: state.input.base64, ...settings};
        const result = await request('/api/photometry-mc/plan', body);
        if (!result.request || !Array.isArray(result.request.nodes) || !result.summary) throw new Error('The server did not return a complete validated plan.');
        const planned = result.request.nodes;
        if (planned.length !== Object.values(settings.grids).reduce((total, values) => total + values.length, 0) ||
            new Set(planned.map(node => node && node.node_id)).size !== planned.length ||
            planned.some(node => !node || !Object.prototype.hasOwnProperty.call(settings.grids, node.parameter) ||
              !((typeof node.node_id === 'string' && node.node_id.length > 0) || Number.isSafeInteger(node.node_id)) ||
              !settings.grids[node.parameter].includes(node.value)) ||
            !/^[0-9a-f]{64}$/i.test(String(result.summary.input_utf8_sha256)) ||
            !/^[0-9a-f]{64}$/i.test(String(result.summary.canonical_input_sha256))) {
          throw new Error('The returned grid or input provenance does not match the requested plan.');
        }
        if (key !== signature(config())) throw new Error('Input changed while planning. Validate again.');
        state.plan = {body, signature: key, request: result.request, summary: result.summary};
        state.view = 'plan'; el['plan-details'].hidden = false;
        el['plan-json'].textContent = JSON.stringify({summary: result.summary, grids: settings.grids, entropy: settings.entropy,
          wall_seconds: settings.wall_seconds, max_saved_bytes: settings.max_saved_bytes,
          nodes: result.request.nodes.map(node => ({node_id: node.node_id, parameter: node.parameter, value: node.value,
            seed_slots: Array.isArray(node.all199_seed_slots) ? node.all199_seed_slots.length : 'Retained in the full request/export'})),
          evidence_scope: result.request.evidence_scope || result.summary.evidence_scope}, null, 2);
        el['plan-status'].textContent = 'Plan validated · ' + result.request.nodes.length + ' requested points · no analysis performed.';
        el['result-scope'].textContent = 'Validated plan only. Every listed point is not yet run; no calibration decision exists.';
        renderNodes(result.request.nodes, []); el['result-json'].textContent = 'No analysis has been run.';
      });
    }
    async function refreshStatus() {
      if (!state.jobId || state.pollBusy || state.disposed) return false;
      stopPoll(); state.pollBusy = true; updateButtons();
      const id = state.jobId; const watch = state.watch;
      try {
        const result = await request('/api/photometry-mc/jobs/' + encodeURIComponent(id));
        if (watch !== state.watch || id !== state.jobId || state.disposed) return false;
        if (!ACTIVE.has(result.status) && !TERMINAL.has(result.status)) throw new Error('The server returned an unknown job status. Existing records are retained.');
        state.jobStatus = result.status; state.snapshot = result; state.view = 'job';
        const item = state.history.get(id); item.status = result.status; item.snapshot = result;
        const progress = result.progress || {}; const summary = result.summary || {};
        el['job-title'].textContent = 'Job ' + id;
        el['job-status'].textContent = result.status + (state.cancelRequested && active() ? ' · cancellation requested, awaiting confirmation' : '');
        const completed = progress.completed_nodes; const total = progress.planned_nodes;
        el['node-progress'].textContent = text(completed) + ' / ' + text(total);
        el['fit-progress'].textContent = text(progress.committed_bootstrap_fits);
        el.stage.textContent = text(progress.current_node) + ' / ' + text(progress.stage);
        el.workspace.textContent = text(result.workspace_path);
        el['progress-bar'].hidden = false;
        if (Number.isInteger(total) && total > 0 && Number.isInteger(completed) && completed >= 0 && completed <= total) {
          el['progress-bar'].max = total; el['progress-bar'].value = completed;
        } else el['progress-bar'].removeAttribute('value');
        el['result-scope'].textContent = 'Job ' + id + ' · ' + result.status + '. Finite-grid, fitted-nuisance approximation; validation PENDING. ' + text(summary.evidence_scope || result.evidence_scope);
        renderNodes(item.plannedNodes, summary.nodes); el['result-json'].textContent = JSON.stringify(result, null, 2);
        history(); clearError();
        if (active()) state.pollTimer = later(() => refreshStatus(), 1000);
        return true;
      } catch (error) {
        if (watch === state.watch) {
          showError(error); el['job-status'].textContent = 'Status unavailable. The job may continue; retry status or request cancellation. Prior records remain retained.';
        }
        return false;
      } finally { state.pollBusy = false; updateButtons(); }
    }
    async function start() {
      if (active()) return false;
      const ok = await operation(async () => {
        if (!state.plan || state.plan.signature !== signature(config())) throw new Error('Validate the current input and configuration before starting.');
        const result = await request('/api/photometry-mc/start', state.plan.body);
        const id = safeJobId(result.job_id); stopPoll(); state.watch++;
        state.jobId = id; state.jobStatus = 'pending'; state.cancelRequested = false; state.view = 'job';
        state.history.set(id, {status: 'pending', plannedNodes: state.plan.request.nodes, snapshot: null}); history();
        el['job-title'].textContent = 'Job ' + id; el['job-status'].textContent = result.duplicate_prevented ? 'Existing matching job retained; fetching status.' : 'Job submitted; fetching status.';
        renderNodes(state.plan.request.nodes, []);
      });
      if (ok) await refreshStatus();
      return ok;
    }
    async function cancel() {
      if (!state.jobId || !active()) return false;
      const ok = await operation(async () => {
        await request('/api/photometry-mc/jobs/' + encodeURIComponent(state.jobId) + '/cancel', {});
        state.cancelRequested = true; el['job-status'].textContent = 'Cancellation requested; waiting for a terminal status. Committed records are retained.';
      }, true);
      if (ok) await refreshStatus();
      return ok;
    }
    function download(blob, filename) {
      if (deps.download) { deps.download(blob, filename); return; }
      const url = root.URL.createObjectURL(blob); const link = doc.createElement('a');
      link.href = url; link.download = filename; doc.body.append(link); link.click(); link.remove();
      later(() => root.URL.revokeObjectURL(url), 0);
    }
    async function exportJob() {
      if (state.view !== 'job' || !state.jobId || !TERMINAL.has(state.jobStatus)) return false;
      return operation(async () => {
        const blob = await request('/api/photometry-mc/jobs/' + encodeURIComponent(state.jobId) + '/export', {}, true);
        download(blob, 'BHSM_photometry_MC_' + state.jobId + '.zip');
      });
    }
    async function replay(mode) {
      if (mode !== 'integrity' && mode !== 'numerical') { showError(new Error('Choose an explicit replay mode.')); return false; }
      if (active()) return false;
      return operation(async () => {
        if (!state.replay) throw new Error('Choose a saved ZIP first.');
        const label = mode === 'integrity' ? 'Integrity-only verification' : 'Saved-state numerical replay';
        state.view = 'replay_unverified'; renderNodes([], []);
        el['result-scope'].textContent = label + ' · ' + state.replay.name + '. Request pending; no passed verification for this request.';
        el['result-json'].textContent = 'Verification pending for this request.';
        el['replay-status'].textContent = mode === 'integrity' ? 'Checking stored integrity; no numerical recomputation requested.' : 'Recomputing saved-state objectives and contrasts; no optimization requested.';
        try {
        if (state.replay.file.size !== state.replay.bytes) throw new Error('The selected ZIP byte count changed; select the file again.');
        const result = await request('/api/photometry-mc/replay-file?mode=' + mode, state.replay.file, false, 'application/zip');
        const responseMode = mode === 'integrity' ? 'INTEGRITY_ONLY' : 'NUMERICAL_SAVED_STATE_REPLAY';
        if (!result.verification || result.verification.mode !== responseMode || result.verification.requested_mode !== mode || typeof result.verification.passed !== 'boolean') throw new Error('The server did not return a verification for the requested mode.');
        state.view = 'replay';
        el['replay-status'].textContent = label + ': ' + (result.verification.passed ? 'checks passed' : 'failed or unresolved checks retained') + '. ' + text(result.verification.scope);
        el['result-scope'].textContent = label + ' · ' + state.replay.name + '. Validation remains PENDING; no optimization, continuous interval or coverage certification.';
        renderNodes([], result.summary && result.summary.nodes); el['result-json'].textContent = JSON.stringify(result, null, 2);
        if (!result.verification.passed) showError(new Error('Verification reported failed or unresolved checks. The full response remains visible.'));
        } catch (error) {
          const message = error && error.message ? error.message : String(error);
          el['replay-status'].textContent = label + ' unavailable or refused: ' + message;
          el['result-scope'].textContent = label + ' · ' + state.replay.name + '. No passed verification for this request. Prior local jobs remain in job history.';
          el['result-json'].textContent = JSON.stringify({status: 'REFUSED_OR_UNAVAILABLE', requested_mode: mode,
            file: state.replay.name, verification: null, error: message}, null, 2);
          throw error;
        }
      });
    }
    async function selectJob(id) {
      if (state.busy || state.pollBusy || active() || !state.history.has(id)) return false;
      stopPoll(); state.watch++; state.jobId = id; state.jobStatus = state.history.get(id).status; state.cancelRequested = false;
      return refreshStatus();
    }
    el.form.addEventListener('submit', event => { event.preventDefault(); return plan(); });
    el['input-file'].addEventListener('change', () => loadInput(el['input-file'].files[0] || null));
    el['replay-file'].addEventListener('change', () => loadReplay(el['replay-file'].files[0] || null));
    ['te-grid', 'u0-grid', 'entropy', 'wall'].forEach(name => el[name].addEventListener('input', dropPlan));
    el.start.addEventListener('click', start); el.cancel.addEventListener('click', cancel);
    el.refresh.addEventListener('click', refreshStatus); el.export.addEventListener('click', exportJob);
    el.integrity.addEventListener('click', () => replay('integrity')); el.numerical.addEventListener('click', () => replay('numerical'));
    el['job-history'].addEventListener('change', () => selectJob(el['job-history'].value));
    el['return-job'].addEventListener('click', refreshStatus); updateButtons();
    return Object.freeze({loadInput, loadReplay, plan, start, refreshStatus, cancel, exportJob, replay, selectJob,
      dispose() { state.disposed = true; state.watch++; stopPoll(); },
      snapshot() { return {jobId: state.jobId, jobStatus: state.jobStatus, hasInput: !!state.input, hasPlan: !!state.plan,
        inputBytes: state.input ? state.input.bytes : 0, replayBytes: state.replay ? state.replay.bytes : 0,
        view: state.view, rows: state.viewNodes, lastError: state.lastError, cancelRequested: state.cancelRequested}; }});
  }
  const api = Object.freeze({configuration, bytesToBase64, mergeNodes, probability, safeJobId, createApp, INPUT_LIMIT, ZIP_LIMIT});
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.BHSMPhotometryMC = api;
  if (root.document && root.document.getElementById('mc-form')) createApp();
})(typeof globalThis !== 'undefined' ? globalThis : this);
