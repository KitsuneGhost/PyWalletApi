import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://pywallet_user:pywallet_pass@localhost:5432/pywallet"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
