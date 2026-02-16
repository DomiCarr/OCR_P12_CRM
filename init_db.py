# init_db.py
from sqlalchemy import create_engine
from app.models import Base
from config.config import Config


def create_tables():
    """
    Creates all database tables defined in the models.
    """
    engine = create_engine(Config.get_db_url())

    print("Connecting to the database...")
    try:
        # Create all tables stored in the metadata
        Base.metadata.create_all(engine)
        print("Success: All tables created successfully.")
    except Exception as e:
        print(f"Error during table creation: {e}")


if __name__ == "__main__":
    create_tables()