'use strict';
(() => {
  const el=id=>document.getElementById(id);
  let programText=null;
  function link(parent,label,url){const a=document.createElement('a');a.textContent=label;a.href=url;a.target='_blank';a.rel='noopener noreferrer';parent.append(a);}
  function evidence(parent,title,values){const section=document.createElement('section'),h=document.createElement('h3'),ul=document.createElement('ul');h.textContent=title;for(const text of values){const li=document.createElement('li');li.textContent=text;ul.append(li);}section.append(h,ul);parent.append(section);}
  fetch('/api/targets').then(async response=>{if(!response.ok)throw new Error((await response.json()).error);return response.text();}).then(text=>{
    const data=JSON.parse(text),target=data.primary_investigation_target;programText=text;
    el('target-name').textContent=target.event_id;
    el('category').textContent=target.investigation_category;
    el('selection').textContent='Provisional lead for independent evaluation. This is a previously published candidate, not a new engine discovery. Its placement here is a research priority, not a calibrated black-hole ranking.';
    evidence(el('case-evidence'),'Why investigate?',target.evidence_for);
    evidence(el('case-evidence'),'What could change the interpretation?',target.evidence_against_or_unresolved);
    el('next-observation').textContent='Next evidence: '+target.next_observation;
    link(el('citation'),target.source.title,target.source.url);
    for(const item of target.literature_alternatives){const tr=document.createElement('tr');for(const value of [item.photometric_mode,item.mass_prior,item.branch,(item.published_branch_weight*100).toFixed(1)+'%',String(item.published_mass_posterior_median_msun)]){const td=document.createElement('td');td.textContent=value;tr.append(td);}el('alternatives').append(tr);}
    el('known-name').textContent=data.known_black_hole_validation_benchmark.event_id;
    el('known-status').textContent='Published positive reference. Independent tracker recovery remains unaccepted.';
    el('control-name').textContent=data.non_black_hole_comparison.event_id;
    el('control-status').textContent='Published brown-dwarf lens; it has not been independently recovered by this engine.';
    link(el('control-citation'),'Primary study',data.non_black_hole_comparison.source_url);
    el('gate').textContent=data.publication_gate.ready?'Evidence gate completed':'Publication held for evidence review';
    for(const reason of data.publication_gate.reasons){const li=document.createElement('li');li.textContent=reason;el('gate-reasons').append(li);}
    el('bhsm').textContent=data.bhsm_interpretation;el('provenance').textContent=JSON.stringify(data,null,2);
    el('export').disabled=false;el('status').textContent='Target program verified. Primary candidate: '+target.event_id+'; scientific publication readiness: '+String(data.publication_gate.ready)+'.';
  }).catch(error=>{el('status').textContent=error.message;});
  el('export').addEventListener('click',()=>{if(!programText)return;const url=URL.createObjectURL(new Blob([programText],{type:'application/json;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='BHSM_Primary_Target_Evidence.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);});
})();
