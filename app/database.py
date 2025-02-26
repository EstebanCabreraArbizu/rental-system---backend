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

class Database:
    @staticmethod
    def execute_query(query, params=None, fetch=True):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = None
                
            return result
            
        except Exception as e:
            print(f"Error en la consulta: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
            raise
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close() 