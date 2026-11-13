from sqlalchemy import select
from fastapi import HTTPException
from src.models import CorrespondenceRun,ContingencyStudy
from src.constants.enums import RunStatus
from src.utils.serialize import row
from .audit import record
def list_runs(db):return [row(x) for x in db.scalars(select(CorrespondenceRun).order_by(CorrespondenceRun.id.desc()))]
def get_run(db,id):
 obj=db.get(CorrespondenceRun,id)
 if not obj:raise HTTPException(404,'对应分析不存在')
 return obj
def create_run(db,data,user):
 if not db.get(ContingencyStudy,data.study_id):raise HTTPException(404,'列联研究不存在')
 obj=CorrespondenceRun(**data.model_dump(),creator_id=user.id);db.add(obj);db.commit()
 from src.worker import analyze_run
 try:analyze_run.delay(obj.id)
 except Exception:obj.status=RunStatus.FAILED;obj.error='队列不可用';db.commit();raise HTTPException(503,obj.error)
 record(db,user.email,'ca.queued',{'run_id':obj.id});return row(obj)
