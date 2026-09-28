import pandas as pd,numpy as np,glob
dfs=[pd.read_csv(f,names=['t','d','o','h','l','c','v'],skiprows=1) for f in sorted(glob.glob('eod-*.csv'))]
df=pd.concat(dfs,ignore_index=True)
# add latest days from 2026 daily data already covered? check last date
print(df.shape, df.d.min(), df.d.max(), df.t.nunique())
df=df.drop_duplicates(['t','d'],keep='last')
dates=np.sort(df.d.unique());print('dates',len(dates))
setd=df[df.t=='SET'].set_index('d').sort_index()
print('SET days',len(setd),'missing SET on',len(set(dates)-set(setd.index)))
cnt=df.groupby('d').size();print(cnt.describe());print('low-count days',cnt[cnt<cnt.rolling(21,center=True,min_periods=5).median()*0.6].head(20))
# per-year stock counts
df['y']=df.d//10000;print(df.groupby('y').t.nunique())
df.to_parquet('panel.parquet') if False else df.to_pickle('panel.pkl')
