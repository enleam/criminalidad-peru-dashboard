IF DB_ID('CriminalidadPeruDB') IS NULL
BEGIN
    CREATE DATABASE CriminalidadPeruDB;
END
GO

USE CriminalidadPeruDB;
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'analytics')
BEGIN
    EXEC('CREATE SCHEMA analytics');
END
GO

IF OBJECT_ID('analytics.fact_denuncias', 'U') IS NOT NULL
BEGIN
    DROP TABLE analytics.fact_denuncias;
END
GO

CREATE TABLE analytics.fact_denuncias (
    denuncia_id BIGINT IDENTITY(1,1) PRIMARY KEY,

    anio SMALLINT NOT NULL,
    mes TINYINT NOT NULL,
    fecha_periodo DATE NOT NULL,

    departamento NVARCHAR(100) NOT NULL,
    provincia NVARCHAR(100) NULL,
    distrito NVARCHAR(100) NULL,
    ubigeo CHAR(6) NULL,

    modalidad NVARCHAR(250) NOT NULL,
    cantidad INT NOT NULL,

    fuente NVARCHAR(150) NOT NULL DEFAULT 'MININTER - SIDPOL',
    fecha_carga DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO

CREATE INDEX IX_fact_denuncias_periodo
ON analytics.fact_denuncias(anio, mes);
GO

CREATE INDEX IX_fact_denuncias_departamento
ON analytics.fact_denuncias(departamento);
GO

CREATE INDEX IX_fact_denuncias_modalidad
ON analytics.fact_denuncias(modalidad);
GO