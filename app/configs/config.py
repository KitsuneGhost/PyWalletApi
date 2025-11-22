import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
        #"postgresql+psycopg2://postgres:SuperSecret123@localhost:5432/pywallet"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
