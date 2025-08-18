from sqlalchemy.orm import declarative_base

from sqlalchemy import (
    Column, ForeignKey, Integer, String, DateTime,
    Date, Text, Float, Time, types, Computed, Index, Boolean,
    JSON, BLOB,
)
from sqlalchemy.dialects.postgresql import TSVECTOR, JSONB, ARRAY
from pgvector.sqlalchemy import Vector

class TSVector(types.TypeDecorator):
    """
    generic class for tsvector type for full text search
    """
    impl = TSVECTOR

Base = declarative_base()

class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class Themes(Base):
    __tablename__ = 'themes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey(Project.id), nullable=False)
    theme_id = Column(String, nullable=False)
    theme_name = Column(String, nullable=False)
    theme_description = Column(Text, nullable=True)

class Topics(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey(Project.id), nullable=False)
    topic_id = Column(String, nullable=False)
    topic_name = Column(String, nullable=False)
    topic_description = Column(Text, nullable=True)
    theme_id = Column(String, ForeignKey(Themes.theme_id), nullable=False)

class Resercher(Base):
    __tablename__ = 'researcher'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id=Column(Integer, ForeignKey(Project.id), nullable=False)
    name=Column(String, nullable=False)
    description = Column(Text, nullable=True)
    model_name = Column(String, nullable=False)
    cache_dir = Column(String, nullable=True)
    url=Column(String, nullable=True)
    prompt = Column(Text, nullable=False)
    is_manager=Column(Boolean, nullable=False)
    papers=Column(JSON, nullable=True) #just paper ids, I can also store the paper ids that are not the db ids but pubmed ids
    themes=Column(JSON, nullable=True) # same as above
    topics=Column(JSON, nullable=True) # same as above, ideally this should be a collection of papers but we are not going to
    #store millions of things in here

class Papers(Base):
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id=Column(Integer, ForeignKey(Project.id), nullable=False)
    source=Column(String, nullable=False) #pubmed or arxiv
    source_id=Column(String, nullable=False)
    title=Column(String, nullable=False)
    doi=Column(String, nullable=True)
    pdf_url = Column(String, nullable=True)
    pdf_path=Column(String, nullable=True)
    abstract=Column(Text, nullable=True)
    abstract_embeddings=Column(Vector(1024))
    abstract_ts_vector=Column(TSVector, Computed("to_tsvector('english', abstract)",
                                                 pesisted=True))
    __table_args__ = (Index('ix_abstract_ts_vector',
                            abstract_ts_vector, postgresql_using='gin'),)

class Figures(Base):
    __tablename__ = 'figures'
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id=Column(Integer, ForeignKey(Papers.id), nullable=False)
    image_blob=Column(BLOB, nullable=False)
    caption=Column(Text, nullable=True)
    ai_caption=Column(Text, nullable=False)
    image_embeddings=Column(Vector(1024))
    caption_embeddings=Column(Vector(1024))
    ai_caption_embeddings=Column(Vector(1024))
    caption_ts_vector=Column(TSVector, Computed("to_tsvector('english', caption)",))
    ai_caption_ts_vector=Column(TSVector, Computed("to_tsvector('english', ai_caption)",))

    __table_args__ = (Index('ix_caption_ts_vector',
                            caption_ts_vector, postgresql_using='gin'),
                      Index('ix_ai_caption_ts_vector',
                            ai_caption_ts_vector, postgresql_using='gin'),
                      )

class Tables(Base):
    __tablename__ = 'tables'
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey(Papers.id), nullable=False)
    image_blob = Column(BLOB, nullable=False)
    caption = Column(Text, nullable=True)
    ai_caption = Column(Text, nullable=False)
    image_embeddings = Column(Vector(1024))
    caption_embeddings = Column(Vector(1024))
    ai_caption_embeddings = Column(Vector(1024))
    caption_ts_vector = Column(TSVector, Computed("to_tsvector('english', caption)", ))
    ai_caption_ts_vector = Column(TSVector, Computed("to_tsvector('english', ai_caption)", ))

    __table_args__ = (Index('ix_caption_ts_vector',
                            caption_ts_vector, postgresql_using='gin'),
                      Index('ix_ai_caption_ts_vector',
                            ai_caption_ts_vector, postgresql_using='gin'),
                      )

class BodyText(Base):
    __tablename__ = 'body_text'
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey(Papers.id), nullable=False)
    chunk_id=Column(Integer, nullable=False)
    embedding_mode=Column(String, nullable=False)
    chunk_text=Column(Text, nullable=False)
    chunk_embeddings=Column(Vector(1024))
    chunk_ts_vector = Column(TSVector, Computed("to_tsvector('english', chunk_text)", ))
    __table_args__ = (Index('ix_chunk_ts_vector',
                            chunk_ts_vector, postgresql_using='gin'),)