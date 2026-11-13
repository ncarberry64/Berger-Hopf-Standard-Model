"""Reproduce temporal/radial comparisons of the preserved changing forms."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy.sparse import csr_matrix


def matrix(a, key):
    return csr_matrix((a[key+'_data'],a[key+'_indices'],a[key+'_indptr']),
        shape=tuple(a[key+'_shape'])).toarray()


def compare(a,b):
    delta=abs(a-b);scaled=delta/np.maximum(1,np.maximum(abs(a),abs(b)))
    ij=np.unravel_index(np.argmax(scaled),scaled.shape)
    return dict(max_absolute=float(delta.max()),max_entry_scaled=float(scaled[ij]),
        max_scaled_index=list(map(int,ij)),old_at_max=float(a[ij]),new_at_max=float(b[ij]),
        relative_global_max_entry=float(delta.max()/max(abs(a).max(),abs(b).max(),np.finfo(float).tiny)),
        relative_Frobenius=float(np.linalg.norm(a-b)/max(np.linalg.norm(b),np.finfo(float).tiny)))


def execute(repository,time4,time6,output):
    repository=Path(repository);sys.path.insert(0,str(repository/'src'))
    from bhsm.interface.muon_parent_positive_gauge_form import one_form_temporal_moments
    from bhsm.interface.muon_parent_positive_brst_ghost import smooth_ghost_temporal_values
    folders=[Path(time4),Path(time6)];reports=[];archives=[];pins={}
    for label,folder in zip(('stable_time4','stable_time6'),folders):
        for filename in ('result.json','changing_forms.npz'):
            pins[label+'/'+filename]=sha256((folder/filename).read_bytes()).hexdigest()
        reports.append(json.loads((folder/'result.json').read_text()))
        with np.load(folder/'changing_forms.npz',allow_pickle=False)as z:archives.append({k:z[k].copy()for k in z.files})
    if [r['time_order_per_tent_half']for r in reports]!=[4,6]or any(r['radial_orders']!=[4,8,16,32]for r in reports):
        raise ValueError('Exact preserved time4/time6 refinement charts required')
    rows=[];radial=[]
    for side in ('incoming','outgoing'):
        for order in (4,8,16,32):
            prefix=f'{side}_radial{order}_'
            names=sorted(k[len(prefix):-6]for k in archives[0]if k.startswith(prefix)and k.endswith('_shape'))
            rows.append(dict(side=side,radial_order=order,matrices={name:compare(matrix(archives[0],prefix+name),matrix(archives[1],prefix+name))for name in names}))
        for low,high in ((4,8),(8,16),(16,32)):
            radial.append(dict(side=side,radial_orders=[low,high],matrices={name:compare(
                matrix(archives[1],f'{side}_radial{low}_'+name),matrix(archives[1],f'{side}_radial{high}_'+name))for name in names}))
    moments=[]
    for n in (4,6,8):
        x,w=np.polynomial.legendre.leggauss(n);t=np.r_[(x+1)/4,(x+3)/4];w=np.tile(w/4,2)
        g=smooth_ghost_temporal_values(t,1.);f=np.column_stack((2*np.minimum(t,1-t),np.where(t<.5,2.,-2.),g[:,0,:2],g[:,1,:2]))
        exact=one_form_temporal_moments(1.);observed=f.T@(w[:,None]*f)
        moments.append(dict(rule_per_half=n,exact=exact.tolist(),observed=observed.tolist(),
            maximum_absolute=float(abs(exact-observed).max()),odd_bubble_square_relative=float((observed[4,4]-exact[4,4])/exact[4,4])))
    for name in ('muon_parent_positive_gauge_form.py','muon_parent_positive_brst_ghost.py'):
        p=repository/'src/bhsm/interface'/name;pins['src/bhsm/interface/'+name]=sha256(p.read_bytes()).hexdigest()
    pins['comparison_source']=sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(classification='SAME_CHANGING_BACKGROUND_FIXED_CHART_RULE_COMPARISONS',
        temporal_comparisons=rows,time6_radial_comparisons=radial,constant_owned_ghost_temporal_moment_controls=moments,
        max_entry_scaled_definition='max_ij |new-old|/max(1,|old|,|new|), in the retained coefficient units',
        all_matrix_entries_and_unfavorable_rules_retained=True,physical_convergence_claimed=False,
        coupled_corrections=0,input_and_source_sha256=pins)
    output=Path(output)
    if output.exists():raise FileExistsError('Preserve previous comparison bytes')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--time4',required=True);p.add_argument('--time6',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();execute(a.repository,a.time4,a.time6,a.output)
