import streamlit as st

st.title('안녕하세요!')

#브라우저에 텍스트 출력
st.write('Hello Streamlit!!!')

st.divider()

#사용자 입력을 받는 요소
name = st.text_input('이름:')

st.write(name)


#### 버튼

def bt1_click(): #정의
  st.write('그렇구나.. 잘했어..')

st.write('')
#btn1 = st.button('push', on_click = bt1_click) #호출
btn1 = st.button('push')
if btn1 :
  #st.write('정말 눌렀어???')
  bt1_click()

#### 판다스 사용하기
import pandas as pd
df = pd.read_csv('./data/pew.csv')

# log 출력하기
print(df.info())

st.write(df.head())
