import NaverNewsCrawler as nnc
import streamlit as st

st.text_input('검색어를 입력하세요: ')
keyword = input('검색어를 입력하세요: ')
corpus = nnc.crawlNaverNewsAll(keyword)
print(len(corpus))
print(corpus[:3])

