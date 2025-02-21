import pyodbc
from .config import Config

def list_drivers():
    print("Drivers disponibles:")
    for driver in pyodbc.drivers():
        print(driver)

def get_db_connection():
    """
    Crea y retorna una conexión a la base de datos SQL Server
    """
    try:
        # Lista los drivers disponibles si hay error
        list_drivers()
        
        conn = pyodbc.connect(Config.SQLSERVER_CONNECTION)
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
        print("Cadena de conexión utilizada:", Config.SQLSERVER_CONNECTION)
        raise 