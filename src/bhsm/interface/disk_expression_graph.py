"""Disk-backed canonical node storage with the same expression semantics."""
from collections import OrderedDict
import json,sqlite3
from bhsm.interface.shared_expression_graph import ExpressionDomain,Expression


class Nodes(list):
    def __init__(self,domain):self.domain=domain
    def __len__(self):return self.domain.count
    def __iter__(self):
        for row in self.domain.db.execute('SELECT payload FROM nodes ORDER BY id'):
            yield json.loads(row[0])
    def __getitem__(self,index):
        d=self.domain
        if isinstance(index,slice):
            start,stop,stride=index.indices(len(self))
            if stride!=1:return [self[i] for i in range(start,stop,stride)]
            return [json.loads(row[0]) for row in d.db.execute('SELECT payload FROM nodes WHERE id>=? AND id<? ORDER BY id',(start,stop))]
        if index<0:index+=len(self)
        if not 0<=index<len(self):raise IndexError(index)
        if index not in d.cache:
            d.cache[index]=json.loads(d.db.execute('SELECT payload FROM nodes WHERE id=?',(index,)).fetchone()[0])
            if len(d.cache)>4096:d.cache.popitem(last=False)
        return d.cache[index]


class DiskExpressionDomain(ExpressionDomain):
    def __init__(self,groups,names):
        super().__init__(groups,names)
        # SQLite's empty filename creates an OS temporary disk database.
        # Completed scientific blocks are saved separately by the producer.
        self.db=sqlite3.connect('')
        self.db.execute('PRAGMA journal_mode=OFF')
        self.db.execute('PRAGMA synchronous=OFF')
        self.db.execute('PRAGMA cache_size=-16384')
        self.db.execute('CREATE TABLE nodes(id INTEGER PRIMARY KEY,payload TEXT NOT NULL UNIQUE)')
        self.count=0;self.cache=OrderedDict();self.keys=OrderedDict();self.nodes=Nodes(self)
    def node(self,data):
        key=json.dumps(data,separators=(',',':'),sort_keys=True)
        if key in self.keys:return Expression(self,self.keys[key])
        row=self.db.execute('SELECT id FROM nodes WHERE payload=?',(key,)).fetchone()
        if row is None:
            index=self.count;self.count+=1
            self.db.execute('INSERT INTO nodes VALUES (?,?)',(index,key))
            self.digest.update(key.encode()+b'\n')
        else:index=row[0]
        self.keys[key]=index
        if len(self.keys)>4096:self.keys.popitem(last=False)
        return Expression(self,index)
