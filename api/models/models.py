"""
Database model definitions
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from core.database import Base


class Content(Base):
    """
    Content model
    Manage collected articles, papers, news, etc.
    """

    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, comment="Title")
    summary = Column(Text, comment="Summary")
    content = Column(Text, comment="Full text")
    original_url = Column(String(1000), unique=True, comment="Original URL")
    source = Column(String(100), nullable=False, comment="Source")
    category = Column(String(50), comment="Category")
    tags = Column(ARRAY(Text), comment="Tags")
    published_at = Column(DateTime, comment="Published at")
    created_at = Column(DateTime, server_default=func.now(), comment="Created at")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="Updated at")
    embedding = Column(Vector(384), comment="Vector embedding")
    content_metadata = Column(JSONB, comment="Metadata")
    view_count = Column(Integer, default=0, comment="View count")
    like_count = Column(Integer, default=0, comment="Like count")
    is_processed = Column(Boolean, default=False, comment="Processed flag")

    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title[:30]}...', source='{self.source}')>"


class User(Base):
    """
    User model
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, comment="Email address")
    password_hash = Column(String(255), nullable=False, comment="Password hash")
    preferences = Column(JSONB, default={}, comment="User preferences")
    is_active = Column(Boolean, default=True, comment="Active flag")
    created_at = Column(DateTime, server_default=func.now(), comment="Created at")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="Updated at")
    last_login_at = Column(DateTime, comment="Last login at")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class UserAction(Base):
    """
    User action model
    Used as training data for recommendation system
    """

    __tablename__ = "user_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="User ID")
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False, comment="Content ID")
    action_type = Column(String(20), nullable=False, comment="Action type(view, like, bookmark, share)")
    created_at = Column(DateTime, server_default=func.now(), comment="Created at")
    action_metadata = Column(JSONB, comment="Metadata")

    def __repr__(self):
        return f"<UserAction(id={self.id}, user_id={self.user_id}, content_id={self.content_id}, type='{self.action_type}')>"


class APIKey(Base):
    """
    API key model
    """

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="User ID")
    name = Column(String(100), nullable=False, comment="Key name")
    key_hash = Column(String(255), unique=True, nullable=False, comment="Key hash")
    key_prefix = Column(String(20), comment="Key prefix")
    rate_limit = Column(Integer, default=100, comment="Rate limit")
    is_active = Column(Boolean, default=True, comment="Active flag")
    last_used_at = Column(DateTime, comment="Last used at")
    created_at = Column(DateTime, server_default=func.now(), comment="Created at")

    def __repr__(self):
        return f"<APIKey(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class Entity(Base):
    """
    Entity model
    Knowledge graph node
    """

    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, comment="Entity name")
    type = Column(String(50), nullable=False, comment="Type(model, company, person, technology)")
    description = Column(Text, comment="Description")
    aliases = Column(ARRAY(Text), comment="Aliases")
    entity_metadata = Column(JSONB, comment="Metadata")
    created_at = Column(DateTime, server_default=func.now(), comment="Created at")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="Updated at")

    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}', type='{self.type}')>"


class EntityRelation(Base):
    """
    Entity relation model
    Knowledge graph edge
    """

    __tablename__ = "entity_relations"

    id = Column(Integer, primary_key=True, index=True)
    source_entity_id = Column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, comment="Source entity ID"
    )
    target_entity_id = Column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, comment="Target entity ID"
    )
    relation_type = Column(String(100), nullable=False, comment="Relation type")
    weight = Column(Float, default=1.0, comment="Weight")
    evidence = Column(Text, comment="Evidence")
    created_at = Column(DateTime, server_default=func.now(), comment="Created at")

    def __repr__(self):
        return f"<EntityRelation(id={self.id}, type='{self.relation_type}')>"
