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
    kratka_wentylacyjna TEXT,
    klamka_do_bramy TEXT,
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
    kratka_wentylacyjna TEXT,
    klamka_do_bramy TEXT,
    szerokosc INTEGER,
    wysokosc INTEGER,
    FOREIGN KEY (projekt_id) REFERENCES Projekt(id) ON DELETE CASCADE
);

CREATE TABLE Cennik (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    typ_bramy TEXT NOT NULL,
    parametr TEXT NOT NULL,
    opcja TEXT NOT NULL,
    doplata INTEGER NOT NULL
);

-- Cena bazowa
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES ('Brama Segmentowa', 'Bazowa', 'Cena', 2500);

-- Parametry i dopłaty
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES
('Brama Segmentowa', 'Rodzaj przetłoczenia', 'Bez przetłoczenia', 0),
('Brama Segmentowa', 'Rodzaj przetłoczenia', 'Średnie', 100),
('Brama Segmentowa', 'Rodzaj przetłoczenia', 'Niskie', 150),
('Brama Segmentowa', 'Rodzaj przetłoczenia', 'Kasetony', 200),

('Brama Segmentowa', 'Struktura powierzchni', 'Silkgrain', 0),
('Brama Segmentowa', 'Struktura powierzchni', 'Woodgrain', 150),
('Brama Segmentowa', 'Struktura powierzchni', 'Smoothgrain', 200),

('Brama Segmentowa', 'Kolor', 'Biały', 0),
('Brama Segmentowa', 'Kolor', 'RAL', 200),

('Brama Segmentowa', 'Przeszklenia', 'Wzór 1', 300),
('Brama Segmentowa', 'Przeszklenia', 'Wzór 2', 350),
('Brama Segmentowa', 'Przeszklenia', 'Wzór 3', 400),

('Brama Segmentowa', 'Klamka do bramy', 'Klamka 1', 50),
('Brama Segmentowa', 'Klamka do bramy', 'Klamka 2', 70),
('Brama Segmentowa', 'Klamka do bramy', 'Klamka 3', 100),
('Brama Segmentowa', 'Klamka do bramy', 'Klamka 4', 150),

('Brama Segmentowa', 'Sposób otwierania drzwi', 'Ręczne', 0),
('Brama Segmentowa', 'Sposób otwierania drzwi', 'Automatyczne', 700),

('Brama Segmentowa', 'Kratka wentylacyjna', 'Lewa', 100),
('Brama Segmentowa', 'Kratka wentylacyjna', 'Prawa', 100),
('Brama Segmentowa', 'Kratka wentylacyjna', 'Obustronna', 200),

('Brama Segmentowa', 'Opcje dodatkowe', 'Drzwi w bramie', 1000),
('Brama Segmentowa', 'Opcje dodatkowe', 'Samozamykacz', 500),
('Brama Segmentowa', 'Opcje dodatkowe', 'Zamykane ręcznie', 200),
('Brama Segmentowa', 'Opcje dodatkowe', 'Rygiel', 150);



-- Cena bazowa
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES ('Brama Roletowa', 'Bazowa', 'Cena', 3000);

-- Parametry i dopłaty
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES
('Brama Roletowa', 'Wysokość profili', '77 mm', 0),
('Brama Roletowa', 'Wysokość profili', '100 mm', 250),

('Brama Roletowa', 'Kolor', 'Biały', 0),
('Brama Roletowa', 'Kolor', 'RAL', 200),

('Brama Roletowa', 'Przeszklenia', 'Wzór 4', 400),

('Brama Roletowa', 'Sposób otwierania bramy', 'Automatyczne (kluczyk)', 700),
('Brama Roletowa', 'Sposób otwierania bramy', 'Zdalne sterowanie', 1000),
('Brama Roletowa', 'Sposób otwierania bramy', 'Fotokomórka', 500),

('Brama Roletowa', 'Kratka wentylacyjna', 'Lewa', 100),
('Brama Roletowa', 'Kratka wentylacyjna', 'Prawa', 100),
('Brama Roletowa', 'Kratka wentylacyjna', 'Obustronna', 200);


-- Cena bazowa
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES ('Brama Rozwierana', 'Bazowa', 'Cena', 2000);

-- Parametry i dopłaty
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES
('Brama Rozwierana', 'Ilość skrzydeł', 'Dwuskrzydłowe', 0),
('Brama Rozwierana', 'Ilość skrzydeł', 'Jednoskrzydłowe prawe', 200),
('Brama Rozwierana', 'Ilość skrzydeł', 'Jednoskrzydłowe lewe', 200),

('Brama Rozwierana', 'Układ wypełnienia', 'Poziome', 0),
('Brama Rozwierana', 'Układ wypełnienia', 'Pionowe', 100),
('Brama Rozwierana', 'Układ wypełnienia', 'Jodełka w górę', 150),

('Brama Rozwierana', 'Kolor', 'Biały', 100),
('Brama Rozwierana', 'Kolor', 'RAL', 200),

('Brama Rozwierana', 'Przeszklenia', 'Okna poziome', 300),
('Brama Rozwierana', 'Przeszklenia', 'Okna pionowe', 400),

('Brama Rozwierana', 'Opcje dodatkowe', 'Rygiel trzypunktowy', 300),
('Brama Rozwierana', 'Opcje dodatkowe', 'Dodatkowe zamknięcie na kłódkę', 200);

-- Klamka do bramy (Brama Rozwierana)
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES
('Brama Rozwierana', 'Klamka do bramy', 'Klamka 1', 50),
('Brama Rozwierana', 'Klamka do bramy', 'Klamka 2', 70),
('Brama Rozwierana', 'Klamka do bramy', 'Klamka 3', 100),
('Brama Rozwierana', 'Klamka do bramy', 'Klamka 4', 150);

-- Kratka wentylacyjna (Brama Rozwierana)
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES
('Brama Rozwierana', 'Kratka wentylacyjna', 'Lewa', 100),
('Brama Rozwierana', 'Kratka wentylacyjna', 'Prawa', 100),
('Brama Rozwierana', 'Kratka wentylacyjna', 'Obustronna', 200);

-- Cena bazowa
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES ('Brama Uchylna', 'Bazowa', 'Cena', 1500);

-- Parametry i dopłaty
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES
('Brama Uchylna', 'Układ wypełnienia', 'Pionowe', 0),
('Brama Uchylna', 'Układ wypełnienia', 'Poziome', 100),
('Brama Uchylna', 'Układ wypełnienia', 'Jodełka w górę', 150),

('Brama Uchylna', 'Kolor', 'Biały', 0),
('Brama Uchylna', 'Kolor', 'RAL', 200),

('Brama Uchylna', 'Przeszklenia', 'Okna poziome', 300),
('Brama Uchylna', 'Przeszklenia', 'Okna pionowe', 400),

('Brama Uchylna', 'Sposób otwierania drzwi', 'Ręczne', 0),
('Brama Uchylna', 'Sposób otwierania drzwi', 'Automatyczne', 700),

('Brama Uchylna', 'Kratka wentylacyjna', 'Lewa', 100),
('Brama Uchylna', 'Kratka wentylacyjna', 'Prawa', 100),
('Brama Uchylna', 'Kratka wentylacyjna', 'Obustronna', 200),

('Brama Uchylna', 'Opcje dodatkowe', 'Rygiel trzypunktowy', 300),
('Brama Uchylna', 'Opcje dodatkowe', 'Dodatkowy rygiel', 150),
('Brama Uchylna', 'Opcje dodatkowe', 'Drzwi przejściowe', 500);

-- Klamka do bramy (Brama Uchylna)
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES
('Brama Uchylna', 'Klamka do bramy', 'Klamka 1', 50),
('Brama Uchylna', 'Klamka do bramy', 'Klamka 2', 70),
('Brama Uchylna', 'Klamka do bramy', 'Klamka 3', 100),
('Brama Uchylna', 'Klamka do bramy', 'Klamka 4', 150);

-- Kratka wentylacyjna (Brama Uchylna)
INSERT INTO CENNIK (typ_bramy, parametr, opcja, doplata) VALUES
('Brama Uchylna', 'Kratka wentylacyjna', 'Lewa', 100),
('Brama Uchylna', 'Kratka wentylacyjna', 'Prawa', 100),
('Brama Uchylna', 'Kratka wentylacyjna', 'Obustronna', 200);
