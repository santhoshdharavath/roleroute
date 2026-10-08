from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    role_goal_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=70)

    modules = relationship("Module", back_populates="role", order_by="Module.order_index")
    internships = relationship("Internship", back_populates="role")


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    role = relationship("Role", back_populates="modules")
    topics = relationship("Topic", back_populates="module", order_by="Topic.order_index")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skill_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=45)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    module = relationship("Module", back_populates="topics")
