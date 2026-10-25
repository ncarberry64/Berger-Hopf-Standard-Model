(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const state = {dataset: null, result: null, busy: false, job: null};
  const finite = x => typeof x === 'number' && Number.isFinite(x);
  const show = value => finite(value) ? new Intl.NumberFormat(undefined, {maximumSignificantDigits: 6}).format(value) : 'Unavailable';
  function error(e) { $('message').textContent = e.message || String(e); $('message').hidden = false; }
  function clearError() { $('message').hidden = true; }
  function busy(value) { state.busy = value; for (const field of document.querySelectorAll('#data-panel input, #data-panel select, #data-panel textarea, #model-panel input')) field.disabled = value; $('import').disabled = value; $('run').disabled = value || !state.dataset; }
  async function api(path, body, binary = false) {
    const response = await fetch(path, {method: body === undefined ? 'GET' : 'POST', cache: 'no-store', headers: body === undefined ? {} : {'Content-Type': 'application/json'}, body: body === undefined ? undefined : JSON.stringify(body)});
    if (!response.ok) { let message; try { message = (await response.json()).error; } catch { message = `Local request failed (${response.status}).`; } throw new Error(message); }
    return binary ? response.blob() : response.json();
  }
  function save(blob, name) { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); }
  function jsonFile(value, name) { save(new Blob([JSON.stringify(value, null, 2) + '\n'], {type: 'application/json'}), name); }
  function reset() { state.dataset = null; state.result = null; $('results').hidden = true; $('empty').hidden = false; $('input-details').hidden = true; $('data-badge').textContent = 'No validated data'; $('validation-state').textContent = 'Import again to validate the selected files and metadata.'; $('run').disabled = true; }
  function selected() {
    if ($('format').value === 'json') return [$('json-file').files[0]].filter(Boolean).map(file => ({file}));
    if ($('format').value === 'ogle3') return [$('ogle-file').files[0]].filter(Boolean).map(file => ({file}));
    return [{file: $('benchmark-ogle').files[0], instrument: 'OGLE'}, {file: $('benchmark-moa').files[0], instrument: 'MOA'}].filter(item => item.file);
  }
  function selectionChanged() { reset(); $('selected-files').textContent = selected().map(item => `${item.instrument ? item.instrument + ': ' : ''}${item.file.name} (${item.file.size.toLocaleString()} bytes)`).join('; ') || 'No files selected.'; }
  function formatChanged() { for (const [id, format] of [['ogle-input', 'ogle3'], ['benchmark-input', 'benchmark'], ['json-input', 'json']]) $(id).hidden = $('format').value !== format; selectionChanged(); }
  async function encoded(file) { const bytes = new Uint8Array(await file.arrayBuffer()); let binary = ''; for (let i = 0; i < bytes.length; i += 32768) binary += String.fromCharCode(...bytes.subarray(i, i + 32768)); return btoa(binary); }
  async function importData() {
    clearError(); busy(true);
    try {
      const files = selected(); if (!files.length) throw new Error('Choose at least one observation file.');
      let response, document;
      if ($('format').value === 'json') {
        if (files[0].file.size > 32000000) throw new Error('Unresolved JSON is limited to 32,000,000 bytes.');
        const text = await files[0].file.text();
        response = await api('/api/photometry/validate', {dataset_json: text}); document = JSON.parse(text);
      } else {
        if (files.reduce((sum, item) => sum + item.file.size, 0) > 24000000) throw new Error('Native files may total at most 24,000,000 bytes before encoding.');
        const metadata = $('metadata').value.trim() ? JSON.parse($('metadata').value) : {};
        const uploads = await Promise.all(files.map(async item => ({name: item.file.name, instrument: item.instrument, content_base64: await encoded(item.file)})));
        response = await api('/api/photometry/import', {format: $('format').value, files: uploads, metadata}); document = response.dataset;
      }
      state.dataset = document; state.result = null; $('results').hidden = true; $('empty').hidden = false;
      $('input-summary').textContent = JSON.stringify(response.summary, null, 2); $('input-details').hidden = false;
      $('input-details').open = true; $('data-badge').textContent = `${response.summary.rows.toLocaleString()} native rows`;
      $('validation-state').textContent = `Validated ${response.summary.schema}. Source row order and positive native errors retained. Review time conventions below.`;
    } catch (e) { reset(); error(e); } finally { busy(false); }
  }
  async function run() {
    clearError(); busy(true); $('retry').hidden = true;
    try {
      const options = {starts: Number($('starts').value), max_nfev: 1500, noise_scale: Number($('noise').value), equal_instrument_weight: $('equal-weight').checked, allow_negative_blend: $('signed-blend').checked};
      const job = await api('/api/photometry/fit', {dataset: state.dataset, options}); state.job = job.job_id;
      $('job-status').textContent = job.duplicate_prevented ? 'Existing matching job resumed.' : 'Queued locally. Every observation will be used.';
      await poll();
    } catch (e) { error(e); $('retry').hidden = !state.job; busy(false); }
  }
  async function poll() {
    while (state.job) {
      const item = await api(`/api/jobs/${state.job}`);
      if (item.status === 'complete') { state.result = item.result; state.dataset = item.result.dataset_input; state.job = null; $('job-status').textContent = 'Fit complete. Inspect all four assessment categories.'; render(); busy(false); return; }
      if (item.status === 'failed') { state.job = null; throw new Error(item.error || 'Fit failed; no inference is reported.'); }
      $('job-status').textContent = `${item.status === 'pending' ? 'Queued' : 'Running'} locally. Keep this page open; cancellation is unavailable.`;
      await new Promise(resolve => setTimeout(resolve, 700));
    }
  }
  function card(label, value) { const div = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd'); dt.textContent = label; dd.textContent = value; div.append(dt, dd); return div; }
  function render() {
    const r = state.result; $('empty').hidden = true; $('results').hidden = false; $('result-status').textContent = r.status.replaceAll('_', ' ');
    $('gates').replaceChildren(card('Numerical convergence', `Optimizer: ${r.numerical_convergence.optimizer_success}; multistart confirmed: ${r.numerical_convergence.multistart_confirmed}`), card('Photometric admission', r.physical_admission.status), card('Observational adequacy', r.observational_adequacy.status), card('Identification', `${r.uncertainty.rank} / ${r.uncertainty.parameter_count} locally identified combinations; mass unresolved`));
    const sigma = r.uncertainty.standard_errors;
    $('parameters').replaceChildren(card(`t0 · HJD − ${state.dataset.common_numeric_origin_jd} days`, `${show(r.parameters.t0)} ± ${show(sigma.t0)} (local curvature σ)`), card('Einstein crossing timescale · days', `${show(r.parameters.tE_days)} ± ${show(sigma.tE_days)} (local curvature σ)`), card('Impact parameter u0', `${show(r.parameters.u0)} ± ${show(sigma.u0)} (local curvature σ)`));
    $('identification').textContent = `Identified parameters: ${r.uncertainty.identified_parameters.join(', ')}. Unidentified: ${r.uncertainty.unidentified_parameters.join(', ') || 'none among the fitted photometric parameters'}. Local errors are conditional on this likelihood; they do not establish coverage or an angular trajectory.`;
    $('flags').textContent = `Flags: ${r.flags.join('; ') || 'No listed diagnostic flag'}. No observational black-hole discovery or follow-up probability is assigned by this app.`;
    $('diagnostics').textContent = JSON.stringify(r.diagnostics, null, 2); $('raw-result').textContent = JSON.stringify(r, null, 2);
    const measuredInstruments = new Set(state.dataset.rows.map(row => row.instrument));
    $('instrument').replaceChildren(...Object.keys(state.dataset.instruments).filter(name => measuredInstruments.has(name)).map(name => { const option = document.createElement('option'); option.value = name; option.textContent = name; return option; }));
    plots();
  }
  function plot(canvas, rows, values, predictions, label, reverse) {
    const width = Math.max(300, canvas.clientWidth || 700), height = canvas.id === 'lightcurve' ? 310 : 240, ratio = Math.max(1, window.devicePixelRatio || 1);
    canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio); const c = canvas.getContext('2d'); c.scale(ratio, ratio);
    const origin = state.dataset.common_numeric_origin_jd, instrument = $('instrument').value, timing = state.dataset.instruments[instrument].time;
    const times = rows.map(row => row.native_time + timing.numeric_origin_jd - origin);
    let xmin = Infinity, xmax = -Infinity, ymin = 0, ymax = 0;
    times.forEach(x => { xmin = Math.min(xmin, x); xmax = Math.max(xmax, x); });
    if (reverse) { ymin = Infinity; ymax = -Infinity; }
    values.concat(predictions || []).forEach(y => { ymin = Math.min(ymin, y); ymax = Math.max(ymax, y); });
    const dx = xmax - xmin || 1, dy = ymax - ymin || 1; xmin -= .025 * dx; xmax += .025 * dx; ymin -= .08 * dy; ymax += .08 * dy;
    const l = 65, right = width - 18, top = 18, bottom = height - 48;
    const x = t => l + (t - xmin) / (xmax - xmin) * (right - l), y = value => reverse ? top + (value - ymin) / (ymax - ymin) * (bottom - top) : bottom - (value - ymin) / (ymax - ymin) * (bottom - top);
    c.fillStyle = '#fff'; c.fillRect(0, 0, width, height); c.font = '10px sans-serif';
    for (let i = 0; i <= 4; i++) { const xv = xmin + (xmax - xmin) * i / 4, yv = ymin + (ymax - ymin) * i / 4; c.strokeStyle = '#e4ebee'; c.beginPath(); c.moveTo(x(xv), top); c.lineTo(x(xv), bottom); c.moveTo(l, y(yv)); c.lineTo(right, y(yv)); c.stroke(); c.fillStyle = '#596d7b'; c.textAlign = 'center'; c.fillText(show(xv), x(xv), bottom + 17); c.textAlign = 'right'; c.fillText(show(yv), l - 7, y(yv) + 3); }
    if (!reverse) { c.strokeStyle = '#8b9da8'; c.beginPath(); c.moveTo(l, y(0)); c.lineTo(right, y(0)); c.stroke(); }
    c.fillStyle = '#367ba5'; values.forEach((v, i) => { c.beginPath(); c.arc(x(times[i]), y(v), 1.7, 0, 2 * Math.PI); c.fill(); });
    if (predictions) { const order = times.map((_, i) => i).sort((a, b) => times[a] - times[b]); c.strokeStyle = '#be632b'; c.lineWidth = 1.4; c.beginPath(); order.forEach((i, k) => k ? c.lineTo(x(times[i]), y(predictions[i])) : c.moveTo(x(times[i]), y(predictions[i]))); c.stroke(); }
    c.fillStyle = '#405563'; c.textAlign = 'center'; c.fillText(`HJD − ${origin} · relative native days`, (l + right) / 2, height - 8); c.save(); c.translate(13, (top + bottom) / 2); c.rotate(-Math.PI / 2); c.fillText(label, 0, 0); c.restore();
  }
  function plots() {
    if (!state.result) return; const r = state.result, indices = [];
    state.dataset.rows.forEach((row, i) => { if (row.instrument === $('instrument').value) indices.push(i); });
    const rows = indices.map(i => state.dataset.rows[i]);
    plot($('lightcurve'), rows, rows.map(row => row.magnitude), indices.map(i => r.predictions_magnitude[i]), 'Native apparent magnitude', true);
    plot($('residuals'), rows, indices.map(i => r.standardized_residuals[i]), null, 'Residual / assumed native noise', false);
    $('plot-note').textContent = `${rows.length.toLocaleString()} / ${r.point_count.toLocaleString()} total native observations shown for ${$('instrument').value}; no rows excluded. Blue: native measurements. Orange: fitted model at every retained time. Magnitude increases downward. Source-row identities remain in the exported result/input.`;
  }
  $('format').addEventListener('change', formatChanged);
  for (const id of ['ogle-file', 'benchmark-ogle', 'benchmark-moa', 'json-file']) $(id).addEventListener('change', selectionChanged);
  $('metadata').addEventListener('input', reset);
  $('import').addEventListener('click', importData); $('run').addEventListener('click', run);
  $('retry').addEventListener('click', async () => { clearError(); busy(true); try { await poll(); $('retry').hidden = true; } catch (e) { error(e); busy(false); } });
  $('instrument').addEventListener('change', plots); window.addEventListener('resize', plots);
  $('download-input').addEventListener('click', () => jsonFile(state.dataset, 'Blackhole_Tracker_native_input.json'));
  $('export-json').addEventListener('click', () => jsonFile(state.result, 'Blackhole_Tracker_photometry_result.json'));
  $('export-bundle').addEventListener('click', async () => { try { save(await api('/api/export', {result: state.result}, true), 'Blackhole_Tracker_photometry_analysis.zip'); } catch (e) { error(e); } });
  $('export-report').addEventListener('click', async () => { try { const report = await api('/api/report', {result: state.result}); save(new Blob([report.html], {type: 'text/html'}), 'Blackhole_Tracker_photometry_report.html'); } catch (e) { error(e); } });
  api('/api/health').then(value => { $('version').textContent = `Research edition ${value.version}`; }).catch(error);
})();
