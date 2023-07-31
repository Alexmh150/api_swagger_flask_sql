-- Question: From the two most commonly appearing regions, which is the latest datasource?
select a.region_name, x.count, x.last_trip_date from dim_region a
inner join (select region_id, count(1) as count, max(datetime) as last_trip_date from trip 
			group by region_id
			order by count desc
			limit 2 ) x on a.region_id = x.region_id