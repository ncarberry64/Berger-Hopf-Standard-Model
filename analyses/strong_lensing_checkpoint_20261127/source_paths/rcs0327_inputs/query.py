import urllib.request as u,urllib.parse as p,json
q={"service":"Mast.Caom.Filtered","params":{"columns":"*","filters":[{"paramName":"proposal_id","values":["12267"]},{"paramName":"obs_collection","values":["HST"]}]},"format":"json","pagesize":200,"page":1}
for u0 in ['https://mast.stsci.edu/api/v0/invoke','https://mast.stsci.edu/api/v0.1/invoke']:
 for method,arg in [('get','params'),('post','data')]:
  try:
   d=p.urlencode({"request":json.dumps(q)})
   with u.urlopen(u.Request(u0+"?"+d if method=="get" else u0,data=d.encode() if method=="post" else None),timeout=12) as r: a=r.read()
   print(a[:200],flush=True)
   if "data" in json.loads(a): open("rcs0327_inputs/mast.json","wb").write(a); quit()
  except Exception as e:print(e,flush=True)
