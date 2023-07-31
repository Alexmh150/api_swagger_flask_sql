from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Define the Trip table
class Trip(Base):
    __tablename__ = 'trip'

    trip_id = Column(Integer, primary_key=True)
    region_name = Column(String, ForeignKey('dim_region.region_name'))
    origin_coord = Column(String)
    destination_coord = Column(String)
    datetime = Column(DateTime)
    datasource = Column(String)

    region = relationship("DimRegion", back_populates="trips")

# Define the DimDate table
class DimDate(Base):
    __tablename__ = 'dim_date'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    day_name = Column(String)
    week_number = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)

# Define the DimRegion table
class DimRegion(Base):
    __tablename__ = 'dim_region'

    region_id = Column(Integer, primary_key=True)
    region_name = Column(String, unique=True)
    region_population = Column(Integer)

    trips = relationship("Trip", back_populates="region")

def create_database(database_name):
    engine = create_engine(f'sqlite:///{database_name}')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    return engine