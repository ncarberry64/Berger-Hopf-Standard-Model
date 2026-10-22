(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const state = { dataset: null, validated: false, validating: false, loading: false, result: null, examples: [], busy: false,
    jobId: null, jobPhase: 'idle', polling: false, pollTimer: null, elapsedTimer: null, startedAt: null, toastTimer: null };
  const SVG = 'http://www.w3.org/2000/svg';
  const finite = value => typeof value === 'number' && Number.isFinite(value);
  const human = value => String(value ?? '').replaceAll('_', ' ').toLowerCase().replace(/^./, c => c.toUpperCase());
  const family = () => document.querySelector('input[name="family"]:checked').value;
  const configuration = () => ({ family: family(), nuisance: $('nuisance-select').value,
    starts: Math.max(1, Math.min(8, Math.round(Number($('fit-starts').value) || 2))) });

  function number(value, digits = 4) {
    if (!finite(value)) return 'Not available';
    if (value === 0) return '0';
    const absolute = Math.abs(value);
    if (absolute >= 1e6 || absolute < 1e-3) return value.toExponential(digits - 1);
    return new Intl.NumberFormat(undefined, { maximumSignificantDigits: digits }).format(value);
  }
  function vector(values) {
    if (!Array.isArray(values) || values.length < 2) return 'Not available';
    return `x ${number(values[0])} · y ${number(values[1])}`;
  }
  function uncertainty(value, units) {
    if (Array.isArray(value)) return `Local 1σ: x ${finite(value[0]) ? '± ' + number(value[0]) : 'unresolved'} · y ${finite(value[1]) ? '± ' + number(value[1]) : 'unresolved'} ${units}`;
    return finite(value) ? `± ${number(value)} ${units} · local 1σ` : 'Uncertainty not identified';
  }
  function showError(message) { $('global-message').textContent = message; $('global-message').hidden = false; }
  function clearError() { $('global-message').hidden = true; $('global-message').textContent = ''; }
  function toast(message) {
    clearTimeout(state.toastTimer); $('toast').textContent = message; $('toast').hidden = false;
    state.toastTimer = setTimeout(() => { $('toast').hidden = true; }, 4500);
  }
  async function api(path, body) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30000);
    try {
      const response = await fetch(path, { method: body === undefined ? 'GET' : 'POST',
        headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body), signal: controller.signal,
        cache: 'no-store' });
      let payload;
      try { payload = await response.json(); }
      catch { throw new Error(`The local server returned an unreadable response (${response.status}).`); }
      if (!response.ok || payload?.error) {
        const error = new Error(payload?.error || `Request failed (${response.status}).`);
        error.status = response.status; throw error;
      }
      return payload;
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('The local server did not respond within 30 seconds.');
      throw error;
    } finally { clearTimeout(timer); }
  }
  async function apiZip(path, body) {
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 30000);
    try {
      const response = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body), signal: controller.signal, cache: 'no-store' });
      const type = response.headers.get('Content-Type') || '';
      if (!response.ok || type.includes('json')) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || `Export failed (${response.status}).`);
      }
      if (!type.includes('zip') && !type.includes('octet-stream')) throw new Error('The server did not return a ZIP archive.');
      const blob = await response.blob(); if (!blob.size) throw new Error('The server returned an empty archive.');
      return blob;
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('The archive request did not respond within 30 seconds.');
      throw error;
    } finally { clearTimeout(timer); }
  }
  function syncControls() {
    const hasData = !!state.dataset;
    const locked = state.busy || state.validating || state.loading;
    $('load-example').disabled = locked || !state.examples.length;
    $('example-select').disabled = locked || !state.examples.length;
    $('file-input').disabled = locked;
    $('validate-data').disabled = locked || !hasData;
    $('run-fit').disabled = locked || !state.validated;
    $('clear-data').disabled = locked;
    $('source-json').disabled = locked || !hasData;
    $('copy-input').disabled = !hasData;
    $('download-input').disabled = !hasData;
    document.querySelectorAll('input[name="family"], #nuisance-select, #fit-starts').forEach(el => { el.disabled = locked; });
    $('run-fit').querySelector('span').textContent = state.busy ? 'Fit in progress…' : 'Run fit';
    $('r1-note').hidden = family() !== 'r1';
    $('job-help').hidden = !state.busy;
    $('model-selection-summary').textContent = `${family() === 'r1' ? 'Conditional R1 response selected' : 'Ordinary BHSM interpretation selected'} · ${$('nuisance-select').value === 'full' ? 'expanded environment and shape' : 'smooth tidal shear'}`;
    $('config-json').textContent = JSON.stringify(configuration(), null, 2);
  }
  function runMessage(message, busy = false) {
    $('run-state').textContent = message; $('run-state').classList.toggle('busy', busy);
  }
  function jobPhase(phase) {
    state.jobPhase = phase;
    const labels = { idle: 'Not started', pending: 'Pending', running: 'Running', complete: 'Completed', failed: 'Failed', interrupted: 'Connection interrupted' };
    $('job-status').textContent = labels[phase] || 'Status unavailable';
    $('job-status').className = `job-status ${phase}`;
  }
  function validationMessage(message, status = '') {
    const element = $('validation-state');
    element.className = `validation-state ${status}`;
    element.querySelector('.status-mark').textContent = status === 'success' ? '✓' : status === 'error' ? '!' : '○';
    element.querySelector('span:last-child').textContent = message;
    $('data-badge').className = `badge ${status || 'neutral'}`;
    $('data-badge').textContent = status === 'success' ? 'Validated' : status === 'error' ? 'Not valid' : state.dataset ? 'Needs validation' : 'No data';
  }
  function clearResults() {
    state.result = null;
    $('result-content').hidden = true; $('empty-results').hidden = false;
    $('raw-result-details').hidden = true; $('raw-result').textContent = '';
    $('empty-results').querySelector('h2').textContent = state.dataset ? 'Ready for inference.' : 'Start with the ordinary lens response.';
    $('empty-results').querySelector('.empty-footnote').textContent = state.dataset ? 'No completed fit for this input and configuration.' : 'No fit has been run. No example results are displayed.';
    if (!state.busy) jobPhase('idle');
    renderCalibrations();
  }
  function distance(value) {
    if (!finite(value)) return 'Not supplied';
    return value >= 1e6 ? `${number(value / 1e6)} Mpc` : value >= 1000 ? `${number(value / 1000)} kpc` : `${number(value)} pc`;
  }
  function renderCalibrations(model) {
    const raw = state.dataset, container = $('supplied-calibrations'), values = $('calibration-values'); values.replaceChildren();
    if (!raw) { container.hidden = true; $('input-provenance').hidden = true; return; }
    container.hidden = false;
    const g = raw.geometry || {}, a = raw.analysis || {}, kind = raw.provenance?.kind;
    $('input-provenance').hidden = false;
    $('input-provenance').textContent = kind === 'synthetic' ? 'SYNTHETIC INPUT · A demonstration, not an observed detection'
      : kind === 'observed' ? 'OBSERVED INPUT · Origin declared by the supplied metadata' : 'INPUT ORIGIN · Not declared';
    $('input-provenance').className = `input-provenance ${kind === 'synthetic' ? 'synthetic' : ''}`;
    $('calibrations-state').textContent = state.validated ? 'Supplied values · held fixed in the fit' : 'Supplied values · awaiting input validation';
    const radius = finite(a.r0_pc) ? `${distance(a.r0_pc)} · declared`
      : finite(model?.r0_pc) ? `${distance(model.r0_pc)} · model default` : 'Model default · computed after initialization';
    const entries = [['Lens distance', distance(g.D_l_pc)], ['Source distance', distance(g.D_s_pc)],
      ['Lens–source distance', distance(g.D_ls_pc)], ['Redshift · lens / source', `${number(g.z_l)} / ${number(g.z_s)}`],
      ['Reference observer epoch', `${number(raw.reference_epoch_yr, 8)} yr`], ['Boundary radius', radius],
      ['Observer correction', Array.isArray(a.lens_parallax_factors) ? 'Supplied parallax factors' : 'Zero parallax term assumed']];
    for (const [label, value] of entries) {
      const row = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
      dt.textContent = label; dd.textContent = value; row.append(dt, dd); values.append(row);
    }
  }
  function setDataset(dataset, name, sourceText) {
    if (!dataset || typeof dataset !== 'object' || Array.isArray(dataset)) throw new Error('The dataset must be a JSON object.');
    state.dataset = dataset; state.validated = false;
    clearResults(); clearError();
    // Preserve imported text until strict server validation: parsing and then
    // stringifying would silently erase duplicate JSON object keys.
    $('source-json').value = sourceText ?? JSON.stringify(dataset, null, 2);
    $('loaded-name').textContent = name || dataset.title || dataset.name || 'Imported dataset';
    $('loaded-file').hidden = false; $('dataset-summary').hidden = true;
    validationMessage('Input loaded. Validate its measurements, units and covariance.');
    renderCalibrations(); runMessage('Validate the dataset to enable the fit.'); syncControls();
  }
  function renderSummary(summary) {
    const container = $('dataset-summary'); container.replaceChildren();
    const entries = [
      ['Epochs / rows', summary?.rows ?? summary?.n_epochs ?? state.dataset?.epochs_yr?.length],
      ['Observer span', finite(summary?.span_observer_years) ? `${number(summary.span_observer_years)} yr` : null],
      ['Provenance', summary?.provenance?.kind ? human(summary.provenance.kind) : null],
      ['Covariance', summary?.covariance ? 'Validated full matrix' : null]
    ];
    for (const [label, value] of entries) {
      if (value === null || value === undefined) continue;
      const div = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
      dt.textContent = label; dd.textContent = value; div.append(dt, dd); container.append(div);
    }
    container.hidden = !container.children.length;
  }
  async function validateDataset() {
    if (!state.dataset || state.busy || state.validating || state.loading) return;
    clearError(); state.validated = false; state.validating = true; syncControls();
    validationMessage('Checking the dataset…');
    try {
      const source = $('source-json').value;
      if (new TextEncoder().encode(source).length > 8_000_000) throw new Error('The dataset exceeds 8 MB (8,000,000 bytes).');
      const parsed = JSON.parse(source);
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) throw new Error('The dataset must be a JSON object.');
      state.dataset = parsed;
      const response = await api('/api/validate', { dataset_json: source });
      if (!response.valid) throw new Error(response.message || 'The dataset did not pass validation.');
      state.validated = true;
      validationMessage('Measurements and covariance passed validation.', 'success');
      renderSummary(response.summary); renderCalibrations(); runMessage('Ready. Run the ordinary fit, or inspect advanced choices.');
    } catch (error) {
      validationMessage(error instanceof SyntaxError ? `Invalid JSON: ${error.message}` : error.message, 'error');
      $('dataset-summary').hidden = true; runMessage('Resolve the input error before fitting.');
    } finally {
      state.validating = false;
      if (state.validated) renderCalibrations();
      else { $('supplied-calibrations').hidden = true; $('input-provenance').hidden = true; }
      syncControls();
    }
  }
  async function loadExamples() {
    try {
      const examples = await api('/api/examples');
      if (!Array.isArray(examples)) throw new Error('The examples endpoint returned an invalid list.');
      state.examples = examples;
      $('example-select').replaceChildren();
      if (!examples.length) {
        const option = new Option('No built-in examples available', ''); $('example-select').append(option);
      } else {
        for (const example of examples) $('example-select').append(new Option(example.title || example.id, example.id));
        updateExampleDescription();
      }
    } catch (error) {
      $('example-select').replaceChildren(new Option('Examples unavailable', ''));
      $('example-description').textContent = `Could not load built-in examples: ${error.message}`;
    } finally { syncControls(); }
  }
  function updateExampleDescription() {
    const example = state.examples.find(item => String(item.id) === $('example-select').value);
    $('example-description').textContent = example?.description || '';
    const link = $('download-example-bundle');
    link.setAttribute('aria-disabled', example ? 'false' : 'true');
    if (example) link.href = `/api/examples/${encodeURIComponent(example.id)}/bundle`;
    else link.removeAttribute('href');
  }
  async function loadSelectedExample() {
    const id = $('example-select').value; if (!id || state.busy || state.loading) return;
    state.loading = true; syncControls(); clearError();
    try {
      const dataset = await api(`/api/examples/${encodeURIComponent(id)}`);
      const example = state.examples.find(item => String(item.id) === id);
      setDataset(dataset, example?.title || id);
    } catch (error) { showError(`Could not load the example: ${error.message}`); }
    finally { state.loading = false; syncControls(); }
  }
  function stopElapsed() { clearInterval(state.elapsedTimer); state.elapsedTimer = null; }
  function finishBusy() {
    state.busy = false; state.polling = false;
    stopElapsed(); clearTimeout(state.pollTimer); $('retry-job').hidden = true; syncControls();
  }
  async function submitFit() {
    if (!state.dataset || !state.validated || state.busy) return;
    clearError(); clearResults();
    state.busy = true; state.jobId = null; state.startedAt = Date.now(); syncControls();
    jobPhase('pending'); $('empty-results').querySelector('h2').textContent = 'Fit submitted.';
    $('empty-results').querySelector('.empty-footnote').textContent = 'The local server is fitting your dataset. Results appear only when the job completes.';
    runMessage('Submitting the fit…', true);
    state.elapsedTimer = setInterval(() => {
      if (state.polling) runMessage(`${state.jobPhase === 'pending' ? 'Waiting for the local worker' : 'Fitting ' + (family() === 'r1' ? 'the conditional R1 response' : 'the ordinary response')} · ${Math.floor((Date.now() - state.startedAt) / 1000)} s elapsed`, true);
    }, 1000);
    try {
      const response = await api('/api/fit', { dataset: state.dataset, ...configuration() });
      if (!response.job_id) throw new Error('The server did not return a fit job identifier.');
      state.jobId = response.job_id; state.polling = true; pollJob();
    } catch (error) {
      finishBusy(); jobPhase('failed'); showError(`The fit request failed: ${error.message}`);
      runMessage('Fit not started. Review the error and retry.');
      $('empty-results').querySelector('h2').textContent = 'No completed fit.';
      $('empty-results').querySelector('.empty-footnote').textContent = 'The server did not return a completed inference result.';
    }
  }
  async function pollJob() {
    if (!state.jobId) return;
    state.polling = true; $('retry-job').hidden = true;
    try {
      const job = await api(`/api/jobs/${encodeURIComponent(state.jobId)}`);
      if (job.status === 'complete') {
        if (!job.result || typeof job.result !== 'object') throw new Error('The completed job has no result object.');
        state.result = job.result; finishBusy(); jobPhase('complete'); renderResult();
        runMessage(`Complete${finite(job.result.runtime_seconds) ? ` · ${number(job.result.runtime_seconds, 3)} s` : ''}. Inspect fit status and admission before interpreting estimates.`);
        toast('Fit complete. Review the diagnostics.');
      } else if (job.status === 'failed') {
        finishBusy(); jobPhase('failed'); showError(`The fit failed: ${job.error || 'No error detail was provided.'}`);
        runMessage('Fit failed. No inference result is displayed.');
        $('empty-results').querySelector('h2').textContent = 'No completed fit.';
        $('empty-results').querySelector('.empty-footnote').textContent = 'The failed job returned no result. Review the message before retrying.';
      } else if (['running', 'queued', 'pending'].includes(job.status)) {
        const waiting = job.status !== 'running';
        jobPhase(waiting ? 'pending' : 'running');
        $('empty-results').querySelector('h2').textContent = waiting ? 'Waiting for the local worker.' : 'The fit is running.';
        runMessage(`${waiting ? 'Pending' : 'Running'} · ${Math.floor((Date.now() - state.startedAt) / 1000)} s elapsed`, true);
        state.pollTimer = setTimeout(pollJob, 1000);
      } else {
        throw new Error(`Unknown job status: ${String(job.status)}.`);
      }
    } catch (error) {
      if (error.status === 404) {
        clearResults(); state.jobId = null; finishBusy(); jobPhase('failed');
        showError('The local server no longer has this job. It may have restarted; the unfinished result cannot be recovered. Your input is retained and you can run the fit again.');
        runMessage('Job unavailable. Run the fit again or load another dataset.');
        $('empty-results').querySelector('h2').textContent = 'No completed fit.';
        $('empty-results').querySelector('.empty-footnote').textContent = 'The previous job is unavailable. No inference result is displayed.';
        return;
      }
      state.polling = false; stopElapsed();
      jobPhase('interrupted');
      showError(`Could not read the job status: ${error.message} The job may still be running on the local server. Use “Retry job status” to reconnect without starting another fit.`);
      runMessage('Status connection interrupted. The fit has not been declared failed.');
      $('retry-job').hidden = false;
    }
  }
  function renderResult() {
    const result = state.result; if (!result) return;
    clearError(); $('empty-results').hidden = true; $('result-content').hidden = false;
    const estimate = result.estimates || {}, sigma = result.uncertainty || {};
    $('mass-value').textContent = number(estimate.mass_msun);
    $('mass-uncertainty').textContent = uncertainty(sigma.mass_msun, 'M☉');
    $('center-value').textContent = vector(estimate.center_mas);
    $('center-uncertainty').textContent = uncertainty(sigma.center_mas, 'mas');
    $('motion-value').textContent = vector(estimate.proper_motion_mas_yr);
    $('motion-uncertainty').textContent = uncertainty(sigma.proper_motion_mas_yr, 'mas/yr');
    $('quality-value').textContent = finite(result.chi2) && finite(result.dof) ? `${number(result.chi2)} / ${number(result.dof)}` : 'Not available';
    const pValue = finite(result.goodness_of_fit_p) ? `p = ${number(result.goodness_of_fit_p, 3)}` : 'Goodness-of-fit probability unavailable';
    $('quality-detail').textContent = `${pValue}${result.optimizer_converged === false ? ' · optimizer not converged' : ''}`;
    const statuses = {
      TRACKED: ['success', 'The fitted motion meets the declared tracking criterion within this model and calibration.'],
      PARTIALLY_IDENTIFIED: ['warning', 'Motion is unresolved or a model bound qualifies this fit. Some quantities can remain informative; inspect the qualifications.'],
      INSUFFICIENT_INFORMATION: ['warning', 'The data do not identify the requested track. Point estimates are shown for audit; null uncertainties are unresolved, not zero.'],
      FIT_REJECTED: ['error', 'The fit did not pass its admission checks. Displayed estimates are diagnostic and do not establish a valid track.']
    };
    const [tone, description] = statuses[result.status] || ['neutral', 'Review the complete diagnostics and model assumptions.'];
    $('result-status-label').className = `badge ${tone}`;
    $('result-status-label').textContent = human(result.status || 'Status not provided');
    $('result-status-description').textContent = description;
    renderOutcome(result); renderCalibrations(result.model);
    renderModelContext(result.model);
    renderBHSMInterpretation(result.bhsm_interpretation, result.model);
    renderEnvelope(result.conditional_envelope); renderDiagnostics(result.diagnostics);
    $('envelope-panel').hidden = result.model?.family !== 'r1';
    renderCorrelations(result);
    $('raw-result-details').hidden = false; $('raw-result').textContent = JSON.stringify(result, null, 2);
    renderCharts();
  }
  function renderOutcome(result) {
    const provenance = result.data_summary?.provenance || state.dataset?.provenance || {};
    $('result-provenance').textContent = provenance.kind === 'synthetic'
      ? 'SYNTHETIC RESULT · Recovery of a simulated input, not an observed detection'
      : provenance.kind === 'observed' ? 'DECLARED OBSERVED INPUT · Interpret with its reduction and calibration' : 'Input provenance unavailable';
    const n = result.epochs_yr?.length || state.dataset?.epochs_yr?.length || 0;
    $('answer-supplied').textContent = `${n} rows and full covariance; distances, redshifts, clock and frame held fixed.`;
    $('answer-fitted').textContent = 'Mass, reference location and motion; background-source positions and the selected environment.';
    const answers = { TRACKED: 'Mass and a supported motion track within the declared model.',
      PARTIALLY_IDENTIFIED: 'Some quantities remain unresolved or limited by modeling bounds.',
      INSUFFICIENT_INFORMATION: 'Mass information is insufficient for a supported track.',
      FIT_REJECTED: 'Rejected model fit. Displayed parameter values are diagnostic only.' };
    $('answer-support').textContent = answers[result.status] || 'Review the recorded checks before using any estimate.';
    $('result-status-label').textContent = result.status === 'TRACKED' ? 'Supported track'
      : result.status === 'PARTIALLY_IDENTIFIED' ? 'Partly constrained'
      : result.status === 'INSUFFICIENT_INFORMATION' ? 'Unresolved' : result.status === 'FIT_REJECTED' ? 'Rejected' : human(result.status);
  }
  function renderModelContext(model) {
    const container = $('model-context'); container.replaceChildren();
    if (!model || model.family !== 'r1') { container.hidden = true; return; }
    const treatments = {
      fixed_regular_body_proxy: 'Fixed regular-body flux proxy',
      fitted_conditional_flux: 'Fitted conditional scalar flux'
    };
    const label = document.createElement('span'); label.className = 'model-context-label'; label.textContent = 'FLUX TREATMENT';
    const value = document.createElement('strong');
    value.textContent = treatments[model.flux_policy] || (model.flux_policy ? human(model.flux_policy) : 'Not specified in this result');
    container.append(label, value); container.hidden = false;
  }
  function renderBHSMInterpretation(interpretation, model) {
    const dictionary = $('bhsm-parameter-dictionary'); dictionary.replaceChildren();
    const available = interpretation && typeof interpretation === 'object';
    $('bhsm-one-potential').textContent = available && typeof interpretation.one_potential_rule === 'string'
      ? interpretation.one_potential_rule
      : 'Equivalent gravity and envelope descriptions represent one fitted optical potential and are counted once.';
    $('bhsm-inference-scope').textContent = available && typeof interpretation.inference_scope === 'string'
      ? interpretation.inference_scope
      : 'This result has no structured interpretation record. Its compact-lens estimates remain available; rerun the fit to record their BHSM interpretation.';
    $('bhsm-model-role').textContent = available && typeof interpretation.model_role === 'string' ? interpretation.model_role : '';
    const meanings = available && Array.isArray(interpretation.parameter_meanings) ? interpretation.parameter_meanings : [];
    for (const entry of meanings) {
      if (!entry || typeof entry !== 'object') continue;
      const row = document.createElement('div'), term = document.createElement('dt'), definition = document.createElement('dd');
      term.textContent = String(entry.parameter || 'Model parameter');
      const meaning = document.createElement('p');
      meaning.textContent = typeof entry.interpretation === 'string' ? entry.interpretation : '';
      definition.append(meaning);
      if (typeof entry.qualification === 'string' && entry.qualification) {
        const qualification = document.createElement('p'); qualification.className = 'dictionary-qualification';
        qualification.textContent = entry.qualification; definition.append(qualification);
      }
      row.append(term, definition); dictionary.append(row);
    }
    $('bhsm-conditional-extension').textContent = available && typeof interpretation.conditional_extension === 'string' ? interpretation.conditional_extension : '';
    const weyl = available && typeof interpretation.weyl_convention === 'string' ? interpretation.weyl_convention : '';
    $('bhsm-weyl-convention').textContent = weyl; $('bhsm-weyl-convention').hidden = !weyl;
    $('bhsm-dictionary-details').hidden = !available;
    const radius = finite(model?.r0_pc) ? distance(model.r0_pc) : 'not supplied';
    $('boundary-choice-summary').textContent = `Derived boundary quantities use an enclosing radius of ${radius}${model?.worldtube_policy === 'supplied' ? ' · declared and fixed' : ' · model default'}. This is not a measured hard-boundary or horizon radius.`;
    renderSphericalBoundary(available ? interpretation.spherical_boundary : null, model);
    renderCoreSurface(available ? interpretation.core_surface : null, available ? interpretation.source_provenance : null);
  }
  function renderCoreSurface(context, provenance) {
    $('bhsm-core-surface-summary')?.remove();
    $('bhsm-core-surface-details')?.remove();
    if (!context || typeof context !== 'object') return;
    const anchor = $('boundary-choice-summary'), panel = anchor?.parentElement;
    if (!panel) return;
    const summary = document.createElement('div'); summary.id = 'bhsm-core-surface-summary';
    const labels = [['Spacetime-side surface', context.surface_summary], ['Core', context.core_summary]];
    for (const [label, text] of labels) {
      if (typeof text !== 'string' || !text) continue;
      const paragraph = document.createElement('p'), heading = document.createElement('strong');
      paragraph.className = 'interpretation-scope'; heading.textContent = `${label}: `;
      paragraph.append(heading, document.createTextNode(text)); summary.append(paragraph);
    }
    if (summary.childElementCount) {
      const qualification = document.createElement('p'); qualification.className = 'field-help';
      qualification.textContent = 'Proposed BHSM interpretation · not a classification measured by this lens fit.';
      summary.append(qualification); panel.insertBefore(summary, anchor);
    }
    const details = document.createElement('details'); details.id = 'bhsm-core-surface-details';
    details.className = 'interpretation-dictionary';
    const title = document.createElement('summary'); title.textContent = 'BHSM surface/core theory and provenance'; details.append(title);
    function paragraph(text) {
      if (typeof text !== 'string' || !text) return;
      const element = document.createElement('p'); element.textContent = text; details.append(element);
    }
    paragraph(context.attribution);
    paragraph(context.matching_summary);
    paragraph(context.inference_scope);
    const ledger = document.createElement('dl');
    for (const entry of Array.isArray(context.claim_ledger) ? context.claim_ledger : []) {
      if (!entry || typeof entry !== 'object' || typeof entry.statement !== 'string') continue;
      const row = document.createElement('div'), label = document.createElement('dt'), content = document.createElement('dd');
      label.textContent = typeof entry.label === 'string' ? entry.label : 'Theory statement';
      const statement = document.createElement('p'); statement.textContent = entry.statement; content.append(statement);
      if (typeof entry.status === 'string' && entry.status) {
        const status = document.createElement('p'); status.className = 'dictionary-qualification';
        status.textContent = `Scope: ${human(entry.status)}.`; content.append(status);
      }
      if (Array.isArray(entry.source_refs) && entry.source_refs.length) {
        const sources = document.createElement('p'); sources.className = 'dictionary-qualification';
        sources.textContent = `Source references: ${entry.source_refs.filter(value => typeof value === 'string').join('; ')}`; content.append(sources);
      }
      row.append(label, content); ledger.append(row);
    }
    if (ledger.childElementCount) details.append(ledger);
    if (provenance && typeof provenance === 'object') {
      const sourceDetails = document.createElement('details'), sourceTitle = document.createElement('summary'), sourceRecord = document.createElement('pre');
      sourceTitle.textContent = 'Versioned source record'; sourceRecord.className = 'admission-details';
      sourceRecord.textContent = JSON.stringify(provenance, null, 2); sourceDetails.append(sourceTitle, sourceRecord); details.append(sourceDetails);
    }
    panel.insertBefore(details, $('bhsm-dictionary-details'));
  }
  function renderSphericalBoundary(boundary, model) {
    const container = $('bhsm-spherical-boundary'); container.replaceChildren();
    if (!boundary || typeof boundary !== 'object') { container.hidden = true; return; }
    container.hidden = false;
    if (boundary.status !== 'AVAILABLE') {
      const note = document.createElement('p'); note.className = 'boundary-unavailable';
      note.textContent = typeof boundary.reason === 'string' ? boundary.reason
        : boundary.status === 'NOT_REPORTED_FOR_REJECTED_FIT' ? 'A spherical boundary value is not reported for a rejected fit.'
        : boundary.status === 'NOT_REPORTED_FOR_UNRESOLVED_MASS' ? 'The mass is unresolved, so a spherical boundary value is not reported.'
        : 'A spherical boundary representation was not evaluated for this result.';
      container.append(note); return;
    }
    const heading = document.createElement('h4'); heading.textContent = 'Spherical boundary representation';
    const radius = document.createElement('p'); radius.className = 'boundary-radius';
    const supplied = model?.worldtube_policy === 'supplied';
    radius.textContent = `${supplied ? 'Declared representation radius' : 'Model representation radius'}: ${number(boundary.radius_pc)} pc · fixed for these derived values`;
    container.append(heading, radius);
    if (!supplied) {
      const choice = document.createElement('p'); choice.className = 'boundary-radius-policy';
      choice.textContent = model?.worldtube_policy
        ? `Radius policy: ${model.worldtube_policy}. The radius is not measured by this fit.`
        : 'The radius comes from the model configuration and is not measured by this fit.';
      container.append(choice);
    }
    const cards = document.createElement('div'); cards.className = 'boundary-measures';
    for (const [label, value, sigma, units] of [
      ['Curvature deficit δk', boundary.curvature_deficit_pc_inverse, boundary.curvature_deficit_sigma_pc_inverse, 'pc⁻¹'],
      ['Boundary energy E / c²', boundary.boundary_energy_over_Msun_c2, boundary.boundary_energy_sigma_over_Msun_c2, 'M☉']
    ]) {
      const card = document.createElement('div'), title = document.createElement('div'), estimate = document.createElement('strong'), error = document.createElement('p');
      card.className = 'boundary-measure'; title.className = 'boundary-measure-label'; title.textContent = label;
      estimate.textContent = `${number(value)} ${units}`; error.textContent = uncertainty(sigma, units);
      card.append(title, estimate, error); cards.append(card);
    }
    container.append(cards);
    for (const text of [boundary.geometry, boundary.qualification]) {
      if (typeof text !== 'string' || !text) continue;
      const note = document.createElement('p'); note.className = 'boundary-qualification'; note.textContent = text; container.append(note);
    }
  }
  function renderEnvelope(envelope) {
    const status = envelope?.status || 'NOT_REQUESTED';
    $('envelope-status').textContent = human(status);
    const container = $('envelope-detail'); container.replaceChildren();
    if (!envelope || status === 'NOT_REQUESTED') {
      const p = document.createElement('p'); p.className = 'field-help';
      p.textContent = 'No conditional envelope was requested for this fit.'; container.append(p); return;
    }
    const description = document.createElement('p'); description.className = 'field-help';
    description.textContent = status === 'NOT_EVALUATED'
      ? 'Envelope information was not evaluated because the baseline fit did not pass its checks.'
      : status === 'NOT_ADMITTED'
      ? 'This response is outside the model’s admitted approximation domain for the supplied configuration.'
      : 'Sensitivity is assessed only for boundary states inside the declared model-admission bound.';
    container.append(description);
    if (['NOT_ADMITTED', 'NOT_EVALUATED'].includes(status) && Array.isArray(envelope.reasons)) {
      for (const reason of envelope.reasons) {
        const p = document.createElement('p'); p.className = 'envelope-explanation';
        p.textContent = typeof reason === 'string' ? reason : reason.message || JSON.stringify(reason);
        container.append(p);
      }
    }
    const cards = document.createElement('div'); cards.className = 'envelope-measures';
    function card(label, value, detail, wide = false) {
      const article = document.createElement('div'); article.className = `envelope-measure${wide ? ' wide' : ''}`;
      const heading = document.createElement('div'), number = document.createElement('strong'), explanation = document.createElement('p');
      heading.className = 'envelope-measure-label'; heading.textContent = label;
      number.textContent = value; explanation.textContent = detail;
      article.append(heading, number, explanation); cards.append(article);
    }
    if (finite(envelope.boundary_amplitude_cap)) card('Admitted boundary norm', `≤ ${number(envelope.boundary_amplitude_cap, 3)}`,
      'Sufficient bound on the normalized scalar state. This is not a predicted astrophysical amplitude.');
    if (finite(envelope.maximum_admitted_local_snr)) card('Largest admitted local SNR', number(envelope.maximum_admitted_local_snr, 3),
      'Largest local signal-to-noise ratio after source and lens freedoms are profiled.');
    if (envelope.all_admitted_states_below_unit_snr === true) {
      card('Do the data resolve admitted states?', 'No',
        'Every state inside the stated norm bound remains below unit local SNR for this covariance.', true);
    } else if (status === 'UNRESOLVED') {
      card('Do the data resolve admitted states?', 'Not established',
        'The analysis does not resolve all conditional envelope directions within the declared model.', true);
    } else if (status === 'INFORMATION_AVAILABLE') {
      card('Do the data resolve admitted states?', 'Local sensitivity available',
        'The model retains conditional response information. This is a sensitivity result, not a deformation detection.', true);
    }
    if (cards.children.length) container.append(cards);
    if (envelope.unconstrained_estimate_inside_admitted_ball === false) {
      const note = document.createElement('div'); note.className = 'envelope-domain-note';
      const title = document.createElement('strong'), body = document.createElement('p');
      title.textContent = 'Unconstrained estimate outside the admitted domain';
      body.textContent = 'That unrestricted fit value is not a physical boundary-state measurement. It must not be interpreted as a detected deformation.';
      note.append(title, body); container.append(note);
    }
    const technical = document.createElement('details'); technical.className = 'envelope-technical';
    const summary = document.createElement('summary'); summary.textContent = 'Technical admission details';
    const pre = document.createElement('pre'); pre.className = 'admission-details'; pre.textContent = JSON.stringify(envelope, null, 2);
    technical.append(summary, pre); container.append(technical);
  }
  function renderDiagnostics(diagnostics) {
    const container = $('diagnostics-list'); container.replaceChildren();
    const list = Array.isArray(diagnostics) ? diagnostics : [];
    if (!list.length) {
      const p = document.createElement('p'); p.className = 'field-help'; p.textContent = 'The server supplied no additional diagnostics.'; container.append(p); return;
    }
    for (const item of list) {
      const level = ['warning', 'error'].includes(item.level) ? item.level : 'info';
      const row = document.createElement('div'); row.className = `diagnostic ${level}`;
      const icon = document.createElement('span'); icon.className = 'diagnostic-icon'; icon.textContent = level === 'info' ? 'i' : '!'; icon.setAttribute('aria-label', level);
      const body = document.createElement('div'), code = document.createElement('div'), message = document.createElement('p');
      const labels = { COMPACT_EXTERIOR_ONLY: 'Exterior interpretation', SYNTHETIC_DATA: 'Synthetic measurements',
        FIT_REJECTED: 'Fit rejected', MOTION_UNRESOLVED: 'Motion unresolved', PARAMETER_NULLS: 'Unresolved combinations',
        BOUND_ACTIVE: 'Model bound active', PHYSICAL_DOMAIN: 'Outside the model domain', R1_DOMAIN: 'Outside the conditional R1 domain', CONDITIONAL_FLUX: 'Conditional scalar-flux assumption' };
      code.className = 'diagnostic-code'; code.textContent = labels[item.code] || human(item.code || level); message.textContent = item.message || '';
      body.append(code, message); row.append(icon, body); container.append(row);
    }
  }
  function renderCorrelations(result) {
    function strongest(matrix, labels, omitted = []) {
      if (!Array.isArray(matrix)) return [];
      const pairs = [];
      for (let i = 0; i < labels.length; i++) for (let j = i + 1; j < labels.length; j++) {
        if (omitted[i] || omitted[j]) continue;
        const vi = matrix[i]?.[i], vj = matrix[j]?.[j], cross = matrix[i]?.[j];
        if (!finite(vi) || !finite(vj) || !finite(cross) || vi <= 0 || vj <= 0) continue;
        const rho = Math.max(-1, Math.min(1, cross / Math.sqrt(vi * vj)));
        if (Math.abs(rho) > 1e-6) pairs.push({ label: `${labels[i]} ↔ ${labels[j]}`, rho });
      }
      return pairs.sort((a, b) => Math.abs(b.rho) - Math.abs(a.rho)).slice(0, 4);
    }
    function show(container, pairs, empty) {
      container.replaceChildren();
      if (!pairs.length) { const p = document.createElement('p'); p.className = 'correlation-note'; p.textContent = empty; container.append(p); return; }
      for (const pair of pairs) {
        const row = document.createElement('div'), label = document.createElement('span'), value = document.createElement('strong'), bar = document.createElement('div'), fill = document.createElement('span');
        row.className = 'correlation-row'; label.textContent = pair.label; value.textContent = `${pair.rho >= 0 ? '+' : ''}${number(pair.rho, 3)}`;
        bar.className = 'correlation-bar'; fill.style.width = `${Math.abs(pair.rho) * 100}%`; bar.append(fill); row.append(label, value, bar); container.append(row);
      }
    }
    const fields = ['positive image x', 'positive image y', 'negative image x', 'negative image y', 'log flux ratio', 'delay'];
    const C = covariance(), measurementLabels = Array.from({ length: C.length }, (_, i) => `Row ${Math.floor(i / 6) + 1} ${fields[i % 6]}`);
    show($('measurement-correlations'), strongest(C, measurementLabels), 'No nonzero off-diagonal correlations are present in the supplied matrix.');
    const names = result.model?.fitted_parameters || [], internal = result._internal || {};
    const meanings = { log_mass: 'Mass', center_x: 'Center x', center_y: 'Center y', motion_x: 'Motion x', motion_y: 'Motion y',
      shear_plus: 'Tidal shear 1', shear_cross: 'Tidal shear 2', compact_plus: 'Compact shape 1', compact_cross: 'Compact shape 2', convergence: 'Environmental focusing', log_flux: 'Scalar flux' };
    const indices = names.map((name, i) => meanings[name] ? i : -1).filter(i => i >= 0);
    const pcov = indices.map(i => indices.map(j => internal.covariance?.[i]?.[j]));
    const omitted = indices.map(i => internal.unidentified?.[i] === true);
    show($('parameter-correlations'), strongest(pcov, indices.map(i => meanings[names[i]]), omitted),
      'No resolved nonzero correlations are available for the displayed lens parameters. Unidentified directions are excluded.');
  }
  function renderWhitenedResiduals() {
    const container = $('whitened-residual-chart'), residuals = state.result?.whitened_residuals;
    if (!Array.isArray(residuals) || !residuals.length || residuals.some(value => !finite(value))) {
      chartEmpty(container, 'Whitened residuals were not supplied for this fit.'); return;
    }
    const frame = plotFrame(container, 'Residuals whitened by the complete supplied covariance',
      [-.5, residuals.length - .5], extent([0, ...residuals]), 'Whitened component', 'Residual / supplied noise', false, 230);
    line(frame, [[-.5, 0], [residuals.length - .5, 0]], '#8b9da8', '4 3');
    residuals.forEach((value, i) => {
      frame.svg.append(svgElement('line', { x1: frame.x(i), x2: frame.x(i), y1: frame.y(0), y2: frame.y(value), stroke: '#9eb7c3', 'stroke-width': 1 }));
      marker(frame, i, value, { radius: 2.7, label: `Whitened component ${i + 1}: ${number(value)} supplied-noise units` });
    });
  }

  function svgElement(tag, attributes = {}, text) {
    const element = document.createElementNS(SVG, tag);
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    if (text !== undefined) element.textContent = text;
    return element;
  }
  function extent(values) {
    const valid = values.filter(finite); if (!valid.length) return [-1, 1];
    let lo = Math.min(...valid), hi = Math.max(...valid);
    const span = hi - lo || Math.max(Math.abs(lo) * .15, .01);
    return [lo - .12 * span, hi + .12 * span];
  }
  function tick(value) {
    if (value === 0 || Math.abs(value) < 1e-13) return '0';
    const abs = Math.abs(value);
    return abs >= 1e4 || abs < .001 ? value.toExponential(1) : String(Number(value.toPrecision(4)));
  }
  function plotFrame(container, title, xExtent, yExtent, xLabel, yLabel, equalAspect = false, height = 300) {
    container.replaceChildren();
    const width = Math.max(340, container.clientWidth || 600);
    const margin = { l: 66, r: 20, t: 18, b: 47 }, pw = width - margin.l - margin.r, ph = height - margin.t - margin.b;
    let [xmin, xmax] = xExtent, [ymin, ymax] = yExtent;
    if (equalAspect) {
      const unit = Math.max((xmax - xmin) / pw, (ymax - ymin) / ph), cx = (xmin + xmax) / 2, cy = (ymin + ymax) / 2;
      xmin = cx - unit * pw / 2; xmax = cx + unit * pw / 2; ymin = cy - unit * ph / 2; ymax = cy + unit * ph / 2;
    }
    const x = value => margin.l + (value - xmin) / (xmax - xmin) * pw;
    const y = value => margin.t + ph - (value - ymin) / (ymax - ymin) * ph;
    const svg = svgElement('svg', { viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': title });
    svg.append(svgElement('title', {}, title));
    const count = width < 470 ? 4 : 5;
    for (let i = 0; i <= count; i++) {
      const xv = xmin + (xmax - xmin) * i / count, yv = ymin + (ymax - ymin) * i / count;
      svg.append(svgElement('line', { x1: x(xv), x2: x(xv), y1: margin.t, y2: margin.t + ph, stroke: '#e4ebee', 'stroke-width': 1 }));
      svg.append(svgElement('line', { x1: margin.l, x2: margin.l + pw, y1: y(yv), y2: y(yv), stroke: '#e4ebee', 'stroke-width': 1 }));
      svg.append(svgElement('text', { x: x(xv), y: height - 27, 'text-anchor': 'middle', fill: '#627987', 'font-family': 'Consolas,monospace', 'font-size': 10 }, tick(xv)));
      svg.append(svgElement('text', { x: margin.l - 9, y: y(yv) + 3, 'text-anchor': 'end', fill: '#627987', 'font-family': 'Consolas,monospace', 'font-size': 10 }, tick(yv)));
    }
    svg.append(svgElement('text', { x: margin.l + pw / 2, y: height - 5, 'text-anchor': 'middle', fill: '#526c7b', 'font-size': 11 }, xLabel));
    svg.append(svgElement('text', { transform: `translate(13 ${margin.t + ph / 2}) rotate(-90)`, 'text-anchor': 'middle', fill: '#526c7b', 'font-size': 11 }, yLabel));
    container.append(svg);
    return { svg, x, y, width, height };
  }
  function line(frame, points, color = '#007f93', dash = '') {
    const valid = points.filter(p => p.every(finite)); if (!valid.length) return;
    const path = valid.map((point, i) => `${i ? 'L' : 'M'}${frame.x(point[0])},${frame.y(point[1])}`).join(' ');
    const attributes = { d: path, fill: 'none', stroke: color, 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
    if (dash) attributes['stroke-dasharray'] = dash;
    frame.svg.append(svgElement('path', attributes));
  }
  function marker(frame, xValue, yValue, options = {}) {
    if (!finite(xValue) || !finite(yValue)) return;
    const point = svgElement('circle', { cx: frame.x(xValue), cy: frame.y(yValue), r: options.radius || 3.2,
      fill: options.hollow ? '#fff' : '#172d3c', stroke: options.color || '#172d3c', 'stroke-width': 1.2 });
    if (options.label) point.append(svgElement('title', {}, options.label));
    frame.svg.append(point);
  }
  function errorBar(frame, xValue, yValue, sx, sy, color = '#849ca9') {
    const attributes = { stroke: color, 'stroke-width': 1, opacity: .65 };
    const x = frame.x(xValue), y = frame.y(yValue);
    if (finite(sx) && sx >= 0) {
      const left = frame.x(xValue - sx), right = frame.x(xValue + sx);
      frame.svg.append(svgElement('line', { ...attributes, x1: left, x2: right, y1: y, y2: y }));
      frame.svg.append(svgElement('line', { ...attributes, x1: left, x2: left, y1: y - 2, y2: y + 2 }));
      frame.svg.append(svgElement('line', { ...attributes, x1: right, x2: right, y1: y - 2, y2: y + 2 }));
    }
    if (finite(sy) && sy >= 0) {
      const top = frame.y(yValue + sy), bottom = frame.y(yValue - sy);
      frame.svg.append(svgElement('line', { ...attributes, x1: x, x2: x, y1: top, y2: bottom }));
      frame.svg.append(svgElement('line', { ...attributes, x1: x - 2, x2: x + 2, y1: top, y2: top }));
      frame.svg.append(svgElement('line', { ...attributes, x1: x - 2, x2: x + 2, y1: bottom, y2: bottom }));
    }
  }
  function chartEmpty(container, message) { container.replaceChildren(); const p = document.createElement('div'); p.className = 'chart-empty'; p.textContent = message; container.append(p); }
  function rows() {
    const result = state.result || {};
    return { observed: Array.isArray(result.observations) ? result.observations : [],
      predicted: Array.isArray(result.predictions) ? result.predictions : [],
      epochs: Array.isArray(result.epochs_yr) ? result.epochs_yr : [] };
  }
  function covariance() { return state.result?.covariance || state.dataset?.covariance || []; }
  function blockCovariance(index) {
    const full = covariance(), offset = index * 6;
    if (!Array.isArray(full) || !Array.isArray(full[offset]) || full[offset].length < offset + 6) return null;
    return Array.from({ length: 6 }, (_, i) => full[offset + i]?.slice(offset, offset + 6));
  }
  function variance(row, cov) {
    if (!cov || cov.some(r => !Array.isArray(r) || r.length < 6)) return null;
    let value = 0;
    for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) {
      if (!finite(cov[i][j])) return null; value += row[i] * cov[i][j] * row[j];
    }
    return value >= -1e-16 ? Math.sqrt(Math.max(0, value)) : null;
  }
  function pairCenter(row, index) {
    if (!Array.isArray(row) || row.slice(0, 5).some(value => !finite(value))) return null;
    const k = Math.exp(row[4] / 2); if (!finite(k)) return null;
    const wp = 1 / (1 + k), wm = k / (1 + k);
    const point = [wp * row[0] + wm * row[2], wp * row[1] + wm * row[3]];
    const jx = [wp, 0, wm, 0, .5 * k * (row[2] - row[0]) / (1 + k) ** 2, 0];
    const jy = [0, wp, 0, wm, .5 * k * (row[3] - row[1]) / (1 + k) ** 2, 0];
    const cov = blockCovariance(index);
    return { point, sigma: [variance(jx, cov), variance(jy, cov)], index };
  }
  function renderTrack() {
    const container = $('track-chart'), { observed, predicted, epochs } = rows();
    const track = state.result?.center_track_mas;
    const trackSigma = state.result?.center_track_sigma_mas || [];
    const legend = container.closest('.chart-panel').querySelector('.plot-legend');
    function setLegend(observedLabel, fittedLabel) {
      const first = document.createElement('span'), second = document.createElement('span');
      const dot = document.createElement('i'), stroke = document.createElement('i');
      dot.className = 'legend-dot'; stroke.className = 'legend-line';
      first.append(dot, document.createTextNode(observedLabel)); second.append(stroke, document.createTextNode(fittedLabel));
      legend.replaceChildren(first, second);
    }
    if (Array.isArray(track) && track.length && track.every(p => Array.isArray(p) && p.length >= 2 && p.slice(0, 2).every(finite))) {
      setLegend('GR pair diagnostic', 'Fitted center');
      const measured = observed.map(pairCenter).filter(Boolean);
      const xs = [], ys = [];
      track.forEach((p, i) => { xs.push(p[0]); ys.push(p[1]); if (finite(trackSigma[i]?.[0])) xs.push(p[0] - trackSigma[i][0], p[0] + trackSigma[i][0]); if (finite(trackSigma[i]?.[1])) ys.push(p[1] - trackSigma[i][1], p[1] + trackSigma[i][1]); });
      measured.forEach(({ point: p, sigma: sig }) => { xs.push(p[0]); ys.push(p[1]); if (finite(sig[0])) xs.push(p[0] - sig[0], p[0] + sig[0]); if (finite(sig[1])) ys.push(p[1] - sig[1], p[1] + sig[1]); });
      const frame = plotFrame(container, 'Lens center trajectory with marginal uncertainties', extent(xs), extent(ys), 'x [mas]', 'y [mas]', true, 320);
      track.forEach((p, i) => errorBar(frame, p[0], p[1], trackSigma[i]?.[0], trackSigma[i]?.[1], '#3aa8b6'));
      const ordered = track.map((point, i) => ({ point, i })).sort((a, b) => (epochs[a.i] ?? a.i) - (epochs[b.i] ?? b.i));
      line(frame, ordered.map(item => item.point));
      measured.forEach(({ point: p, sigma: sig, index }) => { errorBar(frame, p[0], p[1], sig[0], sig[1]); marker(frame, p[0], p[1], { label: `Pair-derived GR center, epoch ${epochs[index] ?? index}: (${number(p[0])}, ${number(p[1])}) mas` }); });
      if (track.length > 1) {
        [ordered[0], ordered[ordered.length - 1]].forEach(({ point: p, i }) => { frame.svg.append(svgElement('text', { x: frame.x(p[0]) + 7, y: frame.y(p[1]) - 8, fill: '#007f93', 'font-size': 9 }, `t=${String(epochs[i] ?? i)}`)); });
      }
      $('track-title').textContent = 'Lens-center trajectory';
      $('track-caption').textContent = 'Dots: centers inferred from the observed pairs using the isolated GR identity, a diagnostic rather than an independent observable. Cyan: fitted center track. Bars show marginal 1σ uncertainties where identified; the fit retains the full covariance.';
      return;
    }
    setLegend('Observed images', 'Fitted images');
    if (!observed.length && !predicted.length) { chartEmpty(container, 'The server did not supply astrometric observations or predictions.'); return; }
    const xs = [], ys = [];
    [...observed, ...predicted].forEach(row => { if (Array.isArray(row)) { xs.push(row[0], row[2]); ys.push(row[1], row[3]); } });
    const frame = plotFrame(container, 'Observed and fitted primary image positions', extent(xs), extent(ys), 'x [mas]', 'y [mas]', true, 320);
    predicted.forEach((row, i) => [0, 2].forEach(offset => marker(frame, row[offset], row[offset + 1], { hollow: true, color: '#007f93', radius: 4.6, label: `Fitted ${offset ? 'negative' : 'positive'}-parity image, epoch ${epochs[i] ?? i}` })));
    observed.forEach((row, i) => {
      const cov = blockCovariance(i);
      [0, 2].forEach(offset => {
        const sx = finite(cov?.[offset]?.[offset]) ? Math.sqrt(Math.max(0, cov[offset][offset])) : null;
        const sy = finite(cov?.[offset + 1]?.[offset + 1]) ? Math.sqrt(Math.max(0, cov[offset + 1][offset + 1])) : null;
        errorBar(frame, row[offset], row[offset + 1], sx, sy);
        marker(frame, row[offset], row[offset + 1], { hollow: offset === 2, label: `${offset ? 'Inner' : 'Outer'} image, epoch ${epochs[i] ?? i}` });
      });
    });
    $('track-title').textContent = 'Observed and fitted image plane';
    $('track-caption').textContent = 'Dark filled/open markers: observed positive/negative-parity images. Cyan rings: fitted images. Different source rows are not connected into a trajectory. Coordinate bars show supplied marginal 1σ uncertainty where available.';
  }
  function renderSeries() {
    const container = $('series-chart'), { observed, predicted, epochs } = rows();
    if (!observed.length || !epochs.length) { chartEmpty(container, 'The server did not supply an epoch series.'); return; }
    const index = Number($('series-select').value);
    const labels = ['Positive-parity image x [mas]', 'Positive-parity image y [mas]', 'Negative-parity image x [mas]', 'Negative-parity image y [mas]', 'ln(flux ratio)', 'Time delay [s]'];
    const values = [];
    const errors = observed.map((row, i) => {
      values.push(row[index]); const cov = blockCovariance(i), value = cov?.[index]?.[index];
      const sigma = finite(value) && value >= 0 ? Math.sqrt(value) : null;
      if (finite(sigma)) values.push(row[index] - sigma, row[index] + sigma);
      if (finite(predicted[i]?.[index])) values.push(predicted[i][index]);
      return sigma;
    });
    const frame = plotFrame(container, `Observed and fitted ${labels[index]} over epochs`, extent(epochs), extent(values), 'Epoch [observer yr]', labels[index], false, 270);
    predicted.forEach((row, i) => marker(frame, epochs[i], row[index], { hollow: true, color: '#007f93', radius: 4.6, label: `Epoch ${epochs[i]}: fitted ${number(row[index])}` }));
    observed.forEach((row, i) => { errorBar(frame, epochs[i], row[index], null, errors[i]); marker(frame, epochs[i], row[index], { label: `Epoch ${epochs[i]}: observed ${number(row[index])}${finite(errors[i]) ? ' ± ' + number(errors[i]) : ''}; fit ${number(predicted[i]?.[index])}` }); });
    $('series-caption').textContent = errors.some(finite)
      ? 'Dark markers and bars: measured values with input marginal 1σ uncertainties. Cyan rings: fitted values for the same rows. Source positions are free per row; no continuous source trajectory is inferred. The inference uses the complete covariance, including correlations not shown by individual bars.'
      : 'Dark markers: supplied measurements. Cyan rings: fitted values for the same independent rows. No continuous source trajectory is inferred. The server did not supply marginal uncertainties for this display.';
  }
  function renderCharts() { if (state.result) { renderTrack(); renderSeries(); renderWhitenedResiduals(); } }
  function download(content, filename, type) {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = filename;
    document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  $('example-select').addEventListener('change', updateExampleDescription);
  $('download-example-bundle').addEventListener('click', event => { if (event.currentTarget.getAttribute('aria-disabled') === 'true') event.preventDefault(); });
  $('load-example').addEventListener('click', loadSelectedExample);
  $('file-input').addEventListener('change', async event => {
    const file = event.target.files?.[0]; if (!file || state.busy || state.loading) return;
    state.loading = true; syncControls();
    try {
      if (file.size > 8_000_000) throw new Error('The dataset file exceeds 8 MB (8,000,000 bytes). Use the documented 3–80 row input with its full covariance.');
      const text = (await file.text()).replace(/^\uFEFF/, '');
      setDataset(JSON.parse(text), file.name, text);
    } catch (error) { showError(`Could not import the dataset: ${error.message}`); }
    finally { event.target.value = ''; state.loading = false; syncControls(); }
  });
  $('clear-data').addEventListener('click', () => {
    state.dataset = null; state.validated = false; clearResults(); clearError();
    $('source-json').value = ''; $('loaded-file').hidden = true; $('dataset-summary').hidden = true;
    validationMessage('Load an example or import a dataset to begin.');
    runMessage('Validate a dataset to enable the fit.');
    $('empty-results').querySelector('h2').textContent = 'Start with the ordinary lens response.';
    $('empty-results').querySelector('.empty-footnote').textContent = 'No fit has been run. No example results are displayed.';
    syncControls();
  });
  $('source-json').addEventListener('input', () => {
    state.validated = false; clearResults(); $('dataset-summary').hidden = true;
    $('supplied-calibrations').hidden = true; $('input-provenance').hidden = true;
    validationMessage('Input edited. Validate the updated JSON before fitting.'); runMessage('Revalidate the edited dataset.'); syncControls();
  });
  $('validate-data').addEventListener('click', validateDataset);
  document.querySelectorAll('input[name="family"], #nuisance-select, #fit-starts').forEach(element => element.addEventListener('change', () => {
    if (element.id === 'fit-starts') element.value = configuration().starts;
    clearResults(); syncControls();
    runMessage(state.validated ? 'Configuration changed. Ready to run inference.' : 'Validate a dataset to enable the fit.');
  }));
  $('run-fit').addEventListener('click', submitFit);
  $('retry-job').addEventListener('click', () => { clearError(); state.polling = true; runMessage('Reconnecting to the fit job…', true); pollJob(); });
  $('series-select').addEventListener('change', renderSeries);
  $('copy-input').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText($('source-json').value); toast('Dataset JSON copied.'); }
    catch { toast('Clipboard access is unavailable. Use Download input instead.'); }
  });
  $('download-input').addEventListener('click', () => download($('source-json').value, 'bhtracker-dataset.json', 'application/json'));
  $('export-json').addEventListener('click', () => { if (state.result) download(JSON.stringify(state.result, null, 2), 'bhtracker-result.json', 'application/json'); });
  $('export-bundle').addEventListener('click', async () => {
    if (!state.result || $('export-bundle').disabled) return;
    $('export-bundle').disabled = true; $('export-bundle').textContent = 'Preparing replay bundle…';
    try {
      const blob = await apiZip('/api/export', { result: state.result });
      download(blob, 'bhsm-analysis-replay.zip', 'application/zip'); toast('Replay bundle downloaded.');
    } catch (error) { showError(`Could not export the replay bundle: ${error.message}`); }
    finally { $('export-bundle').disabled = false; $('export-bundle').textContent = 'Download replay bundle'; }
  });
  $('export-html').addEventListener('click', async () => {
    if (!state.result) return;
    $('export-html').disabled = true;
    try {
      const report = await api('/api/report', { result: state.result });
      if (typeof report.html !== 'string' || !report.html) throw new Error('The server did not supply report HTML.');
      download(report.html, 'bhtracker-report.html', 'text/html;charset=utf-8'); toast('HTML report exported.');
    } catch (error) { showError(`Could not export the report: ${error.message}`); }
    finally { $('export-html').disabled = false; }
  });
  let resizeTimer;
  window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(renderCharts, 150); });
  window.addEventListener('beforeunload', () => { clearTimeout(state.pollTimer); stopElapsed(); });
  syncControls(); loadExamples();
})();
