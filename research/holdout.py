import engine,numpy as np,json
F=engine.load();D=F['dates']
NEW=dict(fam='bo',bo=55,trend=True,exit_sma=100,atr_k=3.0,size='equal',minTO=50e6,maxpos=10,regime='both',br_min=50)
NEWnoBR=dict(NEW,regime='sma200')
BASE={}
def setbh(a,b):
    i0=max(np.searchsorted(D,a),260);i1=np.searchsorted(D,b,side='right');s=F['set'][i0:i1];pk=np.maximum.accumulate(s)
    return dict(cagr=((s[-1]/s[0])**(245/len(s))-1)*100,mdd=(s/pk-1).min()*100)
out={}
for per,(a,b) in {'dev':(20060101,20211231),'hold':(20220101,20260925),'full':(20060101,20260925)}.items():
    print('==',per,a,b,'SET B&H',{k:round(v,1) for k,v in setbh(a,b).items()})
    for nm,c in (('current v7',BASE),('new',NEW),('new w/o breadth',NEWnoBR)):
        r=engine.run(c,a,b,log=True)
        print(f"  {nm:16s} CAGR {r['cagr']:6.1f}  MDD {r['mdd']:6.1f}  MAR {r['mar']:5.2f}  Sharpe {r['sharpe']:4.2f}  trades {r['n']:4d}  win {r['wr']:4.1f}%  PF {r['pf']:4.2f}  worstY {r['worst_y']:6.1f}  expo {r['expo']:3.0f}%")
        if per=='hold' or per=='full':print('     years',[(int(y),round(v,1)) for y,v in r['years']])
