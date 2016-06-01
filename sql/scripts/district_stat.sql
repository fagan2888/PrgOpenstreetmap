SELECT PC.code,
       R.count_rest,
       P.count_bars,
       S.count_supermarkets,
       T.count_tourist
FROM
  (SELECT DISTINCT substr(value, 1, 2) AS code
   FROM nodes_tags
   WHERE KEY = "postcode"
     AND substr(value,1,1)="1" ) PC
LEFT JOIN
  (SELECT substr(nt1.value,1,2) AS code,
                                   count(*) AS count_rest
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   INNER JOIN nodes_tags nt1 ON (n.id = nt1.id)
   WHERE nt.KEY = "amenity"
     AND nt.value = "restaurant"
     AND nt1.KEY="postcode"
   GROUP BY code ) R ON (PC.code = R.code)
LEFT JOIN
  (SELECT substr(nt1.value,1,2) AS code,
                                   count(*) AS count_bars
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   INNER JOIN nodes_tags nt1 ON (n.id = nt1.id)
   WHERE nt.KEY = "amenity"
     AND (nt.value = "pub"
          OR nt.value="bar")
     AND nt1.KEY="postcode"
   GROUP BY code ) P ON (PC.code = P.code)
LEFT JOIN
  (SELECT substr(nt1.value,1,2) AS code,
                                   count(*) AS count_supermarkets
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   INNER JOIN nodes_tags nt1 ON (n.id = nt1.id)
   WHERE nt.KEY = "shop"
     AND nt.value = "supermarket"
     AND nt1.KEY="postcode"
   GROUP BY code ) S ON (PC.code = S.code)
LEFT JOIN
  (SELECT substr(nt1.value,1,2) AS code,
                                   count(*) AS count_tourist
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   INNER JOIN nodes_tags nt1 ON (n.id = nt1.id)
   WHERE nt.KEY = "tourism"
     AND nt1.KEY="postcode"
   GROUP BY code ) T ON (PC.code = T.code)