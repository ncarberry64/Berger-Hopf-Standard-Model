"""Join independent batch receipts into exact full 741-point DF coverage."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import derive_n12_gate7_full_direct_physical_jacobians as backend

BATCHES=[list(range(start,min(start+29,370))) for start in range(0,370,29)]


def aggregate_batches(producer,batches):
    expected=producer.binding()
    files={};proofs={};covered_endpoints=set();covered_midpoints=set()
    for indices in batches:
        directory=producer.WORK/'batches'/f'{indices[0]:03d}_{indices[-1]:03d}'
        manifest_path=directory/'manifest.json';receipt_path=directory/'reproduction.json'
        manifest=json.loads(manifest_path.read_text());receipt=json.loads(receipt_path.read_text())
        endpoints=sorted({node for index in indices for node in (index,index+1)})
        if (manifest.get('binding')!=expected or manifest.get('midpoints')!=indices or manifest.get('endpoints')!=endpoints
                or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
                or receipt.get('points')!=len(endpoints)+len(indices)
                or receipt.get('manifest_SHA256')!=producer.values.sha(manifest_path)):
            raise RuntimeError('exact independently reproduced batch coverage required')
        inventory={producer.file_key(producer.WORK/f'{stage}_{i:03d}.{ext}')
                   for stage,points in (('endpoint',endpoints),('midpoint',indices))
                   for i in points for ext in ('json','npz')}
        if set(manifest.get('files',{}))!=inventory:
            raise RuntimeError('exact batch file inventory required')
        producer.values.verify_binding(dict(files=manifest['files']))
        for name,digest in manifest['files'].items():
            if name in files and files[name]!=digest:
                raise RuntimeError('overlapping independent batches disagree')
            files[name]=digest
        for path in (manifest_path,receipt_path):proofs[producer.file_key(path)]=producer.values.sha(path)
        covered_endpoints.update(endpoints);covered_midpoints.update(indices)
    if covered_endpoints!=set(range(371)) or covered_midpoints!=set(range(370)) or len(files)!=1482:
        raise RuntimeError('all 741 physical derivative points must be independently reproduced')
    producer.values.verify_binding(expected)
    producer.values.verify_binding(dict(files=proofs))
    return dict(scope='SELECTED_DIRECT_PHYSICAL_HS_AMBIENT_JACOBIANS',binding=expected,
        endpoints=list(range(371)),midpoints=list(range(370)),files=files,all_741_DF_covered=True,
        physical_Z1_recertified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False),proofs


def main():
    producer=backend.install_backend()
    manifest,proofs=aggregate_batches(producer,BATCHES)
    producer.values.write_json(producer.WORK/'manifest.json',manifest)
    producer.values.write_json(producer.WORK/'reproduction.json',dict(byte_identical=True,independent_recomputation=True,
        manifest_SHA256=producer.values.sha(producer.WORK/'manifest.json'),points=741,
        evidence='EVERY_POINT_COVERED_BY_AT_LEAST_ONE_VERIFIED_INDEPENDENT_RECOMPUTATION_BATCH',
        independently_reproduced_batch_files=proofs,
        aggregation_source_SHA256=producer.values.sha(Path(__file__)),FULL_BHSM_COMPLETE=False))
    print(json.dumps(dict(independently_reproduced_points=741,batches=len(BATCHES),
        manifest_SHA256=producer.values.sha(producer.WORK/'manifest.json'))),flush=True)


if __name__=='__main__':main()
