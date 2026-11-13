import numpy as np
from .diagnostics import independence_diagnostics
TOL=1e-12

def correspondence(table,row_meta,column_meta,axes=2):
 X=np.asarray(table)
 if X.ndim!=2 or min(X.shape)<2 or max(X.shape)>12 or not np.issubdtype(X.dtype,np.number) or not np.isfinite(X).all() or (X<0).any() or not np.equal(X,np.floor(X)).all():raise ValueError('列联表须2..12行列的有限非负整数矩阵')
 if len(row_meta)!=X.shape[0] or len(column_meta)!=X.shape[1]:raise ValueError('类别维度不匹配')
 if len({x['id'] for x in row_meta})!=len(row_meta) or len({x['id'] for x in column_meta})!=len(column_meta):raise ValueError('轴内类别重复')
 if not isinstance(axes,int) or not 1<=axes<=2:raise ValueError('显示轴数只能1或2')
 X=X.astype(float);n=float(X.sum())
 if not 0<n<=144000000:raise ValueError('总计数为零或超研究配额')
 row_keep=X.sum(axis=1)>0;col_keep=X.sum(axis=0)>0
 dropped_rows=[row_meta[i] for i in range(len(row_meta)) if not row_keep[i]];dropped_columns=[column_meta[j] for j in range(len(column_meta)) if not col_keep[j]]
 A=X[np.ix_(row_keep,col_keep)];rows=[row_meta[i] for i in range(len(row_meta)) if row_keep[i]];cols=[column_meta[j] for j in range(len(column_meta)) if col_keep[j]]
 if min(A.shape)<2:raise ValueError('剔除零边际后至少需要2个有效行和列')
 P=A/n;r=P.sum(axis=1);c=P.sum(axis=0);S=(P-np.outer(r,c))/np.sqrt(np.outer(r,c))
 U,s,Vt=np.linalg.svd(S,full_matrices=False)
 for k in range(len(s)):
  pivot=int(np.argmax(np.abs(U[:,k])))
  if U[pivot,k]<0:U[:,k]*=-1;Vt[k,:]*=-1
 inertia=float(np.sum(S*S));rank=min(int(np.sum(s>TOL)),A.shape[0]-1,A.shape[1]-1);direction=inertia>TOL*TOL and rank>0
 if not direction:rank=0
 active_s=s[:rank];lambdas=active_s**2;shown=min(axes,rank)
 F=(U[:,:rank]*active_s)/np.sqrt(r[:,None]) if rank else np.empty((len(r),0));G=(Vt[:rank,:].T*active_s)/np.sqrt(c[:,None]) if rank else np.empty((len(c),0))
 def points(meta,mass,coordinates,axis):
  out=[]
  for i,m in enumerate(meta):
   values=coordinates[i];distance=float(np.sum(values*values));contribution=(mass[i]*values*values/lambdas).tolist() if rank else []
   cos2=(values*values/distance).tolist() if distance>TOL*TOL else [None]*rank
   out.append({**m,'axis':axis,'mass':float(mass[i]),'coordinates':values.tolist(),'contributions':contribution,'cos2':cos2,'display_quality':float(np.clip(sum(cos2[:shown]),0.,1.)) if distance>TOL*TOL else None,'chi_square_distance_squared':distance,'centroid':distance<=TOL*TOL})
  return out
 degeneracies=[]
 for k in range(rank-1):
  if abs(active_s[k]-active_s[k+1])<=1e-8*max(active_s[k],active_s[k+1]):degeneracies.append([k+1,k+2])
 diagnostic=independence_diagnostics(A)
 return {'n':int(n),'table':A.astype(int).tolist(),'row_categories':rows,'column_categories':cols,'dropped_rows':dropped_rows,'dropped_columns':dropped_columns,'row_masses':r.tolist(),'column_masses':c.tolist(),'standardized_residual_matrix':S.tolist(),'svd':{'U':U.tolist(),'singular_values':s.tolist(),'Vt':Vt.tolist()},'total_inertia':inertia,'rank':rank,'direction_available':direction,'displayed_axes':shown,'axes':[{'axis':i+1,'singular_value':float(v),'inertia':float(v*v),'share':float(v*v/inertia)} for i,v in enumerate(active_s)],'retained_inertia':float(np.clip(np.sum(lambdas[:shown])/inertia,0.,1.)) if direction else None,'row_points':points(rows,r,F,'row'),'column_points':points(cols,c,G,'column'),'degenerate_axes':degeneracies,'diagnostics':diagnostic,'zero_tolerance':TOL,'coordinate_caveat':'Both sets are principal coordinates: within-row and within-column chi-square geometry; cross row-column distances are not directly interpretable. 2D omits unretained inertia; low cos2 points are poorly represented. Repeated singular values have nonunique axis rotations even after sign fixing.','zero_message':None if direction else '总惯量在数值零范围：没有可解释方向，不绘制伪造坐标轴。'}
