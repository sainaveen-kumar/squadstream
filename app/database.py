import os
from sqlmodel import SQLModel, create_engine, Session

# 1. Get DB URL from Environment Variable (Render provides this)
database_url = os.environ.get("DATABASE_URL")

# 2. Fallback to SQLite if no URL is found (Local Development)
if not database_url:
    sqlite_file_name = "squadstream.db"
    database_url = f"sqlite:///{sqlite_file_name}"
    connect_args = {"check_same_thread": False} # Required for SQLite
else:
    # 3. Fix for Postgres URL (Render uses 'postgres://', SQLAlchemy needs 'postgresql://')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    connect_args = {} # Postgres doesn't need special args

# 4. Create the Engine
engine = create_engine(database_url, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)