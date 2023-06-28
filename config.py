import os
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSW = os.getenv('DB_PASSW')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

DATABASE_URL = os.getenv('DATABASE_URL')
