import yfinance as yf
import pandas as pd
import dart_fss as dart
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()
dart.set_api_key(os.environ['DART_KEY'])

@lru_cache(maxsize=1)
def _get_corp_list():
    return dart.get_corp_list()

class Stock:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(f"{symbol}.KS")
        corp_list = _get_corp_list()
        results = corp_list.find_by_stock_code(symbol)
        self.corp = results if results else None

    def get_basic_info(self) -> str:
        info = self.ticker.info
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 0)
        fields = {
            '회사명':    info.get('longName', 'N/A'),
            '산업':      info.get('industry', 'N/A'),
            '섹터':      info.get('sector', 'N/A'),
            '시가총액':  f"{market_cap/1_0000_0000_0000:.0f}조" if market_cap else 'N/A',
            '발행주식수': f"{shares:,}" if shares else 'N/A',
        }
        df = pd.DataFrame.from_dict(fields, orient='index', columns=['Value'])
        df.index.name = '항목'
        return df.to_markdown()

    def get_price_history(self, period="3y", interval="1mo") -> str:
        hist = self.ticker.history(period=period, interval=interval)
        if hist.empty:
            return "주가 데이터를 불러올 수 없습니다."
        hist = hist[["Open", "High", "Low", "Close", "Volume"]].copy()
        hist.columns = ["시가", "고가", "저가", "종가", "거래량"]
        hist.index = hist.index.strftime("%Y-%m")
        for col in ["시가", "고가", "저가", "종가"]:
            hist[col] = hist[col].map("{:,.0f}".format)
        hist["거래량"] = hist["거래량"].map("{:,.0f}".format)
        return hist.to_markdown()

    def get_key_metrics(self) -> str:
        info = self.ticker.info
        def fmt_pct(v):
            return f"{v*100:.2f}%" if v else "N/A"
        def fmt_val(v):
            return f"{v:,.2f}" if v else "N/A"
        fields = {
            "PER (Trailing)": fmt_val(info.get("trailingPE")),
            "PER (Forward)":  fmt_val(info.get("forwardPE")),
            "PBR":            fmt_val(info.get("priceToBook")),
            "EPS (Trailing)": fmt_val(info.get("trailingEps")),
            "EPS (Forward)":  fmt_val(info.get("forwardEps")),
            "ROE":            fmt_pct(info.get("returnOnEquity")),
            "ROA":            fmt_pct(info.get("returnOnAssets")),
            "베타":           fmt_val(info.get("beta")),
        }
        df = pd.DataFrame.from_dict(fields, orient='index', columns=['Value'])
        df.index.name = '항목'
        return df.to_markdown()

    def get_52week_range(self) -> str:
        info = self.ticker.info
        low  = info.get("fiftyTwoWeekLow", 0)
        high = info.get("fiftyTwoWeekHigh", 0)
        curr = info.get("currentPrice", 0)
        pos  = (curr - low) / (high - low) * 100 if high != low else 0
        fields = {
            "52주 최고가":       f"{high:,.0f}원",
            "52주 최저가":       f"{low:,.0f}원",
            "현재가":            f"{curr:,.0f}원",
            "52주 범위 내 위치": f"{pos:.1f}%",
        }
        df = pd.DataFrame.from_dict(fields, orient='index', columns=['Value'])
        df.index.name = '항목'
        return df.to_markdown()

    def get_dividend_info(self) -> str:
        info = self.ticker.info
        div_yield = info.get("dividendYield")
        div_rate  = info.get("dividendRate")
        payout    = info.get("payoutRatio")
        fields = {
            "배당 수익률": f"{div_yield*100:.2f}%" if div_yield else "N/A",
            "주당 배당금": f"{div_rate:,.0f}원"    if div_rate  else "N/A",
            "배당 성향":   f"{payout*100:.2f}%"    if payout    else "N/A",
        }
        df = pd.DataFrame.from_dict(fields, orient='index', columns=['Value'])
        df.index.name = '항목'
        return df.to_markdown()

    def get_volume_info(self) -> str:
        info = self.ticker.info
        fields = {
            "현재 거래량":        f"{info.get('volume', 0):,}",
            "평균 거래량(10일)":  f"{info.get('averageVolume10days', 0):,}",
            "평균 거래량(3개월)": f"{info.get('averageVolume', 0):,}",
        }
        df = pd.DataFrame.from_dict(fields, orient='index', columns=['Value'])
        df.index.name = '항목'
        return df.to_markdown()

    def get_financial_health(self) -> str:
        info = self.ticker.info
        def fmt_pct(v):
            return f"{v*100:.2f}%" if v else "N/A"
        def fmt_val(v):
            return f"{v:,.2f}" if v else "N/A"
        fcf = info.get("freeCashflow")
        fields = {
            "부채비율 (D/E)":   fmt_val(info.get("debtToEquity")),
            "유동비율":         fmt_val(info.get("currentRatio")),
            "영업이익률":       fmt_pct(info.get("operatingMargins")),
            "순이익률":         fmt_pct(info.get("profitMargins")),
            "매출 성장률(YoY)": fmt_pct(info.get("revenueGrowth")),
            "잉여현금흐름":     f"{fcf/1e8:.0f}억원" if fcf else "N/A",
        }
        df = pd.DataFrame.from_dict(fields, orient='index', columns=['Value'])
        df.index.name = '항목'
        return df.to_markdown()

    def _clean_fs_df(self, df, key_items=None):
        label_ko_col = None
        date_cols = []
        for col in df.columns:
            if isinstance(col, tuple) and col[1] == 'label_ko':
                label_ko_col = col
            elif isinstance(col, tuple) and isinstance(col[0], str) and col[0][:4].isdigit():
                date_cols.append(col)
        if label_ko_col is None:
            return df.to_markdown()
        result = df[[label_ko_col] + date_cols].copy()
        result = result.set_index(label_ko_col)
        result.columns = [col[0][:4] + '년' for col in date_cols]
        if key_items:
            result = result[result.index.isin(key_items)]
        def fmt(v):
            try:
                v = float(v)
                if abs(v) >= 1e12:
                    return f"{v/1e12:.1f}조"
                elif abs(v) >= 1e8:
                    return f"{v/1e8:.0f}억"
                else:
                    return f"{v:,.0f}"
            except:
                return v
        result = result.map(fmt)
        result.index.name = '항목'
        return result.to_markdown()

    def get_analyst_target(self) -> str:
        info  = self.ticker.info
        curr  = info.get("currentPrice", 0)
        mean  = info.get("targetMeanPrice", 0)
        upside = (mean / curr - 1) * 100 if curr and mean else 0
        fields = {
            "현재가":        f"{curr:,.0f}원" if curr else "N/A",
            "목표주가 평균": f"{mean:,.0f}원" if mean else "N/A",
            "목표주가 최고": f"{info.get('targetHighPrice', 0):,.0f}원" if info.get('targetHighPrice') else "N/A",
            "목표주가 최저": f"{info.get('targetLowPrice', 0):,.0f}원" if info.get('targetLowPrice') else "N/A",
            "상승 여력":     f"{upside:.1f}%",
        }
        df = pd.DataFrame.from_dict(fields, orient='index', columns=['Value'])
        df.index.name = '항목'
        return df.to_markdown()

    def get_holders_info(self) -> str:
        info = self.ticker.info
        inst = info.get("heldPercentInstitutions")
        ins  = info.get("heldPercentInsiders")
        result = f"**기관 보유 비중**: {inst*100:.2f}%\n\n" if inst else "**기관 보유 비중**: N/A\n\n"
        result += f"**내부자 보유 비중**: {ins*100:.2f}%\n\n" if ins else "**내부자 보유 비중**: N/A\n\n"
        inst_df = self.ticker.institutional_holders
        if inst_df is not None and not inst_df.empty:
            result += "**기관 투자자 현황 (상위 10)**\n" + inst_df.head(10).to_markdown()
        return result

    def get_buyback_info(self) -> str:
        try:
            cf = self.ticker.cashflow
            rows = [r for r in cf.index if 'Repurchase' in str(r) or 'Buyback' in str(r)]
            if rows:
                return cf.loc[rows].to_markdown()
        except:
            pass
        return "자사주 매입 데이터 없음"

    def get_news(self, n=5) -> str:
        news_list = self.ticker.news[:n]
        if not news_list:
            return "뉴스 데이터 없음"
        lines = []
        for i, news in enumerate(news_list, 1):
            content = news.get("content", {})
            lines.append(f"**[{i}] {content.get('title', 'N/A')}**")
            lines.append(f"{content.get('pubDate', 'N/A')}\n")
        return "\n".join(lines)

    def get_stock_splits(self) -> str:
        splits = self.ticker.splits
        if splits.empty:
            return "주식 분할 이력 없음"
        splits.index = splits.index.strftime("%Y-%m-%d")
        return splits.to_markdown()

    def get_financial_statement(self) -> str:
        if self.corp is None:
            return "DART에서 해당 종목을 찾을 수 없습니다."
        fs = self.corp.extract_fs(bgn_de='20230101')
        IS_ITEMS = ['매출액', '매출총이익', '영업이익', '당기순이익']
        BS_ITEMS = ['유동자산', '비유동자산', '자산총계', '유동부채', '비유동부채', '부채총계', '자본총계']
        CF_ITEMS = ['영업활동현금흐름', '투자활동현금흐름', '재무활동현금흐름']
        sections = []
        try:
            sections.append("### 손익계산서\n" + self._clean_fs_df(fs['is'], IS_ITEMS))
        except: pass
        try:
            sections.append("### 재무상태표\n" + self._clean_fs_df(fs['bs'], BS_ITEMS))
        except: pass
        try:
            sections.append("### 현금흐름표\n" + self._clean_fs_df(fs['cf'], CF_ITEMS))
        except: pass
        return "\n\n".join(sections) if sections else "재무제표 데이터를 불러올 수 없습니다."
