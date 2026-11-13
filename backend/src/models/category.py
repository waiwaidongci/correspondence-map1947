from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,ForeignKey,UniqueConstraint,Integer
from src.config.database import Base
class Category(Base):
 __tablename__='categories'
 __table_args__=(UniqueConstraint('study_id','axis','code'),)
 id:Mapped[int]=mapped_column(primary_key=True)
 study_id:Mapped[int]=mapped_column(ForeignKey('contingency_studies.id'))
 axis:Mapped[str]=mapped_column(String(10))
 code:Mapped[str]=mapped_column(String(30))
 label:Mapped[str]=mapped_column(String(80))
 position:Mapped[int]=mapped_column(Integer)
