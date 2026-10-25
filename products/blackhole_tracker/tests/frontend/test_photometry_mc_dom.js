'use strict';
// All HTTP, files, timers and downloads are invented/mocked. No backend/model.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const web = path.resolve(__dirname, '../../bhtracker/web');
const ui = require(path.join(web, 'photometry-mc.js'));
const html = fs.readFileSync(path.join(web, 'photometry-mc.html'), 'utf8');
const cases = [];
const encode = value => Buffer.from(value, 'binary').toString('base64');
const sample = Buffer.from('\ufeff{\r\n"row_identity":"α", "unknown":null\r\n}\r\n', 'utf8');
const zip = Uint8Array.from([80, 75, 3, 4, 0, 255, 128, 13, 10]);

class Element {
  constructor(tag, id) { this.tagName = tag; this.id = id || ''; this.children = []; this.listeners = {}; this._text = ''; this.value = ''; this.disabled = false; this.hidden = false; this.files = []; this.attrs = {}; }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
  set innerHTML(_) { throw new Error('Unsafe innerHTML use'); }
  get innerHTML() { throw new Error('Unsafe innerHTML use'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this._text = ''; this.children = nodes; }
  setAttribute(name, value) { this.attrs[name] = String(value); }
  removeAttribute(name) { delete this.attrs[name]; if (name === 'value') this.value = undefined; }
  addEventListener(name, fn) { (this.listeners[name] ||= []).push(fn); }
  async emit(name, event) { for (const fn of this.listeners[name] || []) await fn(event || {}); }
  remove() {}
  click() { return this.emit('click'); }
}

function fixtureFile(bytes, name = 'input.json') {
  const owned = Uint8Array.from(bytes);
  return {name, size: owned.length, arrayBuffer: async () => owned.slice().buffer};
}

function harness() {
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
  assert.equal(new Set(ids).size, ids.length, 'actual HTML IDs are unique');
  const elements = Object.fromEntries(ids.map(id => [id, new Element('fixture', id)]));
  for (const match of html.matchAll(/<input\b[^>]*\bid="([^"]+)"[^>]*>/g)) {
    const value = match[0].match(/\bvalue="([^"]*)"/); if (value) elements[match[1]].value = value[1];
  }
  const created = [];
  const doc = {getElementById: id => elements[id] || null, createElement: tag => { created.push(tag); return new Element(tag); }, body: new Element('body')};
  const queued = []; const calls = []; const downloads = []; const timers = new Map(); let timerId = 0;
  async function fetch(url, options) {
    calls.push({url, method: options.method, headers: options.headers, credentials: options.credentials, cache: options.cache, redirect: options.redirect,
      body: options.body === undefined ? undefined : options.headers['Content-Type'] === 'application/zip' ? options.body : JSON.parse(options.body)});
    assert.ok(queued.length, 'no unmocked HTTP request: ' + url);
    const next = queued.shift(); assert.equal(url, next.url); assert.equal(options.method, next.method);
    if (next.error) throw next.error;
    const value = typeof next.value === 'function' ? await next.value(calls[calls.length - 1].body) : next.value;
    return {ok: next.status < 400, status: next.status,
      headers: {get: () => next.mime || 'application/json'},
      json: async () => JSON.parse(JSON.stringify(value)), blob: async () => value};
  }
  const app = ui.createApp({document: doc, fetch, btoa: encode,
    setTimeout: (fn, ms) => { const id = ++timerId; timers.set(id, {fn, ms}); return id; },
    clearTimeout: id => timers.delete(id), download: (blob, name) => downloads.push({blob, name})});
  function enqueue(method, url, value, status = 200, mime) { queued.push({method, url, value, status, mime}); }
  function planResponse(body) {
    const nodes = [];
    for (const parameter of ['tE_days', 'u0']) (body.grids[parameter] || []).forEach((value, at) => {
      nodes.push({node_id: parameter + '_' + at, parameter, value, all199_seed_slots: Array.from({length: 199}, (_, slot) => slot)});
    });
    const sha = crypto.createHash('sha256').update(Buffer.from(body.input_base64, 'base64')).digest('hex');
    return {request: {nodes, evidence_scope: 'MOCK APPROXIMATE PENDING'}, summary: {rows: 5, instruments: ['OGLE'], input_utf8_sha256: sha, canonical_input_sha256: 'b'.repeat(64)}};
  }
  async function planned() {
    assert.equal(await app.loadInput(fixtureFile(sample)), true);
    elements['mc-te-grid'].value = '100, 200';
    elements['mc-u0-grid'].value = '';
    enqueue('POST', '/api/photometry-mc/plan', planResponse);
    let prevented = false;
    await elements['mc-form'].emit('submit', {preventDefault: () => { prevented = true; }});
    assert.equal(prevented, true); assert.equal(app.snapshot().hasPlan, true);
  }
  function job(status, nodes = [], extra = {}) { return {status, workspace_path: 'C:\\MOCK\\durable-workspace', progress: {completed_nodes: status === 'complete' ? 2 : 0, planned_nodes: 2, committed_bootstrap_fits: 3, current_node: 'tE_days_0', stage: 'MOCK'}, summary: {nodes, evidence_scope: 'APPROXIMATE / VALIDATION PENDING'}, ...extra}; }
  async function started(status = 'running', nodes = []) {
    await planned(); enqueue('POST', '/api/photometry-mc/start', {job_id: 'job-1', duplicate_prevented: false}, 202);
    enqueue('GET', '/api/photometry-mc/jobs/job-1', job(status, nodes));
    assert.equal(await app.start(), true);
  }
  return {app, el: elements, doc, created, queued, calls, downloads, timers, enqueue, planned, started, job, planResponse};
}

async function test(name, fn) { await fn(); cases.push(name); }

(async () => {
  await test('strict increasing grids, explicit entropy and resource budget', () => {
    assert.equal(ui.INPUT_LIMIT,32_000_000); assert.equal(ui.ZIP_LIMIT,128*1024*1024);
    assert.deepEqual(ui.configuration('0.1 10000', '.0001,10', '0,4294967295', '3600'), {grids: {tE_days: [.1, 10000], u0: [.0001, 10]}, entropy: [0, 4294967295], wall_seconds: 3600, max_saved_bytes: 268435456});
  });
  await test('invalid grids are refused without inferred points', () => {
    for (const grids of [['', ''], ['2,1', ''], ['1,1', ''], ['NaN', ''], ['0x10', ''], ['.09', ''], ['', '0'], [Array.from({length:18}, (_,i)=>i+1).join(','), '']]) assert.throws(() => ui.configuration(...grids, '1', '600'));
  });
  await test('seed and wall controls cannot silently coerce invalid values', () => {
    for (const seed of ['', '-1', '1.5', '4294967296', 'true', Array(17).fill('1').join(',')]) assert.throws(() => ui.configuration('1', '', seed, '600'));
    for (const wall of ['0', '3601', '1.5', 'Infinity']) assert.throws(() => ui.configuration('1', '', '1', wall));
  });
  await test('exact BOM CRLF UTF8 and binary bytes survive chunked base64', () => {
    assert.deepEqual(Buffer.from(ui.bytesToBase64(sample, encode), 'base64'), sample);
    const large = Uint8Array.from({length: 70001}, (_,i)=>i%251);
    assert.deepEqual(Buffer.from(ui.bytesToBase64(large, encode), 'base64'), Buffer.from(large));
    assert.deepEqual(Buffer.from(ui.bytesToBase64(zip, encode), 'base64'), Buffer.from(zip));
  });
  await test('missing, extra and duplicate incoming grid rows are retained', () => {
    const plan = [{node_id:'a',parameter:'tE_days',value:10},{node_id:'b',parameter:'u0',value:.1}];
    const incoming = [{node_id:'a',decision:'UNKNOWN'},{node_id:'a',decision:'FAILED'},{node_id:'extra',decision:'UNKNOWN'}];
    const before = JSON.stringify([plan,incoming]); const out = ui.mergeNodes(plan,incoming);
    assert.equal(out.length,4); assert.equal(out[1].decision,'UNKNOWN_NOT_RETURNED'); assert.equal(out[2].decision,'FAILED');
    assert.equal(JSON.stringify([plan,incoming]),before);
  });
  await test('empty app performs no HTTP or example analysis', () => {
    const h=harness(); assert.equal(h.calls.length,0); assert.equal(h.app.snapshot().hasInput,false);
    assert.equal(h.el['mc-start'].disabled,true); assert.equal(h.el['mc-export'].disabled,true); h.app.dispose();
  });
  await test('oversized and changed input-byte counts refuse before planning', async () => {
    const h=harness(); let read=false;
    assert.equal(await h.app.loadInput({name:'large',size:ui.INPUT_LIMIT+1,arrayBuffer:async()=>{read=true;}}),false);
    assert.equal(read,false); assert.equal(h.calls.length,0);
    assert.equal(await h.app.loadInput({name:'bad',size:2,arrayBuffer:async()=>new Uint8Array([1]).buffer}),false);
    assert.equal(h.app.snapshot().hasInput,false); h.app.dispose();
  });
  await test('plan sends original bytes and fixed explicit configuration only', async () => {
    const h=harness(); await h.planned(); const body=h.calls[0].body;
    assert.deepEqual(Buffer.from(body.input_base64,'base64'),sample); assert.deepEqual(body.entropy,[20261025,4242]);
    assert.deepEqual(body.grids,{tE_days:[100,200]}); assert.equal(body.wall_seconds,600);
    assert.equal(h.app.snapshot().view,'plan'); assert.equal(h.el['mc-export'].disabled,true);
    assert.ok(h.el['mc-plan-status'].textContent.includes('no analysis')); h.app.dispose();
  });
  await test('input changes invalidate a previously validated plan', async () => {
    const h=harness(); await h.planned(); h.el['mc-te-grid'].value='300'; await h.el['mc-te-grid'].emit('input');
    assert.equal(h.app.snapshot().hasPlan,false); assert.equal(h.el['mc-start'].disabled,true);
    assert.equal(await h.app.start(),false); assert.equal(h.calls.length,1); h.app.dispose();
  });
  await test('wrong returned grid/hash cannot become a valid plan', async () => {
    const h=harness(); await h.app.loadInput(fixtureFile(sample));h.el['mc-te-grid'].value='100';
    h.enqueue('POST','/api/photometry-mc/plan',body=>{const r=h.planResponse(body);r.summary.input_utf8_sha256=null;return r;});
    assert.equal(await h.app.plan(),false);assert.equal(h.app.snapshot().hasPlan,false);h.app.dispose();
  });
  await test('running job displays progress and retains all planned unknown nodes', async () => {
    const h=harness();await h.started();assert.equal(h.app.snapshot().jobStatus,'running');assert.equal(h.app.snapshot().rows.length,2);
    assert.equal(h.el['mc-cancel'].disabled,false);assert.equal(h.el['mc-export'].disabled,true);
    assert.equal(h.el['mc-node-progress'].textContent,'0 / 2');assert.equal(h.el['mc-fit-progress'].textContent,'3');
    assert.equal(h.el['mc-workspace'].textContent,'C:\\MOCK\\durable-workspace');h.app.dispose();
  });
  await test('cancellation is requested first and terminal unknown rows remain visible', async () => {
    const h=harness();await h.started();h.enqueue('POST','/api/photometry-mc/jobs/job-1/cancel',{cancellation_requested:true});
    h.enqueue('GET','/api/photometry-mc/jobs/job-1',h.job('running'));
    assert.equal(await h.app.cancel(),true);assert.equal(h.app.snapshot().jobStatus,'running');assert.equal(h.app.snapshot().cancelRequested,true);
    assert.ok(h.el['mc-job-status'].textContent.includes('awaiting confirmation'));
    h.enqueue('GET','/api/photometry-mc/jobs/job-1',h.job('cancelled',[{node_id:'tE_days_0',parameter:'tE_days',value:100,decision:'UNKNOWN',p_lower:null,p_upper:null,unknown:199}]));
    await h.app.refreshStatus();assert.equal(h.app.snapshot().rows.length,2);assert.equal(h.app.snapshot().rows[1].decision,'UNKNOWN_NOT_RETURNED');
    assert.equal(h.el['mc-export'].disabled,false);assert.equal(h.el['mc-node-rows'].children[0].children[3].textContent,'Unavailable');h.app.dispose();
  });
  await test('failed partial job can export without converting missing probability to zero', async () => {
    const h=harness();await h.started('failed',[{node_id:'tE_days_0',parameter:'tE_days',value:100,decision:'UNKNOWN',p_lower:null,p_upper:2,unknown:198}]);
    assert.equal(h.el['mc-node-rows'].children[0].children[3].textContent,'Unavailable');assert.equal(h.el['mc-node-rows'].children[0].children[4].textContent,'Unavailable');
    h.enqueue('POST','/api/photometry-mc/jobs/job-1/export',{bytes:'MOCK ZIP'},200,'application/zip');
    assert.equal(await h.app.exportJob(),true);assert.equal(h.downloads.length,1);assert.equal(h.downloads[0].name,'BHSM_photometry_MC_job-1.zip');h.app.dispose();
  });
  await test('network status failure retains job, rows and retry/cancel access', async () => {
    const h=harness();await h.started();h.queued.push({method:'GET',url:'/api/photometry-mc/jobs/job-1',error:new Error('Offline <script>')});
    assert.equal(await h.app.refreshStatus(),false);assert.equal(h.app.snapshot().jobId,'job-1');assert.equal(h.app.snapshot().rows.length,2);
    assert.equal(h.el['mc-refresh'].disabled,false);assert.equal(h.el['mc-cancel'].disabled,false);
    h.enqueue('GET','/api/photometry-mc/jobs/job-1',h.job('complete'));assert.equal(await h.app.refreshStatus(),true);
    assert.equal(h.app.snapshot().lastError,null);h.app.dispose();
  });
  await test('unsafe job identifier cannot become a route', async () => {
    const h=harness();await h.planned();h.enqueue('POST','/api/photometry-mc/start',{job_id:'../other'},202);
    assert.equal(await h.app.start(),false);assert.equal(h.calls.length,2);assert.equal(h.app.snapshot().jobId,null);h.app.dispose();
  });
  await test('integrity replay is explicit and preserves raw ZIP bytes', async () => {
    const h=harness(); const file=fixtureFile(zip,'audit.zip'); file.arrayBuffer=async()=>{throw new Error('ZIP must not be read into memory');};
    await h.app.loadReplay(file);
    h.enqueue('POST','/api/photometry-mc/replay-file?mode=integrity',{verification:{passed:true,mode:'INTEGRITY_ONLY',requested_mode:'integrity',scope:'bytes only'},summary:{nodes:[{node_id:'x',parameter:'u0',value:.1,decision:'UNKNOWN',unknown:199}]}});
    assert.equal(await h.app.replay('integrity'),true);assert.equal(h.calls.length,1);assert.equal(h.calls[0].body,file);
    assert.equal(h.calls[0].headers['Content-Type'],'application/zip');assert.equal(h.calls[0].credentials,'same-origin');
    assert.equal(h.calls[0].cache,'no-store');assert.equal(h.calls[0].redirect,'error');assert.ok(h.el['mc-replay-status'].textContent.includes('Integrity-only'));
    assert.equal(h.el['mc-export'].disabled,true);h.app.dispose();
  });
  await test('numerical replay failure retains full unknown result and differs from integrity', async () => {
    const h=harness(); const file=fixtureFile(zip); await h.app.loadReplay(file);h.enqueue('POST','/api/photometry-mc/replay-file?mode=numerical',{verification:{passed:false,mode:'NUMERICAL_SAVED_STATE_REPLAY',requested_mode:'numerical',scope:'saved-state objective mismatch'},summary:{nodes:[{node_id:'x',parameter:'tE_days',value:100,decision:'UNKNOWN',unknown:199}]}});
    assert.equal(await h.app.replay('numerical'),true);assert.equal(h.calls[0].body,file);assert.ok(h.el['mc-replay-status'].textContent.includes('Saved-state numerical'));
    assert.ok(h.app.snapshot().lastError.includes('unresolved'));assert.equal(h.app.snapshot().rows.length,1);h.app.dispose();
  });
  await test('replay mode mismatch refuses the claimed verification', async () => {
    for (const verification of [{passed:true,mode:'INTEGRITY_ONLY',requested_mode:'numerical'},
      {passed:true,mode:'NUMERICAL_SAVED_STATE_REPLAY',requested_mode:'integrity'},
      {passed:true,mode:'numerical',requested_mode:'numerical'},
      {passed:true,mode:'NUMERICAL_SAVED_STATE_REPLAY'}]) {
      const h=harness();await h.app.loadReplay(fixtureFile(zip));h.enqueue('POST','/api/photometry-mc/replay-file?mode=numerical',{verification,summary:{nodes:[]}});
      assert.equal(await h.app.replay('numerical'),false);assert.notEqual(h.app.snapshot().view,'replay');h.app.dispose();
    }
  });
  await test('oversized export error leaves durable workspace and terminal results intact', async () => {
    const h=harness();await h.started('complete');h.enqueue('POST','/api/photometry-mc/jobs/job-1/export',{error:'Browser ZIP limit exceeded; use CLI/file export.'},413);
    assert.equal(await h.app.exportJob(),false);assert.equal(h.downloads.length,0);assert.equal(h.app.snapshot().jobStatus,'complete');
    assert.equal(h.app.snapshot().rows.length,2);assert.equal(h.el['mc-workspace'].textContent,'C:\\MOCK\\durable-workspace');h.app.dispose();
  });
  await test('completed job history remains available after another run', async () => {
    const h=harness();await h.started('complete');h.enqueue('POST','/api/photometry-mc/start',{job_id:'job-2'},202);
    h.enqueue('GET','/api/photometry-mc/jobs/job-2',h.job('complete'));await h.app.start();assert.equal(h.el['mc-job-history'].children.length,2);
    h.enqueue('GET','/api/photometry-mc/jobs/job-1',h.job('failed'));await h.app.selectJob('job-1');assert.equal(h.app.snapshot().jobId,'job-1');
    assert.equal(h.app.snapshot().rows.length,2);h.app.dispose();
  });
  await test('disposing a view stops polling without issuing cancellation or analysis', async () => {
    const h=harness();await h.started();assert.ok(h.timers.size>0);const count=h.calls.length;h.app.dispose();assert.equal(h.timers.size,0);
    assert.equal(await h.app.refreshStatus(),false);assert.equal(h.calls.length,count);
  });
  await test('untrusted names, node fields and server errors render only as text', async () => {
    const h=harness();await h.app.loadInput(fixtureFile(sample,'<img src=x onerror=evil>.json'));assert.ok(h.el['mc-input-note'].textContent.includes('<img'));
    h.el['mc-te-grid'].value='100';h.enqueue('POST','/api/photometry-mc/plan',h.planResponse);await h.app.plan();
    h.enqueue('POST','/api/photometry-mc/start',{job_id:'safe'},202);h.enqueue('GET','/api/photometry-mc/jobs/safe',h.job('failed',[{node_id:'tE_days_0',parameter:'tE_days',value:100,decision:'<svg onload=evil>',unknown:'<script>evil</script>'}],{workspace_path:'<img workspace>'}));
    await h.app.start();assert.ok(h.el['mc-node-rows'].textContent.includes('<svg'));assert.equal(h.el['mc-workspace'].textContent,'<img workspace>');
    assert.ok(!h.created.includes('script')&&!h.created.includes('img')&&!h.created.includes('svg'));h.app.dispose();
  });
  await test('wrong binary MIME is not downloaded as an audit ZIP', async () => {
    const h=harness();await h.started('complete');h.enqueue('POST','/api/photometry-mc/jobs/job-1/export',{error:'not ZIP'},200,'application/json');
    assert.equal(await h.app.exportJob(),false);assert.equal(h.downloads.length,0);h.app.dispose();
  });
  await test('active jobs lock input and replay without extra HTTP work', async () => {
    const h=harness();await h.started();const count=h.calls.length;assert.equal(await h.app.loadInput(fixtureFile(sample)),false);
    assert.equal(await h.app.replay('numerical'),false);assert.equal(await h.app.start(),false);assert.equal(h.calls.length,count);h.app.dispose();
  });
  await test('duplicate plan clicks cannot issue overlapping requests', async () => {
    const h=harness();await h.app.loadInput(fixtureFile(sample));h.el['mc-te-grid'].value='100';let release;
    h.enqueue('POST','/api/photometry-mc/plan',body=>new Promise(resolve=>{release=()=>resolve(h.planResponse(body));}));
    const first=h.app.plan();assert.equal(await h.app.plan(),false);assert.equal(h.calls.length,1);release();assert.equal(await first,true);h.app.dispose();
  });
  await test('request timeout is unknown outcome, not a grid rejection', async () => {
    const h=harness();await h.planned();const error=new Error('aborted');error.name='AbortError';
    h.queued.push({method:'POST',url:'/api/photometry-mc/start',error});assert.equal(await h.app.start(),false);
    assert.ok(h.app.snapshot().lastError.includes('outcome is unavailable'));assert.equal(h.app.snapshot().view,'plan');h.app.dispose();
  });
  await test('above-old-limit ZIP is streamed as the exact File without allocating its contents', async () => {
    const h=harness(); let reads=0;
    const file={name:'large-audit.zip',size:40*1024*1024+1,arrayBuffer:async()=>{reads++;throw new Error('No large ZIP read allowed');}};
    assert.equal(await h.app.loadReplay(file),true);assert.equal(reads,0);assert.equal(h.calls.length,0);
    assert.equal(h.app.snapshot().replayBytes,file.size);
    h.enqueue('POST','/api/photometry-mc/replay-file?mode=numerical',{verification:{passed:true,mode:'NUMERICAL_SAVED_STATE_REPLAY',requested_mode:'numerical',scope:'MOCK saved-state replay'},summary:{input_utf8_sha256:'a'.repeat(64),canonical_input_sha256:'b'.repeat(64),nodes:[{node_id:'missing',decision:'UNKNOWN',unknown:199}]},evidence_scope:{validation:'PENDING',physical_mass:null}});
    assert.equal(await h.app.replay('numerical'),true);assert.equal(reads,0);assert.equal(h.calls.length,1);
    assert.equal(h.calls[0].body,file);assert.equal(h.calls[0].headers['Content-Type'],'application/zip');
    const saved=JSON.parse(h.el['mc-result-json'].textContent);assert.equal(saved.summary.input_utf8_sha256,'a'.repeat(64));
    assert.equal(saved.summary.canonical_input_sha256,'b'.repeat(64));assert.equal(saved.evidence_scope.validation,'PENDING');
    assert.equal(saved.evidence_scope.physical_mass,null);assert.equal(h.app.snapshot().rows[0].unknown,199);h.app.dispose();
  });
  await test('invalid ZIP sizes refuse before reading or sending a file', async () => {
    const h=harness();let reads=0;
    for (const size of [0,-1,ui.ZIP_LIMIT+1,Infinity,1.5]) {
      assert.equal(await h.app.loadReplay({name:'bad.zip',size,arrayBuffer:async()=>{reads++;}}),false);
      assert.equal(h.app.snapshot().replayBytes,0);assert.equal(h.el['mc-integrity'].disabled,true);
    }
    assert.equal(reads,0);assert.equal(h.calls.length,0);h.app.dispose();
  });
  await test('binary replay failure keeps the selected file and never falls back to base64 JSON', async () => {
    const h=harness();const file={name:'large.zip',size:45*1024*1024,arrayBuffer:async()=>{throw new Error('No archive read');}};
    await h.app.loadReplay(file);h.enqueue('POST','/api/photometry-mc/replay-file?mode=integrity',{error:'Saved archive rejected'},422);
    assert.equal(await h.app.replay('integrity'),false);assert.equal(h.calls.length,1);assert.equal(h.calls[0].body,file);
    assert.equal(h.app.snapshot().replayBytes,file.size);assert.ok(h.app.snapshot().lastError.includes('rejected'));
    assert.equal(h.el['mc-integrity'].disabled,false);h.app.dispose();
  });
  await test('u0-only request omits absent tE and allows exactly 16 entropy components', async () => {
    const h=harness();await h.app.loadInput(fixtureFile(sample));h.el['mc-te-grid'].value='';h.el['mc-u0-grid'].value='.1,.2';
    h.el['mc-entropy'].value=Array(16).fill('4294967295').join(',');h.enqueue('POST','/api/photometry-mc/plan',h.planResponse);
    assert.equal(await h.app.plan(),true);assert.deepEqual(h.calls[0].body.grids,{u0:[.1,.2]});
    assert.equal(h.calls[0].body.entropy.length,16);assert.equal(h.app.snapshot().rows.length,2);h.app.dispose();
  });
  await test('tamper refusal replaces pending and prior passed replay status', async () => {
    const h=harness();await h.app.loadReplay(fixtureFile(zip,'good.zip'));
    h.enqueue('POST','/api/photometry-mc/replay-file?mode=numerical',{verification:{passed:true,mode:'NUMERICAL_SAVED_STATE_REPLAY',requested_mode:'numerical',scope:'saved states'},summary:{nodes:[{node_id:'old',decision:'INCLUDED'}]}});
    assert.equal(await h.app.replay('numerical'),true);assert.ok(h.el['mc-replay-status'].textContent.includes('checks passed'));
    await h.app.loadReplay(fixtureFile(zip,'tampered.zip'));assert.equal(h.app.snapshot().rows.length,0);
    assert.ok(!h.el['mc-replay-status'].textContent.includes('checks passed'));
    assert.ok(!h.el['mc-result-json'].textContent.includes('"passed": true'));
    h.enqueue('POST','/api/photometry-mc/replay-file?mode=integrity',{error:'Replay member bytes/hash mismatch'},422);
    assert.equal(await h.app.replay('integrity'),false);assert.equal(h.app.snapshot().view,'replay_unverified');
    assert.equal(h.app.snapshot().rows.length,0);assert.ok(h.el['mc-replay-status'].textContent.includes('unavailable or refused'));
    assert.ok(h.el['mc-replay-status'].textContent.includes('hash mismatch'));
    assert.ok(!h.el['mc-replay-status'].textContent.includes('Checking'));
    assert.equal(JSON.parse(h.el['mc-result-json'].textContent).verification,null);
    assert.equal(h.el['mc-integrity'].disabled,false);h.app.dispose();
  });
  await test('replay transport failure clears stale verification and preserves job history', async () => {
    const h=harness();await h.started('complete');await h.app.loadReplay(fixtureFile(zip,'saved.zip'));
    h.queued.push({method:'POST',url:'/api/photometry-mc/replay-file?mode=numerical',error:new Error('Offline')});
    assert.equal(await h.app.replay('numerical'),false);assert.equal(h.app.snapshot().jobId,'job-1');
    assert.ok(h.el['mc-replay-status'].textContent.includes('Offline'));assert.equal(h.app.snapshot().rows.length,0);
    assert.equal(h.el['mc-return-job'].hidden,false);h.enqueue('GET','/api/photometry-mc/jobs/job-1',h.job('complete'));
    assert.equal(await h.app.refreshStatus(),true);assert.equal(h.app.snapshot().view,'job');h.app.dispose();
  });
  process.stdout.write(JSON.stringify({passed:true,tests:cases.length,cases,backend_calls:0,native_model_calls:0,scientific_validation:false})+'\n');
})().catch(error => { process.stderr.write(error.stack+'\n'); process.exitCode=1; });
