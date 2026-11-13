"""Export the actual corrected full18 body and analytic coordinate germ."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_chronological_current_body import chronological_current_body_point
from bhsm.interface.muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts


def materialize(action_folder,output):
    base=ROOT/action_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every body matching application')
    refs={}
    def read(p,expected=None):
        h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and expected!=h:raise ValueError('same current field germ changed')
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(base/'result.json');refs.update(md['input_hashes'])
    incidence=read(base/'original_n1_angular_and_source_incidence.npz',md['archives']['original_n1_angular_and_source_incidence.npz']['sha256'])
    x=incidence['same_n0_field_values'];pr=incidence['quadrature_provenance'];phases={};lifts={}
    for side in('incoming','outgoing'):
        phases[side],_=retained_input(side,refs)
        lifts[side]=chronological_n0_field_lifts(phases[side]['representation'],incidence['original_value_permutation'])
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(Path(path).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_chronological_current_body.py',
        'scripts/evaluate_muon_continued_current_factor.py','scripts/evaluate_muon_reached_trace_action.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True);archives={};rows=[];index=0;maxR=0.;maxH=0.;maxDelta=0.;maxTime=0.
    def save(name,data):
        p=out/name;deterministic_archive(p,data)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split every complete body/germ array')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def flush():
        nonlocal rows,index
        if not rows:return
        save(f'corrected_full18_body_points_{index}.npz',{k:np.array([r[k]for r in rows])for k in rows[0]})
        index+=len(rows);rows=[]
    for path in sorted(base.glob('owned_current_point_sources_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1])):
        points=read(path,md['archives'][path.name]['sha256'])
        for k,iq in enumerate(points['original_quadrature_index']):
            iq=int(iq);p=pr[iq];anchor,z=p[:2];N=points['N'][k];clock=p[3]
            side='incoming'if p[5].real==0 else'outgoing'
            (j,pj,dj),(l,pl,dl)=points['rows'][k];j,l=int(j.real),int(l.real)
            v=pj*x[j]+pl*x[l];t=1j*N/clock*(dj*x[j]+dl*x[l])
            a=chronological_current_body_point(phases[side],float(anchor.real),z,v,t,lifts[side])
            hd=float(np.max(abs(a['H_realified']-points['updated_H_realified'][k])))
            rd=float(abs(a['R']-points['R'][k]));maxR=max(maxR,rd);maxH=max(maxH,hd)
            if hd!=0:raise ValueError('same actual homogeneous scalar coefficient changed')
            maxDelta=max(maxDelta,float(np.linalg.norm(a['Hcan']-a['original_base_Hcan'])))
            maxTime=max(maxTime,float(np.linalg.norm(a['Hcan_coordinate_first'])))
            data={k:v for k,v in a.items()if isinstance(v,np.ndarray)or isinstance(v,(complex,float,np.complexfloating))}
            data.update(original_quadrature_index=iq,original_rows=points['rows'][k],source_side=int(p[5].real),
                source_cell=int(p[7].real),coordinate_anchor=float(anchor.real),coordinate_offset=z,
                original_measure=p[2],original_right_clock=p[3],original_reflected_clock=p[4],
                coordinate_slope=p[8],owned_current_FE2_values=points['current_FE2_values'][k],
                owned_current_proper_clock=points['current_proper_clock'][k],
                original_current_vertex_R=points['R'][k],radius_binary_reconstruction_difference=a['R']-points['R'][k])
            rows.append(data)
            if len(rows)==64:flush()
        print(json.dumps(dict(stage='corrected_original_full18_current_body',quadrature_done=index+len(rows),total=3832)),flush=True)
    flush()
    if index!=3832:raise ValueError('all chronological cell and corner body germs required')
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same corrected body source changed')
    result=dict(classification='EVALUATED_CORRECTED_WHOLE_CHRONOLOGICAL_FULL18_CURRENT_BODY_AND_COORDINATE_FIRST_GERM',
        input_hashes=refs,archives=archives,quadrature_nodes=index,original_temporal_nodes=1151,
        body_equation='Hcan=(-i alpha.Omega_space+3gamma5/2)/R+M_fixedY(H)-i Omega_time/N',
        coordinate_first='exact future-coordinate germ of owned affine geometry/parent/reference chart plus piecewise-linear nodal84 correction',
        original_H_coefficient_match_max=maxH,current_radius_binary_reconstruction_difference_max=maxR,
        corrected_body_difference_norm_max=maxDelta,coordinate_first_body_norm_max=maxTime,
        full18_charged_neutral_family_and_fixedY_retained=True,At_coefficient_body_jet_retained=True,
        At_action_kinetic_rate_invented=False,body_coefficients_or_field_tangents_conjugated=False,
        original_converged_classical_graph_not_old_FE2_body=True,original_classical_quantum_gradient_not_assigned_zero=True,
        external_energy_source_anchor_not_retuned=True,physical_pole_or_LSZ_or_native_relative_domain_identified=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 analytic coefficient and first-germ action application on all3832 original chronological points. No exterior state, native graded loop domain, energy analytic continuation or physical matching enclosure inferred.')
    rp=out/'result.json';rp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),files=len(archives),**{k:v for k,v in result.items()if k.endswith('_max')})),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.action_folder,a.output)
