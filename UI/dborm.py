from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


# This file should be run once every time the database is modified
# DO NOT RUN it after storing data, will lose the data otherwise

Base = declarative_base()

class Upload(Base):
    __tablename__ = 'upload'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(1000), nullable=True)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///srflow.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)