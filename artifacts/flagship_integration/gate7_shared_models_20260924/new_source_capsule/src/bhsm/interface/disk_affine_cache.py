"""Bounded-memory, outward cache for large shared-expression compilers.

Arb's public constructor can enlarge a serialized radius. Every assignment
therefore decodes its stored value immediately, including cache hits. This
fixed outward conversion is deterministic and is part of this compiler's
arithmetic, rather than depending on eviction order or available memory.
The exact symbolic expression is unaffected.
"""
from collections import OrderedDict
import json
import sqlite3
from flint import arb, fmpq
from bhsm.interface.shared_expression_graph import pair, restore
from bhsm.interface.sparse_affine_enclosure import SparseAffine


class DiskAffineCache:
    def __init__(self, backend, capacity=2048):
        self.backend, self.capacity = backend, capacity
        self.cache = OrderedDict()
        self.db = sqlite3.connect('')
        self.db.execute('PRAGMA journal_mode=OFF')
        self.db.execute('PRAGMA synchronous=OFF')
        self.db.execute('PRAGMA cache_size=-8192')
        self.db.execute('CREATE TABLE bounds(id INTEGER PRIMARY KEY, payload TEXT NOT NULL)')

    def __contains__(self, index):
        return index in self.cache or self.db.execute('SELECT 1 FROM bounds WHERE id=?', (index,)).fetchone() is not None

    def decode(self, payload):
        c, a, r = json.loads(payload)
        return SparseAffine(self.backend, restore(c), {int(i): restore(v) for i, v in a}, arb(fmpq(r)))

    def remember(self, index, value):
        self.cache[index] = value
        self.cache.move_to_end(index)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
        return value

    def __getitem__(self, index):
        if index in self.cache:
            self.cache.move_to_end(index)
            return self.cache[index]
        row = self.db.execute('SELECT payload FROM bounds WHERE id=?', (index,)).fetchone()
        if row is None:
            raise KeyError(index)
        return self.remember(index, self.decode(row[0]))

    def __setitem__(self, index, value):
        payload = json.dumps([pair(value.c), [[i, pair(v)] for i, v in sorted(value.coefficients.items())], str(value.r.fmpq())], separators=(',', ':'))
        self.db.execute('INSERT OR REPLACE INTO bounds VALUES (?,?)', (index, payload))
        self.remember(index, self.decode(payload))
