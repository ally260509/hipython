import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - Power BI 스타일
st.markdown("""
<style>
    /* 전체 배경 */
    .main {
        background-color: #f5f5f5;
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label {
        color: #333333;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* 헤더 스타일 */
    .dashboard-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
        letter-spacing: 1px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* 필터 헤더 */
    .filter-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 1rem;
    }
    
    /* KPI 카드 스타일 */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 1.2rem;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 4px solid #2563eb;
    }
    
    div[data-testid="stMetric"] label {
        color: #666666 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    /* 섹션 타이틀 */
    .section-title {
        color: #1a1a1a;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2563eb;
    }
    
    /* 차트 컨테이너 */
    .chart-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1.5rem;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f5f5f5;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        color: #666666;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2563eb;
        color: white;
    }
    
    /* 데이터프레임 스타일 */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background-color: #1e40af;
    }
    
    /* 셀렉트박스 스타일 */
    .stSelectbox, .stMultiSelect {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로딩 및 전처리 함수
@st.cache_data
def load_and_process_data():
    """데이터 로드 및 세그먼테이션 처리"""
    df = pd.read_csv('./data/walmart.csv')
    
    # 연령 그룹 정리
    age_order = ['0-17', '18-25', '26-35', '36-45', '46-50', '51-55', '55+']
    df['Age_grp'] = pd.Categorical(df['Age'], categories=age_order, ordered=True)
    
    # Occupation 그룹핑 (직업 코드별 평균 구매액 기준)
    occ_avg = df.groupby('Occupation')['Purchase'].mean()
    occ_terciles = pd.qcut(occ_avg, q=3, labels=['Occ_Low', 'Occ_Mid', 'Occ_High'])
    occ_map = occ_terciles.to_dict()
    df['Occupation_grp'] = df['Occupation'].map(occ_map)
    
    # Price Segment (구매액 기준)
    df['Price_Segment'] = pd.qcut(df['Purchase'], q=3, labels=['Price_Low', 'Price_Mid', 'Price_High'])
    
    # 세그먼트 생성
    seg_cols = ['Age_grp', 'Gender', 'Occupation_grp', 'Price_Segment']
    df['Segment_AGOP'] = df[seg_cols].astype(str).agg(' | '.join, axis=1)
    
    return df

@st.cache_data
def create_segment_summary(df):
    """세그먼트별 요약 통계"""
    seg_summary = (
        df.groupby('Segment_AGOP')
        .agg(
            customers=('User_ID', 'nunique'),
            transactions=('Segment_AGOP', 'size'),
            revenue=('Purchase', 'sum'),
            avg_purchase=('Purchase', 'mean'),
            median_purchase=('Purchase', 'median')
        )
        .reset_index()
    )
    
    # 매출 비중 계산
    total_revenue = seg_summary['revenue'].sum()
    seg_summary['revenue_share'] = seg_summary['revenue'] / total_revenue
    
    # 타겟 스코어 계산
    seg_summary['target_score'] = (
        seg_summary['revenue_share'] * 
        (seg_summary['avg_purchase'] / seg_summary['avg_purchase'].max())
    )
    
    # 버킷 분류
    def bucketize(seg_str):
        if ('Occ_High' in seg_str) and ('Price_High' in seg_str):
            return 'Defend'
        if ('Occ_Mid' in seg_str) and ('Price_Mid' in seg_str):
            return 'Grow'
        if (('Occ_Mid' in seg_str) or ('Occ_High' in seg_str)) and ('Price_Low' in seg_str):
            return 'Expand'
        return 'Other'
    
    seg_summary['bucket'] = seg_summary['Segment_AGOP'].apply(bucketize)
    
    return seg_summary

# 데이터 로드
df = load_and_process_data()
seg_summary = create_segment_summary(df)

# 버킷별 색상 매핑
bucket_colors = {
    'Defend': '#dc2626',
    'Grow': '#2563eb',
    'Expand': '#16a34a'
}

# 사이드바 - 필터
with st.sidebar:
    st.markdown('<div class="filter-header">FILTERS</div>', unsafe_allow_html=True)
    
    # 날짜 필터 (시각적으로만)
    st.markdown("**Date**")
    st.markdown("📅 2023 전체")
    st.markdown("")
    
    # City Category 필터
    st.markdown("**City Category**")
    city_options = ['All'] + sorted(df['City_Category'].unique().tolist())
    selected_city = st.selectbox("도시 카테고리", city_options, label_visibility="collapsed")
    
    st.markdown("")
    
    # 성별 필터
    st.markdown("**Gender**")
    gender_options = ['All', 'M', 'F']
    selected_gender = st.selectbox("성별", gender_options, label_visibility="collapsed")
    
    st.markdown("")
    
    # 연령대 필터
    st.markdown("**Age Group**")
    age_options = ['All'] + ['0-17', '18-25', '26-35', '36-45', '46-50', '51-55', '55+']
    selected_age = st.selectbox("연령대", age_options, label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("""
    <div style='padding: 1rem; background-color: #f0f9ff; border-radius: 6px; border-left: 3px solid #2563eb;'>
        <p style='margin: 0; font-size: 0.85rem; color: #1e40af; font-weight: 600;'>Strategy Buckets</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #334155;'>
            <strong>Defend:</strong> 충성고객<br>
            <strong>Grow:</strong> 성장 고객 (업셀 전략)<br>
            <strong>Expand:</strong> 잠재고객 (프로모션, 크로스셀 전략)
        </p>
    </div>
    """, unsafe_allow_html=True)

# 메인 컨텐츠
st.markdown('<div class="dashboard-header">CUSTOMER SEGMENTATION DASHBOARD</div>', unsafe_allow_html=True)

# 필터 적용
filtered_df = df.copy()
if selected_city != 'All':
    filtered_df = filtered_df[filtered_df['City_Category'] == selected_city]
if selected_gender != 'All':
    filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
if selected_age != 'All':
    filtered_df = filtered_df[filtered_df['Age'] == selected_age]

# 필터링된 데이터로 세그먼트 재계산
filtered_seg = create_segment_summary(filtered_df)

# KPI 섹션 - 4개만
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_customers = filtered_df['User_ID'].nunique()
    st.metric("Total Customers", f"{total_customers:,}")

with col2:
    total_revenue = filtered_df['Purchase'].sum()
    st.metric("Total Revenue", f"{total_revenue:,}")

with col3:
    avg_revenue = filtered_df.groupby('User_ID')['Purchase'].sum().mean()
    st.metric("AVG Revenue", f"{avg_revenue:,.0f}")

with col4:
    avg_order_value = filtered_df['Purchase'].mean()
    st.metric("Avg Order Value", f"{avg_order_value:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# 메인 차트 섹션
col1, col2 = st.columns([1, 1])

with col1:
    # Total Amount Spent by Segment - 세그먼트별 다른 색상
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    bucket_revenue = filtered_seg[filtered_seg['bucket'] != 'Other'].groupby('bucket')['revenue'].sum().reset_index()
    bucket_revenue = bucket_revenue.sort_values('revenue', ascending=False)
    
    # 버킷별 색상 리스트
    colors = [bucket_colors.get(bucket, '#999999') for bucket in bucket_revenue['bucket']]
    
    fig_amount = go.Figure(data=[
        go.Bar(
            x=bucket_revenue['bucket'],
            y=bucket_revenue['revenue'],
            marker_color=colors,
            text=bucket_revenue['revenue'].apply(lambda x: f"{x/1e6:.0f}M"),
            textposition='outside',
            textfont=dict(size=12, color='#1a1a1a', family='Arial Black')
        )
    ])
    
    fig_amount.update_layout(
        title={
            'text': 'Total Amount Spent by Segment',
            'font': {'size': 16, 'color': '#1a1a1a', 'family': 'Arial'}
        },
        xaxis_title='',
        yaxis_title='',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f0f0f0',
            tickformat=',.0f',
            tickfont=dict(size=11, color='#666666')
        ),
        xaxis=dict(
            tickfont=dict(size=12, color='#1a1a1a')
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig_amount, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Segment Wise Growth Rate (모의 데이터)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # 주별 성장률 시뮬레이션
    import numpy as np
    weeks = list(range(26, 40))
    
    # 각 버킷별 성장 패턴 생성
    np.random.seed(42)
    grow_growth = [15000 + i*500 + np.random.randint(-1000, 1000) for i in range(len(weeks))]
    defend_growth = [3000 + i*50 + np.random.randint(-200, 200) for i in range(len(weeks))]
    expand_growth = [10000 + i*300 + np.random.randint(-500, 500) for i in range(len(weeks))]
    
    fig_growth = go.Figure()
    
    fig_growth.add_trace(go.Scatter(
        x=weeks, y=grow_growth,
        mode='lines+markers',
        name='Grow',
        line=dict(color=bucket_colors['Grow'], width=3),
        marker=dict(size=6)
    ))
    
    fig_growth.add_trace(go.Scatter(
        x=weeks, y=defend_growth,
        mode='lines+markers',
        name='Defend',
        line=dict(color=bucket_colors['Defend'], width=3),
        marker=dict(size=6)
    ))
    
    fig_growth.add_trace(go.Scatter(
        x=weeks, y=expand_growth,
        mode='lines+markers',
        name='Expand',
        line=dict(color=bucket_colors['Expand'], width=3),
        marker=dict(size=6)
    ))
    
    fig_growth.update_layout(
        title={
            'text': 'Segment Wise Growth Rate',
            'font': {'size': 16, 'color': '#1a1a1a'}
        },
        xaxis_title='',
        yaxis_title='',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f0f0f0',
            tickformat=',.0f',
            tickfont=dict(size=11, color='#666666')
        ),
        xaxis=dict(
            tickfont=dict(size=11, color='#666666')
        )
    )
    
    st.plotly_chart(fig_growth, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 하단 차트 섹션
col1, col2 = st.columns([1, 2])

with col1:
    # Total Customers by Segment (Pie Chart)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    bucket_customers = filtered_seg[filtered_seg['bucket'] != 'Other'].groupby('bucket')['customers'].sum().reset_index()
    
    # 색상 매핑
    colors = [bucket_colors.get(b, '#999999') for b in bucket_customers['bucket']]
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=bucket_customers['bucket'],
        values=bucket_customers['customers'],
        hole=0.5,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textfont=dict(size=12, color='white'),
        showlegend=True
    )])
    
    fig_pie.update_layout(
        title={
            'text': 'Total Customers by Segment',
            'font': {'size': 16, 'color': '#1a1a1a'}
        },
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.1
        ),
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Revenue Breakdown with Tabs
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["AVG. Revenue", "AVG. Order Value", "Avg. No. of Purchases"])
    
    with tab1:
        # AVG. Revenue by Segment
        bucket_avg_revenue = filtered_seg[filtered_seg['bucket'] != 'Other'].copy()
        bucket_avg_revenue['avg_revenue_per_customer'] = bucket_avg_revenue['revenue'] / bucket_avg_revenue['customers']
        bucket_avg_revenue = bucket_avg_revenue.sort_values('avg_revenue_per_customer', ascending=True)
        
        colors = [bucket_colors.get(b, '#999999') for b in bucket_avg_revenue['bucket']]
        
        fig_avg_rev = go.Figure(data=[
            go.Bar(
                y=bucket_avg_revenue['bucket'],
                x=bucket_avg_revenue['avg_revenue_per_customer'],
                orientation='h',
                marker_color=colors,
                text=bucket_avg_revenue['avg_revenue_per_customer'].apply(lambda x: f"{x/1e3:.1f}K"),
                textposition='outside',
                textfont=dict(size=11)
            )
        ])
        
        fig_avg_rev.update_layout(
            title='AVG. Revenue by Segment',
            height=300,
            margin=dict(l=100, r=20, t=40, b=20),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='#f0f0f0',
                tickformat=',.0f'
            ),
            yaxis=dict(
                tickfont=dict(size=10)
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig_avg_rev, use_container_width=True)
    
    with tab2:
        # AVG. Order Value by Segment
        bucket_aov = filtered_seg[filtered_seg['bucket'] != 'Other'].copy()
        bucket_aov = bucket_aov.sort_values('avg_purchase', ascending=True)
        
        colors = [bucket_colors.get(b, '#999999') for b in bucket_aov['bucket']]
        
        fig_aov = go.Figure(data=[
            go.Bar(
                y=bucket_aov['bucket'],
                x=bucket_aov['avg_purchase'],
                orientation='h',
                marker_color=colors,
                text=bucket_aov['avg_purchase'].apply(lambda x: f"{x/1e3:.1f}K"),
                textposition='outside'
            )
        ])
        
        fig_aov.update_layout(
            title='AVG. Order Value by Segment',
            height=300,
            margin=dict(l=100, r=20, t=40, b=20),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            showlegend=False
        )
        
        st.plotly_chart(fig_aov, use_container_width=True)
    
    with tab3:
        # Avg. No. of Purchases by Segment
        bucket_freq = filtered_seg[filtered_seg['bucket'] != 'Other'].copy()
        bucket_freq['avg_purchases_per_customer'] = bucket_freq['transactions'] / bucket_freq['customers']
        bucket_freq = bucket_freq.sort_values('avg_purchases_per_customer', ascending=True)
        
        colors = [bucket_colors.get(b, '#999999') for b in bucket_freq['bucket']]
        
        fig_freq = go.Figure(data=[
            go.Bar(
                y=bucket_freq['bucket'],
                x=bucket_freq['avg_purchases_per_customer'],
                orientation='h',
                marker_color=colors,
                text=bucket_freq['avg_purchases_per_customer'].apply(lambda x: f"{x:.1f}"),
                textposition='outside'
            )
        ])
        
        fig_freq.update_layout(
            title='Avg. No. of Purchases by Segment',
            height=300,
            margin=dict(l=100, r=20, t=40, b=20),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            showlegend=False
        )
        
        st.plotly_chart(fig_freq, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 상위 타겟 세그먼트 테이블
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Top Priority Target Segments</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Defend", "Grow", "Expand"])

with tab1:
    defend_top = (
        filtered_seg[filtered_seg['bucket'] == 'Defend']
        .sort_values('target_score', ascending=False)
        .head(5)
    )
    
    if not defend_top.empty:
        st.markdown("**최고 가치 고객 - 관계 유지 및 VIP 혜택 제공**")
        
        display_cols = ['Segment_AGOP', 'customers', 'transactions', 'revenue', 'avg_purchase', 'target_score']
        defend_display = defend_top[display_cols].copy()
        defend_display['revenue'] = defend_display['revenue'].apply(lambda x: f"${x:,.0f}")
        defend_display['avg_purchase'] = defend_display['avg_purchase'].apply(lambda x: f"${x:,.0f}")
        defend_display['target_score'] = defend_display['target_score'].apply(lambda x: f"{x:.3f}")
        
        defend_display.columns = ['Segment', 'Customers', 'Transactions', 'Revenue', 'Avg Purchase', 'Target Score']
        
        st.dataframe(defend_display, use_container_width=True, hide_index=True)

with tab2:
    grow_top = (
        filtered_seg[filtered_seg['bucket'] == 'Grow']
        .sort_values('target_score', ascending=False)
        .head(5)
    )
    
    if not grow_top.empty:
        st.markdown("**성장 잠재력 고객 - 프로모션 및 크로스셀 기회**")
        
        display_cols = ['Segment_AGOP', 'customers', 'transactions', 'revenue', 'avg_purchase', 'target_score']
        grow_display = grow_top[display_cols].copy()
        grow_display['revenue'] = grow_display['revenue'].apply(lambda x: f"${x:,.0f}")
        grow_display['avg_purchase'] = grow_display['avg_purchase'].apply(lambda x: f"${x:,.0f}")
        grow_display['target_score'] = grow_display['target_score'].apply(lambda x: f"{x:.3f}")
        
        grow_display.columns = ['Segment', 'Customers', 'Transactions', 'Revenue', 'Avg Purchase', 'Target Score']
        
        st.dataframe(grow_display, use_container_width=True, hide_index=True)

with tab3:
    expand_top = (
        filtered_seg[filtered_seg['bucket'] == 'Expand']
        .sort_values('target_score', ascending=False)
        .head(5)
    )
    
    if not expand_top.empty:
        st.markdown("**확장 기회 고객 - 업셀링 및 가치 제안**")
        
        display_cols = ['Segment_AGOP', 'customers', 'transactions', 'revenue', 'avg_purchase', 'target_score']
        expand_display = expand_top[display_cols].copy()
        expand_display['revenue'] = expand_display['revenue'].apply(lambda x: f"${x:,.0f}")
        expand_display['avg_purchase'] = expand_display['avg_purchase'].apply(lambda x: f"${x:,.0f}")
        expand_display['target_score'] = expand_display['target_score'].apply(lambda x: f"{x:.3f}")
        
        expand_display.columns = ['Segment', 'Customers', 'Transactions', 'Revenue', 'Avg Purchase', 'Target Score']
        
        st.dataframe(expand_display, use_container_width=True, hide_index=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #999; padding: 1rem; font-size: 0.85rem;'>
    <p>Customer Segmentation Dashboard | Data updated: Feb 12, 2026</p>
</div>
""", unsafe_allow_html=True)