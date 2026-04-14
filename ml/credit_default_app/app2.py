import os
import joblib
import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="신용카드 채무불이행 예측",
    page_icon="💳",
    layout="wide",
)

# ──────────────────────────────────────────────────────────────
# FR-03 | NFR-02 : 서비스 시작 시 모델 로드 — 실패 시 즉시 중단
# ──────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "service_pipeline.pkl")

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None, f"service_pipeline.pkl 없음 ({MODEL_PATH})"
    try:
        return joblib.load(MODEL_PATH), None
    except Exception as e:
        return None, str(e)

pipeline, load_error = load_model()

if load_error:
    st.error(f"⚠ 모델 로드 오류 — {load_error}")
    st.info("관리자에게 문의하거나 service_pipeline.pkl 파일을 확인해주세요.")
    st.stop()   # NFR-02 : 오류 시 서비스 중단


# ──────────────────────────────────────────────────────────────
# FR-02 : 입력값 유효성 검사
# EX-01 결측값 | EX-02 범위 초과 | EX-03 타입 오류
# NFR-06 try-except | NFR-07 앱 종료 없이 유지
# ──────────────────────────────────────────────────────────────
def validate(data: dict) -> list[str]:
    errors = []

    # EX-01 결측값
    for k, v in data.items():
        if v is None:
            errors.append(f"[EX-01] {k} : 값이 없습니다.")
    if errors:
        return errors

    # EX-02 범위
    if not (10_000 <= data["LIMIT_BAL"] <= 1_000_000):
        errors.append("[EX-02] LIMIT_BAL : 10,000 ~ 1,000,000 NT$ 범위를 벗어났습니다.")
    if not (18 <= data["AGE"] <= 100):
        errors.append("[EX-02] AGE : 18 ~ 100 범위를 벗어났습니다.")
    for k in ["PAY_0","PAY_2","PAY_3","PAY_4","PAY_5","PAY_6"]:
        if data[k] not in range(-2, 10):
            errors.append(f"[EX-02] {k} : -2 ~ 9 범위를 벗어났습니다.")
    for k in [f"BILL_AMT{i}" for i in range(1,7)] + [f"PAY_AMT{i}" for i in range(1,7)]:
        if not (0 <= data[k] <= 10_000_000):
            errors.append(f"[EX-02] {k} : 0 ~ 10,000,000 NT$ 범위를 벗어났습니다.")

    # EX-03 타입
    for k, v in data.items():
        if not isinstance(v, (int, float)):
            errors.append(f"[EX-03] {k} : 숫자 타입 오류 ({type(v).__name__})")

    return errors


# ──────────────────────────────────────────────────────────────
# FR-05 : 4단계 위험등급 분류
# ──────────────────────────────────────────────────────────────
def classify_risk(p: float) -> dict:
    if p >= 0.7:
        return {
            "grade": "위험", "level": "HIGH RISK", "emoji": "🔴",
            "color": "#EF4444", "bg": "#FEF2F2", "border": "#FCA5A5",
            "action": [
                "신용한도 즉시 정지",
                "추심 절차 개시 검토",
                "여신 전문가 즉각 배정",
            ],
            "desc": "채무불이행 확률 70% 이상 — 즉각적인 조치가 필요합니다.",
        }
    elif p >= 0.5:
        return {
            "grade": "경고", "level": "WARNING", "emoji": "🟠",
            "color": "#F97316", "bg": "#FFF7ED", "border": "#FED7AA",
            "action": [
                "신용한도 축소 검토",
                "집중 모니터링 등록",
                "30일 이내 재심사 권고",
            ],
            "desc": "채무불이행 확률 50~70% — 신용 관리가 필요합니다.",
        }
    elif p >= 0.3:
        return {
            "grade": "주의", "level": "CAUTION", "emoji": "🟡",
            "color": "#CA8A04", "bg": "#FEFCE8", "border": "#FDE68A",
            "action": [
                "분기별 정기 모니터링",
                "추가 서류 심사 권고",
                "한도 조정 여부 검토",
            ],
            "desc": "채무불이행 확률 30~50% — 지속적인 모니터링이 필요합니다.",
        }
    else:
        return {
            "grade": "안전", "level": "SAFE", "emoji": "🟢",
            "color": "#16A34A", "bg": "#F0FDF4", "border": "#86EFAC",
            "action": [
                "정상 거래 유지",
                "신용한도 증액 검토 가능",
                "우량 고객 관리 프로그램 적용",
            ],
            "desc": "채무불이행 확률 30% 미만 — 정상 거래를 유지하세요.",
        }


# ──────────────────────────────────────────────────────────────
# 헤더 배너
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#1e3a5f,#2563EB);
            padding:22px 30px; border-radius:14px; margin-bottom:24px;'>
  <h1 style='color:#fff; margin:0; font-size:26px;'>
    💳 신용카드 채무불이행 예측 시스템
  </h1>
  <p style='color:#93C5FD; margin:6px 0 0; font-size:14px;'>
    고객 신용정보를 입력하면 채무불이행 확률과 4단계 위험등급을 즉시 예측합니다.
  </p>
  <p style='color:#60A5FA; margin:4px 0 0; font-size:12px;'>
    ✅ 모델 로드 완료 (service_pipeline.pkl) &nbsp;|&nbsp;
    🔒 NFR-03: 입력 정보는 서버에 저장되지 않습니다 &nbsp;|&nbsp;
    ⚡ NFR-01: 3초 이내 응답 보장
  </p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# 사이드바 : FR-01 고객 정보 입력 (23개 변수)
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 고객 정보 입력")
    st.caption("FR-01 : 23개 변수를 UI 위젯으로 입력받습니다.")
    st.divider()

    # 기본 정보
    st.markdown("**① 기본 정보**")
    LIMIT_BAL = st.number_input(
        "신용한도 (NT$)", min_value=10_000, max_value=1_000_000,
        value=200_000, step=10_000, help="범위: 10,000 ~ 1,000,000")
    SEX       = st.selectbox("성별", [1, 2],
        format_func=lambda x: "남성" if x == 1 else "여성")
    EDUCATION = st.selectbox("학력", [1, 2, 3, 4],
        format_func=lambda x: {1:"대학원",2:"대학교",3:"고등학교",4:"기타"}[x])
    MARRIAGE  = st.selectbox("결혼여부", [1, 2, 3],
        format_func=lambda x: {1:"기혼",2:"미혼",3:"기타"}[x])
    AGE       = st.number_input("나이", min_value=18, max_value=100, value=35)

    st.divider()

    # 납부 현황
    st.markdown("**② 납부 현황** (최근 6개월)")
    st.caption("-2=잔액없음 | -1=정상 | 0=최소납부 | 1~9=연체개월")
    cols_pay = st.columns(2)
    PAY_0 = cols_pay[0].selectbox("9월 PAY_0", list(range(-2,10)), index=2)
    PAY_2 = cols_pay[1].selectbox("8월 PAY_2", list(range(-2,10)), index=2)
    PAY_3 = cols_pay[0].selectbox("7월 PAY_3", list(range(-2,10)), index=2)
    PAY_4 = cols_pay[1].selectbox("6월 PAY_4", list(range(-2,10)), index=2)
    PAY_5 = cols_pay[0].selectbox("5월 PAY_5", list(range(-2,10)), index=2)
    PAY_6 = cols_pay[1].selectbox("4월 PAY_6", list(range(-2,10)), index=2)

    st.divider()

    # 청구금액
    st.markdown("**③ 청구금액** (NT$)")
    cols_bill = st.columns(2)
    BILL_AMT1 = cols_bill[0].number_input("9월", 0, 10_000_000, 50_000, 1_000, key="b1")
    BILL_AMT2 = cols_bill[1].number_input("8월", 0, 10_000_000, 48_000, 1_000, key="b2")
    BILL_AMT3 = cols_bill[0].number_input("7월", 0, 10_000_000, 46_000, 1_000, key="b3")
    BILL_AMT4 = cols_bill[1].number_input("6월", 0, 10_000_000, 44_000, 1_000, key="b4")
    BILL_AMT5 = cols_bill[0].number_input("5월", 0, 10_000_000, 42_000, 1_000, key="b5")
    BILL_AMT6 = cols_bill[1].number_input("4월", 0, 10_000_000, 40_000, 1_000, key="b6")

    st.divider()

    # 납부금액
    st.markdown("**④ 납부금액** (NT$)")
    cols_pamt = st.columns(2)
    PAY_AMT1 = cols_pamt[0].number_input("9월", 0, 10_000_000, 5_000, 1_000, key="p1")
    PAY_AMT2 = cols_pamt[1].number_input("8월", 0, 10_000_000, 5_000, 1_000, key="p2")
    PAY_AMT3 = cols_pamt[0].number_input("7월", 0, 10_000_000, 5_000, 1_000, key="p3")
    PAY_AMT4 = cols_pamt[1].number_input("6월", 0, 10_000_000, 5_000, 1_000, key="p4")
    PAY_AMT5 = cols_pamt[0].number_input("5월", 0, 10_000_000, 5_000, 1_000, key="p5")
    PAY_AMT6 = cols_pamt[1].number_input("4월", 0, 10_000_000, 5_000, 1_000, key="p6")

    st.divider()
    predict_btn = st.button(
        "🔍 채무불이행 예측하기", type="primary", use_container_width=True)


# ──────────────────────────────────────────────────────────────
# 메인 영역 : 대기 화면
# ──────────────────────────────────────────────────────────────
if not predict_btn:
    st.markdown("""
    <div style='text-align:center; padding:50px 20px;'>
      <div style='font-size:72px;'>💳</div>
      <h3 style='color:#374151; margin-top:16px;'>
        좌측 사이드바에 고객 정보를 입력하고<br>
        <span style='color:#2563EB;'>예측하기</span> 버튼을 눌러주세요
      </h3>
      <p style='color:#9CA3AF; font-size:13px;'>
        FR-01: 23개 변수 &nbsp;|&nbsp; FR-05: 4단계 위험등급 &nbsp;|&nbsp;
        NFR-01: 3초 이내 응답
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 위험등급 판정 기준 (FR-05)")
    guide = pd.DataFrame({
        "등급"        : ["🔴 위험 (HIGH RISK)", "🟠 경고 (WARNING)",
                         "🟡 주의 (CAUTION)",   "🟢 안전 (SAFE)"],
        "채무불이행 확률": ["p ≥ 70%", "50% ≤ p < 70%",
                          "30% ≤ p < 50%", "p < 30%"],
        "권장조치"     : ["신용한도 즉시 정지 / 추심 개시",
                         "신용한도 축소 / 집중 모니터링",
                         "정기 모니터링 / 추가 심사",
                         "정상 거래 유지 / 한도 증액 검토"],
    })
    st.dataframe(guide, use_container_width=True, hide_index=True)
    st.stop()


# ──────────────────────────────────────────────────────────────
# 입력 데이터 조립
# ──────────────────────────────────────────────────────────────
input_data = {
    "LIMIT_BAL": LIMIT_BAL, "SEX": SEX, "EDUCATION": EDUCATION,
    "MARRIAGE": MARRIAGE,   "AGE": AGE,
    "PAY_0": PAY_0, "PAY_2": PAY_2, "PAY_3": PAY_3,
    "PAY_4": PAY_4, "PAY_5": PAY_5, "PAY_6": PAY_6,
    "BILL_AMT1": BILL_AMT1, "BILL_AMT2": BILL_AMT2, "BILL_AMT3": BILL_AMT3,
    "BILL_AMT4": BILL_AMT4, "BILL_AMT5": BILL_AMT5, "BILL_AMT6": BILL_AMT6,
    "PAY_AMT1": PAY_AMT1,   "PAY_AMT2": PAY_AMT2,   "PAY_AMT3": PAY_AMT3,
    "PAY_AMT4": PAY_AMT4,   "PAY_AMT5": PAY_AMT5,   "PAY_AMT6": PAY_AMT6,
}

# ── FR-02 : 유효성 검사 ──────────────────────────────────────
errors = validate(input_data)
if errors:
    st.error("⚠ 입력값 오류 — 아래 항목을 수정 후 재입력해주세요.")
    for err in errors:
        st.warning(err)
    st.stop()   # NFR-07: 앱 종료 없이 오류 표시 후 대기

# ── FR-04 : 모델 추론 (NFR-06: try-except) ───────────────────
try:
    with st.spinner("예측 중..."):
        df        = pd.DataFrame([input_data])
        proba     = pipeline.predict_proba(df)[0]
        p_ok      = float(proba[0])
        p_default = float(proba[1])

    # NFR-06: 예측값 범위 검사
    if not (0.0 <= p_default <= 1.0 and 0.0 <= p_ok <= 1.0):
        st.error("✕ 모델 오류 반환 — 예측에 실패했습니다.")
        st.stop()

except Exception as e:
    st.error(f"✕ 모델 오류 반환 — {e}")
    st.stop()

# ── FR-05 : 위험등급 분류 ────────────────────────────────────
risk = classify_risk(p_default)


# ══════════════════════════════════════════════════════════════
# FR-06 : 결과 출력
# ══════════════════════════════════════════════════════════════

# ① 대형 위험등급 카드
st.markdown(f"""
<div style='background:{risk["bg"]};
            border:2px solid {risk["border"]};
            border-left:8px solid {risk["color"]};
            border-radius:14px; padding:24px 28px; margin-bottom:20px;'>
  <div style='display:flex; align-items:center; gap:20px;'>
    <div style='font-size:56px; line-height:1;'>{risk["emoji"]}</div>
    <div>
      <div style='font-size:12px; color:#6B7280; font-weight:700;
           letter-spacing:3px; text-transform:uppercase; margin-bottom:4px;'>
        FR-05 위험등급 판정
      </div>
      <div style='font-size:36px; font-weight:900; color:{risk["color"]}; line-height:1.1;'>
        {risk["grade"]}
        <span style='font-size:18px; font-weight:500; color:#6B7280;'>
          &nbsp;{risk["level"]}
        </span>
      </div>
      <div style='font-size:14px; color:#374151; margin-top:8px;'>
        {risk["desc"]}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ② 확률 수치 메트릭 (3컬럼)
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("⚠ 채무불이행 확률", f"{p_default*100:.1f}%")
with m2:
    st.metric("✅ 정상 확률",      f"{p_ok*100:.1f}%")
with m3:
    st.metric("📊 위험등급",       f"{risk['emoji']} {risk['grade']}")

st.divider()

# ③ 확률 게이지 바
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.markdown("**✅ 정상 확률**")
    st.progress(p_ok)
    st.caption(f"{p_ok*100:.1f}%")
with col_g2:
    st.markdown("**⚠ 채무불이행 확률**")
    st.progress(p_default)
    st.caption(f"{p_default*100:.1f}%")

st.divider()

# ④ 권장조치 카드 (FR-06: st.info)
st.subheader("💡 권장조치")
action_items = "".join(
    [f"<li style='margin:8px 0; font-size:15px; color:#1E40AF;'>{a}</li>"
     for a in risk["action"]]
)
st.markdown(f"""
<div style='background:#EFF6FF; border-left:5px solid #2563EB;
            border-radius:10px; padding:18px 22px;'>
  <ul style='margin:0; padding-left:22px;'>
    {action_items}
  </ul>
</div>
""", unsafe_allow_html=True)

st.divider()

# ⑤ 4단계 위험등급 척도 시각화
st.subheader("📊 위험등급 척도")
grade_info = [
    ("🟢", "안전",  "SAFE",      "#16A34A", "p < 30%"),
    ("🟡", "주의",  "CAUTION",   "#CA8A04", "30~50%"),
    ("🟠", "경고",  "WARNING",   "#F97316", "50~70%"),
    ("🔴", "위험",  "HIGH RISK", "#EF4444", "p ≥ 70%"),
]
for col, (emoji, grade, level, color, prob) in zip(st.columns(4), grade_info):
    is_current = grade == risk["grade"]
    with col:
        st.markdown(f"""
        <div style='
          border:{("3px solid " + color) if is_current else "1px solid #E5E7EB"};
          background:{("rgba(0,0,0,0.04)") if is_current else "#FAFAFA"};
          border-radius:12px; padding:16px 12px; text-align:center;
          {"box-shadow:0 4px 12px rgba(0,0,0,0.12);" if is_current else "opacity:0.6;"}'>
          <div style='font-size:28px;'>{emoji}</div>
          <div style='font-weight:800; font-size:16px; color:{color}; margin:4px 0;'>{grade}</div>
          <div style='font-size:11px; color:#6B7280;'>{level}</div>
          <div style='font-size:12px; color:#9CA3AF; margin-top:4px;'>{prob}</div>
          {"<div style='margin-top:8px; font-size:12px; font-weight:700; color:" + color + ";'>▲ 현재 등급</div>" if is_current else ""}
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ⑥ FR-07: 입력값 요약 — 탭 형식 st.dataframe
st.subheader("📝 입력값 요약 (FR-07)")
tab1, tab2, tab3, tab4 = st.tabs(["기본 정보", "납부 현황", "청구금액", "납부금액"])

with tab1:
    st.dataframe(pd.DataFrame({
        "변수"   : ["LIMIT_BAL","SEX","EDUCATION","MARRIAGE","AGE"],
        "입력값" : [LIMIT_BAL, SEX, EDUCATION, MARRIAGE, AGE],
        "설명"   : ["신용한도(NT$)","성별(1=남/2=여)","학력(1~4)","결혼여부(1~3)","나이"],
    }), use_container_width=True, hide_index=True)

with tab2:
    st.dataframe(pd.DataFrame({
        "변수"   : ["PAY_0","PAY_2","PAY_3","PAY_4","PAY_5","PAY_6"],
        "입력값" : [PAY_0,PAY_2,PAY_3,PAY_4,PAY_5,PAY_6],
        "월"     : ["9월","8월","7월","6월","5월","4월"],
        "의미"   : ["정상" if v==-1 else ("잔액없음" if v==-2 else f"연체 {v}개월")
                    for v in [PAY_0,PAY_2,PAY_3,PAY_4,PAY_5,PAY_6]],
    }), use_container_width=True, hide_index=True)

with tab3:
    vals_b = [BILL_AMT1,BILL_AMT2,BILL_AMT3,BILL_AMT4,BILL_AMT5,BILL_AMT6]
    st.dataframe(pd.DataFrame({
        "변수"      : [f"BILL_AMT{i}" for i in range(1,7)],
        "청구금액(NT$)": vals_b,
        "월"        : ["9월","8월","7월","6월","5월","4월"],
    }), use_container_width=True, hide_index=True)

with tab4:
    vals_p = [PAY_AMT1,PAY_AMT2,PAY_AMT3,PAY_AMT4,PAY_AMT5,PAY_AMT6]
    st.dataframe(pd.DataFrame({
        "변수"      : [f"PAY_AMT{i}" for i in range(1,7)],
        "납부금액(NT$)": vals_p,
        "월"        : ["9월","8월","7월","6월","5월","4월"],
    }), use_container_width=True, hide_index=True)

st.caption("🔒 NFR-03: 위 정보는 예측에만 사용되며 서버에 저장되지 않습니다.")
