import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = 'tu_clave_secreta'
    SQLSERVER_CONNECTION = (
        'DRIVER={ODBC Driver 17 for SQL Server};'  # Asegúrate de tener este driver instalado
        'SERVER=LAPTOP-70S6BK7M;'
        'DATABASE=RENTALLDB2;'
        'UID=dev_mps;'
        'PWD=polo1266;'
        'Trusted_Connection=no;'
    )
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
