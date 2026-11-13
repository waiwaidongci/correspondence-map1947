import json
from pathlib import Path
from celery import Celery
from src.config.database import SessionLocal
from src.config.settings import REDIS_URL,ARTIFACT_DIR
from src.models import CorrespondenceRun
from src.services.catalog import table_data
from src.services.ca import correspondence
from src.services.fingerprint import fingerprint
from src.services.audit import record
app=Celery('correspondence_map',broker=REDIS_URL,backend=REDIS_URL)
app.conf.update(task_track_started=True,worker_prefetch_multiplier=1,task_acks_late=True)
@app.task(name='ca.analyze',soft_time_limit=120,time_limit=150)
def analyze_run(id):
 with SessionLocal() as db:
  run=db.get(CorrespondenceRun,id)
  if not run or run.status=='succeeded':return
  run.status='running';db.commit()
  try:
   study,rows,cols,cells,table=table_data(db,run.study_id);result=correspondence(table,rows,cols,run.axes);result['fingerprint']=fingerprint(study,rows,cols,cells,run.axes)
   Path(ARTIFACT_DIR).mkdir(parents=True,exist_ok=True);Path(ARTIFACT_DIR,f'ca-{id}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False));run.result=result;run.status='succeeded';run.error=None;db.commit();record(db,'worker','ca.succeeded',{'run_id':id,'inertia':result['total_inertia']})
  except Exception as e:
   db.rollback();run=db.get(CorrespondenceRun,id);run.status='failed';run.error=str(e)[:1000];db.commit();record(db,'worker','ca.failed',{'run_id':id,'error':run.error})
