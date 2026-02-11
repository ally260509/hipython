# 🛒 Walmart 고객 세그멘테이션 기반 매출 성장 분석

## 📌 프로젝트 개요

본 프로젝트는 Walmart 고객 구매 데이터를 활용해
고객을 구매 행동(소비 여력·가격 수용도) 기준으로 세그멘테이션하고,
이를 바탕으로 매출 성장을 위한 마케팅 타겟과 전략을 도출하는 것을 목표로 한다.

## 🎯 분석 목적

행동 기반 고객 세그멘테이션 설계

세그먼트별 매출 기여도 및 성장 가능성 평가

Defend / Grow / Expand 마케팅 전략 프레임 정의

## 📊 데이터 설명

출처: Kaggle – Walmart 고객 구매 데이터

단위: 트랜잭션 단위

주요 변수

인구통계: Age, Gender, Occupation

상품: Product_Category

거래: Purchase

※ Occupation, Product_Category는 의미 없는 코드 → 행동 기준으로 재정의

## 🔎 핵심 분석 방법

Purchase 로그 변환 (log1p)
→ 왜도 완화 및 안정적 비교

Occupation 재구성
→ 소비 성향(저·중·고 소비)

Product_Category → Price_Segment 전환
→ 저가 / 중가 / 고가 가격대 세그먼트

## 🧩 최종 세그멘테이션 구조
Age_grp × Gender × Occupation_grp × Price_Segment

📈 세그먼트 전략 프레임
🛡️ Defend

고소비 · 고가 상품 고객

목표: 유지 및 프리미엄 강화

## 🚀 Grow

중소비 · 중가 상품 고객

목표: 객단가·빈도 증가 (핵심 성장 타겟)

## 🌱 Expand

소비 여력은 있으나 저가에 고착된 고객

목표: 가격대 상향 전환

## 🔥 주요 인사이트

26–35세 남성 · 고소비 직업군 · 고가 상품 고객이 최상위 매출 기여

Grow 세그먼트가 단기 매출 성장의 핵심

Expand 세그먼트는 가치 인식 개선 시 높은 성장 잠재력 보유

## 📌 결론

매출 성장은 고객의 속성이 아니라
고객의 ‘소비 행동’을 이해하는 데서 시작된다.

본 프로젝트는 행동 기반 세그멘테이션이
실행 가능한 마케팅 전략으로 이어질 수 있음을 보여준다.

## 🧠 사용 기술

Python (Pandas, NumPy, Matplotlib, Seaborn)
EDA · Feature Engineering · 고객 세그멘테이션 · 마케팅 분석