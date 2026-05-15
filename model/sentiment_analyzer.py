from konlpy.tag import Okt
import joblib

# 모델 로딩
class SentimentAnalyzer:
    def __init__(self, vectorizer_file, model_file):
        self.__vectorizer = joblib.load(vectorizer_file)
        self.__sa_model = joblib.load(model_file)
    
    def korean_tokenizer(self, text):
        my_tags = ['Noun', 'Adjective', 'Verb']
        my_stopwords = [] # 나중에 추가하기
        tokenizer = Okt()
        return [word for word, tag in tokenizer.pos(text) if tag in my_tags and word not in my_stopwords]

    def analyze_sentiment(self, review):
        token_review = ' '.join(self.korean_tokenizer(review))
        # 전처리 및 특징 벡터 추출
        review_fv = self.__vectorizer.transform([token_review])
        # print(review_fv)

        result = self.__sa_model.predict(review_fv)
        # print(result)

        show = '긍정' if result[0] >= 0.5 else '부정'
        return show 