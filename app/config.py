import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    SQLSERVER_CONNECTION = (
        "DRIVER={SQL Server};"
        "SERVER=LAPTOP-70S6BK7M;"
        "DATABASE=RENTALLDB;"
        "UID=dev_mps;"
        "PWD=polo1266"
    )
