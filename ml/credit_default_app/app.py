import streamlit as st
from predict import predict

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="신용카드 채무불이행 예측",
    page_icon="💳",
    layout="wide",
)

# ── 제목 ─────────────────────────────────────────────────────
st.title("💳 신용카드 채무불이행 예측 시스템")
st.markdown("고객 정보를 입력하면 **채무불이행 여부**를 예측합니다.")
st.divider()

# ── 입력 섹션 ────────────────────────────────────────────────
st.subheader("📋 고객 기본 정보")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    LIMIT_BAL = st.number_input(
        "신용한도 (NT$)",
        min_value=10000, max_value=1000000,
        value=200000, step=10000,
    )

with col2:
    SEX = st.selectbox("성별", options=[1, 2], format_func=lambda x: "남성" if x == 1 else "여성")

with col3:
    EDUCATION = st.selectbox(
        "학력",
        options=[1, 2, 3, 4],
        format_func=lambda x: {1: "대학원", 2: "대학교", 3: "고등학교", 4: "기타"}[x],
    )

with col4:
    MARRIAGE = st.selectbox(
        "결혼여부",
        options=[1, 2, 3],
        format_func=lambda x: {1: "기혼", 2: "미혼", 3: "기타"}[x],
    )

with col5:
    AGE = st.number_input("나이", min_value=18, max_value=100, value=35)

st.divider()

# ── 납부 현황 ────────────────────────────────────────────────
st.subheader("📅 최근 6개월 납부 현황")
st.caption("-2: 잔액없음  |  -1: 정상납부  |  0: 최소금액납부  |  1~9: 연체개월수")

pay_cols = st.columns(6)
pay_labels = ["PAY_0 (9월)", "PAY_2 (8월)", "PAY_3 (7월)", "PAY_4 (6월)", "PAY_5 (5월)", "PAY_6 (4월)"]
pay_keys   = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
pay_values = {}

for col, label, key in zip(pay_cols, pay_labels, pay_keys):
    with col:
        pay_values[key] = st.selectbox(label, options=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], index=2)

st.divider()

# ── 청구금액 ────────────────────────────────────────────────
st.subheader("💰 월별 청구금액 (NT$)")
bill_cols = st.columns(6)
bill_labels = ["BILL_AMT1 (9월)", "BILL_AMT2 (8월)", "BILL_AMT3 (7월)",
               "BILL_AMT4 (6월)", "BILL_AMT5 (5월)", "BILL_AMT6 (4월)"]
bill_defaults = [50000, 48000, 46000, 44000, 42000, 40000]
bill_values = {}

for col, label, default in zip(bill_cols, bill_labels, bill_defaults):
    key = label.split()[0]
    with col:
        bill_values[key] = st.number_input(label, min_value=0, max_value=2000000,
                                           value=default, step=1000)

st.divider()

# ── 납부금액 ────────────────────────────────────────────────
st.subheader("💵 월별 납부금액 (NT$)")
pay_amt_cols = st.columns(6)
pay_amt_labels = ["PAY_AMT1 (9월)", "PAY_AMT2 (8월)", "PAY_AMT3 (7월)",
                  "PAY_AMT4 (6월)", "PAY_AMT5 (5월)", "PAY_AMT6 (4월)"]
pay_amt_values = {}

for col, label in zip(pay_amt_cols, pay_amt_labels):
    key = label.split()[0]
    with col:
        pay_amt_values[key] = st.number_input(label, min_value=0, max_value=2000000,
                                              value=5000, step=1000)

st.divider()

# ── 예측 버튼 ────────────────────────────────────────────────
predict_btn = st.button("🔍 채무불이행 예측하기", type="primary", use_container_width=True)

# ── 예측 실행 및 결과 출력 ────────────────────────────────────
if predict_btn:
    input_data = {
        "LIMIT_BAL": LIMIT_BAL,
        "SEX": SEX,
        "EDUCATION": EDUCATION,
        "MARRIAGE": MARRIAGE,
        "AGE": AGE,
        **pay_values,
        **bill_values,
        **pay_amt_values,
    }

    with st.spinner("예측 중..."):
        result = predict(input_data)

    st.divider()
    st.subheader("📊 예측 결과")

    res_col1, res_col2, res_col3 = st.columns(3)

    with res_col1:
        if result["prediction"] == 1:
            st.error(f"### ⚠️ 판정: {result['label']}")
        else:
            st.success(f"### ✅ 판정: {result['label']}")

    with res_col2:
        st.metric(
            label="✅ 정상 확률",
            value=f"{result['probability_ok'] * 100:.1f}%",
        )

    with res_col3:
        st.metric(
            label="⚠️ 채무불이행 확률",
            value=f"{result['probability_default'] * 100:.1f}%",
        )

    # 확률 프로그레스 바
    st.markdown("**정상 확률**")
    st.progress(result["probability_ok"])

    st.markdown("**채무불이행 확률**")
    st.progress(result["probability_default"])

    # 입력값 요약 (접기)
    with st.expander("📝 입력값 요약 보기"):
        st.json(input_data)
