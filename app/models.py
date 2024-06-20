from sqlalchemy import Column, String, DateTime, Boolean, Integer, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Content(Base):
    __tablename__ = 'content'

    id = Column(String, primary_key=True)
    slug = Column(String, unique=True)
    created_at = Column(DateTime)
    description = Column(String)
    image_id = Column(String)
    title = Column(String)
    flagged = Column(Boolean)
    generating = Column(Boolean)
    view_count = Column(Integer)
    hot_score = Column(Integer)


class ImageData(Base):
    __tablename__ = 'image_data'

    id = Column(String, primary_key=True)
    jpeg_data = Column(LargeBinary)
