"""Reconcile only provenance leaves of reused coordinate/incidence proofs.

The direct consumed kinematic and output-map certificates must have identical
non-input fields. The sole nonidentical transitive numeric leaf allowed is
the resolved-coordinate screen witness, which these point producers do not
read: they consume kinematic matrices and frozen output-map rows instead.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent/'BHSM-ae32-crossing-correction'


def sha(path):
    data = path.read_bytes()
    if path.suffix in ('.json','.md','.py'):
        data = data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest().upper()


def main():
    names = ('CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER','FROZEN_CAUSAL_MAP_CONSTRUCTION',
        'FROZEN_OUTPUT_MAP_CONSTRUCTION','RESOLVED_COORDINATE_CAUSAL_TRANSPORT',
        'KINEMATIC_CAUSAL_ARITHMETIC_ENVELOPE')
    substitutions = {}
    for name in names:
        rel = 'artifacts/flagship_integration/BHSM_N12_GATE7_'+name+'.json'
        old,new = [json.loads((root/rel).read_bytes()) for root in (SOURCE,ROOT)]
        a,b = deepcopy(old),deepcopy(new)
        a.pop('inputs'); b.pop('inputs')
        if name == 'RESOLVED_COORDINATE_CAUSAL_TRANSPORT':
            for item in (a,b):
                adjudication = item['stored_polynomial_with_coordinate_and_storage_error']['adjudication']
                if adjudication['status'] != 'STORED_POLYNOMIAL_SELF_MAP':
                    raise ValueError('Both independent stored screens must pass')
                adjudication.pop('witness')
        if a != b:
            raise ValueError('Scientific certificate fields changed: '+name)
        substitutions[rel] = (sha(SOURCE/rel),sha(ROOT/rel))
    theory = 'theory/n12_gate7_current_green_signed_transverse_causal_center.md'
    receipt_path = ROOT/'artifacts/mission_state/BHSM_GATE7_CAUSAL_CENTER_THEORY_BINDING_RECONCILIATION_V37.json'
    receipt = json.loads(receipt_path.read_bytes())
    old_theory='FA7606C3B39586A0B1D679CBBD7FB4A31121EC0F874CFD16A7DF35E84F0D0159'
    new_theory='FB1E849DA7ACD0E4BF26AAAE3366BA90713274424EFDD9AA4596BF20603909F3'
    if sha(SOURCE/theory)!=old_theory or sha(ROOT/theory)!=new_theory or receipt['scientific_fields_changed']:
        raise ValueError('The previously audited provenance-only theory bridge changed')
    substitutions[theory]=(old_theory,new_theory)
    changes=[]; planned=[]; verified={}
    for directory in ('.physical_first_midpoint_coordinate_error_work','.physical_midpoint_incidence_error_work'):
        for i in range(370):
            path=ROOT/f'artifacts/flagship_integration/{directory}/midpoint_{i:03d}.json'
            old=json.loads(path.read_bytes()); new=deepcopy(old); leaves=[]
            for rel,expected in old['source_SHA256'].items():
                target=ROOT/rel
                if rel not in verified: verified[rel]=sha(target)
                actual=verified[rel]
                if actual == expected: continue
                if substitutions.get(rel)!=(expected,actual):
                    raise ValueError('Unapproved physical source change: '+rel)
                new['source_SHA256'][rel]=actual; leaves.append(rel)
            a,b=deepcopy(old),deepcopy(new);a.pop('source_SHA256');b.pop('source_SHA256')
            if a!=b or sha(path.with_suffix('.npz'))!=old['data_SHA256']:
                raise ValueError('Numerical point/data changed')
            if leaves:
                payload=(json.dumps(new,indent=2,sort_keys=True)+'\n').encode()
                changes.append(dict(path=path.relative_to(ROOT).as_posix(),old_SHA256=sha(path),
                    new_SHA256=hashlib.sha256(payload).hexdigest().upper(),changed_source_leaves=leaves))
                planned.append((path,payload))
    for path,payload in planned:path.write_bytes(payload)
    result=dict(algorithm='GATE7_REUSED_PHYSICAL_POINT_PROVENANCE_RECONCILIATION_V1',
        changes=changes,substitutions=substitutions,numeric_point_fields_changed=False,
        data_arrays_changed=False,original_domain_changed=False,
        direct_consumed_kinematic_and_output_certificates_numerically_identical=True,
        resolved_screen_witness_not_consumed_by_point_producers=True,
        prior_theory_bridge_SHA256=sha(receipt_path),Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    out=ROOT/'artifacts/mission_state/BHSM_GATE7_PHYSICAL_POINT_PROVENANCE_20260923.json'
    with out.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'point_provenance_records_updated':len(changes),'scientific_fields_changed':False}))


if __name__=='__main__':main()
