"""Missing MP radial64/time8 Lorenz operands, without replaying other rules.

This is a new quadrature combination on the same supplied real affine
history. No solved field history, source/D5 campaign or original birth
correction is repeated. Exact integrated MP tuples feed finite Pi assembly.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import mpmath as mp
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'audits')]
import bhsm_changing_lorenz_mp_coefficient_values_20261016 as owner
import bhsm_changing_lorenz_mp_time_control_20261016 as clock
from bhsm_changing_ordinary_oneform_gram_mp_20261016 import ordinary_point
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

OWNER_SHA='1b0a9713749feb062fecdb664598a7a5b3528bd72ec5aa18176ae88eb5b88eff'
CLOCK_SHA='cbb9280f9cadd18f73be462b0d1c87643135ae95910640690586ed228a3d67ea'


def execute(refinement,application,output):
    out=Path(output)
    if out.exists():raise FileExistsError('Preserve every numerical readout')
    for module,h in ((owner,OWNER_SHA),(clock,CLOCK_SHA)):
        assert sha256(Path(module.__file__).read_bytes()).hexdigest()==h
    phases,reference,frozen,E,pins=owner.load_inputs(refinement,application)
    arrays,records={},[]
    with mp.workdps(80):
        c=owner.constants()
        for side in ('incoming','outgoing'):
            phase=phases[side];length=abs(owner.m(phase['span']))
            origin=min(owner.m(phase['span']),mp.mpf(0))
            times,tw=owner.time_nodes(phase,frozen[side,64],'mp',8,80)
            rho,rw=owner.radial_nodes(frozen[side,64],'mp',64,80,c)
            snapshots=[]
            for u,w in zip(times,tw):
                t=u+origin;raw=owner.raw_at(phase,t)
                g=owner.geometry(raw,c['WALL']/2,c)
                chart=owner.response_chart(g['delta'],c,96,'mp',80)
                snapshots.append(dict(t=t,raw=raw,weight=w,chart=chart,
                    temporal=owner.temporal_values(u,length),tent=2*min(u/length,1-u/length)))
            total=owner.tensor.tensors();Goo=owner.tensor.zeros((10,10))
            indices=((284,924),(0,0),(20,183),(40,823))
            literal=[mp.mpf(0) for _ in indices];point_controls=[]
            for ri,(r,wr) in enumerate(zip(rho,rw)):
                basis=owner.radial_basis(r,reference,c)
                for ti in range(len(times)//2):
                    group=[]
                    for k in (ti,len(times)-1-ti):
                        s=snapshots[k]
                        val=owner.coefficient(s['raw'],s['t'],r,side,phase.get('parent_reference'),
                            reference,c,s['chart'],basis_data=basis)
                        point=owner.native_point(val['A'],val['metric'],s['temporal'],val['radial'],s['tent'],c)
                        weight=wr*s['weight'];group.append((weight,point))
                        Goo+=weight*ordinary_point(val['metric'],val['radial'],s['tent'])
                        for j,(i,l) in enumerate(indices):
                            term=owner.native_literal(i,l,val['A'],E,val['metric'],s['temporal'],val['radial'],s['tent'],c)
                            literal[j]+=weight*term
                            if ri in (0,32,63) and k in (0,len(times)-1):
                                exact=owner.tensor.tensor_entry(point,E,i,l)
                                point_controls.append(dict(radial_index=ri,time_index=k,row=i,column=l,
                                    absolute=mp.nstr(abs(exact-term),65)))
                    for name in total:
                        total[name]+=group[0][0]*group[0][1][name]+group[1][0]*group[1][1][name]
                if ri%8==0 or ri==63:
                    print(json.dumps(dict(side=side,radial_order=64,time_order=8,completed_radius=ri+1)),flush=True)
            B=owner.tensor.assemble(total,E)
            controls=[dict(row=i,column=j,literal_MP_integral=mp.nstr(z,65),
                tensor_MP_integral=mp.nstr(B[i,j],65),absolute=mp.nstr(abs(z-B[i,j]),65))
                for (i,j),z in zip(indices,literal)]
            local={};clock.pack_moments(local,total)
            clock.pack_moments(local,dict(ordinary_Gram10=Goo))
            local['EW4_real_angular_derivatives']=E
            local['radial_points']=np.array(list(map(float,rho)))
            local['radial_coordinate_weights']=np.array(list(map(float,rw)))
            local['temporal_coordinate_time']=np.array([float(s['t']) for s in snapshots])
            local['temporal_coordinate_weights']=np.array(list(map(float,tw)))
            owner.tensor.save_matrix(local,'B',owner.tensor.as_float(B))
            for name,a in local.items():arrays[side+'_'+name]=a
            records.append(dict(side=side,radial_order=64,time_order_per_half=8,anchor_order=96,
                point_literal_controls=point_controls,integrated_literal_controls=controls,
                maximum_literal_MP_integrated_absolute=mp.nstr(max(mp.mpf(x['absolute']) for x in controls),65),
                complete_B_shape=list(B.shape),exact_working_binary_moments_retained=True))
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and (name.startswith('bhsm.') or name.startswith('bhsm_')) and Path(p).is_relative_to(ROOT):
            pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    for rel,h in pins.items():assert sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
    out.mkdir(parents=True);_compressed_npz(out/'radial64_time8_moments.npz',arrays)
    result=dict(classification='MISSING_SAME_REAL_CELL_RADIAL64_TIME8_EXACT_LORENZ_MOMENTS',
        records=records,source_and_owner_sha256=dict(sorted(pins.items())),
        numerical_sha256=sha256((out/'radial64_time8_moments.npz').read_bytes()).hexdigest(),
        original_TIME6_archive_sha256=owner.tensor.TIME6_SHA,arithmetic_dps=80,
        physical_native_or_outgoing_operator_completed=False,full15_value_composition_completed=False,
        original_physical_source_domain_derivative_pass=False,original_coupled_matching_corrections=0,
        physical_muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--refinement',required=True)
    p.add_argument('--application',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();execute(a.refinement,a.application,a.output)
