'use strict';
(() => {
  const el=id=>document.getElementById(id);
  const status=message=>{el('status').textContent=message;};
  let resultText=null, loadedInputText=null, generation=0;
  const inputText=()=>loadedInputText===null?el('input-json').value:loadedInputText;
  function loadInput(text){loadedInputText=text;el('input-json').value=text;}
  const numeric=v=>typeof v==='number'&&Number.isFinite(v);
  const fmt=v=>numeric(v)?v.toPrecision(6):'Unavailable';
  const tail=v=>v===0?'Below floating-point range':fmt(v);
  async function request(path,body){
    const response=await fetch(path,{method:body===undefined?'GET':'POST',headers:body===undefined?{}:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
    if(!response.ok){let error;try{error=(await response.json()).error;}catch{error='Local request failed.';}throw new Error(error);}
    return response;
  }
  function clearResult(){generation++;resultText=null;el('download').disabled=true;el('result').replaceChildren();const h=document.createElement('h2');h.textContent='Track evidence';el('result').append(h);el('track-plot').replaceChildren();el('plot-caption').textContent='No measured track loaded.';}
  function row(dl,label,value){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;dl.append(dt,dd);}
  function svg(tag,attributes,text){const node=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [key,value] of Object.entries(attributes))node.setAttribute(key,String(value));if(text!==undefined)node.textContent=text;el('track-plot').append(node);return node;}
  function plot(result){
    const input=result.dataset_input, points=input.rows.map(r=>r.position_mas), predicted=result.predictions_mas;
    const variance=i=>input.noise.covariance_kind==='FULL_2N'?[input.full_covariance_mas2[2*i][2*i],input.full_covariance_mas2[2*i+1][2*i+1]]:[input.rows[i].covariance_mas2[0][0],input.rows[i].covariance_mas2[1][1]];
    const ranges=[0,1].map(axis=>{const values=points.flatMap((p,i)=>[p[axis]-Math.sqrt(variance(i)[axis]),p[axis]+Math.sqrt(variance(i)[axis]),predicted[i][axis]]);let lo=Math.min(...values),hi=Math.max(...values),span=hi-lo;if(!(span>0))span=1;return [lo-span*.12,hi+span*.12];});
    const x=v=>82+(v-ranges[0][0])/(ranges[0][1]-ranges[0][0])*760,y=v=>353-(v-ranges[1][0])/(ranges[1][1]-ranges[1][0])*310;
    el('track-plot').replaceChildren();svg('line',{x1:82,y1:353,x2:842,y2:353,class:'axis'});svg('line',{x1:82,y1:43,x2:82,y2:353,class:'axis'});
    for(let i=0;i<=4;i++){const a=ranges[0][0]+i/4*(ranges[0][1]-ranges[0][0]),b=ranges[1][0]+i/4*(ranges[1][1]-ranges[1][0]);svg('text',{x:x(a),y:375,'text-anchor':'middle'},fmt(a));svg('text',{x:72,y:y(b)+4,'text-anchor':'end'},fmt(b));}
    svg('text',{x:450,y:403,'text-anchor':'middle'},'East offset (mas)');svg('text',{x:15,y:22},'North offset (mas)');
    const order=input.rows.map((r,i)=>i).sort((a,b)=>input.rows[a].native_time-input.rows[b].native_time);
    svg('polyline',{points:order.map(i=>x(predicted[i][0])+','+y(predicted[i][1])).join(' '),class:'fit'});
    points.forEach((p,i)=>{const v=variance(i),sx=Math.sqrt(v[0]),sy=Math.sqrt(v[1]);svg('line',{x1:x(p[0]-sx),y1:y(p[1]),x2:x(p[0]+sx),y2:y(p[1]),class:'error'});svg('line',{x1:x(p[0]),y1:y(p[1]-sy),x2:x(p[0]),y2:y(p[1]+sy),class:'error'});const point=svg('circle',{cx:x(p[0]),cy:y(p[1]),r:4,class:'sample'});const title=document.createElementNS('http://www.w3.org/2000/svg','title');title.textContent=input.rows[i].source_row_id+' · native epoch '+input.rows[i].native_time;point.append(title);svg('text',{x:x(p[0])+7,y:y(p[1])-7},String(i+1));});
    const first=input.rows[order[0]].native_time,last=input.rows[order[order.length-1]].native_time;
    el('plot-caption').textContent='Native epochs '+first+' → '+last+' '+input.time.native_unit+'; '+input.time.convention+'; clock '+input.time.scale+'. Row numbers identify the original input order. Gold: supplied lens positions; gray: marginal 1σ bars; teal: fitted path in time order. The fit uses the full supplied covariance; bars do not display its correlations.';
  }
  function render(text,verification){
    const result=JSON.parse(text);resultText=text;el('download').disabled=false;
    const container=el('result');container.replaceChildren();const h=document.createElement('h2');h.textContent='Track evidence';container.append(h);const dl=document.createElement('dl');container.append(dl);
    row(dl,'Input identity',result.dataset_input.lens_id);
    row(dl,'Dataset kind',result.dataset_input.metadata?.synthetic===true?'SYNTHETIC CONTROL':result.dataset_input.position_origin);
    row(dl,'Track assessment',result.status);
    row(dl,'Angular motion (E, N)',result.parameters.angular_motion_mas_per_Julian_year.map(fmt).join(', ')+' mas / Julian year');
    row(dl,'Motion component errors',result.standard_errors.angular_motion_mas_per_Julian_year.map(fmt).join(', ')+' mas / Julian year');
    row(dl,'χ² / degrees of freedom',fmt(result.diagnostics.chi_square)+' / '+result.diagnostics.degrees_of_freedom);
    row(dl,'Residual upper-tail probability',tail(result.diagnostics.chi_square_upper_probability));
    row(dl,'Stationary-motion probability',tail(result.diagnostics.stationary_null_probability));
    row(dl,'Black-hole identity','Unavailable from this route');
    row(dl,'Mass / distance / physical speed','Unavailable');
    row(dl,'Replay',verification?'Verified against the installed method; this is a consistency check.':'Export is available; reopen to verify the saved track.');
    const note=document.createElement('p');note.textContent='Probabilities depend on the declared Gaussian covariance and rectilinear model. No significance threshold or black-hole classification is applied by this view.';container.append(note);
    for(const value of result.qualifications||[]){const p=document.createElement('p');p.textContent=typeof value==='string'?value:JSON.stringify(value);container.append(p);}
    const details=document.createElement('details'),summary=document.createElement('summary'),pre=document.createElement('pre');summary.textContent='Full result, covariance and provenance';pre.textContent=text;details.append(summary,pre);container.append(details);plot(result);
  }
  function bind(id,action){el(id).addEventListener('click',async()=>{const button=el(id),current=generation;button.disabled=true;try{await action();}catch(error){if(current===generation)status(error.message);}finally{button.disabled=id==='download'&&!resultText;}});}
  el('input-json').addEventListener('input',()=>{loadedInputText=null;clearResult();});
  bind('demo',async()=>{const current=generation,value=await (await request('/api/skytrack/example')).json();if(current!==generation)return;loadInput(value.dataset_json);clearResult();status('Synthetic demonstration loaded. These positions are invented controls, not observations or a black-hole discovery.');});
  bind('validate',async()=>{const current=generation,value=await (await request('/api/skytrack/validate',{dataset_json:inputText()})).json();if(current!==generation)return;status('Input admitted for conditional angular-track fitting: '+JSON.stringify(value.summary));});
  bind('fit',async()=>{const current=generation;status('Fitting the supplied angular track…');const value=await (await request('/api/skytrack/fit',{dataset_json:inputText()})).json();if(current!==generation)return;render(value.result_json,false);status('Track fit complete. Read the model, noise and association qualifications before interpreting motion.');});
  bind('replay',async()=>{const current=generation,text=resultText||inputText();const value=await (await request('/api/skytrack/replay',{result_json:text})).json();if(current!==generation)return;render(value.result_json,true);loadInput(JSON.parse(value.result_json).dataset_input_json);status('Replay verified: saved input, configuration and numerical track agree with the installed method.');});
  bind('download',async()=>{if(!resultText)throw new Error('Fit or verify a saved track first.');const current=generation,response=await request('/api/skytrack/export',{result_json:resultText}),blob=await response.blob();if(current!==generation)return;const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='BHSM_Moving_Lens_Replay.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);status('Replay exported with the original input text, uncertainties, identities and BHSM interpretation.');});
  bind('reset',async()=>{loadedInputText=null;el('input-json').value='';el('track-file').value='';clearResult();status('Workspace cleared. Open a measured track or the synthetic demonstration.');});
  el('track-file').addEventListener('change',async()=>{const file=el('track-file').files[0];if(!file)return;clearResult();loadedInputText=null;el('input-json').value='';const current=generation;try{if(file.size>32_000_000)throw new Error('The browser replay file limit is 32 MB.');const text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(await file.arrayBuffer());if(current!==generation)return;if(file.size>8_000_000&&JSON.parse(text).schema!=='bhtracker.measured_lens_skytrack_result.v1')throw new Error('The browser track input limit is 8 MB; larger supported inputs use the Python/CLI route.');loadInput(text);status('File loaded: '+file.name+'. Validate input or verify replay before using it.');}catch(error){if(current===generation)status(error.message);}});
})();
