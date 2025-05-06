from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = "sqlite:///prometheus_swarm.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(SessionLocal)

def get_db():
    """
    Create a new database session
    
    Returns:
        A SQLAlchemy scoped session
    """
    return session

def get_session():
    """
    Get a new database session
    
    Returns:
        A new SQLAlchemy session
    """
    return SessionLocal()

def initialize_database():
    """
    Initialize the database by creating all tables
    """
    from . import transaction_evidence  # Import local model
    from sqlalchemy.orm import declarative_base
    
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)

# Call initialize_database when the module is imported
initialize_database()