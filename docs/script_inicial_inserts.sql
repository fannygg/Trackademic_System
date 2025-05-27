-- Inserts
-- Project: Trackademic
-- Fanny Giraldo
-- Oscar Suarez

INSERT INTO COUNTRIES (code, name) VALUES
(1, 'Colombia'),
(2, 'Ecuador'),
(3, 'Perú'),
(4, 'Brasil'),
(5, 'Argentina');


INSERT INTO CONTRACT_TYPES (name) VALUES
('Tiempo completo'),
('Cátedra'),
('Medio tiempo'),
('Honorarios'),
('Interinidad');

INSERT INTO EMPLOYEE_TYPES (name) VALUES
('Docente'),
('Investigador'),
('Administrativo'),
('Decano'),
('Coordinador');

INSERT INTO DEPARTMENTS (code, name, country_code) VALUES
(10, 'Valle del Cauca', 1),
(11, 'Antioquia', 1),
(12, 'Cundinamarca', 1),
(13, 'Guayas', 2),
(14, 'Lima', 3);

INSERT INTO CITIES (code, name, dept_code) VALUES
(100, 'Cali', 10),
(101, 'Medellín', 11),
(102, 'Bogotá', 12),
(103, 'Guayaquil', 13),
(104, 'Lima', 14);


INSERT INTO FACULTIES (code, name, location, phone_number, dean_id) VALUES
(1, 'Ingeniería', 'Edificio C', '6025551234', NULL),
(2, 'Ciencias Sociales', 'Edificio E', '6025552345', NULL),
(3, 'Ciencias Económicas', 'Edificio F', '6025553456', NULL),
(4, 'Ciencias Políticas', 'Edificio H', '6025554567', NULL),
(5, 'Ciencias de la Salud', 'Edificio G', '6025555678', NULL);

INSERT INTO CAMPUSES (code, name, city_code) VALUES
(1, 'Campus Cali', 100),
(2, 'Centro Bogotá', 102),
(3, 'Campus Medellín', 101),
(4, 'Extensión Guayaquil', 103),
(5, 'Sede Lima', 104);

INSERT INTO EMPLOYEES (
    id, first_name, last_name, email, contract_type, employee_type, 
    faculty_code, campus_code, birth_place_code
) VALUES
('icesi101', 'Carlos', 'Ramírez', 'c.ramirez@icesi.edu.co', 'Cátedra', 'Docente', 1, 1, 100),
('icesi102', 'Mónica', 'Rojas', 'm.rojas@icesi.edu.co', 'Tiempo completo', 'Docente', 1, 1, 100),
('icesi103', 'Ana', 'López', 'a.lopez@icesi.edu.co', 'Medio tiempo', 'Investigador', 2, 2, 102),
('icesi104', 'Julián', 'Mejía', 'j.mejia@icesi.edu.co', 'Tiempo completo', 'Docente', 3, 1, 101),
('icesi105', 'Laura', 'Cárdenas', 'l.cardenas@icesi.edu.co', 'Honorarios', 'Administrativo', 4, 3, 101);

INSERT INTO AREAS (code, name, faculty_code, coordinator_id) VALUES
(1, 'Sistemas', 1, 'icesi101'),
(2, 'Industrial', 1, 'icesi102'),
(3, 'Psicología', 2, 'icesi103'),
(4, 'Economía', 3, 'icesi104'),
(5, 'Derecho', 4, 'icesi105');

INSERT INTO PROGRAMS (code, name, area_code) VALUES
(101, 'Ingeniería de Sistemas', 1),
(102, 'Ingeniería Industrial', 2),
(103, 'Psicología Clínica', 3),
(104, 'Economía Aplicada', 4),
(105, 'Derecho Corporativo', 5);

INSERT INTO SUBJECTS (code, name, program_code) VALUES
('IS301', 'Bases de Datos', 101),
('IS302', 'Desarrollo Web', 101),
('II201', 'Optimización', 102),
('PS101', 'Neuropsicología', 103),
('EC101', 'Microeconomía', 104);

INSERT INTO GROUPS (number, semester, subject_code, professor_id) VALUES
(1, '2024-1', 'IS301', 'icesi101'),
(1, '2024-1', 'IS302', 'icesi102'),
(1, '2024-1', 'II201', 'icesi102'),
(1, '2024-1', 'PS101', 'icesi103'),
(1, '2024-1', 'EC101', 'icesi104');