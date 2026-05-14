"""Initialize the database and create all tables."""

from db.base import Base
from db.models import Invoice, User  # noqa: F401
from db.session import engine


def init():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init()
