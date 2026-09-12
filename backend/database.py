import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, ForeignKey, String, Text, JSON, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./digital_guardrails.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}, pool_pre_ping=True)
if DATABASE_URL.startswith('sqlite'):
    @event.listens_for(engine, 'connect')
    def foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')
SessionLocal = sessionmaker(engine, expire_on_commit=False)
class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), default='Demo guardian')
    retention_days: Mapped[int] = mapped_column(default=7)
    snippets_enabled: Mapped[bool] = mapped_column(default=True)
class Conversation(Base):
    __tablename__ = 'conversations'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    child_label: Mapped[str] = mapped_column(String(40))
    source_platform: Mapped[str] = mapped_column(String(30))
    language: Mapped[str] = mapped_column(String(30))
    message_count: Mapped[int] = mapped_column(default=0)
    signals: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(default=now)
class Alert(Base):
    __tablename__ = 'alerts'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id'), index=True)
    risk_score: Mapped[int]
    risk_level: Mapped[str] = mapped_column(String(10))
    pattern_type: Mapped[str] = mapped_column(String(60))
    flagged_snippet: Mapped[str] = mapped_column(String(180))
    explanation: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(80))
    confidence: Mapped[float]
    reviewed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=now, index=True)

class Report(Base):
    __tablename__ = 'reports'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    linked_alert_id: Mapped[str | None] = mapped_column(ForeignKey('alerts.id', ondelete='SET NULL'), nullable=True)
    # Only a SHA-256 digest of a random receipt secret is retained.
    anonymous_token: Mapped[str] = mapped_column(String(64), unique=True)
    selected_context: Mapped[str] = mapped_column(String(50))
    report_text: Mapped[str] = mapped_column(Text, default='')
    urgency_level: Mapped[str] = mapped_column(String(10))
    detection_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='submitted')
    created_at: Mapped[datetime] = mapped_column(default=now, index=True)

class AidRoute(Base):
    __tablename__ = 'aid_routes'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey('reports.id', ondelete='CASCADE'), unique=True)
    aid_channel_name: Mapped[str] = mapped_column(String(100))
    routed_at: Mapped[datetime] = mapped_column(default=now)
    status: Mapped[str] = mapped_column(String(30))
