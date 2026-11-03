"""Original serialization helpers; frozen evidence is shipped alongside."""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import io,json,zipfile
import numpy as np

def save(path,value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')

def npz(path,arrays):
    with ZipFile(path,'x',ZIP_DEFLATED) as z:
        for key,value in sorted(arrays.items()):
            buf=BytesIO();np.save(buf,value,allow_pickle=False)
            info=ZipInfo(key+'.npy',(2026,11,3,0,0,0));info.compress_type=ZIP_DEFLATED
            z.writestr(info,buf.getvalue())
