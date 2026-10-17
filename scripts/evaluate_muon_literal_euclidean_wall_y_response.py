"""Evaluate common-Y coefficients of the same coupled natural-wall current."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_literal_euclidean_higgs_green import _read
from bhsm.interface.muon_literal_euclidean_wall_y_response import joint_wall_current_y_coefficients
from bhsm.interface.muon_euclidean_angular_weak_action import euclidean_node_field_images
from bhsm.interface.muon_continued_action_reality import action_reality_coefficient,actual_source_curve_coefficients
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous current coefficients')
    refs={};pending=[];records=[]
    def receipt(folder):
        p=ROOT/folder/'result.json';refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        return json.loads(p.read_bytes())
    wall='artifacts/muon_literal_euclidean_wall_action_20261011/run_2';wm=receipt(wall)
    eu='artifacts/muon_piecewise_euclidean_action_20261011/run_2';em=receipt(eu)
    source='artifacts/muon_corrected_profile_magnetic_response_20261011/run_1';sm=receipt(source)
    for side in('incoming','outgoing'):
        phase,_=retained_input(side,refs)
        data=[_read(ROOT/source/f'{side}_{key}.npz',refs,sm['array_archives'][f'{side}_{key}.npz']['sha256'])for key in('phase','velocity','contacts')]
        curves=actual_source_curve_coefficients(*data)
        nodes=_read(ROOT/eu/f'{side}_nodes.npz',refs,em['archives'][f'{side}_nodes.npz']['sha256'])
        nodes['total_proper_clock']=next(r['total_proper_clock']for r in em['records']if r['side']==side)
        fields=euclidean_node_field_images(phase,curves,nodes);fi=FAMILY_INDICES[1]
        for key,zkey in(('H','coordinate_offset'),('Hsharp','reflected_coordinate_offset')):
            nodes[key]=np.array([action_reality_coefficient(phase,float(t),z)['Hcan'][np.ix_(fi,fi)]
                for t,z in zip(nodes['coordinate_anchor'],nodes[zkey])])
        point=_read(ROOT/wall/f'{side}_original_nodes.npz',refs,wm['archives'][f'{side}_original_nodes.npz']['sha256'])
        key=f'{side}_cells_2_field_original_action_Green.npz'
        green=_read(ROOT/wall/key,refs,wm['archives'][key]['sha256'])['original_action_Green']
        app=joint_wall_current_y_coefficients(nodes,fields,point['E'],green,point['wall_trace_map'],temporal_cells=2,order=3)
        arrays={k:v for k,v in app.items()if isinstance(v,np.ndarray)}
        direct=[]
        for family in(1,2):
            key=f'{side}_family_{family}_cells_2_current.npz'
            direct.append(_read(ROOT/wall/key,refs,wm['archives'][key]['sha256'])['open_Gaussian_current'])
        arrays['physical_Y_raw_paired_subtraction_diagnostic']=direct[0]-direct[1]
        arrays['shared_coefficient_vs_raw_subtraction_difference']=app['paired_current_coefficients_through_order']-arrays['physical_Y_raw_paired_subtraction_diagnostic']
        pending.append((side+'_coefficients.npz',arrays))
        record=dict(side=side,current_coefficient_norms=[float(np.linalg.norm(a))for a in app['current_Y_coefficients']],
            continued_energy_coefficient_norms=[float(np.linalg.norm(a))for a in app['continued_energy_first_Y_coefficients']],
            paired_coefficient_current_norm=float(np.linalg.norm(app['paired_current_coefficients_through_order'])),
            raw_physical_Y_subtraction_norm=float(np.linalg.norm(arrays['physical_Y_raw_paired_subtraction_diagnostic'])),
            shared_vs_raw_subtraction_difference_norm=float(np.linalg.norm(arrays['shared_coefficient_vs_raw_subtraction_difference'])),
            relative_operator_perturbation_norm_estimates=app['finite_operator_relative_perturbation_norm'])
        records.append(record);print(json.dumps(dict(stage='shared_literal_joint_wall_Y_current',**record),sort_keys=True),flush=True)
    for name in('muon_literal_euclidean_wall_y_response','muon_literal_euclidean_wall_action','muon_euclidean_angular_weak_action','muon_continued_action_reality'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    for p in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_literal_euclidean_wall_y_response.py'):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed original current changed')
    out.mkdir(parents=True);archives={}
    for name,arrays in pending:
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024*1024:raise ArithmeticError('split packaging without pruning')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    result=dict(classification='EVALUATED_SHARED_Y_LITERAL_COUPLED_WALL_CURRENT_AND_ENERGY_COEFFICIENTS',input_hashes=refs,archives=archives,records=records,
        Y0='analytic Taylor coefficient of actual fixed H/gauge/geometry; no physical H=0 state or matched external pole mass stripped',
        recurrence='G_j=-G0(K1 G_jminus1+K2 G_jminus2); all odd coefficients retained; literal left/numerator coefficient contacts retained',
        energy='analytic continued Lorentz external phase dual +tau and right -tau contacts; no internal operator continuation inferred',
        physical_pole_mass_counterterm_match_completed=False,common_native_cutoff=None,physical_F2=None,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary common coefficient current, shared full672 inverse and finiteFE; perturbation norms are estimates, not outward Taylor or physical error bounds')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.output)
