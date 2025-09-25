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


user_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("email", sa.String, unique=True),
    sa.Column("password", sa.String),
    sa.Column("confirmed", sa.Boolean, default=False),
)

posts = sa.Table(
    "posts",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("body", sa.String),
    sa.Column("user_id", sa.ForeignKey("users.id"), nullable=False),
)

comments = sa.Table(
    "comments",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("body", sa.String),
    sa.Column("post_id", sa.ForeignKey("posts.id"), nullable=False),
    sa.Column("user_id", sa.ForeignKey("users.id"), nullable=False),
)

likes_table = sa.Table(
    "likes",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("post_id", sa.ForeignKey("posts.id"), nullable=False),
    sa.Column("user_id", sa.ForeignKey("users.id"), nullable=False),
)

metadata.create_all(engine)  # Create tables after defining them

database = databases.Database(
    settings.database_url, force_rollback=settings.db_force_rollback
)
