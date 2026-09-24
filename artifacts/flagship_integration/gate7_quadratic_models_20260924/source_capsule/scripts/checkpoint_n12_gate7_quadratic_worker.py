"""Guarded debugger hook for our running Python 3.14 numerical worker only.

Executed with sys.remote_exec on a PID launched by this task. Saves completed
models, or installs that save immediately before output support. Changes only
the numerical support backend; every forward arithmetic method is checked
unchanged. It never attaches to a scientific producer or another application.
"""
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from flint import arb,ctx

if Path(sys.argv[0]).name!='prototype_n12_gate7_sparse_quadratic.py':
    raise RuntimeError('refuse any process except this numerical prototype worker')
work=Path(sys.argv[sys.argv.index('--work')+1]).resolve()
repo=Path.cwd().resolve()
if work.parent!=repo/'tmp/gate7_quadratic_20260924':
    raise RuntimeError('unexpected worker output directory')
frames=[]
for top in sys._current_frames().values():
    while top is not None:
        if top.f_code.co_name=='main' and Path(top.f_code.co_filename).name=='prototype_n12_gate7_sparse_quadratic.py':
            frames.append(top)
        top=top.f_back
if len(frames)!=1:raise RuntimeError('one suspended prototype main frame required')
main=frames[0]
if main.f_locals['receipt']['graph_SHA256']!='e104d285f142a40dcd307d5a1d6ee633e2b89c3f85ff62aa052041ec572724d9':
    raise RuntimeError('unexpected frozen graph')
if ctx.prec!=512:raise RuntimeError('unchanged 512-bit forward arithmetic required')
from bhsm.interface.shared_expression_graph import pair


def snapshot():
    local=main.f_locals
    if 'models' not in local:return False
    def encode(v):
        return dict(c=pair(v.c),a=[[i,pair(x)] for i,x in sorted(v.a.items())],q=v.q,qb=str(v.qb.fmpq()),
                    tails={k:str(x.fmpq()) for k,x in sorted(v.tails.items())})
    meta=local['meta']
    row=dict(models={n:encode(v) for n,v in local['models'].items()},stats=local['stats'],
             graph_SHA256=local['receipt']['graph_SHA256'],parameter_order=meta['parameter_order'],groups=meta['groups'],
             frozen_checkpoint='cef38b6b',radius_exact=meta['radius_exact'])
    local['d'].store.db.commit()
    path=work/'compiled_roots.json'
    payload=json.dumps(row,sort_keys=True)+'\n'
    if path.exists() and json.loads(path.read_bytes())!=row:raise RuntimeError('changed completed checkpoint')
    path.write_text(payload)
    return True


ready=snapshot()
receipt=dict(pid=os.getpid(),scope=main.f_locals['args'].scope,checkpoint_ready=ready,
             frozen_checkpoint='cef38b6b',forward_arithmetic_changed=False,scientific_producers_run=False)
if not ready:
    import bhsm.interface.sparse_quadratic_enclosure as original
    methods=('__init__','__add__','__mul__','scale','unary','support')
    before={name:getattr(original.QuadraticModel,name) for name in methods}
    module=importlib.import_module('bhsm.interface.block_quadratic_expansion')
    module=importlib.reload(module)
    grouped=importlib.import_module('bhsm.interface.quadratic_group_support')
    # Load the corrected support method without replacing class identities or
    # reloading the module used by the ongoing forward arithmetic.
    spec=importlib.util.spec_from_file_location('_quadratic_support_only',original.__file__)
    fresh=importlib.util.module_from_spec(spec);spec.loader.exec_module(fresh)
    original.QuadraticDomain.polynomial_range=fresh.QuadraticDomain.polynomial_range
    def final_support(self):
        q=module.expand_batched(self.domain.store,[(self.q,arb(1))],self.domain.groups,
                               progress=lambda text:print(text,flush=True))
        value,structure=grouped.grouped_range(self.domain,self.c,self.a,q)
        return (abs(value).upper()+self.r).upper(),q,structure
    original.QuadraticModel.final_support=final_support
    previous=main.f_globals['encoded'];cache={}
    def encoded(model,*args,**kwargs):
        if not (work/'compiled_roots.json').exists():
            if not snapshot():raise RuntimeError('cannot support before completed forward checkpoint')
        key=id(model)
        if key not in cache:cache[key]=previous(model,*args,**kwargs)
        return cache[key]
    main.f_globals['encoded']=encoded
    if any(getattr(original.QuadraticModel,name) is not value for name,value in before.items()):
        raise RuntimeError('forward arithmetic unexpectedly changed')
    receipt['support_backend']='batched_group_matrix_support'
    receipt['checkpoint_deferred_until_forward_complete']=True
(work/'support_transition_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print('NUMERICAL_WORKER_CHECKPOINT_AND_SUPPORT_TRANSITION '+json.dumps(receipt),flush=True)
