import psycopg2
import psycopg2.extras
import pandas as pd

class PostgreSQL:
    def __init__(self) -> None:
        self.conn = psycopg2.connect('postgresql://metricas_en_vivo:datariders@dashboard-prod.clclsyibonem.us-east-1.rds.amazonaws.com:5432/metricas_en_vivo')

    def query(self, statement) -> pd.DataFrame:
        with self.conn.cursor() as cur:
            cur.execute(statement)
            results = cur.fetchall()
        return pd.DataFrame(results, columns=[i[0] for i in cur.description])

    def execute(self, statement, values=None):
        """Ejecuta una sentencia SQL con valores parametrizados."""
        with self.conn.cursor() as cur:
            try:
                cur.execute(statement, values)
            except Exception as e:
                print(f"Error ejecutando SQL: {e}")

    def disconnect(self):
        self.conn.close()
    
    def upsert(self, table_name: str, df: pd.DataFrame, key_cols: str = None):
        '''
        Inserta o actualiza registros en la tabla especificada utilizando los datos de un DataFrame.

        Parámetros:
        - `table_name` (str): El nombre de la tabla donde se insertarán o actualizarán los registros.
        - `df` (pd.DataFrame): El DataFrame que contiene los datos a insertar o actualizar.
        - `key_cols` (str, opcional): Las columnas utilizadas para identificar conflictos. Si no se especifica, se utilizan las dos primeras columnas del DataFrame.

        Devuelve:
        - None: Realiza el commit de la transacción a la base de datos.

        Excepciones:
        - Exception: Imprime el mensaje de error y la sentencia SQL si ocurre un error durante la ejecución.
        '''
        cols = ','.join(df.columns.to_list())
        key_cols = 'UKEY' if key_cols is None else key_cols  # Cambiar a UKEY
        update_cols = ', \n'.join([cadena + ' = EXCLUDED.' + cadena for cadena in df.columns.to_list()])
        statement = f''' INSERT INTO "{table_name}" ({cols}) VALUES %s
        ON CONFLICT ({key_cols}) DO 
        UPDATE SET {update_cols}
        '''
        data = [tuple(row) for row in df.itertuples(index=False)]

        with self.conn.cursor() as cur:
            try: psycopg2.extras.execute_values(cur, statement, data)
            except Exception as e: 
                print(e)
                print(statement, data)
        self.conn.commit()
