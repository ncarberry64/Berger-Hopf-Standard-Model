"""Read large immutable graph JSON without materializing its node array."""
import gzip,json


class Reader:
    def __init__(self,stream):self.stream,self.buffer,self.position,self.eof=stream,'',0,False
    def fill(self):
        self.buffer=self.buffer[self.position:];self.position=0
        chunk=self.stream.read(65536)
        if not chunk:self.eof=True
        self.buffer+=chunk
    def character(self):
        while True:
            while self.position<len(self.buffer) and self.buffer[self.position].isspace():self.position+=1
            if self.position<len(self.buffer):return self.buffer[self.position]
            if self.eof:return ''
            self.fill()
    def expect(self,char):
        if self.character()!=char:raise ValueError('malformed graph JSON; expected '+char)
        self.position+=1
    def value(self):
        self.character();decoder=json.JSONDecoder()
        while True:
            try:
                value,end=decoder.raw_decode(self.buffer,self.position)
                if end==len(self.buffer) and not self.eof:
                    self.fill();continue
                self.position=end
                return value
            except json.JSONDecodeError:
                if self.eof:raise
                self.fill()


def read_graph(path,on_node=None):
    """Return metadata; optionally visit each node in topological order."""
    metadata={};count=0
    with gzip.open(path,'rt',encoding='utf8') as stream:
        r=Reader(stream);r.expect('{')
        while r.character()!='}':
            key=r.value()
            if not isinstance(key,str) or key in metadata:raise ValueError('unique object keys required')
            r.expect(':')
            if key=='nodes':
                if 'node_count' in metadata:raise ValueError('duplicate node array')
                r.expect('[')
                while r.character()!=']':
                    node=r.value()
                    if on_node is not None:on_node(count,node)
                    count+=1
                    if r.character()==']':break
                    r.expect(',')
                r.expect(']');metadata['node_count']=count
            else:metadata[key]=r.value()
            if r.character()=='}':break
            r.expect(',')
        r.expect('}')
        if r.character():raise ValueError('trailing graph data')
    if metadata.get('format')!='SHARED_EXPRESSION_DAG_V1' or 'node_count' not in metadata:
        raise ValueError('complete shared graph artifact required')
    return metadata
