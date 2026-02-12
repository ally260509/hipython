import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Style (tone similar to reference)
# =========================
st.markdown(
"""
<style>
.block-container {max-width: 1350px; padding-top: 1rem;}
.topbar{
  background:#0B5FA5; color:#fff; padding:14px 18px; border-radius:10px;
  font-weight:800; letter-spacing:0.5px; text-align:center;
}
.kpi{
  background:#fff; border:1px solid rgba(0,0,0,0.08); border-radius:12px;
  padding:12px 14px; box-shadow:0 1px 10px rgba(0,0,0,0.03);
}
.kpi-title{font-size:0.85rem; color:rgba(0,0,0,0.60); margin-bottom:6px; font-weight:600;}
.kpi-value{font-size:2.0rem; font-weight:800; margin:0; line-height:1.05;}
.kpi-sub{font-size:0.8rem; color:rgba(0,0,0,0.55); margin-top:6px;}
.panel{
  background:#fff; border:1px solid rgba(0,0,0,0.08); border-radius:12px;
  padding:10px 12px; box-shadow:0 1px 10px rgba(0,0,0,0.03);
}
.panel-title{font-weight:800; margin:6px 0 8px 0;}
[data-testid="stSidebar"]{
  border-right: 1px solid rgba(0,0,0,0.08);
}
[data-testid="stSidebar"] .sidebar-title{
  background:#0B5FA5; color:#fff; padding:10px 12px; border-radius:10px;
  font-weight:800; text-align:center; margin-bottom:10px;
}
.small-note{color:rgba(0,0,0,0.60); font-size:0.85rem;}
</style>
""",
unsafe_allow_html=True
)

# =========================
# Path handling (robust)
# =========================
def safe_path(p: str) -> str:
    return os.path.normpath(str(p).strip().strip('"').strip("'"))

def resolve_path(user_path: str) -> str:
    """
    Robust path resolver:
    - Accepts absolute path
    - Resolves relative to script dir (walmart.py)
    - Resolves relative to CWD
    - Auto-fixes duplicated folder like streamlit_exam\\streamlit_exam\\...
    - If input begins with streamlit_exam\\..., tries stripping that prefix
    - Tries common fallbacks (data/walmart.csv, streamlit_exam/data/walmart.csv)
    """
    p = safe_path(user_path)

    # 1) absolute path
    if os.path.isabs(p) and os.path.exists(p):
        return p

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # walmart.py 위치
    CWD = os.getcwd()

    candidates = []

    # 2) as-is relative to BASE_DIR / CWD
    candidates.append(os.path.join(BASE_DIR, p))
    candidates.append(os.path.join(CWD, p))

    # 3) auto-fix duplicated folder names in the combined paths
    def dedupe_double_folder(path_str: str, folder_name: str) -> str:
        token = f"{os.sep}{folder_name}{os.sep}{folder_name}{os.sep}"
        repl  = f"{os.sep}{folder_name}{os.sep}"
        return path_str.replace(token, repl)

    for base in [BASE_DIR, CWD]:
        candidates.append(dedupe_double_folder(os.path.join(base, p), "streamlit_exam"))

    # 4) If user provided streamlit_exam\... but BASE_DIR already points inside that folder,
    #    try stripping the first "streamlit_exam\" from the input
    parts = p.split(os.sep)
    if len(parts) >= 2 and parts[0].lower() == "streamlit_exam":
        stripped = os.sep.join(parts[1:])
        candidates.append(os.path.join(BASE_DIR, stripped))
        candidates.append(os.path.join(CWD, stripped))

    # 5) Common fallbacks (file-only)
    file_only = os.path.basename(p)
    candidates.extend([
        os.path.join(BASE_DIR, "data", file_only),
        os.path.join(BASE_DIR, "streamlit_exam", "data", file_only),
        os.path.join(CWD, "data", file_only),
        os.path.join(CWD, "streamlit_exam", "data", file_only),
    ])

    # normalize + unique
    uniq, seen = [], set()
    for c in candidates:
        c = os.path.normpath(c)
        if c not in seen:
            uniq.append(c)
            seen.add(c)

    for c in uniq:
        if os.path.exists(c):
            return c

    # detailed error
    preview = "\n".join([f"- {c}" for c in uniq[:10]])
    raise FileNotFoundError(
        "경로에 파일이 없습니다.\n"
        f"입력값: {user_path}\n\n"
        "확인한 후보 경로(상위 10개):\n"
        f"{preview}\n\n"
        "가장 확실한 해결:\n"
        "1) 좌측 업로드로 CSV 넣기\n"
        "2) 절대경로 입력 (예: C:\\Users\\...\\walmart.csv)\n"
        "3) 또는 Data path에 'data\\walmart.csv' 입력"
    )

@st.cache_data
def load_csv_any(path_or_uploaded):
    if hasattr(path_or_uploaded, "read"):  # uploaded file object
        return pd.read_csv(path_or_uploaded)
    real_path = resolve_path(path_or_uploaded)
    return pd.read_csv(real_path)

# =========================
# Analytics helpers
# =========================
def fmt_k(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "-"
    x = float(x)
    ax = abs(x)
    if ax >= 1e9:  return f"{x/1e9:.2f}B"
    if ax >= 1e6:  return f"{x/1e6:.2f}M"
    if ax >= 1e3:  return f"{x/1e3:.2f}K"
    return f"{x:.0f}"

def age_to_grp(age_str: str) -> str:
    s = str(age_str)
    if s == "0-17": return "0–17"
    if s == "18-25": return "18–25"
    if s == "26-35": return "26–35"
    if s == "36-45": return "36–45"
    if s in ["46-50", "51-55", "55+"]: return "46+"
    return "Unknown"

def age_mid(age_str: str) -> float:
    s = str(age_str)
    mapping = {
        "0-17": 8.5, "18-25": 21.5, "26-35": 30.5, "36-45": 40.5,
        "46-50": 48.0, "51-55": 53.0, "55+": 58.0
    }
    return mapping.get(s, np.nan)

def minmax(s):
    return (s - s.min()) / (s.max() - s.min() + 1e-9)

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    if "Purchase" not in df.columns:
        raise ValueError(f"필수 컬럼 'Purchase'가 없습니다. 현재 컬럼 예시: {list(df.columns)[:20]}")

    df = df.copy()
    df["log_purchase"] = np.log1p(df["Purchase"])

    if "Age" in df.columns:
        df["Age_grp"] = df["Age"].apply(age_to_grp)
        df["Age_mid"] = df["Age"].apply(age_mid)
    else:
        df["Age_grp"] = "Unknown"
        df["Age_mid"] = np.nan

    if "Gender" not in df.columns:
        df["Gender"] = "Unknown"

    # Price segment from Purchase quantiles
    q1, q2 = df["Purchase"].quantile([0.33, 0.66]).values
    df["Price_Segment"] = pd.cut(
        df["Purchase"],
        bins=[-np.inf, q1, q2, np.inf],
        labels=["Price_Low", "Price_Mid", "Price_High"]
    ).astype(str)

    # Occupation group from Occupation mean(log_purchase)
    if "Occupation" in df.columns:
        occ_mean = df.groupby("Occupation")["log_purchase"].mean()
        o1, o2 = occ_mean.quantile([0.33, 0.66]).values

        def occ_group(occ):
            m = occ_mean.get(occ, np.nan)
            if np.isnan(m):
                return "Occ_Other"
            if m <= o1:
                return "Occ_Low"
            elif m <= o2:
                return "Occ_Mid"
            else:
                return "Occ_High"

        df["Occupation_grp"] = df["Occupation"].apply(occ_group)
    else:
        df["Occupation_grp"] = "Occ_Other"

    # Strategy bucket rule
    def bucketize_from_parts(occ_grp: str, price_seg: str) -> str:
        if (occ_grp == "Occ_High") and (price_seg == "Price_High"):
            return "Defend"
        if (occ_grp == "Occ_Mid") and (price_seg == "Price_Mid"):
            return "Grow"
        if (occ_grp in ["Occ_Mid", "Occ_High"]) and (price_seg == "Price_Low"):
            return "Expand"
        return "Other"

    df["bucket"] = [bucketize_from_parts(o, p) for o, p in zip(df["Occupation_grp"], df["Price_Segment"])]

    df["Segment_AGOP"] = df[["Age_grp", "Gender", "Occupation_grp", "Price_Segment"]].astype(str).agg(" | ".join, axis=1)
    return df

@st.cache_data
def build_segment_table(df: pd.DataFrame) -> pd.DataFrame:
    customers = ("User_ID", "nunique") if "User_ID" in df.columns else ("Segment_AGOP", "size")

    seg = (
        df.groupby("Segment_AGOP")
          .agg(
              customers=customers,
              transactions=("Segment_AGOP", "size"),
              revenue=("Purchase", "sum"),
              avg_purchase=("Purchase", "mean"),
              median_purchase=("Purchase", "median"),
          )
          .reset_index()
    )
    seg["revenue_share"] = seg["revenue"] / seg["revenue"].sum()

    def bucketize(seg_str: str):
        if ("Occ_High" in seg_str) and ("Price_High" in seg_str):
            return "Defend"
        if ("Occ_Mid" in seg_str) and ("Price_Mid" in seg_str):
            return "Grow"
        if (("Occ_Mid" in seg_str) or ("Occ_High" in seg_str)) and ("Price_Low" in seg_str):
            return "Expand"
        return "Other"

    seg["bucket"] = seg["Segment_AGOP"].apply(bucketize)

    seg["rev_n"]  = minmax(seg["revenue"])
    seg["cust_n"] = minmax(seg["customers"])
    seg["tx_n"]   = minmax(seg["transactions"])
    seg["aov_n"]  = minmax(seg["avg_purchase"])

    seg["target_score"] = 0.45*seg["rev_n"] + 0.25*seg["cust_n"] + 0.20*seg["tx_n"] + 0.10*seg["aov_n"]
    return seg

def calc_kpis(df: pd.DataFrame):
    customers = df["User_ID"].nunique() if "User_ID" in df.columns else len(df)
    transactions = len(df)
    revenue = df["Purchase"].sum()
    aov = df["Purchase"].mean()
    avg_purchases = (transactions / customers) if customers else np.nan
    clv_proxy = (revenue / customers) if customers else np.nan
    return customers, revenue, aov, avg_purchases, clv_proxy

# =========================
# Sidebar
# =========================
st.sidebar.markdown('<div class="sidebar-title">FILTERS</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="small-note">경로 문제 방지를 위해 기본값은 data\\walmart.csv 입니다.</div>', unsafe_allow_html=True)

# ✅ Fix: default path set to "data\\walmart.csv"
default_path = r"data\walmart.csv"
path = st.sidebar.text_input("Data path", value=default_path)
up = st.sidebar.file_uploader("or Upload CSV", type=["csv"])

try:
    raw = load_csv_any(up) if up is not None else load_csv_any(path)
    # show resolved absolute path for transparency
    if up is None:
        st.sidebar.success(f"Loaded file:\n{resolve_path(path)}")
    else:
        st.sidebar.success("Loaded file: (uploaded)")
    df = preprocess(raw)
except Exception as e:
    st.error(str(e))
    st.stop()

st.sidebar.markdown("---")
bucket = st.sidebar.selectbox("Strategy Bucket", ["All", "Defend", "Grow", "Expand", "Other"], index=0)
rank_by = st.sidebar.selectbox(
    "Ranking Metric",
    ["target_score", "revenue", "revenue_share", "customers", "transactions", "avg_purchase"],
    index=0
)
min_tx = st.sidebar.slider("MIN_TX (min transactions per segment)", 200, 3000, 500, 50)
top_n = st.sidebar.selectbox("Top N", [10, 20, 50, 100], index=1)

st.sidebar.markdown("---")
st.sidebar.markdown("### Demographics / Context")

def pick(df_, col, label):
    if col not in df_.columns:
        return "All"
    opts = ["All"] + sorted(df_[col].dropna().unique().tolist())
    return st.sidebar.selectbox(label, opts, index=0)

f_age = pick(df, "Age", "Age (raw)")
f_gender = pick(df, "Gender", "Gender")
f_marital = pick(df, "Marital_Status", "Marital (0/1)")
f_city = pick(df, "City_Category", "City_Category")
f_stay = pick(df, "Stay_In_Current_City_Years", "Stay Years")

# Apply row filters
df_f = df.copy()
if f_age != "All": df_f = df_f[df_f["Age"] == f_age]
if f_gender != "All": df_f = df_f[df_f["Gender"] == f_gender]
if f_marital != "All" and "Marital_Status" in df_f.columns: df_f = df_f[df_f["Marital_Status"] == f_marital]
if f_city != "All" and "City_Category" in df_f.columns: df_f = df_f[df_f["City_Category"] == f_city]
if f_stay != "All" and "Stay_In_Current_City_Years" in df_f.columns: df_f = df_f[df_f["Stay_In_Current_City_Years"] == f_stay]

seg = build_segment_table(df_f)
seg_f = seg[seg["transactions"] >= min_tx].copy()
if bucket != "All":
    seg_f = seg_f[seg_f["bucket"] == bucket].copy()
seg_f = seg_f.sort_values(rank_by, ascending=False)

# =========================
# Main UI
# =========================
st.markdown('<div class="topbar">CUSTOMER SEGMENTATION DASHBOARD</div>', unsafe_allow_html=True)

customers, revenue, aov, avg_purchases, clv_proxy = calc_kpis(df_f)
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi">
      <div class="kpi-title">Total Customers</div>
      <div class="kpi-value">{fmt_k(customers)}</div>
      <div class="kpi-sub">Unique customers (User_ID)</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi">
      <div class="kpi-title">Total Gross Sales</div>
      <div class="kpi-value">{fmt_k(revenue)}</div>
      <div class="kpi-sub">Sum of Purchase</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi">
      <div class="kpi-title">Avg Order Value (AOV)</div>
      <div class="kpi-value">{fmt_k(aov)}</div>
      <div class="kpi-sub">Mean Purchase per transaction</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi">
      <div class="kpi-title">Avg No. of Purchases</div>
      <div class="kpi-value">{avg_purchases:.2f}</div>
      <div class="kpi-sub">Transactions / Customers</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi">
      <div class="kpi-title">Customer Value (Proxy)</div>
      <div class="kpi-value">{fmt_k(clv_proxy)}</div>
      <div class="kpi-sub">Gross Sales / Customers</div>
    </div>""", unsafe_allow_html=True)

st.write("")

# Charts (reference-like layout)
row1_left, row1_right = st.columns([1.05, 1.25])

with row1_left:
    st.markdown('<div class="panel"><div class="panel-title">Total Amount Spent by Strategy Bucket</div>', unsafe_allow_html=True)
    bucket_rev = (
        seg.groupby("bucket")["revenue"].sum()
           .sort_values(ascending=False)
           .reset_index()
    )
    fig = px.bar(bucket_rev, x="bucket", y="revenue", text=bucket_rev["revenue"].apply(fmt_k))
    fig.update_traces(textposition="outside")
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Gross Sales", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with row1_right:
    st.markdown('<div class="panel"><div class="panel-title">Bucket Spend by Age (Raw Age as X-axis)</div>', unsafe_allow_html=True)
    if df_f["Age_mid"].notna().any():
        age_bucket = (
            df_f.dropna(subset=["Age_mid"])
               .groupby(["Age_mid", "bucket"])["Purchase"].sum()
               .reset_index()
               .sort_values("Age_mid")
        )
        fig2 = px.line(age_bucket, x="Age_mid", y="Purchase", color="bucket", markers=True)
        fig2.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10),
                           xaxis_title="Age (approx midpoint)", yaxis_title="Gross Sales")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Age 컬럼이 없어 추세 차트를 표시할 수 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

row2_left, row2_right = st.columns([1.05, 1.25])

with row2_left:
    st.markdown('<div class="panel"><div class="panel-title">Total Customers by Strategy Bucket</div>', unsafe_allow_html=True)
    if "User_ID" in df_f.columns:
        cust_bucket = df_f.groupby("bucket")["User_ID"].nunique().reset_index(name="customers")
    else:
        cust_bucket = df_f.groupby("bucket").size().reset_index(name="customers")
    fig3 = px.pie(cust_bucket, names="bucket", values="customers", hole=0.25)
    fig3.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with row2_right:
    st.markdown('<div class="panel"><div class="panel-title">Revenue Breakdown (Bucket → Top Product Categories)</div>', unsafe_allow_html=True)
    if "Product_Category" in df_f.columns:
        top_pc = df_f.groupby(["bucket", "Product_Category"])["Purchase"].sum().reset_index()
        top_pc["rank"] = top_pc.groupby("bucket")["Purchase"].rank(method="first", ascending=False)
        top_pc = top_pc[top_pc["rank"] <= 8].copy()
        fig4 = px.bar(
            top_pc.sort_values(["bucket", "Purchase"], ascending=[True, False]),
            x="Purchase",
            y=top_pc["Product_Category"].astype(str),
            color="bucket",
            orientation="h"
        )
        fig4.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10),
                           xaxis_title="Gross Sales", yaxis_title="Product_Category (Top 8 per bucket)")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Product_Category 컬럼이 없어 Revenue Breakdown을 표시할 수 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# Targets
st.write("")
st.markdown('<div class="panel"><div class="panel-title">Top Targets (Segment_AGOP)</div>', unsafe_allow_html=True)

if len(seg_f) == 0:
    st.info("현재 필터 조건에서 세그먼트가 없습니다. MIN_TX 또는 필터를 조정하세요.")
else:
    cA, cB = st.columns(2)
    top1 = seg_f.iloc[0]
    with cA:
        st.markdown("**Top Target (Current Ranking)**")
        st.code(top1["Segment_AGOP"])
        st.write(f"- Bucket: **{top1['bucket']}**")
        st.write(f"- Customers: {int(top1['customers']):,}")
        st.write(f"- Transactions: {int(top1['transactions']):,}")
        st.write(f"- Gross Sales: {fmt_k(top1['revenue'])} | Share: {top1['revenue_share']:.2%}")
        st.write(f"- AOV: {top1['avg_purchase']:.2f} | Median: {top1['median_purchase']:.2f}")
        st.write(f"- Target Score: {top1['target_score']:.3f}")

    exp = seg_f[seg_f["bucket"] == "Expand"].sort_values("revenue", ascending=False)
    with cB:
        st.markdown("**Urgent Target (Expand • Gross Sales TOP)**")
        if len(exp) == 0:
            st.write("Expand 세그먼트가 없습니다.")
        else:
            urgent = exp.iloc[0]
            st.code(urgent["Segment_AGOP"])
            st.write(f"- Bucket: **{urgent['bucket']}**")
            st.write(f"- Customers: {int(urgent['customers']):,}")
            st.write(f"- Transactions: {int(urgent['transactions']):,}")
            st.write(f"- Gross Sales: {fmt_k(urgent['revenue'])} | Share: {urgent['revenue_share']:.2%}")
            st.write(f"- AOV: {urgent['avg_purchase']:.2f} | Median: {urgent['median_purchase']:.2f}")
            st.write(f"- Target Score: {urgent['target_score']:.3f}")

    st.markdown("---")
    cols = ["Segment_AGOP", "bucket", "customers", "transactions", "revenue", "revenue_share",
            "avg_purchase", "median_purchase", "target_score"]
    table = seg_f[cols].head(top_n).copy()
    st.dataframe(table, use_container_width=True, hide_index=True)

    csv = table.to_csv(index=False).encode("utf-8-sig")
    st.download_button("Download Top-N CSV", data=csv, file_name="top_targets.csv", mime="text/csv")

st.markdown('</div>', unsafe_allow_html=True)
st.caption("Note: raw walmart.csv(Black Friday 형태) 기준 자동으로 Age_grp/Price_Segment/Occupation_grp/Segment_AGOP를 생성합니다.")
