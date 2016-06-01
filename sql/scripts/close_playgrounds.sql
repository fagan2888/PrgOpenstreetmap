SELECT A.id,
       B.value AS playground,
       A.lt,
       A.ln,
       distance(A.lt, A.ln, TRG_LAT, TRG_LON) AS dist
FROM
  (SELECT wt.id,
          avg(n.lat) AS lt,
                        avg(n.lon) AS ln
   FROM ways w
   INNER JOIN
     (SELECT wn.id,
             n.lat,
             n.lon
      FROM ways_nodes wn
      INNER JOIN nodes n ON (wn.node_id = n.id) ) AS n ON (w.id = n.id)
   INNER JOIN ways_tags wt ON (w.id = wt.id
                               AND n.id=wt.id)
   WHERE wt.key="leisure"
     AND wt.value="playground"
   GROUP BY wt.id) A
LEFT JOIN ways_tags B ON (A.id = B.id
                          AND B.key="name")
ORDER BY dist LIMIT LIMIT_THRSH