import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import platform

def set_korean_font():
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    plt.rc('axes', unicode_minus=False)

def visualize_barh_graph(counter, num_word):

    set_korean_font()

    most_common = counter.most_common(num_word)
    word_list = [x[0] for x in most_common][::-1] # 역순 정렬 (높은 게 위로)
    count_list = [x[1] for x in most_common][::-1]

    fig, ax = plt.subplots()
    ax.barh(word_list, count_list)
    ax.set_title(f"상위 {num_word}개 단어 빈도수")
    ax.set_xlabel('빈도')
    st.pyplot(fig)


def visualize_wordcloud(counter, num_word):
    font_path = "C:/Windows/Fonts/malgun.ttf"

    wc = WordCloud(
        font_path=font_path,
        background_color='white',
        width=800,
        height=600,
        max_words=num_word,
        colormap='viridis'
    )

    # 워드클라우드 생성
    gen = wc.generate_from_frequencies(counter)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(gen, interpolation='bilinear')
    ax.axis('off') # 축 제거
    st.pyplot(fig)
