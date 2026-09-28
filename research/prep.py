import pandas as pd,numpy as np,re
df=pd.read_pickle('panel.pkl')
setdays=set(df[df.t=='SET'].d)
df=df[df.d.isin(setdays)]
WL={'COM7','PR9','I2','A5','BE8','ATP30','2S','88TH','S11','B52','7UP','3K'}
FUNDS=set('VAYU1,TIF1,MNIT2,GLD,TDEX,LHHOTEL,WHART,WHAIR,IMPACT,PROSPECT,AIMIRT,AXTRART,FUTURERT,SIRIPRT,SSTRT,1DIV,BSET100,CHINA,BMSCG,BMSCITH,UBOT,UHERO,ENGY,BCHINA,GLDTH,TDEX'.split(','))
def common(t):
    if t in ('SET','SET50','SET100','MAI'):return False
    if not re.match(r'^[A-Z0-9]{1,8}$',t):return False
    if t in FUNDS or re.search(r'(IF|REIT)$',t):return False
    if re.search(r'\d',t) and t not in WL:return False
    return True
df=df[df.t.map(common)|df.t.isin(['SET','SET50','SET100','MAI'])]
print('tickers',df.t.nunique(),'rows',len(df))
dates=np.sort(df.d.unique());N=len(dates);di={d:i for i,d in enumerate(dates)}
tick=sorted(t for t in df.t.unique() if t not in ('SET','SET50','SET100','MAI'))
ti={t:i for i,t in enumerate(tick)}
M=len(tick)
O,H,L,C,V=[np.full((N,M),np.nan) for _ in range(5)]
sub=df[df.t.isin(ti)]
r=sub.d.map(di).values;c=sub.t.map(ti).values
for A,col in ((O,'o'),(H,'h'),(L,'l'),(C,'c'),(V,'v')):A[r,c]=sub[col].values
st=df[df.t=='SET'].set_index('d').sort_index()
SET=st.reindex(dates)
np.savez_compressed('dense.npz',dates=dates,tick=np.array(tick),O=O,H=H,L=L,C=C,V=V,SETc=SET.c.values,SETo=SET.o.values)
# jump check
ret=C[1:]/np.fmax(np.where(np.isnan(C[:-1]),np.nan,C[:-1]),1e-9)-1
TO=C*V
big=np.argwhere(np.abs(ret)>0.35)
liq=[(dates[i+1],tick[j],round(ret[i,j],3)) for i,j in big if np.nanmean(TO[max(0,i-20):i+1,j])>50e6]
print('jumps>35% total',len(big),'in liquid names',len(liq));print(liq[:25])
print('N days',N,'M stocks',M)
