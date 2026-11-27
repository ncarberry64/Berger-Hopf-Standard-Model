import numpy as np
def pix(ra,de,n):
 z=np.sin(np.radians(de));t=(ra%360)/90
 assert abs(z)<2/3
 a=int(n*(.5+t-.75*z));b=int(n*(.5+t+.75*z))
 fa,fb=a//n,b//n
 f=(fa|4) if fa==fb else fa if fa<fb else fb+8
 ix=b%n;iy=n-a%n-1
 part=lambda u:sum(((u>>i)&1)<<(2*i) for i in range(n.bit_length()-1))
 return n*n*f+part(ix)+2*part(iy)
ra,de=146.73617048,10.1146953
for n in [32,64,128]:
 print(n,pix(ra,de,n),sorted(set(pix(ra+x/np.cos(np.radians(de)),de+y,n) for x in np.linspace(-.69,.69,280) for y in np.linspace(-.69,.69,280) if x*x+y*y<.685**2)))
