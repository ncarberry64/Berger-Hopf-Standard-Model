"""Verify numerical circuit identity up to IDs without expanding monomials."""
from array import array
import hashlib
import heapq
import json


def verify_identity(left_db,right_db,root_pairs,progress=None):
    """Compare all reachable payloads with a bijection preserving shared nodes.

    Identical-looking but differently shared nodes are not silently merged.
    Dense arrays store integer IDs only (8 bytes per circuit node), never
    quadratic coefficient matrices. A mismatch refuses enclosure reuse.
    """
    n=max(a for a,b in root_pairs);m=max(b for a,b in root_pairs)
    if 8*(n+m+2)>1024**3:raise MemoryError('explicit circuit identity index cap exceeded')
    forward=array('q',[0])*(n+1);reverse=array('q',[0])*(m+1)
    heap=[];digest=hashlib.sha256();count=0
    def put(a,b):
        if a==0 or b==0:
            if a!=b:raise ValueError('zero quadratic mismatch')
            return
        if not(0<a<=n and 0<b<=m):raise ValueError('acyclic circuit ID range required')
        if forward[a] or reverse[b]:
            if forward[a]!=b or reverse[b]!=a:raise ValueError('quadratic sharing mismatch')
            return
        forward[a]=b;reverse[b]=a;heapq.heappush(heap,-a)
    for a,b in root_pairs:put(a,b)
    while heap:
        a=-heapq.heappop(heap);b=forward[a]
        ar=left_db.execute('SELECT payload FROM q WHERE id=?',(a,)).fetchone()
        br=right_db.execute('SELECT payload FROM q WHERE id=?',(b,)).fetchone()
        if ar is None or br is None:raise ValueError('missing committed circuit node')
        av=json.loads(ar[0]);bv=json.loads(br[0])
        if av[1:]!=bv[1:] or len(av[0])!=len(bv[0]):raise ValueError('different numerical quadratic payload')
        for (ai,ac),(bi,bc) in zip(av[0],bv[0]):
            if ac!=bc or not(0<ai<a and 0<bi<b):raise ValueError('different coefficients or non-acyclic circuit')
            put(ai,bi)
        digest.update(str(a).encode()+b':'+ar[0].encode()+b'\n')
        count+=1
        if progress and count%100000==0:progress(f'verified common quadratic circuit nodes {count}')
    return dict(verified=True,reachable_nodes=count,source_reachable_payload_SHA256=digest.hexdigest().upper(),
                all_coefficients_and_aliases_identical=True,root_pairs=[list(p) for p in root_pairs])
