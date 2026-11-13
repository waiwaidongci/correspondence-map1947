from sqlalchemy import select
from fastapi import HTTPException
from src.models import ContingencyStudy,Category,CellCount
from src.utils.serialize import row
from .audit import record

def studies(db):
 out=[]
 for s in db.scalars(select(ContingencyStudy).order_by(ContingencyStudy.id)):
  cats=list(db.scalars(select(Category).where(Category.study_id==s.id)));cs=list(db.scalars(select(CellCount).where(CellCount.study_id==s.id)))
  out.append(dict(row(s),rows=sum(x.axis=='row' for x in cats),columns=sum(x.axis=='column' for x in cats),total=sum(x.count for x in cs)))
 return out
def categories(db):return [row(x) for x in db.scalars(select(Category).order_by(Category.study_id,Category.axis,Category.position))]
def cells(db):return [row(x) for x in db.scalars(select(CellCount).order_by(CellCount.id))]
def table_data(db,id):
 study=db.get(ContingencyStudy,id)
 if not study:raise HTTPException(404,'列联研究不存在')
 rows=[row(x) for x in db.scalars(select(Category).where(Category.study_id==id,Category.axis=='row').order_by(Category.code))];cols=[row(x) for x in db.scalars(select(Category).where(Category.study_id==id,Category.axis=='column').order_by(Category.code))];cs=[row(x) for x in db.scalars(select(CellCount).where(CellCount.study_id==id))];lookup={(x['row_id'],x['column_id']):x['count'] for x in cs}
 return row(study),rows,cols,cs,[[lookup.get((r['id'],c['id']),0) for c in cols] for r in rows]
def create_study(db,data,user):
 if db.scalar(select(ContingencyStudy).where(ContingencyStudy.name==data.name)):raise HTTPException(409,'研究名称已存在')
 obj=ContingencyStudy(**data.model_dump(exclude={'rows','columns','counts'}));db.add(obj);db.flush();axes=[]
 for axis,items in [('row',data.rows),('column',data.columns)]:
  group=[]
  for i,item in enumerate(items):
   cat=Category(study_id=obj.id,axis=axis,position=i,**item.model_dump());db.add(cat);db.flush();group.append(cat)
  axes.append(group)
 for i,r in enumerate(axes[0]):
  for j,c in enumerate(axes[1]):db.add(CellCount(study_id=obj.id,row_id=r.id,column_id=c.id,count=data.counts[i][j]))
 db.commit();record(db,user.email,'study.import',{'study_id':obj.id});return row(obj)
def patch_category(db,id,data,user):
 obj=db.get(Category,id)
 if not obj:raise HTTPException(404,'类别不存在')
 obj.label=data.label;db.commit();record(db,user.email,'category.label',{'category_id':id});return row(obj)
def patch_cell(db,id,data,user):
 obj=db.get(CellCount,id)
 if not obj:raise HTTPException(404,'单元格不存在')
 obj.count=data.count;db.commit();record(db,user.email,'cell.count',{'cell_id':id,'count':obj.count});return row(obj)
