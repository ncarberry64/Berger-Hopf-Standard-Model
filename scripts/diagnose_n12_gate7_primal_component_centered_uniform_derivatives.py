"""Diagnostic: refine the paired primal response before physical differentiation."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import diagnose_n12_gate7_component_centered_uniform_derivatives as component
import numpy as np

diagnostic=component.diagnostic


def evaluate(engine,source,start,stop):
    p=engine.p;midpoint='raw_center' in source;index=source['index']
    folder='.coupled_midpoint_physical_value_work' if midpoint else '.affine_physical_value_pilot_work'
    kind='interval' if midpoint else 'endpoint'
    directory=ROOT/f'artifacts/flagship_integration/{folder}/{kind}_{index:03d}'
    record_path=directory/'record.json';data_path=directory/'value.npz';receipt_path=directory/'reproduction.json'
    for file in (record_path,data_path,receipt_path,Path(__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    p.verify_sources(source['binding'])
    record=diagnostic.json.loads(record_path.read_bytes());receipt=diagnostic.json.loads(receipt_path.read_bytes())
    if (record['data_SHA256']!=p.values.sha(data_path) or receipt['record_SHA256']!=p.values.sha(record_path)
            or receipt['independent_recomputation'] is not True or receipt['byte_identical'] is not True):
        raise ArithmeticError('unchanged paired primal response evidence required')
    with np.load(data_path,allow_pickle=False) as a:
        def read(name):return p.hs.restore_balls(a[name+'_mid_q'],a[name+'_rad_q'])
        center=read('response_center');residual=read('preconditioned_response_residual');old=read('response_box')
    if center.shape!=(62,) or residual.shape!=(62,) or old.shape!=(62,):
        raise ArithmeticError('complete original primal response operands required')
    if not all(a.contains(b) and b.contains(a) for a,b in zip(source['response'],old,strict=True)):
        raise ArithmeticError('primal response does not match the already verified same-family source')
    z=center.copy();z[-1]=-z[-1]
    refined,proof=component.rows.enclose_response_rows(z,residual,source['paired']['radii'],source['paired']['variation'])
    refined[-1]=-refined[-1]
    if not all(a.contains(b) for a,b in zip(old,refined,strict=True)):
        raise ArithmeticError('refined primal response must remain inside the paired response box')
    source['response']=refined
    try:arrays,report=component.evaluate(engine,source,start,stop)
    finally:source['response']=old
    arrays.update(original_primal_response=old,refined_primal_response=refined)
    report['paired_primal_component_refinement']=proof
    report['physical_domain_radii_changed']=False
    return arrays,report


diagnostic.evaluate=evaluate
if __name__=='__main__':diagnostic.main()
