# ui와 인터랙션하는 main logic만 포함
# 누가 일할 건지 뿌려주는 애


import streamlit as st
import mylib.myTextAnalyzer as ta
import mylib.myStreamlitVisualizer as sv
import pandas as pd
from konlpy.tag import Okt

# 1. 데이터 로딩
def load_uploaded_file(file):
    try:
        df = pd.read_csv(file)
        if 'review' in df.columns:
            return df['review'].dropna().astype(str).tolist()
        else:
            st.error("CSV 파일에 'review' 컬럼이 없습니다. 컬럼명을 확인해주세요.")
            return None
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

# 2. 데이터 빈도수 만들기    
def get_word_freq(corpus):
    my_tags = ['Noun', 'Verb', 'Adjective']
    my_stopwords = ['없다', '필요없다', '하는', '한다', '의하여', '하여', '있다', '하며', '하여야']
    return ta.count_word_freq(corpus, Okt(), my_tags, my_stopwords)

# 3. 수평 막대 그래프 -> 상위 20개 시각화
def draw_barh_graph(counter, num_word):
    st.subheader(f'단어 빈도수 차트 (상위 {num_word}개)')
    sv.visualize_barh_graph(counter, num_word)

# 4. 워드 클라우드 -> 상위 50개 시각화
def draw_wordcloud(counter, num_word):
    st.subheader(f'워드 클라우드 (상위 {num_word}개)')
    sv.visualize_wordcloud(counter, num_word)


# 메인 로직
st.set_page_config(page_title="다음 영화 리뷰 텍스트 분석", layout="wide")
st.title("다음 영화 리뷰 텍스트 분석")

# 사이드바 -> 데이터 파일 업로드
st.sidebar.header("데이터 업로드")
uploaded_file = st.sidebar.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    st.info(f"업로드 완료: {uploaded_file.name}")

    if st.button('데이터 분석 시작', use_container_width=True):
        corpus = load_uploaded_file(uploaded_file)

        if corpus:
            with st.spinner('데이터 분석 중...'):
                counter = get_word_freq(corpus)
                st.success('데이터 분석 완료!')

                col1, col2 = st.columns(2)
                with col1:
                    draw_barh_graph(counter, num_word=20)
                with col2:
                    draw_wordcloud(counter, num_word=50)    
                
                st.divider()
                st.subheader("데이터 요약")
                st.write(f"총 고유 단어 수: {len(counter)}")

else:
    st.warning("CSV 파일을 업로드해주세요.")