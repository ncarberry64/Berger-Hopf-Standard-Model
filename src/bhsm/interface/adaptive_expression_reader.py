"""Read immutable graphs with bounded streaming and adaptive metadata reads.

The original reader remains frozen with the active model producers. Large
c/a/r metadata objects otherwise cause repeated decoding after each 64 KiB
increment. Geometric growth avoids that quadratic parsing cost without
changing a byte of model data or repeating a scientific calculation.
"""
import gzip,json
from bhsm.interface.streamed_expression_artifact import Reader


class AdaptiveReader(Reader):
    def fill_more(self,size):
        self.buffer=self.buffer[self.position:];self.position=0
        chunk=self.stream.read(size)
        if not chunk:self.eof=True
        self.buffer+=chunk

    def value(self):
        self.character();decoder=json.JSONDecoder();size=65536
        while True:
            try:
                value,end=decoder.raw_decode(self.buffer,self.position)
                if end==len(self.buffer) and not self.eof:
                    self.fill_more(size);continue
                self.position=end
                return value
            except json.JSONDecodeError:
                if self.eof:raise
                self.fill_more(size);size=min(32*1024*1024,2*size)


def read_graph(path,on_node=None):
    metadata={};count=0
    with gzip.open(path,'rt',encoding='utf8') as stream:
        r=AdaptiveReader(stream);r.expect('{')
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
