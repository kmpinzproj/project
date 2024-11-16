-- Tworzenie tabeli: project
CREATE TABLE project (
    id INTEGER PRIMARY KEY, -- SQLite traktuje INTEGER PRIMARY KEY jako auto-increment
    name TEXT NOT NULL,
    save_time DATETIME NOT NULL,
    gate_type TEXT NOT NULL
);

-- Tworzenie tabeli: project_main
CREATE TABLE project_main (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    color TEXT,
    height REAL,
    width REAL,
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- Tworzenie tabeli: gate_segment
CREATE TABLE gate_segment (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    surface_pattern TEXT,
    surface_structure TEXT,
    opening_method TEXT,
    bolt INTEGER, -- Zastąpienie BOOLEAN przez INTEGER (0 lub 1)
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- Tworzenie tabeli: gate_roller
CREATE TABLE gate_roller (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    opening_method TEXT,
    glass_inserts INTEGER, -- Zastąpienie BOOLEAN przez INTEGER (0 lub 1)
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- Tworzenie tabeli: gate_casement
CREATE TABLE gate_casement (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    wing_count INTEGER,
    insulation INTEGER, -- Zastąpienie BOOLEAN przez INTEGER (0 lub 1)
    filling TEXT,
    windows TEXT,
    additional_options TEXT,
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- Tworzenie tabeli: gate_tilt
CREATE TABLE gate_tilt (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    filling TEXT,
    opening_method TEXT,
    windows TEXT,
    extra_doors INTEGER, -- Zastąpienie BOOLEAN przez INTEGER (0 lub 1)
    additional_options TEXT,
    FOREIGN KEY (project_id) REFERENCES project(id)
);
