"""File with settings and configs for the project"""

from envparse import Env
env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@localhost:5433/postgres",
)

TEST_DATABASE_URL =env.str(
    "TEST_DATABASE_URL",
    default="postgresql+asyncpg://postgres_test:postgres_test@localhost:5434/postgres_test"
)