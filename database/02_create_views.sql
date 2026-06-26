USE CriminalidadPeruDB;
GO

IF OBJECT_ID('analytics.vw_resumen_general', 'V') IS NOT NULL
    DROP VIEW analytics.vw_resumen_general;
GO

CREATE VIEW analytics.vw_resumen_general AS
SELECT
    SUM(cantidad) AS total_denuncias,
    COUNT(*) AS total_registros,
    MIN(anio) AS anio_inicio,
    MAX(anio) AS anio_fin,
    COUNT(DISTINCT departamento) AS total_departamentos,
    COUNT(DISTINCT modalidad) AS total_modalidades
FROM analytics.fact_denuncias;
GO

IF OBJECT_ID('analytics.vw_denuncias_por_anio', 'V') IS NOT NULL
    DROP VIEW analytics.vw_denuncias_por_anio;
GO

CREATE VIEW analytics.vw_denuncias_por_anio AS
SELECT
    anio,
    SUM(cantidad) AS total_denuncias
FROM analytics.fact_denuncias
GROUP BY anio;
GO

IF OBJECT_ID('analytics.vw_denuncias_por_mes', 'V') IS NOT NULL
    DROP VIEW analytics.vw_denuncias_por_mes;
GO

CREATE VIEW analytics.vw_denuncias_por_mes AS
SELECT
    fecha_periodo,
    anio,
    mes,
    SUM(cantidad) AS total_denuncias
FROM analytics.fact_denuncias
GROUP BY fecha_periodo, anio, mes;
GO

IF OBJECT_ID('analytics.vw_denuncias_por_departamento', 'V') IS NOT NULL
    DROP VIEW analytics.vw_denuncias_por_departamento;
GO

CREATE VIEW analytics.vw_denuncias_por_departamento AS
SELECT
    departamento,
    SUM(cantidad) AS total_denuncias
FROM analytics.fact_denuncias
GROUP BY departamento;
GO

IF OBJECT_ID('analytics.vw_denuncias_por_modalidad', 'V') IS NOT NULL
    DROP VIEW analytics.vw_denuncias_por_modalidad;
GO

CREATE VIEW analytics.vw_denuncias_por_modalidad AS
SELECT
    modalidad,
    SUM(cantidad) AS total_denuncias
FROM analytics.fact_denuncias
GROUP BY modalidad;
GO

IF OBJECT_ID('analytics.vw_denuncias_por_provincia', 'V') IS NOT NULL
    DROP VIEW analytics.vw_denuncias_por_provincia;
GO

CREATE VIEW analytics.vw_denuncias_por_provincia AS
SELECT
    departamento,
    provincia,
    SUM(cantidad) AS total_denuncias
FROM analytics.fact_denuncias
GROUP BY departamento, provincia;
GO

IF OBJECT_ID('analytics.vw_denuncias_por_distrito', 'V') IS NOT NULL
    DROP VIEW analytics.vw_denuncias_por_distrito;
GO

CREATE VIEW analytics.vw_denuncias_por_distrito AS
SELECT
    departamento,
    provincia,
    distrito,
    ubigeo,
    SUM(cantidad) AS total_denuncias
FROM analytics.fact_denuncias
GROUP BY departamento, provincia, distrito, ubigeo;
GO