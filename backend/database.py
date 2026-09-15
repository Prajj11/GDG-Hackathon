import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, ForeignKey, String, Text, JSON, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./digital_guardrails.db')
if DATABASE_URL.startswith(('postgres://', 'postgresql://')):
    DATABASE_URL = 'postgresql+psycopg://' + DATABASE_URL.split('://', 1)[1]
elif DATABASE_URL.startswith('sqlite:///'):
    raw_path = DATABASE_URL.split('sqlite:///', 1)[1]
    dir_name = os.path.dirname(raw_path)
    if dir_name and not os.path.isdir(dir_name):
        try:
            os.makedirs(dir_name, exist_ok=True)
        except Exception:
            DATABASE_URL = 'sqlite:///./digital_guardrails.db'
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
    name: Mapped[str] = mapped_column(String(80), default='Guardian')
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

class Account(Base):
    __tablename__ = 'accounts'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(20), index=True)  # 'guardian' | 'ngo'
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    full_name: Mapped[str] = mapped_column(String(100), default='')
    organization_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    stationed_location: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    child_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=now)

class Report(Base):
    __tablename__ = 'reports'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    linked_alert_id: Mapped[str | None] = mapped_column(ForeignKey('alerts.id', ondelete='SET NULL'), nullable=True)
    # Only a SHA-256 digest of a random receipt secret is retained.
    anonymous_token: Mapped[str] = mapped_column(String(64), unique=True)
    selected_context: Mapped[str] = mapped_column(String(50))
    report_text: Mapped[str] = mapped_column(Text, default='')
    urgency_level: Mapped[str] = mapped_column(String(10))
    locality: Mapped[str] = mapped_column(String(60), default='South Delhi', index=True)
    assigned_worker: Mapped[str | None] = mapped_column(String(80), nullable=True)
    caseworker_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    detection_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='submitted')
    created_at: Mapped[datetime] = mapped_column(default=now, index=True)

def ensure_schema(target_engine):
    Base.metadata.create_all(target_engine, tables=[Account.__table__])
    if str(target_engine.url).startswith('sqlite'):
        with target_engine.connect() as conn:
            cursor = conn.exec_driver_sql("PRAGMA table_info(reports)")
            cols = [row[1] for row in cursor.fetchall()]
            if cols:
                if 'locality' not in cols:
                    conn.exec_driver_sql("ALTER TABLE reports ADD COLUMN locality VARCHAR(60) DEFAULT 'South Delhi'")
                if 'assigned_worker' not in cols:
                    conn.exec_driver_sql("ALTER TABLE reports ADD COLUMN assigned_worker VARCHAR(80)")
                if 'caseworker_notes' not in cols:
                    conn.exec_driver_sql("ALTER TABLE reports ADD COLUMN caseworker_notes TEXT")
                conn.commit()

    with SessionLocal() as db:
        if db.query(Account).count() == 0:
            from passlib.context import CryptContext
            pwd_ctx = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
            demo_hash = pwd_ctx.hash('demo123')
            db.add_all([
                Account(
                    role='guardian',
                    username='guardian',
                    email='guardian@family.org',
                    password_hash=demo_hash,
                    full_name='Priya Sharma',
                    child_name="Aarav's Phone"
                ),
                Account(
                    role='ngo',
                    username='cwc_southdelhi',
                    email='officer.delhi@cwc.gov.in',
                    password_hash=demo_hash,
                    full_name='Ms. S. Sharma (CPO)',
                    organization_name='South Delhi Child Welfare Committee',
                    stationed_location='South Delhi'
                ),
                Account(
                    role='ngo',
                    username='mumbai_cwc',
                    email='support@mumbaicwc.org',
                    password_hash=demo_hash,
                    full_name='Rajesh Varma (Field Officer)',
                    organization_name='Mumbai Suburban Child Protection Unit',
                    stationed_location='Mumbai Suburban'
                ),
                Account(
                    role='ngo',
                    username='bengaluru_cwc',
                    email='contact@bengalurucwc.org',
                    password_hash=demo_hash,
                    full_name='Dr. Anita Rao',
                    organization_name='Bengaluru Urban Child Welfare Committee',
                    stationed_location='Bengaluru Urban'
                ),
            ])
            db.commit()

class AidRoute(Base):
    __tablename__ = 'aid_routes'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey('reports.id', ondelete='CASCADE'), unique=True)
    aid_channel_name: Mapped[str] = mapped_column(String(100))
    routed_at: Mapped[datetime] = mapped_column(default=now)
    status: Mapped[str] = mapped_column(String(30))

class DatasetRecord(Base):
    __tablename__ = 'dataset_records'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    origin: Mapped[str] = mapped_column(String(20), index=True)  # 'real' | 'synthetic'
    source_dataset: Mapped[str] = mapped_column(String(80), index=True)
    language: Mapped[str] = mapped_column(String(30), index=True)
    script: Mapped[str] = mapped_column(String(20))
    pattern_label: Mapped[str] = mapped_column(String(60), index=True)
    risk_level: Mapped[str] = mapped_column(String(20), index=True)
    target_text: Mapped[str] = mapped_column(Text)
    window_text: Mapped[str] = mapped_column(Text)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    turns: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(default=now)
