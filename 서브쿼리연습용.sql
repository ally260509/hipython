USE wntrade;

select 고객번호, 고객회사명, 담당자명, 마일리지
from 고객
where 마일리지 = (
	select max(마일리지)
    from 고객
    );
    
select 고객번호, 고객회사명, 담당자명, 마일리지
from 고객
join (
	select max(마일리지) as max_mileage
    from 고객
) m
on 마일리지 = m.max_mileage;

select 고객번호, 고객회사명, 담당자명, 마일리지
from 고객
order by 마일리지 desc
limit 1;

select 고객회사명, 담당자명
from 고객
join 주문
on 고객.고객번호 = 주문.고객번호
where 주문번호 = 'H0250';

select 고객회사명, 담당자명
from 고객
where 고객번호 = (
	select 고객번호
    from 주문
    where 주문번호 = 'H0250'
    );
    
select 고객회사명, 담당자명, 마일리지
from 고객
where 마일리지 > (
	select min(마일리지)
    from 고객
    where 도시 = '부산광역시'
    );
