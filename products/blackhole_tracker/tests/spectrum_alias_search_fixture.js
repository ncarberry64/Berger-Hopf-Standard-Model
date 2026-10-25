'use strict';
// Exercise the installed viewer's actual functions, without DOM/network/fit calls.
const fs=require('fs'),zlib=require('zlib'),vm=require('vm'),assert=require('assert');
const html=zlib.gunzipSync(fs.readFileSync(process.argv[2])).toString('utf8');
const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)];assert.strictEqual(scripts.length,2);
const runtime=scripts[1][1],identity=runtime.match(/^const trackViewerIdentity=.*$/m),ids=runtime.match(/^const trackControlIds=.*$/m);assert(identity&&ids);
const declarations=[...runtime.matchAll(/^function\s+(\w+)\(/gm)];
function extract(name){const i=declarations.findIndex(d=>d[1]===name);assert(i>=0,name);const s=runtime.slice(declarations[i].index,i+1<declarations.length?declarations[i+1].index:runtime.length).replace(identity[0]+'\n','').trim();new vm.Script('('+s+')');return s}
const names=['canonicalViewValue','sameViewValue','optionalPositive','qualifiedMembershipAliases','passesUnknownKept','filterTrackRecords','trackViewState','trackViewEnvelope','csvCell','canonicalCsvValue','trackViewCsv','parseTrackCsv','validateTrackView','trackViewFromCsv'];
const context={assert,payload:scripts[0][1],summary:null};vm.createContext(context);
const source=`
const data=JSON.parse(payload),all=data.points,byId=new Map(all.map(p=>[p.point_id,p]));
${identity[0]}
${ids[0]}
${names.map(extract).join('\n')}
const blank=()=>Object.fromEntries(trackControlIds.map(k=>[k,'']));
let filters=blank(),filtered=all,sequenceIds=[],selected=null,viewValidationError=null;
function currentTrackFilters(){return filters}
const matches=q=>filterTrackRecords(all,{...blank(),search:q});
const known=all.find(p=>p.event_id==='OGLE-2011-BLG-0462');assert(known);
assert.strictEqual(known.known_label,'LITERATURE_POSITIVE_BH_BENCHMARK');assert.strictEqual(known.mass_msun,null);
const counts={};for(const query of ['OB110462','MOA-2011-BLG-191','OGLE-11-462','OGLE-2011-BLG-0462',' ob110462 ']){const points=matches(query);assert.deepStrictEqual(points.map(p=>p.point_id),[known.point_id]);counts[query]=points.length}
assert.strictEqual(matches('Gaia18ajz').length,0);
const invented={...known,point_id:'INVENTED',event_id:'INVENTED',source_id_string:null,aliases:[],catalog_search_names:[],SIMBAD:{aliases:['CONTEXT-NEIGHBOR']},native_catalog_membership_evidence:[{aliases:['DIRECT-ONLY'],Gaia:{aliases:['CONTEXT-NEIGHBOR']}}]};
assert.strictEqual(filterTrackRecords([invented],{...blank(),search:'CONTEXT-NEIGHBOR'}).length,0);assert.strictEqual(filterTrackRecords([invented],{...blank(),search:'DIRECT-ONLY'}).length,1);
for(const value of [null,{},'CONTEXT-NEIGHBOR']){invented.native_catalog_membership_evidence=value;assert.deepStrictEqual(qualifiedMembershipAliases(invented),[]);assert.strictEqual(filterTrackRecords([invented],blank()).length,1)}
filters={...blank(),search:'OB110462'};filtered=matches(filters.search);sequenceIds=[all.find(p=>p.evidence_status==='INADEQUATE').point_id,all.find(p=>p.evidence_status==='NUMERICALLY_UNRESOLVED').point_id];
const current=trackViewEnvelope();assert.strictEqual(current.viewer_identity.view_revision,'v11');assert.strictEqual(current.viewer_identity.data_revision,'v10');
validateTrackView(JSON.parse(JSON.stringify(current)));const round=trackViewFromCsv(trackViewCsv(current));assert.deepStrictEqual(round.viewer_identity,current.viewer_identity);assert.deepStrictEqual(round.points,current.points);assert.deepStrictEqual(round.sequence_records,current.sequence_records);
const bad=JSON.parse(JSON.stringify(current));delete bad.viewer_identity;bad.displayed_point_ids=[];bad.points=[];assert.throws(()=>validateTrackView(bad),/Displayed identities/);assert.throws(()=>trackViewFromCsv(trackViewCsv(bad)),/Displayed identities/);
filters={...blank(),search:'OGLE-2011-BLG-0462'};filtered=matches(filters.search);const legacy=trackViewEnvelope();delete legacy.viewer_identity;validateTrackView(legacy);trackViewFromCsv(trackViewCsv(legacy));
const unknown=JSON.parse(JSON.stringify(current));unknown.viewer_identity.view_revision='UNKNOWN';assert.throws(()=>validateTrackView(unknown),/different viewer/);
summary={passed:true,known_alias_counts:counts,context_neighbor_matches:0,gaia18ajz_historical_matches:0,view_revision:current.viewer_identity.view_revision,data_revision:current.viewer_identity.data_revision,json_csv_replay:true,hidden_sequence_count:round.sequence_records.length,legacy_wrong_subset_refused:true,legacy_canonical_compatible:true,unknown_viewer_refused:true};
`;
new vm.Script(source).runInContext(context,{timeout:60000});process.stdout.write(JSON.stringify(context.summary)+'\n');
