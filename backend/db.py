from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="user")

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target = Column(String(255), nullable=False)
    tools_used = Column(JSON)
    status = Column(Enum("running", "complete", "failed"), default="running")
    scan_date = Column(DateTime, default=datetime.utcnow)
    overall_risk = Column(String(50))
    has_accepted_disclaimer = Column(Integer, default=0)

    user = relationship("User", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")
    fixes = relationship("Fix", back_populates="scan", cascade="all, delete-orphan")
    exploits = relationship("Exploit", back_populates="scan", cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="scan", uselist=False, cascade="all, delete-orphan")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    vuln_id = Column(String(20))
    name = Column(String(255))
    severity = Column(Enum("Critical", "High", "Medium", "Low", "Info"))
    cvss_score = Column(Float)
    cve_ids = Column(JSON)
    affected_port = Column(String(30))
    affected_service = Column(String(150))
    description = Column(Text)
    evidence = Column(Text)
    attack_vector = Column(String(50))
    exploitability = Column(String(50))

    scan = relationship("Scan", back_populates="vulnerabilities")

class Fix(Base):
    __tablename__ = "fixes"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    vuln_id = Column(String(20))
    fix_summary = Column(String(255))
    fix_detail = Column(Text)
    patch_ref = Column(String(500))
    priority = Column(Enum("Immediate", "Short-term", "Long-term"))

    scan = relationship("Scan", back_populates="fixes")

class Exploit(Base):
    __tablename__ = "exploits"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    vuln_id = Column(String(20))
    exploit_name = Column(String(255))
    tool_used = Column(String(100))
    payload = Column(Text)
    difficulty = Column(String(50))
    notes = Column(Text)

    scan = relationship("Scan", back_populates="exploits")

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), unique=True)
    raw_outputs = Column(Text)
    ai_analysis = Column(Text)
    executive_summary = Column(Text)
    attack_surface = Column(JSON)
    pentest_notes = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)
    user_notes = Column(Text)

    scan = relationship("Scan", back_populates="summary")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db, username: str, email: str, password_hash: str):
    user = User(username=username, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_scan(db, user_id: int, target: str, tools_used: list, has_accepted_disclaimer: int = 0):
    scan = Scan(
        user_id=user_id,
        target=target,
        tools_used=tools_used,
        status="running",
        has_accepted_disclaimer=has_accepted_disclaimer
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan

def get_scan(db, scan_id: int, user_id: int):
    return db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user_id).first()

def update_scan_status(db, scan_id: int, status: str, overall_risk: str = None):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.status = status
        if overall_risk:
            scan.overall_risk = overall_risk
        db.commit()
    return scan

def save_vulnerability(db, scan_id: int, vuln_data: dict):
    vuln = Vulnerability(scan_id=scan_id, **vuln_data)
    db.add(vuln)
    db.commit()
    return vuln

def save_fix(db, scan_id: int, fix_data: dict):
    fix = Fix(scan_id=scan_id, **fix_data)
    db.add(fix)
    db.commit()
    return fix

def save_exploit(db, scan_id: int, exploit_data: dict):
    exploit = Exploit(scan_id=scan_id, **exploit_data)
    db.add(exploit)
    db.commit()
    return exploit

def save_summary(db, scan_id: int, summary_data: dict):
    existing = db.query(Summary).filter(Summary.scan_id == scan_id).first()
    if existing:
        for key, value in summary_data.items():
            setattr(existing, key, value)
    else:
        summary = Summary(scan_id=scan_id, **summary_data)
        db.add(summary)
    db.commit()
    return existing

def get_user_scans(db, user_id: int, skip: int = 0, limit: int = 50):
    return db.query(Scan).filter(Scan.user_id == user_id).order_by(Scan.scan_date.desc()).offset(skip).limit(limit).all()

def get_scan_stats(db, user_id: int):
    scans = db.query(Scan).filter(Scan.user_id == user_id).all()
    total = len(scans)
    complete = len([s for s in scans if s.status == "complete"])
    critical = 0
    high = 0
    medium = 0
    low = 0
    for scan in scans:
        if scan.vulnerabilities:
            for v in scan.vulnerabilities:
                if v.severity == "Critical":
                    critical += 1
                elif v.severity == "High":
                    high += 1
                elif v.severity == "Medium":
                    medium += 1
                elif v.severity == "Low":
                    low += 1
    return {
        "total": total,
        "complete": complete,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low
    }

def delete_scan(db, scan_id: int, user_id: int):
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user_id).first()
    if scan:
        db.delete(scan)
        db.commit()
        return True
    return False