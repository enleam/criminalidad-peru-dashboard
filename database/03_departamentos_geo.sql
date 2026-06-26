USE CriminalidadPeruDB;
GO

IF OBJECT_ID('analytics.dim_departamento_geo', 'U') IS NOT NULL
BEGIN
    DROP TABLE analytics.dim_departamento_geo;
END
GO

CREATE TABLE analytics.dim_departamento_geo (
    departamento NVARCHAR(100) PRIMARY KEY,
    latitud DECIMAL(10,6) NOT NULL,
    longitud DECIMAL(10,6) NOT NULL
);
GO

INSERT INTO analytics.dim_departamento_geo 
(departamento, latitud, longitud)
VALUES
('AMAZONAS', -5.115146, -78.110827),
('ANCASH', -9.529848, -77.528672),
('ÁNCASH', -9.529848, -77.528672),
('APURIMAC', -13.633333, -72.883333),
('APURÍMAC', -13.633333, -72.883333),
('AREQUIPA', -16.398890, -71.535000),
('AYACUCHO', -13.158780, -74.223210),
('CAJAMARCA', -7.163780, -78.500270),
('CALLAO', -12.056590, -77.118140),
('CUSCO', -13.522640, -71.967340),
('HUANCAVELICA', -12.786389, -74.975556),
('HUANUCO', -9.930620, -76.242230),
('HUÁNUCO', -9.930620, -76.242230),
('ICA', -14.067770, -75.728610),
('JUNIN', -11.158950, -75.993040),
('JUNÍN', -11.158950, -75.993040),
('LA LIBERTAD', -8.111604, -79.028778),
('LAMBAYEQUE', -6.771370, -79.840880),
('LIMA', -12.046374, -77.042793),
('LORETO', -3.749120, -73.253830),
('MADRE DE DIOS', -12.593310, -69.189130),
('MOQUEGUA', -17.193760, -70.935670),
('PASCO', -10.683333, -76.266667),
('PIURA', -5.194490, -80.632820),
('PUNO', -15.840222, -70.021880),
('SAN MARTIN', -6.034160, -76.971680),
('SAN MARTÍN', -6.034160, -76.971680),
('TACNA', -18.014650, -70.253620),
('TUMBES', -3.566940, -80.451530),
('UCAYALI', -8.379150, -74.553870);
GO

IF OBJECT_ID('analytics.vw_mapa_denuncias_departamento', 'V') IS NOT NULL
BEGIN
    DROP VIEW analytics.vw_mapa_denuncias_departamento;
END
GO

CREATE VIEW analytics.vw_mapa_denuncias_departamento AS
SELECT
    f.departamento,
    g.latitud,
    g.longitud,
    SUM(f.cantidad) AS total_denuncias
FROM analytics.fact_denuncias f
INNER JOIN analytics.dim_departamento_geo g
    ON f.departamento = g.departamento
GROUP BY
    f.departamento,
    g.latitud,
    g.longitud;
GO