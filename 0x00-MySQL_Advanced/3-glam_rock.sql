-- Active: 1695137323808@@127.0.0.1@3306@holberton
--  SQL script that lists all bands with Glam rock as their main style,
-- ranked by their longevity
-- Requirements:
-- Import this table dump: metal_bands.sql.zip
-- Column names must be: band_name and lifespan (in years until 2022 - use 2022 instead of YEAR(CURDATE()))
-- use attributes formed and split for computing the lifespan

SELECT band_name, (IFNULL(split, 2022) - formed) AS lifespan
FROM metal_bands
WHERE style LIKE '%Glam Rock%'
ORDER BY lifespan DESC;