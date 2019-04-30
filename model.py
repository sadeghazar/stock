from sqlalchemy import Column, DateTime, Integer, LargeBinary, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class TblHistory(Base):
    __tablename__ = 'tbl_history'

    id = Column(Integer, unique=True)
    namad_name = Column(Text, nullable=False, unique=True)
    namad_id = Column(Integer, nullable=False, unique=True, primary_key=True)
    history = Column(Text)
    last_update = Column(DateTime)
