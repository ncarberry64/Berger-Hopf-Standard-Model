"""Diagnostic iteration of the already paired coupled defect components."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import diagnose_n12_gate7_centered_uniform_derivatives as diagnostic
import numpy as np
from bhsm.interface import decomposed_coupled_response as decomposition
from bhsm.interface import affine_hs_midpoint_domain as grouped

original_evaluate=diagnostic.evaluate


def evaluate(engine,source,start,stop):
    p=engine.p;midpoint='raw_center' in source;index=source['index']
    folder='.coupled_midpoint_eigenpair_pilot_work' if midpoint else '.affine_eigenpair_pilot_work'
    kind='interval' if midpoint else 'endpoint'
    directory=ROOT/f'artifacts/flagship_integration/{folder}/{kind}_{index:03d}'
    record_path=directory/'record.json';data_path=directory/'eigenpair.npz'
    for file in (record_path,data_path,Path(__file__),Path(decomposition.__file__),Path(grouped.__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    p.verify_sources(source['binding'])
    record=diagnostic.json.loads(record_path.read_bytes());trial=len(record['report']['trials'])-1
    if record['data_SHA256']!=p.values.sha(data_path):raise ArithmeticError('paired eigenpair data changed')
    with np.load(data_path,allow_pickle=False) as data:
        def read(name):return p.hs.restore_balls(data[name+'_mid_q'],data[name+'_rad_q'])
        D=read('center_defect');signed=read(f'trial_{trial}_signed_variation_derivatives')
        original_r=read(f'trial_{trial}_radii')
    r=source['paired']['radii']
    if original_r.shape!=r.shape or not all(a.contains(b) and b.contains(a) for a,b in zip(original_r,r)):
        raise ArithmeticError('same original eigenpair radius box required')
    groups=source.get('groups')
    if groups is None:
        groups=[dict(start=0,stop=1,norm='interval',radius=source['tube']['radius_longitudinal']),
                dict(start=1,stop=75,norm='euclidean',radius=source['tube']['radius_transverse'])]
    S=grouped.group_row_bounds(signed,groups)
    bound=decomposition.CoupledDefectBound(D,source['paired']['rm'],r,S)
    previous=diagnostic.enclose_response
    def enclose(z,e,weights,V):
        if not all(a.contains(b) and b.contains(a) for a,b in zip(weights,r,strict=True)):
            raise ArithmeticError('coupled family weights changed')
        return bound.enclose(z,e)
    try:
        diagnostic.enclose_response=enclose
        arrays,proof=original_evaluate(engine,source,start,stop)
    finally:diagnostic.enclose_response=previous
    proof['same_paired_defect_components_used']=True
    arrays.update(original_state_variation=S,original_domain_radii=r,center_defect=D)
    return arrays,proof


diagnostic.evaluate=evaluate
if __name__=='__main__':diagnostic.main()
