"""Original serialization helpers; frozen evidence is shipped alongside."""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import io,json,zipfile
import numpy as np

def save(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')

def npz(p,arrays):
    with ZipFile(p,'x',ZIP_DEFLATED) as z:
        for k,v in sorted(arrays.items()):
            b=BytesIO();np.save(b,v,allow_pickle=False);i=ZipInfo(k+'.npy',(2026,11,3,0,0,0));i.compress_type=ZIP_DEFLATED;z.writestr(i,b.getvalue())
