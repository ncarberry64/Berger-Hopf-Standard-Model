from urllib.request import urlopen
from urllib.parse import urlencode
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
q="""SELECT targetid,mean_fiber_ra AS target_ra,mean_fiber_dec AS target_dec,z,zwarn,deltachi2,healpix,program,survey,spectype FROM desi_dr1.zpix WHERE survey='main' AND program IN ('bright','dark') AND mean_fiber_ra BETWEEN 146.055 AND 147.417 AND mean_fiber_dec BETWEEN 9.445 AND 10.784 AND healpix IN (4352,4353,27562,27563) AND z BETWEEN .18 AND .265 AND zwarn=0 AND spectype='GALAXY' AND deltachi2>=9"""
i=[('noirlab','https://datalab.noirlab.edu/tap/sync'),('beta','https://beta.datalab.noirlab.edu/tap/sync')]
def take(x):
 n,base=x
 try:
  with urlopen(base+'?'+urlencode(dict(REQUEST='doQuery',LANG='ADQL',FORMAT='csv',QUERY=q)),timeout=20) as f:s=f.read().decode()
  if 'targetid' not in s.splitlines()[0].lower() or s.startswith('<?'):raise ValueError(s[:1000])
  Path(f'jackpot_desi_tap_{n}.csv').write_text(s)
  print(n,len(s.splitlines()),s[:400],flush=True)
 except Exception as e:print(n,repr(e),getattr(e,'read',lambda:b'')()[:1200],flush=True)
with ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(take,i))
