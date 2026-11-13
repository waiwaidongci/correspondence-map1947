from pydantic import BaseModel,Field
from typing import Literal
class NoteInput(BaseModel):
 run_id:int=Field(gt=0)
 name:str=Field(min_length=1,max_length=100)
 category_ids:list[int]=Field(min_length=1,max_length=24)
 interpretation:str=Field(min_length=1,max_length=700)
 next_step:str=Field(min_length=1,max_length=500)
class ApprovalInput(BaseModel):
 status:Literal['approved','rejected']
 review_note:str=Field(min_length=1,max_length=500)
