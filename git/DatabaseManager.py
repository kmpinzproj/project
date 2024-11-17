import sqlite3

class DatabaseManager:

    DB_PATH = '../resources/project_db.db'

    def connect(self):
        """Nawiązuje połączenie z bazą danych."""
        return sqlite3.connect(self.DB_PATH)

    def list_projects(self):
        """Wyświetla wszystkie rekordy z tabeli Projekt."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Projekt")
            projects = cursor.fetchall()
            conn.close()
            return projects
        except sqlite3.Error as e:
            print(f"Błąd podczas listowania danych: {e}")
            return []

    def add_project(self, nazwa, typ_bramy):
        """Dodaje nowy rekord do tabeli Projekt.
        :param nazwa: Nazwa projektu.
        :param typ_bramy: Typ bramy projektu.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Projekt (nazwa, typ_bramy, data_zapisu) VALUES (?, ?, CURRENT_TIMESTAMP)", (nazwa, typ_bramy))
            conn.commit()
            conn.close()
            print("Dodano nowy projekt.")
        except sqlite3.Error as e:
            print(f"Błąd podczas dodawania rekordu: {e}")

# Przykład użycia klasy
if __name__ == "__main__":
    db_manager = DatabaseManager()

    # Dodanie nowego projektu
    db_manager.add_project("Projekt B", "Brama Segmentowa")
    db_manager.add_project("Projekt C", "Brama Roletowa")
    db_manager.add_project("Projekt D", "Brama Uchylna")
    db_manager.add_project("Projekt E", "Brama Rozwierana")
    db_manager.add_project("Projekt F", "Brama Uchylna")

    # Listowanie projektów
    projekty = db_manager.list_projects()
    for projekt in projekty:
        print(projekt)
