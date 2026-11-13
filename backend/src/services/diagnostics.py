import numpy as np
from scipy.stats import chi2

def independence_diagnostics(table):
 X=np.asarray(table,dtype=float);n=float(X.sum());r=X.sum(axis=1)/n;c=X.sum(axis=0)/n
 expected=n*np.outer(r,c);delta=X-expected;pearson=delta/np.sqrt(expected)
 adjusted=delta/np.sqrt(expected*(1-r[:,None])*(1-c[None,:]))
 statistic=float(np.sum(pearson**2));df=(X.shape[0]-1)*(X.shape[1]-1);fraction=float(np.mean(expected<5));under1=bool(np.any(expected<1));reliable=not under1 and fraction<=.2
 return {'chi_square':statistic,'df':int(df),'p_value':float(chi2.sf(statistic,df)),'expected':expected.tolist(),'pearson_residuals':pearson.tolist(),'adjusted_standardized_residuals':adjusted.tolist(),'expected_min':float(expected.min()),'fraction_expected_under5':fraction,'any_expected_under1':under1,'asymptotic_reliable':reliable,'p_label':'渐近p可按假设谨慎读取' if reliable else '稀疏表：渐近p不可靠，不作强显著结论','residual_caveat':'Adjusted residuals are descriptive diagnostics without multiple-cell testing correction.'}
