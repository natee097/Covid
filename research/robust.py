import engine,numpy as np
NEW=dict(fam='bo',bo=55,trend=True,exit_sma=100,atr_k=3.0,size='equal',minTO=50e6,maxpos=10,regime='both',br_min=50)
engine.load()
for sl in (0.0015,0.003):
    engine.SLIP=sl
    for nm,c in (('current',{}),('new',NEW)):
        r=engine.run(c,20060101,20260925);print(f'slip {sl*1e4:.0f}bps {nm:8s} CAGR {r["cagr"]:5.1f} MDD {r["mdd"]:6.1f}')
engine.SLIP=0.0015
print('rolling 5y windows (start Jan):')
for y in range(2006,2022):
    a=y*10000+101;b=(y+5)*10000+101 if y+5<=2026 else 20260925
    rn=engine.run(NEW,a,b);rc=engine.run({},a,b)
    print(y,'-',min(y+5,2026),f'new CAGR {rn["cagr"]:5.1f} MDD {rn["mdd"]:6.1f} | current CAGR {rc["cagr"]:5.1f} MDD {rc["mdd"]:6.1f}')
