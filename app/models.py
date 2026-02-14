from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String, primary_key=True, index=True)
    store_name = Column(String, nullable=False)
    area_code = Column(String, nullable=False)

    visits = relationship("Visit", back_populates="store")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="ONGOING")
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    visits = relationship("Visit", back_populates="job")
    
class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    store_id = Column(String, ForeignKey("stores.store_id"))
    visit_time = Column(DateTime, nullable=False)

    job = relationship("Job", back_populates="visits")
    store = relationship("Store", back_populates="visits")
    images = relationship("Image", back_populates="visit")
    
class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"))
    image_url = Column(String, nullable=False)

    height = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    perimeter = Column(Float, nullable=True)

    visit = relationship("Visit", back_populates="images")