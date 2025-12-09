import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"  # gets database url from env variable
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET = os.getenv(
        "JWT_SECRET"
    )
    JWT_ISSUER = os.getenv(
        "JWT_ISSUER"
    )
