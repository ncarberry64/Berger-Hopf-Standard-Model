"""Source-only reconstruction from published positions; no lens centers or masses.
CL0024: arXiv:1709.03531 Table 2.
MACS J0416: A&A 674 A79 Table A.1, System 12.
"""
import itertools as it
import json
import numpy as np

cl = np.array([
[[65452,15418],[65486,15421],[65495,15453],[65505,15463],[65520,15470],[65528,15463]],
[[65700,15722],[65710,15702],[65688,15700],[65684,15695],[65683,15685],[65689,15678]],
[[65800,16163],[65823,16128],[65813,16178],[65815,16183],[65824,16173],[65832,16154]],
[[64345,16557],[64336,16524],[64311,16524],[64304,16517],[64298,16503],[64303,16495]],
[[64756,16184],[64739,16187],[64739,16175],[64736,16173],[64729,16171],[64724,16173]]
], dtype=float)
macs = np.array([
[[36838,-67456],[36658,-67316],[36567,-67368],[36283,-67485],[36904,-67201],[36608,-67572]],
[[36504,-67024],[36592,-67231],[36496,-67272],[36267,-67462],[36833,-67101],[36292,-67157]]
],dtype=float)
cl = (cl-cl[0,0])*.036*np.array([np.cos(np.deg2rad(17.16)),1])
macs = (macs-macs[0,0])*.0036*np.array([np.cos(np.deg2rad(24.067)),1])

def solve(X,Y,sign,scaled):
    u,s,v = np.linalg.svd(X.T@Y)
    d = sign*np.linalg.det(u@v)
    R = u@np.diag([1.,d])@v
    if scaled: R *= (s[0]+d*s[1])/np.sum(X**2)
    return R

def run(a,b,ntrain):
    es={k:[] for k in ('shift','mirror','rotate','mirror_scale','rotate_scale','affine')}
    per=[]
    for tr in it.combinations(range(len(a)),ntrain):
        te=[i for i in range(len(a)) if i not in tr]
        tr=list(tr)
        A=a[tr].mean(axis=0); B=b[tr].mean(axis=0)
        X=a[tr]-A; Y=b[tr]-B
        maps={'shift': np.eye(2),'mirror':solve(X,Y,-1,False),'rotate':solve(X,Y,1,False),'mirror_scale':solve(X,Y,-1,True),'rotate_scale':solve(X,Y,1,True)}
        if ntrain>=3:
            maps['affine']=np.linalg.lstsq(X,Y,rcond=None)[0]
        row={}
        for k,M in maps.items():
            e=np.linalg.norm((a[te]-A)@M+B-b[te],axis=1)
            es[k].extend(e)
            row[k]=float(np.sqrt(np.mean(e**2)))
        per.append(row)
    return {'ntrain':ntrain,'folds':len(per),'rms':{k:float(np.sqrt(np.mean(np.square(v)))) for k,v in es.items() if v},
      'mirror_beats_rotation_folds':sum(x['mirror']<x['rotate'] for x in per)}
def main():
    tests={'MACS0416-12b-c':macs,'MACS0416-12b-c-no-closest':macs[:,[0,1,2,4,5]],
      **{f'CL0024-1-{i+1}':cl[[0,i]] for i in range(1,5)}}
    return {k:[run(*v,n) for n in [2,len(v[0])-1]] for k,v in tests.items()}
if __name__=='__main__':
 print(json.dumps(main(),indent=2))
