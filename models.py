from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ChatSettings(Base):
    __tablename__ = 'chat_settings'
    id = Column(BigInteger, primary_key=True)
    title = Column(String)
    welcome_text = Column(String, nullable=True)
    rules_text = Column(String, nullable=True)
    warn_limit = Column(Integer, default=3)
    warn_period = Column(Integer, default=7*24*60)      # минуты
    mute_duration = Column(Integer, default=7*24*60)
    ban_duration = Column(Integer, nullable=True)
    is_antispam = Column(Boolean, default=True)
    access_map = Column(JSON, default={})

class UserRank(Base):
    __tablename__ = 'user_ranks'
    chat_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    rank = Column(Integer, default=0)
    assigned_by = Column(BigInteger)
    assigned_at = Column(DateTime, default=datetime.now)

class Warn(Base):
    __tablename__ = 'warns'
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    issuer_id = Column(BigInteger)
    reason = Column(String, nullable=True)
    issued_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)

class Mute(Base):
    __tablename__ = 'mutes'
    chat_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    expires_at = Column(DateTime)

class Ban(Base):
    __tablename__ = 'bans'
    chat_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    expires_at = Column(DateTime, nullable=True)