import json
from sqlalchemy import select,func
from src.config.database import Base,engine,SessionLocal
from src.models import *
from src.utils.security import hash_password
from src.services.catalog import table_data
from src.services.ca import correspondence
from src.services.fingerprint import fingerprint

def seed():
 Base.metadata.create_all(engine)
 with SessionLocal() as db:
  for role,name in [('admin','许禾 · 展陈研究负责人'),('analyst','陈陌 · 偏好结构研究员'),('viewer','林叙 · 导览观察员')]:
   email=role+'@hemo.demo'
   if not db.scalar(select(User).where(User.email==email)):db.add(User(email=email,name=name,role=role,password_hash=hash_password('Hemo2026!')))
  db.commit()
  scenarios=[('秋季导览类别研究',['家庭同行','学习小组','独立参访','策展同业'],['故事导览','材料触摸','开放讨论','地图路径','静观笔记'],[[120,38,18,30,19],[27,112,36,27,23],[24,33,120,27,21],[45,42,27,75,36]]),('接近独立的对照折页',['A类参访','B类参访','C类参访','D类参访'],['文字','触摸','讨论','路径','笔记'],[[46,44,45,45,45],[45,46,44,45,45],[45,45,46,44,45],[44,45,45,46,45]]),('稀疏试采与零边际',['交流团','工坊团','研究团','零样本类','随访团'],['文字卡','互动台','声景线','零样本列'],[[2,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,0],[1,0,1,0]])]
  for index,(name,rowlabels,collabels,table) in enumerate(scenarios,1):
   if db.scalar(select(ContingencyStudy).where(ContingencyStudy.name==name)):continue
   study=ContingencyStudy(name=name,filename=f'hm-guide-contingency-{index}.csv',description='机构级匿名类别计数；合成展陈工作流，不作人群因果推断。');db.add(study);db.flush();groups=[]
   for axis,labels in [('row',rowlabels),('column',collabels)]:
    group=[]
    for i,label in enumerate(labels):
     category=Category(study_id=study.id,axis=axis,code=('R' if axis=='row' else 'C')+str(i+1),label=label,position=i);db.add(category);db.flush();group.append(category)
    groups.append(group)
   for i,r in enumerate(groups[0]):
    for j,c in enumerate(groups[1]):db.add(CellCount(study_id=study.id,row_id=r.id,column_id=c.id,count=table[i][j]))
   db.commit()
  if not db.scalar(select(CorrespondenceRun).where(CorrespondenceRun.name=='秋季导览结构初稿')):
   study=db.scalar(select(ContingencyStudy).where(ContingencyStudy.name==scenarios[0][0]));meta,rows,cols,cells,table=table_data(db,study.id);result=correspondence(table,rows,cols,2);result['fingerprint']=fingerprint(meta,rows,cols,cells,2);admin=db.scalar(select(User).where(User.role=='admin'));run=CorrespondenceRun(study_id=study.id,name='秋季导览结构初稿',axes=2,status='succeeded',result=result,creator_id=admin.id);db.add(run);db.flush();db.add(InterpretationNote(run_id=run.id,name='行轮廓结构与导览小样草案',category_ids=[p['id'] for p in result['row_points'][:2]],interpretation='先读取同行轮廓与显示质量，不把行列两点间接近当成直接偏好距离。',next_step='保留完整惯量和期望计数诊断，再做独立导览小样试验。',creator_id=admin.id));db.add(AuditLog(actor='seed',action='demo.created',detail={'total_counts':1806,'tables':3}));db.commit()
  counts={t.__tablename__:db.scalar(select(func.count()).select_from(t)) for t in [User,ContingencyStudy,Category,CellCount,CorrespondenceRun,InterpretationNote]};print(json.dumps(counts));return counts
if __name__=='__main__':seed()
