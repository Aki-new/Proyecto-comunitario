import sqlite3 as db

class ConexionDB:
    def __init__(self, db_path="database/database.db"):
        self.db_path = db_path

    def obtener_conexion(self):
        return db.connect(self.db_path)