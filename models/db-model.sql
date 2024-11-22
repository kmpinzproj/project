CREATE TABLE Projekt (
    id INTEGER PRIMARY KEY, -- SQLite traktuje INTEGER PRIMARY KEY jako auto-increment
    nazwa TEXT NOT NULL UNIQUE, -- Nazwa projektu musi być unikalna
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
    szerokosc INTEGER, -- Dodano szerokość bramy
    wysokosc INTEGER,  -- Dodano wysokość bramy
    FOREIGN KEY (projekt_id) REFERENCES Projekt(id)
);

CREATE TABLE BramaRoletowa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id INTEGER,
    wysokosc_profili INTEGER,
    kolor_standardowy TEXT,
    kolor_ral TEXT,
    sposob_otwierania_bramy TEXT,
    przeszklenia TEXT,
    szerokosc INTEGER, -- Dodano szerokość bramy
    wysokosc INTEGER,  -- Dodano wysokość bramy
    FOREIGN KEY (projekt_id) REFERENCES Projekt(id)
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
    szerokosc INTEGER, -- Dodano szerokość bramy
    wysokosc INTEGER,  -- Dodano wysokość bramy
    FOREIGN KEY (projekt_id) REFERENCES Projekt(id)
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
    szerokosc INTEGER, -- Dodano szerokość bramy
    wysokosc INTEGER,  -- Dodano wysokość bramy
    FOREIGN KEY (projekt_id) REFERENCES Projekt(id)
);
