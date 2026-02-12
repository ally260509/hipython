# 사이드바 만들기

#import streamlit as st

# layout 요소 2

#st.sidebar.radio(
  #'이동', 
  #['메인페이지', '분석보고서', '설정']
#)
#st.sidebar.metric('접속자수:', '백만명', '+백만명')

#if st.sidebar.button('Push!!!'):
  #st.balloons()

# 바이브를 위한 프롬프트
# 파이썬 스트림릿 대시보드를 만들어주세요.
# 아래의 구조를 실행가능한 파이썬 코드로 완성하세요
# 기본구성
# 페이지 제목 표시, 이미지 1장 넣기
# 사이드바는 컨트롤 센터로 지정
# 사이드바에 메뉴이동 라디오 버튼(메인페이지, 분석보고서, 설정)
# 메인페이지
# 2개의 컬럼으로 kpi 대시보드 구성
# 방문자수, 활성사용자수를 메트릭 카드로 구성
# 분석페이지
# 탭으로 구성 (차트/데이터/설정)
# 차트탭에는 간단한 사용자 방문현황 그래프
# 데이터탭에는 데이터 테이블 출력
# 설정탭에는 연결 시 옵션 체크박스
# 추가요구사항
# streamlit 함수 : 기발하고 예쁜 것 위주로 적용
# 코드 전체를 한번에 출력
# 꼭 실행가능한 코드여야 함


# app.py
# 실행: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# -----------------------------
# Page Config + Global Styling
# -----------------------------
st.set_page_config(
    page_title="Dolphiners Films | KPI Dashboard",
    page_icon="🐬",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* 전체 톤 */
.block-container { padding-top: 1.2rem; padding-bottom: 2.2rem; }
h1, h2, h3 { letter-spacing: -0.02em; }

/* 메트릭 카드 살짝 세련되게 */
[data-testid="stMetric"] {
  padding: 16px 16px 10px 16px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(6px);
}
[data-testid="stMetric"] label { opacity: 0.8; }
[data-testid="stMetricValue"] { font-size: 2.1rem; }
[data-testid="stMetricDelta"] { font-size: 0.95rem; }

/* 탭 간격 */
div[data-baseweb="tab-list"] { gap: 6px; }

/* 데이터프레임 라운딩 느낌 */
div[data-testid="stDataFrame"] > div { border-radius: 14px; overflow: hidden; }

/* Sidebar 타이틀 */
section[data-testid="stSidebar"] .stMarkdown h2 {
  margin-top: 0.2rem;
  letter-spacing: -0.02em;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# Assets (Image)
# - 돌고래유괴단 관련 기사 이미지(광고 스틸컷)
# -----------------------------
HERO_IMAGE_URL = "https://talkimg.imbc.com/TVianUpload/tvian/TViews/image/2023/07/21/bb92166f-6beb-49c7-832a-5984da9cae8f.jpg"

# -----------------------------
# Helpers
# -----------------------------
def safe_toast(msg: str, icon: str = "✨"):
    # Streamlit 버전에 따라 toast가 없을 수 있어서 안전 처리
    if hasattr(st, "toast"):
        st.toast(msg, icon=icon)

@st.cache_data(show_spinner=False)
def make_daily_kpi(days: int = 30, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    end = datetime.now().date()
    dates = pd.date_range(end=end, periods=days, freq="D")

    base_views = np.linspace(120_000, 420_000, days)
    noise = rng.normal(0, 22_000, days)
    views = np.maximum(10_000, (base_views + noise).astype(int))

    like_rate = rng.uniform(0.012, 0.028, days)  # 1.2% ~ 2.8%
    likes = np.maximum(0, (views * like_rate + rng.normal(0, 600, days)).astype(int))

    df = pd.DataFrame({"date": dates.date, "views": views, "likes": likes})
    df["views_ma7"] = df["views"].rolling(7, min_periods=1).mean().round(0).astype(int)
    return df

@st.cache_data(show_spinner=False)
def make_viewer_table(kpi_df: pd.DataFrame, seed: int = 11) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = kpi_df["date"].tolist()

    # 성별 비율
    female = rng.uniform(0.42, 0.62, len(dates))
    male = 1.0 - female

    # 연령대(합이 1에 가깝도록)
    a1 = rng.uniform(0.05, 0.12, len(dates))   # 13-17
    a2 = rng.uniform(0.24, 0.38, len(dates))   # 18-24
    a3 = rng.uniform(0.28, 0.42, len(dates))   # 25-34
    a4 = np.maximum(0.0, 1.0 - (a1 + a2 + a3)) # 35+

    peak_slots = rng.choice(["07-09(출근)", "12-14(점심)", "18-21(프라임)", "22-01(심야)"], size=len(dates))
    top_device = rng.choice(["Mobile", "Desktop", "TV", "Tablet"], size=len(dates), p=[0.58, 0.18, 0.20, 0.04])
    top_region = rng.choice(["서울", "경기", "부산", "대구", "인천", "광주", "대전"], size=len(dates), p=[0.28,0.26,0.12,0.09,0.09,0.08,0.08])

    avg_watch_sec = rng.normal(54, 9, len(dates))  # 평균 시청 시간(초)
    avg_watch_sec = np.clip(avg_watch_sec, 18, 120).round(1)

    # 광고/브랜드별로 쪼개는 듯한 "캠페인 태그"
    campaign_tag = rng.choice(["Brand Film", "Short Form", "Teaser", "Launch", "Performance"], size=len(dates))

    t = pd.DataFrame({
        "일자": dates,
        "성별(여%)": (female * 100).round(1),
        "성별(남%)": (male * 100).round(1),
        "연령(13-17%)": (a1 * 100).round(1),
        "연령(18-24%)": (a2 * 100).round(1),
        "연령(25-34%)": (a3 * 100).round(1),
        "연령(35+%)": (a4 * 100).round(1),
        "시청시간대(피크)": peak_slots,
        "평균시청시간(초)": avg_watch_sec,
        "TOP 기기": top_device,
        "TOP 지역": top_region,
        "캠페인 태그": campaign_tag,
    })

    return t

def kpi_delta(curr: int, prev: int) -> str:
    if prev == 0:
        return "—"
    pct = (curr - prev) / prev * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"

def build_views_chart(kpi_df: pd.DataFrame):
    base = pd.DataFrame({
        "date": pd.to_datetime(kpi_df["date"]),
        "views": kpi_df["views"],
        "views_ma7": kpi_df["views_ma7"],
    })

    line = (
        alt.Chart(base)
        .mark_line()
        .encode(
            x=alt.X("date:T", title="일자"),
            y=alt.Y("views:Q", title="조회수"),
            tooltip=[
                alt.Tooltip("date:T", title="일자"),
                alt.Tooltip("views:Q", title="조회수", format=","),
            ],
        )
    )

    ma = (
        alt.Chart(base)
        .mark_line(strokeDash=[6, 4])
        .encode(
            x="date:T",
            y=alt.Y("views_ma7:Q", title=""),
            tooltip=[
                alt.Tooltip("date:T", title="일자"),
                alt.Tooltip("views_ma7:Q", title="7일 이동평균", format=","),
            ],
        )
    )

    band = (
        alt.Chart(base)
        .mark_area(opacity=0.15)
        .encode(
            x="date:T",
            y="views:Q",
        )
    )

    return (band + line + ma).properties(height=320).interactive()

# -----------------------------
# Sidebar (Control Center)
# -----------------------------
with st.sidebar:
    st.markdown("## 🎛️ Control Center")
    page = st.radio(
        "메뉴 이동",
        ["메인 페이지", "분석보고서", "설정"],
        index=0,
        help="대시보드 섹션을 이동합니다.",
    )

    st.divider()

    # UX 느낌: 필터/컨트롤
    st.markdown("### 🧪 Quick Controls")
    DAYS = st.slider("분석 기간(일)", 7, 60, 30, step=1)
    show_ma = st.toggle("7일 이동평균 표시", value=True)
    mock_mode = st.toggle("Mock Data 모드", value=True, help="현재는 샘플 데이터로 동작합니다.")

    st.divider()
    st.markdown("### 🔔 Signals")
    anomaly_guard = st.checkbox("급등/급락 감지(알림)", value=True)
    auto_refresh = st.checkbox("자동 새로고침(데모)", value=False)
    st.caption("※ 자동 새로고침은 실제 배포 시 st_autorefresh 등으로 연결 권장")

# -----------------------------
# Data
# -----------------------------
kpi_df = make_daily_kpi(days=DAYS, seed=7)
viewer_df = make_viewer_table(kpi_df, seed=11)

# KPI 요약
curr_views = int(kpi_df["views"].iloc[-1])
prev_views = int(kpi_df["views"].iloc[-2]) if len(kpi_df) >= 2 else 0
curr_likes = int(kpi_df["likes"].iloc[-1])
prev_likes = int(kpi_df["likes"].iloc[-2]) if len(kpi_df) >= 2 else 0

# Anomaly (간단 룰 기반)
if anomaly_guard and len(kpi_df) >= 8:
    v_today = kpi_df["views"].iloc[-1]
    v_ma7 = kpi_df["views"].rolling(7).mean().iloc[-2]  # 전일까지의 MA7
    if pd.notna(v_ma7) and v_ma7 > 0:
        ratio = v_today / v_ma7
        if ratio >= 1.35:
            safe_toast("조회수가 평소 대비 크게 상승했어요.", icon="🚀")
        elif ratio <= 0.70:
            safe_toast("조회수가 평소 대비 크게 하락했어요.", icon="🧊")

# -----------------------------
# Header (Title + Image)
# -----------------------------
st.title("🐬 Dolphiners Films — KPI Dashboard")
st.caption("광고 성과(YouTube) 모니터링용 데모 대시보드 · UI/UX 프로토타입 (Streamlit)")

with st.expander("📌 Hero Image (광고 스틸컷)", expanded=True):
    st.image(HERO_IMAGE_URL, use_container_width=True, caption="Dolphiners Films 관련 광고 스틸컷(기사 이미지)")

# =============================
# Page: Main
# =============================
if page == "메인 페이지":
    st.subheader("📊 Executive Snapshot")

    # 2 컬럼 KPI 구성
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.metric(
            label="YouTube 광고 조회수 (Today)",
            value=f"{curr_views:,}",
            delta=kpi_delta(curr_views, prev_views),
        )

        # 보너스: 미니 트렌드
        chart_df = kpi_df.copy()
        chart_df["date"] = pd.to_datetime(chart_df["date"])
        mini = alt.Chart(chart_df).mark_line().encode(
            x=alt.X("date:T", title=""),
            y=alt.Y("views:Q", title=""),
            tooltip=[alt.Tooltip("date:T", title="일자"), alt.Tooltip("views:Q", title="조회수", format=",")],
        ).properties(height=140)
        st.altair_chart(mini, use_container_width=True)

    with c2:
        st.metric(
            label="‘좋아요’ 클릭수 (Today)",
            value=f"{curr_likes:,}",
            delta=kpi_delta(curr_likes, prev_likes),
        )

        like_rate_today = (curr_likes / curr_views * 100) if curr_views else 0
        like_rate_prev = (prev_likes / prev_views * 100) if prev_views else 0

        st.metric(
            label="Like Rate (Today)",
            value=f"{like_rate_today:.2f}%",
            delta=f"{(like_rate_today - like_rate_prev):+.2f}pp" if prev_views else "—",
        )

    st.divider()

    # 살짝 기발한 UI: 상태 배지 + 진행바
    st.markdown("### 🧭 Health Check")
    h1, h2, h3 = st.columns(3)
    with h1:
        st.info("Signal: **Stable** · 노이즈 내 변동", icon="🟦")
    with h2:
        st.success("Pipeline: **Ready** · 데이터 생성 OK", icon="🟩")
    with h3:
        st.warning("Action: **Connect API** · 설정에서 연결", icon="🟨")

    st.progress(min(1.0, max(0.0, curr_views / 500_000)), text="목표(500k views) 대비 진행률")

    st.divider()
    st.markdown("### 🧩 Notes")
    with st.container():
        st.write(
            "- 이 화면은 **임원/클라이언트용 KPI 스냅샷**을 의도했어요.\n"
            "- 실제 구현 시 YouTube Analytics API 연결 + 캠페인/영상별 드릴다운 구조를 추천."
        )

# =============================
# Page: Analytics Report
# =============================
elif page == "분석보고서":
    st.subheader("🧪 분석보고서")

    tab_chart, tab_data, tab_settings = st.tabs(["📈 차트", "🗃️ 데이터", "⚙️ 설정"])

    with tab_chart:
        st.markdown("#### 일별 YouTube 광고 조회수 현황")
        if not show_ma:
            # 이동평균 숨김 옵션
            tmp = kpi_df.copy()
            tmp["views_ma7"] = np.nan

        fig = build_views_chart(kpi_df if show_ma else tmp)
        st.altair_chart(fig, use_container_width=True)

        st.caption("실선: 일별 조회수 · 점선: 7일 이동평균")

    with tab_data:
        st.markdown("#### 광고 시청자(샘플) — 일자별 테이블")
        st.caption("컬럼 예시: 성별, 연령대, 시청시간대, 평균시청시간, TOP 기기/지역 등 (5개 이상 구성)")

        # 데이터 편집 가능한 UI (예쁨 + 실무 감각)
        edited = st.data_editor(
            viewer_df,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
        )

        # 다운로드
        csv = edited.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSV 다운로드",
            data=csv,
            file_name="dolphiners_viewer_daily.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with tab_settings:
        st.markdown("#### 연결 시 옵션")
        colA, colB = st.columns(2, gap="large")
        with colA:
            st.checkbox("YouTube Analytics API 연결", value=False)
            st.checkbox("캠페인/영상별 세그먼트 가져오기", value=True)
            st.checkbox("실시간(near real-time) 지표 포함", value=False)
        with colB:
            st.checkbox("개인정보 마스킹(PII 제거)", value=True)
            st.checkbox("이상치 알림(Webhook/Slack)", value=True)
            st.checkbox("자동 리포트 스냅샷(PDF)", value=False)

        st.info("체크 항목은 데모 UI입니다. 실제 구현 시 설정값을 secrets.toml + DB로 관리하세요.", icon="🧠")

# =============================
# Page: Settings
# =============================
else:  # "설정"
    st.subheader("⚙️ 설정")

    st.markdown("### Workspace")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.text_input("프로젝트 이름", value="Dolphiners KPI Dashboard")
        st.selectbox("기본 리포트 단위", ["일간", "주간", "월간"], index=0)
        st.multiselect("기본 필터(데모)", ["캠페인", "영상", "지역", "기기", "연령대"], default=["캠페인", "영상"])
        st.toggle("다크 모드 최적화(시각적)", value=True)

    with col2:
        st.markdown("#### Data Source")
        st.radio("데이터 소스", ["Mock 데이터", "YouTube API", "BigQuery/DB"], index=0)
        st.text_input("API Key (데모)", value="", type="password", placeholder="실제 배포 시 st.secrets 사용")
        st.toggle("캐시 활성화(st.cache_data)", value=True)
        st.toggle("서버 로그(디버그)", value=False)

    st.divider()
    st.markdown("### Actions")
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("✅ 설정 저장", use_container_width=True):
            safe_toast("설정을 저장했어요.", icon="💾")
            st.balloons()
    with a2:
        if st.button("🔄 데이터 새로고침(데모)", use_container_width=True):
            st.cache_data.clear()
            safe_toast("데이터를 새로고침했어요.", icon="🔄")
            st.rerun()
    with a3:
        if st.button("🧹 캐시 클리어", use_container_width=True):
            st.cache_data.clear()
            safe_toast("캐시를 비웠어요.", icon="🧼")

    st.caption("실서비스에서는 역할(권한)·환경(dev/prod)·감사로그까지 묶어서 Settings를 설계하는 걸 추천.")

# Footer
st.divider()
st.caption("© Prototype Dashboard · Streamlit UI Demo")








# 터미널 입력 명령어: streamlit run app3.py