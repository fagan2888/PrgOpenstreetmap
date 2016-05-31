closest_veg_restaurants = """
	select N1.id, N1.value as rest_name, N2.value as addr_street, N3.value as addr_hsnumber, N4.value as rest_phone, distance(B.lat, B.lon, TRG_LAT, TRG_LON) as dist
	from
	nodes_tags N1  
	    inner join  
	    (select n.id, n.lat, n.lon
	    from
	    nodes n inner join nodes_tags nt on (n.id = nt.id)
	    where nt.key = "cuisine"
	    and (nt.value like "%vegetarian%" or nt.value like "%vegan_food%" 
	        or nt.value like "%vegan%")
	    ) B on (N1.id = B.id)
	    left join nodes_tags N2 on (N1.id = N2.id and N2.key="street")
	    left join nodes_tags N3 on (N1.id = N3.id and N3.key="housenumber")
	    left join nodes_tags N4 on (N1.id = N4.id and N4.key="phone")

	where N1.key = "name"

	order by dist

	limit LIMIT_THRSH

"""

close_playgrounds = """
	select A.id, B.value as playground, A.lt, A.ln, distance(A.lt, A.ln, TRG_LAT, TRG_LON) as dist
	from 
	(select wt.id, avg(n.lat) as lt, avg(n.lon) as ln
	from 
	ways w inner join 
	    (select wn.id, n.lat, n.lon
	    from ways_nodes wn 
	        inner join nodes n on (wn.node_id = n.id)
	    ) as n on (w.id = n.id)
	    inner join ways_tags wt on (w.id = wt.id and n.id=wt.id)
	where
	wt.key="leisure"
	and wt.value="playground"
	group by wt.id) A
	left join ways_tags B on (A.id = B.id and B.key="name")
	order by dist

	limit LIMIT_THRSH

"""

