import pandas as pd
from collections import Counter

# csv 파일에서 분석 대상 텍스트를 추출하여 반환
# input : csv 파일, 분석 대상 컬럼명
# output : 분석 대상 텍스트 리스트
def load_corpus(datafile, col_name):
    data_df = pd.read_csv(datafile)
    reviews = list(data_df[col_name])
    return reviews

def tokenize_korean_corpus(corpus, tokenizer, my_tags, my_stopwords):
    words = []
    for review in corpus:
        for word, pos in tokenizer.pos(review):
            if pos in my_tags and word not in my_stopwords and len(word) > 1:
                words.append(word)

    return words

# input : 분석 대상 텍스트 리스트
# output : Counter 객체 (단어 빈도수)
def count_word_freq(corpus, tokenizer, my_tags, my_stopwords):
    words = tokenize_korean_corpus(corpus, tokenizer, my_tags, my_stopwords)
    
    # 단어 빈도수 계산
    return Counter(words)

