# database.py
import databases
import sqlalchemy as sa

from social_media_api.config import settings

print(f"Database URL in database.py: {settings.database_url}")  # Debug print

metadata = sa.MetaData()

engine = sa.create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Only needed for SQLite
)

posts = sa.Table(
    "posts",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("body", sa.String),
)

comments = sa.Table(
    "comments",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("body", sa.String),
    sa.Column("post_id", sa.ForeignKey("posts.id"), nullable=False),
)

metadata.create_all(engine)  # Create tables after defining them

database = databases.Database(
    settings.database_url, force_rollback=settings.db_force_rollback
)
