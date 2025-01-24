'''Module to connect to mysql database'''
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# config variable
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "scraper_db")


class MyDatabase:
    def __init__(self, db_host=DB_HOST, db_user=DB_USER, db_password=DB_PASSWORD, db_name=DB_NAME):
        try:
            self.conn = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
            self.cur = self.conn.cursor()
            self.db_name = db_name
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    url VARCHAR(255),
                    upc VARCHAR(64) UNIQUE,
                    name VARCHAR(128),
                    price_excl_tax DECIMAL(10, 2),
                    price_incl_tax DECIMAL(10, 2),
                    tax DECIMAL(10, 2),
                    price DECIMAL(10, 2),
                    type VARCHAR(32),
                    genre VARCHAR(32),
                    availability INTEGER,
                    no_of_reviews INTEGER,
                    stars INTEGER,
                    description TEXT,
                    PRIMARY KEY(id)
                )
            """)
        except mysql.connector.Error as err:
            print(f"[ERROR] Cannot connect to database: {err}")
            raise Exception(f"Cannot connect to database: {err}")
        self.sys_table = ['information_schema', 'mysql', 'performance_schema', 'sys']

    def get_tables_name(self):
        self.cur.execute("SHOW TABLES;")
        all_user_tables = [table[0] for table in self.cur.fetchall() if table[0] not in self.sys_table]
        return all_user_tables

    def get_column_names(self, table_name):
        '''Get all column names of a table'''
        # Validate table_name to prevent SQL injection
        if not table_name.isidentifier():
            raise ValueError("Invalid table name")
            
        self.cur.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column[0] for column in self.cur.fetchall()]
        print(f"[INFO] Columns are: {columns}")
        return columns

    def get_records(self, table, limit=5, offset=None):
        # Validate table name
        if not table.isidentifier():
            return "Invalid table name"

        try:
            query = f"SELECT * FROM {table} LIMIT %s"
            params = [limit]
            
            if offset is not None:
                query += " OFFSET %s"
                params.append(offset)
                
            self.cur.execute(query, tuple(params))
            records = self.cur.fetchall()
            return records
        except mysql.connector.Error as err:
            print(f"Error occurred while reading from database: {err}")
            return f"Error occurred while reading from database: {err}"

    def close_connection(self):
        self.cur.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()


if __name__ == "__main__":
    try:
        with MyDatabase() as db:
            SAMPLE_TABLE_NAME = "books"
            # Check if table exists before querying
            tables = db.get_tables_name()
            if SAMPLE_TABLE_NAME in tables:
                column_names = db.get_column_names(SAMPLE_TABLE_NAME)
                db.get_records(SAMPLE_TABLE_NAME)
            else:
                print(f"Table {SAMPLE_TABLE_NAME} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
