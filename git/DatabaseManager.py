import sqlite3
import json

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

    def add_project_from_json(self, project_json):
        """
        Dodaje projekt i powiązaną bramę na podstawie danych z JSON.
        Jeśli projekt o tej samej nazwie już istnieje, usuwa go przed dodaniem nowego.

        :param project_json: Słownik reprezentujący dane projektu i bramy.
        :return: None
        """
        try:
            # Pobranie nazwy projektu
            project_name = project_json.get("Nazwa projektu")
            if not project_name:
                raise ValueError("JSON musi zawierać klucz 'Nazwa projektu'.")

            # Sprawdzenie, czy projekt o tej nazwie już istnieje
            if self.check_project_existence(project_name):
                conn = self.connect()
                cursor = conn.cursor()

                # Pobranie ID projektu
                cursor.execute("SELECT id FROM Projekt WHERE nazwa = ?", (project_name,))
                projekt_id = cursor.fetchone()[0]  # Pobranie ID projektu

                # Usuwanie powiązanych rekordów z tabel bram
                cursor.execute("DELETE FROM BramaSegmentowa WHERE projekt_id = ?", (projekt_id,))
                cursor.execute("DELETE FROM BramaRoletowa WHERE projekt_id = ?", (projekt_id,))
                cursor.execute("DELETE FROM BramaRozwierana WHERE projekt_id = ?", (projekt_id,))
                cursor.execute("DELETE FROM BramaUchylna WHERE projekt_id = ?", (projekt_id,))

                # Usuwanie rekordu z tabeli Projekt
                cursor.execute("DELETE FROM Projekt WHERE id = ?", (projekt_id,))

                conn.commit()
                print(f"Usunięto istniejący projekt o nazwie '{project_name}' oraz powiązane rekordy.")
                conn.close()

            # Pobranie typu bramy
            gate_type = project_json.get("Typ bramy")
            if not gate_type:
                raise ValueError("JSON musi zawierać klucz 'Typ bramy' określający typ bramy.")

            # Dopasowanie typu bramy do bazy danych
            typ_bramy_map = {
                "Brama Segmentowa": "segmentowa",
                "Brama Roletowa": "roletowa",
                "Brama Rozwierana": "rozwierana",
                "Brama Uchylna": "uchylna",
            }

            if gate_type not in typ_bramy_map:
                raise ValueError(f"Nieznany typ bramy: {gate_type}")

            typ_bramy = typ_bramy_map[gate_type]

            # Pobranie wymiarów
            dimensions = project_json.get("Wymiary", {})
            width = dimensions.get("Szerokość")
            height = dimensions.get("Wysokość")

            conn = self.connect()
            cursor = conn.cursor()

            # Dodanie projektu do tabeli Projekt
            cursor.execute(
                "INSERT INTO Projekt (nazwa, data_zapisu, typ_bramy) VALUES (?, CURRENT_TIMESTAMP, ?)",
                (project_name, typ_bramy)
            )
            projekt_id = cursor.lastrowid  # Pobierz ID dodanego projektu

            # Dodanie danych bramy do odpowiedniej tabeli
            gate_data = self._map_gate_data(typ_bramy, project_json)
            self._add_gate(cursor, projekt_id, typ_bramy, gate_data, width, height)

            conn.commit()
            print(f"Projekt '{project_name}' został dodany do bazy danych.")

        except sqlite3.Error as e:
            print(f"Błąd SQL podczas dodawania projektu: {e}")
        except Exception as e:
            print(f"Błąd: {e}")
        finally:
            conn.close()

    def _map_gate_data(self, typ_bramy, gate_data):
        """
        Mapuje dane bramy z JSON na format wymagany przez bazę danych.

        :param typ_bramy: Typ bramy (np. "segmentowa", "roletowa", itp.)
        :param gate_data: Słownik danych bramy.
        :return: Słownik dopasowany do struktury bazy danych.
        """
        try:
            if typ_bramy == "segmentowa":
                return {
                    "rodzaj_przetloczenia": gate_data.get("Rodzaj przetłoczenia", None),
                    "struktura_powierzchni": gate_data.get("Struktura powierzchni", None),
                    "kolor_standardowy": gate_data.get("Kolor standardowy", None),
                    "kolor_ral": gate_data.get("Kolor RAL", None),
                    "sposob_otwierania_drzwi": gate_data.get("Sposób otwierania drzwi", None),
                    "opcje_dodatkowe": ", ".join(gate_data.get("Opcje dodatkowe", [])),
                    "kratka_wentylacyjna": gate_data.get("Kratka wentylacyjna", None),
                    "przeszklenia": gate_data.get("Przeszklenia", None),
                    "klamka_do_bramy": gate_data.get("Klamka do bramy", None),
                }

            elif typ_bramy == "roletowa":
                return {
                    "wysokosc_profili": gate_data.get("Wysokość profili", None),
                    "kolor_standardowy": gate_data.get("Kolor standardowy", None),
                    "kolor_ral": gate_data.get("Kolor RAL", None),
                    "sposob_otwierania_bramy": gate_data.get("Sposób otwierania bramy", None),
                    "przeszklenia": gate_data.get("Przeszklenia", None),
                }

            elif typ_bramy == "rozwierana":
                return {
                    "ilosc_skrzydel": gate_data.get("Ilość skrzydeł", None),
                    "ocieplenie": gate_data.get("Ocieplenie", None),
                    "uklad_wypelnienia": gate_data.get("Układ wypełnienia", None),
                    "kolor_standardowy": gate_data.get("Kolor standardowy", None),
                    "kolor_ral": gate_data.get("Kolor RAL", None),
                    "przeszklenia": gate_data.get("Przeszklenia", None),
                    "opcje_dodatkowe": ", ".join(gate_data.get("Opcje dodatkowe", [])),
                }

            elif typ_bramy == "uchylna":
                return {
                    "uklad_wypelnienia": gate_data.get("Układ wypełnienia", None),
                    "kolor_standardowy": gate_data.get("Kolor standardowy", None),
                    "kolor_ral": gate_data.get("Kolor RAL", None),
                    "sposob_otwierania_drzwi": gate_data.get("Sposób otwierania drzwi", None),
                    "przeszklenia": gate_data.get("Przeszklenia", None),
                    "drzwi_przejsciowe": gate_data.get("Drzwi przejściowe", None),
                    "opcje_dodatkowe": ", ".join(gate_data.get("Opcje dodatkowe", [])),
                }

            else:
                raise ValueError(f"Nieobsługiwany typ bramy: {typ_bramy}")

        except Exception as e:
            print(f"Błąd podczas mapowania danych dla typu '{typ_bramy}': {e}")
            return {}

    def _add_gate(self, cursor, projekt_id, typ_bramy, gate_data, width, height):
        """
        Dodaje dane bramy do odpowiedniej tabeli.
        """
        if typ_bramy == "segmentowa":
            cursor.execute("""
                        INSERT INTO BramaSegmentowa 
                        (projekt_id, rodzaj_przetloczenia, struktura_powierzchni, kolor_standardowy, kolor_ral, 
                         sposob_otwierania_drzwi, opcje_dodatkowe, kratka_wentylacyjna, przeszklenia, klamka_do_bramy, szerokosc, wysokosc)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                projekt_id,
                gate_data.get("rodzaj_przetloczenia"),
                gate_data.get("struktura_powierzchni"),
                gate_data.get("kolor_standardowy"),
                gate_data.get("kolor_ral"),
                gate_data.get("sposob_otwierania_drzwi"),
                gate_data.get("opcje_dodatkowe"),
                gate_data.get("kratka_wentylacyjna"),
                gate_data.get("przeszklenia"),
                gate_data.get("klamka_do_bramy"),
                width,
                height
            ))

        elif typ_bramy == "roletowa":
            cursor.execute("""
                INSERT INTO BramaRoletowa 
                (projekt_id, wysokosc_profili, kolor_standardowy, kolor_ral, sposob_otwierania_bramy, przeszklenia, szerokosc, wysokosc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                projekt_id,
                gate_data.get("wysokosc_profili"),
                gate_data.get("kolor_standardowy"),
                gate_data.get("kolor_ral"),
                gate_data.get("sposob_otwierania_bramy"),
                gate_data.get("przeszklenia"),
                width,
                height
            ))

        elif typ_bramy == "rozwierana":
            cursor.execute("""
                INSERT INTO BramaRozwierana 
                (projekt_id, ilosc_skrzydel, ocieplenie, uklad_wypelnienia, kolor_standardowy, kolor_ral, przeszklenia, opcje_dodatkowe, szerokosc, wysokosc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                projekt_id,
                gate_data.get("ilosc_skrzydel"),
                gate_data.get("ocieplenie"),
                gate_data.get("uklad_wypelnienia"),
                gate_data.get("kolor_standardowy"),
                gate_data.get("kolor_ral"),
                gate_data.get("przeszklenia"),
                gate_data.get("opcje_dodatkowe"),
                width,
                height
            ))

        elif typ_bramy == "uchylna":
            cursor.execute("""
                INSERT INTO BramaUchylna 
                (projekt_id, uklad_wypelnienia, kolor_standardowy, kolor_ral, sposob_otwierania_drzwi, przeszklenia, opcje_dodatkowe, szerokosc, wysokosc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                projekt_id,
                gate_data.get("uklad_wypelnienia"),
                gate_data.get("kolor_standardowy"),
                gate_data.get("kolor_ral"),
                gate_data.get("sposob_otwierania_drzwi"),
                gate_data.get("przeszklenia"),
                gate_data.get("opcje_dodatkowe"),
                width,
                height
            ))

    def get_project_by_name(self, project_name):
        """
        Pobiera szczegóły projektu oraz powiązaną bramę na podstawie nazwy projektu.

        :param project_name: Nazwa projektu.
        :return: Słownik zawierający dane projektu oraz powiązanej bramy.
        """
        conn = self.connect()
        cursor = conn.cursor()

        # Pobierz szczegóły projektu na podstawie nazwy
        cursor.execute("SELECT * FROM Projekt WHERE nazwa = ?", (project_name,))
        project = cursor.fetchone()

        if not project:
            conn.close()
            raise ValueError(f"Projekt o nazwie '{project_name}' nie istnieje.")

        # Słownik na dane wyjściowe
        project_data = {
            "projekt": {
                "id": project[0],
                "nazwa": project[1],
                "data_zapisu": project[2],
                "typ_bramy": project[3]
            },
            "brama": None
        }

        # Pobierz dane o bramie na podstawie typu bramy
        typ_bramy = project[3]

        if typ_bramy == "segmentowa":
            cursor.execute("SELECT * FROM BramaSegmentowa WHERE projekt_id = ?", (project[0],))
            brama = cursor.fetchone()
            if brama:
                project_data["brama"] = {
                    "rodzaj_przetloczenia": brama[2],
                    "struktura_powierzchni": brama[3],
                    "kolor_standardowy": brama[4],
                    "kolor_ral": brama[5],
                    "sposob_otwierania_drzwi": brama[6],
                    "opcje_dodatkowe": brama[7],
                    "kratka_wentylacyjna": brama[8],
                    "przeszklenia": brama[9],
                    "klamka_do_bramy": brama[10],
                    "szerokosc": brama[11],
                    "wysokosc": brama[12]
                }

        elif typ_bramy == "roletowa":
            cursor.execute("SELECT * FROM BramaRoletowa WHERE projekt_id = ?", (project[0],))
            brama = cursor.fetchone()
            if brama:
                project_data["brama"] = {
                    "wysokosc_profili": brama[2],
                    "kolor_standardowy": brama[3],
                    "kolor_ral": brama[4],
                    "sposob_otwierania_bramy": brama[5],
                    "przeszklenia": brama[6],
                    "szerokosc": brama[7],
                    "wysokosc": brama[8]
                }

        elif typ_bramy == "rozwierana":
            cursor.execute("SELECT * FROM BramaRozwierana WHERE projekt_id = ?", (project[0],))
            brama = cursor.fetchone()
            if brama:
                project_data["brama"] = {
                    "ilosc_skrzydel": brama[2],
                    "ocieplenie": brama[3],
                    "uklad_wypelnienia": brama[4],
                    "kolor_standardowy": brama[5],
                    "kolor_ral": brama[6],
                    "przeszklenia": brama[7],
                    "opcje_dodatkowe": brama[8],
                    "szerokosc": brama[9],
                    "wysokosc": brama[10]
                }

        elif typ_bramy == "uchylna":
            cursor.execute("SELECT * FROM BramaUchylna WHERE projekt_id = ?", (project[0],))
            brama = cursor.fetchone()
            if brama:
                project_data["brama"] = {
                    "uklad_wypelnienia": brama[2],
                    "kolor_standardowy": brama[3],
                    "kolor_ral": brama[4],
                    "sposob_otwierania_drzwi": brama[5],
                    "przeszklenia": brama[6],
                    "opcje_dodatkowe": brama[7],
                    "szerokosc": brama[8],
                    "wysokosc": brama[9]
                }

        conn.close()
        return project_data

    def load_project_to_json(self, project_name, output_file):
        """
        Pobiera dane projektu z bazy na podstawie nazwy projektu i zapisuje je do pliku JSON.

        :param project_name: Nazwa projektu, który ma być zapisany do JSON.
        :param output_file: Ścieżka do pliku, w którym dane zostaną zapisane.
        """
        try:
            # Pobierz dane projektu
            project_data = self.get_project_by_name(project_name)
            if not project_data:
                print(f"Nie znaleziono projektu o nazwie {project_name}")
                return
            # Mapowanie typu bramy na pełną nazwę
            full_gate_type_map = {
                "segmentowa": "Brama Segmentowa",
                "roletowa": "Brama Roletowa",
                "uchylna": "Brama Uchylna",
                "rozwierana": "Brama Rozwierana"
            }
            # Pobranie pełnej nazwy bramy
            gate_type_full = full_gate_type_map.get(project_data["projekt"]["typ_bramy"], "Nieznany typ bramy")

            # Mapowanie kluczy na polskie nazwy
            key_map = {
                "ilosc_skrzydel": "Ilość skrzydeł",
                "ocieplenie": "Ocieplenie",
                "uklad_wypelnienia": "Układ wypełnienia",
                "kolor_standardowy": "Kolor standardowy",
                "kolor_ral": "Kolor RAL",
                "wysokosc_profili": "Wysokość profili",
                "sposob_otwierania_drzwi": "Sposób otwierania drzwi",
                "sposob_otwierania_bramy": "Sposób otwierania bramy",
                "przeszklenia": "Przeszklenia",
                "drzwi_przejsciowe": "Drzwi przejściowe",
                "opcje_dodatkowe": "Opcje dodatkowe",
                "rodzaj_przetloczenia": "Rodzaj przetłoczenia",
                "struktura_powierzchni": "Struktura powierzchni",
                "kratka_wentylacyjna": "Kratka wentylacyjna",
                "przeszklenia": "Przeszklenia",
                "klamka_do_bramy": "Klamka do bramy"
            }

            # Przygotowanie struktury JSON
            project_json = {
                "Nazwa Projektu": project_data["projekt"]["nazwa"],
                "Typ bramy": gate_type_full,
                "Wymiary": {
                    "Szerokość": project_data["brama"]["szerokosc"],
                    "Wysokość": project_data["brama"]["wysokosc"]
                }
            }
            # Przetwarzanie danych bramy
            for key, value in project_data["brama"].items():
                if key in ["szerokosc", "wysokosc"]:
                    continue  # Pomijamy szerokość i wysokość, bo są już w "Wymiary"
                mapped_key = key_map.get(key, key)  # Mapowanie kluczy na polskie nazwy
                if key == "opcje_dodatkowe" and value:  # Opcje dodatkowe jako lista
                    project_json[mapped_key] = [opt.strip() for opt in value.split(",")]
                else:
                    project_json[mapped_key] = value

            # Zapis do pliku JSON
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(project_json, json_file, ensure_ascii=False, indent=4)

            print(f"Projekt zapisano do pliku JSON: {output_file}")
        except Exception as e:
           print(f"Błąd podczas zapisywania projektu do JSON: {e}")

    def check_project_existence(self, project_name):
        """
        Sprawdza, czy projekt o podanej nazwie istnieje w bazie danych.
        Zwraca True, jeśli projekt istnieje, w przeciwnym razie False.
        """
        try:
            conn = self.connect()  # Nawiązanie połączenia z bazą
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM Projekt WHERE nazwa = ?"
            cursor.execute(query, (project_name,))
            result = cursor.fetchone()
            conn.close()
            return result[0] > 0  # Zwraca True, jeśli istnieje przynajmniej 1 rekord z tą nazwą projektu
        except sqlite3.Error as e:
            print(f"Błąd podczas sprawdzania istnienia projektu: {e}")
            return False


# TESTOWANIE BAZY DANYCH
if __name__ == "__main__":
    db_manager = DatabaseManager()
    #
    # # Dodanie nowego projektu
    # db_manager.add_project("Projekt G", "Brama Segmentowa")
    # db_manager.add_project("Projekt H", "Brama Roletowa")
    # db_manager.add_project("Projekt I", "Brama Uchylna")
    # db_manager.add_project("Projekt J", "Brama Rozwierana")
    # db_manager.add_project("Projekt K", "Brama Uchylna")

    # Listowanie projektów
    projekty = db_manager.list_projects()
    for projekt in projekty:
        print(projekt)

    # Załadowanie JSON jako słownika Python

    db_manager = DatabaseManager()
    with open("../resources/selected_options.json", "r", encoding="utf-8") as file:
        project_json = json.load(file)
    # Dodanie projektu do bazy danych
    db_manager = DatabaseManager()
    db_manager.add_project_from_json(project_json)
