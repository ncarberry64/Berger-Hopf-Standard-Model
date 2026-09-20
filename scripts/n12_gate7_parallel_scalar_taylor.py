"""Process isolation for independent, identically ordered scalar contractions.

Each worker executes the same parent action and Taylor operations. Parallelism
is only across outputs: it does not regroup a contraction or alter its domain.
"""
import hashlib
import json
from pathlib import Path
import sys


def encode_scalar(value):
    from flint import arb
    from bhsm.interface.shared_action_taylor import Taylor
    if isinstance(value,Taylor):
        return ['t',[[str(v.mid().fmpq()),str(v.rad().fmpq())]
                     for v in [value.c,*value.a.entries(),value.r]]]
    value=arb(value)
    return ['a',[str(value.mid().fmpq()),str(value.rad().fmpq())]]


def _initialize(root,local_interface,groups,state,legs,binding,out):
    global _cert,_domain,_state,_legs,_maps,_binding,_out,_Taylor,_action_adapter,_np
    sys.path[:0]=[str(Path(root)/'scripts'),str(Path(root)/'src')]
    import numpy as np
    from flint import arb,arb_mat,ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm.interface
    bhsm.interface.__path__.insert(0,local_interface)
    from bhsm.interface.shared_action_taylor import Taylor,TaylorDomain,scalar_taylor_action
    ctx.prec=512
    _np=np;_cert=engine.p.values.cert;_Taylor=Taylor;_action_adapter=scalar_taylor_action
    _domain=TaylorDomain(groups,max(stop for _,stop,_ in groups))
    def decode(value):
        tag,data=value
        if tag=='a':return arb(data[0])+arb(0,arb(data[1]))
        if tag!='t':raise ValueError('Explicit Taylor or Arb encoding required')
        values=[arb(m)+arb(0,arb(r)) for m,r in data]
        return Taylor(_domain,values[0],arb_mat(1,_domain.dimension,values[1:-1]),values[-1])
    _state=np.array([decode(v) for v in state],dtype=object)
    _legs={name:np.array([decode(v) for v in vector],dtype=object) for name,vector in legs.items()}
    center=[v.c for v in _state]
    _maps=[_cert._dense_mapping(_cert._integrand(center,node,0).maps) for node in range(_cert.POINTS)]
    _binding=binding;_out=Path(out)


def _contract(task):
    from flint import arb
    name,names=task
    path=_out/(name+'.json')
    with _action_adapter(_cert):
        value=_cert._contracted_action(_state,[_legs[key] for key in names],_maps)
    if isinstance(value,arb):value=_domain.affine(value)
    record=dict(binding=_binding,values=encode_scalar(value)[1])
    # Match the exact canonical encoder used by the retained producer.
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    payload=engine.p.geometry.encoded(record)
    with path.open('xb') as stream:stream.write(payload)
    return name,hashlib.sha256(payload).hexdigest().upper()


def precompute(root,domain,state,legs,tasks,binding,out,workers):
    """Materialize missing scalar checkpoints, retaining operation order."""
    if workers<2:return
    from concurrent.futures import ProcessPoolExecutor,as_completed
    import multiprocessing
    missing=[]
    for task in tasks:
        path=out/(task[0]+'.json')
        if path.exists():
            if json.loads(path.read_bytes())['binding']!=binding:
                raise ValueError('Parallel checkpoint source mismatch')
        else:missing.append(task)
    if not missing:return
    with ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn'),
            initializer=_initialize,initargs=(str(root),str(Path(__file__).resolve().parents[1]/'src/bhsm/interface'),domain.groups,
                [encode_scalar(v) for v in state],
                {key:[encode_scalar(v) for v in vector] for key,vector in legs.items()},binding,str(out))) as pool:
        futures=[pool.submit(_contract,task) for task in missing]
        for count,future in enumerate(as_completed(futures),1):
            name,_=future.result()
            if count==1 or count%10==0 or count==len(missing):
                print(json.dumps(dict(parallel_contractions_complete=count,total=len(missing),last=name)),flush=True)
