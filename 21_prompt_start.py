from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
res = client.responses.create(
    model = 'gpt-4o-mini',
    input = [
        {'role':'system','content':'너는 파인다이닝 쉐프야'}, 
        {'role':'user','content':'발렌타인데이 때 주문할 메뉴를 추천해줘'}
    ],
    temperature = 0
)
print(res.output_text)