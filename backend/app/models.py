import datetime
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="citizen", nullable=False)  # 'citizen' or 'admin'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    reports = relationship("LeakReport", back_populates="reporter", cascade="all, delete-orphan")
    verifications = relationship("Verification", back_populates="user", cascade="all, delete-orphan")
    status_changes = relationship("StatusHistory", back_populates="changer", cascade="all, delete-orphan")

class LeakReport(Base):
    __tablename__ = "leak_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, default="Reported", nullable=False)  # 'Reported', 'In Progress', 'Resolved'
    verification_count = Column(Integer, default=0, nullable=False)
    severity = Column(String, default="Medium", nullable=False)  # 'Low', 'Medium', 'High' (estimated by AI Engine)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    reporter = relationship("User", back_populates="reports")
    verifications = relationship("Verification", back_populates="report", cascade="all, delete-orphan")
    status_history = relationship("StatusHistory", back_populates="report", cascade="all, delete-orphan")

class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("leak_reports.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    verified_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    report = relationship("LeakReport", back_populates="verifications")
    user = relationship("User", back_populates="verifications")

    # Enforce one verification per user per report
    __table_args__ = (
        UniqueConstraint("report_id", "user_id", name="uq_report_user_verification"),
    )

class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("leak_reports.id", ondelete="CASCADE"), nullable=False)
    old_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)
    remarks = Column(Text, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    report = relationship("LeakReport", back_populates="status_history")
    changer = relationship("User", back_populates="status_changes")
