import numpy as np,pandas as pd
def compressed_roll(A,fn):
    out=np.full(A.shape,np.nan)
    for j in range(A.shape[1]):
        idx=np.where(~np.isnan(A[:,j]))[0]
        if len(idx)==0:continue
        out[idx,j]=fn(pd.Series(A[idx,j])).values
    return out
def build(path='adj.npz'):
    z=np.load(path);O,H,L,C,V=z['O'],z['H'],z['L'],z['C'],z['V']
    N,M=C.shape;F={}
    F['dates']=z['dates'];F['tick']=z['tick'];F['O'],F['H'],F['L'],F['C']=O,H,L,C
    for n in (50,100,200):F['s%d'%n]=compressed_roll(C,lambda s,n=n:s.rolling(n).mean())
    # TR on traded bars
    TR=np.full(C.shape,np.nan)
    for j in range(M):
        idx=np.where(~np.isnan(C[:,j]))[0]
        if len(idx)==0:continue
        c=C[idx,j];h=H[idx,j];l=L[idx,j];pc=np.r_[np.nan,c[:-1]]
        tr=np.fmax(h-l,np.fmax(np.abs(h-pc),np.abs(l-pc)));tr[0]=h[0]-l[0]
        TR[idx,j]=tr
    F['atr20']=compressed_roll(TR,lambda s:s.rolling(20).mean())
    for n in (20,40,55,70):F['hh%d'%n]=compressed_roll(H,lambda s,n=n:s.shift(1).rolling(n).max())
    F['ll20']=compressed_roll(L,lambda s:s.shift(1).rolling(20).min())
    F['rto']=compressed_roll(C*V,lambda s:s.rolling(20).mean())
    Cf=pd.DataFrame(C).ffill().values;F['Cf']=Cf
    F['set']=pd.Series(z['SETc']).ffill().values
    F['set200']=pd.Series(F['set']).rolling(200).mean().values
    # breadth: % common stocks above own SMA50 (traded today, min 100 names)
    ab=(C>F['s50']*(1+1e-6));cnt=(~np.isnan(C)&~np.isnan(F['s50'])).sum(1)
    br=np.where(cnt>=100,(ab&~np.isnan(F['s50'])).sum(1)/np.maximum(cnt,1)*100,np.nan);F['breadth']=br
    return F
if __name__=='__main__':
    import pickle,time;t=time.time();F=build();pickle.dump(F,open('F.pkl','wb'),protocol=4);print('built',time.time()-t)
