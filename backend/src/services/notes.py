from sqlalchemy import select
from fastapi import HTTPException
from src.models import InterpretationNote,CorrespondenceRun
from src.constants.enums import NoteStatus,RunStatus
from src.utils.serialize import row
from .audit import record
def list_notes(db):return [row(x) for x in db.scalars(select(InterpretationNote).order_by(InterpretationNote.id.desc()))]
def create_note(db,data,user):
 run=db.get(CorrespondenceRun,data.run_id)
 if not run or run.status!=RunStatus.SUCCEEDED:raise HTTPException(422,'请选择成功分析')
 ids={p['id'] for p in run.result['row_points']+run.result['column_points']}
 if len(set(data.category_ids))!=len(data.category_ids) or not set(data.category_ids)<=ids:raise HTTPException(422,'解释类别须来自本运行有效行列且不重复')
 obj=InterpretationNote(**data.model_dump(),creator_id=user.id);db.add(obj);db.commit();record(db,user.email,'interpretation.created',{'note_id':obj.id});return row(obj)
def approve_note(db,id,data,user):
 obj=db.get(InterpretationNote,id)
 if not obj:raise HTTPException(404,'解释记录不存在')
 if obj.status!=NoteStatus.DRAFT:raise HTTPException(409,'仅草案可审阅')
 obj.status=data.status;obj.review_note=data.review_note;db.commit();record(db,user.email,'interpretation.reviewed',{'note_id':id,'status':obj.status});return row(obj)
