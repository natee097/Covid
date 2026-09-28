import numpy as np,pickle
F=None
def load():
    global F
    if F is None:F=pickle.load(open('F.pkl','rb'))
    return F
FEE=0.0016;SLIP=0.0015;EPS=1e-6
BASE=dict(fam='bo',bo=20,exit_sma=50,atr_k=2.0,trend=False,regime='sma200',rank='c_s50',
          size='risk',risk=1.0,maxpos=5,even=False,minTO=50e6,gap=None,time_stop=None,
          # momentum family
          mom_lb=126,mom_skip=0,rebal=21,trend_sma=100,buffer=2.0,mom_stop=None)
def run(cfg,start,end,cap0=1_000_000,log=False):
    F=load();c=dict(BASE);c.update(cfg)
    D=F['dates'];O,H,L,C=F['O'],F['H'],F['L'],F['C'];N,M=C.shape
    i0=np.searchsorted(D,start);i1=np.searchsorted(D,end,side='right')
    i0=max(i0,260)
    cash=cap0;pos={};pendB=[];pendS=[];trades=[];eq=np.zeros(i1-i0);expo=0
    k=c['atr_k'];sx=c['exit_sma'];sxa=F['s%d'%sx] if sx else None
    hh=F['hh%d'%c['bo']] if c['fam']=='bo' else None
    last_reb=-10**9
    for n,i in enumerate(range(i0,i1)):
        # 1) fills at open
        for s in pendS:
            p=pos.pop(s,None)
            if p is None:continue
            px=O[i,s] if O[i,s]>0 else p['lc']
            px*=(1-SLIP);pro=px*p['q']*(1-FEE);cash+=pro
            trades.append((p['din'],D[i],s,p['fill'],px,p['q'],pro-p['cost']))
        pendS=[]
        for b in pendB:
            s,q,atr,sigc=b
            if s in pos or len(pos)>=c['maxpos']:continue
            if not O[i,s]>0:continue
            if c['gap'] and O[i,s]/sigc-1>c['gap']:continue
            px=O[i,s]*(1+SLIP)
            if c['size']=='equal':
                eqv=cash+sum(pp['q']*pp['lc'] for pp in pos.values())
                q=int(min(eqv/c['maxpos'],cash)/(px*(1+FEE))/100)*100
            else:
                cost=px*q*(1+FEE)
                if cost>cash:q=int(cash/(px*(1+FEE))/100)*100
            if q<=0:continue
            cost=px*q*(1+FEE);cash-=cost
            pos[s]=dict(din=D[i],fill=px,q=q,cost=cost,trail=px-k*atr if atr==atr else 0,lc=px,hi=px,nb=0)
        pendB=[]
        # 2) close: trail + exits
        for s,p in pos.items():
            cc=C[i,s]
            if not cc>0:continue
            p['lc']=cc;p['nb']+=1
            if c['fam']=='bo':
                a=F['atr20'][i,s]
                if a==a:p['trail']=max(p['trail'],cc-k*a)
                ex=(cc<p['trail']-EPS*cc) or (sxa is not None and sxa[i,s]==sxa[i,s] and cc<sxa[i,s]-EPS*cc)
                if c['time_stop'] and p['nb']>=c['time_stop'] and cc<p['fill']*1.0:ex=True
                if ex:pendS.append(s)
            else:
                if c['mom_stop']:
                    a=F['atr20'][i,s]
                    if a==a:p['trail']=max(p['trail'],cc-c['mom_stop']*a)
                    if cc<p['trail']:pendS.append(s)
        # 3) regime
        rg=True
        if c['regime']=='sma200':rg=F['set'][i]>F['set200'][i]*(1+EPS)
        elif c['regime']=='breadth':rg=F['breadth'][i]>=c.get('br_min',40) if F['breadth'][i]==F['breadth'][i] else True
        elif c['regime']=='both':rg=(F['set'][i]>F['set200'][i]*(1+EPS)) and (F['breadth'][i]>=c.get('br_min',40) if F['breadth'][i]==F['breadth'][i] else True)
        elif c['regime']=='none':rg=True
        eqv=cash+sum(p['q']*p['lc'] for p in pos.values())
        if c['fam']=='bo' and rg:
            cc=C[i];ok=(cc>0)&(F['rto'][i]>=c['minTO']*(1-EPS))&(cc>hh[i]*(1+EPS))&(cc>F['s50'][i]*(1+EPS))&(F['atr20'][i]>0)
            if c['trend']:ok&=(F['s50'][i]>F['s200'][i]*(1+EPS))
            if c.get('max_atrp'):ok&=(F['atr20'][i]/np.where(cc>0,cc,np.nan)*100<=c['max_atrp'])
            cand=np.where(ok)[0]
            cand=[s for s in cand if s not in pos]
            if cand:
                if c['rank']=='c_s50':key=C[i,cand]/F['s50'][i,cand]
                elif c['rank']=='mom126':
                    j=i-126;key=F['Cf'][i,cand]/F['Cf'][j,cand] if j>=0 else np.zeros(len(cand))
                    key=np.nan_to_num(key,nan=-1)
                elif c['rank']=='rs60':
                    j=i-60;key=(F['Cf'][i,cand]/F['Cf'][j,cand])/(F['set'][i]/F['set'][j]);key=np.nan_to_num(key,nan=-1)
                order=np.lexsort((np.array(cand),-key))
                slots=c['maxpos']-len(pos)+len(pendS)
                budget=eqv*c['risk']/100
                for o in order:
                    if slots<=0:break
                    s=cand[o];a=F['atr20'][i,s]
                    q=int(budget/(k*a)/100)*100 if c['size']=='risk' else 1
                    if c['size']=='risk' and c['even']:q=min(q,int(eqv/c['maxpos']/C[i,s]/100)*100)
                    if q<=0:continue
                    pendB.append((s,q,a,C[i,s]));slots-=1
        if c['fam']=='mom':
            if not rg:
                pendS=list(set(pendS)|set(pos.keys()))
            elif i-last_reb>=c['rebal']:
                last_reb=i
                j=i-c['mom_lb']-c['mom_skip'];jj=i-c['mom_skip']
                cc=C[i];ok=(cc>0)&(F['rto'][i]>=c['minTO'])
                ts=c['trend_sma']
                if ts:ok&=(cc>F['s%d'%ts][i])
                m=F['Cf'][jj]/F['Cf'][j]-1 if j>=0 else np.full(M,np.nan)
                ok&=~np.isnan(m)
                cand=np.where(ok)[0]
                order=cand[np.lexsort((cand,-m[cand]))]
                rank={s:r for r,s in enumerate(order)}
                keep=[s for s in pos if rank.get(s,10**9)<c['maxpos']*c['buffer'] and s not in pendS]
                for s in list(pos):
                    if s not in keep and s not in pendS:pendS.append(s)
                slots=c['maxpos']-len(keep)
                for s in order:
                    if slots<=0:break
                    if s in pos:continue
                    pendB.append((s,1,F['atr20'][i,s],C[i,s]));slots-=1
        eqv=cash+sum(p['q']*p['lc'] for p in pos.values())
        eq[n]=eqv;expo+=(eqv-cash)/eqv if eqv>0 else 0
    return stats(eq,trades,D[i0:i1],cap0,expo/max(1,len(eq)),log)
def stats(eq,trades,dates,cap0,expo,log):
    yrs=len(eq)/245;end=eq[-1]
    cagr=((end/cap0)**(1/yrs)-1)*100 if yrs>0 else 0
    pk=np.maximum.accumulate(eq);dd=(eq/pk-1).min()*100
    r=np.diff(eq)/eq[:-1];sh=r.mean()/r.std()*np.sqrt(245) if r.std()>0 else 0
    pl=np.array([t[6] for t in trades]) if trades else np.array([0.0])
    wins=pl[pl>0];los=pl[pl<=0]
    pf=wins.sum()/-los.sum() if los.sum()<0 else np.inf
    ys={}
    for d,v in zip(dates,eq):ys[d//10000]=v
    yr=[];prev=cap0
    for y in sorted(ys):yr.append((y,(ys[y]/prev-1)*100));prev=ys[y]
    out=dict(cagr=cagr,mdd=dd,mar=cagr/abs(dd) if dd<0 else np.inf,sharpe=sh,n=len(trades),wr=(pl>0).mean()*100,pf=pf,expo=expo*100,
             worst_y=min(v for _,v in yr),end=end)
    if log:out['eq']=eq;out['trades']=trades;out['years']=yr;out['dates']=dates
    return out
