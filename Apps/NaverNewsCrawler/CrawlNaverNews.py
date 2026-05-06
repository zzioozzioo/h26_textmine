# 사용자와의 소통을 위한 인터페이스

import NaverNewsCrawler as nnc
import streamlit as st
import pandas as pd


def clean_news_data(corpus):
    df = pd.DataFrame(corpus)

    # HTML 태그 제거 및 데이터 정제
    df['title'] = df['title'].str.replace('<b>', '').str.replace('</b>', '')
    df['description'] = df['description'].str.replace('<b>', '').str.replace('</b>', '')
    return df

def display_news_preview(corpus, limit=5):
    st.subheader('최신 뉴스 미리보기')
    for index, item in enumerate(corpus[:5]): # 상위 5개 출력
        st.markdown(f"**{index + 1}. {item['title'].replace('<b>', '').replace('</b>', '')}**")
        st.write(item['description'].replace('<b>','').replace('</b>',''))
        st.caption(f"작성일: {item['pubDate']}")
        st.divider()


# 메인 로직
st.title('네이버 뉴스 크롤러')
st.write('네이버 뉴스에서 원하는 검색어로 뉴스를 크롤링합니다.')

# 1. 사용자 입력 받기
keyword = st.text_input('검색어를 입력하세요: ')

# 2. 뉴스 수집
if st.button('뉴스 수집 시작'):
    if keyword:
        with st.spinner('뉴스를 수집하는 중입니다...'):
            corpus = nnc.crawlNaverNewsAll(keyword)
        
        if corpus:
            st.success(f'{len(corpus)}개의 뉴스를 수집했습니다!')

            print(len(corpus))
            print(corpus[:3])

            # 데이터 정제 및 프레임 생성
            df = clean_news_data(corpus)

            # 전체 데이터 표 출력
            st.dataframe(df[['title', 'description', 'link', 'pubDate']]) # 제목, 설명, 링크, 발행일 표시

            # 개별 뉴스 상세 보기
            display_news_preview(corpus)
        
        else:
            st.warning('검색 결과가 없습니다.')
    else:
        st.error('검색어를 입력해주세요.')

