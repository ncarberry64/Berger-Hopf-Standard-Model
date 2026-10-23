'use strict';
(() => {
  const C = AtlasCore;
  const $ = id => document.getElementById(id);
  const LABELS = {REVIEW_REQUIRED: 'Review required', SUPPORTED_LENSING_EVENT: 'Supported lensing event',
    BLACK_HOLE_SEARCH_TARGET: 'Black-hole search target', BLACK_HOLE_CANDIDATE: 'Black-hole candidate',
    STRONGLY_SUPPORTED_BLACK_HOLE_IDENTIFICATION: 'Strongly supported black-hole identification'};
  const COLORS = {REVIEW_REQUIRED: '#acb8c2', SUPPORTED_LENSING_EVENT: '#42bacc', BLACK_HOLE_SEARCH_TARGET: '#efbd59',
    BLACK_HOLE_CANDIDATE: '#cc9bdf', STRONGLY_SUPPORTED_BLACK_HOLE_IDENTIFICATION: '#a4dc87'};
  const state = {inventory: null, inventoryText: null, source: null, filters: C.defaultFilters(), selected: null, fullSky: false};
  function node(tag, text, className) {
    const n = document.createElement(tag); if (text !== undefined) n.textContent = text;
    if (className) n.className = className; return n;
  }
  function status(text, error = false) { $('status').textContent = text; $('status').classList.toggle('error', error); }
  function title(value) { return String(value).replaceAll('_', ' ').toLowerCase().replace(/^./, c => c.toUpperCase()); }
  function short(value, max = 110) { const s = typeof value === 'string' ? value : JSON.stringify(value); return s.length > max ? s.slice(0, max) + '…' : s; }
  function safeUrl(value) { try { const u = new URL(value); return ['http:', 'https:'].includes(u.protocol) ? u.href : null; } catch { return null; } }
  function options(element, values, labels = null) {
    element.replaceChildren(element.options[0]);
    values.forEach(value => { const opt = node('option', labels ? labels[value] : title(value)); opt.value = value; element.append(opt); });
  }
  function setFilters() { for (const [key, id] of Object.entries({query: 'search', tier: 'tier', cohort: 'cohort', flag: 'flag', sort: 'sort'})) $(id).value = state.filters[key]; }
  function readFilters() { state.filters = {query: $('search').value, tier: $('tier').value, cohort: $('cohort').value, flag: $('flag').value, sort: $('sort').value}; render(); }
  function install(inventory, inventoryText, source, filters) {
    C.validateInventory(inventory); state.inventory = inventory; state.inventoryText = inventoryText; state.source = source;
    state.filters = filters || C.defaultFilters(); state.selected = null;
    options($('tier'), C.TIERS.filter(t => inventory.events.some(e => e.tier === t)), LABELS);
    options($('cohort'), [...new Set(inventory.events.flatMap(e => e.cohorts))].sort());
    options($('flag'), [...new Set(inventory.events.flatMap(e => e.quality_flags))].sort());
    setFilters(); $('download-json').disabled = false; $('download-csv').disabled = false;
    $('integrity').textContent = 'Inventory UTF-8 SHA-256\n' + source.inventory_utf8_sha256 + '\n\n' +
      'Reviewer repository\n' + C.REPOSITORY + '\n\n' + 'Data origin\n' + (source.origin || 'Saved replay');
    render();
  }
  function renderSummary() {
    const e = state.inventory.events, m=state.inventory.metadata.counts || {}; const counts = [['Unique cohort events', e.length],
      ['Pilot / published parallax', `${m.pilot_events ?? '—'} / ${m.published_parallax_events ?? '—'}`],
      ['Frozen photometric follow-ups', m.pilot_frozen_followup_targets ?? '—'],
      ['Conditional search targets', e.filter(x => x.tier === 'BLACK_HOLE_SEARCH_TARGET').length],
      ['Inadequate pilot simple fits', m.pilot_inadequate_simple_model ?? '—'], ['New black-hole interpretations', 0]];
    $('summary').replaceChildren(...counts.map(([label, value]) => { const n = node('div', undefined, 'metric'); n.append(node('strong', String(value)), node('span', label)); return n; }));
  }
  function render() {
    if (!state.inventory) return;
    const rows = C.filterEvents(state.inventory, state.filters);
    if (!rows.some(e => e.event_id === state.selected)) state.selected = rows[0]?.event_id || null;
    $('visible-count').textContent = `${rows.length} / ${state.inventory.events.length} visible`;
    $('empty').hidden = rows.length > 0;
    renderSummary(); renderTable(rows); renderMap(rows); renderDetail(rows.find(e => e.event_id === state.selected)); renderBenchmarks();
  }
  function select(id) { state.selected = id; render(); }
  function renderTable(rows) {
    $('event-table').replaceChildren(...rows.map(e => {
      const tr = node('tr'); tr.classList.toggle('selected', e.event_id === state.selected);
      const identity = node('td'); const pick = node('button', e.event_id); pick.addEventListener('click', () => select(e.event_id));
      identity.append(pick); if (e.known_aliases.length) identity.append(node('small', e.known_aliases.join(' · ')));
      const tier = node('td'); tier.append(node('span', LABELS[e.tier], 'tag'));
      const d = e.source_direction; const dir = node('td', d.ra_deg === null ? 'Unavailable' : `${d.ra_deg.toFixed(5)}°\n${d.dec_deg.toFixed(5)}°`, 'direction');
      dir.style.whiteSpace = 'pre-line'; const quality = node('td');
      e.quality_flags.forEach(f => quality.append(node('span', title(f), 'flag')));
      if (!e.quality_flags.length) quality.textContent = 'None recorded';
      tr.append(identity, tier, dir, quality); return tr;
    }));
  }
  function svg(tag, attrs = {}, text) { const n = document.createElementNS('http://www.w3.org/2000/svg', tag); Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v)); if (text !== undefined) n.textContent = text; return n; }
  function renderMap(rows) {
    const sky = $('sky-map'); sky.replaceChildren(); const points = rows.filter(e => e.source_direction.ra_deg !== null);
    $('map-count').textContent = `${points.length} markers`;
    const tiers = C.TIERS.filter(t => rows.some(e => e.tier === t));
    $('map-legend').replaceChildren(...tiers.map(t => { const n = node('span'); const swatch = node('i'); swatch.style.background = COLORS[t]; n.append(swatch, document.createTextNode(LABELS[t])); return n; }));
    let lo = 0, hi = 360, bottom = -90, top = 90;
    if (!state.fullSky && points.length) {
      // Circular RA centering avoids a false 359° span near the coordinate seam.
      const rad = Math.PI / 180; const center = Math.atan2(points.reduce((s,e) => s + Math.sin(e.source_direction.ra_deg*rad),0),
        points.reduce((s,e) => s + Math.cos(e.source_direction.ra_deg*rad),0)) / rad;
      const offsets = points.map(e => ((e.source_direction.ra_deg - center + 540) % 360) - 180);
      lo = center + Math.min(...offsets); hi = center + Math.max(...offsets);
      bottom = Math.min(...points.map(e => e.source_direction.dec_deg)); top = Math.max(...points.map(e => e.source_direction.dec_deg));
      const dx = Math.max(.5, (hi-lo)*.1), dy = Math.max(.5,(top-bottom)*.15); lo -= dx; hi += dx; bottom = Math.max(-90,bottom-dy); top = Math.min(90,top+dy);
    }
    const left=61,right=879,up=22,down=344; const x = ra => right - (ra-lo)/(hi-lo)*(right-left); const y = dec => down-(dec-bottom)/(top-bottom)*(down-up);
    for(let i=0;i<=6;i++) {const a=lo+(hi-lo)*i/6, px=x(a); sky.append(svg('line',{x1:px,y1:up,x2:px,y2:down,class:'grid'})); sky.append(svg('text',{x:px,y:364,'text-anchor':'middle'}, `${((a%360+360)%360).toFixed(1)}°`));}
    for(let i=0;i<=4;i++) {const d=bottom+(top-bottom)*i/4, py=y(d); sky.append(svg('line',{x1:left,y1:py,x2:right,y2:py,class:'grid'})); sky.append(svg('text',{x:49,y:py+4,'text-anchor':'end'}, `${d.toFixed(1)}°`));}
    sky.append(svg('text',{x:470,y:384,'text-anchor':'middle'},'RIGHT ASCENSION · DEGREES'));
    points.forEach(e => { const raw=e.source_direction.ra_deg; const mid=(lo+hi)/2; const ra=state.fullSky?raw:mid+((raw-mid+540)%360)-180;
      const mark=svg('circle',{cx:x(ra),cy:y(e.source_direction.dec_deg),r:e.event_id===state.selected?6:4,fill:COLORS[e.tier],class:'marker'+(e.event_id===state.selected?' selected':''),tabindex:'0','role':'button','aria-label':`${e.event_id}, ${LABELS[e.tier]}, source/event direction`});
      mark.append(svg('title',{},`${e.event_id} · ${LABELS[e.tier]}\nSource/event direction only`)); mark.addEventListener('click',()=>select(e.event_id)); mark.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();select(e.event_id);}}); sky.append(mark);});
    if(!points.length) sky.append(svg('text',{x:450,y:180,'text-anchor':'middle'},'No source/event directions in this filtered view'));
  }
  function facts(section, items) { const dl = node('dl'); for (const [name,value] of items) { const row = node('div'); row.append(node('dt',name),node('dd',value ?? 'Unavailable',value === null || value === undefined?'unavailable':'')); dl.append(row); } section.append(dl); }
  function detailSection(parent, heading) { const n=node('div',undefined,'detail-section'); n.append(node('h3',heading)); parent.append(n); return n; }
  function rawBlock(parent, data) { const d=node('details'); d.append(node('summary','Inspect source fields')); d.append(node('pre',JSON.stringify(data,null,2))); parent.append(d); }
  function renderDetail(e) {
    const panel=$('event-detail'); panel.replaceChildren();
    if(!e){panel.append(node('p','No event selected. Reset the filters to inspect the inventory.'));return;}
    panel.append(node('p','SELECTED EVENT','kicker'),node('h2',e.event_id,'event-name'),node('span',LABELS[e.tier],'tag'));
    panel.append(node('p',e.known_aliases.length?e.known_aliases.join(' · '):'No additional aliases recorded.','aliases'));
    const basis=detailSection(panel,'Evidence and classification');
    if(e.classification_basis) basis.append(node('p',typeof e.classification_basis==='string'?title(e.classification_basis):JSON.stringify(e.classification_basis)));
    basis.append(node('p','A tier records evidence and a reason for follow-up. It does not convert a long-duration event into a black-hole mass.'));
    if(e.quality_flags.length) {const list=node('ul');e.quality_flags.forEach(f=>list.append(node('li',title(f))));basis.append(list);}
    const direction=detailSection(panel,'Where to look: source/event direction'); const d=e.source_direction;
    facts(direction,[['Right ascension',d.ra_hms || (d.ra_deg===null?null:d.ra_deg.toFixed(7)+'°')],['Declination',d.dec_dms || (d.dec_deg===null?null:d.dec_deg.toFixed(7)+'°')],['Coordinate frame',d.frame],['Equinox',d.equinox],['Observation epoch',d.epoch],['Direction uncertainty',d.uncertainty===null?null:JSON.stringify(d.uncertainty)]]);
    direction.append(node('p','The J2000 equinox does not establish an observation epoch or a motion correction. This direction is not an independently inferred present-day lens position.'));
    const lens=detailSection(panel,'Lens quantities'); facts(lens,[['Inferred lens position',null],['Lens position date/error',null],['Lens distance',null],['Lens mass / bounds',null],['Absolute proper motion',null],['Radial velocity',null],['Core / membrane / horizon',null]]);
    const photo=detailSection(panel,'Photometric assessment'); const pa=e.photometric_assessment || {};
    facts(photo,[['Tracker fit status',pa.tracker_status?title(pa.tracker_status):null],['Frozen follow-up eligible',pa.followup_eligible===null||pa.followup_eligible===undefined?null:pa.followup_eligible?'Yes':'No'],
      ['Fitted crossing time',Number.isFinite(pa.fitted_tE_days)?pa.fitted_tE_days.toFixed(2)+' days':null],
      ['Conditional timescale limits',Number.isFinite(pa.timescale_profile_lower_days)&&Number.isFinite(pa.timescale_profile_upper_days)?`${pa.timescale_profile_lower_days.toFixed(2)}–${pa.timescale_profile_upper_days.toFixed(2)} days`:null]]);
    photo.append(node('p','A conditional fitted crossing time is a light-curve parameter, not a lens mass. Fit status and screening conditions govern its use.'));rawBlock(photo,pa);
    const literature=detailSection(panel,'Published evidence and alternatives');
    const assessment=e.literature_assessment;
    if(assessment && typeof assessment==='object') {
      for (const [k,v] of Object.entries(assessment)) {
        if(v===null || v===undefined) continue;
        if(typeof v==='string' || typeof v==='number' || typeof v==='boolean') literature.append(node('p',title(k)+': '+String(v)));
      }
      if(Array.isArray(assessment.interpretations)) for(const interpretation of assessment.interpretations){
        const item=node('div',undefined,'literature-item');item.append(node('strong',interpretation.publication || 'Published interpretation'));
        if(interpretation.role)item.append(node('p',title(interpretation.role)));
        if(interpretation.caution)item.append(node('p',interpretation.caution,'literature-caution'));
        if(safeUrl(interpretation.url)){const a=node('a','Read the primary publication ↗');a.href=safeUrl(interpretation.url);a.target='_blank';a.rel='noopener noreferrer';item.append(a);}
        literature.append(item);
      }
      if(Array.isArray(assessment.alternatives)){literature.append(node('p','Alternatives: '+assessment.alternatives.join('; ')+'.'));}
    }
    rawBlock(literature,assessment ?? null);
    const next=detailSection(panel,'Next useful evidence');
    if(Array.isArray(e.next_actions)){const ul=node('ul');e.next_actions.forEach(a=>ul.append(node('li',typeof a==='string'?a:JSON.stringify(a))));next.append(ul);}else next.append(node('p',e.next_actions?JSON.stringify(e.next_actions):'No event-specific action recorded.'));
    if(Array.isArray(e.missing_observations)){const list=node('ul');e.missing_observations.forEach(x=>list.append(node('li',x)));next.append(node('p','Still missing:'),list);}
    const provenance=detailSection(panel,'Provenance');
    const urls=new Set();for(const p of e.provenance){const url=typeof p==='string'?p:p?.url;if(safeUrl(url)&&!urls.has(url)){urls.add(url);const a=node('a',typeof p==='object'?(p.source_role || p.role || 'Primary source')+' ↗':p);a.href=safeUrl(url);a.target='_blank';a.rel='noopener noreferrer';provenance.append(a,node('br'));}}
    rawBlock(provenance,e.provenance);
  }
  function renderBenchmarks() {
    let box=$('benchmark-panel');
    if(!box){box=node('section',undefined,'panel benchmark');box.id='benchmark-panel';$('summary').after(box);}
    box.replaceChildren(node('p','SEPARATE KNOWN-SYSTEM BENCHMARK','kicker'));
    const benchmarks=state.inventory.benchmarks || [];
    if(!benchmarks.length){box.append(node('p','Published known-system benchmark records are not included in this inventory version.'));return;}
    box.append(node('h2','Published black-hole evidence is a benchmark, not a tracker recovery claim.'));
    for(const b of benchmarks){box.append(node('p',`${b.event_id || 'Known system'} · Published interpretation: ${title(b.benchmark_status || 'See provenance')} · Tracker recovery: ${title(b.tracker_recovery_status || 'NOT_ESTABLISHED')}.`));
      if(Array.isArray(b.classification_evidence))b.classification_evidence.forEach(x=>box.append(node('p',x)));
      const d=b.source_direction;box.append(node('p',`Published source/event direction: RA ${d.ra_deg.toFixed(7)}°, Dec ${d.dec_deg.toFixed(7)}° (${d.frame}). Inferred lens position, epoch and uncertainty: unavailable.`));
      rawBlock(box,b);}
    box.append(node('p','Benchmark entries are separate from the cohort counts and search-target ranking.'));
  }
  function download(name, content, type) { const url=URL.createObjectURL(new Blob([content],{type})); const a=node('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000); }
  $('search').addEventListener('input',readFilters); for(const id of ['tier','cohort','flag','sort']) $(id).addEventListener('change',readFilters);
  $('reset').addEventListener('click',()=>{state.filters=C.defaultFilters();setFilters();render();});
  $('fit-map').addEventListener('click',()=>{state.fullSky=false;$('fit-map').classList.add('active');$('all-sky').classList.remove('active');render();});
  $('all-sky').addEventListener('click',()=>{state.fullSky=true;$('all-sky').classList.add('active');$('fit-map').classList.remove('active');render();});
  $('download-csv').addEventListener('click',()=>{try{download('BHSM_candidate_atlas_filtered.csv',C.exportCsv(state.inventory,state.filters,state.source.inventory_utf8_sha256),'text/csv;charset=utf-8');status('Filtered CSV exported with provenance, inventory metadata and explicit unavailable-field policy. Use the JSON replay to preserve the complete inventory.');}catch(err){status(err.message,true);}});
  $('download-json').addEventListener('click',async()=>{try{const replay=await C.createReplay(state.inventory,state.filters,state.source,new Date().toISOString(),state.inventoryText);download('BHSM_candidate_atlas_replay.json',JSON.stringify(replay,null,2),'application/json');status(`Exported ${replay.payload_sha256.slice(0,12)}… · filtered records and the complete original inventory are included. Replay restores the saved view without refitting.`);}catch(err){status(err.message,true);}});
  $('replay-file').addEventListener('change',async()=>{const file=$('replay-file').files[0];if(!file)return;try{if(file.size>32*1024*1024)throw new Error('Replay exceeds the 32 MiB import limit.');const p=await C.validateReplay(C.parseJsonStrict(C.decodeUtf8(await file.arrayBuffer())));install(p.inventory,p.inventory_json,{...p.data_source,origin:'Validated saved replay: '+file.name,inventory_utf8_sha256:p.inventory_utf8_sha256},p.filters);status(`Replay integrity verified. Restored ${p.selected_event_ids.length} filtered records; all ${p.inventory.events.length} cohort records are preserved. No physical fit was run.`);}catch(err){status('Replay rejected; the current inventory remains unchanged. '+err.message,true);}finally{$('replay-file').value='';}});
  async function start(){try{const [manifestResponse,inventoryResponse]=await Promise.all([fetch('atlas_manifest.json',{cache:'no-store'}),fetch('atlas_data.json',{cache:'no-store'})]);if(!manifestResponse.ok||!inventoryResponse.ok)throw new Error('The atlas data and manifest are unavailable. Start the local server with the reviewed inventory path.');const manifest=C.parseJsonStrict(C.decodeUtf8(await manifestResponse.arrayBuffer()));const text=C.decodeUtf8(await inventoryResponse.arrayBuffer());const digest=await C.sha256(text);if(digest!==manifest.inventory_utf8_sha256)throw new Error('Source inventory SHA-256 mismatch. No records were admitted.');const inventory=C.validateInventory(C.parseJsonStrict(text));install(inventory,text,{origin:manifest.origin||'Local reviewed inventory',inventory_utf8_sha256:digest});status(`Loaded ${inventory.events.length} cohort records. Source-file SHA-256 verified. Unresolved physical quantities remain unavailable.`);}catch(err){status(err.message,true);}}
  start();
})();
