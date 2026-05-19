# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Flask Secret Key
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

    # MongoDB Configuration
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017/habittracker"
    )