from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Create the base class of the object
Base = declarative_base()

# Define DataPoint Object
class DataPoint(Base):
    # Table Name
    __tablename__ = 'data_point'
    # Structure of the table
    id = Column(Integer)
    dormitoryName = Column(String(8))
    time = Column(DateTime, primary_key=True)
    hour = Column(Integer)
    phone = Column(String(8))
    model = Column(String(8))
    vTotal = Column(Float)
    price = Column(Float)
    iTotal = Column(Float)
    freeEnd = Column(Float)
    cosTotal = Column(Float)
    pTotal = Column(Float)
    surplus = Column(Float)
    totalActiveDisp = Column(Float)