"""Bind new independently evaluated diagnostics without promoting a moment."""
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile

WORK=Path(r'C:/Users/carbe/OneDrive/Documents/CODEX')
REPO=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
OUT=REPO/'artifacts/muon_outgoing_probe_domain_20261015'


def digest(path):return sha256(path.read_bytes()).hexdigest()


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def copy(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.read_bytes()!=source.read_bytes():
        raise ValueError('Preserve different archived bytes: '+str(target))
    copyfile(source,target)


def pair(base,left,right,component,selected=None):
    a,b=base/left,base/right
    names=sorted(p.relative_to(a).as_posix() for p in a.rglob('*') if p.is_file())
    other=sorted(p.relative_to(b).as_posix() for p in b.rglob('*') if p.is_file())
    if names!=other:raise ValueError('Different scientific output files')
    hashes={}
    archived=[]
    for name in names:
        if (a/name).read_bytes()!=(b/name).read_bytes():raise ValueError('Different scientific repeat bytes: '+name)
        hashes[name]=digest(a/name)
        if selected is None or selected(name):
            for run in (left,right):copy(base/run/name,OUT/component/run/name)
            archived.append(name)
    return dict(component=component,source_base=str(base),actual_independent_evaluations=[left,right],
        all_output_sha256=hashes,archived_files=archived)


def chunks(source,relative):
    data=source.read_bytes();parts=[]
    for index,start in enumerate(range(0,len(data),4*1024**2)):
        part=data[start:start+4*1024**2]
        target=OUT/(relative+f'.{index:03d}.bin');target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=part:raise ValueError('Different old chunk')
        target.write_bytes(part)
        parts.append(dict(path=target.relative_to(OUT).as_posix(),bytes=len(part),sha256=sha256(part).hexdigest()))
    if b''.join((OUT/q['path']).read_bytes() for q in parts)!=data:raise ValueError('Chunk reconstruction mismatch')
    return dict(original_source=str(source),original_name=source.name,bytes=len(data),sha256=digest(source),chunks=parts)


def main():
    pairs=[pair(WORK/'outputs/bhsm_outgoing_missing_jet_sensitivity_20261015','run_1','run_2','missing_jet_sensitivity'),
           pair(WORK/'outputs/bhsm_outgoing_trace_two_parameter_jet_20261015','run_1','run_2','mixed_domain_consumer'),
           pair(WORK/'outputs/bhsm_physical_outgoing_operand_evidence_20261015','run_1','run_2','physical_operand_evidence')]
    # Additional radial pairs/chunks are added only after their numerical runs finish.
    source_sha={p.name:digest(p) for p in sorted((OUT/'sources').glob('*.py'))}
    report=dict(classification='EVALUATED_OUTGOING_PROBE_DOMAIN_CONTACTS_AND_MISSING_JET_SENSITIVITY',
        actual_scientific_repeat_pairs=pairs,original_source_sha256=source_sha,
        installed_consumer_matches_evaluated_source_bytes=(REPO/'src/bhsm/interface/muon_outgoing_trace_probe_jet.py').read_bytes()==(OUT/'sources/bhsm_outgoing_trace_two_parameter_jet_20261015.py').read_bytes(),
        physical_outgoing_energy_jet=None,physical_outgoing_magnetic_jet=None,
        physical_full_derivative_passed=False,physical_radial_convergence_established=False,
        normalized_physical_two_spin_state=None,physical_magnetic_moment=None,physical_g_mu=None,physical_a_mu=None,
        coupled_matching_corrections_applied=0,after_correction_Maxwell_all226_pass=False,
        completed_source_D5_profile_history_canonical_pairing_campaigns_restarted=False,
        empirical_muon_mass_or_anomaly_consumed=False,
        serialization_is_not_an_independent_scientific_evaluation=True)
    payload=encoded(report)
    for number in (1,2):(OUT/f'binding_run_{number}.json').write_bytes(payload)
    copy(Path(__file__),OUT/'packaging_script.py')
    print(json.dumps(dict(binding_sha256=sha256(payload).hexdigest(),scientific_pairs=len(pairs))))


if __name__=='__main__':main()
