"""Apply both energy source legs to the complete original current transfer."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_chronological_literal_current_source import literal_point_current_sources
from bhsm.interface.muon_chronological_current_energy import (
    literal_point_energy_sources,chronological_energy_transfer_chunk,
    clock_origin_energy_contacts)


def materialize(current_folder,action_folder,output):
    base=ROOT/current_folder;action=ROOT/action_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve all current energy applications')
    refs={}
    def read(p,expected=None):
        h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same current energy operand changed: '+str(p))
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(base/'result.json');am=read(action/'result.json')
    if md['classification']!='EVALUATED_WHOLE_ORIGINAL_N1_LITERAL_CURRENT_AND_TRANSPOSE_ADJOINT':
        raise ValueError('same complete original current solve required')
    if md['current_kind']!='literal':raise ValueError('complete original gauge/H wall vertices required')
    refs.update(md['input_hashes']);refs.update(am['input_hashes'])
    inc=read(action/'original_n1_angular_and_source_incidence.npz',am['archives']['original_n1_angular_and_source_incidence.npz']['sha256'])
    pieces=[read(p,am['archives'][p.name]['sha256'])for p in
        sorted(action.glob('owned_current_point_sources_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1]))]
    points={k:np.concatenate([a[k]for a in pieces])for k in pieces[0]};del pieces
    arm=np.asarray(inc['quadrature_provenance'][:,5].real,int)
    at=np.flatnonzero(arm==(0 if md['source_side']=='incoming'else 1))
    labels=points['rows'][at,:,0].real.astype(int)
    if not np.array_equal(labels,points['rows'][at,:,0]):raise ValueError('all exact chronological source nodes required')
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),
        'src/bhsm/interface/muon_chronological_current_energy.py','tests/test_muon_chronological_current_energy.py',
        'scripts/evaluate_muon_reached_trace_action.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True);archives={};records=[];maxsource=0.
    def save(name,data):
        p=out/name;deterministic_archive(p,data)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split complete energy matrices')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    names=('source_transfer','independent_transpose_transfer','left_energy_leg','right_energy_leg',
           'continued_energy_first','real_proper_frequency_first')
    totals={k:np.zeros((288,288),complex)for k in names}
    tau=points['current_proper_clock'][at]
    origin=complex(tau[0])
    for spectator in range(2):
        Rlift=inc['right_current_field_source_lifts'][spectator]
        Llift=inc['literal_left_current_field_source_lifts'][spectator]
        summed={k:np.zeros((288,288),complex)for k in names}
        initialR=np.zeros((176,288),complex);initialL=np.zeros_like(initialR)
        for start in range(1,1151,8):
            stop=min(start+8,1151);count=stop-start
            fields={k:[]for k in('original_literal_left_transpose_source','original_literal_right_current_source',
                                 'original_current_response','original_transpose_current_adjoint')}
            for spin in range(6):
                name=f'spectator_{spectator}_external_{spin}_nodes_{start}.npz'
                a=read(base/name,md['archives'][name]['sha256'])
                if not np.array_equal(a['source_column_indices'],np.arange(spin*48,(spin+1)*48)):
                    raise ValueError('same complete288 column order required')
                for k in fields:fields[k].append(a[k])
            a={k:np.concatenate(v,axis=2)for k,v in fields.items()}
            jr=np.zeros((count,176,288),complex);jl=np.zeros_like(jr)
            re=np.zeros_like(jr);le=np.zeros_like(jr)
            hit=at[np.flatnonzero(np.any((labels>=start)&(labels<stop),axis=1))]
            for iq in hit:
                S=literal_point_current_sources(points['current_vertices'][iq,md['family']-1],
                    points['current_FE2_values'][iq],Rlift,Llift)
                SE=literal_point_energy_sources(S,points['current_proper_clock'][iq])
                for j,p,d in points['rows'][iq]:
                    j=int(j.real)
                    if not start<=j<stop:continue
                    m=complex(points['measure'][iq])*complex(p);k=j-start
                    jr[k,:168]+=m*S['literal_right_source'];jl[k,:168]+=m*S['literal_left_transpose_source']
                    re[k,:168]+=m*SE['literal_right_energy_source'];le[k,:168]+=m*SE['literal_left_energy_source']
            maxsource=max(maxsource,float(np.max(abs(jr-a['original_literal_right_current_source']))),
                float(np.max(abs(jl-a['original_literal_left_transpose_source']))))
            # Source reconstruction uses the identical node order and map.
            scale=max(float(np.max(abs(jr))),float(np.max(abs(jl))),np.finfo(float).tiny)
            if maxsource>64*np.finfo(float).eps*scale:
                raise ArithmeticError('energy legs are not on the same saved literal source')
            c=chronological_energy_transfer_chunk(a['original_literal_left_transpose_source'],
                a['original_literal_right_current_source'],a['original_current_response'],
                a['original_transpose_current_adjoint'],le,re)
            for k in names:summed[k]+=c[k]
            if start in(569,1145):
                save(f'spectator_{spectator}_energy_sources_node_{start}.npz',dict(
                    original_node_start=np.array(start),left_energy_source=le,right_energy_source=re,
                    same_source_reconstruction_left=jl-a['original_literal_left_transpose_source'],
                    same_source_reconstruction_right=jr-a['original_literal_right_current_source']))
            if (start-1)%128==0:
                print(json.dumps(dict(stage='complete288_ordered_energy_legs',spectator=spectator,
                    original_nodes_done=stop-1,same_source_reconstruction_max=maxsource)),flush=True)
        # The held initial source is still an explicit conormal operand.
        for iq in at[np.flatnonzero(np.any(labels==0,axis=1))]:
            S=literal_point_current_sources(points['current_vertices'][iq,md['family']-1],
                points['current_FE2_values'][iq],Rlift,Llift)
            SE=literal_point_energy_sources(S,points['current_proper_clock'][iq])
            for j,p,d in points['rows'][iq]:
                if j.real==0:
                    m=complex(points['measure'][iq])*complex(p)
                    initialR[:168]+=m*SE['literal_right_energy_source']
                    initialL[:168]+=m*SE['literal_left_energy_source']
        contacts=clock_origin_energy_contacts(summed['source_transfer'],summed['independent_transpose_transfer'],origin)
        save(f'spectator_{spectator}_complete288_current_energy.npz',dict(**summed,**contacts,
            initial_right_energy_source_reaction=initialR,initial_left_energy_source_reaction=initialL))
        for k in names:totals[k]+=summed[k]
        records.append(dict(spectator=spectator,left_energy_leg_norm=float(np.linalg.norm(summed['left_energy_leg'])),
            right_energy_leg_norm=float(np.linalg.norm(summed['right_energy_leg'])),
            continued_energy_first_norm=float(np.linalg.norm(summed['continued_energy_first'])),
            independent_transpose_difference_max=float(np.max(abs(summed['source_transfer']-summed['independent_transpose_transfer']))),
            clock_origin_cancellation_max=float(np.max(abs(contacts['clock_origin_cancellation'])))))
    contacts=clock_origin_energy_contacts(totals['source_transfer'],totals['independent_transpose_transfer'],origin)
    save('complete288_current_energy.npz',dict(**totals,**contacts,source_column_shape=np.array([6,2,6,4]),
        source_proper_clock=tau,source_quadrature_indices=at,source_energy_anchor=np.array(0.)))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(Path(path).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same current energy pins changed')
    result=dict(classification='EVALUATED_WHOLE_ORIGINAL_COMPLETE288_CURRENT_BOTH_ORDERED_SOURCE_ENERGY_LEGS',
        input_hashes=refs,archives=archives,source_side=md['source_side'],family=md['family'],records=records,
        energy_equation='C_E=J_L,E^T u+p^T J_R,E; J_L,E=+tau_E J_L; J_R,E=-tau_E J_R',
        source_energy_anchor=0.,source_energy_is_continued_owned_proper_clock_germ=True,
        real_proper_frequency_first_is_i_times_continued_energy_first=True,
        same_source_reconstruction_max=maxsource,source_transfer_norm=float(np.linalg.norm(totals['source_transfer'])),
        left_energy_leg_norm=float(np.linalg.norm(totals['left_energy_leg'])),
        right_energy_leg_norm=float(np.linalg.norm(totals['right_energy_leg'])),
        continued_energy_first_norm=float(np.linalg.norm(totals['continued_energy_first'])),
        independent_transpose_difference_max=float(np.max(abs(totals['source_transfer']-totals['independent_transpose_transfer']))),
        clock_origin_cancellation_max=float(np.max(abs(contacts['clock_origin_cancellation']))),
        all_original_Gauss_frame_initial_freefinal_and_corner_rows_retained=True,
        computational_FE2_test_extension_to_exterior_supplied=False,
        fixed_background_field_operator_energy_derivative_zero_by_declared_source_graph=True,
        physical_pole_or_LSZ_or_lifetime_normalization_identified=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 complete source-energy adjoint contraction. Same-source reconstruction and original transpose pairing defects are explicit. Upstream action/source production and physical exterior matching are not bounded by these defects.')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),continued_energy_first_norm=result['continued_energy_first_norm'],
        same_source_reconstruction_max=maxsource)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--current-folder',type=Path,required=True)
    p.add_argument('--action-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.current_folder,a.action_folder,a.output)
