from dotenv import load_dotenv
import os
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
print("API Key configured:", "OPENAI_API_KEY" in os.environ)

#랭체인
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

#종목 투자보고서 프롬프트 실행

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3)

def investment_report(symbol, company, stock):
  prompt = ChatPromptTemplate.from_messages(
    [
      ('system', '''
            당신은 10년 이상 경력의 한국 주식 시장 전문 애널리스트입니다.
            KOSPI 상장 기업의 재무제표와 기본정보를 분석하여
            전문적인 투자 보고서를 작성합니다.
            투자의견은 매수 / 중립 / 매도 중 하나로 명확히 제시하고,
            AI 추정 목표주가도 반드시 포함하세요.
        '''),
      ('user', '''
            종목코드 {symbol} / {company} 투자 보고서를 아래 정보를 바탕으로
            마크다운 형식으로 한글 작성해주세요.

            ## 작성 항목
            1. 기업 개요
            2. 재무 분석 (손익계산서 / 재무상태표 / 현금흐름표 요약)
            3. 투자 포인트 (긍정적 요인)
            4. 리스크 요인
            5. 투자의견 및 AI 추정 목표주가

            ---
            [기본정보]
            {business_info}

            [재무제표]
            {financial_statements}
       ''')
    ]
  )
  output_parser = StrOutputParser()
  
  chain = prompt | llm | output_parser
  response = chain.invoke({
    'symbol': symbol,
    'company':company,
    'business_info': stock.get_basic_info(),
    'financial_statements': stock.get_financial_statement()
  })
  
  return response
