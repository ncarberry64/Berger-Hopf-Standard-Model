"""Apply retained curvature/Green to the complete canonical lepton wall image."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_parent_positive_open_current import actual_positive_open_current_application
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    base=ROOT/'artifacts/muon_parent_positive_gauge_form_20261011/run_1'
    receipt=json.loads((base/'result.json').read_bytes());hashes=dict(receipt['input_hashes']);records=[];files={};out.mkdir(parents=True)
    hashes[(base/'result.json').relative_to(ROOT).as_posix()]=sha256((base/'result.json').read_bytes()).hexdigest()
    for side in ('incoming','outgoing'):
        gauge={}
        for part in ('action','hilbert','green'):
            path=base/(side+'_'+part+'.npz');p=path.relative_to(ROOT).as_posix();h=sha256(path.read_bytes()).hexdigest()
            if h!=receipt['numerical_files'][path.name]['sha256']:raise ValueError('same action/Gram/Green binding changed')
            hashes[p]=h
            with np.load(path,allow_pickle=False) as a:gauge.update({k:a[k].copy() for k in a.files})
        b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        hashes.update(b['input_hashes']);f=magnetic_open_fields_at_node(b,b['source']['times'][2])
        if not np.array_equal(f['raw_fields'],gauge['raw_fields']):raise ValueError('same raw current/operator background required')
        r=actual_positive_open_current_application(f['raw_fields'],b['representation'],gauge)
        path=out/(side+'_application.npz');deterministic_archive(path,{k:v for k,v in r.items() if isinstance(v,np.ndarray)})
        if path.stat().st_size>10*1024**2:raise ValueError('lossless archive exceeds publication limit')
        files[path.name]=dict(sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
        records.append(dict(side=side,full18_current_curvature_form_norm=float(np.linalg.norm(r['full18_open_current_curvature_form'])),
            stable_wall_curvature_return_norm=float(np.linalg.norm(r['stable_wall_curvature_Green_return'])),
            full18_current_curvature_Green_return_cap_norm=float(np.linalg.norm(r['full18_open_current_curvature_Green_return_cap'])),
            current_image_Lorenz_relative_defect=r['current_image_Lorenz_relative_defect'],
            no_curvature_inverse_majorant=r['no_curvature_inverse_majorant'],
            common_cap_action_Maxwell_factor=r['common_cap_action_Maxwell_factor']))
        print(json.dumps(dict(stage='actual_full18_open_wall_current',**records[-1]),sort_keys=True),flush=True)
    for p in ('src/bhsm/interface/muon_parent_positive_open_current.py','src/bhsm/interface/muon_parent_positive_gauge_form.py',
        'src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py','src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',
        'src/bhsm/interface/muon_parent_mean_causal_action.py',Path(__file__).relative_to(ROOT).as_posix()):hashes[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise RuntimeError('consumed owner changed')
    result=dict(classification='EVALUATED_ACTUAL_FULL18_OPEN_WALL_CURRENT_YM_CURVATURE_CONTRACTION',input_hashes=hashes,
        numerical_files=files,records=records,
        gyromagnetic_operator='nonuniform weighted deltaF†deltaF plus literal <F,delta²F> and finite Lorenz fixing; canonical D_strat restriction not asserted',
        current_angular_normalization='phi_h=Y_h/sqrt(V),phi0=1/sqrt(V), int dOmega Y_hY_j=Vdelta; no extraV in vertex',
        current_pointwise_canonical_field='chi_point=R4^(3/2)psi_point/V; constant angular coefficient is sqrt(V)*chi_point',
        physical_Lorenz_Gauss_BRST_quotient_or_LSZ_completed=False,
        intermediate_fermion_Green_inserted=False,
        intrinsic_Higgs_gauge_boundary_mass_and_mixed_rows_included=False,
        complete_native_quantum_Sigma_or_normalized_Pauli_assigned=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 same stored finite action/Gram current contraction and stable inverse difference; normalized inverse majorants exclude operator/Gram production and physical matching. These norms are not anomaly bounds.')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],records=records,numerical_files=files)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.output),sort_keys=True))
