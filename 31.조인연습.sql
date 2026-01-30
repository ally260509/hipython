USE WNTRADE;

-- CROSS JOIN > INNER JOIN

SELECT 부서.부서번호 AS 부서부서번호, 사원.부서번호 AS 사원부서번호, 이름, 부서명
FROM 부서
CROSS JOIN 사원
ON 부서.부서번호 = 사원.부서번호
WHERE 이름 = '배재용';

-- 주문, 고객 INNER JOIN
SELECT 주문번호, 고객회사명, 주문일
FROM 주문 JOIN 고객
ON 주문.고객번호 = 고객.고객번호
WHERE 주문.고객번호 = 'ITCWH';

-- 주문, 사원 INNER JOIN 주문번호별 담당자
SELECT 주문번호, 주문.사원번호, 고객번호, 사원.이름
FROM 주문 JOIN 사원
ON 주문.사원번호 = 사원.사원번호;

-- 고객, 제품 > 크로스조인 -> 기준 세울 때 많이 함(모든 경우의 수 다 볼 때)
SELECT 고객회사명, 제품명
FROM 고객 JOIN 제품;

-- 고객, 마일리지등급

SELECT 고객.고객회사명, 고객.마일리지, 마일리지등급.등급명
FROM 고객 JOIN 마일리지등급
ON 고객.마일리지 BETWEEN 마일리지등급.하한마일리지 AND 마일리지등급.상한마일리지;