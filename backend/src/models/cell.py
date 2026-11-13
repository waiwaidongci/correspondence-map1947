from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import ForeignKey,UniqueConstraint,CheckConstraint
from src.config.database import Base
class CellCount(Base):
 __tablename__='cell_counts'
 __table_args__=(UniqueConstraint('row_id','column_id'),CheckConstraint('count>=0',name='count_nonnegative'))
 id:Mapped[int]=mapped_column(primary_key=True)
 study_id:Mapped[int]=mapped_column(ForeignKey('contingency_studies.id'))
 row_id:Mapped[int]=mapped_column(ForeignKey('categories.id'))
 column_id:Mapped[int]=mapped_column(ForeignKey('categories.id'))
 count:Mapped[int]=mapped_column()
