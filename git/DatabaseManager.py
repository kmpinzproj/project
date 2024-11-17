import sqlite3
from sqlite3 import Error

class DatabaseManager:
    def __init__(self, db_file):
        """
        Inicjalizuje obiekt klasy DatabaseManager i tworzy połączenie z bazą danych.
        :param db_file: ścieżka do pliku bazy danych SQLite
        """
        self.db_file = db_file
        self.conn = None
        self.connect()

    def connect(self):
        """
        Nawiązuje połączenie z bazą danych.
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            print("Połączono z bazą danych.")
        except Error as e:
            print(f"Błąd podczas łączenia z bazą danych: {e}")

    def execute_query(self, query, params=None):
        """
        Wykonuje zapytanie SQL.
        :param query: zapytanie SQL do wykonania
        :param params: opcjonalne parametry do zapytania
        :return: wynik zapytania (jeśli dotyczy)
        """
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
            print("Zapytanie wykonane pomyślnie.")
            return cursor
        except Error as e:
            print(f"Błąd podczas wykonywania zapytania: {e}")
            return None

    def fetch_all(self, query, params=None):
        """
        Pobiera wszystkie wiersze z wyniku zapytania.
        :param query: zapytanie SQL
        :param params: opcjonalne parametry do zapytania
        :return: lista wyników
        """
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return []

    def close(self):
        """
        Zamyka połączenie z bazą danych.
        """
        if self.conn:
            self.conn.close()
            print("Połączenie z bazą danych zostało zamknięte.")