USE WNTRADE;

SELECT
	도시, 
    COUNT(*) AS 고객수,
    AVG(마일리지) AS 평균마일리지
FROM 고객
WHERE 지역 = ''
GROUP BY 도시
WITH ROLLUP;

SELECT
	도시,
    COUNT(*) AS 고객수,
    AVG(마일리지) AS 평균마일리지
FROM 고객
WHERE 지역 = ''
GROUP BY 도시
WITH ROLLUP;

SELECT
	담당자직위,
    도시,
    COUNT(*) AS 고객수
FROM 고객
WHERE 담당자직위 LIKE '마케팅%'
GROUP BY 담당자직위, 도시
WITH ROLLUP;

SELECT
	지역,
    COUNT(*) AS 고객수,
    GROUPING(지역) AS 구분
FROM 고객
WHERE 담당자직위 = '대표 이사'
GROUP BY 지역
WITH ROLLUP;