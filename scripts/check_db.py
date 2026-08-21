import sys
import os
sys.path.append(os.getcwd())
from config import Config
from sqlalchemy import create_engine

try:
    print(f"Testing connection to: {Config.SQLALCHEMY_DATABASE_URI}")
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    connection = engine.connect()
    print("Connection successful!")
    connection.close()
except Exception as e:
    print(f"Connection failed: {e}")
