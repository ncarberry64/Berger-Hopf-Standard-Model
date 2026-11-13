"""Evaluate actual birth density and clock/reset contacts at energy0."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_continued_action_reality import action_reality_coefficient
from bhsm.interface.muon_birth_external_trace_chart import birth_external_trace_chart
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve each actual reset chart application')
    refs={};geo={}
    for side in('incoming','outgoing'):
        phase,_=retained_input(side,refs)
        geo[side]=action_reality_coefficient(phase,0,0j)['geometry']
    p=ROOT/'artifacts/muon_piecewise_euclidean_action_20261011/run_2/result.json'
    refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest();md=json.loads(p.read_bytes())
    clocks={side:next(r['total_proper_clock']for r in md['records']if r['side']==side)for side in geo}
    a=birth_external_trace_chart(geo['incoming']['R4'],geo['outgoing']['R4'],clocks['incoming'],0.,raw_reset=np.eye(18),energy=0.)
    out.mkdir(parents=True)
    arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
    arrays.update(parent_radius=np.array(geo['incoming']['R4']),child_radius=np.array(geo['outgoing']['R4']),
        parent_lapse=np.array(geo['incoming']['N']),child_lapse=np.array(geo['outgoing']['N']),
        parent_birth_source_clock=np.array(clocks['incoming']),child_birth_source_clock=np.array(0.),
        continued_external_energy_anchor=np.array(0.))
    p=out/'application.npz';_compressed_npz(p,arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'scripts/evaluate_muon_continued_current_factor.py',
        'tests/test_muon_birth_external_trace_chart.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):raise RuntimeError('same birth chart/source pin changed')
    result=dict(classification='EVALUATED_SAME_BIRTH_CANONICAL_DENSITY_AND_EXTERNAL_ENVELOPE_RESET',
        input_hashes=refs,archives={'application.npz':dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        parent_R4=geo['incoming']['R4'].real,child_R4=geo['outgoing']['R4'].real,
        child_parent_half_density_ratio=((geo['outgoing']['R4']/geo['incoming']['R4'])**1.5).real,
        parent_lapse=geo['incoming']['N'].real,child_lapse=geo['outgoing']['N'].real,
        owned_arm_source_clock_jump=-clocks['incoming'],external_energy_anchor=0.,
        source_energy_reset_first_max=float(np.max(abs(a['envelope_value_reset_energy_first']))),
        literal_left_reset_first_has_opposite_origin_contact=True,
        analytic_trace_pairing_residual_max=float(np.max(abs(a['analytic_trace_pairing_residual']))),
        canonical_common_frame_I_reset_difference_max=float(np.max(abs(a['canonical_value_reset']-np.eye(18)))),
        density_chart='chi_point=R4^(3/2)psi_point/V; angular coefficient constant normalization cancels between arms',
        lapse_used_as_spinor_amplitude=False,independent_seam_phase_added=False,
        source_chart='incoming proper FE2 clock reaches Tparent at birth; outgoing proper FE2 clock starts0',
        original_converged_n0_field_correction_changes_geometry=False,
        physical_stop_pole_or_mass_selected=False,
        error_scope='binary64 actual represented birth coframe and analytic envelope reset; no physical exterior/canonical-stop or Pauli enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),half_density_ratio=result['child_parent_half_density_ratio'],
        clock_reset_first=result['source_energy_reset_first_max'],canonical_I_defect=result['canonical_common_frame_I_reset_difference_max'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.output)
