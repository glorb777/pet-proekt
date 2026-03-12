-- создание бд
CREATE DATABASE IF NOT EXISTS university_db;
USE university_db;

-- создание таблиц 
CREATE TABLE `Sotrudniki`(
    `Kod_sotrudnika` INT NOT NULL,
    `Familiya` VARCHAR(50) NOT NULL,
    `Imya` VARCHAR(50) NOT NULL,
    `Otchestvo` VARCHAR(50) NULL,
    `Dolzhnost` VARCHAR(50) NOT NULL,
    `Podrazdelenie` VARCHAR(50) NOT NULL,
    `Telefon` VARCHAR(20) NOT NULL,
    `Email` VARCHAR(50) NULL,
    `Propusk_ID` VARCHAR(20) NULL,
    `Primechanie` TEXT NULL,
    PRIMARY KEY(`Kod_sotrudnika`)
);
ALTER TABLE
    `Sotrudniki` ADD UNIQUE `sotrudniki_propusk_id_unique`(`Propusk_ID`);
CREATE TABLE `Fakultety`(
    `Kod_fakulteta` VARCHAR(10) NOT NULL,
    `Nazvanie` VARCHAR(100) NOT NULL,
    `Dekan` INT NULL,
    PRIMARY KEY(`Kod_fakulteta`)
);
CREATE TABLE `Gruppy`(
    `Kod_gruppy` VARCHAR(10) NOT NULL,
    `Nazvanie` VARCHAR(50) NOT NULL,
    `Kod_fakulteta` VARCHAR(10) NOT NULL,
    `Kurator` INT NULL,
    PRIMARY KEY(`Kod_gruppy`)
);
CREATE TABLE `Kafedry`(
    `Kod_kafedry` VARCHAR(10) NOT NULL,
    `Nazvanie` VARCHAR(100) NOT NULL,
    `Zaveduyushchiy` INT NULL,
    PRIMARY KEY(`Kod_kafedry`)
);
CREATE TABLE `Distsipliny`(
    `Kod_distsipliny` VARCHAR(10) NOT NULL,
    `Naimenovanie` VARCHAR(100) NOT NULL,
    `Kod_kafedry` VARCHAR(10) NOT NULL,
    `Chasy_lektsiy` INT NULL,
    `Chasy_praktiki` INT NULL,
    `Chasy_laboratornykh` INT NULL,
    `Kod_prepodavatelya` INT NULL,
    PRIMARY KEY(`Kod_distsipliny`)
);
CREATE TABLE `Studenty`(
    `Kod_studenta` INT NOT NULL,
    `Familiya` VARCHAR(50) NOT NULL,
    `Imya` VARCHAR(50) NOT NULL,
    `Otchestvo` VARCHAR(50) NULL,
    `Data_rozhdeniya` DATE NOT NULL,
    `Pasportnye_dannye` VARCHAR(20) NOT NULL,
    `Adres` VARCHAR(200) NOT NULL,
    `Telefon` VARCHAR(20) NOT NULL,
    `Email` VARCHAR(50) NULL,
    `Data_zachisleniya` DATE NOT NULL,
    `Nomer_prikaza` VARCHAR(20) NOT NULL,
    `Kod_gruppy` VARCHAR(10) NULL,
    `Fakultet` VARCHAR(100) NULL,
    PRIMARY KEY(`Kod_studenta`)
);
CREATE TABLE `Ekzamens`(
    `Kod_zapisi` INT NOT NULL,
    `Kod_studenta` INT NOT NULL,
    `Kod_distsipliny` VARCHAR(10) NOT NULL,
    `Data_ekzamena` DATE NOT NULL,
    `Ocenka` VARCHAR(10) NOT NULL,
    `Podpis_prepodavatelya` VARCHAR(100) NOT NULL,
    PRIMARY KEY(`Kod_zapisi`)
);
CREATE TABLE `Propuski`(
    `Kod_propyska` VARCHAR(20) NOT NULL,
    `Kod_sotrudnika` INT NOT NULL,
    `Data_vydachi` DATE NOT NULL,
    `Data_okonchaniya` DATE NOT NULL,
    `Primechanie` TEXT NULL,
    PRIMARY KEY(`Kod_propyska`)
);
CREATE TABLE Stat_Log (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Stat_Type VARCHAR(100) NOT NULL,
    Value DECIMAL(10, 2),
    Log_Date DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE Employee_Counter (
    id INT PRIMARY KEY,
    Total_Employees INT NOT NULL
);
ALTER TABLE
    `Studenty` ADD CONSTRAINT `studenty_kod_gruppy_foreign` FOREIGN KEY(`Kod_gruppy`) REFERENCES `Gruppy`(`Kod_gruppy`);
ALTER TABLE
    `Distsipliny` ADD CONSTRAINT `distsipliny_kod_prepodavatelya_foreign` FOREIGN KEY(`Kod_prepodavatelya`) REFERENCES `Sotrudniki`(`Kod_sotrudnika`);
ALTER TABLE
    `Propuski` ADD CONSTRAINT `propuski_kod_sotrudnika_foreign` FOREIGN KEY(`Kod_sotrudnika`) REFERENCES `Sotrudniki`(`Kod_sotrudnika`);
ALTER TABLE
    `Fakultety` ADD CONSTRAINT `fakultety_dekan_foreign` FOREIGN KEY(`Dekan`) REFERENCES `Sotrudniki`(`Kod_sotrudnika`);
ALTER TABLE
    `Ekzamens` ADD CONSTRAINT `ekzamens_kod_studenta_foreign` FOREIGN KEY(`Kod_studenta`) REFERENCES `Studenty`(`Kod_studenta`);
ALTER TABLE
    `Distsipliny` ADD CONSTRAINT `distsipliny_kod_kafedry_foreign` FOREIGN KEY(`Kod_kafedry`) REFERENCES `Kafedry`(`Kod_kafedry`);
ALTER TABLE
    `Ekzamens` ADD CONSTRAINT `ekzamens_kod_distsipliny_foreign` FOREIGN KEY(`Kod_distsipliny`) REFERENCES `Distsipliny`(`Kod_distsipliny`);
ALTER TABLE
    `Gruppy` ADD CONSTRAINT `gruppy_kod_fakulteta_foreign` FOREIGN KEY(`Kod_fakulteta`) REFERENCES `Fakultety`(`Kod_fakulteta`);

-- Вставка двнных
INSERT INTO Sotrudniki (Kod_sotrudnika, Familiya, Imya, Otchestvo, Dolzhnost, Podrazdelenie, Telefon, Email, Propusk_ID) VALUES
(101, 'Иванов', 'Петр', 'Сергеевич', 'Профессор', 'Кафедра ИТ', '123-456-7890', 'ivanov@uni.edu', 'S001'),
(102, 'Смирнова', 'Анна', 'Олеговна', 'Декан', 'Факультет ФИИТ', '987-654-3210', 'smirnova@uni.edu', 'S002'),
(103, 'Кузнецов', 'Дмитрий', 'Андреевич', 'Заведующий кафедрой', 'Кафедра ИТ', '555-123-4567', 'kuznetsov@uni.edu', 'S003');

INSERT INTO Fakultety (Kod_fakulteta, Nazvanie, Dekan) VALUES
('FIIT', 'Факультет информационных технологий', 102),
('FEST', 'Факультет экономики и статистики', NULL);

INSERT INTO Kafedry (Kod_kafedry, Nazvanie, Zaveduyushchiy) VALUES
('IT', 'Информационные технологии', 103),
('MAT', 'Высшая математика', NULL);

INSERT INTO Gruppy (Kod_gruppy, Nazvanie, Kod_fakulteta, Kurator) VALUES
('IT-201', 'ИТ-201', 'FIIT', 101),
('ES-101', 'ЭС-101', 'FEST', NULL);

INSERT INTO Distsipliny (Kod_distsipliny, Naimenovanie, Kod_kafedry, Chasy_lektsiy, Chasy_praktiki, Chasy_laboratornykh, Kod_prepodavatelya) VALUES
('DB-001', 'Базы данных', 'IT', 32, 16, 16, 101),
('ALGEBRA', 'Линейная алгебра', 'MAT', 48, 32, 0, NULL);

INSERT INTO Studenty (Kod_studenta, Familiya, Imya, Otchestvo, Data_rozhdeniya, Pasportnye_dannye, Adres, Telefon, Email, Data_zachisleniya, Nomer_prikaza, Kod_gruppy, Fakultet) VALUES
(2001, 'Алексеев', 'Иван', 'Григорьевич', '2004-05-15', '1234 567890', 'г. Москва, ул. Ленина, д. 1', '900-111-2233', 'alekseev@mail.ru', '2023-09-01', 'P-23-001', 'IT-201', 'Факультет информационных технологий'),
(2002, 'Васильева', 'Мария', 'Николаевна', '2003-11-20', '5678 901234', 'г. Москва, пр. Мира, д. 5', '900-333-4455', 'vasilieva@mail.ru', '2023-09-01', 'P-23-001', 'IT-201', 'Факультет информационных технологий');

INSERT INTO Ekzamens (Kod_studenta, Kod_distsipliny, Data_ekzamena, Ocenka, Podpis_prepodavatelya) VALUES
(2001, 'DB-001', '2024-01-15', 'Отлично', 'Иванов П.С.'),
(2002, 'DB-001', '2024-01-15', 'Хорошо', 'Иванов П.С.');

INSERT INTO Propuski (Kod_propyska, Kod_sotrudnika, Data_vydachi, Data_okonchaniya) VALUES
('P-S001', 101, '2023-01-01', '2024-12-31'),
('P-S002', 102, '2023-01-01', '2025-12-31');

-- обновление записей
UPDATE Kafedry
SET Zaveduyushchiy = 101 
WHERE Kod_kafedry = 'MAT';

UPDATE Sotrudniki
SET Dolzhnost = 'Старший научный сотрудник'
WHERE Kod_sotrudnika = 103;

UPDATE Ekzamens
SET Ocenka = 'Отлично'
WHERE Kod_studenta = 2002 AND Kod_distsipliny = 'DB-001';

-- удаление записей

DELETE FROM Propuski
WHERE Kod_propyska = 'P-S001';

DELETE FROM Ekzamens WHERE Kod_studenta = 2001;

DELETE FROM Studenty
WHERE Kod_studenta = 2001;


-- Создание пользователей и наделение их правами

CREATE USER 'dek_user'@'localhost' IDENTIFIED BY 'password123';

GRANT SELECT ON university_db.Studenty TO 'dek_user'@'localhost';
GRANT SELECT ON university_db.Gruppy TO 'dek_user'@'localhost';
GRANT SELECT ON university_db.Fakultety TO 'dek_user'@'localhost';
GRANT SELECT ON university_db.Distsipliny TO 'dek_user'@'localhost';

CREATE USER 'hr_user'@'localhost' IDENTIFIED BY 'password456';
GRANT SELECT, INSERT, UPDATE, DELETE ON university_db.Sotrudniki TO 'hr_user'@'localhost';


-- 2 Часть 

-- Запрос на соеденение таблиц
SELECT
    Studenty.Familiya,
    Studenty.Imya,
    Studenty.Otchestvo,
    Gruppy.Nazvanie AS Nazvanie_gruppy,
    Fakultety.Nazvanie AS Nazvanie_fakulteta 
FROM
    Studenty
JOIN
    Gruppy ON Studenty.Kod_gruppy = Gruppy.Kod_gruppy
JOIN
    Fakultety ON Gruppy.Kod_fakulteta = Fakultety.Kod_fakulteta; 
    
-- агрегирующие операции

SELECT
    AVG(Chasy_lektsiy) AS Srednee_chasy_lektsiy,
    COUNT(Kod_distsipliny) AS Kolichestvo_distsiplin, 
    SUM(Chasy_praktiki) AS Summa_chasy_praktiki
FROM
    Distsipliny;

-- группировку (GROUP BY) и сортировку (ORDER BY)

SELECT
    Dolzhnost,
    COUNT(Kod_sotrudnika) AS Kolichestvo_sotrudnikov
FROM
    Sotrudniki
GROUP BY
    Dolzhnost 
ORDER BY
    Kolichestvo_sotrudnikov DESC;

-- вложенные подзапросы

SELECT
    Familiya,
    Imya,
    Dolzhnost
FROM
    Sotrudniki
WHERE
    Kod_sotrudnika IN (
        SELECT
            Dekan
        FROM
            Fakultety
        WHERE
            Dekan IS NOT NULL 
    );

--  на использование «функций управления потоком» (IF, CASE).создание одного представления на наиболее популярный запрос (CREATE VIEW)

SELECT
    Familiya,
    Imya,
    Dolzhnost,
    CASE
        WHEN Dolzhnost = 'Профессор' THEN 'Высший состав' 
        WHEN Dolzhnost LIKE '%Заведующий%' THEN 'Руководящий состав'
        ELSE 'Прочий персонал'
    END AS Kategoriya_sotrudnika
FROM
    Sotrudniki
WHERE
    Dolzhnost IN ('Профессор', 'Заведующий кафедрой', 'Старший научный сотрудник');

-- CREATE VIEW

CREATE VIEW View_Students_Info AS
SELECT
    s.Kod_studenta,
    s.Familiya,
    s.Imya,
    g.Nazvanie AS Nazvanie_gruppy,
    f.Nazvanie AS Nazvanie_fakulteta
FROM
    Studenty s
JOIN
    Gruppy g ON s.Kod_gruppy = g.Kod_gruppy
JOIN
    Fakultety f ON g.Kod_fakulteta = f.Kod_fakulteta;

SELECT * FROM View_Students_Info;

-- 3-1

CREATE PROCEDURE calculate_discipline_stats()
BEGIN
    INSERT INTO Stat_Log (Stat_Type, Value)
        SELECT 'Среднее ', AVG(Chasy_lektsiy) FROM Distsipliny
        UNION ALL
        SELECT 'Сумма ', SUM(Chasy_lektsiy) FROM Distsipliny
        UNION ALL
        SELECT 'Максимум ', MAX(Chasy_lektsiy) FROM Distsipliny
        UNION ALL
        SELECT 'Минимум ', MIN(Chasy_lektsiy) FROM Distsipliny;
END;

-- 3-2 

CREATE FUNCTION s_c_position (position_name VARCHAR(50))
    RETURNS INT
    DETERMINISTIC
BEGIN 
    DECLARE count INT;
    SELECT COUNT(Kod_sotrudnika) INTO count 
    FROM Sotrudniki WHERE Dolzhnost = position_name;
    RETURN count;
END;

-- 3-3 

INSERT INTO Employee_Counter (id, Total_E)
SELECT 1, COUNT(*) FROM Sotrudniki;

CREATE TRIGGER trg_sotrudniki_after
AFTER INSERT ON Sotrudniki
FOR EACH ROW
BEGIN
    UPDATE Employee_Counter
    SET Total_E = Total_E + 1
    WHERE id = 1;
END;

CREATE TRIGGER trg_delete_sotrudniki
AFTER DELETE ON Sotrudniki
FOR EACH ROW
BEGIN
    UPDATE Employee_Counter
    SET Total_E = Total_E - 1
    WHERE id = 1;
END;
