import json,hashlib
def fingerprint(study,rows,columns,cells,axes):
 payload={'study':{k:study[k] for k in ('id','name','filename','description')},'rows':sorted(rows,key=lambda x:x['code']),'columns':sorted(columns,key=lambda x:x['code']),'cells':sorted([{'row_id':x['row_id'],'column_id':x['column_id'],'count':x['count']} for x in cells],key=lambda x:(x['row_id'],x['column_id'])),'axes':axes,'algorithm':'ca-principal-svd-chi-square-v1','singular_zero_tol':1e-12}
 return hashlib.sha256(json.dumps(payload,sort_keys=True,allow_nan=False,separators=(',',':')).encode()).hexdigest()
