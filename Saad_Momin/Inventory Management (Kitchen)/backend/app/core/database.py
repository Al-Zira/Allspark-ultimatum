from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy import Column, Float
from sqlalchemy.sql import text
from sqlalchemy import inspect

# Load environment variables
load_dotenv()

# Get database URL from environment variable, default to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kitchen_inventory.db")

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=5,         # Maximum number of connections
    max_overflow=10      # Maximum number of connections beyond pool_size
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create MetaData instance
metadata = MetaData()

# Create base class for declarative models
Base = declarative_base(metadata=metadata)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        # Import models here to ensure they are registered with Base
        from app.models.inventory import InventoryItem
        from app.models.expiration import ExpirationTracker
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise 

def migrate_db():
    """Handle migrations"""
    inspector = inspect(engine)
    if 'inventory_items' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('inventory_items')]
        if 'value_per_unit' not in columns:
            with engine.begin() as conn:
                conn.execute(text('ALTER TABLE inventory_items ADD COLUMN value_per_unit FLOAT'))
        if 'estimated_value' not in columns:
            with engine.begin() as conn:
                conn.execute(text('ALTER TABLE inventory_items ADD COLUMN estimated_value FLOAT'))
                # Update existing records to calculate estimated_value
                conn.execute(text('UPDATE inventory_items SET estimated_value = value_per_unit * quantity WHERE value_per_unit IS NOT NULL')) 