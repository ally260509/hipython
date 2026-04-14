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
# FR-03 | NFR-02 : 서비스 시작 시 모델 로드 (실패 시 즉시 중단)
# ──────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'service_pipeline.pkl')

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None, f"service_pipeline.pkl 없음 → 경로 확인: {MODEL_PATH}"
    try:
        return joblib.load(MODEL_PATH), None
    except Exception as e:
        return None, str(e)

pipeline, load_error = load_model()

if load_error:
    st.error(f"⚠ 모델 로드 오류\n\n{load_error}")
    st.info("관리자에게 문의하거나 service_pipeline.pkl 파일을 확인해주세요.")
    st.stop()   # NFR-02 : 오류 메시지 출력 후 서비스 중단


# ──────────────────────────────────────────────────────────────
# FR-02 : 입력값 유효성 검사 (EX-01 결측 / EX-02 범위 / EX-03 타입)
# NFR-06 : try-except 처리  |  NFR-07 : 앱 종료 없이 오류 반환
# ──────────────────────────────────────────────────────────────
def validate(data: dict) -> list[str]:
    errors = []

    # EX-01 결측값 확인
    for k, v in data.items():
        if v is None or v == "":
            errors.append(f"[EX-01] {k}: 값이 없습니다.")

    if errors:          # 결측 있으면 범위 검사 생략
        return errors

    # EX-02 범위 초과 확인
    range_rules = {
        "LIMIT_BAL" : (10_000,    1_000_000),
        "SEX"       : (1,         2),
        "EDUCATION" : (1,         4),
        "MARRIAGE"  : (1,         3),
        "AGE"       : (18,        100),
    }
    for key, (lo, hi) in range_rules.items():
        if not (lo <= data[key] <= hi):
            errors.append(f"[EX-02] {key}: {lo} ~ {hi} 범위를 벗어났습니다. (입력값: {data[key]})")

    pay_keys = ["PAY_0","PAY_2","PAY_3","PAY_4","PAY_5","PAY_6"]
    for k in pay_keys:
        if data[k] not in range(-2, 10):
            errors.append(f"[EX-02] {k}: -2 ~ 9 범위를 벗어났습니다. (입력값: {data[k]})")

    amt_keys = [f"BILL_AMT{i}" for i in range(1,7)] + [f"PAY_AMT{i}" for i in range(1,7)]
    for k in amt_keys:
        if not (0 <= data[k] <= 10_000_000):
            errors.append(f"[EX-02] {k}: 0 ~ 10,000,000 범위를 벗어났습니다. (입력값: {data[k]})")

    # EX-03 타입 오류 확인
    all_keys = list(range_rules.keys()) + pay_keys + amt_keys
    for k in all_keys:
        if not isinstance(data[k], (int, float)):
            errors.append(f"[EX-03] {k}: 숫자 타입이어야 합니다. (입력값: {type(data[k]).__name__})")

    return errors


# ──────────────────────────────────────────────────────────────
# FR-05 : 4단계 위험등급 분류
# ──────────────────────────────────────────────────────────────
def classify_risk(p: float) -> dict:
    if p >= 0.7:
        return {
            "grade"  : "위험",
            "level"  : "HIGH RISK",
            "emoji"  : "🔴",
            "tag"    : "error",
            "action" : "신용한도 즉시 정지 / 추심 절차 개시 검토",
            "desc"   : "채무불이행 확률이 70% 이상입니다. 즉각적인 조치가 필요합니다.",
        }
    elif p >= 0.5:
        return {
            "grade"  : "경고",
            "level"  : "WARNING",
            "emoji"  : "🟠",
            "tag"    : "warning",
            "action" : "신용한도 축소 검토 / 집중 모니터링",
            "desc"   : "채무불이행 확률이 50~70%입니다. 신용 관리가 필요합니다.",
        }
    elif p >= 0.3:
        return {
            "grade"  : "주의",
            "level"  : "CAUTION",
            "emoji"  : "🟡",
            "tag"    : "warning",
            "action" : "정기 모니터링 / 추가 심사 권고",
            "desc"   : "채무불이행 확률이 30~50%입니다. 지속적인 모니터링이 필요합니다.",
        }
    else:
        return {
            "grade"  : "안전",
            "level"  : "SAFE",
            "emoji"  : "🟢",
            "tag"    : "success",
            "action" : "정상 거래 유지 / 신용한도 증액 검토",
            "desc"   : "채무불이행 확률이 30% 미만입니다. 정상 거래를 유지하세요.",
        }


# ──────────────────────────────────────────────────────────────
# 화면 상단
# ──────────────────────────────────────────────────────────────
st.title("💳 신용카드 채무불이행 예측 시스템")
st.markdown("고객 정보를 입력하면 **채무불이행 여부**와 **위험등급**을 예측합니다.")
st.caption("🔒 NFR-03: 입력된 고객 정보는 서버에 저장되지 않습니다.")
st.divider()


# ──────────────────────────────────────────────────────────────
# FR-01 : 고객 기본 정보 입력
# ──────────────────────────────────────────────────────────────
st.subheader("📋 고객 기본 정보")
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    LIMIT_BAL = st.number_input(
        "신용한도 (NT$)", min_value=10_000, max_value=1_000_000, value=200_000, step=10_000)
with c2:
    SEX = st.selectbox(
        "성별", options=[1, 2],
        format_func=lambda x: "남성" if x == 1 else "여성")
with c3:
    EDUCATION = st.selectbox(
        "학력", options=[1, 2, 3, 4],
        format_func=lambda x: {1:"대학원", 2:"대학교", 3:"고등학교", 4:"기타"}[x])
with c4:
    MARRIAGE = st.selectbox(
        "결혼여부", options=[1, 2, 3],
        format_func=lambda x: {1:"기혼", 2:"미혼", 3:"기타"}[x])
with c5:
    AGE = st.number_input("나이", min_value=18, max_value=100, value=35)

st.divider()

# ── 납부 현황 ────────────────────────────────────────────────
st.subheader("📅 최근 6개월 납부 현황")
st.caption("-2: 잔액없음  |  -1: 정상납부  |  0: 최소금액납부  |  1~9: 연체개월수")

pay_meta = [
    ("PAY_0","PAY_0 (9월)"), ("PAY_2","PAY_2 (8월)"), ("PAY_3","PAY_3 (7월)"),
    ("PAY_4","PAY_4 (6월)"), ("PAY_5","PAY_5 (5월)"), ("PAY_6","PAY_6 (4월)"),
]
pay_values = {}
for col, (key, label) in zip(st.columns(6), pay_meta):
    with col:
        pay_values[key] = st.selectbox(
            label, options=list(range(-2, 10)), index=2)

st.divider()

# ── 청구금액 ────────────────────────────────────────────────
st.subheader("💰 월별 청구금액 (NT$)")
bill_meta = [
    ("BILL_AMT1","BILL_AMT1 (9월)", 50_000),
    ("BILL_AMT2","BILL_AMT2 (8월)", 48_000),
    ("BILL_AMT3","BILL_AMT3 (7월)", 46_000),
    ("BILL_AMT4","BILL_AMT4 (6월)", 44_000),
    ("BILL_AMT5","BILL_AMT5 (5월)", 42_000),
    ("BILL_AMT6","BILL_AMT6 (4월)", 40_000),
]
bill_values = {}
for col, (key, label, default) in zip(st.columns(6), bill_meta):
    with col:
        bill_values[key] = st.number_input(
            label, min_value=0, max_value=10_000_000, value=default, step=1_000)

st.divider()

# ── 납부금액 ────────────────────────────────────────────────
st.subheader("💵 월별 납부금액 (NT$)")
pay_amt_meta = [
    ("PAY_AMT1","PAY_AMT1 (9월)"),
    ("PAY_AMT2","PAY_AMT2 (8월)"),
    ("PAY_AMT3","PAY_AMT3 (7월)"),
    ("PAY_AMT4","PAY_AMT4 (6월)"),
    ("PAY_AMT5","PAY_AMT5 (5월)"),
    ("PAY_AMT6","PAY_AMT6 (4월)"),
]
pay_amt_values = {}
for col, (key, label) in zip(st.columns(6), pay_amt_meta):
    with col:
        pay_amt_values[key] = st.number_input(
            label, min_value=0, max_value=10_000_000, value=5_000, step=1_000)

st.divider()

# ──────────────────────────────────────────────────────────────
# 예측 버튼
# ──────────────────────────────────────────────────────────────
predict_btn = st.button(
    "🔍 채무불이행 예측하기", type="primary", use_container_width=True)

# ──────────────────────────────────────────────────────────────
# 예측 실행
# ──────────────────────────────────────────────────────────────
if predict_btn:

    input_data = {
        "LIMIT_BAL": LIMIT_BAL, "SEX": SEX,
        "EDUCATION": EDUCATION, "MARRIAGE": MARRIAGE, "AGE": AGE,
        **pay_values, **bill_values, **pay_amt_values,
    }

    # ── FR-02 : 유효성 검사 ──────────────────────────────────
    errors = validate(input_data)
    if errors:
        st.error("⚠ 입력값 오류가 있습니다. 아래 항목을 수정 후 다시 예측해주세요.")
        for err in errors:
            st.warning(err)
        st.stop()   # NFR-07: 앱 종료 없이 오류만 표시 후 대기

    # ── FR-04 : 모델 추론 (NFR-01: 3초 이내 / NFR-06: try-except) ──
    try:
        with st.spinner("예측 중..."):
            df       = pd.DataFrame([input_data])
            proba    = pipeline.predict_proba(df)[0]
            p_ok      = float(proba[0])
            p_default = float(proba[1])

        # NFR-06 : 예측값 범위 검사
        if not (0.0 <= p_default <= 1.0 and 0.0 <= p_ok <= 1.0):
            st.error("✕ 모델 오류 반환: 예측에 실패했습니다.")
            st.stop()

    except Exception as e:
        st.error(f"✕ 모델 오류 반환: {e}")
        st.stop()

    # ── FR-05 : 위험등급 분류 ────────────────────────────────
    risk = classify_risk(p_default)

    # ──────────────────────────────────────────────────────────
    # FR-06 : 결과 출력
    # ──────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 예측 결과")

    col_grade, col_ok, col_def = st.columns(3)

    with col_grade:
        label = f"### {risk['emoji']} 판정: {risk['grade']}  ({risk['level']})"
        if risk["tag"] == "error":
            st.error(label)
        elif risk["tag"] == "warning":
            st.warning(label)
        else:
            st.success(label)

    with col_ok:
        st.metric(label="✅ 정상 확률",          value=f"{p_ok * 100:.1f}%")

    with col_def:
        st.metric(label="⚠ 채무불이행 확률",     value=f"{p_default * 100:.1f}%")

    # 권장조치 – st.info
    st.info(f"💡 **권장조치**: {risk['action']}\n\n{risk['desc']}")

    # 확률 프로그레스 바
    st.markdown("**✅ 정상 확률**")
    st.progress(p_ok)
    st.markdown("**⚠ 채무불이행 확률**")
    st.progress(p_default)

    # ── FR-07 : 입력값 요약 테이블 – st.dataframe ────────────
    st.subheader("📝 입력값 요약")
    summary = pd.DataFrame(
        [(k, v) for k, v in input_data.items()],
        columns=["변수", "입력값"],
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)

    # NFR-03 안내
    st.caption("🔒 위 정보는 예측에만 사용되며 서버에 저장되지 않습니다.")
