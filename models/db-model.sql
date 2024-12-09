CREATE TABLE Projekt (
    id INTEGER PRIMARY KEY,
    nazwa TEXT NOT NULL UNIQUE,
    data_zapisu DATETIME NOT NULL,
    typ_bramy TEXT NOT NULL
);

CREATE TABLE BramaSegmentowa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id INTEGER,
    rodzaj_przetloczenia TEXT,
    struktura_powierzchni TEXT,
    kolor_standardowy TEXT,
    kolor_ral TEXT,
    sposob_otwierania_drzwi TEXT,
    opcje_dodatkowe TEXT,
    kratka_wentylacyjna TEXT,
    przeszklenia TEXT,
    klamka_do_bramy TEXT,
    szerokosc INTEGER,
    wysokosc INTEGER,
    FOREIGN KEY (projekt_id) REFERENCES Projekt(id) ON DELETE CASCADE
);

CREATE TABLE BramaRoletowa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id INTEGER,
    wysokosc_profili INTEGER,
    kolor_standardowy TEXT,
    kolor_ral TEXT,
    sposob_otwierania_bramy TEXT,
    przeszklenia TEXT,
    szerokosc INTEGER,
    wysokosc INTEGER,
    FOREIGN KEY (projekt_id) REFERENCES Projekt(id) ON DELETE CASCADE
);

CREATE TABLE BramaRozwierana (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id INTEGER,
    ilosc_skrzydel TEXT,
    ocieplenie TEXT,
    uklad_wypelnienia TEXT,
    kolor_standardowy TEXT,
    kolor_ral TEXT,
    przeszklenia TEXT,
    opcje_dodatkowe TEXT,
    szerokosc INTEGER,
    wysokosc INTEGER,
    FOREIGN KEY (projekt_id) REFERENCES Projekt(id) ON DELETE CASCADE
);

CREATE TABLE BramaUchylna (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id INTEGER,
    uklad_wypelnienia TEXT,
    kolor_standardowy TEXT,
    kolor_ral TEXT,
    sposob_otwierania_drzwi TEXT,
    przeszklenia TEXT,
    opcje_dodatkowe TEXT,
    szerokosc INTEGER,
    wysokosc INTEGER,
    FOREIGN KEY (projekt_id) REFERENCES Projekt(id) ON DELETE CASCADE
);
