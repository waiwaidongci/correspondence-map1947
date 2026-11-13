from pydantic import BaseModel,Field
class RunInput(BaseModel):
 study_id:int=Field(gt=0)
 name:str=Field(min_length=1,max_length=100)
 axes:int=Field(ge=1,le=2,strict=True)
