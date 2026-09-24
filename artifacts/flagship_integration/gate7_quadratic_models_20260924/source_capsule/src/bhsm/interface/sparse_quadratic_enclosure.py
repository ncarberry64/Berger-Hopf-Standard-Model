"""Degree-two product-ball Taylor models with disk-backed factored quadratics.

Coefficient convention: q[(i,j)] multiplies theta_i theta_j once, i <= j.
Intermediate forms are sparse linear circuits of outer-product atoms; only
requested outputs are expanded. This is a numerical compiler, not a producer
of scientific expressions or an authority for unresolved auxiliary leaves.
"""
import json
import sqlite3
from collections import defaultdict
from flint import arb, fmpq
from bhsm.interface.shared_expression_graph import pair, restore
from bhsm.interface.shared_parameter_residual import validate_groups


def upper(x):
    return abs(x).upper()


def clean(values):
    return {k: v for k, v in values.items() if not v.is_zero()}


def accumulate(out, key, value):
    out[key] = out.get(key, arb(0)) + value


class QuadraticStore:
    """Append-only coefficient circuit, bounded SQLite page cache, no dense Q."""
    def __init__(self, path=':memory:'):
        self.db = sqlite3.connect(str(path))
        self.db.execute('PRAGMA journal_mode=OFF')
        self.db.execute('PRAGMA synchronous=OFF')
        self.db.execute('PRAGMA cache_size=-8192')
        self.db.execute('CREATE TABLE IF NOT EXISTS q(id INTEGER PRIMARY KEY, payload TEXT)')
        self.count = self.db.execute('SELECT COALESCE(MAX(id),0) FROM q').fetchone()[0]

    def add(self, links=(), left=None, right=None):
        combined = {}
        for i, c in links:
            if i and not c.is_zero():
                accumulate(combined, i, c)
        combined = clean(combined)
        atom = bool(left) and bool(right)
        if not combined and not atom:
            return 0
        if len(combined) == 1 and not atom:
            i, c = next(iter(combined.items()))
            if c == 1:
                return i
        self.count += 1
        row = [[[i, pair(v)] for i, v in sorted(combined.items())],
               [[i, pair(v)] for i, v in sorted((left or {}).items())],
               [[i, pair(v)] for i, v in sorted((right or {}).items())]]
        self.db.execute('INSERT INTO q VALUES (?,?)', (self.count, json.dumps(row, separators=(',', ':'))))
        return self.count

    def expand(self, links):
        """Reverse accumulation fuses shared circuit nodes before monomials.

        Pending coefficients live on disk as necessary in the SQLite circuit;
        the frontier contains scalar adjoints, never intermediate Q matrices.
        """
        import heapq
        pending = {}
        heap = []
        def put(i, v):
            if not i or v.is_zero():
                return
            if i not in pending:
                pending[i] = arb(0)
                heapq.heappush(heap, -i)
            pending[i] += v
        for i, v in links:
            put(i, v)
        out = {}
        while heap:
            i = -heapq.heappop(heap)
            weight = pending.pop(i)
            if weight.is_zero():
                continue
            row = self.db.execute('SELECT payload FROM q WHERE id=?', (i,)).fetchone()
            links, left, right = json.loads(row[0])
            for j, c in links:
                put(j, weight * restore(c))
            a = [(j, restore(v)) for j, v in left]
            b = [(j, restore(v)) for j, v in right]
            for j, x in a:
                for k, y in b:
                    accumulate(out, (min(j, k), max(j, k)), weight*x*y)
        return clean(out)


class QuadraticDomain:
    def __init__(self, groups, dimension, store=None):
        validate_groups(groups, dimension)
        self.groups, self.dimension = tuple(groups), dimension
        self.store = store or QuadraticStore()
        self.group_of = {i: g for g, (a, b, _) in enumerate(groups) for i in range(a, b)}

    def linear_bound(self, a):
        totals = [arb(0) for _ in self.groups]
        for i, v in a.items():
            g = self.group_of[i]
            totals[g] += upper(v)**2 if self.groups[g][2] == 'euclidean' else upper(v)
        return sum((v.sqrt() if self.groups[g][2] == 'euclidean' else v
                    for g, v in enumerate(totals)), arb(0)).upper()

    def model(self, c=0, a=None, tails=None):
        return QuadraticModel(self, arb(c), a or {}, 0, arb(0), tails or {})

    def polynomial_range(self, c, a, q):
        """Outward block support, without boxing Euclidean coordinates.

        Scalar diagonal+linear blocks use the exact stationary-point formula
        (interval coefficients handled by a separate outward uncertainty).
        Symmetric Euclidean diagonal blocks use a sparse Gershgorin enclosure;
        cross blocks use min(Frobenius,sqrt(norm1*normInf)) operator bounds.
        Cross-block signs survive coefficient fusion, but independent block
        support is an explicitly reported relaxation.
        """
        blocks = defaultdict(dict)
        for (i, j), v in sorted(q.items()):
            blocks[self.group_of[i], self.group_of[j]][i, j] = v
        result = arb(c)
        used = set()
        structure = []
        for g, (start, stop, kind) in enumerate(self.groups):
            if kind != 'interval':
                continue
            l = a.get(start, arb(0)); d = blocks.pop((g, g), {}).get((start, start), arb(0))
            lm, dm = l.mid(), d.mid()
            candidates = [-lm+dm, lm+dm]
            if not dm.is_zero():
                point = -lm/(2*dm)
                if point.lower() >= -1 and point.upper() <= 1:
                    candidates.append(-lm*lm/(4*dm))
                elif point.contains(-1) or point.contains(1):
                    # Ambiguous stationary-point location: retaining it enlarges.
                    candidates.append(-lm*lm/(4*dm))
            lo = min(v.lower() for v in candidates)
            hi = max(v.upper() for v in candidates)
            error = (l.rad()+d.rad()).upper()
            result += (lo+hi)/2 + arb(0, ((hi-lo)/2+error).upper())
            used.add(start)
        result += arb(0, self.linear_bound({i:v for i,v in a.items() if i not in used}))
        for (g, h), entries in sorted(blocks.items()):
            kg, kh = self.groups[g][2], self.groups[h][2]
            frob2 = arb(0); rows = {}; cols = {}
            if g == h and kg == 'euclidean':
                diagonal = {}; off = {}
                for (i, j), v in entries.items():
                    if i == j:
                        diagonal[i] = v
                        frob2 += upper(v)**2
                    else:
                        w = upper(v)/2
                        accumulate(off, i, w); accumulate(off, j, w)
                        frob2 += 2*w*w
                indices = range(self.groups[g][0], self.groups[g][1])
                lo = min([arb(0)] + [(diagonal.get(i,arb(0))-off.get(i,arb(0))).lower() for i in indices])
                hi = max([arb(0)] + [(diagonal.get(i,arb(0))+off.get(i,arb(0))).upper() for i in indices])
                f = frob2.sqrt().upper()
                lo, hi = max(lo, -f), min(hi, f)
                result += (lo+hi)/2 + arb(0, ((hi-lo)/2).upper())
                bound = max(abs(lo), abs(hi)).upper()
                method = 'symmetric_Gershgorin_intersect_Frobenius'
            else:
                for (i, j), v in entries.items():
                    w = upper(v); frob2 += w*w
                    accumulate(rows, i, w); accumulate(cols, j, w)
                if kg != 'box' and kh != 'box':
                    bound = min(frob2.sqrt().upper(),
                                (max(v.upper() for v in rows.values())
                                 *max(v.upper() for v in cols.values())).sqrt().upper())
                    method = 'rectangular_operator_Frobenius_1_inf'
                else:
                    # Actual boxes only; no Euclidean group is coordinate-boxed.
                    if kg == 'euclidean':
                        bound = sum((v*v for v in rows.values()),arb(0)).sqrt().upper()
                    elif kh == 'euclidean':
                        bound = sum((v*v for v in cols.values()),arb(0)).sqrt().upper()
                    else:
                        bound = sum((upper(v) for v in entries.values()),arb(0)).upper()
                    method = 'actual_box_mixed_support'
                result += arb(0, bound)
            structure.append(dict(groups=[g,h], monomials=len(entries), method=method,
                                  frobenius_upper=str(frob2.sqrt().upper().fmpq()),
                                  support_upper=str(bound.fmpq())))
        return result, structure


class QuadraticModel:
    def __init__(self, d, c, a, q, qb, tails):
        self.domain, self.c, self.a, self.q, self.qb = d, c, clean(a), q, qb
        self.tails = clean(tails)
        self.lb = d.linear_bound(self.a)

    @property
    def r(self):
        return sum(self.tails.values(), arb(0)).upper()

    def support(self):
        return (upper(self.c)+self.lb+self.qb+self.r).upper()

    def scale(self, b):
        b = arb(b)
        return QuadraticModel(self.domain, self.c*b, {i:v*b for i,v in self.a.items()},
                              self.domain.store.add([(self.q,b)]), (self.qb*upper(b)).upper(),
                              {k:(v*upper(b)).upper() for k,v in self.tails.items()})

    def __add__(self, other):
        if not isinstance(other, QuadraticModel):
            other = self.domain.model(other)
        if other.domain is not self.domain:
            raise ValueError('one physical parameter domain required')
        a = self.a.copy(); tails = self.tails.copy()
        for i, v in other.a.items(): accumulate(a, i, v)
        for k, v in other.tails.items(): accumulate(tails, k, v)
        q = self.domain.store.add([(self.q,arb(1)),(other.q,arb(1))])
        return QuadraticModel(self.domain,self.c+other.c,a,q,(self.qb+other.qb).upper(),
                              {k:v.upper() for k,v in tails.items()})

    __radd__ = __add__
    def __neg__(self): return self.scale(-1)
    def __sub__(self, other): return self + (-other)
    def __rsub__(self, other): return other + (-self)
    def __mul__(self, other):
        if not isinstance(other, QuadraticModel): return self.scale(other)
        if other.domain is not self.domain: raise ValueError('one physical parameter domain required')
        a = {i:v*other.c for i,v in self.a.items()}
        for i,v in other.a.items(): accumulate(a,i,v*self.c)
        q = self.domain.store.add([(self.q,other.c),(other.q,self.c)],self.a,other.a)
        qb = (self.qb*upper(other.c)+other.qb*upper(self.c)+self.lb*other.lb).upper()
        tails = {}
        # |P_a e_b| + |P_b e_a| + |e_a e_b|; split the last equally
        # between source labels for a conservative additive diagnostic ledger.
        for model, factor in ((self,upper(other.c)+other.lb+other.qb+other.r/2),
                              (other,upper(self.c)+self.lb+self.qb+self.r/2)):
            for k,v in model.tails.items(): accumulate(tails,k,v*factor)
        high = self.lb*other.qb+other.lb*self.qb+self.qb*other.qb
        accumulate(tails,'cubic_and_higher',high)
        return QuadraticModel(self.domain,self.c*other.c,a,q,qb,{k:v.upper() for k,v in tails.items()})

    __rmul__ = __mul__

    def unary(self, op, lower=None):
        width = (self.lb+self.qb+self.r).upper()
        full = self.c+arb(0,width)
        if op == 'exp':
            f=self.c.exp(); first=f; second=f; third=full.exp().upper()
        elif op == 'log':
            safe=min(full.lower(),self.c.lower())
            if not safe>0: raise ArithmeticError('positive logarithm domain required')
            f=self.c.log(); first=1/self.c; second=-1/self.c**2; third=(2/safe**3).upper()
        elif op == 'inverse':
            safe=min(arb(lower),self.c.lower()) if lower is not None else abs(full).lower()
            if not safe>0: raise ArithmeticError('inverse domain crosses zero')
            f=1/self.c; first=-1/self.c**2; second=2/self.c**3; third=(6/safe**4).upper()
        elif op == 'sqrt_positive':
            f=self.c.sqrt(); safe=min(arb(lower),f.lower())
            if not safe>0: raise ArithmeticError('positive square-root domain required')
            first=1/(2*f); second=-1/(4*f**3); third=(3/(8*safe**5)).upper()
        else: raise ValueError(op)
        atom=self.domain.store.add(left=self.a,right=self.a)
        q=self.domain.store.add([(self.q,first),(atom,second/2)])
        qb=(upper(first)*self.qb+upper(second)*self.lb**2/2).upper()
        tails={k:(upper(first)*v).upper() for k,v in self.tails.items()}
        extra=self.qb+self.r
        # Taylor around c: retain first*Q and second*L^2/2 only.
        accumulate(tails,'cubic_and_higher',upper(second)*(2*self.lb*extra+extra**2)/2+third*width**3/6)
        return QuadraticModel(self.domain,f,{i:v*first for i,v in self.a.items()},q,qb,
                              {k:v.upper() for k,v in tails.items()})

    def expanded(self):
        return self.domain.store.expand([(self.q,arb(1))])

    def final_support(self):
        from bhsm.interface.block_quadratic_expansion import expand_batched
        from bhsm.interface.quadratic_group_support import grouped_range
        q=expand_batched(self.domain.store,[(self.q,arb(1))],self.domain.groups)
        interval,structure=grouped_range(self.domain,self.c,self.a,q)
        return (upper(interval)+self.r).upper(),q,structure
