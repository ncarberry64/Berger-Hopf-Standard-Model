"""Archive actual finite computations, including unresolved physical gates."""
from pathlib import Path
from hashlib import sha256
import json
import shutil

REPO=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
WORK=Path(r'C:/Users/carbe/OneDrive/Documents/CODEX')
OUT=REPO/'artifacts/muon_angular_retarded_polynomial_20261015'
FIELD=WORK/'outputs/bhsm_same_stage_n1_weak_field_20261015'


def digest(p):return sha256(p.read_bytes()).hexdigest()


def encoded(x):return (json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists()and dst.read_bytes()!=src.read_bytes():raise RuntimeError('Preserve different old bytes: '+str(dst))
    shutil.copyfile(src,dst);assert digest(src)==digest(dst)


def main():
    pairs=[
        ('angular',WORK/'outputs/bhsm_full_angular_probe_closure_20261015','run_1','run_2',False),
        ('collar_current',WORK/'outputs/bhsm_finite_pole_collar_current_20261015','run_1','run_2',False),
        ('coefficients',FIELD,'coefficients_run_1','coefficients_run_2',False),
        ('ramp_bias',FIELD,'bounded_time_control_run_1','bounded_time_control_run_2',False),
        ('original336_binding',FIELD,'independent_original336_binding_run_1','independent_original336_binding_run_2',False),
        ('polynomial_field',FIELD,'polynomial16_run_1','polynomial16_run_2',False),
        ('polynomial_lepton',WORK/'outputs/bhsm_polynomial_angular_retarded_lepton_20261015','run_3','run_4',False),
        *[(f'midpoint_diagnostic_{n}',FIELD,f'midpoint{n}_run_1',f'midpoint{n}_run_2',True)for n in(8,16,32)],
    ]
    repeated=[]
    for name,base,left,right,compact in pairs:
        a,b=base/left,base/right
        files=sorted(x.name for x in a.iterdir()if x.is_file())
        assert files==sorted(x.name for x in b.iterdir()if x.is_file())
        for f in files:assert(a/f).read_bytes()==(b/f).read_bytes(),(name,f)
        selected=files if not compact else [f for f in files if f=='result.json'or f.startswith('cell_0000_')or f.startswith(f'cell_{int(name.split("_")[-1])-1:04d}_')]
        for run in(left,right):
            for f in selected:copy(base/run/f,OUT/name/run/f)
        repeated.append(dict(component=name,actual_independent_evaluations=[left,right],
            all_actual_output_hashes={f:digest(a/f)for f in files},
            archived_files=selected,omitted_diagnostic_intermediate_samples_still_available_locally=compact))
    # The exact reduced maps are larger than10MiB each. Preserve every byte
    # in fixed4MiB chunks, together with the original filename/hash mapping.
    reduced=FIELD/'reduced_source_maps_run_1';copy(reduced/'result.json',OUT/'reduced_maps/result.json')
    chunkmap=[]
    for index,source in enumerate(sorted(reduced.glob('*.npz'))):
        raw=source.read_bytes();chunks=[]
        for n,start in enumerate(range(0,len(raw),4*1024**2)):
            data=raw[start:start+4*1024**2];target=OUT/f'reduced_maps/stage{index}.{n:03d}.bin';target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists()and target.read_bytes()!=data:raise RuntimeError('Different chunk already exists')
            target.write_bytes(data);chunks.append(dict(path=target.relative_to(OUT).as_posix(),sha256=sha256(data).hexdigest(),bytes=len(data)))
        assert b''.join((OUT/c['path']).read_bytes()for c in chunks)==raw
        chunkmap.append(dict(original_path=str(source),original_name=source.name,sha256=digest(source),bytes=len(raw),chunks=chunks))
    (OUT/'reduced_maps/chunk_manifest.json').write_bytes(encoded(chunkmap))
    scripts=[
        'bhsm_exact_action_balls.py','bhsm_baton_zoo_exact_acb_packets.py',
        'bhsm_full_angular_probe_closure_20261015.py','bhsm_muon_finite_pole_collar_current_20261015.py',
        'bhsm_muon_exact_stage_n1_weak_probe_20261015.py','bhsm_muon_same_stage_retarded_n1_20261015.py',
        'bhsm_muon_same_stage_n1_response_binding_20261015.py','bhsm_muon_n1_ramp_time_control_20261015.py',
        'bhsm_muon_same_stage_n1_reduced_sources_20261015.py','bhsm_muon_shifted_polynomial_retarded_n1_20261015.py',
        'bhsm_finite_angular_retarded_lepton_20261015.py','bhsm_polynomial_angular_retarded_lepton_20261015.py',
    ]
    for name in scripts:copy(WORK/name,REPO/'audits'/name)
    for name in('test_bhsm_muon_n1_ramp_time_control_20261015.py','test_bhsm_shifted_polynomial_retarded_n1_20261015.py'):
        body=(WORK/name).read_text(encoding='utf8')
        body=body.replace("Path(__file__).with_name('bhsm_muon_shifted_polynomial_retarded_n1_20261015.py')",
            'Path(__file__).resolve().parents[1]/"audits"/"bhsm_muon_shifted_polynomial_retarded_n1_20261015.py"')
        prefix='from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parents[1]/"audits"))\n'
        (REPO/'tests'/name).write_text(prefix+body,encoding='utf8',newline='\n')
    (OUT/'packaging_script.py').write_bytes(Path(__file__).read_bytes())
    report=dict(classification='EVALUATED_FINITE_FULL_ONE_INSERTION_ANGULAR_RETARDED_RESPONSE_WITH_SOURCE_QUADRATURE_REPAIR',
        benchmark='User-confirmed formed muon in weak measuring field; full self-fields/decay channels retained.',
        actual_scientific_repeat_pairs=repeated,reduced_map_chunks=chunkmap,
        source_sha256={s:digest(WORK/s)for s in scripts},
        exact_time_bias='midpoint_m[g_prime]=1+7/(8m^4), m=steps/4; no bias fitted into action coefficients.',
        fixed_integration='w=z-B1 Q, w_prime=A w+(A B1+B0)Q with actual source polynomials and canonical z corner carry.',
        complex_collar_not_a_new_positive_norm_gate=True,
        physical_outgoing_Gamma_E=None,physical_outgoing_Gamma_B=None,physical_muon_spin_poles=None,
        physical_magnetic_moment=None,physical_g_mu=None,physical_a_mu=None,coupled_matching_corrections_applied=0,
        fresh_physical_Maxwell_all226_after_pass=False,
        finite_control_does_not_admit_physical_derivative=True,
        source_D5_profile_history_canonical_pairing_campaigns_restarted=False,
        retained_nonzero_gauge_H_spin_orbital_and_endpoint_terms=True,
        serialization_scope='This manifest is a binding only; actual independent numerical evaluations are enumerated separately.')
    payload=encoded(report)
    for run in(1,2):(OUT/f'binding_run_{run}.json').write_bytes(payload)
    print(json.dumps(dict(output=str(OUT),binding_sha256=sha256(payload).hexdigest(),
        scientific_pairs=len(repeated),new_source_count=len(scripts),packet_bytes=sum(p.stat().st_size for p in OUT.rglob('*')if p.is_file()))))


if __name__=='__main__':main()
