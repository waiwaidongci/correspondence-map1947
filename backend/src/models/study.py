from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String
from src.config.database import Base
class ContingencyStudy(Base):
 __tablename__='contingency_studies'
 id:Mapped[int]=mapped_column(primary_key=True)
 name:Mapped[str]=mapped_column(String(100),unique=True)
 filename:Mapped[str]=mapped_column(String(160))
 description:Mapped[str]=mapped_column(String(500),default='')
