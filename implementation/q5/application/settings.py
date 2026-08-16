from os import getenv


class Settings:
    API_TOKEN = getenv("USER_API_TOKEN", "")
    DATABASE_URL = getenv("USER_DATABASE_URL", "sqlite:///users.db")
    PASSWORD_ITERATIONS = int(getenv("USER_PASSWORD_ITERATIONS", "200000"))
    PASSWORD_SALT_BYTES = int(getenv("USER_PASSWORD_SALT_BYTES", "16"))
    GENERATED_PASSWORD_LENGTH = int(getenv("USER_GENERATED_PASSWORD_LENGTH", "12"))

