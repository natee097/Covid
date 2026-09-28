import numpy as np
NICE=[1.25,1.5,2,2.5,3,4,5,8,10,20,25,50,100]
def snap(r):
    best=r;bd=0.08
    for k in NICE:
        for x in (k,1/k):
            d=abs(r/x-1)
            if d<bd:bd=d;best=x
    return best
def tick_size(p):
    for lim,t in ((2,0.01),(5,0.02),(10,0.05),(25,0.1),(100,0.25),(200,0.5),(400,1.0)):
        if p<lim:return t
    return 2.0
def adjust(O,H,L,C,V,thr=0.34,maxgap=3):
    """back-adjust splits: consecutive-day open vs prev close move beyond the ±30% limit = corporate action"""
    O,H,L,C,V=[a.copy() for a in (O,H,L,C,V)]
    N,M=C.shape;events=[]
    for j in range(M):
        idx=np.where(~np.isnan(C[:,j]))[0]
        if len(idx)<2:continue
        for a,b in zip(idx[:-1],idx[1:]):
            if b-a>maxgap:continue                 # หยุดพักการซื้อขาย: ถือว่าเป็นราคาจริง
            p=C[a,j];o=O[b,j] if not np.isnan(O[b,j]) and O[b,j]>0 else C[b,j]
            if not(p>0 and o>0):continue
            r=o/p
            if abs(o-p)>=(0.30*p+2*tick_size(p))*(1-1e-6):   # เสมอ = เหตุการณ์บริษัท
                f=snap(r)
                O[:b,j]*=f;H[:b,j]*=f;L[:b,j]*=f;C[:b,j]*=f;V[:b,j]/=f
                events.append((b,j,r,f))
    return O,H,L,C,V,events
if __name__=='__main__':
    z=np.load('dense.npz');dates=z['dates'];tick=z['tick']
    O,H,L,C,V,ev=adjust(z['O'],z['H'],z['L'],z['C'],z['V'])
    print('events',len(ev))
    for b,j,r,f in ev[:12]:print(dates[b],tick[j],round(r,3),round(f,4))
    for name in ['CPALL','BANPU','BDMS','PTT','BTS']:
        j=list(tick).index(name);e=[(dates[b],round(r,3),round(f,4)) for b,jj,r,f in ev if jj==j];print(name,e)
    np.savez_compressed('adj.npz',dates=dates,tick=tick,O=O,H=H,L=L,C=C,V=V,SETc=z['SETc'],SETo=z['SETo'])
    import pandas as pd
    Cf=pd.DataFrame(C).ffill().values;prev=np.vstack([np.full((1,C.shape[1]),np.nan),Cf[:-1]])
    ret=C/prev-1;TO=pd.DataFrame(C*V).rolling(20,min_periods=5).mean().shift(1).values
    print('remaining liquid jumps>32%:',int(((np.abs(ret)>0.32)&(TO>50e6)).sum()))
