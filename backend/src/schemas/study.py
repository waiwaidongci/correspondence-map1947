from pydantic import BaseModel,Field,model_validator,StrictInt
class CategoryInput(BaseModel):
 code:str=Field(min_length=1,max_length=30)
 label:str=Field(min_length=1,max_length=80)
class StudyInput(BaseModel):
 name:str=Field(min_length=1,max_length=100)
 filename:str=Field(min_length=1,max_length=160)
 description:str=Field(default='',max_length=500)
 rows:list[CategoryInput]=Field(min_length=2,max_length=12)
 columns:list[CategoryInput]=Field(min_length=2,max_length=12)
 counts:list[list[StrictInt]]
 @model_validator(mode='after')
 def validate_table(self):
  if len({x.code for x in self.rows})!=len(self.rows) or len({x.code for x in self.columns})!=len(self.columns):raise ValueError('同一轴类别code不得重复')
  if len(self.counts)!=len(self.rows) or any(len(x)!=len(self.columns) for x in self.counts):raise ValueError('计数矩阵维度与类别不匹配')
  if any(type(c)!=int or not 0<=c<=1000000 for row in self.counts for c in row):raise ValueError('计数须0..1000000整数')
  if sum(sum(row) for row in self.counts)==0:raise ValueError('总计数须大于0')
  return self
