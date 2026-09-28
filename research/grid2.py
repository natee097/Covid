import engine,itertools,json
from multiprocessing import Pool
DEV=(20060101,20211231)
B=dict(fam='bo',bo=55,trend=True,exit_sma=100,atr_k=3.0,size='equal',minTO=50e6,maxpos=10)
def job(cfg):
    c=dict(B);c.update(cfg);r=engine.run(c,*DEV);return cfg,{k:float(v) for k,v in r.items()}
if __name__=='__main__':
    cfgs=[{}]
    for rg,br in [('breadth',40),('breadth',50),('both',40),('both',50),('none',0)]:cfgs.append(dict(regime=rg,br_min=br))
    for mp in (8,12,15):cfgs.append(dict(maxpos=mp))
    for a in (5,7,10):cfgs.append(dict(max_atrp=a))
    for m in (100e6,):cfgs.append(dict(minTO=m))
    for k in (2.5,3.5,4.0):cfgs.append(dict(atr_k=k))
    for bo in (40,70):cfgs.append(dict(bo=bo))
    cfgs.append(dict(exit_sma=200));cfgs.append(dict(exit_sma=50,atr_k=3.0))
    cfgs.append(dict(size='risk',risk=1.0,even=True));cfgs.append(dict(size='risk',risk=0.75,even=True))
    with Pool(4) as p:res=p.map(job,cfgs)
    json.dump(res,open('grid2_dev.json','w'))
    for c,r in res:print(round(r['mar'],3),round(r['cagr'],1),round(r['mdd'],1),round(r['sharpe'],2),int(r['n']),round(r['worst_y'],1),round(r['expo']),c)
