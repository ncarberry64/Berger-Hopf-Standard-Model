"""Apply the complete endpoint formation-source jet to actual joined states."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_inherited_magnetic_endpoint_cotangent import inherited_magnetic_endpoint_cotangent
from bhsm.interface.muon_holomorphic_current_source import two_term_complex_sum
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source_folder,output):
    src=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every joined endpoint action application')
    pins={};archives={}
    def read(p,expected=None):
        raw=p.read_bytes();digest=sha256(raw).hexdigest()
        if not p.is_relative_to(ROOT):raise ValueError('same calling checkout source required')
        pins[p.relative_to(ROOT).as_posix()]=digest
        if expected is not None and digest!=expected:raise ValueError('actual inherited state source pin changed')
        if p.suffix=='.json':return json.loads(raw)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    md=read(src/'result.json');inputs={case:read(src/(case+'_actual_birth_reconstitution_and_source_contacts.npz'),
        md['archives'][case+'_actual_birth_reconstitution_and_source_contacts.npz']['sha256'])for case in('normal_basis','area_source')}
    for n,m in sorted(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if n.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_inherited_magnetic_endpoint_cotangent.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True);records={}
    def metric(x):
        i=np.unravel_index(np.argmax(abs(x)),x.shape);v=x[i]
        return dict(norm=float(np.linalg.norm(x)),maximum=float(abs(v)),worst_index=[int(j)for j in i],worst_complex=[float(v.real),float(v.imag)])
    for case,data in inputs.items():
        a=inherited_magnetic_endpoint_cotangent(data)
        for name in('full_interface_action_cotangent','prescribed_source_action_cotangent','full_minus_source_action_cotangent'):
            if np.max(abs(a[name]-data[name]))>3e-14:raise ValueError('existing joined action/source identity changed')
            hi,lo=two_term_complex_sum(a[name+'_first'][0],a[name+'_first'][1])
            a[name+'_first_combined_high']=hi;a[name+'_first_combined_low']=lo
        p=out/(case+'_complete_endpoint_action_source_first.npz');_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        archives[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        records[case]={name:metric(a[name])for name in('full_interface_action_cotangent','prescribed_source_action_cotangent',
            'full_minus_source_action_cotangent','full_minus_source_action_cotangent_first','prescribed_source_direct_motion','prescribed_source_momentum_motion')}
        records[case]['prescribed_source_first_high_low']=[metric(v)for v in a['prescribed_source_action_cotangent_first']]
        records[case]['original_joined_free_domain_row_max']=md['applications'][case]['free_domain_and_constraint_dual_range_max']
        records[case]['original_joined_canonical_propagated_row_max']=md['applications'][case]['original_propagated_rows_max']
        records[case]['source_on_actual_current_norm']=md['applications'][case]['current_terms']['total']
        print(json.dumps(dict(case=case,**records[case]),sort_keys=True),flush=True)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('source/action bytes changed during consumption')
    result=dict(classification='EVALUATED_JOINED_MAGNETIC_ENDPOINT_FORMATION_SOURCE_COTANGENT_FIRST',
        input_hashes=pins,archives=archives,source_folder=source_folder.as_posix(),applications=records,
        direct_source_motion_and_both_actual_parent_child_Pi_responses_consumed=True,
        high_low_sources_acted_before_products=True,independent_left_not_conjugated=True,
        momentum_kind='original Lorentz canonical Pi; a continued weak cotangent has common -i factor',
        endpoint_cotangent_role='normal/area first jet of actual magnetic bilinear q_parent.T Pi_parent-q_child.T Pi_child; prescribed wall/source contribution retained, not forced zero',
        physical_formation_complete_gamma_clock_exterior_pole_charge_or_Pauli_matched=False,
        next_actual_relation='compose this endpoint source-action contribution with the original full coupled birth formation/energy/gamma(c) rows, then the action-selected exterior Gamma2(E)=Bi+Bf U and Z=L Gamma2_E R; no initial-I replacement',
        previously_computed_outgoing_D3_and_quadratic_scope='zero-Cauchy child controls use different field/rate/first and15-point turn-on; new inherited child uses20 actual-owner source points. Recompute source-dependent D3 K/BF/BR/M, field-force and quadratic both-response contractions on these new points; original signed polynomial/image primitives and stage forms remain reusable',
        missing_native_or_pole_sector_assigned_zero=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='literal binary endpoint action/source contraction and first jet on supplied joined states; source row residuals and complement differences are not a physical or outward error enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),archives=len(archives))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.source_folder,a.output)
