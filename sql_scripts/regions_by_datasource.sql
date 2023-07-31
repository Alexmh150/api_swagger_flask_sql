-- Question:  What regions has the "cheap_mobile" datasource appeared in?
declare @region_name varchar(50) = 'cheap_mobile'
select
    distinct 
c.* from trip a
inner join dim_region c on a.region_id = c.region_id
inner join dim_datasource b on a.datasource_id = b.datasource_id
where b.datasource_name = @region_name