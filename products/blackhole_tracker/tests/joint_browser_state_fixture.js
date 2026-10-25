'use strict';
// Execute the shipped UI event handlers with deterministic DOM/network adapters.
// This fixture tests state transitions; the scientific API has separate tests.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(process.argv[2],'utf8');
const mode=process.argv[3];
const nodes=new Map();
class Element{
  constructor(id=''){this.id=id;this.hidden=false;this.disabled=false;this.textContent='';this.files=[];this.checked=false;this.value='';}
  addEventListener(){}
  append(){}
  replaceChildren(...children){if(this.id==='instrument')this.value=children[0]?.value||'';}
  getBoundingClientRect(){return {width:600,height:280};}
  getContext(){return new Proxy({},{get:()=>()=>{},set:()=>true});}
}
const get=id=>{if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id);};
const dataset={photometry:[{instrument:'OGLE',time_jd_tdb:2455760,magnitude:20,magnitude_error:.01}],astrometry:[{time_jd_tdb:2455760,north_error_mas:.2,east_error_mas:.2}]};
const summary={photometry_rows:1,astrometry_rows:1,time_coordinate:'Declared native clock'};
const saved={schema:'bhtracker.joint_result.v2',dataset_input:dataset,status:'JOINT_MODEL_OR_NOISE_INADEQUATE',mass_status:'UNSUPPORTED_MODEL_OR_NOISE_INADEQUATE',
  model_options:{gp:true},fit_configuration:{requested_starts:16,max_nfev:1800},numerical_convergence:{attempted_starts:12,converged_starts:12},parameters:{mass_msun:7.1},
  photometric_predictions_magnitude:[20],whitened_photometric_residuals:[0],astrometric_residuals_NE_mas:[[0,0]]};
if(mode==='numerical_fallback')delete saved.fit_configuration.requested_starts;
if(mode==='default_fallback'){delete saved.fit_configuration.requested_starts;delete saved.numerical_convergence.attempted_starts;}
const expectedStarts=mode==='numerical_fallback'?12:16;
const requests=[];
async function fetch(path,options){
  requests.push({path,options});
  let body;
  if(path==='/api/health')body={version:'test'};
  else if(path==='/api/joint/validate')body={summary};
  else if(path==='/api/joint/result')body={summary,dataset_json:JSON.stringify(dataset)};
  else if(path==='/api/joint/fit')body={job_id:'failed-search'};
  else if(path==='/api/jobs/failed-search')body={status:'complete',result:{status:'JOINT_SEARCH_FAILED'},result_json:'{"status":"JOINT_SEARCH_FAILED"}'};
  else if(path==='/api/joint/profile')body={job_id:'saved-profile'};
  else if(path==='/api/jobs/saved-profile')body={status:'complete',result:{rows:[{mass_msun:7,solution_status:'UNRESOLVED'}]}};
  else throw new Error('Unexpected request '+path);
  return {ok:true,json:async()=>body};
}
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element()},window:{devicePixelRatio:1,addEventListener(){}},fetch,
  setTimeout,clearTimeout,Blob,URL,console});
vm.runInContext(source,context,{filename:process.argv[2]});
get('input-format').value='json';get('starts').value='1';get('evaluations').value='1';get('options').value='{}';get('scientific-version').value='v2';get('masses').value='1,7,10';
get('dataset-file').files=[{size:100,text:async()=>JSON.stringify(dataset)}];
get('result-file').files=[{size:100,text:async()=>JSON.stringify(saved)}];
async function settle(){for(let i=0;i<6;i++)await new Promise(resolve=>setImmediate(resolve));}
async function click(id){await get(id).onclick();await settle();}
(async()=>{
  await click('validate');
  await click('run');
  assert.match(get('job-status').textContent,/Search failed/);
  assert.equal(get('download-failure').hidden,false);
  assert.equal(get('results').hidden,true);
  await click('load-result');
  assert.equal(get('message').hidden,true);
  assert.equal(get('job-status').textContent,'Saved result verified; no new fit run.');
  assert.equal(Number(get('starts').value),expectedStarts);
  assert.equal(Number(get('evaluations').value),1800);
  assert.equal(get('results').hidden,false);
  assert.equal(get('download-failure').hidden,true);
  assert.match(get('replay-status').textContent,/Saved-state replay passed/);
  assert.equal(requests.filter(r=>r.path==='/api/joint/fit').length,1,'opening must not launch optimization');
  await click('profile');
  assert.equal(get('profile-result').hidden,false);
  assert.match(get('profile-summary').textContent,/UNRESOLVED/);
  await click('validate');
  assert.equal(get('results').hidden,true);
  assert.equal(get('profile-result').hidden,true);
  assert.equal(get('profile-summary').textContent,'');
  assert.equal(get('replay-status').textContent,'');
  assert.equal(get('retry').hidden,true);
  assert.equal(get('profile').disabled,true);
  assert.equal(get('run').disabled,false);
  assert.match(get('job-status').textContent,/no fit run for this input/);
  assert.equal(requests.filter(r=>r.path==='/api/joint/fit').length,1,'new input validation must not launch optimization');
  process.stdout.write(JSON.stringify({mode,passed:true,restored_starts:expectedStarts}));
})().catch(error=>{console.error(error);process.exitCode=1;});
