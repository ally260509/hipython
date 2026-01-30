USE WNTRADE;

SELECT FIELD('SQL', 'SQL', 'JAVA', 'C');

SELECT FIELD('오땅', '홈런볼', '오땅', '초콜릿');

SELECT REPLACE('ABC-DEF', '-', '*');

SELECT REVERSE('ABCDE');

SELECT NOW()
, SYSDATE()
, CURDATE()
, CURTIME();

SELECT NOW() AS 'START', SLEEP(5), NOW() AS 'END';  -- 시작시간 기준
SELECT SYSDATE() AS 'START', SLEEP(5), SYSDATE() AS 'END'; -- 

SELECT 고객번호, IF(마일리지>1000, 'VIP', 'GOLD') AS 등급
FROM 고객;

SELECT IF(12500 * 450 >= 5000000, '초과달성', '미달성');

SELECT 고객번호, IF(도시 like '%광역시', '대도시', '소도시')
FROM 고객;

SELECT 
	주문번호,
	단가,
	주문수량,
	단가*주문수량 as 주문금액,
	CASE 
		WHEN 단가*주문수량 > 5000000 THEN '초과달성'
		WHEN 단가*주문수량 > 4000000 THEN '달성'
		ELSE '미달성'
	END AS 달성여부
FROM 주문세부;

-- 마일리지 등급 부여 VIP, GOLD, SILVER, BRONZE

SELECT 마일리지
FROM 고객
ORDER BY 마일리지;

SELECT
	고객번호,
	담당자명,
    마일리지,
    CASE
		WHEN 마일리지 > 100000 THEN 'VIP'
        WHEN 마일리지 > 10000 THEN 'GOLD'
        WHEN 마일리지 > 5000 THEN 'SILVER'
        ELSE 'BRONZE'
	END AS 고객분류
FROM 고객;

-- 발송일 컬럼 기준, '배송대기', '빠른배송', '일반배송'으로 설정

SELECT 
	주문일,
    발송일 
FROM 주문;

SELECT
	주문번호,
    고객번호,
    주문일,
    발송일,
	CASE
		WHEN 발송일 IS NULL THEN '배송대기'
        WHEN 발송일 - 주문일 <= 2 THEN '빠른배송'
        ELSE'일반배송'
	END AS 배송현황
FROM 주문;

-- 부서코드 > 부서명으로

SELECT *
FROM 사원;

SELECT *
FROM 부서;

SELECT
	사원번호,
    이름,
    부서번호,
    CASE
		WHEN 부서번호 = 'A1' THEN '영업부'
        WHEN 부서번호 = 'A2' THEN '기획부'
        WHEN 부서번호 = 'A3' THEN '개발부'
		ELSE '홍보부'
	END AS 부서명
FROM 사원;

-- 연습1. 고객회사명 앞2글자 '*' 마스킹 처리
SELECT
	고객번호,
    고객회사명,
    담당자명,
    CONCAT('**', SUBSTRING(고객회사명, 3)) AS 고객회사명_마스킹
FROM 고객;

-- 연습2. 주문세부 정보중 주문금액, 할인금액, 실제주문금액 출력(1단위에서 버림)

SELECT 
	도시,
	COUNT(*),
    COUNT(고객번호),
    COUNT(도시),
    COUNT(DISTINCT 지역),
    SUM(마일리지),
    AVG(마일리지),
    MIN(마일리지),
    MAX(마일리지)
FROM 고객
-- WHERE 도시 LIKE '서울%';
GROUP BY 도시;

-- 담당자별로 그룹

SELECT 
	담당자직위,
    도시,
	COUNT(고객번호),
    SUM(마일리지),
    AVG(마일리지)
FROM 고객
GROUP BY 담당자직위, 도시
ORDER BY 담당자직위, 도시;

-- GROUP BY 조건 HAVING
-- 고객 - 도시별로 그룹 - 고객수, 평균마일리지, 고객수 > 10 이상만 추출

SELECT 
	도시,
	COUNT(고객번호),
	AVG(마일리지)
FROM 고객
GROUP BY 도시
WITH ROLLUP
HAVING COUNT(고객번호) >= 5;

-- 고객번호 T로 시작하는 고객을 도시별로 묶어 마일리지 합 출력, 단, 1000점 이상만

SELECT
	도시,
    SUM(마일리지)    
FROM 고객
WHERE 고객번호 LIKE 'T%'
GROUP BY 도시
WITH ROLLUP
HAVING SUM(마일리지) >= 100;

-- 광역시 고객, 담당자 직위별로 최대마일리지, 단, 10000점 이상 레코드만 출력

SELECT
	담당자직위,
	MAX(마일리지),
    SUM(마일리지),
    AVG(마일리지)
FROM 고객
WHERE 도시 LIKE '%광역시'
GROUP BY 담당자직위
WITH ROLLUP -- 총계 행이 추가
HAVING MAX(마일리지) >=10000;



