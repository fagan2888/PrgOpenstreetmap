SELECT N1.id,
       N1.value AS rest_name,
       N2.value AS addr_street,
       N3.value AS addr_hsnumber,
       N4.value AS rest_phone,
       distance(B.lat, B.lon, TRG_LAT, TRG_LON) AS dist
FROM nodes_tags N1
INNER JOIN
  (SELECT n.id,
          n.lat,
          n.lon
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   WHERE nt.key = "cuisine"
     AND (nt.value LIKE "%vegetarian%"
          OR nt.value LIKE "%vegan_food%"
          OR nt.value LIKE "%vegan%") ) B ON (N1.id = B.id)
LEFT JOIN nodes_tags N2 ON (N1.id = N2.id
                            AND N2.key="street")
LEFT JOIN nodes_tags N3 ON (N1.id = N3.id
                            AND N3.key="housenumber")
LEFT JOIN nodes_tags N4 ON (N1.id = N4.id
                            AND N4.key="phone")
WHERE N1.key = "name"
ORDER BY dist LIMIT LIMIT_THRSH