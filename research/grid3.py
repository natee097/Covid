import engine,json
from multiprocessing import Pool
DEV=(20060101,20211231)
B=dict(fam='bo',bo=55,trend=True,exit_sma=100,atr_k=3.0,size='equal',minTO=50e6,maxpos=10,regime='both',br_min=50)
def job(cfg):
    c=dict(B);c.update(cfg);r=engine.run(c,*DEV);return cfg,{k:float(v) for k,v in r.items()}
if __name__=='__main__':
    cfgs=[dict(br_min=b) for b in (42,45,48,50,52,55,58,60)]+[dict(minTO=m) for m in (20e6,30e6,40e6,60e6,70e6,80e6)]
    cfgs+=[dict(regime='breadth',br_min=b) for b in (45,55,60)]
    with Pool(4) as p:res=p.map(job,cfgs)
    for c,r in res:print(round(r['mar'],3),round(r['cagr'],1),round(r['mdd'],1),round(r['sharpe'],2),int(r['n']),round(r['worst_y'],1),round(r['expo']),c)
