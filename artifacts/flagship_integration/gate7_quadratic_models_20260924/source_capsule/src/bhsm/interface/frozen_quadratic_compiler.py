"""Replay selected frozen DAG ancestors in degree-two arithmetic only."""
import json
import mmap
import struct
from collections import Counter
from flint import arb, fmpq
from bhsm.interface.shared_expression_graph import restore
from bhsm.interface.sparse_quadratic_enclosure import QuadraticModel


def children(n):
    if n[0] == 'linear': return [j for j, _ in n[1]]
    if n[0] == 'product': return n[1]
    if n[0] in ('exp','log','inverse','sqrt_positive'): return [n[1]]
    return []


class FrozenIndex:
    def __init__(self, path):
        self.files = [(path/name).open('rb') for name in ('nodes.jsonl','offsets.bin')]
        self.data,self.offsets = [mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) for f in self.files]
        self.count = len(self.offsets)//8-1

    def __getitem__(self, i):
        a,b = struct.unpack_from('<QQ',self.offsets,8*i)
        return json.loads(self.data[a:b])


def selected_ancestors(index, roots, cuts=()):
    """One byte and one uint32 per frozen node; no Python adjacency graph."""
    import numpy as np
    marked=np.zeros(index.count,dtype=np.uint8)
    refs=np.zeros(index.count,dtype=np.uint32)
    for i in roots: marked[i]=1; refs[i]+=1
    ops=Counter()
    for i in range(max(roots),-1,-1):
        if not marked[i]: continue
        n=index[i];ops[n[0]]+=1
        if i in cuts: continue
        for j in children(n):
            if not 0<=j<i: raise ValueError('frozen DAG must be acyclic')
            marked[j]=1;refs[j]+=1
    return marked,refs,dict(ops)


def compile_selected(index, metadata, domain, names, progress=print,
                     cuts=None, coefficient_limit=4000000, frontier_path=None):
    """Reference-counted frontier; hard coefficient cap fails rather than OOM.

    Optional cuts are explicitly inherited frozen affine enclosures. Default
    is no cut: all selected dependencies are replayed from exact DAG nodes.
    Same-family certified constraints apply without dropping signed terms.
    """
    cuts=cuts or {}
    roots={name:metadata['roots'][name] for name in names}
    marked,refs,ops=selected_ancestors(index,set(roots.values()),cuts)
    progress('selected '+json.dumps(dict(nodes=int(marked.sum()),operations=ops,cuts=len(cuts))))
    if frontier_path is None:
        values={}
    else:
        from bhsm.interface.quadratic_frontier_cache import FrontierCache
        values=FrontierCache(domain,frontier_path)
    live_coefficients=0;peak=0;done=0
    constraints=metadata.get('certified_enclosures',{})
    provenance=metadata.get('leaf_provenance',{})
    for i in range(max(roots.values())+1):
        if not marked[i]: continue
        n=index[i];op=n[0];d=domain
        if i in cuts:
            row=cuts[i]
            v=d.model(restore(row['c']),{j:restore(c) for j,c in row['a']},
                      {'inherited_affine_frontier':arb(fmpq(row['r']))})
        elif op=='constant': v=d.model(arb(fmpq(n[1])))
        elif op=='leaf':
            role=provenance.get(str(i),{}).get('role','unspecified_leaf')
            label='q_implicit_correction' if role=='new_implicit_remainder' else 'inherited_leaf_tail'
            v=d.model(restore(n[2]),{j:restore(c) for j,c in n[3]}, {label:arb(fmpq(n[4]))})
        elif op=='linear':
            v=sum((values[j].scale(arb(fmpq(c))) for j,c in n[1]),d.model())
        elif op=='product':
            v=d.model(1)
            for j in n[1]: v=v*values[j]
        else:
            v=values[n[1]].unary(op,arb(fmpq(n[2])) if len(n)>2 else None)
        fact=constraints.get(str(i))
        if fact:
            ball=restore(fact['ball']);center=ball.mid()
            translated=(v.r+abs(v.c-center).upper()).upper()
            direct=(ball.rad()+v.lb+v.qb).upper()
            if direct<translated:
                tails={'certified_value_parameter_loss':direct}
            else:
                tails=v.tails.copy()
                tails['certified_value_recenter'] = abs(v.c-center).upper()
            v=QuadraticModel(d,center,v.a,v.q,v.qb,tails)
        if not v.support().is_finite(): raise ArithmeticError('nonfinite quadratic enclosure at '+str(i))
        values[i]=v;live_coefficients+=len(v.a);peak=max(peak,live_coefficients)
        if frontier_path is None and live_coefficients>coefficient_limit:
            raise MemoryError('explicit sparse frontier coefficient limit exceeded')
        if i not in cuts:
            for j in children(n):
                refs[j]-=1
                if refs[j]==0:
                    live_coefficients-=len(values[j].a);del values[j]
        done+=1
        if done%10000==0:
            domain.store.db.commit()
            progress(f'compiled {done} frozen_node {i} live {len(values)} coefficients {live_coefficients} Q_circuit {domain.store.count}')
    return {name:values[i] for name,i in roots.items()},dict(selected_nodes=done,peak_live_linear_coefficients=peak,
                                                         operations=ops,affine_frontier_count=len(cuts))
