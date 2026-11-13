from fastapi import HTTPException
from src.models import InterpretationNote,CorrespondenceRun
from src.constants.enums import NoteStatus
from src.utils.csv_export import csv_response
def export_note(db,id):
 note=db.get(InterpretationNote,id)
 if not note:raise HTTPException(404,'解释记录不存在')
 if note.status!=NoteStatus.APPROVED:raise HTTPException(403,'仅获批解释可导出')
 run=db.get(CorrespondenceRun,note.run_id);rows=[]
 for p in run.result['row_points']+run.result['column_points']:
  if p['id'] in note.category_ids:
   shown=run.result['displayed_axes'];xy=[p['coordinates'][k] if k<shown else None for k in range(2)];rows.append([note.name,p['axis'],p['code'],p['label'],p['mass'],*xy,p['display_quality'],run.result['retained_inertia'],run.result['diagnostics']['p_value'],run.result['diagnostics']['asymptotic_reliable'],note.interpretation,note.next_step,note.review_note,'行列跨集距离不可直接解释；稀疏表渐近p不可靠'])
 return csv_response(f'interpretation-{id}.csv',rows,['解释','点集','code','类别','质量mass','主坐标1','主坐标2','显示cos2','保留惯量','渐近p','期望计数条件可用','人工解释','下一步','审阅说明','边界'])
