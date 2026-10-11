from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings


def normalize_database_url(url: str) -> str:
    """Normalize Supabase/Render PostgreSQL URLs for psycopg 3 + SQLAlchemy."""
    url = url.strip()
    # Supabase dashboard and many hosting providers may show postgres:// or
    # postgresql:// URLs. This project installs psycopg v3, so select its dialect.
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]

    # Supabase requires encrypted connections. Add sslmode=require only when
    # the connection URL does not already specify an SSL mode.
    if url.startswith("postgresql+psycopg://") and "sslmode=" not in url.lower():
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}sslmode=require"
    return url


database_url = normalize_database_url(settings.database_url)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
