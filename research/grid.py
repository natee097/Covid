import engine,itertools,json,sys
from multiprocessing import Pool
DEV=(20060101,20211231)
def job(cfg):
    engine.load()
    r=engine.run(cfg,*DEV)
    return cfg,{k:float(v) for k,v in r.items()}
if __name__=='__main__':
    cfgs=[]
    for bo,tr,(sx,k),size,mto,mp in itertools.product([20,55],[False,True],[(50,2.0),(None,3.0),(100,3.0)],['risk','equal'],[50e6,200e6],[5,10]):
        cfgs.append(dict(fam='bo',bo=bo,trend=tr,exit_sma=sx,atr_k=k,size=size,minTO=mto,maxpos=mp,even=(size=='risk')))
    for lb,sk,mp,ts,mto,rg in itertools.product([126,252],[0,21],[5,10],[None,100,200],[50e6,200e6],['sma200','none']):
        cfgs.append(dict(fam='mom',mom_lb=lb,mom_skip=sk,maxpos=mp,trend_sma=ts,minTO=mto,regime=rg,size='equal'))
    with Pool(4) as p:res=p.map(job,cfgs)
    json.dump(res,open('grid_dev.json','w'))
    res.sort(key=lambda x:-x[1]['mar'])
    for c,r in res[:25]:print(round(r['mar'],3),round(r['cagr'],1),round(r['mdd'],1),round(r['sharpe'],2),int(r['n']),round(r['worst_y'],1),c)
