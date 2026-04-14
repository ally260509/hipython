import streamlit as st
from search.stock_search import stock_search
from stock_info.stock_info import Stock as StockInfo
from report_service.investment_report import investment_report

class SearchResult:
    def __init__(self, item):
        self.item = item

    @property
    def symbol(self):
        return self.item['Symbol']

    @property
    def name(self):
        return self.item['Name']

    def __str__(self):
        return f'{self.symbol}: {self.name}'


st.title('KOSPI 종목 투자 보고서')
search_query = st.text_input('회사명', '삼성전자')

hits_list = stock_search(search_query)['hits']
if not hits_list:
    st.warning('검색 결과가 없습니다.')
    st.stop()

search_results = [SearchResult(hit) for hit in hits_list]
selected = st.selectbox('검색 결과 목록', search_results)

stock = StockInfo(selected.symbol)

# ── 기본정보 ──────────────────────────────────
st.header(f'{selected.name} 기본정보')
st.markdown(stock.get_basic_info())

# ── 주가 정보 ─────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.subheader('52주 가격 범위')
    st.markdown(stock.get_52week_range())
with col2:
    st.subheader('거래량')
    st.markdown(stock.get_volume_info())

st.subheader('과거 주가 (3년 월봉)')
st.markdown(stock.get_price_history())

# ── 투자 지표 ─────────────────────────────────
col3, col4 = st.columns(2)
with col3:
    st.subheader('주요 지표')
    st.markdown(stock.get_key_metrics())
with col4:
    st.subheader('재무 건전성')
    st.markdown(stock.get_financial_health())

# ── 배당 정보 ─────────────────────────────────
st.subheader('배당 정보')
st.markdown(stock.get_dividend_info())

# ── 애널리스트 목표주가 ───────────────────────
st.subheader('애널리스트 목표주가')
st.markdown(stock.get_analyst_target())

# ── 기관/내부자 보유 ──────────────────────────
st.subheader('기관/내부자 보유 현황')
st.markdown(stock.get_holders_info())

# ── 자사주 매입 ───────────────────────────────
st.subheader('자사주 매입')
st.markdown(stock.get_buyback_info())

# ── 최근 뉴스 ─────────────────────────────────
st.subheader('최근 뉴스')
st.markdown(stock.get_news())

# ── 주식 분할 이력 ────────────────────────────
st.subheader('주식 분할 이력')
st.markdown(stock.get_stock_splits())

# ── 재무제표 (DART) ───────────────────────────
st.header('재무제표')
with st.spinner('재무제표 불러오는 중...'):
    st.markdown(stock.get_financial_statement())

# ── 투자 보고서 ───────────────────────────────
st.header('AI 투자 보고서')
if st.button('보고서 생성'):
    with st.spinner('AI 투자 보고서 작성 중...'):
        report = investment_report(selected.symbol, selected.name, stock)
    st.markdown(report)
