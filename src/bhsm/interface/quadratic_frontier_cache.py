"""Bounded live compiler frontier with verified bit-exact Arb round trips."""
import marshal
import sqlite3
from collections import OrderedDict
from flint import arb
from bhsm.interface.sparse_quadratic_enclosure import QuadraticModel


def pack_ball(x):
    return tuple(map(int,x.mid().man_exp())),tuple(map(int,x.rad().man_exp()))


def unpack_ball(row):
    """Restore exactly or fail; never let eviction alter an enclosure.

    Arb's public radius constructor rounds upward. Feed a dyadic strictly
    below the stored 30-bit magnitude and verify the result against BOTH
    stored endpoints of the representation. The verification is essential;
    this is not an assumption about a future python-flint implementation.
    """
    m,(r,e)=row
    if not r:
        value=arb(m)
    else:
        shift=max(0,30-r.bit_length())
        value=arb(m,(((r<<shift)*4-1),e-shift-2))
    if pack_ball(value)!=row:
        raise ArithmeticError('bit-exact Arb restoration unavailable')
    return value


class FrontierCache:
    def __init__(self, domain, path, capacity=400000):
        self.domain,self.capacity,self.weight=domain,capacity,0
        self.cache=OrderedDict();self.spilled=set()
        self.db=sqlite3.connect(str(path))
        self.db.execute('PRAGMA journal_mode=OFF')
        self.db.execute('PRAGMA synchronous=OFF')
        self.db.execute('PRAGMA cache_size=-8192')
        self.db.execute('CREATE TABLE live(id INTEGER PRIMARY KEY,payload BLOB)')

    def encode(self,v):
        return marshal.dumps((pack_ball(v.c),[(i,pack_ball(x)) for i,x in v.a.items()],
                              v.q,pack_ball(v.qb),[(k,pack_ball(x)) for k,x in v.tails.items()]))

    def decode(self,payload):
        c,a,q,qb,tails=marshal.loads(payload)
        return QuadraticModel(self.domain,unpack_ball(c),{i:unpack_ball(v) for i,v in a},q,
                              unpack_ball(qb),{k:unpack_ball(v) for k,v in tails})

    def __setitem__(self,i,v):
        if i in self.cache:
            self.weight-=len(self.cache.pop(i).a)+8
        self.cache[i]=v;self.weight+=len(v.a)+8
        while self.weight>self.capacity and len(self.cache)>1:
            j,x=self.cache.popitem(last=False);self.weight-=len(x.a)+8
            if j not in self.spilled:
                payload=self.encode(x)
                # Verify every ball before saving; cache hits and misses have
                # identical c/a/q/r, without repeated outward inflation.
                self.decode(payload)
                self.db.execute('INSERT INTO live VALUES (?,?)',(j,payload));self.spilled.add(j)

    def __getitem__(self,i):
        if i in self.cache:
            self.cache.move_to_end(i);return self.cache[i]
        row=self.db.execute('SELECT payload FROM live WHERE id=?',(i,)).fetchone()
        if row is None:raise KeyError(i)
        v=self.decode(row[0]);self[i]=v;return v

    def __delitem__(self,i):
        if i in self.cache:self.weight-=len(self.cache.pop(i).a)+8
        if i in self.spilled:
            self.db.execute('DELETE FROM live WHERE id=?',(i,));self.spilled.remove(i)

    def __len__(self):return len(self.spilled|self.cache.keys())
