import streamlit as st

st.title("Hello, Streamlit World")
name = "Jiwoo"
st.title(f"Hello, {name}~~~~ Welcome to Streamlit World!!")


# Write, Magic Command
import pandas as pd

df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [10, 20, 30, 40]
})
print(df)


# Text 출력
st.title('제일 큰 글자 title')
st.header('title보다 작은 글자인 header')
st.subheader('일반 글자보다 약간 큰 subheader')
st.text('일반 글자 text')

st.success('성공')
st.warning('경고')
st.info('정보')
st.error('오류')
st.exception(RuntimeError("This is an exception of type RuntimeError"))

import time

@st.cache_data
def change_text():
    text = st.text("텍스트가 변할 겁니다.")
    time.sleep(2)
    text.info('2초가 지났습니다.')
change_text()


# Input Widgets
st.button('clicked_button')
list_of_options = ['신경망', '랜덤포레스트', 'SVM']
selected_radio = st.radio('머신러닝 방법', list_of_options)
st.info(selected_radio)

st.checkbox('토큰화')

selected_selectbox = st.selectbox('머신러닝 방법', list_of_options)
st.info(selected_selectbox)

selected_multiselect = st.multiselect('머신러닝 방법', list_of_options)
st.info(selected_multiselect)

selected_slider = st.slider('가중치', 0, 10, 5, 1)
st.info(f'가중치: {selected_slider}')

st.number_input('message')


# Form
with st.form('my_form'):
    submitted = st.form_submit_button('submit')

if submitted:
    print('submitted!')


# 사용자 입력 폼 만들기
st.subheader('사용자 입력 폼')
name = st.text_input('이름')
age = st.number_input('나이', 1, 150, 1, 1)
checkbox = st.checkbox('약관에 동의합니다')

if st.button('제출') and checkbox:
    st.text(f'이름: {name}, 나이: {age}')
    st.success('약관에 동의했습니다.')


# sidebar 속성
st.sidebar.text_input('input text: ')
st.sidebar.button('new button')


# matplotlib, wordcloud 사용
import matplotlib.pyplot as plt

subjects = ['Linux', 'ADsP', 'SQLD', 'CSTS']
progress = [80, 20, 20, 0]

fix, ax = plt.subplots() 
ax.barh(subjects, progress, color='skyblue')

ax.set_xlabel('Progress (%)')
ax.set_title('Study Status')
st.pyplot(fix)