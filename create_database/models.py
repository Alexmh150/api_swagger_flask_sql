from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Define the Trip table
class Trip(Base):
    __tablename__ = 'trip'

    # Declare attributes
    trip_id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('dim_region.region_id'))
    origin_coord = Column(String)
    destination_coord = Column(String)
    datetime = Column(DateTime)
    datasource_id = Column(Integer, ForeignKey('dim_datasource.datasource_id'))

    region = relationship("DimRegion", back_populates="trips")
    datasource = relationship("DimDatasource", back_populates="trips")


# Define the DimDate table
class DimDate(Base):
    __tablename__ = 'dim_date'
    
    # Declare attributes
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    day_name = Column(String)
    week_number = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)

# Define the DimRegion table
class DimRegion(Base):
    __tablename__ = 'dim_region'

    # Declare attributes
    region_id = Column(Integer, primary_key=True)
    region_name = Column(String, unique=True)
    region_population = Column(Integer)

    trips = relationship("Trip", back_populates="region")

# Define the DimDatasource table
class DimDatasource(Base):
    __tablename__ = 'dim_datasource'

    # Declare attributes
    datasource_id = Column(Integer, primary_key=True)
    datasource_name = Column(String, unique=True)
    datasource_url = Column(String)

    trips = relationship("Trip", back_populates="datasource")

# Create dabase based on the model
def create_database(database_name):
    engine = create_engine(f'sqlite:///{database_name}')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    return engine