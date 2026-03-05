import streamlit as st
import pandas as pd
import re
from datetime import date
from collections import Counter

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="아이그로스 점심 전략 대시보드", layout="wide")

st.title("🍱 아이그로스 점심 전략 시스템 (Hybrid Mode)")

# -----------------------------
# 파일 로드
# -----------------------------
file_path = "./data/아이그로스 교육센터 맛집 list.xlsx"
df = pd.read_excel(file_path, skiprows=2)
df.columns = df.iloc[0]
df = df.drop(index=0).reset_index(drop=True)
df = df[['식당명','대표메뉴1','대표메뉴2','기타사항']]

# -----------------------------
# 가격 추출
# -----------------------------
def extract_price(text):
    if pd.isna(text):
        return None
    match = re.search(r'(\d{1,3},?\d{0,3})원', str(text))
    if match:
        return int(match.group(1).replace(',', ''))
    return None

df['가격'] = df['대표메뉴1'].apply(extract_price)

# -----------------------------
# 카테고리 자동 분류
# -----------------------------
def categorize(menu):
    if pd.isna(menu):
        return "기타"
    menu = str(menu)

    if any(x in menu for x in ['짜장','짬뽕','마라']):
        return "중식"
    elif any(x in menu for x in ['카츠','우동','초밥','돈카츠']):
        return "일식"
    elif any(x in menu for x in ['김밥','떡볶이','라면']):
        return "분식"
    elif any(x in menu for x in ['파스타','피자']):
        return "양식"
    elif any(x in menu for x in ['샌드위치','브런치']):
        return "샌드위치"
    elif any(x in menu for x in ['찌개','국밥','제육','비빔밥','순두부']):
        return "한식"
    else:
        return "기타"

df['카테고리'] = df['대표메뉴1'].apply(categorize)

# -----------------------------
# 점수 계산 함수
# -----------------------------
def base_score(row):
    score = 6
    if pd.notna(row['기타사항']):
        text = str(row['기타사항'])
        if "맛있" in text:
            score += 1
        if "비추천" in text:
            score -= 1
    return score

def price_score(price):
    if price is None:
        return 0
    if price <= 7000:
        return 2
    elif price <= 10000:
        return 1
    return 0

def sleep_risk(menu):
    text = str(menu)
    risk = 0
    if any(x in text for x in ['짜장','짬뽕','볶음','면']):
        risk += 2
    if any(x in text for x in ['카츠','튀김']):
        risk += 2
    if any(x in text for x in ['찌개','국밥']):
        risk += 1
    return risk

df['기본평점'] = df.apply(base_score, axis=1)
df['가성비점수'] = df['가격'].apply(price_score)
df['졸림리스크'] = df['대표메뉴1'].apply(sleep_risk)

df['최종점수'] = df['기본평점'] + df['가성비점수'] - df['졸림리스크']

# 점수 구성 요소 표시용 컬럼

df['설명_기본평점'] = df['기본평점']
df['설명_가성비'] = df['가성비점수']
df['설명_졸림차감'] = -df['졸림리스크']

# 예시 거리 점수 (지금은 고정 없으면 0)
df['설명_거리'] = 0

# 리스크 패널티 (현재 구현 안했으면 0)
df['설명_리스크'] = 0

# -----------------------------
# 웹 보완 (Hybrid)
# -----------------------------
st.sidebar.header("🌐 Hybrid 보완")
include_web = st.sidebar.checkbox("웹 검색 후보 포함")

if include_web:
    web_data = pd.DataFrame({
        "식당명":["신규맛집A","신규맛집B"],
        "대표메뉴1":["비빔국수 8,000원","돈카츠 9,000원"],
        "가격":[8000,9000],
        "카테고리":["한식","일식"],
        "기본평점":[7,7],
        "가성비점수":[1,1],
        "졸림리스크":[1,2]
    })
    web_data["최종점수"] = web_data["기본평점"] + web_data["가성비점수"] - web_data["졸림리스크"]
    df = pd.concat([df, web_data], ignore_index=True)

# -----------------------------
# TOP3 추천
# -----------------------------
top3 = df.sort_values(by="최종점수", ascending=False).head(3)

st.subheader("🥇 오늘의 추천 TOP3")
st.dataframe(
    top3[
        [
            '식당명',
            '카테고리',
            '가격',
            '설명_기본평점',
            '설명_가성비',
            '설명_졸림차감',
            '최종점수'
        ]
    ]
)

st.subheader("📊 추천 기준 상세 설명")

for _, row in top3.iterrows():
    with st.expander(f"{row['식당명']} 점수 상세"):
        st.write(f"기본평점: {row['설명_기본평점']}")
        st.write(f"가성비 점수: {row['설명_가성비']}")
        st.write(f"졸림 차감: {row['설명_졸림차감']}")
        st.write(f"최종 점수: {row['최종점수']}")

# -----------------------------
# 선택 기록 저장
# -----------------------------
st.subheader("📝 오늘 선택 기록")

if "log" not in st.session_state:
    st.session_state.log = []

selected = st.selectbox("오늘 먹은 식당 선택", df["식당명"].unique())

if st.button("기록 저장"):
    record = df[df["식당명"] == selected].iloc[0].to_dict()
    record["date"] = str(date.today())
    record["집중도점수"] = 10 - record["졸림리스크"]
    st.session_state.log.append(record)
    st.success("기록 저장 완료")

# -----------------------------
# 주간 통계
# -----------------------------
if st.session_state.log:
    log_df = pd.DataFrame(st.session_state.log)

    st.subheader("📊 주간 카테고리 분포")
    st.bar_chart(log_df["카테고리"].value_counts())

    st.subheader("💰 주간 소비 총액")
    st.metric("총 소비 금액", f"{log_df['가격'].sum():,}원")

    st.subheader("🧠 평균 집중도")
    st.metric("집중도 평균", round(log_df["집중도점수"].mean(),2))
    
