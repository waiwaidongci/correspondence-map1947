from pydantic import BaseModel,Field
class CellPatch(BaseModel):
 count:int=Field(ge=0,le=1000000,strict=True)
class CategoryPatch(BaseModel):
 label:str=Field(min_length=1,max_length=80)
