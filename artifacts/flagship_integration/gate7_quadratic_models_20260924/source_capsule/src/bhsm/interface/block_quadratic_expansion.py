"""Stream factored quadratic atoms into small Arb blocks at output time."""
import heapq
import json
from flint import arb,arb_mat
from bhsm.interface.shared_expression_graph import restore
from bhsm.interface.sparse_quadratic_enclosure import accumulate,clean


def expand_blocks(store, links, groups, progress=None):
    """Same polynomial as scalar expansion, with outward block arithmetic.

    Only occupied group pairs are allocated. In the frozen physical domain,
    each dense block is at most 74 by 74. No 450 by 450 dense Q is created.
    Shared circuit adjoints are combined before any outer product.
    """
    group_of={i:g for g,(a,b,_) in enumerate(groups) for i in range(a,b)}
    pending={};heap=[];blocks={};sparse={};visited=0;atoms=0
    def put(i,v):
        if not i or v.is_zero():return
        if i not in pending:
            pending[i]=arb(0);heapq.heappush(heap,-i)
        pending[i]+=v
    for i,v in links:put(i,v)
    while heap:
        i=-heapq.heappop(heap);weight=pending.pop(i)
        if weight.is_zero():continue
        row=store.db.execute('SELECT payload FROM q WHERE id=?',(i,)).fetchone()
        edge,left,right=json.loads(row[0])
        for j,c in edge:put(j,weight*restore(c))
        if left and right:
            atoms+=1
            a=[(j,restore(v)) for j,v in left];b=[(j,restore(v)) for j,v in right]
            if len(a)*len(b)<128:
                for j,x in a:
                    for k,y in b:accumulate(sparse,(min(j,k),max(j,k)),weight*x*y)
            else:
                ga={};gb={}
                for j,v in a:ga.setdefault(group_of[j],{})[j]=v*weight
                for j,v in b:gb.setdefault(group_of[j],{})[j]=v
                va={g:arb_mat(stop-start,1,[vals.get(j,arb(0)) for j in range(start,stop)])
                    for g,vals in ga.items() for start,stop,_ in [groups[g]]}
                vb={g:arb_mat(stop-start,1,[vals.get(j,arb(0)) for j in range(start,stop)])
                    for g,vals in gb.items() for start,stop,_ in [groups[g]]}
                for g,x in va.items():
                    for h,y in vb.items():
                        key=min(g,h),max(g,h)
                        outer=x*y.transpose() if g<=h else y*x.transpose()
                        blocks[key]=blocks[key]+outer if key in blocks else outer
        visited+=1
        if progress and visited%100000==0:progress(f'quadratic adjoints {visited}; atoms {atoms}; blocks {len(blocks)}')
    for (g,h),block in sorted(blocks.items()):
        start,stop,_=groups[g];second,end,_=groups[h]
        for i in range(start,stop):
            for j in range(max(i,second) if g==h else second,end):
                value=block[i-start,j-second]
                if g==h and i!=j:value+=block[j-start,i-second]
                if not value.is_zero():accumulate(sparse,(i,j),value)
    return clean(sparse)


def expand_batched(store, links, groups, progress=None, batch_size=128):
    """Fuse rank-one atoms into small matrix products, U @ V.T, in batches.

    This avoids allocating a 74x74 outer product for each individual atom.
    Physical group rows and atom columns stay aligned; no extra parameter
    or independent error is introduced. All operations use outward Arb.
    """
    group_of={i:g for g,(a,b,_) in enumerate(groups) for i in range(a,b)}
    pending={};heap=[];blocks={};sparse={};batch=[];visited=0;atoms=0
    def put(i,v):
        if not i or v.is_zero():return
        if i not in pending:pending[i]=arb(0);heapq.heappush(heap,-i)
        pending[i]+=v
    def flush():
        if not batch:return
        left_groups={group_of[i] for a,b in batch for i in a}
        right_groups={group_of[i] for a,b in batch for i in b}
        left={g:arb_mat(stop-start,len(batch),[a.get(i,arb(0)) for i in range(start,stop) for a,b in batch])
              for g in sorted(left_groups) for start,stop,_ in [groups[g]]}
        right={g:arb_mat(stop-start,len(batch),[b.get(i,arb(0)) for i in range(start,stop) for a,b in batch])
               for g in sorted(right_groups) for start,stop,_ in [groups[g]]}
        for g,x in left.items():
            for h,y in right.items():
                key=min(g,h),max(g,h)
                value=x*y.transpose() if g<=h else y*x.transpose()
                blocks[key]=blocks[key]+value if key in blocks else value
        batch.clear()
    for i,v in links:put(i,v)
    while heap:
        i=-heapq.heappop(heap);weight=pending.pop(i)
        if weight.is_zero():continue
        edge,left,right=json.loads(store.db.execute('SELECT payload FROM q WHERE id=?',(i,)).fetchone()[0])
        for j,c in edge:put(j,weight*restore(c))
        if left and right:
            atoms+=1
            a={j:weight*restore(v) for j,v in left};b={j:restore(v) for j,v in right}
            if len(a)*len(b)<128:
                for j,x in a.items():
                    for k,y in b.items():accumulate(sparse,(min(j,k),max(j,k)),x*y)
            else:
                batch.append((a,b))
                if len(batch)>=batch_size:flush()
        visited+=1
        if progress and visited%100000==0:progress(f'batched adjoints {visited}; atoms {atoms}; blocks {len(blocks)}')
    flush()
    for (g,h),block in sorted(blocks.items()):
        start,stop,_=groups[g];second,end,_=groups[h]
        for i in range(start,stop):
            for j in range(max(i,second) if g==h else second,end):
                value=block[i-start,j-second]
                if g==h and i!=j:value+=block[j-start,i-second]
                if not value.is_zero():accumulate(sparse,(i,j),value)
    return clean(sparse)
